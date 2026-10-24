"""Corbeille des dossiers et menu contextuel du tableau (mixin de MainWindow)."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QAction, QCursor
from PySide6.QtWidgets import (
    QDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QTableWidgetItem,
)

from amso.core.database import (
    SourceRecord,
    TrackRecord,
)
from amso.core.i18n import tr
from amso.ui.dialogs.delete_track_dialog import DeleteTrackDialog, send_file_to_trash

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    _MixinBase = QMainWindow
else:
    _MixinBase = object


class FoldersTrashMixin(_MixinBase):
    """Corbeille des dossiers et menu contextuel du tableau (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de MainWindow sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    def _load_trash_view(self) -> None:
        """Charge et affiche les éléments de la corbeille (morceaux ignorés)."""
        ignored_items = self.db.get_ignored_tracks()
        cnt = len(ignored_items)
        count_key = "folders.track_count_singular" if cnt == 1 else "folders.track_count"
        self.lbl_folder_count_badge.setText(tr(count_key, count=f"{cnt:,}"))

        self.trash_table.setRowCount(cnt)
        for row, it in enumerate(ignored_items):
            file_path = it.get("source_path") or it.get("source_ref") or ""
            norm_path = file_path.replace("\\", "/")
            file_name = norm_path.rsplit("/", 1)[-1] if norm_path else ""
            folder_loc = norm_path.rsplit("/", 1)[0] if "/" in norm_path else ""
            created_at = it.get("created_at") or ""

            exists = os.path.exists(file_path) if file_path else False

            # Col 0: Nom du fichier
            item_fn = QTableWidgetItem(f"🎵  {file_name}")
            item_fn.setData(Qt.ItemDataRole.UserRole, it)
            self.trash_table.setItem(row, 0, item_fn)

            # Col 1: Emplacement source
            item_dir = QTableWidgetItem(folder_loc)
            item_dir.setToolTip(file_path)
            self.trash_table.setItem(row, 1, item_dir)

            # Col 2: Date de retrait
            item_date = QTableWidgetItem(created_at)
            item_date.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.trash_table.setItem(row, 2, item_date)

            # Col 3: Statut sur disque
            status_text = tr("trash.status_present") if exists else tr("trash.status_missing")
            item_status = QTableWidgetItem(status_text)
            item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.trash_table.setItem(row, 3, item_status)

    def _on_restore_selected_trash(self) -> None:
        """Restaure les morceaux sélectionnés dans la corbeille."""
        selected_indexes = self.trash_table.selectionModel().selectedRows()
        if not selected_indexes:
            return
        items_to_restore: list[dict[str, Any]] = []
        for idx in selected_indexes:
            item_0 = self.trash_table.item(idx.row(), 0)
            if item_0:
                data = item_0.data(Qt.ItemDataRole.UserRole)
                if data:
                    items_to_restore.append(data)
        if items_to_restore:
            self._restore_ignored_items(items_to_restore)

    def _on_clear_all_trash(self) -> None:
        """Vide l'intégralité de la corbeille AMSO."""
        reply = QMessageBox.question(
            self,
            tr("trash.clear_confirm_title"),
            tr("trash.clear_confirm_message"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.clear_ignored_tracks()
            self._load_trash_view()
            self._refresh_folders_tree()

    def _on_trash_table_context_menu(self, pos: QPoint) -> None:
        """Menu contextuel sur un élément de la corbeille."""
        item = self.trash_table.itemAt(pos)
        if not item:
            return
        row = item.row()
        item_0 = self.trash_table.item(row, 0)
        if not item_0:
            return
        data = item_0.data(Qt.ItemDataRole.UserRole)
        if not data:
            return

        menu = QMenu(self)

        act_restore = QAction(tr("trash.action_restore"), self)
        act_restore.triggered.connect(lambda: self._restore_ignored_items([data]))
        menu.addAction(act_restore)

        file_path = data.get("source_path") or data.get("source_ref")
        if file_path and os.path.exists(file_path):
            act_open = QAction(tr("context_menu.open_file_location"), self)
            act_open.triggered.connect(lambda: self._open_file_location(file_path))
            menu.addAction(act_open)

        menu.addSeparator()

        act_del = QAction(tr("trash.btn_clear_all"), self)
        act_del.triggered.connect(lambda: self._delete_single_trash_item(data))
        menu.addAction(act_del)

        menu.exec(self.trash_table.mapToGlobal(pos))

    def _delete_single_trash_item(self, data: dict[str, Any]) -> None:
        """Retire une seule entrée de la table des ignorés."""
        source_ref = data.get("source_ref")
        if source_ref:
            self.db.unignore_track(source_ref)
            self._load_trash_view()
            self._refresh_folders_tree()

    def _on_trash_table_double_clicked(self, index) -> None:
        """Double-clic sur une ligne de la corbeille : propose de restaurer le morceau."""
        if not index.isValid():
            return
        item_0 = self.trash_table.item(index.row(), 0)
        if item_0:
            data = item_0.data(Qt.ItemDataRole.UserRole)
            if data:
                self._restore_ignored_items([data])

    def _find_source_for_path(self, file_path: str) -> SourceRecord | None:
        """Recherche la source configurée correspondant au chemin de fichier fourni."""
        if not file_path:
            return None
        norm_fp = file_path.replace("\\", "/").lower()
        best_source = None
        best_len = 0
        for src in self.db.get_sources():
            root = (src.path_or_uri or "").replace("\\", "/").rstrip("/").lower()
            if root and norm_fp.startswith(root) and len(root) > best_len:
                best_source = src
                best_len = len(root)
        return best_source

    def _restore_ignored_items(self, items: list[dict[str, Any]]) -> None:
        """Restaure les morceaux ignorés et déclenche la synchronisation de leur source."""
        sources_to_sync: set[int] = set()
        restored_count = 0
        for it in items:
            source_ref = it.get("source_ref")
            source_path = it.get("source_path")
            if source_ref:
                self.db.unignore_track(source_ref)
                restored_count += 1
                if source_path:
                    src = self._find_source_for_path(source_path)
                    if src and src.id:
                        sources_to_sync.add(src.id)

        # Déclencher synchronisation pour les sources concernées
        for s_id in sources_to_sync:
            src = self.db.get_source(s_id)
            if src:
                self._start_scan(src, user_initiated=True)

        self._load_trash_view()
        self._refresh_folders_tree()
        self.table_model.reload_data()
        self.folder_table_model.reload_data()
        self._update_track_count()
        self._refresh_stats_view()

        self.status_label.setText(f"♻️ {tr('trash.restore_success', count=restored_count)}")

    def _on_folder_table_context_menu(self, pos: QPoint) -> None:
        index = self.folder_table_view.indexAt(pos)
        menu = QMenu(self)

        if index.isValid():
            selected_tracks = self._get_selected_tracks(self.folder_table_view, self.folder_table_model, index.row())
            if selected_tracks:
                act_next = QAction(tr("context_menu.play_next"), self)
                act_next.triggered.connect(lambda: self._insert_next_with_vlc_check(selected_tracks))
                menu.addAction(act_next)

                act_add = QAction(tr("context_menu.add_to_playlist"), self)
                act_add.triggered.connect(lambda: self._append_tracks_with_vlc_check(selected_tracks))
                menu.addAction(act_add)

                menu.addSeparator()

            track = self.folder_table_model.get_track_at(index.row())
            if track:
                action_open_dir = QAction(tr("context_menu.open_file_location"), self)
                action_open_dir.triggered.connect(lambda: self._open_file_location(track.source_path))
                menu.addAction(action_open_dir)

                menu.addSeparator()

                action_del = QAction(tr("context_menu.delete_track"), self)
                action_del.triggered.connect(lambda: self._delete_track_from_folder_view(track))
                menu.addAction(action_del)

                menu.addSeparator()

        # Personnalisation des colonnes accessible directement depuis le tableau
        cols_submenu = self._build_columns_menu(self.folder_table_view, self.folder_table_model, "folders")
        cols_submenu.setTitle("⚙️  " + tr("table.menu_columns"))
        menu.addMenu(cols_submenu)

        menu.exec(QCursor.pos())

    def _delete_track_from_folder_view(self, track: TrackRecord) -> None:
        if track.id is None:
            return
        dlg = DeleteTrackDialog(track, self)
        if dlg.exec() != QDialog.DialogCode.Accepted or not dlg.action:
            return

        if dlg.action == "trash" and track.source_path:
            send_file_to_trash(track.source_path)

        # Dans les deux cas (retirer de la bibliothèque ou corbeille), on ignore pour les futurs scans
        self.db.ignore_track(track.source_ref, track.source_path)
        self.db.delete_track(track.id)

        # Retirer de la playlist du lecteur s'il y est présent
        self._remove_track_from_player(track)

        self.folder_table_model.reload_data()
        self.table_model.reload_data()
        self._update_track_count()
        self._refresh_stats_view()
        self._refresh_folders_tree()
