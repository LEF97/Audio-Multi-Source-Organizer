"""Page Dossiers, arbre, corbeille et doublons par dossier (mixin de MainWindow)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTableView,
    QTableWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from amso.core.database import TrackRecord
from amso.core.i18n import tr
from amso.ui.models_base import format_duration
from amso.ui.styles import make_tree_action_button
from amso.ui.views.cover_helper import get_default_cover_pixmap, load_cover_async, load_folder_cover_async
from amso.ui.views.playlist_ui_builder import PlaylistHeaderWidget
from amso.ui.widgets.common import ElidedClickableLabel

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

        # 0. Lecteur et informations de liste de lecture (partagés avec la vue Liste de lecture)
        self.folders_player_header = PlaylistHeaderWidget(
            self.player_service,
            parent=container,
            title_key="sidebar.drawer_library",
        )
        main_layout.addWidget(self.folders_player_header, 0)

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
        self.lbl_folder_breadcrumb = ElidedClickableLabel("📁  --")
        self.lbl_folder_breadcrumb.setObjectName("folderBreadcrumbLabel")
        self.lbl_folder_breadcrumb.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_folder_breadcrumb.clicked.connect(self._on_open_current_folder_explorer)
        top_layout.addWidget(self.lbl_folder_breadcrumb, 1)

        # Badge de décompte des pistes
        self.lbl_folder_count_badge = QLabel("")
        self.lbl_folder_count_badge.setFixedHeight(24)
        self.lbl_folder_count_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_folder_count_badge.setStyleSheet(
            "background-color: #20242D; color: #94A3B8; font-size: 12px; font-weight: 600; padding: 2px 10px; border-radius: 12px;"
        )
        self._update_folder_count_badge(count=0, total_duration_sec=0.0)
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
        left_layout.setContentsMargins(12, 18, 6, 12)
        left_layout.setSpacing(10)

        tree_top_layout = QHBoxLayout()
        tree_top_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_tree_title = QLabel(tr("folders.tree_title"))
        self.lbl_tree_title.setStyleSheet(
            "color: #94A3B8; font-size: 12px; font-weight: 700; text-transform: uppercase;"
        )
        tree_top_layout.addWidget(self.lbl_tree_title)
        tree_top_layout.addStretch()

        self.btn_refresh_tree = make_tree_action_button("🔄", tr("folders.btn_refresh"))
        self.btn_refresh_tree.clicked.connect(self._refresh_folders_tree)
        tree_top_layout.addWidget(self.btn_refresh_tree)

        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderLabels([tr("table.col_folder_name"), tr("folders.tree_col_count")])

        self.btn_expand_tree = make_tree_action_button("⊞", tr("folders.btn_expand_all"))
        self.btn_expand_tree.clicked.connect(lambda: self.folder_tree.expandAll())
        tree_top_layout.addWidget(self.btn_expand_tree)

        self.btn_collapse_tree = make_tree_action_button("⊟", tr("folders.btn_collapse_all"))
        self.btn_collapse_tree.clicked.connect(lambda: self.folder_tree.collapseAll())
        tree_top_layout.addWidget(self.btn_collapse_tree)

        left_layout.addLayout(tree_top_layout)

        # Pochette du titre sélectionné entre le titre de l'arborescence et le tableau Dossier
        cover_row = QHBoxLayout()
        cover_row.setContentsMargins(0, 2, 0, 2)
        cover_row.addStretch()
        self.lbl_folder_selected_cover = QLabel()
        self.lbl_folder_selected_cover.setFixedSize(136, 136)
        self.lbl_folder_selected_cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_folder_selected_cover.setStyleSheet(
            "background-color: #0F172A; border: 1px solid #282C37; border-radius: 10px;"
        )
        self.lbl_folder_selected_cover.setPixmap(get_default_cover_pixmap(136, 10))
        self._folder_cover_target_path: str | None = None
        self._last_folder_selection_key: tuple[Any, ...] | None = None
        cover_row.addWidget(self.lbl_folder_selected_cover)
        cover_row.addStretch()
        left_layout.addLayout(cover_row)

        self.folder_tree.header().setStretchLastSection(False)
        self.folder_tree.header().setMinimumSectionSize(35)
        # Colonnes 240 + 75 px > largeur du panneau (280 px) : la barre horizontale apparaissait et
        # scrollTo() décalait la vue à chaque changement de ligne courante. La colonne du nom
        # absorbe la largeur restante, la barre horizontale est désactivée.
        self.folder_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.folder_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.folder_tree.header().resizeSection(1, 75)
        self.folder_tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.folder_tree.setIndentation(16)
        self.folder_tree.setAnimated(True)
        self.folder_tree.itemClicked.connect(self._on_folder_tree_item_clicked)
        self.folder_tree.currentItemChanged.connect(self._on_folder_tree_current_changed)
        self.folder_tree.itemExpanded.connect(self._on_folder_tree_item_expanded)
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
        self.folder_table_model.modelReset.connect(self._on_folder_model_reset)
        self.folder_table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.folder_table_view.customContextMenuRequested.connect(self._on_folder_table_context_menu)
        self.folder_table_view.doubleClicked.connect(self._on_folder_table_view_double_clicked)
        sel_model = self.folder_table_view.selectionModel()
        if sel_model is not None:
            sel_model.currentRowChanged.connect(self._on_folder_table_current_row_changed)

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
        self.lbl_trash_title = QLabel(tr("trash.banner_title"))
        self.lbl_trash_title.setStyleSheet("color: #F8FAFC; font-size: 13px; font-weight: 700;")
        trash_info_layout.addWidget(self.lbl_trash_title)

        self.lbl_trash_desc = QLabel(tr("trash.banner_desc"))
        self.lbl_trash_desc.setStyleSheet("color: #94A3B8; font-size: 11px;")
        self.lbl_trash_desc.setWordWrap(True)
        trash_info_layout.addWidget(self.lbl_trash_desc)
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
                tr("table.col_filename"),
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

    def _on_folder_tree_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        self._select_folder_item(item)

    def _on_folder_tree_current_changed(
        self, current: QTreeWidgetItem | None, previous: QTreeWidgetItem | None
    ) -> None:
        if current:
            self._select_folder_item(current)

    def _node_selection_key(self, data: dict[str, Any]) -> tuple[Any, ...]:
        """Retourne une clé stable identifiant un nœud de l'arborescence."""
        if data.get("is_trash"):
            return ("trash",)
        if data.get("is_playlist_album"):
            return ("playlist_album", data.get("playlist_id"), str(data.get("album", "")))
        if data.get("is_playlist"):
            return ("playlist", data.get("playlist_id"))
        return ("folder", data.get("source_id"), data.get("folder_path"))

    def _select_first_folder_track(self) -> None:
        """Sélectionne le premier titre du tableau de droite et remonte l'ascenseur en haut."""
        if self.folder_table_model.rowCount() > 0:
            self.folder_table_view.selectRow(0)
            self.folder_table_view.scrollToTop()
            self._update_folder_selected_cover(self.folder_table_model.get_track_at(0))
        else:
            self._update_folder_selected_cover(None)

    def _on_folder_table_current_row_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        """Met à jour la pochette affichée à gauche quand le titre sélectionné change."""
        track = self.folder_table_model.get_track_at(current.row()) if current.isValid() else None
        self._update_folder_selected_cover(track)

    def _get_folder_fallback_track_paths(self, folder_path: str, source_id: int | None) -> list[str]:
        """Retourne jusqu'à 3 chemins de pistes (dossier ou playlists contenues) pour extraire une pochette."""
        fallback_tracks = self.db.get_tracks_by_folder(
            folder_path=folder_path,
            source_id=source_id,
            recursive=True,
            limit=3,
        )
        paths = [p for t in fallback_tracks if (p := (t.source_path or t.source_ref))]
        if paths or source_id is None:
            return paths

        fp_prefix = folder_path.replace("\\", "/").rstrip("/").lower()
        for pl in self.db.get_playlists(source_id=source_id):
            pl_fp = (pl.file_path or "").replace("\\", "/").lower()
            if pl_fp == fp_prefix or pl_fp.startswith(f"{fp_prefix}/"):
                pl_tracks = self.db.get_playlist_tracks(pl.id)
                paths = [p for t in pl_tracks[:3] if (p := (t.source_path or t.source_ref))]
                if paths:
                    return paths
        return []

    def _update_folder_selected_cover(self, track: TrackRecord | None) -> None:
        """Charge de façon asynchrone la pochette du titre sélectionné ou du dossier actif."""
        if not hasattr(self, "lbl_folder_selected_cover"):
            return
        folder_path = getattr(self, "_current_selected_folder_path", None)
        if track is not None:
            self._folder_cover_target_path = track.source_path or track.source_ref
            pix = load_cover_async(track, size=136, radius=10, callback=self._on_folder_cover_loaded)
        elif folder_path:
            self._folder_cover_target_path = folder_path
            source_id = getattr(self, "_current_selected_source_id", None)
            fallback_paths = self._get_folder_fallback_track_paths(folder_path, source_id)
            pix = load_folder_cover_async(
                folder_path,
                size=136,
                radius=10,
                callback=self._on_folder_cover_loaded,
                fallback_track_paths=fallback_paths,
            )
        else:
            self._folder_cover_target_path = None
            pix = get_default_cover_pixmap(136, 10)
        self.lbl_folder_selected_cover.setPixmap(pix)

    def _on_folder_cover_loaded(self, path: str, pixmap: QPixmap) -> None:
        """Applique la pochette chargée en arrière-plan si la sélection est toujours la même."""
        if path == getattr(self, "_folder_cover_target_path", None) and hasattr(self, "lbl_folder_selected_cover"):
            self.lbl_folder_selected_cover.setPixmap(pixmap)

    def _select_folder_item(self, item: QTreeWidgetItem) -> None:
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, dict):
            return

        node_key = self._node_selection_key(data)
        if getattr(self, "_last_folder_selection_key", None) == node_key:
            return
        self._last_folder_selection_key = node_key

        if data.get("is_trash"):
            self._current_selected_folder_path = None
            self.lbl_folder_breadcrumb.setText(f"🗑️  {tr('folders.tree_trash')}")
            self.lbl_folder_breadcrumb.setToolTip(tr("trash.breadcrumb_tooltip"))
            self.cb_recursive.setVisible(False)
            self.folder_search_edit.setVisible(False)
            self.right_stack.setCurrentIndex(2)
            self._load_trash_view()
            self._update_folder_selected_cover(None)
            return

        if data.get("is_playlist_album"):
            self._current_selected_folder_path = None
            pl_id = data.get("playlist_id")
            pl_name = data.get("file_name", "Playlist")
            pl_path = data.get("file_path", "")
            album_raw = str(data.get("album", ""))
            album_label = album_raw if album_raw else tr("folders.unknown_album")
            self.lbl_folder_breadcrumb.setText(f"🎶  {pl_name}  ›  📁  {album_label}")
            self.lbl_folder_breadcrumb.setToolTip(f"{album_label}\n{pl_path}")
            self.cb_recursive.setVisible(False)
            self.folder_search_edit.setVisible(True)
            self.right_stack.setCurrentIndex(1)
            self.folder_table_model.set_playlist(pl_id, album=album_raw)
            self._update_folder_count_badge()
            self._select_first_folder_track()
            return

        if data.get("is_playlist"):
            self._current_selected_folder_path = None
            pl_id = data.get("playlist_id")
            pl_name = data.get("file_name", "Playlist")
            pl_path = data.get("file_path", "")
            pl_format = str(data.get("format", ""))
            is_cue = pl_format.lower() == "cue"
            kind = "Feuille CUE" if is_cue else f"Playlist {pl_format.upper()}"
            self.lbl_folder_breadcrumb.setText(f"{'💿' if is_cue else '🎶'}  {pl_name}")
            self.lbl_folder_breadcrumb.setToolTip(f"{kind}\n{pl_path}")
            self.cb_recursive.setVisible(False)
            self.folder_search_edit.setVisible(True)
            self.right_stack.setCurrentIndex(1)
            self.folder_table_model.set_playlist(pl_id)
            self._update_folder_count_badge()
            self._select_first_folder_track()
            return

        self.cb_recursive.setVisible(True)
        self.folder_search_edit.setVisible(True)

        folder_path = data.get("folder_path")
        source_id = data.get("source_id")

        if not folder_path:
            self._current_selected_folder_path = None
            self.right_stack.setCurrentIndex(0)
            self.lbl_folder_breadcrumb.setText("📁  --")
            self.lbl_folder_breadcrumb.setToolTip("")
            self._update_folder_count_badge(count=0, total_duration_sec=0.0)
            self._update_folder_selected_cover(None)
            return

        self._current_selected_folder_path = str(folder_path)
        self._current_selected_source_id = source_id

        self.lbl_folder_breadcrumb.setText(f"📁  {folder_path}")
        self.lbl_folder_breadcrumb.setToolTip(f"{folder_path}\n({tr('folders.breadcrumb_tooltip')})")
        self.right_stack.setCurrentIndex(1)

        recursive = self.cb_recursive.isChecked()
        self.folder_table_model.set_folder(folder_path, source_id=source_id, recursive=recursive)

        self._update_folder_count_badge()
        self._select_first_folder_track()

    def scroll_folder_table_to_current_track(self) -> None:
        """Positionne le défilement du tableau de la bibliothèque sur le titre actif sans modifier la sélection."""
        if not hasattr(self, "folder_table_model") or not hasattr(self, "folder_table_view"):
            return
        row = self.folder_table_model.current_track_row()
        if 0 <= row < self.folder_table_model.rowCount():
            model_idx = self.folder_table_model.index(row, 0)
            self.folder_table_view.scrollTo(model_idx, QAbstractItemView.ScrollHint.PositionAtCenter)

    def _on_folder_recursive_toggled(self, checked: bool) -> None:
        self._last_folder_selection_key = None
        item = self.folder_tree.currentItem()
        if item:
            self._select_folder_item(item)

    def _on_folder_search_changed(self, text: str) -> None:
        self._folder_search_timer.start()

    def _perform_folder_search(self) -> None:
        self.folder_table_model.set_search_query(self.folder_search_edit.text())
        self._update_folder_count_badge()

    def _update_folder_count_badge(
        self,
        count: int | None = None,
        total_duration_sec: float | None = None,
    ) -> None:
        """Met à jour le badge de décompte et de durée totale de la bibliothèque."""
        if count is None:
            cnt = self.folder_table_model.rowCount()
            dur_sec = self.folder_table_model.total_duration_seconds()
        else:
            cnt = count
            dur_sec = total_duration_sec or 0.0

        dur_str = format_duration(dur_sec)
        key = "playlist.stats_count_singular" if cnt == 1 else "playlist.stats_count"
        self.lbl_folder_count_badge.setText(tr(key, count=f"{cnt:,}", duration=dur_str))

    def _on_folder_model_reset(self) -> None:
        """Synchronise le badge lorsque le modèle de la bibliothèque est réinitialisé."""
        if hasattr(self, "right_stack") and self.right_stack.currentIndex() == 2:
            return
        self._update_folder_count_badge()
