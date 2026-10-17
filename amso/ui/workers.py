"""Workers asynchrones PySide6 (QThread) pour AMSO.

Déporte les opérations lourdes (scans de disques, calculs de hash et requêtes)
en tâche de fond pour garantir une interface 100% réactive.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal

from amso.core.database import DatabaseManager, SourceRecord
from amso.core.scanner import LocalScanner, ScanSummary


class ScanWorker(QThread):
    """Worker de scan multithreadé tournant en arrière-plan."""

    phase1_finished = Signal(object)  # ScanSummary émis dès la fin de l'inventaire rapide
    progress = Signal(int, int, str)  # (current, total, current_file) pour Phase 2
    status_message = Signal(str)  # message informatif
    scan_finished = Signal(object)  # ScanSummary final
    scan_error = Signal(str)  # message d'erreur

    def __init__(
        self,
        db: DatabaseManager,
        source: SourceRecord,
        compute_hash: bool = True,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.db = db
        self.source = source
        self.compute_hash = compute_hash
        self.scanner = LocalScanner(db=self.db)

    def run(self) -> None:
        """Exécution du scan en 2 temps dans le thread dédié."""
        try:
            summary = self.scanner.scan_source(
                source=self.source,
                on_progress=self._on_progress,
                on_status=self._on_status,
                on_phase1_finished=self._on_phase1_done,
                compute_hash=self.compute_hash,
            )
            self.scan_finished.emit(summary)
        except Exception as e:
            self.scan_error.emit(str(e))

    def _on_phase1_done(self, summary: ScanSummary) -> None:
        self.phase1_finished.emit(summary)

    def cancel(self) -> None:
        """Interrompt immédiatement le scanner en arrière-plan."""
        self.scanner.cancel()

    def _on_progress(self, current: int, total: int, file_path: str) -> None:
        self.progress.emit(current, total, file_path)

    def _on_status(self, msg: str) -> None:
        self.status_message.emit(msg)
