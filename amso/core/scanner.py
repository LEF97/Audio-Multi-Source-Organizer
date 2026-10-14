"""Scanner de système de fichiers multithreadé pour AMSO.

Effectue un parcours récursif rapide, une indexation incrémentale
(évite de relire les fichiers inchangés via mtime/size), et synchronise
les résultats directement avec la base SQLite3 de façon découplée de Qt.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
import os
from pathlib import Path
import threading
import time
from typing import Callable, Optional, Sequence

from amso.core.database import DatabaseManager, SourceRecord, SourceType, TrackRecord
from amso.core.metadata import extract_metadata, is_audio_file


@dataclass(slots=True)
class ScanSummary:
    """Bilan récapitulatif d'une opération de scan."""

    source_id: int
    source_path: str
    total_found: int = 0
    added: int = 0
    updated: int = 0
    unchanged: int = 0
    deleted: int = 0
    errors: list[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0
    cancelled: bool = False


# Callbacks de progression
ProgressCallback = Callable[[int, int, str], None]  # (traité, total, chemin_courant)
StatusCallback = Callable[[str], None]  # message informatif


class LocalScanner:
    """Moteur de découverte et d'indexation des fichiers audio locaux."""

    def __init__(
        self,
        db: DatabaseManager,
        max_workers: Optional[int] = None,
        batch_size: int = 250,
    ) -> None:
        self.db = db
        # Par défaut, adapter au nombre de CPU disponibles
        cpu_count = os.cpu_count() or 4
        self.max_workers = max_workers or min(32, cpu_count * 2)
        self.batch_size = batch_size
        self._cancel_event = threading.Event()

    def cancel(self) -> None:
        """Demande l'annulation immédiate du scan en cours."""
        self._cancel_event.set()

    def is_cancelled(self) -> bool:
        """Indique si une annulation a été demandée."""
        return self._cancel_event.is_set()

    def scan_source(
        self,
        source: SourceRecord,
        on_progress: Optional[ProgressCallback] = None,
        on_status: Optional[StatusCallback] = None,
        compute_hash: bool = True,
    ) -> ScanSummary:
        """Parcourt récursivement le répertoire d'une source locale et synchronise la base."""
        self._cancel_event.clear()
        start_time = time.perf_counter()

        summary = ScanSummary(
            source_id=source.id or 0,
            source_path=source.path_or_uri,
        )

        root_path = Path(source.path_or_uri).resolve()
        if not root_path.exists() or not root_path.is_dir():
            err = f"Répertoire source introuvable ou inaccessible : {source.path_or_uri}"
            summary.errors.append(err)
            if on_status:
                on_status(err)
            return summary

        if on_status:
            on_status(f"Découverte des fichiers audio dans {root_path}...")

        # 1. Découverte rapide de tous les fichiers audio
        audio_files: list[Path] = []
        try:
            for entry in os.walk(root_path):
                if self._cancel_event.is_set():
                    summary.cancelled = True
                    break
                dirpath, _, filenames = entry
                for fn in filenames:
                    ext = os.path.splitext(fn)[1].lower()
                    if ext and is_audio_file(fn):
                        audio_files.append(Path(dirpath) / fn)
        except Exception as e:
            summary.errors.append(f"Erreur lors du parcours du dossier : {e}")

        summary.total_found = len(audio_files)

        if self._cancel_event.is_set():
            summary.cancelled = True
            summary.elapsed_seconds = round(time.perf_counter() - start_time, 2)
            return summary

        if on_status:
            on_status(f"{len(audio_files)} fichiers audio détectés. Analyse incrémentale...")

        # 2. Récupération de l'état existant en base pour scan incrémental
        existing_tracks_map: dict[str, tuple[float, int]] = {}
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT source_ref, file_mtime, file_size FROM tracks WHERE source_id = ?;",
                (source.id,),
            )
            for r in cursor:
                ref = r["source_ref"]
                mtime = float(r["file_mtime"] or 0.0)
                size = int(r["file_size"] or 0)
                existing_tracks_map[ref] = (mtime, size)

        # 3. Séparation entre fichiers à réanalyser et fichiers inchangés
        files_to_process: list[tuple[Path, bool]] = []  # (path, is_update)
        current_refs: set[str] = set()

        for fpath in audio_files:
            ref = fpath.as_posix()
            current_refs.add(ref)

            try:
                stat = fpath.stat()
                mtime = stat.st_mtime
                size = stat.st_size
            except (OSError, PermissionError):
                continue

            if ref in existing_tracks_map:
                prev_mtime, prev_size = existing_tracks_map[ref]
                # Si taille et date de modification identiques, fichier inchangé
                if abs(prev_mtime - mtime) < 0.001 and prev_size == size:
                    summary.unchanged += 1
                    continue
                else:
                    files_to_process.append((fpath, True))  # mise à jour
            else:
                files_to_process.append((fpath, False))  # ajout

        if on_status:
            on_status(
                f"{len(files_to_process)} fichiers à extraire "
                f"({summary.unchanged} déjà à jour)."
            )

        # 4. Extraction multithreadée des métadonnées
        processed_count = summary.unchanged
        total_total = len(audio_files)

        if files_to_process:
            buffer: list[TrackRecord] = []

            def _worker(item: tuple[Path, bool]) -> tuple[TrackRecord, bool]:
                path, is_update = item
                rec = extract_metadata(
                    path,
                    source_id=source.id,
                    source_type=SourceType.LOCAL,
                    compute_hash=compute_hash,
                )
                return rec, is_update

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(_worker, it): it for it in files_to_process}

                for future in as_completed(futures):
                    if self._cancel_event.is_set():
                        summary.cancelled = True
                        break

                    try:
                        record, is_update = future.result()
                        buffer.append(record)
                        if is_update:
                            summary.updated += 1
                        else:
                            summary.added += 1
                    except Exception as exc:
                        summary.errors.append(f"Erreur d'extraction sur {futures[future][0]}: {exc}")

                    processed_count += 1
                    if on_progress and (processed_count % 10 == 0 or processed_count == total_total):
                        on_progress(processed_count, total_total, str(futures[future][0]))

                    # Écriture par lot dans SQLite
                    if len(buffer) >= self.batch_size:
                        self.db.upsert_tracks_batch(buffer)
                        buffer.clear()

                # Vider le buffer restant
                if buffer:
                    self.db.upsert_tracks_batch(buffer)
                    buffer.clear()

        # 5. Nettoyage des fichiers supprimés du disque
        if not summary.cancelled and source.id is not None:
            summary.deleted = self.db.prune_missing_tracks(source.id, current_refs)
            self.db.update_source_scanned(source.id)

        summary.elapsed_seconds = round(time.perf_counter() - start_time, 2)

        if on_status:
            on_status(
                f"Scan terminé en {summary.elapsed_seconds}s : "
                f"+{summary.added} ajouts, {summary.updated} mis à jour, "
                f"-{summary.deleted} supprimés, {summary.unchanged} inchangés."
            )

        return summary
