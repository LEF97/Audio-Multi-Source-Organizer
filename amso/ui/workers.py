"""Workers asynchrones PySide6 (QThread) pour AMSO.

Déporte les opérations lourdes (scans de disques, calculs de hash et requêtes)
en tâche de fond pour garantir une interface 100% réactive.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QObject, QThread, Signal

from amso.core.database import DatabaseManager, SourceRecord
from amso.core.scanner import LocalScanner, ScanSummary


class ScanWorker(QThread):
    """Worker de scan multithreadé tournant en arrière-plan."""

    progress = Signal(int, int, str)  # (current, total, current_file)
    status_message = Signal(str)      # message informatif
    scan_finished = Signal(object)    # ScanSummary
    scan_error = Signal(str)          # message d'erreur

    def __init__(
        self,
        db: DatabaseManager,
        source: SourceRecord,
        compute_hash: bool = True,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self.db = db
        self.source = source
        self.compute_hash = compute_hash
        self.scanner = LocalScanner(db=self.db)

    def run(self) -> None:
        """Exécution du scan dans le thread dédié."""
        try:
            summary = self.scanner.scan_source(
                source=self.source,
                on_progress=self._on_progress,
                on_status=self._on_status,
                compute_hash=self.compute_hash,
            )
            self.scan_finished.emit(summary)
        except Exception as e:
            self.scan_error.emit(str(e))

    def cancel(self) -> None:
        """Interrompt immédiatement le scanner en arrière-plan."""
        self.scanner.cancel()

    def _on_progress(self, current: int, total: int, file_path: str) -> None:
        self.progress.emit(current, total, file_path)

    def _on_status(self, msg: str) -> None:
        self.status_message.emit(msg)
