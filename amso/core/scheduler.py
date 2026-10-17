"""Planificateur et orchestrateur de synchronisation automatique pour AMSO.

Gère les déclenchements périodiques (intervalle), au démarrage et en continu
(QFileSystemWatcher + battement d'actualisation pour NAS/SMB et sous-dossiers)
avec gestion de file d'attente pour éviter les scans concurrents.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from PySide6.QtCore import QFileSystemWatcher, QObject, QTimer, Signal

from amso.core.database import DatabaseManager, SourceRecord, SourceType


class SyncScheduler(QObject):
    """Planificateur centralisé des synchronisations de sources."""

    # Signal émis vers l'IHM lorsqu'un scan doit être exécuté (émet un SourceRecord)
    request_scan = Signal(object)

    def __init__(self, db: DatabaseManager, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.db = db
        self._is_running = False
        self._current_scanning_source_id: int | None = None
        self._queue: list[int] = []

        # 1. Timer de vérification périodique (toutes les 5 secondes pour réactivité accrue avec les secondes)
        self._interval_timer = QTimer(self)
        self._interval_timer.setInterval(5_000)
        self._interval_timer.timeout.connect(self._check_all_scheduled_sources)

        # 2. Surveillance du système de fichiers pour les sources en temps réel
        self._watcher = QFileSystemWatcher(self)
        self._watcher.directoryChanged.connect(self._on_directory_changed)

        # 3. Timer debounce pour ne pas déclencher un scan à chaque fichier écrit
        self._debounce_timers: dict[str, QTimer] = {}

    def start(self) -> None:
        """Démarre le planificateur de synchronisation."""
        self._is_running = True
        self.refresh_watched_directories()
        self._interval_timer.start()

        # Planifier les scans au démarrage (startup + realtime) avec un léger différé (1.5s)
        QTimer.singleShot(1500, self._trigger_startup_sources)

    def stop(self) -> None:
        """Arrête le planificateur."""
        self._is_running = False
        self._interval_timer.stop()
        if self._watcher.directories():
            self._watcher.removePaths(self._watcher.directories())
        for timer in self._debounce_timers.values():
            timer.stop()
        self._debounce_timers.clear()

    def refresh_watched_directories(self) -> None:
        """Met à jour les dossiers surveillés par QFileSystemWatcher selon les sources actives."""
        existing = self._watcher.directories()
        if existing:
            self._watcher.removePaths(existing)

        sources = self.db.get_sources()
        for src in sources:
            if src.sync_mode == "realtime" and src.source_type == SourceType.LOCAL and src.id:
                p = Path(src.path_or_uri)
                norm_p = os.path.normpath(str(p))
                if os.path.isdir(norm_p):
                    self._watcher.addPath(norm_p)

    @property
    def _watched_paths(self) -> list[str]:
        return self._watcher.directories()

    def _trigger_startup_sources(self) -> None:
        """Déclenche la synchronisation des sources configurées en mode 'startup' ou 'realtime'."""
        if not self._is_running:
            return
        sources = self.db.get_sources()
        for src in sources:
            # Enfiler les sources 'startup', 'realtime' ou celles jamais scannées
            if src.id and (src.sync_mode in ("startup", "realtime") or not src.last_scanned_at):
                self.enqueue_source(src.id)

    def _check_all_scheduled_sources(self) -> None:
        """Vérifie les sources périodiques et le battement de veille des sources en continu (NAS/SMB)."""
        if not self._is_running:
            return

        sources = self.db.get_sources()
        now = datetime.now(UTC)

        for src in sources:
            if not src.id:
                continue

            # Cas 1 : Source jamais scannée -> scan immédiat requis
            if not src.last_scanned_at:
                if src.sync_mode in ("startup", "realtime", "interval"):
                    self.enqueue_source(src.id)
                continue

            # Calculer le temps écoulé depuis la dernière synchronisation
            try:
                last_dt = datetime.fromisoformat(src.last_scanned_at)
                if last_dt.tzinfo is None:
                    last_dt = last_dt.replace(tzinfo=UTC)
                elapsed = (now - last_dt).total_seconds()
            except Exception:
                elapsed = 999999.0

            # Cas 2 : Mode intervalle (ex: toutes les N minutes)
            if src.sync_mode == "interval":
                interval_sec = max(5, src.sync_interval_minutes) * 60
                if elapsed >= interval_sec:
                    self.enqueue_source(src.id)

            # Cas 3 : Mode en continu (realtime)
            # Sur les disques locaux, QFileSystemWatcher réagit instantanément.
            # Sur les NAS réseau (partages SMB / UNC) ou les sous-dossiers profonds,
            # Windows ne propage pas toujours les notifications d'événements.
            # Un battement périodique paramétrable (sync_interval_seconds, 60s par défaut) garantit la détection.
            elif src.sync_mode == "realtime":
                realtime_sec = max(5, getattr(src, "sync_interval_seconds", 60) or 60)
                if elapsed >= realtime_sec:
                    self.enqueue_source(src.id)

    _check_interval_sources = _check_all_scheduled_sources

    def _on_directory_changed(self, dir_path: str) -> None:
        """Déclenché par QFileSystemWatcher lorsqu'un dossier surveillé est modifié."""
        if not self._is_running:
            return

        norm_dir = os.path.normpath(dir_path).rstrip("\\/").lower()
        sources = self.db.get_sources()
        target_source: SourceRecord | None = None
        for s in sources:
            if s.sync_mode == "realtime":
                src_p = os.path.normpath(s.path_or_uri).rstrip("\\/").lower()
                if src_p == norm_dir:
                    target_source = s
                    break

        if not target_source or not target_source.id:
            return

        # Debounce : attendre 2 secondes de calme avant de lancer le scan
        key = str(target_source.id)
        if key not in self._debounce_timers:
            t = QTimer(self)
            t.setSingleShot(True)
            t.setInterval(2000)
            t.timeout.connect(lambda sid=target_source.id: self.enqueue_source(sid))
            self._debounce_timers[key] = t

        self._debounce_timers[key].start()

    def enqueue_source(self, source_id: int) -> None:
        """Ajoute une source à la file d'attente de synchronisation."""
        if source_id == self._current_scanning_source_id:
            return
        if source_id not in self._queue:
            self._queue.append(source_id)
        self._process_queue()

    _enqueue_scan = enqueue_source

    def _process_queue(self) -> None:
        """Traite le prochain élément de la file d'attente si aucun scan n'est en cours."""
        if self._current_scanning_source_id is not None:
            return
        if not self._queue:
            return

        next_id = self._queue.pop(0)
        source = self.db.get_source(next_id)
        if source:
            self._current_scanning_source_id = next_id
            self.request_scan.emit(source)
        else:
            self._process_queue()

    def notify_scan_started(self, source_id: int) -> None:
        """Indique au planificateur qu'un scan a débuté (manuel ou automatique)."""
        self._current_scanning_source_id = source_id
        if source_id in self._queue:
            self._queue.remove(source_id)

    def notify_scan_finished(self, source_id: int) -> None:
        """Notifie le planificateur qu'un scan est terminé pour libérer la file d'attente."""
        if self._current_scanning_source_id == source_id:
            self._current_scanning_source_id = None
        self._process_queue()

    def get_schedule_status(self) -> dict:
        """Retourne l'état complet du planificateur : source active, file d'attente et prochaines synchros."""
        now = datetime.now(UTC)
        current_source = (
            self.db.get_source(self._current_scanning_source_id) if self._current_scanning_source_id else None
        )

        queue_sources: list[SourceRecord] = []
        for sid in self._queue:
            s = self.db.get_source(sid)
            if s:
                queue_sources.append(s)

        upcoming: list[dict] = []
        sources = self.db.get_sources()
        for src in sources:
            if not src.id:
                continue
            if src.sync_mode == "interval":
                interval_sec = max(5, src.sync_interval_minutes) * 60
                elapsed = 0.0
                if src.last_scanned_at:
                    try:
                        last_dt = datetime.fromisoformat(src.last_scanned_at)
                        if last_dt.tzinfo is None:
                            last_dt = last_dt.replace(tzinfo=UTC)
                        elapsed = (now - last_dt).total_seconds()
                    except Exception:
                        elapsed = 0.0
                remaining = max(0, int(interval_sec - elapsed))
                upcoming.append(
                    {
                        "source": src,
                        "mode": "interval",
                        "remaining_seconds": remaining,
                        "interval_minutes": src.sync_interval_minutes,
                    }
                )
            elif src.sync_mode == "realtime":
                upcoming.append(
                    {
                        "source": src,
                        "mode": "realtime",
                        "remaining_seconds": 0,
                        "interval_minutes": 0,
                    }
                )

        upcoming.sort(key=lambda x: (0 if x["mode"] == "realtime" else 1, x["remaining_seconds"]))

        return {
            "current_source": current_source,
            "queue_sources": queue_sources,
            "upcoming": upcoming,
            "is_running": self._is_running,
        }
