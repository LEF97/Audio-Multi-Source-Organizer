"""Page Dossiers, arbre, corbeille et doublons par dossier (mixin de MainWindow)."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QAction, QCursor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from amso.core.database import (
    SourceRecord,
    SourceType,
    TrackRecord,
)
from amso.core.i18n import tr
from amso.ui.dialogs.delete_track_dialog import DeleteTrackDialog, send_file_to_trash
from amso.ui.widgets.common import ClickableLabel

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    _MixinBase = QMainWindow
else:
    _MixinBase = object


class FoldersPageMixin(_MixinBase):
    """Page Dossiers, arbre, corbeille et doublons par dossier (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de MainWindow sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    def _create_folders_page(self) -> QWidget:
        """Page de navigation par dossiers avec arborescence hiérarchique et tableau des fichiers."""
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Barre supérieure à hauteur fixe
        top_bar = QFrame()
        top_bar.setObjectName("topBarFrame")
        top_bar.setFixedHeight(50)
        top_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(16, 6, 16, 6)
        top_layout.setSpacing(12)
        top_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.lbl_folders_page_title = QLabel(tr("folders.page_title"))
        self.lbl_folders_page_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        top_layout.addWidget(self.lbl_folders_page_title)

        # Fil d'Ariane / Chemin sélectionné (cliquable pour ouvrir dans l'Explorateur)
        self.lbl_folder_breadcrumb = ClickableLabel("📁  --")
        self.lbl_folder_breadcrumb.setObjectName("folderBreadcrumbLabel")
        self.lbl_folder_breadcrumb.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_folder_breadcrumb.setMaximumWidth(450)
        self.lbl_folder_breadcrumb.clicked.connect(self._on_open_current_folder_explorer)
        top_layout.addWidget(self.lbl_folder_breadcrumb)

        top_layout.addStretch()

        # Badge de décompte des pistes
        self.lbl_folder_count_badge = QLabel(tr("folders.track_count", count="0"))
        self.lbl_folder_count_badge.setFixedHeight(24)
        self.lbl_folder_count_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_folder_count_badge.setStyleSheet(
            "background-color: #20242D; color: #94A3B8; font-size: 12px; font-weight: 600; padding: 2px 10px; border-radius: 12px;"
        )
        top_layout.addWidget(self.lbl_folder_count_badge)

        # Option Inclure les sous-dossiers
        self.cb_recursive = QCheckBox(tr("folders.include_subfolders"))
        self.cb_recursive.setChecked(False)
        self.cb_recursive.toggled.connect(self._on_folder_recursive_toggled)
        top_layout.addWidget(self.cb_recursive)

        # Recherche rapide dans le dossier
        self.folder_search_edit = QLineEdit()
        self.folder_search_edit.setObjectName("folderSearchEdit")
        self.folder_search_edit.setPlaceholderText(tr("folders.search_placeholder"))
        self.folder_search_edit.setMaximumWidth(220)
        self.folder_search_edit.setFixedHeight(30)
        self.folder_search_edit.textChanged.connect(self._on_folder_search_changed)
        top_layout.addWidget(self.folder_search_edit)

        main_layout.addWidget(top_bar, 0)

        # 2. Séparateur horizontal (Splitter gauche / droite)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #282C37; }")

        # --- Panneau Gauche : Arborescence ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(12, 12, 6, 12)
        left_layout.setSpacing(8)

        tree_top_layout = QHBoxLayout()
        tree_top_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_tree_title = QLabel(tr("folders.tree_title"))
        self.lbl_tree_title.setStyleSheet(
            "color: #94A3B8; font-size: 12px; font-weight: 700; text-transform: uppercase;"
        )
        tree_top_layout.addWidget(self.lbl_tree_title)
        tree_top_layout.addStretch()

        self.btn_refresh_tree = QPushButton("🔄")
        self.btn_refresh_tree.setToolTip(tr("folders.btn_refresh"))
        self.btn_refresh_tree.setStyleSheet(
            "font-size: 11px; padding: 2px 6px; background: transparent; border: 1px solid #333846; border-radius: 4px; color: #94A3B8;"
        )
        self.btn_refresh_tree.clicked.connect(self._refresh_folders_tree)
        tree_top_layout.addWidget(self.btn_refresh_tree)

        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderLabels([tr("folders.tree_col_folder"), tr("folders.tree_col_count")])

        self.btn_expand_tree = QPushButton("⊞")
        self.btn_expand_tree.setToolTip(tr("folders.btn_expand_all"))
        self.btn_expand_tree.setStyleSheet(
            "font-size: 11px; padding: 2px 6px; background: transparent; border: 1px solid #333846; border-radius: 4px; color: #94A3B8;"
        )
        self.btn_expand_tree.clicked.connect(lambda: self.folder_tree.expandAll())
        tree_top_layout.addWidget(self.btn_expand_tree)

        self.btn_collapse_tree = QPushButton("⊟")
        self.btn_collapse_tree.setToolTip(tr("folders.btn_collapse_all"))
        self.btn_collapse_tree.setStyleSheet(
            "font-size: 11px; padding: 2px 6px; background: transparent; border: 1px solid #333846; border-radius: 4px; color: #94A3B8;"
        )
        self.btn_collapse_tree.clicked.connect(lambda: self.folder_tree.collapseAll())
        tree_top_layout.addWidget(self.btn_collapse_tree)

        left_layout.addLayout(tree_top_layout)
        self.folder_tree.header().setStretchLastSection(False)
        self.folder_tree.header().setMinimumSectionSize(35)
        self.folder_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.folder_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.folder_tree.header().resizeSection(0, 240)
        self.folder_tree.header().resizeSection(1, 75)
        self.folder_tree.setIndentation(16)
        self.folder_tree.setAnimated(True)
        self.folder_tree.itemClicked.connect(self._on_folder_tree_item_clicked)
        self.folder_tree.currentItemChanged.connect(self._on_folder_tree_current_changed)
        self.folder_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.folder_tree.customContextMenuRequested.connect(self._on_folder_tree_context_menu)
        left_layout.addWidget(self.folder_tree)

        splitter.addWidget(left_widget)

        # --- Panneau Droit : Fichiers du dossier ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(6, 12, 12, 12)
        right_layout.setSpacing(0)

        # Stack de contenu droit (Placeholder OU Table)
        self.right_stack = QStackedWidget()

        # Page 0 : Placeholder
        self.folder_placeholder = QWidget()
        placeholder_layout = QVBoxLayout(self.folder_placeholder)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.setSpacing(12)

        icon_lbl = QLabel("📁")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 54px; color: #475569;")
        placeholder_layout.addWidget(icon_lbl)

        self.lbl_placeholder_title = QLabel(tr("folders.empty_selection_title"))
        self.lbl_placeholder_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_placeholder_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        placeholder_layout.addWidget(self.lbl_placeholder_title)

        self.lbl_placeholder_desc = QLabel(tr("folders.empty_selection_desc"))
        self.lbl_placeholder_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_placeholder_desc.setStyleSheet("color: #94A3B8; font-size: 13px; max-width: 420px;")
        self.lbl_placeholder_desc.setWordWrap(True)
        placeholder_layout.addWidget(self.lbl_placeholder_desc)

        self.right_stack.addWidget(self.folder_placeholder)

        # Page 1 : Table des fichiers du dossier harmonisée
        self.folder_table_view = QTableView()
        self._setup_track_table_view(self.folder_table_view, self.folder_table_model, "folders")
        self.folder_table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.folder_table_view.customContextMenuRequested.connect(self._on_folder_table_context_menu)
        self.folder_table_view.doubleClicked.connect(self._on_folder_table_view_double_clicked)

        self.right_stack.addWidget(self.folder_table_view)

        # Page 2 : Vue dédiée de la Corbeille (morceaux retirés/ignorés)
        self.trash_container = QWidget()
        trash_main_layout = QVBoxLayout(self.trash_container)
        trash_main_layout.setContentsMargins(0, 0, 0, 0)
        trash_main_layout.setSpacing(10)

        trash_header_frame = QFrame()
        trash_header_frame.setStyleSheet("""
            QFrame {
                background-color: #1A1D24;
                border: 1px solid #282C37;
                border-radius: 8px;
                padding: 8px 12px;
            }
        """)
        trash_header_layout = QHBoxLayout(trash_header_frame)
        trash_header_layout.setContentsMargins(4, 4, 4, 4)
        trash_header_layout.setSpacing(12)

        trash_info_layout = QVBoxLayout()
        trash_info_layout.setSpacing(2)
        lbl_trash_title = QLabel(tr("trash.banner_title"))
        lbl_trash_title.setStyleSheet("color: #F8FAFC; font-size: 13px; font-weight: 700;")
        trash_info_layout.addWidget(lbl_trash_title)

        lbl_trash_desc = QLabel(tr("trash.banner_desc"))
        lbl_trash_desc.setStyleSheet("color: #94A3B8; font-size: 11px;")
        lbl_trash_desc.setWordWrap(True)
        trash_info_layout.addWidget(lbl_trash_desc)
        trash_header_layout.addLayout(trash_info_layout, 1)

        self.btn_restore_selected_trash = QPushButton(tr("trash.btn_restore_selected"))
        self.btn_restore_selected_trash.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restore_selected_trash.setStyleSheet("""
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                border: 1px solid #38BDF8;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0369A1;
            }
        """)
        self.btn_restore_selected_trash.clicked.connect(self._on_restore_selected_trash)
        trash_header_layout.addWidget(self.btn_restore_selected_trash)

        self.btn_clear_all_trash = QPushButton(tr("trash.btn_clear_all"))
        self.btn_clear_all_trash.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_all_trash.setStyleSheet("""
            QPushButton {
                background-color: #20242D;
                color: #F87171;
                border: 1px solid #333846;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7F1D1D;
                color: #FFFFFF;
                border-color: #EF4444;
            }
        """)
        self.btn_clear_all_trash.clicked.connect(self._on_clear_all_trash)
        trash_header_layout.addWidget(self.btn_clear_all_trash)

        trash_main_layout.addWidget(trash_header_frame)

        # Tableau des éléments de la corbeille
        self.trash_table = QTableWidget()
        self.trash_table.setColumnCount(4)
        self.trash_table.setHorizontalHeaderLabels(
            [
                tr("trash.col_filename"),
                tr("trash.col_path"),
                tr("trash.col_deleted_at"),
                tr("trash.col_status"),
            ]
        )
        self.trash_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.trash_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.trash_table.setAlternatingRowColors(True)
        self.trash_table.setShowGrid(False)
        self.trash_table.verticalHeader().setVisible(False)
        self.trash_table.verticalHeader().setDefaultSectionSize(32)

        th_header = self.trash_table.horizontalHeader()
        th_header.setStretchLastSection(False)
        th_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        th_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        th_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        th_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.trash_table.setColumnWidth(0, 280)
        self.trash_table.setColumnWidth(2, 140)
        self.trash_table.setColumnWidth(3, 140)

        self.trash_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.trash_table.customContextMenuRequested.connect(self._on_trash_table_context_menu)
        self.trash_table.doubleClicked.connect(self._on_trash_table_double_clicked)

        trash_main_layout.addWidget(self.trash_table, 1)

        self.right_stack.addWidget(self.trash_container)
        right_layout.addWidget(self.right_stack)

        splitter.addWidget(right_widget)

        # Ratios (1/3 arborescence, 2/3 table) et dimensions initiales
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setSizes([280, 920])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

        main_layout.addWidget(splitter, 1)
        return container

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

    def _on_folder_tree_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        self._select_folder_item(item)

    def _on_folder_tree_current_changed(
        self, current: QTreeWidgetItem | None, previous: QTreeWidgetItem | None
    ) -> None:
        if current:
            self._select_folder_item(current)

    def _select_folder_item(self, item: QTreeWidgetItem) -> None:
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, dict):
            return

        if data.get("is_trash"):
            self.lbl_folder_breadcrumb.setText(f"🗑️  {tr('folders.tree_trash')}")
            self.lbl_folder_breadcrumb.setToolTip(tr("trash.breadcrumb_tooltip"))
            self.cb_recursive.setVisible(False)
            self.folder_search_edit.setVisible(False)
            self.right_stack.setCurrentIndex(2)
            self._load_trash_view()
            return

        if data.get("is_playlist"):
            pl_id = data.get("playlist_id")
            pl_name = data.get("file_name", "Playlist")
            pl_path = data.get("file_path", "")
            self.lbl_folder_breadcrumb.setText(f"🎶  {pl_name}")
            self.lbl_folder_breadcrumb.setToolTip(f"Playlist {str(data.get('format', '')).upper()}\n{pl_path}")
            self.cb_recursive.setVisible(False)
            self.folder_search_edit.setVisible(True)
            self.right_stack.setCurrentIndex(1)
            self.folder_table_model.set_playlist(pl_id)
            cnt = self.folder_table_model.rowCount()
            count_key = "folders.track_count_singular" if cnt == 1 else "folders.track_count"
            self.lbl_folder_count_badge.setText(tr(count_key, count=f"{cnt:,}"))
            return

        self.cb_recursive.setVisible(True)
        self.folder_search_edit.setVisible(True)

        folder_path = data.get("folder_path")
        source_id = data.get("source_id")

        if not folder_path:
            self.right_stack.setCurrentIndex(0)
            self.lbl_folder_breadcrumb.setText("📁  --")
            self.lbl_folder_breadcrumb.setToolTip("")
            self.lbl_folder_count_badge.setText(tr("folders.track_count", count="0"))
            return

        self.lbl_folder_breadcrumb.setText(f"📁  {folder_path}")
        self.lbl_folder_breadcrumb.setToolTip(f"{folder_path}\n({tr('folders.breadcrumb_tooltip')})")
        self.right_stack.setCurrentIndex(1)

        recursive = self.cb_recursive.isChecked()
        self.folder_table_model.set_folder(folder_path, source_id=source_id, recursive=recursive)

        cnt = self.folder_table_model.rowCount()
        count_key = "folders.track_count_singular" if cnt == 1 else "folders.track_count"
        self.lbl_folder_count_badge.setText(tr(count_key, count=f"{cnt:,}"))

    def _on_folder_recursive_toggled(self, checked: bool) -> None:
        item = self.folder_tree.currentItem()
        if item:
            self._select_folder_item(item)

    def _on_folder_search_changed(self, text: str) -> None:
        self._folder_search_timer.start()

    def _perform_folder_search(self) -> None:
        self.folder_table_model.set_search_query(self.folder_search_edit.text())
        cnt = self.folder_table_model.rowCount()
        count_key = "folders.track_count_singular" if cnt == 1 else "folders.track_count"
        self.lbl_folder_count_badge.setText(tr(count_key, count=f"{cnt:,}"))

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
