"""Liste des sources, menu contextuel et suppression (mixin de MainWindow)."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
)

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


class SourcesListMixin(_MixinBase):
    """Liste des sources, menu contextuel et suppression (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de MainWindow sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    def refresh_sources_list(self) -> None:
        """Met à jour les boutons de sources dans le tiroir Sources."""
        while self.sources_layout.count():
            item = self.sources_layout.takeAt(0)
            if item is not None:
                w = item.widget()
                if w is not None:
                    w.deleteLater()

        sources = self.db.get_sources()
        if hasattr(self, "page_player") and self.page_player:
            self.page_player.set_has_sources(len(sources) > 0)

        for src in sources:
            icon_str = "💾" if src.source_type == SourceType.LOCAL else "☁️"
            btn = QPushButton(f"{icon_str}  {src.name}")
            btn.setProperty("class", "nav-btn")
            btn.setCheckable(True)
            btn.setToolTip(src.path_or_uri)
            btn.clicked.connect(lambda checked=False, s=src: self._on_source_selected(s))
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda pos, s=src, b=btn: self._on_source_context_menu(pos, s, b))
            self.nav_button_group.addButton(btn)
            self.sources_layout.addWidget(btn)

    def _create_source_context_menu(self, source: SourceRecord) -> QMenu:
        """Crée le menu contextuel pour une source (synchroniser, ouvrir explorer, propriétés, supprimer)."""
        menu = QMenu(self)

        action_sync = QAction("🔄  " + tr("sources.menu_sync"), self)
        action_sync.triggered.connect(lambda: self._start_scan(source, user_initiated=True))
        menu.addAction(action_sync)

        if source.path_or_uri:
            action_open = QAction("📂  " + tr("sources.menu_open_explorer"), self)
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
        if hasattr(self, "scheduler") and self.scheduler:
            self.scheduler.refresh_watched_directories()
            if data["sync_mode"] == "realtime" and source.id and not source.last_scanned_at:
                self.scheduler.enqueue_source(source.id)

    def _on_source_context_menu(self, pos: QPoint, source: SourceRecord, button: QPushButton) -> None:
        menu = self._create_source_context_menu(source)
        menu.exec(button.mapToGlobal(pos))

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
                action=f"Source supprimée : {source.name}",
                level="INFO",
                category="LIBRARY",
                source_name=source.name,
                details=f"Emplacement: {source.path_or_uri}",
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
            self._refresh_stats_view()

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
