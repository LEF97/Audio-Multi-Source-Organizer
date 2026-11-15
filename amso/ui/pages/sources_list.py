"""Liste des sources, menu contextuel et suppression (mixin de MainWindow)."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from typing import TYPE_CHECKING, Any

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
)

from amso.core.activity_messages import LogMessage
from amso.core.database import (
    SourceRecord,
    SourceType,
)
from amso.core.i18n import tr
from amso.ui.dialogs.source_config_dialog import SourceConfigDialog

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    _MixinBase = QMainWindow
else:
    _MixinBase = object


def format_sync_mode_label(source: SourceRecord) -> str:
    """Formate le libellé lisible du mode et de l'intervalle de synchronisation d'une source."""
    raw_mode = getattr(source, "sync_mode", "manual") or "manual"
    interval_m = getattr(source, "sync_interval_minutes", 60) or 60
    interval_s = getattr(source, "sync_interval_seconds", 60) or 60
    if raw_mode == "interval":
        return f"⏱️  {interval_m} min"
    if raw_mode == "realtime":
        return f"⚡  {tr('sync_mode.realtime')} ({interval_s}s)"
    if raw_mode == "startup":
        return f"🚀  {tr('sync_mode.startup')}"
    return f"✋  {tr('sync_mode.manual')}"


class SourcesListMixin(_MixinBase):
    """Liste des sources, menu contextuel et suppression (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de MainWindow sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    def refresh_sources_list(self) -> None:
        """Synchronise l'indicateur de présence de sources dans le lecteur."""
        if hasattr(self, "page_player") and self.page_player:
            sources = self.db.get_sources()
            self.page_player.set_has_sources(len(sources) > 0)

    def _create_source_context_menu(self, source: SourceRecord) -> QMenu:
        """Crée le menu contextuel pour une source (bibliothèque, synchro, explorer, propriétés, supprimer)."""
        menu = QMenu(self)

        if hasattr(self, "_open_source_in_library"):
            action_lib = QAction("📁  " + tr("library_sources.menu_open_in_library"), self)
            action_lib.triggered.connect(lambda: self._open_source_in_library(source))
            menu.addAction(action_lib)

        action_sync = QAction("🔄  " + tr("sources.menu_sync"), self)
        action_sync.triggered.connect(lambda: self._start_scan(source, user_initiated=True))
        menu.addAction(action_sync)

        if source.source_type == SourceType.LOCAL and source.path_or_uri:
            action_open = QAction("📂  " + tr("common.open_explorer"), self)
            action_open.triggered.connect(lambda: self._open_source_in_explorer(source.path_or_uri))
            menu.addAction(action_open)

        action_props = QAction(tr("sources.menu_properties"), self)
        action_props.triggered.connect(lambda: self._on_edit_source_properties(source))
        menu.addAction(action_props)

        menu.addSeparator()

        action_del = QAction("🗑️  " + tr("sources.menu_delete"), self)
        action_del.triggered.connect(lambda: self._on_delete_source(source))
        menu.addAction(action_del)

        return menu

    def _on_edit_source_properties(self, source: SourceRecord) -> None:
        """Ouvre le dialogue de configuration / propriétés d'une source."""
        dlg = SourceConfigDialog(source=source, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        if source.id is None:
            return

        data = dlg.get_data()
        self.db.update_source_sync_config(
            source_id=source.id,
            sync_mode=data["sync_mode"],
            sync_interval_minutes=data.get("sync_interval_minutes", 60),
            sync_interval_seconds=data.get("sync_interval_seconds", 60),
            name=data["name"],
        )

        self.refresh_sources_list()
        self._refresh_folders_tree()
        self._refresh_settings_sources_table()
        if hasattr(self, "_refresh_library_sources_tree"):
            self._refresh_library_sources_tree()
        if hasattr(self, "scheduler") and self.scheduler:
            self.scheduler.refresh_watched_directories()
            if data["sync_mode"] == "realtime" and source.id and not source.last_scanned_at:
                self.scheduler.enqueue_source(source.id)

    def _open_source_in_explorer(self, path: str) -> None:
        """Ouvre un dossier de source dans le gestionnaire de fichiers OS."""
        if not path:
            return
        norm_path = os.path.normpath(path)
        if os.path.exists(norm_path):
            if sys.platform == "win32":
                os.startfile(norm_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", norm_path])
            else:
                subprocess.run(["xdg-open", norm_path])
        else:
            QMessageBox.warning(
                self,
                tr("folders.folder_not_found_title"),
                tr("folders.folder_not_found_message", path=norm_path),
            )

    def _on_delete_source(self, source: SourceRecord) -> None:
        """Supprime une source et rafraîchit la bibliothèque."""
        if source.id is None:
            return
        reply = QMessageBox.question(
            self,
            tr("sources.delete_confirm_title"),
            tr("sources.delete_confirm_message", name=source.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_source(source.id)
            self.db.add_activity_log(
                action=LogMessage("log.source_removed", {"source": source.name}),
                level="INFO",
                category="LIBRARY",
                source_name=source.name,
                details=[LogMessage("log.detail_location", {"path": source.path_or_uri})],
            )
            if hasattr(self, "page_logs") and self.page_logs:
                self.page_logs.mark_dirty()
            self.refresh_sources_list()
            self._refresh_folders_tree()
            self._refresh_settings_sources_table()
            if hasattr(self, "scheduler") and self.scheduler:
                self.scheduler.refresh_watched_directories()
            self.table_model.reload_data()
            self.folder_table_model.reload_data()
            self._update_track_count()

    def _on_settings_source_double_clicked(self, row: int, column: int) -> None:
        """Ouvre les propriétés d'une source au double-clic sur une ligne du tableau."""
        sources = self.db.get_sources()
        if 0 <= row < len(sources):
            self._on_edit_source_properties(sources[row])

    def _on_table_source_mode_changed(self, source: SourceRecord, new_mode: str) -> None:
        """Modifie instantanément le mode de synchronisation d'une source depuis le tableau."""
        if not new_mode or source.id is None:
            return
        interval = getattr(source, "sync_interval_minutes", 60) or 60
        interval_sec = getattr(source, "sync_interval_seconds", 60) or 60
        self.db.update_source_sync_config(
            source_id=source.id,
            sync_mode=new_mode,
            sync_interval_minutes=interval,
            sync_interval_seconds=interval_sec,
        )
        if hasattr(self, "scheduler") and self.scheduler:
            self.scheduler.refresh_watched_directories()
            if new_mode == "realtime" and source.id and not source.last_scanned_at:
                self.scheduler.enqueue_source(source.id)
        self.status_label.setText(tr("status.source_sync_updated", name=source.name))
        self._refresh_settings_sources_table()
