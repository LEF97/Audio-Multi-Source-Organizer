"""Ajout de dossier et pilotage des scans (mixin de MainWindow)."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt, QThread
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QMainWindow,
    QMessageBox,
)

from amso.core.activity_messages import LogMessage, raw_line
from amso.core.database import (
    SourceRecord,
    SourceType,
)
from amso.core.i18n import tr
from amso.core.scanner import ScanSummary
from amso.ui.dialogs.source_config_dialog import SourceConfigDialog
from amso.ui.workers import ScanWorker

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    _MixinBase = QMainWindow
else:
    _MixinBase = object


class ScanControllerMixin(_MixinBase):
    """Ajout de dossier et pilotage des scans (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de MainWindow sont résolus dynamiquement (typage uniquement)
        scan_worker: ScanWorker | None
        _last_scan_progress_time: float

        def __getattr__(self, name: str) -> Any: ...

    def _on_add_local_folder(self) -> None:
        """Permet à l'utilisateur de sélectionner un dossier audio local et de configurer sa synchronisation."""
        folder = QFileDialog.getExistingDirectory(
            self,
            tr("dialog.select_folder_title"),
            str(Path.home()),
        )
        if not folder:
            return

        folder_path = Path(folder).resolve()
        dlg = SourceConfigDialog(initial_path=str(folder_path), parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        data = dlg.get_data()
        source = self.db.add_source(
            source_type=SourceType.LOCAL,
            name=data["name"],
            path_or_uri=data["path_or_uri"],
            sync_mode=data["sync_mode"],
            sync_interval_minutes=data.get("sync_interval_minutes", 60),
            sync_interval_seconds=data.get("sync_interval_seconds", 60),
        )
        self.refresh_sources_list()
        self._refresh_folders_tree()
        self._refresh_settings_sources_table()
        if hasattr(self, "scheduler") and self.scheduler:
            self.scheduler.refresh_watched_directories()

        self.db.add_activity_log(
            action=LogMessage("log.source_added", {"source": source.name}),
            level="INFO",
            category="LIBRARY",
            source_name=source.name,
            details=[
                LogMessage("log.detail_location", {"path": source.path_or_uri}),
                LogMessage("log.detail_sync_mode", {"mode": source.sync_mode}),
            ],
        )
        if hasattr(self, "page_logs") and self.page_logs:
            self.page_logs.mark_dirty()

        # Lancement immédiat de l'indexation de la nouvelle source en arrière-plan
        self._start_scan(source, user_initiated=True)

    def _on_scan_current_source(self) -> None:
        """Lance le scan sur toutes les sources locales."""
        sources = self.db.get_sources()
        if not sources:
            QMessageBox.information(
                self,
                tr("dialog.no_source_title"),
                tr("dialog.no_source_message"),
            )
            return

        for src in sources:
            if src.source_type == SourceType.LOCAL:
                self._start_scan(src, user_initiated=True)
                break

    def _on_scheduler_request_scan(self, source_or_id: SourceRecord | int) -> None:
        """Callback déclenché par le planificateur de synchronisation automatique."""
        source: SourceRecord | None
        if isinstance(source_or_id, SourceRecord):
            source = source_or_id
        else:
            source = self.db.get_source(source_or_id)
        if source:
            started = self._start_scan(source, user_initiated=False)
            if not started and hasattr(self, "scheduler") and self.scheduler and source.id:
                # Si le scan ne peut démarrer (ex. worker actif), libérer la file
                self.scheduler.notify_scan_finished(source.id)

    def _start_scan(self, source: SourceRecord, user_initiated: bool = False) -> bool:
        """Démarre le worker asynchrone de scan (Étape 1 inventaire rapide + Étape 2 analyse audio)."""
        if self.scan_worker and self.scan_worker.isRunning():
            if hasattr(self, "scheduler") and self.scheduler and source.id:
                self.scheduler.enqueue_source(source.id)
            return False

        self._current_scan_user_initiated = user_initiated
        self._current_scanning_source_id = source.id
        if hasattr(self, "scheduler") and self.scheduler and source.id:
            self.scheduler.notify_scan_started(source.id)

        self._status_is_alert = False
        self.status_label.setCursor(Qt.CursorShape.ArrowCursor)
        self.status_label.setToolTip("")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.btn_cancel_scan.setVisible(True)
        self.status_label.setText(tr("status.scanning", source=source.name))

        if hasattr(self, "btn_activity_feed") and self.btn_activity_feed:
            self.btn_activity_feed.setText(f"🔄 {source.name}")
            self.btn_activity_feed.setStyleSheet(
                """
                QPushButton {
                    background-color: rgba(2, 132, 199, 0.25);
                    color: #38BDF8;
                    border: 1px solid #0284C7;
                    border-radius: 6px;
                    padding: 2px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #0284C7;
                    color: #FFFFFF;
                }
                """
            )
        if hasattr(self, "activity_popover") and self.activity_popover:
            self.activity_popover.update_progress(tr("status.scanning", source=source.name), pct=0)

        self.scan_worker = ScanWorker(db=self.db, source=source, compute_hash=True, parent=self)
        self.scan_worker.progress.connect(self._on_scan_progress)
        self.scan_worker.status_message.connect(self.status_label.setText)
        self.scan_worker.phase1_finished.connect(self._on_phase1_scan_finished)
        self.scan_worker.scan_finished.connect(self._on_scan_finished)
        self.scan_worker.scan_error.connect(self._on_scan_error)
        self.scan_worker.start(QThread.Priority.LowPriority)
        return True

    def _cancel_current_scan(self) -> None:
        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.cancel()
            self.status_label.setText(tr("status.cancelling"))
            if hasattr(self, "activity_popover") and self.activity_popover:
                self.activity_popover.update_progress(tr("status.cancelling"), pct=None)

    def _on_scan_progress(self, current: int, total: int, current_file: str) -> None:
        now = time.perf_counter()
        # Throttling des rafraîchissements IHM (max 8 FPS) pour ne pas engorger la boucle Qt
        if hasattr(self, "_last_scan_progress_time"):
            if (now - self._last_scan_progress_time) < 0.12 and current < total:
                return
        self._last_scan_progress_time = now

        if total > 0:
            pct = int((current / total) * 100)
            self.progress_bar.setValue(pct)
            fn = Path(current_file).name
            status_txt = tr("status.indexing", current=current, total=total, file=fn)
            self.status_label.setText(status_txt)
            if hasattr(self, "activity_popover") and self.activity_popover:
                self.activity_popover.update_progress(status_txt, pct=pct)

    def _on_phase1_scan_finished(self, summary: ScanSummary) -> None:
        """Appelé dès que l'étape 1 (inventaire rapide des fichiers) est achevée."""
        has_structural_changes = summary.added > 0 or summary.deleted > 0 or summary.playlists_changed
        has_any_changes = has_structural_changes or summary.updated > 0

        if has_any_changes:
            self._tracks_dirty = True
            self._folders_dirty = True
            self._stats_dirty = True
            self._sources_dirty = True

        total_indexed = summary.added + summary.updated + summary.unchanged
        self.status_label.setText(tr("status.phase1_done", count=total_indexed))
        if hasattr(self, "activity_popover") and self.activity_popover:
            self.activity_popover.update_progress(tr("status.phase1_done", count=total_indexed), pct=50)

        # Si l'utilisateur consulte activement la vue Morceaux (0) ou Dossiers (3), rafraîchir intelligemment
        curr_page = self.stacked_widget.currentIndex()
        if curr_page == 0:
            if has_any_changes:
                self.table_model.reload_data()
                self._update_track_count()
            self._tracks_dirty = False
        elif curr_page == 3:
            if has_structural_changes:
                self._refresh_folders_tree()
            if has_any_changes:
                self.folder_table_model.reload_data()
            self._folders_dirty = False

    def _on_scan_finished(self, summary: ScanSummary) -> None:
        self.progress_bar.setVisible(False)
        self.btn_cancel_scan.setVisible(False)

        has_structural_changes = summary.added > 0 or summary.deleted > 0 or summary.playlists_changed
        has_any_changes = has_structural_changes or summary.updated > 0

        # Marquer les vues pour un rafraîchissement à la demande uniquement si des changements existent
        if has_any_changes:
            self._tracks_dirty = True
            self._folders_dirty = True
            self._stats_dirty = True
            self._sources_dirty = True

        # Rafraîchir UNIQUEMENT la vue actuellement visible s'il y a eu des modifications
        curr_page = self.stacked_widget.currentIndex()
        if curr_page == 0:
            if has_any_changes:
                self.table_model.reload_data()
                self._update_track_count()
            self._tracks_dirty = False
        elif curr_page == 3:
            # Ne rafraîchir l'arborescence des dossiers que si un dossier a été ajouté ou supprimé
            if has_structural_changes:
                self._refresh_folders_tree()
            if has_any_changes:
                self.folder_table_model.reload_data()
            self._folders_dirty = False
        elif curr_page == 4:
            if has_any_changes:
                self._refresh_settings_sources_table()
            self._sources_dirty = False

        if has_any_changes:
            self.refresh_sources_list()

        # Récupération du nom de la source scannée
        source_name = "Source"
        if self._current_scanning_source_id is not None:
            s_rec = self.db.get_source(self._current_scanning_source_id)
            if s_rec:
                source_name = s_rec.name

        if hasattr(self, "scheduler") and self.scheduler and self._current_scanning_source_id is not None:
            self.scheduler.notify_scan_finished(self._current_scanning_source_id)

        # Réinitialisation de l'affichage du badge d'état
        if hasattr(self, "btn_activity_feed") and self.btn_activity_feed:
            self.btn_activity_feed.setText("⚡ " + tr("status.activity_feed"))
            self.btn_activity_feed.setStyleSheet(
                """
                QPushButton {
                    background-color: #1E293B;
                    color: #94A3B8;
                    border: 1px solid #334155;
                    border-radius: 6px;
                    padding: 2px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #0284C7;
                    color: #FFFFFF;
                    border: 1px solid #38BDF8;
                }
                """
            )

        if summary.cancelled:
            self.status_label.setText(tr("status.cancelled"))
            self.db.add_activity_log(
                action=LogMessage("log.sync_cancelled", {"source": source_name}),
                level="WARNING",
                category="SYNC",
                source_name=source_name,
                details=[LogMessage("log.detail_cancelled")],
            )
        elif summary.errors and summary.added == 0 and summary.updated == 0 and summary.unchanged == 0:
            err_msg = tr("status.scan_errors", count=len(summary.errors))
            self.status_label.setText(err_msg)
            self.db.add_activity_log(
                action=LogMessage("log.sync_failed", {"source": source_name}),
                level="ERROR",
                category="SYNC",
                source_name=source_name,
                details=[raw_line(e) for e in summary.errors],
                items_errors=len(summary.errors),
            )
            if getattr(self, "_current_scan_user_initiated", False):
                QMessageBox.warning(
                    self,
                    tr("dialog.scan_errors_title"),
                    tr("dialog.scan_errors_message", count=len(summary.errors), error=summary.errors[0]),
                )
        else:
            self.status_label.setText(
                tr(
                    "status.scan_finished",
                    elapsed=summary.elapsed_seconds,
                    added=summary.added,
                    updated=summary.updated,
                    unchanged=summary.unchanged,
                )
            )
            lvl = "WARNING" if summary.errors else "SUCCESS"
            detail_lines = [
                LogMessage("log.detail_duration", {"seconds": f"{summary.elapsed_seconds:.1f}"}),
                LogMessage("log.detail_added", {"count": summary.added}),
                LogMessage("log.detail_updated", {"count": summary.updated}),
                LogMessage("log.detail_unchanged", {"count": summary.unchanged}),
                LogMessage("log.detail_deleted", {"count": summary.deleted}),
            ]
            if summary.playlists_changed:
                detail_lines.append(
                    LogMessage(
                        "log.detail_playlists",
                        {
                            "added": summary.playlists_added,
                            "updated": summary.playlists_updated,
                            "deleted": summary.playlists_deleted,
                        },
                    )
                )
                detail_lines.extend(
                    LogMessage("log.detail_playlist_name", {"name": n}) for n in summary.playlist_names[:10]
                )
                if len(summary.playlist_names) > 10:
                    detail_lines.append(LogMessage("log.detail_more", {"count": len(summary.playlist_names) - 10}))
            if summary.errors:
                detail_lines.append(LogMessage("log.detail_errors", {"count": len(summary.errors)}))
                detail_lines.extend(raw_line(e) for e in summary.errors[:10])

            self.db.add_activity_log(
                action=LogMessage("log.sync_success", {"source": source_name}),
                level=lvl,
                category="SYNC",
                source_name=source_name,
                details=detail_lines,
                items_added=summary.added,
                items_updated=summary.updated,
                items_deleted=summary.deleted,
                items_errors=len(summary.errors),
            )

        if hasattr(self, "activity_popover") and self.activity_popover:
            self.activity_popover.update_progress("", pct=None)

        if hasattr(self, "page_logs") and self.page_logs:
            self.page_logs.mark_dirty()

    def _on_scan_error(self, err_msg: str) -> None:
        self.progress_bar.setVisible(False)
        self.btn_cancel_scan.setVisible(False)
        self._status_is_alert = True
        self.status_label.setText(tr("status.scan_error", error=err_msg))
        self.status_label.setToolTip(f"{err_msg}\n({tr('status.click_to_view_logs')})")
        self.status_label.setCursor(Qt.CursorShape.PointingHandCursor)

        source_name = "Source"
        if self._current_scanning_source_id is not None:
            s_rec = self.db.get_source(self._current_scanning_source_id)
            if s_rec:
                source_name = s_rec.name

        if hasattr(self, "scheduler") and self.scheduler and self._current_scanning_source_id is not None:
            self.scheduler.notify_scan_finished(self._current_scanning_source_id)

        if hasattr(self, "btn_activity_feed") and self.btn_activity_feed:
            self.btn_activity_feed.setText("⚡ " + tr("status.activity_feed"))
        if hasattr(self, "activity_popover") and self.activity_popover:
            self.activity_popover.update_progress("", pct=None)

        self.db.add_activity_log(
            action=LogMessage("log.scan_critical", {"source": source_name}),
            level="ERROR",
            category="SYNC",
            source_name=source_name,
            details=[raw_line(err_msg)],
            items_errors=1,
        )

        if hasattr(self, "page_logs") and self.page_logs:
            self.page_logs.mark_dirty()

        if getattr(self, "_current_scan_user_initiated", False):
            QMessageBox.critical(
                self,
                tr("dialog.scan_error_title"),
                tr("dialog.scan_error_message", error=err_msg),
            )

    # -------------------------------------------------------------------------
    # Menu contextuel du tableau
    # -------------------------------------------------------------------------
