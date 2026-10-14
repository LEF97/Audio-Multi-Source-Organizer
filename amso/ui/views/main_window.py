"""Fenêtre principale de l'application AMSO en PySide6."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from typing import Optional

from PySide6.QtCore import QPoint, QSize, Qt, QTimer
from PySide6.QtGui import QAction, QCursor, QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from amso.core.config import get_config_path
from amso.core.database import DatabaseManager, SourceRecord, SourceType, TrackRecord, get_default_data_dir
from amso.core.i18n import SUPPORTED_LANGUAGES, get_i18n, tr
from amso.core.scanner import ScanSummary
from amso.ui.models import TrackTableModel
from amso.ui.theme import DARK_THEME_QSS
from amso.ui.workers import ScanWorker


class CollapsibleDrawer(QWidget):
    """Tiroir pliable/dépliable regroupant des boutons de navigation."""

    def __init__(
        self,
        title: str,
        parent: Optional[QWidget] = None,
        initially_expanded: bool = True,
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._is_expanded = initially_expanded

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # En-tête cliquable avec chevron
        self.header_btn = QPushButton()
        self.header_btn.setProperty("class", "drawer-header")
        self.header_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header_btn.clicked.connect(self.toggle)
        layout.addWidget(self.header_btn)

        # Conteneur des éléments enfants du tiroir
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(2)
        layout.addWidget(self.content_widget)

        self._update_header()
        self.content_widget.setVisible(self._is_expanded)

    def set_title(self, title: str) -> None:
        self._title = title
        self._update_header()

    def _update_header(self) -> None:
        arrow = "▼" if self._is_expanded else "▶"
        self.header_btn.setText(f"{arrow}  {self._title.upper()}")

    def toggle(self) -> None:
        self._is_expanded = not self._is_expanded
        self.content_widget.setVisible(self._is_expanded)
        self._update_header()

    def add_widget(self, widget: QWidget) -> None:
        self.content_layout.addWidget(widget)


class MainWindow(QMainWindow):
    """Fenêtre principale de l'organisateur audio multi-source."""

    def __init__(self, db: DatabaseManager) -> None:
        super().__init__()
        self.db = db
        self.scan_worker: Optional[ScanWorker] = None
        self.i18n = get_i18n()

        self.resize(1200, 780)
        self.setMinimumSize(950, 620)

        # Application du style sombre
        self.setStyleSheet(DARK_THEME_QSS)

        # Initialisation du modèle de données virtualisé
        self.table_model = TrackTableModel(db=self.db, parent=self)

        # Construction de l'interface
        self._setup_ui()
        self._setup_status_bar()

        # Enregistrement du callback de changement de langue dynamique
        self.i18n.add_listener(self._on_language_changed)

        # Appliquer les libellés traduits
        self.retranslate_ui()

        # Timer pour recherche incrémentale fluide (debounce de 250ms)
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(250)
        self._search_timer.timeout.connect(self._perform_search)

        # Chargement initial
        self.refresh_sources_list()
        self.table_model.reload_data()
        self._update_track_count()

    def closeEvent(self, event) -> None:
        self.i18n.remove_listener(self._on_language_changed)
        super().closeEvent(event)

    # -------------------------------------------------------------------------
    # Construction de l'interface graphique
    # -------------------------------------------------------------------------

    def _setup_ui(self) -> None:
        central_widget = QWidget(self)
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal, central_widget)
        main_layout.addWidget(splitter)

        # 1. Barre latérale (Sidebar) avec tiroirs
        sidebar = self._create_sidebar()
        splitter.addWidget(sidebar)

        # 2. Zone principale droite (QStackedWidget pour navigation multi-pages)
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)

        # Ratios de largeur du splitter (240px / reste)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

    def _create_sidebar(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("sidebarFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 14, 10, 14)
        layout.setSpacing(8)

        # Logo / Titre AMSO (sous-titre supprimé selon la demande)
        logo = QLabel("🎵  AMSO")
        logo.setObjectName("appLogoLabel")
        layout.addWidget(logo)

        # Zone défilante pour contenir l'ensemble des tiroirs confortablement
        sidebar_scroll = QScrollArea()
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setStyleSheet("background: transparent; border: none;")

        sidebar_container = QWidget()
        drawers_layout = QVBoxLayout(sidebar_container)
        drawers_layout.setContentsMargins(0, 0, 0, 0)
        drawers_layout.setSpacing(8)

        # Groupe exclusif pour les boutons de navigation
        self.nav_button_group = QButtonGroup(self)
        self.nav_button_group.setExclusive(True)

        # 1. Tiroir BIBLIOTHÈQUE
        self.drawer_library = CollapsibleDrawer(tr("sidebar.drawer_library"), initially_expanded=True)
        self.btn_all_tracks = QPushButton(tr("sidebar.nav_all_tracks"))
        self.btn_all_tracks.setProperty("class", "nav-btn")
        self.btn_all_tracks.setCheckable(True)
        self.btn_all_tracks.setChecked(True)
        self.btn_all_tracks.clicked.connect(self._on_all_tracks_clicked)
        self.nav_button_group.addButton(self.btn_all_tracks)
        self.drawer_library.add_widget(self.btn_all_tracks)
        drawers_layout.addWidget(self.drawer_library)

        # 2. Tiroir OUTILS
        self.drawer_tools = CollapsibleDrawer(tr("sidebar.drawer_tools"), initially_expanded=True)
        self.btn_duplicates = QPushButton(tr("sidebar.nav_duplicates"))
        self.btn_duplicates.setProperty("class", "nav-btn")
        self.btn_duplicates.setCheckable(True)
        self.btn_duplicates.clicked.connect(self._on_duplicates_clicked)
        self.nav_button_group.addButton(self.btn_duplicates)
        self.drawer_tools.add_widget(self.btn_duplicates)
        drawers_layout.addWidget(self.drawer_tools)

        # 3. Tiroir STATISTIQUES (Ouvre la page Statistiques)
        self.drawer_stats = CollapsibleDrawer(tr("sidebar.drawer_stats"), initially_expanded=True)
        self.btn_stats_page = QPushButton(tr("sidebar.nav_stats_page"))
        self.btn_stats_page.setProperty("class", "nav-btn")
        self.btn_stats_page.setCheckable(True)
        self.btn_stats_page.clicked.connect(self._on_stats_page_clicked)
        self.nav_button_group.addButton(self.btn_stats_page)
        self.drawer_stats.add_widget(self.btn_stats_page)
        drawers_layout.addWidget(self.drawer_stats)

        # Alias pour compatibilité tests existants
        self.btn_stats = self.btn_stats_page

        # 4. Tiroir SOURCES (Contient les dossiers sources connectés et le bouton d'ajout)
        self.drawer_sources = CollapsibleDrawer(tr("sidebar.drawer_sources"), initially_expanded=True)
        self.sources_container = QWidget()
        self.sources_layout = QVBoxLayout(self.sources_container)
        self.sources_layout.setContentsMargins(0, 0, 0, 0)
        self.sources_layout.setSpacing(2)
        self.drawer_sources.add_widget(self.sources_container)

        self.btn_add_source = QPushButton(tr("sidebar.btn_add_source"))
        self.btn_add_source.setProperty("class", "secondary-btn")
        self.btn_add_source.clicked.connect(self._on_add_local_folder)
        self.drawer_sources.add_widget(self.btn_add_source)
        drawers_layout.addWidget(self.drawer_sources)

        # Espace élastique avant les paramètres
        drawers_layout.addStretch()

        # 5. Tiroir PARAMÈTRES (À la fin, avec la page Général)
        self.drawer_settings = CollapsibleDrawer(tr("sidebar.drawer_settings"), initially_expanded=True)
        self.btn_settings_general = QPushButton(tr("sidebar.nav_settings_general"))
        self.btn_settings_general.setProperty("class", "nav-btn")
        self.btn_settings_general.setCheckable(True)
        self.btn_settings_general.clicked.connect(self._on_settings_general_clicked)
        self.nav_button_group.addButton(self.btn_settings_general)
        self.drawer_settings.add_widget(self.btn_settings_general)
        drawers_layout.addWidget(self.drawer_settings)

        sidebar_scroll.setWidget(sidebar_container)
        layout.addWidget(sidebar_scroll)

        return frame

    def _create_right_panel(self) -> QWidget:
        """Crée la zone principale à onglets/pages (QStackedWidget)."""
        self.stacked_widget = QStackedWidget()

        # Page 0 : Tableau des morceaux (Bibliothèque / Doublons / Sources)
        self.page_tracks = self._create_tracks_page()
        self.stacked_widget.addWidget(self.page_tracks)

        # Page 1 : Vue Statistiques dédiée
        self.page_stats = self._create_stats_page()
        self.stacked_widget.addWidget(self.page_stats)

        # Page 2 : Paramètres > Général (contenant le sélecteur de langue)
        self.page_settings = self._create_settings_page()
        self.stacked_widget.addWidget(self.page_settings)

        return self.stacked_widget

    # -------------------------------------------------------------------------
    # Pages du QStackedWidget
    # -------------------------------------------------------------------------

    def _create_tracks_page(self) -> QWidget:
        """Page du tableau des pistes virtualisé avec barre d'outils."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Barre supérieure (Recherche & Actions)
        top_bar = QFrame()
        top_bar.setObjectName("topBarFrame")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(16, 10, 16, 10)
        top_layout.setSpacing(12)

        self.search_edit = QLineEdit()
        self.search_edit.setObjectName("searchEdit")
        self.search_edit.setPlaceholderText(tr("topbar.search_placeholder"))
        self.search_edit.textChanged.connect(self._on_search_changed)
        top_layout.addWidget(self.search_edit)

        top_layout.addStretch()

        self.track_count_label = QLabel(tr("topbar.track_count", count="0"))
        self.track_count_label.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 500;")
        top_layout.addWidget(self.track_count_label)

        self.btn_scan_all = QPushButton(tr("topbar.btn_scan_all"))
        self.btn_scan_all.setProperty("class", "primary-btn")
        self.btn_scan_all.clicked.connect(self._on_scan_current_source)
        top_layout.addWidget(self.btn_scan_all)

        layout.addWidget(top_bar)

        # Table View virtualisée
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setShowGrid(False)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.verticalHeader().setDefaultSectionSize(32)

        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)        # Titre
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)    # Artiste
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)    # Album
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)          # Durée
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)          # Qualité
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)          # Format
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)          # Source
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)          # Année
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)          # Piste

        header.resizeSection(1, 180)
        header.resizeSection(2, 180)
        header.resizeSection(3, 75)
        header.resizeSection(4, 110)
        header.resizeSection(5, 70)
        header.resizeSection(6, 85)
        header.resizeSection(7, 65)
        header.resizeSection(8, 55)

        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self._on_table_context_menu)

        layout.addWidget(self.table_view)
        return container

    def _create_stats_page(self) -> QWidget:
        """Page dédiée aux statistiques de la bibliothèque."""
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # En-tête de page
        top_bar = QFrame()
        top_bar.setObjectName("topBarFrame")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 12, 20, 12)

        self.lbl_stats_page_title = QLabel(tr("stats.page_title"))
        self.lbl_stats_page_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        top_layout.addWidget(self.lbl_stats_page_title)

        top_layout.addStretch()

        self.btn_refresh_stats = QPushButton(tr("stats.btn_refresh"))
        self.btn_refresh_stats.setProperty("class", "secondary-btn")
        self.btn_refresh_stats.clicked.connect(self._refresh_stats_view)
        top_layout.addWidget(self.btn_refresh_stats)

        main_layout.addWidget(top_bar)

        # Zone de contenu défilante
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)

        # Rangée des 4 cartes KPI
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(12)

        # 1. Total Morceaux
        self.card_tracks = QFrame()
        self.card_tracks.setProperty("class", "dashboard-card")
        l1 = QVBoxLayout(self.card_tracks)
        l1.setContentsMargins(16, 14, 16, 14)
        self.lbl_kpi_tracks_title = QLabel(tr("stats.card_tracks"))
        self.lbl_kpi_tracks_title.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 600;")
        self.kpi_tracks_val = QLabel("0")
        self.kpi_tracks_val.setStyleSheet("color: #38BDF8; font-size: 26px; font-weight: 700;")
        l1.addWidget(self.lbl_kpi_tracks_title)
        l1.addWidget(self.kpi_tracks_val)
        kpi_layout.addWidget(self.card_tracks)

        # 2. Volume Total
        self.card_size = QFrame()
        self.card_size.setProperty("class", "dashboard-card")
        l2 = QVBoxLayout(self.card_size)
        l2.setContentsMargins(16, 14, 16, 14)
        self.lbl_kpi_size_title = QLabel(tr("stats.card_size"))
        self.lbl_kpi_size_title.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 600;")
        self.kpi_size_val = QLabel("0 Go")
        self.kpi_size_val.setStyleSheet("color: #10B981; font-size: 26px; font-weight: 700;")
        l2.addWidget(self.lbl_kpi_size_title)
        l2.addWidget(self.kpi_size_val)
        kpi_layout.addWidget(self.card_size)

        # 3. Durée d'écoute
        self.card_duration = QFrame()
        self.card_duration.setProperty("class", "dashboard-card")
        l3 = QVBoxLayout(self.card_duration)
        l3.setContentsMargins(16, 14, 16, 14)
        self.lbl_kpi_duration_title = QLabel(tr("stats.card_duration"))
        self.lbl_kpi_duration_title.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 600;")
        self.kpi_duration_val = QLabel("0 h")
        self.kpi_duration_val.setStyleSheet("color: #A855F7; font-size: 26px; font-weight: 700;")
        l3.addWidget(self.lbl_kpi_duration_title)
        l3.addWidget(self.kpi_duration_val)
        kpi_layout.addWidget(self.card_duration)

        # 4. Sources connectées
        self.card_sources = QFrame()
        self.card_sources.setProperty("class", "dashboard-card")
        l4 = QVBoxLayout(self.card_sources)
        l4.setContentsMargins(16, 14, 16, 14)
        self.lbl_kpi_sources_title = QLabel(tr("stats.card_sources"))
        self.lbl_kpi_sources_title.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 600;")
        self.kpi_sources_val = QLabel("0")
        self.kpi_sources_val.setStyleSheet("color: #F59E0B; font-size: 26px; font-weight: 700;")
        l4.addWidget(self.lbl_kpi_sources_title)
        l4.addWidget(self.kpi_sources_val)
        kpi_layout.addWidget(self.card_sources)

        content_layout.addLayout(kpi_layout)

        # Cartes de détail (Formats & Sources)
        details_layout = QHBoxLayout()
        details_layout.setSpacing(14)

        # Détail Formats
        card_formats = QFrame()
        card_formats.setProperty("class", "dashboard-card")
        lf = QVBoxLayout(card_formats)
        lf.setContentsMargins(18, 16, 18, 16)
        self.lbl_section_formats = QLabel(tr("stats.section_formats"))
        self.lbl_section_formats.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700; margin-bottom: 8px;")
        lf.addWidget(self.lbl_section_formats)
        self.lbl_formats_breakdown = QLabel()
        self.lbl_formats_breakdown.setStyleSheet("color: #94A3B8; font-size: 13px; line-height: 1.6;")
        lf.addWidget(self.lbl_formats_breakdown)
        lf.addStretch()
        details_layout.addWidget(card_formats, 1)

        # Détail Types de source
        card_src = QFrame()
        card_src.setProperty("class", "dashboard-card")
        ls = QVBoxLayout(card_src)
        ls.setContentsMargins(18, 16, 18, 16)
        self.lbl_section_sources = QLabel(tr("stats.section_sources"))
        self.lbl_section_sources.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700; margin-bottom: 8px;")
        ls.addWidget(self.lbl_section_sources)
        self.lbl_sources_breakdown = QLabel()
        self.lbl_sources_breakdown.setStyleSheet("color: #94A3B8; font-size: 13px; line-height: 1.6;")
        ls.addWidget(self.lbl_sources_breakdown)
        ls.addStretch()
        details_layout.addWidget(card_src, 1)

        content_layout.addLayout(details_layout)
        content_layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        return container

    def _create_settings_page(self) -> QWidget:
        """Page des Paramètres Généraux (contenant le choix de langue)."""
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        top_bar = QFrame()
        top_bar.setObjectName("topBarFrame")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 12, 20, 12)

        self.lbl_settings_title = QLabel(tr("settings.page_title"))
        self.lbl_settings_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        top_layout.addWidget(self.lbl_settings_title)
        top_layout.addStretch()
        main_layout.addWidget(top_bar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)

        # 1. Carte Langue
        card_lang = QFrame()
        card_lang.setProperty("class", "dashboard-card")
        l_lang = QVBoxLayout(card_lang)
        l_lang.setContentsMargins(18, 16, 18, 16)
        l_lang.setSpacing(8)

        self.lbl_card_lang_title = QLabel(tr("settings.section_language"))
        self.lbl_card_lang_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        l_lang.addWidget(self.lbl_card_lang_title)

        self.lbl_card_lang_desc = QLabel(tr("settings.language_desc"))
        self.lbl_card_lang_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        l_lang.addWidget(self.lbl_card_lang_desc)

        self.combo_language = QComboBox()
        self.combo_language.setObjectName("langComboBox")
        self.combo_language.setMaximumWidth(280)

        lang_display = {
            "fr": "🇫🇷  Français",
            "en": "🇬🇧  English",
            "es": "🇪🇸  Español",
            "it": "🇮🇹  Italiano",
            "de": "🇩🇪  Deutsch",
        }
        for code, name in SUPPORTED_LANGUAGES.items():
            disp = lang_display.get(code, f"{code.upper()} - {name}")
            self.combo_language.addItem(disp, userData=code)

        cur_idx = self.combo_language.findData(self.i18n.current_language)
        if cur_idx >= 0:
            self.combo_language.setCurrentIndex(cur_idx)

        self.combo_language.currentIndexChanged.connect(self._on_language_combo_changed)
        l_lang.addWidget(self.combo_language)
        content_layout.addWidget(card_lang)

        # 2. Carte Emplacement des données
        card_storage = QFrame()
        card_storage.setProperty("class", "dashboard-card")
        l_storage = QVBoxLayout(card_storage)
        l_storage.setContentsMargins(18, 16, 18, 16)
        l_storage.setSpacing(8)

        self.lbl_card_storage_title = QLabel(tr("settings.section_storage"))
        self.lbl_card_storage_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        l_storage.addWidget(self.lbl_card_storage_title)

        cfg_p = str(get_config_path())
        db_p = str(self.db.db_path)

        self.lbl_config_path_val = QLabel(f"• <b>{tr('settings.config_file')}</b> <code>{cfg_p}</code>")
        self.lbl_config_path_val.setStyleSheet("color: #94A3B8; font-size: 12px;")
        l_storage.addWidget(self.lbl_config_path_val)

        self.lbl_db_path_val = QLabel(f"• <b>{tr('settings.db_file')}</b> <code>{db_p}</code>")
        self.lbl_db_path_val.setStyleSheet("color: #94A3B8; font-size: 12px;")
        l_storage.addWidget(self.lbl_db_path_val)

        self.btn_open_data_folder = QPushButton(tr("settings.btn_open_folder"))
        self.btn_open_data_folder.setProperty("class", "secondary-btn")
        self.btn_open_data_folder.setMaximumWidth(220)
        self.btn_open_data_folder.clicked.connect(self._on_open_data_folder)
        l_storage.addWidget(self.btn_open_data_folder)

        content_layout.addWidget(card_storage)

        # 3. Carte À Propos
        card_about = QFrame()
        card_about.setProperty("class", "dashboard-card")
        l_about = QVBoxLayout(card_about)
        l_about.setContentsMargins(18, 16, 18, 16)
        l_about.setSpacing(6)

        self.lbl_card_about_title = QLabel(tr("settings.section_about"))
        self.lbl_card_about_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        l_about.addWidget(self.lbl_card_about_title)

        self.lbl_card_about_desc = QLabel(tr("settings.about_desc"))
        self.lbl_card_about_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        l_about.addWidget(self.lbl_card_about_desc)

        ver_lbl = QLabel("Version : 0.1.0 • Licence GPL-3.0 • AMSO Team")
        ver_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
        l_about.addWidget(ver_lbl)

        content_layout.addWidget(card_about)
        content_layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        return container

    def _setup_status_bar(self) -> None:
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_label = QLabel(tr("status.ready"))
        self.status_bar.addWidget(self.status_label, 1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.btn_cancel_scan = QPushButton(tr("status.cancel"))
        self.btn_cancel_scan.setStyleSheet("font-size: 11px; padding: 2px 8px;")
        self.btn_cancel_scan.setVisible(False)
        self.btn_cancel_scan.clicked.connect(self._cancel_current_scan)
        self.status_bar.addPermanentWidget(self.btn_cancel_scan)

    # -------------------------------------------------------------------------
    # Internationalisation & Changement de langue dynamique
    # -------------------------------------------------------------------------

    def retranslate_ui(self) -> None:
        """Applique les traductions de la langue active à l'ensemble de l'interface."""
        self.setWindowTitle(tr("app.window_title"))

        # Tiroirs
        self.drawer_library.set_title(tr("sidebar.drawer_library"))
        self.drawer_tools.set_title(tr("sidebar.drawer_tools"))
        self.drawer_stats.set_title(tr("sidebar.drawer_stats"))
        self.drawer_sources.set_title(tr("sidebar.drawer_sources"))
        self.drawer_settings.set_title(tr("sidebar.drawer_settings"))

        # Boutons de tiroir
        self.btn_all_tracks.setText(tr("sidebar.nav_all_tracks"))
        self.btn_duplicates.setText(tr("sidebar.nav_duplicates"))
        self.btn_stats_page.setText(tr("sidebar.nav_stats_page"))
        self.btn_settings_general.setText(tr("sidebar.nav_settings_general"))
        self.btn_add_source.setText(tr("sidebar.btn_add_source"))

        # Page Morceaux
        self.search_edit.setPlaceholderText(tr("topbar.search_placeholder"))
        self.btn_scan_all.setText(tr("topbar.btn_scan_all"))
        self.btn_cancel_scan.setText(tr("status.cancel"))

        if not (self.scan_worker and self.scan_worker.isRunning()):
            self.status_label.setText(tr("status.ready"))

        self._update_track_count()
        self.table_model.notify_language_changed()

        # Page Statistiques
        self.lbl_stats_page_title.setText(tr("stats.page_title"))
        self.btn_refresh_stats.setText(tr("stats.btn_refresh"))
        self.lbl_kpi_tracks_title.setText(tr("stats.card_tracks"))
        self.lbl_kpi_size_title.setText(tr("stats.card_size"))
        self.lbl_kpi_duration_title.setText(tr("stats.card_duration"))
        self.lbl_kpi_sources_title.setText(tr("stats.card_sources"))
        self.lbl_section_formats.setText(tr("stats.section_formats"))
        self.lbl_section_sources.setText(tr("stats.section_sources"))
        self._refresh_stats_view()

        # Page Paramètres
        self.lbl_settings_title.setText(tr("settings.page_title"))
        self.lbl_card_lang_title.setText(tr("settings.section_language"))
        self.lbl_card_lang_desc.setText(tr("settings.language_desc"))
        self.lbl_card_storage_title.setText(tr("settings.section_storage"))
        self.btn_open_data_folder.setText(tr("settings.btn_open_folder"))
        self.lbl_card_about_title.setText(tr("settings.section_about"))
        self.lbl_card_about_desc.setText(tr("settings.about_desc"))

        cfg_p = str(get_config_path())
        db_p = str(self.db.db_path)
        self.lbl_config_path_val.setText(f"• <b>{tr('settings.config_file')}</b> <code>{cfg_p}</code>")
        self.lbl_db_path_val.setText(f"• <b>{tr('settings.db_file')}</b> <code>{db_p}</code>")

    def _on_language_combo_changed(self, index: int) -> None:
        lang_code = self.combo_language.itemData(index)
        if lang_code and lang_code != self.i18n.current_language:
            self.i18n.set_language(lang_code, save_to_config=True)

    def _on_language_changed(self, lang_code: str) -> None:
        self.combo_language.blockSignals(True)
        idx = self.combo_language.findData(lang_code)
        if idx >= 0:
            self.combo_language.setCurrentIndex(idx)
        self.combo_language.blockSignals(False)

        self.retranslate_ui()

    # -------------------------------------------------------------------------
    # Actions & Événements
    # -------------------------------------------------------------------------

    def refresh_sources_list(self) -> None:
        """Met à jour les boutons de sources dans le tiroir Sources."""
        while self.sources_layout.count():
            item = self.sources_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        sources = self.db.get_sources()
        for src in sources:
            icon_str = "📁" if src.source_type == SourceType.LOCAL else "☁️"
            btn = QPushButton(f"{icon_str}  {src.name}")
            btn.setProperty("class", "nav-btn")
            btn.setCheckable(True)
            btn.setToolTip(src.path_or_uri)
            btn.clicked.connect(lambda checked=False, s=src: self._on_source_selected(s))
            self.nav_button_group.addButton(btn)
            self.sources_layout.addWidget(btn)

    def _on_all_tracks_clicked(self) -> None:
        self.stacked_widget.setCurrentIndex(0)
        self.table_model.set_filter(source_id=None, source_type=None, search_query=self.search_edit.text())
        self._update_track_count()

    def _on_source_selected(self, source: SourceRecord) -> None:
        self.stacked_widget.setCurrentIndex(0)
        self.table_model.set_filter(source_id=source.id, search_query=self.search_edit.text())
        self._update_track_count()

    def _on_duplicates_clicked(self) -> None:
        """Affiche les morceaux identifiés comme doublons stricts ou similaires."""
        self.stacked_widget.setCurrentIndex(0)
        dup_hash = self.db.find_duplicates_by_hash()
        dup_meta = self.db.find_duplicates_by_metadata()

        all_dup_tracks: list[TrackRecord] = []
        seen_ids: set[int] = set()

        for group in dup_hash + dup_meta:
            for t in group:
                if t.id is not None and t.id not in seen_ids:
                    seen_ids.add(t.id)
                    all_dup_tracks.append(t)

        self.table_model.set_tracks(all_dup_tracks)
        self._update_track_count()
        self.status_label.setText(
            tr(
                "status.duplicates_summary",
                hash_count=len(dup_hash),
                meta_count=len(dup_meta),
            )
        )

    def _on_stats_page_clicked(self) -> None:
        """Bascule sur la page dédiée aux statistiques et actualise les chiffres."""
        self.stacked_widget.setCurrentIndex(1)
        self._refresh_stats_view()

    def _refresh_stats_view(self) -> None:
        """Met à jour les cartes et métriques de la page Statistiques."""
        stats = self.db.get_library_stats()
        size_gb = round(stats["total_size_bytes"] / (1024**3), 2)
        duration_hrs = round(stats["total_duration_seconds"] / 3600, 1)

        self.kpi_tracks_val.setText(f"{stats['total_tracks']:,}")
        self.kpi_size_val.setText(f"{size_gb} Go")
        self.kpi_duration_val.setText(f"{duration_hrs} h")
        self.kpi_sources_val.setText(str(stats["total_sources"]))

        # Détail Formats
        if stats["by_format"]:
            fmts_lines = [
                f"• <b>{k.upper()}</b> : {v:,} morceaux"
                for k, v in stats["by_format"].items()
            ]
            self.lbl_formats_breakdown.setText("<br>".join(fmts_lines))
        else:
            self.lbl_formats_breakdown.setText(f"<i>{tr('dialog.stats_none')}</i>")

        # Détail Sources
        if stats["by_source_type"]:
            srcs_lines = [
                f"• <b>{k.capitalize()}</b> : {v:,} morceaux"
                for k, v in stats["by_source_type"].items()
            ]
            self.lbl_sources_breakdown.setText("<br>".join(srcs_lines))
        else:
            self.lbl_sources_breakdown.setText(f"<i>{tr('dialog.stats_none')}</i>")

    def _on_settings_general_clicked(self) -> None:
        """Bascule sur la page des Paramètres Généraux."""
        self.stacked_widget.setCurrentIndex(2)

    def _on_open_data_folder(self) -> None:
        """Ouvre le répertoire de données de l'application dans l'explorateur."""
        data_dir = get_default_data_dir()
        if sys.platform == "win32":
            subprocess.run(f'explorer "{data_dir}"')
        elif sys.platform == "darwin":
            subprocess.run(["open", str(data_dir)])
        else:
            subprocess.run(["xdg-open", str(data_dir)])

    def _on_search_changed(self, text: str) -> None:
        self._search_timer.start()

    def _perform_search(self) -> None:
        query = self.search_edit.text().strip()
        self.table_model.set_filter(search_query=query)
        self._update_track_count()

    def _update_track_count(self) -> None:
        count = self.table_model.rowCount()
        if count <= 1:
            self.track_count_label.setText(tr("topbar.track_count_singular", count=f"{count:,}"))
        else:
            self.track_count_label.setText(tr("topbar.track_count", count=f"{count:,}"))

    def _on_add_local_folder(self) -> None:
        """Permet à l'utilisateur de sélectionner un dossier audio local à ajouter."""
        folder = QFileDialog.getExistingDirectory(
            self,
            tr("dialog.select_folder_title"),
            str(Path.home()),
        )
        if not folder:
            return

        folder_path = Path(folder).resolve()
        source = self.db.add_source(
            source_type=SourceType.LOCAL,
            name=folder_path.name or str(folder_path),
            path_or_uri=folder_path.as_posix(),
        )
        self.refresh_sources_list()

        reply = QMessageBox.question(
            self,
            tr("dialog.scan_prompt_title"),
            tr("dialog.scan_prompt_message", name=folder_path.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._start_scan(source)

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
                self._start_scan(src)
                break

    def _start_scan(self, source: SourceRecord) -> None:
        """Démarre le worker asynchrone de scan."""
        if self.scan_worker and self.scan_worker.isRunning():
            QMessageBox.warning(self, tr("dialog.scan_running_title"), tr("dialog.scan_running_message"))
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.btn_cancel_scan.setVisible(True)
        self.status_label.setText(tr("status.scanning", source=source.name))

        self.scan_worker = ScanWorker(db=self.db, source=source, compute_hash=True, parent=self)
        self.scan_worker.progress.connect(self._on_scan_progress)
        self.scan_worker.status_message.connect(self.status_label.setText)
        self.scan_worker.scan_finished.connect(self._on_scan_finished)
        self.scan_worker.scan_error.connect(self._on_scan_error)
        self.scan_worker.start()

    def _cancel_current_scan(self) -> None:
        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.cancel()
            self.status_label.setText(tr("status.cancelling"))

    def _on_scan_progress(self, current: int, total: int, current_file: str) -> None:
        if total > 0:
            pct = int((current / total) * 100)
            self.progress_bar.setValue(pct)
            fn = Path(current_file).name
            self.status_label.setText(tr("status.indexing", current=current, total=total, file=fn))

    def _on_scan_finished(self, summary: ScanSummary) -> None:
        self.progress_bar.setVisible(False)
        self.btn_cancel_scan.setVisible(False)
        self.refresh_sources_list()
        self.table_model.reload_data()
        self._update_track_count()
        self._refresh_stats_view()

        if summary.cancelled:
            self.status_label.setText(tr("status.cancelled"))
        elif summary.errors and summary.added == 0 and summary.updated == 0 and summary.unchanged == 0:
            err_msg = tr("status.scan_errors", count=len(summary.errors))
            self.status_label.setText(err_msg)
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

    def _on_scan_error(self, err_msg: str) -> None:
        self.progress_bar.setVisible(False)
        self.btn_cancel_scan.setVisible(False)
        self.status_label.setText(tr("status.scan_error", error=err_msg))
        QMessageBox.critical(
            self,
            tr("dialog.scan_error_title"),
            tr("dialog.scan_error_message", error=err_msg),
        )

    # -------------------------------------------------------------------------
    # Menu contextuel du tableau
    # -------------------------------------------------------------------------

    def _on_table_context_menu(self, pos: QPoint) -> None:
        index = self.table_view.indexAt(pos)
        if not index.isValid():
            return

        track: Optional[TrackRecord] = self.table_model.get_track_at(index.row())
        if not track:
            return

        menu = QMenu(self)

        action_open_dir = QAction(tr("context_menu.open_file_location"), self)
        action_open_dir.triggered.connect(lambda: self._open_file_location(track.source_path))
        menu.addAction(action_open_dir)

        menu.addSeparator()

        action_del = QAction(tr("context_menu.delete_track"), self)
        action_del.triggered.connect(lambda: self._delete_track_from_lib(track))
        menu.addAction(action_del)

        menu.exec(QCursor.pos())

    def _open_file_location(self, file_path: Optional[str]) -> None:
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(
                self,
                tr("dialog.file_not_found_title"),
                tr("dialog.file_not_found_message"),
            )
            return

        norm_path = os.path.normpath(file_path)
        if sys.platform == "win32":
            subprocess.run(f'explorer /select,"{norm_path}"')
        elif sys.platform == "darwin":
            subprocess.run(["open", "-R", norm_path])
        else:
            subprocess.run(["xdg-open", os.path.dirname(norm_path)])

    def _delete_track_from_lib(self, track: TrackRecord) -> None:
        if track.id is None:
            return
        reply = QMessageBox.question(
            self,
            tr("dialog.delete_confirm_title"),
            tr("dialog.delete_confirm_message", title=track.title or tr("track.untitled")),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_track(track.id)
            self.table_model.reload_data()
            self._update_track_count()
            self._refresh_stats_view()
