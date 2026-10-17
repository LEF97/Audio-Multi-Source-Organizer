"""Scanner de système de fichiers multithreadé pour AMSO en 2 temps.

- Phase 1 (Inventaire rapide) : découverte ultra-rapide des chemins, tailles et dates,
  création immédiate des enregistrements en base et nettoyage des fichiers supprimés.
- Phase 2 (Analyse audio approfondie) : extraction multithreadée des métadonnées (Mutagen,
  durée, bitrate, tags, empreintes) en arrière-plan avec sauvegarde progressive.
"""

from __future__ import annotations

import os
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from amso.core.database import DatabaseManager, SourceRecord, SourceType, TrackRecord
from amso.core.metadata import SUPPORTED_AUDIO_EXTENSIONS, extract_metadata


@dataclass(slots=True)
class ScanSummary:
    """Bilan récapitulatif d'une opération de scan."""

    source_id: int
    source_path: str
    phase: int = 1  # 1 = inventaire fichiers, 2 = analyse audio
    total_found: int = 0
    added: int = 0
    updated: int = 0
    unchanged: int = 0
    deleted: int = 0
    analyzed: int = 0  # Nombre de pistes dont les métadonnées audio ont été extraites
    errors: list[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0
    cancelled: bool = False


# Callbacks de progression
ProgressCallback = Callable[[int, int, str], None]  # (traité, total, chemin_courant)
StatusCallback = Callable[[str], None]  # message informatif
PhaseFinishedCallback = Callable[[ScanSummary], None]  # notification de fin d'inventaire Phase 1


class LocalScanner:
    """Moteur de découverte et d'indexation des fichiers audio locaux en deux temps."""

    def __init__(
        self,
        db: DatabaseManager,
        max_workers: int | None = None,
        batch_size: int = 250,
    ) -> None:
        self.db = db
        cpu_count = os.cpu_count() or 4
        # Limite équilibrée pour garantir la réactivité instantanée de l'interface et du lecteur audio
        self.max_workers = max_workers or min(4, max(2, cpu_count // 2))
        self.batch_size = batch_size
        self._cancel_event = threading.Event()

    def cancel(self) -> None:
        """Demande l'annulation immédiate du scan en cours."""
        self._cancel_event.set()

    def is_cancelled(self) -> bool:
        """Indique si une annulation a été demandée."""
        return self._cancel_event.is_set()

    def scan_inventory(
        self,
        source: SourceRecord,
        on_status: StatusCallback | None = None,
    ) -> tuple[ScanSummary, list[Path]]:
        """Phase 1 : Inventaire rapide du système de fichiers et synchronisation immédiate."""
        self._cancel_event.clear()
        start_time = time.perf_counter()

        summary = ScanSummary(
            source_id=source.id or 0,
            source_path=source.path_or_uri,
            phase=1,
        )

        root_path = Path(source.path_or_uri).resolve()
        if not root_path.exists() or not root_path.is_dir():
            err = f"Répertoire source introuvable ou inaccessible : {source.path_or_uri}"
            summary.errors.append(err)
            if on_status:
                on_status(err)
            return summary, []

        if on_status:
            on_status(f"Découverte rapide des fichiers dans {root_path}...")

        # 1. Récupération préalable de l'état existant en base pour comparaison instantanée
        existing_tracks_map: dict[str, tuple[float, int, bool]] = {}
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT source_ref, file_mtime, file_size, metadata_extracted FROM tracks WHERE source_id = ?;",
                (source.id,),
            )
            for r in cursor:
                ref = r["source_ref"]
                mtime = float(r["file_mtime"] or 0.0)
                size = int(r["file_size"] or 0)
                meta_done = bool(r["metadata_extracted"])
                existing_tracks_map[ref] = (mtime, size, meta_done)

        audio_files: list[Path] = []
        current_refs: set[str] = set()
        inventory_buffer: list[TrackRecord] = []

        # 2. Parcours récursif mono-passe ultra-rapide avec os.scandir (exploite WIN32_FIND_DATAW sous Windows/SMB)
        stack: list[Path] = [root_path]
        try:
            while stack:
                if self._cancel_event.is_set():
                    summary.cancelled = True
                    break

                current_dir = stack.pop()
                clean_folder_path = str(current_dir).replace("\\", "/")
                folder_name = current_dir.name or str(current_dir)

                try:
                    with os.scandir(current_dir) as it:
                        for entry in it:
                            if self._cancel_event.is_set():
                                summary.cancelled = True
                                break

                            try:
                                is_d = entry.is_dir(follow_symlinks=False)
                            except (OSError, PermissionError):
                                continue

                            if is_d:
                                stack.append(Path(entry.path))
                            else:
                                fn = entry.name
                                dot_idx = fn.rfind(".")
                                if dot_idx == -1:
                                    continue
                                ext = fn[dot_idx:].lower()
                                if ext not in SUPPORTED_AUDIO_EXTENSIONS:
                                    continue

                                try:
                                    st = entry.stat(follow_symlinks=False)
                                    mtime = st.st_mtime
                                    size = st.st_size
                                except (OSError, PermissionError):
                                    continue

                                fpath = Path(entry.path)
                                audio_files.append(fpath)
                                ref = fpath.as_posix()
                                current_refs.add(ref)

                                if ref in existing_tracks_map:
                                    prev_mtime, prev_size, meta_done = existing_tracks_map[ref]
                                    if abs(prev_mtime - mtime) < 0.001 and prev_size == size:
                                        summary.unchanged += 1
                                        continue
                                    else:
                                        # Fichier modifié sur le disque
                                        summary.updated += 1
                                        rec = TrackRecord(
                                            source_ref=ref,
                                            source_type=SourceType.LOCAL,
                                            source_id=source.id,
                                            source_path=str(fpath),
                                            file_name=fn,
                                            folder_path=clean_folder_path,
                                            folder_name=folder_name,
                                            title=fn[:dot_idx],
                                            format=ext.lstrip("."),
                                            file_size=size,
                                            file_mtime=mtime,
                                            metadata_extracted=False,
                                        )
                                        inventory_buffer.append(rec)
                                else:
                                    # Nouveau fichier découvert
                                    summary.added += 1
                                    rec = TrackRecord(
                                        source_ref=ref,
                                        source_type=SourceType.LOCAL,
                                        source_id=source.id,
                                        source_path=str(fpath),
                                        file_name=fn,
                                        folder_path=clean_folder_path,
                                        folder_name=folder_name,
                                        title=fn[:dot_idx],
                                        format=ext.lstrip("."),
                                        file_size=size,
                                        file_mtime=mtime,
                                        metadata_extracted=False,
                                    )
                                    inventory_buffer.append(rec)

                                if len(inventory_buffer) >= self.batch_size:
                                    self.db.upsert_tracks_batch(inventory_buffer)
                                    inventory_buffer.clear()
                except (OSError, PermissionError) as e:
                    summary.errors.append(f"Erreur d'accès à {current_dir} : {e}")
        except Exception as e:
            summary.errors.append(f"Erreur lors du parcours du dossier : {e}")

        summary.total_found = len(audio_files)

        if inventory_buffer and not summary.cancelled:
            self.db.upsert_tracks_batch(inventory_buffer)
            inventory_buffer.clear()

        # 3. Nettoyage des fichiers supprimés du disque
        if not summary.cancelled and source.id is not None:
            summary.deleted = self.db.prune_missing_tracks(source.id, current_refs)

        summary.elapsed_seconds = round(time.perf_counter() - start_time, 2)
        if on_status:
            on_status(
                f"Inventaire terminé en {summary.elapsed_seconds}s : {summary.total_found} fichiers trouvés "
                f"(+{summary.added} ajouts, {summary.updated} modifiés, -{summary.deleted} supprimés, {summary.unchanged} inchangés)."
            )

        return summary, audio_files

    def extract_audio_metadata(
        self,
        source: SourceRecord,
        on_progress: ProgressCallback | None = None,
        on_status: StatusCallback | None = None,
        compute_hash: bool = True,
    ) -> ScanSummary:
        """Phase 2 : Extraction approfondie des métadonnées audio sur les pistes en attente."""
        start_time = time.perf_counter()
        summary = ScanSummary(
            source_id=source.id or 0,
            source_path=source.path_or_uri,
            phase=2,
        )

        unextracted = self.db.get_unextracted_tracks(source_id=source.id)
        total_to_analyze = len(unextracted)
        summary.total_found = total_to_analyze

        if total_to_analyze == 0:
            if on_status:
                on_status("Toutes les métadonnées audio sont déjà extraites et à jour.")
            summary.elapsed_seconds = round(time.perf_counter() - start_time, 2)
            return summary

        if on_status:
            on_status(f"Analyse audio de {total_to_analyze} fichier(s)...")

        buffer: list[TrackRecord] = []
        analyzed_count = 0

        def _worker(track: TrackRecord) -> TrackRecord:
            fpath = Path(track.source_path or track.source_ref)
            rec = extract_metadata(
                fpath,
                source_id=source.id,
                source_type=SourceType.LOCAL,
                compute_hash=compute_hash,
            )
            rec.metadata_extracted = True
            rec.file_name = track.file_name or fpath.name
            rec.folder_path = track.folder_path or str(fpath.parent).replace("\\", "/")
            rec.folder_name = track.folder_name or fpath.parent.name
            return rec

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(_worker, t): t for t in unextracted}

            for future in as_completed(futures):
                if self._cancel_event.is_set():
                    summary.cancelled = True
                    break

                try:
                    record = future.result()
                    buffer.append(record)
                    summary.analyzed += 1
                except Exception as exc:
                    summary.errors.append(f"Erreur d'extraction sur {futures[future].source_path}: {exc}")

                analyzed_count += 1
                if on_progress and (analyzed_count % 10 == 0 or analyzed_count == total_to_analyze):
                    on_progress(analyzed_count, total_to_analyze, str(futures[future].source_path or ""))

                if len(buffer) >= self.batch_size:
                    self.db.update_track_metadata_batch(buffer)
                    buffer.clear()
                    # Micro-pause pour relâcher le GIL Python et laisser la priorité à l'interface et à SQLite
                    time.sleep(0.002)

            if buffer:
                self.db.update_track_metadata_batch(buffer)
                buffer.clear()
                time.sleep(0.002)

        summary.elapsed_seconds = round(time.perf_counter() - start_time, 2)
        if on_status:
            on_status(
                f"Analyse audio terminée en {summary.elapsed_seconds}s : "
                f"{summary.analyzed}/{total_to_analyze} fichiers enrichis."
            )

        return summary

    def scan_source(
        self,
        source: SourceRecord,
        on_progress: ProgressCallback | None = None,
        on_status: StatusCallback | None = None,
        on_phase1_finished: PhaseFinishedCallback | None = None,
        compute_hash: bool = True,
    ) -> ScanSummary:
        """Exécute la synchronisation complète (Phase 1 inventaire puis Phase 2 analyse audio)."""
        self._cancel_event.clear()
        total_start = time.perf_counter()

        # 1. Phase 1 : Inventaire rapide
        inv_summary, _ = self.scan_inventory(source=source, on_status=on_status)
        if inv_summary.cancelled or inv_summary.errors:
            return inv_summary

        if on_phase1_finished:
            on_phase1_finished(inv_summary)

        # 2. Phase 2 : Extraction audio
        ext_summary = self.extract_audio_metadata(
            source=source,
            on_progress=on_progress,
            on_status=on_status,
            compute_hash=compute_hash,
        )

        if not self._cancel_event.is_set() and source.id is not None:
            self.db.update_source_scanned(source.id)

        # Synthèse combinée
        combined = ScanSummary(
            source_id=source.id or 0,
            source_path=source.path_or_uri,
            phase=2,
            total_found=inv_summary.total_found,
            added=inv_summary.added,
            updated=inv_summary.updated,
            unchanged=inv_summary.unchanged,
            deleted=inv_summary.deleted,
            analyzed=ext_summary.analyzed,
            errors=inv_summary.errors + ext_summary.errors,
            elapsed_seconds=round(time.perf_counter() - total_start, 2),
            cancelled=self._cancel_event.is_set() or inv_summary.cancelled or ext_summary.cancelled,
        )
        return combined
