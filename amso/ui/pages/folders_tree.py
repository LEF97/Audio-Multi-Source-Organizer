"""Arbre des dossiers : rafraîchissement, menu contextuel et explorateur (mixin de MainWindow)."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QMenu,
    QMessageBox,
    QTreeWidgetItem,
)

from amso.core.database import (
    SourceType,
)
from amso.core.i18n import tr

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    _MixinBase = QMainWindow
else:
    _MixinBase = object


class FoldersTreeMixin(_MixinBase):
    """Arbre des dossiers : rafraîchissement, menu contextuel et explorateur (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de MainWindow sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    def _refresh_folders_tree(self) -> None:
        """Construit ou actualise l'arborescence des dossiers à partir des sources configurées."""
        selected_item = self.folder_tree.currentItem()
        prev_folder_path = None
        if selected_item:
            prev_data = selected_item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(prev_data, dict):
                prev_folder_path = prev_data.get("folder_path")

        self.folder_tree.clear()
        sources = self.db.get_sources()
        if not sources:
            self.right_stack.setCurrentIndex(0)
            self.lbl_folder_breadcrumb.setText("📁  --")
            self.lbl_folder_count_badge.setText(tr("folders.track_count", count="0"))
            return

        reselect_item = None

        for src in sources:
            src_icon = "💾" if src.source_type == SourceType.LOCAL else "☁️"
            src_root = (src.path_or_uri or "").replace("\\", "/").rstrip("/")

            source_item = QTreeWidgetItem(self.folder_tree)
            source_item.setText(0, f"{src_icon}  {src.name}")
            source_item.setToolTip(0, src.path_or_uri)
            source_item.setData(
                0,
                Qt.ItemDataRole.UserRole,
                {
                    "source_id": src.id,
                    "folder_path": src_root,
                    "is_source_root": True,
                    "count": 0,
                },
            )

            folders_summary = self.db.get_folders_summary(source_id=src.id)
            tree_items: dict[str, QTreeWidgetItem] = {src_root.lower(): source_item}

            for f in folders_summary:
                fp = (f["folder_path"] or "").replace("\\", "/").rstrip("/")
                f_count = f["track_count"]

                if fp.lower() == src_root.lower():
                    data = source_item.data(0, Qt.ItemDataRole.UserRole)
                    data["count"] = f_count
                    source_item.setData(0, Qt.ItemDataRole.UserRole, data)
                    continue

                if fp.lower().startswith(src_root.lower() + "/"):
                    rel = fp[len(src_root) + 1 :]
                else:
                    rel = fp

                parts = rel.split("/")
                current_accum = src_root
                parent_node = source_item

                for i, part in enumerate(parts):
                    current_accum += "/" + part
                    acc_key = current_accum.lower()

                    if acc_key not in tree_items:
                        node = QTreeWidgetItem(parent_node)
                        node.setText(0, f"📁  {part}")
                        node.setData(
                            0,
                            Qt.ItemDataRole.UserRole,
                            {
                                "source_id": src.id,
                                "folder_path": current_accum,
                                "is_source_root": False,
                                "count": 0,
                            },
                        )
                        tree_items[acc_key] = node
                        parent_node = node
                    else:
                        parent_node = tree_items[acc_key]

                    if i == len(parts) - 1:
                        data = parent_node.data(0, Qt.ItemDataRole.UserRole)
                        data["count"] = f_count
                        parent_node.setData(0, Qt.ItemDataRole.UserRole, data)

            # Intégration des playlists indexées dans l'arborescence (icône 🎶)
            playlists = self.db.get_playlists(source_id=src.id)
            for pl in playlists:
                pl_fp = (pl.folder_path or src_root).replace("\\", "/").rstrip("/")

                if pl_fp.lower() != src_root.lower() and pl_fp.lower() not in tree_items:
                    if pl_fp.lower().startswith(src_root.lower() + "/"):
                        rel = pl_fp[len(src_root) + 1 :]
                    else:
                        rel = pl_fp

                    parts = rel.split("/")
                    current_accum = src_root
                    p_node = source_item

                    for part in parts:
                        current_accum += "/" + part
                        acc_key = current_accum.lower()

                        if acc_key not in tree_items:
                            node = QTreeWidgetItem(p_node)
                            node.setText(0, f"📁  {part}")
                            node.setData(
                                0,
                                Qt.ItemDataRole.UserRole,
                                {
                                    "source_id": src.id,
                                    "folder_path": current_accum,
                                    "is_source_root": False,
                                    "count": 0,
                                },
                            )
                            tree_items[acc_key] = node
                            p_node = node
                        else:
                            p_node = tree_items[acc_key]

                parent_node = tree_items.get(pl_fp.lower(), source_item)

                pl_node = QTreeWidgetItem(parent_node)
                pl_node.setText(0, f"🎶  {pl.file_name}")
                pl_node.setText(1, f"{pl.track_count:,}" if pl.track_count > 0 else "")
                pl_node.setTextAlignment(1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                pl_node.setToolTip(0, f"Playlist {pl.format.upper()}\n{pl.file_path}")
                pl_node.setData(
                    0,
                    Qt.ItemDataRole.UserRole,
                    {
                        "source_id": src.id,
                        "is_playlist": True,
                        "playlist_id": pl.id,
                        "folder_path": pl.file_path,
                        "file_name": pl.file_name,
                        "file_path": pl.file_path,
                        "format": pl.format,
                        "count": pl.track_count,
                    },
                )
                tree_items[pl.file_path.lower()] = pl_node

            def _calc_totals(node: QTreeWidgetItem) -> int:
                d = node.data(0, Qt.ItemDataRole.UserRole) or {}
                if d.get("is_playlist"):
                    return 0
                direct = d.get("count", 0)
                tot = direct
                for c_idx in range(node.childCount()):
                    child = node.child(c_idx)
                    if child is not None:
                        tot += _calc_totals(child)
                node.setText(1, f"{tot:,}" if tot > 0 else "")
                node.setTextAlignment(1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                d["total_count"] = tot
                node.setData(0, Qt.ItemDataRole.UserRole, d)
                return tot

            _calc_totals(source_item)
            source_item.setExpanded(False)

            if prev_folder_path:
                for it in tree_items.values():
                    d = it.data(0, Qt.ItemDataRole.UserRole) or {}
                    if d.get("folder_path") == prev_folder_path:
                        reselect_item = it
                        break

        # Ajout de l'entrée Corbeille en dessous de la liste des sources
        ignored_count = self.db.count_ignored_tracks()
        trash_item = QTreeWidgetItem(self.folder_tree)
        trash_item.setText(0, f"🗑️  {tr('folders.tree_trash')}")
        trash_item.setText(1, f"{ignored_count:,}" if ignored_count > 0 else "")
        trash_item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        trash_item.setData(
            0,
            Qt.ItemDataRole.UserRole,
            {
                "is_trash": True,
                "folder_path": "__trash__",
                "count": ignored_count,
            },
        )
        if prev_folder_path == "__trash__":
            reselect_item = trash_item

        if reselect_item:
            self.folder_tree.setCurrentItem(reselect_item)
            p = reselect_item.parent()
            while p is not None:
                p.setExpanded(True)
                p = p.parent()
        elif self.folder_tree.topLevelItemCount() > 0:
            first_item = self.folder_tree.topLevelItem(0)
            if first_item is not None:
                self.folder_tree.setCurrentItem(first_item)

    def _on_folder_tree_context_menu(self, pos: QPoint) -> None:
        """Menu contextuel pour l'arborescence des dossiers harmonisé avec la vue tableau."""
        item = self.folder_tree.itemAt(pos)
        if not item:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, dict):
            return

        if data.get("is_trash"):
            menu = QMenu(self)
            action_clear = QAction(tr("trash.btn_clear_all"), self)
            action_clear.triggered.connect(self._on_clear_all_trash)
            menu.addAction(action_clear)
            menu.exec(self.folder_tree.mapToGlobal(pos))
            return

        if data.get("is_playlist"):
            pl_id = data.get("playlist_id")
            pl_path = data.get("file_path")
            tracks = self.db.get_playlist_tracks(pl_id) if pl_id else []

            menu = QMenu(self)
            if tracks:
                act_play = QAction(tr("context_menu.play_playlist"), self)
                act_play.triggered.connect(lambda: self.player_service.play_tracks(tracks, start_index=0))
                menu.addAction(act_play)

                act_next = QAction(tr("context_menu.play_next"), self)
                act_next.triggered.connect(lambda: self._insert_next_with_vlc_check(tracks))
                menu.addAction(act_next)

                act_add = QAction(tr("context_menu.add_to_playlist"), self)
                act_add.triggered.connect(lambda: self._append_tracks_with_vlc_check(tracks))
                menu.addAction(act_add)

                menu.addSeparator()

            if pl_path:
                action_open = QAction(tr("context_menu.open_file_location"), self)
                action_open.triggered.connect(lambda: self._open_file_location(pl_path))
                menu.addAction(action_open)

            menu.exec(self.folder_tree.mapToGlobal(pos))
            return

        fp = data.get("folder_path")
        source_id = data.get("source_id")
        is_source_root = data.get("is_source_root", False)

        menu = QMenu(self)

        tracks = []
        if fp:
            tracks = self.db.get_tracks_by_folder(
                folder_path=fp,
                source_id=source_id,
                recursive=self.cb_recursive.isChecked(),
            )

        if tracks:
            act_next = QAction(tr("context_menu.play_next"), self)
            act_next.triggered.connect(lambda: self._insert_next_with_vlc_check(tracks))
            menu.addAction(act_next)

            act_add = QAction(tr("context_menu.add_to_playlist"), self)
            act_add.triggered.connect(lambda: self._append_tracks_with_vlc_check(tracks))
            menu.addAction(act_add)

            menu.addSeparator()

        if fp:
            action_open = QAction(tr("context_menu.open_file_location"), self)
            action_open.triggered.connect(self._on_open_current_folder_explorer)
            menu.addAction(action_open)

        if is_source_root and source_id:
            src = self.db.get_source(source_id)
            if src:
                menu.addSeparator()

                sync_title = tr("sources.menu_sync").removeprefix("🔄").strip()
                action_sync = QAction(f"🔄  {sync_title}", self)
                action_sync.triggered.connect(lambda: self._start_scan(src, user_initiated=True))
                menu.addAction(action_sync)

                props_title = tr("sources.menu_properties").removeprefix("⚙️").removeprefix("⚙").strip()
                action_props = QAction(f"⚙️  {props_title}", self)
                action_props.triggered.connect(lambda: self._on_edit_source_properties(src))
                menu.addAction(action_props)

        menu.exec(self.folder_tree.mapToGlobal(pos))

    def _on_open_current_folder_explorer(self) -> None:
        item = self.folder_tree.currentItem()
        if not item:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, dict):
            return
        if data.get("is_playlist"):
            pl_path = data.get("file_path")
            if pl_path:
                self._open_file_location(pl_path)
            return
        fp = data.get("folder_path")
        if not fp or fp == "__trash__":
            return
        norm_fp = os.path.normpath(fp)
        if os.path.exists(norm_fp):
            if sys.platform == "win32":
                os.startfile(norm_fp)
            elif sys.platform == "darwin":
                subprocess.run(["open", norm_fp])
            else:
                subprocess.run(["xdg-open", norm_fp])
        else:
            QMessageBox.warning(
                self,
                tr("folders.folder_not_found_title"),
                tr("folders.folder_not_found_message", path=norm_fp),
            )

    # -------------------------------------------------------------------------
    # Gestionnaire de la Corbeille AMSO (Morceaux retirés / ignorés)
    # -------------------------------------------------------------------------
