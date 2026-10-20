"""Fenêtre principale de l'application AMSO en PySide6."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from typing import Any, cast

from PySide6.QtCore import QAbstractTableModel, QPoint, QSettings, Qt, QTimer
from PySide6.QtGui import QAction, QCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QDialog,
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
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from amso.core.config import get_config_manager
from amso.core.database import (
    DatabaseManager,
    SourceRecord,
    SourceType,
    TrackRecord,
    get_default_data_dir,
)
from amso.core.i18n import get_i18n, tr
from amso.core.scheduler import SyncScheduler
from amso.services.player_service import PlayerService
from amso.services.sleep_inhibitor import SleepInhibitor
from amso.services.update_checker import UpdateCheckerWorker
from amso.ui.dialogs.delete_track_dialog import DeleteTrackDialog, send_file_to_trash
from amso.ui.dialogs.large_selection_dialog import LargeSelectionDialog
from amso.ui.dialogs.source_config_dialog import SourceConfigDialog
from amso.ui.dialogs.vlc_download_dialog import VlcDownloadDialog
from amso.ui.models import FolderTrackTableModel, TrackTableModel
from amso.ui.pages.folders_page import FoldersPageMixin
from amso.ui.pages.retranslate import RetranslateMixin
from amso.ui.pages.scan_controller import ScanControllerMixin
from amso.ui.pages.session_state import SessionStateMixin
from amso.ui.pages.settings_about import SettingsAboutPageMixin
from amso.ui.pages.settings_general import SettingsGeneralPageMixin
from amso.ui.pages.settings_player import SettingsPlayerPageMixin
from amso.ui.pages.settings_sources import SettingsSourcesPageMixin
from amso.ui.pages.stats_page import StatsPageMixin
from amso.ui.pages.update_controller import UpdateControllerMixin
from amso.ui.theme import DARK_THEME_QSS
from amso.ui.views.activity_feed_popover import ActivityFeedPopover
from amso.ui.views.blind_test_view import BlindTestView
from amso.ui.views.logs_view import LogsView
from amso.ui.views.player_view import PlayerView
from amso.ui.views.playlist_view import PlaylistView
from amso.ui.views.update_banner import UpdateBannerWidget
from amso.ui.widgets.common import ClickableLabel, CollapsibleDrawer, HoverBadgeButton
from amso.ui.workers import ScanWorker

logger = logging.getLogger(__name__)


class MainWindow(SettingsPlayerPageMixin, SettingsAboutPageMixin, StatsPageMixin, SettingsGeneralPageMixin, SettingsSourcesPageMixin, ScanControllerMixin, FoldersPageMixin, UpdateControllerMixin, SessionStateMixin, RetranslateMixin, QMainWindow):
    """Fenêtre principale de l'organisateur audio multi-source."""

    def __init__(
        self,
        db: DatabaseManager,
        progress_callback: Any | None = None,
    ) -> None:
        super().__init__()
        self.db = db
        self.scan_worker: ScanWorker | None = None
        self._current_scanning_source_id: int | None = None
        self.i18n = get_i18n()

        self.resize(1200, 780)
        self.setMinimumSize(950, 620)

        # Application du style sombre et de l'icône officielle
        self.setStyleSheet(DARK_THEME_QSS)
        from amso.ui.theme import get_app_icon

        self.setWindowIcon(get_app_icon())

        # Initialisation des modèles de données virtualisés
        self.table_model = TrackTableModel(db=self.db, parent=self)
        self.folder_table_model = FolderTrackTableModel(db=self.db, parent=self)

        # Service audio central python-vlc
        if progress_callback:
            progress_callback(45, tr("splash.loading_audio"))
        self.player_service = PlayerService(parent=self)
        self._player_state: str = "stopped"
        self.player_service.error_occurred.connect(self._on_player_error)
        self.player_service.state_changed.connect(self._on_player_state_changed)
        self.player_service.track_changed.connect(self._on_player_track_changed_for_save)
        self.player_service.playlist_updated.connect(self._on_playlist_updated_for_save)

        # Sauvegarde automatique asynchrone et debouncée de la playlist (2000 ms / 2s)
        self._playlist_save_timer = QTimer(self)
        self._playlist_save_timer.setSingleShot(True)
        self._playlist_save_timer.setInterval(2000)
        self._playlist_save_timer.timeout.connect(lambda: self._save_current_playlist(immediate=False))

        # Planificateur de synchronisation automatique (Démarrage, Périodique, En continu)
        self.scheduler = SyncScheduler(self.db, parent=self)
        self.scheduler.request_scan.connect(self._on_scheduler_request_scan)

        # Suivi de l'état de vérification des mises à jour
        self._last_update_check: dict[str, Any] = {
            "status": "pending",
            "version": "",
            "date": "",
            "url": "",
            "checked_at": None,
        }

        # Construction de l'interface
        if progress_callback:
            progress_callback(60, tr("splash.loading_ui"))
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_status_bar()

        # Démarrage du planificateur
        self.scheduler.start()

        # Enregistrement du callback de changement de langue dynamique
        self.i18n.add_listener(self._on_language_changed)

        # Appliquer les libellés traduits
        self.retranslate_ui()

        # Timers pour recherche incrémentale fluide (debounce de 250ms)
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(250)
        self._search_timer.timeout.connect(self._perform_search)

        self._folder_search_timer = QTimer(self)
        self._folder_search_timer.setSingleShot(True)
        self._folder_search_timer.setInterval(250)
        self._folder_search_timer.timeout.connect(self._perform_folder_search)

        # Drapeaux de rafraîchissement différé (Lazy Updates pour dissociation totale du lecteur)
        self._tracks_dirty: bool = False
        self._folders_dirty: bool = False
        self._stats_dirty: bool = False
        self._sources_dirty: bool = False
        self._last_scan_progress_time: float = 0.0

        # Chargement initial
        if progress_callback:
            progress_callback(75, tr("splash.loading_library"))
        self._current_active_page: str = "player"
        self.refresh_sources_list()
        self._refresh_folders_tree()
        self.table_model.reload_data()
        self._update_track_count()

        if progress_callback:
            progress_callback(90, tr("splash.restoring_session"))
        self._restore_saved_playlist()
        self._restore_active_page()

        # Vérification non-bloquante des mises à jour en tâche de fond (différée de 3,5s)
        self.update_worker: UpdateCheckerWorker | None = None
        QTimer.singleShot(3500, lambda: self._check_for_updates(manual=False))

        # Vérification périodique toutes les 24h
        self._update_timer = QTimer(self)
        self._update_timer.setInterval(24 * 3600 * 1000)
        self._update_timer.timeout.connect(lambda: self._check_for_updates(manual=False))
        self._update_timer.start()

    def closeEvent(self, event) -> None:
        SleepInhibitor.release()
        if hasattr(self, "_playlist_save_timer") and self._playlist_save_timer.isActive():
            self._playlist_save_timer.stop()
        self._save_all_tables_state()
        self._save_player_state()
        self._save_current_playlist(immediate=True)
        if hasattr(self, "scheduler") and self.scheduler:
            self.scheduler.stop()
        if hasattr(self, "player_service") and self.player_service:
            self.player_service.stop()
        if hasattr(self, "update_worker") and self.update_worker and getattr(self.update_worker, "isRunning", lambda: False)():
            if hasattr(self.update_worker, "cancel"):
                self.update_worker.cancel()
            if hasattr(self.update_worker, "wait"):
                self.update_worker.wait(1000)
        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.cancel()
            self.scan_worker.wait(2000)
        self.i18n.remove_listener(self._on_language_changed)
        if hasattr(self, "db") and self.db:
            try:
                self.db.close()
            except Exception:
                pass
        super().closeEvent(event)

    def _setup_ui(self) -> None:
        central_widget = QWidget(self)
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal, central_widget)
        main_layout.addWidget(splitter, 1)

        # 1. Barre latérale (Sidebar) avec tiroirs
        sidebar = self._create_sidebar()
        splitter.addWidget(sidebar)

        # 2. Zone principale droite (QStackedWidget pour navigation multi-pages)
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)

        # Ratios de largeur du splitter (240px / reste)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        # 3. Bannière discrète de mise à jour (placée juste au-dessus de la barre d'état)
        self.update_banner = UpdateBannerWidget(central_widget)
        main_layout.addWidget(self.update_banner, 0)

    def _create_sidebar(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("sidebarFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 14, 10, 14)
        layout.setSpacing(8)

        # Logo officiel AMSO grand format (le logo intégrant directement le nom AMSO)
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(4, 10, 4, 12)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        from amso.ui.theme import get_app_logo_pixmap

        icon_pm = get_app_logo_pixmap()
        self.lbl_logo_icon = ClickableLabel()
        self.lbl_logo_icon.setObjectName("sidebarLogo")
        self.lbl_logo_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_logo_icon.setToolTip(tr("dialog.about_title") + " (F1)")
        self.lbl_logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if not icon_pm.isNull():
            # Affiche l'image en grand format (120x120) avec lissage haute qualité
            scaled_pm = icon_pm.scaled(
                120,
                120,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.lbl_logo_icon.setPixmap(scaled_pm)
        else:
            self.lbl_logo_icon.setText("🎵")
            self.lbl_logo_icon.setStyleSheet("font-size: 48px; color: #38BDF8;")

        self.lbl_logo_icon.clicked.connect(self._on_settings_about_clicked)
        logo_layout.addWidget(self.lbl_logo_icon)

        # Alias de compatibilité pour les tests
        self.btn_quick_about = self.lbl_logo_icon

        layout.addLayout(logo_layout)

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

        # 0. Tiroir LECTEUR (En première position)
        self.drawer_player = CollapsibleDrawer(tr("sidebar.drawer_player"), initially_expanded=True)
        self.btn_player = QPushButton(tr("sidebar.nav_player"))
        self.btn_player.setProperty("class", "nav-btn")
        self.btn_player.setCheckable(True)
        self.btn_player.clicked.connect(self._on_player_nav_clicked)
        self.nav_button_group.addButton(self.btn_player)
        self.drawer_player.add_widget(self.btn_player)

        self.btn_playlist = QPushButton(tr("sidebar.nav_playlist"))
        self.btn_playlist.setProperty("class", "nav-btn")
        self.btn_playlist.setCheckable(True)
        self.btn_playlist.clicked.connect(self._on_playlist_nav_clicked)
        self.nav_button_group.addButton(self.btn_playlist)
        self.drawer_player.add_widget(self.btn_playlist)
        drawers_layout.addWidget(self.drawer_player)

        # 0b. Tiroir JEUX (Dédié au Blind Test, sous le tiroir Lecteur, fermé par défaut)
        self.drawer_games = CollapsibleDrawer(tr("sidebar.drawer_games"), initially_expanded=False)
        self.btn_blind_test = QPushButton(tr("sidebar.nav_blind_test"))
        self.btn_blind_test.setProperty("class", "nav-btn")
        self.btn_blind_test.setCheckable(True)
        self.btn_blind_test.clicked.connect(self._on_blind_test_nav_clicked)
        self.nav_button_group.addButton(self.btn_blind_test)
        self.drawer_games.add_widget(self.btn_blind_test)
        drawers_layout.addWidget(self.drawer_games)

        # 1. Tiroir BIBLIOTHÈQUE (fermé par défaut)
        self.drawer_library = CollapsibleDrawer(tr("sidebar.drawer_library"), initially_expanded=False)
        self.btn_all_tracks = QPushButton(tr("sidebar.nav_all_tracks"))
        self.btn_all_tracks.setProperty("class", "nav-btn")
        self.btn_all_tracks.setCheckable(True)
        self.btn_all_tracks.setChecked(True)
        self.btn_all_tracks.clicked.connect(self._on_all_tracks_clicked)
        self.nav_button_group.addButton(self.btn_all_tracks)
        self.drawer_library.add_widget(self.btn_all_tracks)

        self.btn_by_folder = QPushButton(tr("sidebar.nav_by_folder"))
        self.btn_by_folder.setProperty("class", "nav-btn")
        self.btn_by_folder.setCheckable(True)
        self.btn_by_folder.clicked.connect(self._on_by_folder_clicked)
        self.nav_button_group.addButton(self.btn_by_folder)
        self.drawer_library.add_widget(self.btn_by_folder)
        drawers_layout.addWidget(self.drawer_library)

        # 2. Tiroir OUTILS (fermé par défaut)
        self.drawer_tools = CollapsibleDrawer(tr("sidebar.drawer_tools"), initially_expanded=False)
        self.btn_duplicates = QPushButton(tr("sidebar.nav_duplicates"))
        self.btn_duplicates.setProperty("class", "nav-btn")
        self.btn_duplicates.setCheckable(True)
        self.btn_duplicates.clicked.connect(self._on_duplicates_clicked)
        self.nav_button_group.addButton(self.btn_duplicates)
        self.drawer_tools.add_widget(self.btn_duplicates)
        drawers_layout.addWidget(self.drawer_tools)

        # 3. Tiroir STATISTIQUES (fermé par défaut)
        self.drawer_stats = CollapsibleDrawer(tr("sidebar.drawer_stats"), initially_expanded=False)
        self.btn_stats_page = QPushButton(tr("sidebar.nav_stats_page"))
        self.btn_stats_page.setProperty("class", "nav-btn")
        self.btn_stats_page.setCheckable(True)
        self.btn_stats_page.clicked.connect(self._on_stats_page_clicked)
        self.nav_button_group.addButton(self.btn_stats_page)
        self.drawer_stats.add_widget(self.btn_stats_page)
        drawers_layout.addWidget(self.drawer_stats)

        # Alias pour compatibilité tests existants
        self.btn_stats = self.btn_stats_page

        # 4. Tiroir SOURCES (fermé par défaut)
        self.drawer_sources = CollapsibleDrawer(tr("sidebar.drawer_sources"), initially_expanded=False)
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

        # 5. Tiroir PARAMÈTRES (Ordre : général, lecteur, sources, logs, à propos, fermé par défaut)
        self.drawer_settings = CollapsibleDrawer(tr("sidebar.drawer_settings"), initially_expanded=False)

        # 1. Général
        self.btn_settings_general = QPushButton(tr("sidebar.nav_settings_general"))
        self.btn_settings_general.setProperty("class", "nav-btn")
        self.btn_settings_general.setCheckable(True)
        self.btn_settings_general.clicked.connect(self._on_settings_general_clicked)
        self.nav_button_group.addButton(self.btn_settings_general)
        self.drawer_settings.add_widget(self.btn_settings_general)

        # 2. Lecteur
        self.btn_settings_player = QPushButton(tr("sidebar.nav_settings_player"))
        self.btn_settings_player.setProperty("class", "nav-btn")
        self.btn_settings_player.setCheckable(True)
        self.btn_settings_player.clicked.connect(self._on_settings_player_clicked)
        self.nav_button_group.addButton(self.btn_settings_player)
        self.drawer_settings.add_widget(self.btn_settings_player)

        # 3. Sources
        self.btn_settings_sources = QPushButton(tr("sidebar.nav_settings_sources"))
        self.btn_settings_sources.setProperty("class", "nav-btn")
        self.btn_settings_sources.setCheckable(True)
        self.btn_settings_sources.clicked.connect(self._on_settings_sources_clicked)
        self.nav_button_group.addButton(self.btn_settings_sources)
        self.drawer_settings.add_widget(self.btn_settings_sources)

        # 4. Logs
        self.btn_settings_logs = QPushButton(tr("sidebar.nav_settings_logs"))
        self.btn_settings_logs.setProperty("class", "nav-btn")
        self.btn_settings_logs.setCheckable(True)
        self.btn_settings_logs.clicked.connect(self._on_settings_logs_clicked)
        self.nav_button_group.addButton(self.btn_settings_logs)
        self.drawer_settings.add_widget(self.btn_settings_logs)

        # 5. À propos
        self.btn_settings_about = QPushButton(tr("sidebar.nav_settings_about"))
        self.btn_settings_about.setProperty("class", "nav-btn")
        self.btn_settings_about.setCheckable(True)
        self.btn_settings_about.clicked.connect(self._on_settings_about_clicked)
        self.nav_button_group.addButton(self.btn_settings_about)
        self.drawer_settings.add_widget(self.btn_settings_about)

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

        # Page 2 : Paramètres > Général (contenant le sélecteur de langue, stockage, à propos)
        self.page_settings = self._create_settings_page()
        self.stacked_widget.addWidget(self.page_settings)

        # Page 3 : Vue Par dossiers (Navigation arborescente des sources)
        self.page_folders = self._create_folders_page()
        self.stacked_widget.addWidget(self.page_folders)

        # Page 4 : Paramètres > Sources (Configuration des sources et synchronisation)
        self.page_settings_sources = self._create_settings_sources_page()
        self.stacked_widget.addWidget(self.page_settings_sources)

        # Page 5 : Vue Lecteur audio grand format
        self.page_player = PlayerView(self.player_service, parent=self)
        self.page_player.effect_changed.connect(self._sync_visual_effect_radio)
        self.page_player.add_folder_requested.connect(self._on_add_local_folder)
        self.stacked_widget.addWidget(self.page_player)

        # Page 5b : Vue Blind Test (Intercalée entre Lecteur et Playlist)
        self.page_blind_test = BlindTestView(self.player_service, parent=self)
        self.page_blind_test.effect_changed.connect(self._sync_visual_effect_radio)
        self.stacked_widget.addWidget(self.page_blind_test)

        # Page 6 : Vue Playlist (Mini-lecteur + Tableau de file d'attente)
        self.page_playlist = PlaylistView(self.player_service, parent=self)
        self.stacked_widget.addWidget(self.page_playlist)

        # Page 7 : Paramètres > Logs (Journal d'activité et événements)
        self.page_logs = LogsView(self.db, parent=self)
        self.stacked_widget.addWidget(self.page_logs)

        # Page 8 : Paramètres > Lecteur (Options d'alimentation, veille et moteur audio)
        self.page_settings_player = self._create_settings_player_page()
        self.stacked_widget.addWidget(self.page_settings_player)

        # Page 9 : Paramètres > À propos (Présentation, crédits et liens de soutien)
        self.page_settings_about = self._create_settings_about_page()
        self.stacked_widget.addWidget(self.page_settings_about)

        # Réaction dynamique au changement d'onglet (ex: gestion du maintien écran sur Lecteur et Playlist)
        self.stacked_widget.currentChanged.connect(self._on_current_page_changed)

        return self.stacked_widget

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Gestion unifiée des tableaux de pistes (Colonnes, Tri, Visibilité, Déplacement)
    # -------------------------------------------------------------------------

    def _setup_track_table_view(self, table_view: QTableView, model: QAbstractTableModel, storage_key: str) -> None:
        """Harmonise et configure un QTableView de pistes :
        - Modèle virtualisé avec l'ensemble des 29 champs de la BDD.
        - Tri activé par clic d'en-tête.
        - Colonnes redimensionnables (Interactive).
        - Colonnes déplaçables par glisser-déposer (setSectionsMovable(True)).
        - Menu contextuel d'en-tête pour masquer / afficher des colonnes.
        - Sauvegarde et restauration persistante dans QSettings.
        """
        table_view.setModel(model)
        table_view.setSortingEnabled(True)
        table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        table_view.setAlternatingRowColors(True)
        table_view.setShowGrid(False)
        table_view.verticalHeader().setVisible(False)
        table_view.verticalHeader().setDefaultSectionSize(32)

        header = table_view.horizontalHeader()
        header.setSectionsMovable(True)
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(35)
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(
            lambda pos, tv=table_view, m=model, key=storage_key: self._on_table_header_context_menu(pos, tv, m, key)
        )

        for col_idx in range(model.columnCount()):
            header.setSectionResizeMode(col_idx, QHeaderView.ResizeMode.Interactive)

        # Restauration de l'état (largeurs, ordre, masquage) ou application des valeurs par défaut
        if not self._restore_table_header_state(table_view, storage_key):
            columns = getattr(model, "COLUMNS", [])
            for col_idx, col_def in enumerate(columns):
                header.resizeSection(col_idx, col_def[2])
                table_view.setColumnHidden(col_idx, not col_def[3])

        header.sectionResized.connect(lambda *_: self._save_table_header_state(table_view, storage_key))
        header.sectionMoved.connect(lambda *_: self._save_table_header_state(table_view, storage_key))
        header.sortIndicatorChanged.connect(lambda *_: self._save_table_header_state(table_view, storage_key))

    def _on_table_header_context_menu(
        self,
        pos: QPoint,
        table_view: QTableView,
        model: QAbstractTableModel,
        storage_key: str,
    ) -> None:
        header = table_view.horizontalHeader()
        menu = self._build_columns_menu(table_view, model, storage_key)
        menu.exec(header.mapToGlobal(pos))

    def _open_columns_menu(
        self,
        button: QPushButton,
        table_view: QTableView,
        model: QAbstractTableModel,
        storage_key: str,
    ) -> None:
        menu = self._build_columns_menu(table_view, model, storage_key)
        pos = QPoint(0, button.height())
        menu.exec(button.mapToGlobal(pos))

    def _build_columns_menu(
        self,
        table_view: QTableView,
        model: QAbstractTableModel,
        storage_key: str,
    ) -> QMenu:
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background-color: #1A1D24; color: #E2E8F0; border: 1px solid #282C37; padding: 4px; }"
            "QMenu::item:selected { background-color: #0284C7; }"
        )

        act_show_all = QAction(tr("table.menu_show_all"), menu)
        act_show_all.triggered.connect(lambda: self._show_all_columns(table_view, storage_key))
        menu.addAction(act_show_all)

        act_reset = QAction(tr("table.menu_reset_columns"), menu)
        act_reset.triggered.connect(lambda: self._reset_default_columns(table_view, storage_key))
        menu.addAction(act_reset)

        menu.addSeparator()

        title_act = QAction(f"— {tr('table.menu_columns')} —", menu)
        title_act.setEnabled(False)
        menu.addAction(title_act)

        for col_idx in range(model.columnCount()):
            col_name = model.headerData(col_idx, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            if not col_name:
                continue
            act = QAction(col_name, menu)
            act.setCheckable(True)
            act.setChecked(not table_view.isColumnHidden(col_idx))
            act.toggled.connect(
                lambda checked, c=col_idx, tv=table_view, sk=storage_key: self._toggle_table_column(tv, c, checked, sk)
            )
            menu.addAction(act)

        return menu

    def _toggle_table_column(self, table_view: QTableView, col_idx: int, visible: bool, storage_key: str) -> None:
        table_view.setColumnHidden(col_idx, not visible)
        self._save_table_header_state(table_view, storage_key)

    def _show_all_columns(self, table_view: QTableView, storage_key: str) -> None:
        for c in range(table_view.model().columnCount()):
            table_view.setColumnHidden(c, False)
        self._save_table_header_state(table_view, storage_key)

    def _reset_default_columns(self, table_view: QTableView, storage_key: str) -> None:
        model = cast(Any, table_view.model())
        header = table_view.horizontalHeader()
        columns = getattr(model, "COLUMNS", [])
        for c in range(model.columnCount()):
            if c < len(columns):
                col_def = columns[c]
                table_view.setColumnHidden(c, not col_def[3])
                header.resizeSection(c, col_def[2])
            visual_idx = header.visualIndex(c)
            if visual_idx != c:
                header.moveSection(visual_idx, c)
        self._save_table_header_state(table_view, storage_key)

    def _save_table_header_state(self, table_view: QTableView, storage_key: str) -> None:
        settings = QSettings("AMSO", "AudioMultiSourceOrganizer")
        settings.setValue(f"header_state_{storage_key}", table_view.horizontalHeader().saveState())
        model = cast(Any, table_view.model())
        if hasattr(model, "_current_sort_col"):
            settings.setValue(f"sort_col_{storage_key}", model._current_sort_col)
            order_val = (
                model._current_sort_order.value
                if hasattr(model._current_sort_order, "value")
                else int(model._current_sort_order)
            )
            settings.setValue(f"sort_order_{storage_key}", order_val)

    def _restore_table_header_state(self, table_view: QTableView, storage_key: str) -> bool:
        settings = QSettings("AMSO", "AudioMultiSourceOrganizer")
        state = settings.value(f"header_state_{storage_key}")
        restored = False
        if state is not None:
            restored = bool(table_view.horizontalHeader().restoreState(state))

        model = cast(Any, table_view.model())
        if hasattr(model, "_current_sort_col"):
            saved_sort_col = settings.value(f"sort_col_{storage_key}")
            saved_sort_order = settings.value(f"sort_order_{storage_key}")
            if saved_sort_col is not None and saved_sort_order is not None:
                try:
                    col = int(saved_sort_col)
                    order = Qt.SortOrder(int(saved_sort_order))
                    if 0 <= col < model.columnCount():
                        model._current_sort_col = col
                        model._current_sort_order = order
                        table_view.horizontalHeader().setSortIndicator(col, order)
                except Exception:
                    pass
        return restored

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

        top_bar.setFixedHeight(50)
        layout.addWidget(top_bar, 0)

        # Table View virtualisée harmonisée
        self.table_view = QTableView()
        self._setup_track_table_view(self.table_view, self.table_model, "all_tracks")
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self._on_table_context_menu)
        self.table_view.doubleClicked.connect(self._on_table_view_double_clicked)

        layout.addWidget(self.table_view, 1)
        return container

    def _setup_status_bar(self) -> None:
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self._status_is_alert: bool = False
        self.status_label = ClickableLabel(tr("status.ready"))
        self.status_label.clicked.connect(self._on_status_label_clicked)
        self.status_bar.addWidget(self.status_label, 1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.btn_cancel_scan = QPushButton(tr("status.cancel"))
        self.btn_cancel_scan.setStyleSheet("font-size: 11px; padding: 2px 8px;")
        self.btn_cancel_scan.setVisible(False)
        self.btn_cancel_scan.clicked.connect(self._cancel_current_scan)
        self.status_bar.addPermanentWidget(self.btn_cancel_scan)

        # Popover flottant du fil d'activité & tâches
        self.activity_popover = ActivityFeedPopover(
            self.db,
            scheduler=getattr(self, "scheduler", None),
            parent=self,
        )
        self.activity_popover.open_logs_requested.connect(self.show_logs_page)

        # Badge interactif au survol dans la barre d'état (bas droite)
        self.btn_activity_feed = HoverBadgeButton("⚡ " + tr("status.activity_feed"))
        self.btn_activity_feed.setCursor(Qt.CursorShape.PointingHandCursor)
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
        self.btn_activity_feed.hover_entered.connect(self._on_activity_feed_hover_entered)
        self.btn_activity_feed.hover_left.connect(self._on_activity_feed_hover_left)
        self.btn_activity_feed.clicked.connect(self._on_activity_feed_clicked)
        self.status_bar.addPermanentWidget(self.btn_activity_feed)

    def _setup_menu_bar(self) -> None:
        """Désactive la barre de menus standard pour une interface épurée et configure le raccourci F1."""
        menu_bar = self.menuBar()
        menu_bar.setVisible(False)
        self.menu_help = None

        self.action_about = QAction(tr("menu.about"), self)
        self.action_about.setShortcut(QKeySequence(Qt.Key.Key_F1))
        self.action_about.triggered.connect(self._on_settings_about_clicked)

        self.action_check_updates = QAction(tr("menu.check_updates"), self)
        self.action_check_updates.triggered.connect(lambda: self._check_for_updates(manual=True))

        # Raccourci F1 global pour accéder directement à la page À propos
        self.shortcut_f1 = QShortcut(QKeySequence(Qt.Key.Key_F1), self)
        self.shortcut_f1.activated.connect(self._on_settings_about_clicked)

    def _show_about_dialog(self) -> None:
        """Bascule directement sur la page Paramètres > À propos."""
        self._on_settings_about_clicked()

    def _on_status_label_clicked(self) -> None:
        """Ouvre les logs lorsqu'on clique sur un avertissement ou une erreur dans la barre d'état."""
        text = self.status_label.text()
        if getattr(self, "_status_is_alert", False) or "⚠️" in text or "❌" in text:
            self.show_logs_page()

    def _on_activity_feed_hover_entered(self) -> None:
        if hasattr(self, "activity_popover") and self.activity_popover:
            self.activity_popover.show_above_widget(self.btn_activity_feed)

    def _on_activity_feed_hover_left(self) -> None:
        if hasattr(self, "activity_popover") and self.activity_popover:
            self.activity_popover.schedule_hide()

    def _on_activity_feed_clicked(self) -> None:
        if hasattr(self, "activity_popover") and self.activity_popover:
            if self.activity_popover.isVisible():
                self.activity_popover.hide()
            else:
                self.activity_popover.show_above_widget(self.btn_activity_feed)

    # -------------------------------------------------------------------------
    # Internationalisation & Changement de langue dynamique
    # -------------------------------------------------------------------------

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

    def _ensure_vlc_available(self) -> bool:
        """Vérifie si VLC est disponible. Si non, propose le téléchargement automatique."""
        if self.player_service.is_vlc_available:
            return True
        dlg = VlcDownloadDialog(self.player_service, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            return self.player_service.is_vlc_available
        return False

    def _on_player_nav_clicked(self) -> None:
        """Active la page du grand Lecteur audio."""
        self._current_active_page = "player"
        if not self.player_service.is_vlc_available:
            self._ensure_vlc_available()
        self.stacked_widget.setCurrentWidget(self.page_player)

    def _on_blind_test_nav_clicked(self) -> None:
        """Active la page du mode Blind Test."""
        self._current_active_page = "blind_test"
        if not self.player_service.is_vlc_available:
            self._ensure_vlc_available()
        self.stacked_widget.setCurrentWidget(self.page_blind_test)

    def _on_playlist_nav_clicked(self) -> None:
        """Active la page de la Liste de lecture (Playlist)."""
        self._current_active_page = "playlist"
        if not self.player_service.is_vlc_available:
            self._ensure_vlc_available()
        self.stacked_widget.setCurrentWidget(self.page_playlist)

    def _on_all_tracks_clicked(self) -> None:
        self._current_active_page = "tracks"
        self.stacked_widget.setCurrentIndex(0)
        if getattr(self, "_tracks_dirty", False):
            self.table_model.set_filter(source_id=None, source_type=None, search_query=self.search_edit.text())
            self._tracks_dirty = False
        else:
            self.table_model.set_filter(source_id=None, source_type=None, search_query=self.search_edit.text())
        self._update_track_count()

    def _on_by_folder_clicked(self) -> None:
        """Active la page d'exploration par dossiers."""
        self._current_active_page = "folders"
        self.stacked_widget.setCurrentIndex(3)
        if self.folder_tree.topLevelItemCount() == 0 or getattr(self, "_folders_dirty", False):
            self._refresh_folders_tree()
            self.folder_table_model.reload_data()
            self._folders_dirty = False

    def _on_source_selected(self, source: SourceRecord) -> None:
        self.stacked_widget.setCurrentIndex(0)
        self.table_model.set_filter(source_id=source.id, search_query=self.search_edit.text())
        self._update_track_count()

    def _on_duplicates_clicked(self) -> None:
        """Affiche les morceaux identifiés comme doublons stricts ou similaires."""
        self._current_active_page = "duplicates"
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
        self._current_active_page = "stats"
        self.stacked_widget.setCurrentIndex(1)
        self._refresh_stats_view()

    def _on_settings_general_clicked(self) -> None:
        """Bascule sur la page des Paramètres Généraux."""
        self._current_active_page = "settings_general"
        self.stacked_widget.setCurrentWidget(self.page_settings)
        if getattr(self, "_stats_dirty", False):
            self._refresh_stats_view()
            self._stats_dirty = False

    def _on_settings_sources_clicked(self) -> None:
        """Bascule sur la page Paramètres > Sources."""
        self._current_active_page = "settings_sources"
        self.stacked_widget.setCurrentWidget(self.page_settings_sources)
        if (
            getattr(self, "_sources_dirty", False)
            or not hasattr(self, "table_settings_sources")
            or self.table_settings_sources.rowCount() == 0
        ):
            self._refresh_settings_sources_table()
            self._sources_dirty = False

    def _on_settings_player_clicked(self) -> None:
        """Bascule sur la page Paramètres > Lecteur."""
        self._current_active_page = "settings_player"
        self.stacked_widget.setCurrentWidget(self.page_settings_player)

    def _update_sleep_inhibition(self) -> None:
        """Met à jour l'inhibition de veille du système et de l'écran selon le mode choisi, l'état et la page active."""
        cfg = get_config_manager()
        is_playing = (getattr(self, "_player_state", "stopped") == "playing") or self.player_service.is_playing
        mode = cfg.get_sleep_mode()

        if not is_playing or mode == "allow":
            SleepInhibitor.release()
            return

        if mode == "always":
            SleepInhibitor.inhibit(prevent_display=True)
            return

        # mode == "player_playlist" (par défaut)
        curr_widget = self.stacked_widget.currentWidget() if hasattr(self, "stacked_widget") else None
        is_player_or_playlist = curr_widget in (
            getattr(self, "page_player", None),
            getattr(self, "page_blind_test", None),
            getattr(self, "page_playlist", None),
        )
        SleepInhibitor.inhibit(prevent_display=is_player_or_playlist)

    def _on_current_page_changed(self, index: int) -> None:
        """Appelé lors du basculement d'onglet pour adapter l'inhibition de veille de l'écran et la page active."""
        prev_page = getattr(self, "_current_active_page", None)
        self._update_sleep_inhibition()
        if hasattr(self, "stacked_widget"):
            curr_widget = self.stacked_widget.currentWidget()
            if prev_page == "blind_test" and curr_widget != getattr(self, "page_blind_test", None):
                if hasattr(self, "player_service") and self.player_service and self.player_service.is_playing:
                    self.player_service.pause()
            if curr_widget == getattr(self, "page_player", None):
                self._current_active_page = "player"
            elif curr_widget == getattr(self, "page_blind_test", None):
                self._current_active_page = "blind_test"
            elif curr_widget == getattr(self, "page_playlist", None):
                self._current_active_page = "playlist"
            elif curr_widget == getattr(self, "page_folders", None):
                self._current_active_page = "folders"
            elif curr_widget == getattr(self, "page_stats", None):
                self._current_active_page = "stats"
            elif curr_widget == getattr(self, "page_settings", None):
                self._current_active_page = "settings_general"
            elif curr_widget == getattr(self, "page_settings_sources", None):
                self._current_active_page = "settings_sources"
            elif curr_widget == getattr(self, "page_settings_player", None):
                self._current_active_page = "settings_player"
            elif curr_widget == getattr(self, "page_logs", None):
                self._current_active_page = "logs"
            elif curr_widget == getattr(self, "page_settings_about", None):
                self._current_active_page = "settings_about"
            elif curr_widget == getattr(self, "page_tracks", None):
                if getattr(self, "_current_active_page", None) != "duplicates":
                    self._current_active_page = "tracks"

    def _on_sleep_mode_changed(self) -> None:
        """Enregistre le choix du mode de veille et applique immédiatement l'effet."""
        cfg = get_config_manager()
        if hasattr(self, "radio_sleep_allow") and self.radio_sleep_allow.isChecked():
            cfg.set_sleep_mode("allow")
        elif hasattr(self, "radio_sleep_always") and self.radio_sleep_always.isChecked():
            cfg.set_sleep_mode("always")
        elif hasattr(self, "radio_sleep_screens") and self.radio_sleep_screens.isChecked():
            cfg.set_sleep_mode("player_playlist")
        self._update_sleep_inhibition()

    def _on_prevent_sleep_toggled(self, checked: bool) -> None:
        """Rétrocompatibilité."""
        cfg = get_config_manager()
        cfg.set_prevent_sleep(checked)
        self._update_sleep_inhibition()

    def _on_transition_mode_changed(self) -> None:
        cfg = get_config_manager()
        if hasattr(self, "radio_trans_standard") and self.radio_trans_standard.isChecked():
            cfg.set_transition_mode("standard")
        elif hasattr(self, "radio_trans_gapless") and self.radio_trans_gapless.isChecked():
            cfg.set_transition_mode("gapless")
        elif hasattr(self, "radio_trans_crossfade") and self.radio_trans_crossfade.isChecked():
            cfg.set_transition_mode("crossfade")
        self._update_crossfade_controls_state()

    def _on_crossfade_slider_changed(self, value: int) -> None:
        cfg = get_config_manager()
        cfg.set_crossfade_duration(value)
        if hasattr(self, "lbl_crossfade_value"):
            self.lbl_crossfade_value.setText(tr("settings.crossfade_duration_val", seconds=str(value)))

    def _update_crossfade_controls_state(self) -> None:
        if not hasattr(self, "crossfade_container") or not hasattr(self, "radio_trans_crossfade"):
            return
        is_cf = self.radio_trans_crossfade.isChecked()
        self.crossfade_container.setEnabled(is_cf)
        if hasattr(self, "lbl_crossfade_duration"):
            self.lbl_crossfade_duration.setStyleSheet(
                "color: #CBD5E1; font-size: 12.5px; font-weight: 500;"
                if is_cf
                else "color: #475569; font-size: 12.5px; font-weight: 500;"
            )
        if hasattr(self, "lbl_crossfade_value"):
            self.lbl_crossfade_value.setStyleSheet(
                "color: #38BDF8; font-size: 12.5px; font-weight: 600; min-width: 90px;"
                if is_cf
                else "color: #475569; font-size: 12.5px; font-weight: 600; min-width: 90px;"
            )

    def _on_visual_effect_changed(self) -> None:
        """Appelé lors d'un changement de sélection dans les boutons radio d'effets visuels."""
        if not hasattr(self, "effect_group"):
            return
        if hasattr(self, "radio_eff_particles") and self.radio_eff_particles.isChecked():
            eff = "particles"
        elif hasattr(self, "radio_eff_waves") and self.radio_eff_waves.isChecked():
            eff = "waves"
        elif hasattr(self, "radio_eff_stars") and self.radio_eff_stars.isChecked():
            eff = "stars"
        elif hasattr(self, "radio_eff_warp") and self.radio_eff_warp.isChecked():
            eff = "warp"
        elif hasattr(self, "radio_eff_warp_dynamic") and self.radio_eff_warp_dynamic.isChecked():
            eff = "warp_dynamic"
        elif hasattr(self, "radio_eff_aurora") and self.radio_eff_aurora.isChecked():
            eff = "aurora"
        elif hasattr(self, "radio_eff_bars") and self.radio_eff_bars.isChecked():
            eff = "bars"
        elif hasattr(self, "radio_eff_bars_full") and self.radio_eff_bars_full.isChecked():
            eff = "bars_full"
        elif hasattr(self, "radio_eff_none") and self.radio_eff_none.isChecked():
            eff = "none"
        else:
            eff = "particles"

        cfg = get_config_manager()
        cfg.set_visual_effect(eff)
        if hasattr(self, "page_player") and self.page_player:
            self.page_player.set_effect_type(eff)
        if hasattr(self, "page_blind_test") and self.page_blind_test:
            self.page_blind_test.set_effect_type(eff)

    def set_visual_effect(self, eff: str) -> None:
        """Applique l'effet visuel à l'ensemble de l'application (Lecteur, Blind Test et réglages)."""
        cfg = get_config_manager()
        cfg.set_visual_effect(eff)
        self._sync_visual_effect_radio(eff)

    def _sync_visual_effect_radio(self, eff: str) -> None:
        """Synchronise l'état des boutons radio Paramètres > Lecteur avec le lecteur sans boucle."""
        if hasattr(self, "page_blind_test") and self.page_blind_test:
            if getattr(self.page_blind_test, "current_effect", None) != eff:
                self.page_blind_test.set_effect_type(eff)
        if hasattr(self, "page_player") and self.page_player:
            if getattr(self.page_player, "current_effect", None) != eff:
                self.page_player.blockSignals(True)
                self.page_player.set_effect_type(eff)
                self.page_player.blockSignals(False)
        if not hasattr(self, "effect_group"):
            return
        radio_map = {
            "particles": getattr(self, "radio_eff_particles", None),
            "waves": getattr(self, "radio_eff_waves", None),
            "stars": getattr(self, "radio_eff_stars", None),
            "warp": getattr(self, "radio_eff_warp", None),
            "warp_dynamic": getattr(self, "radio_eff_warp_dynamic", None),
            "aurora": getattr(self, "radio_eff_aurora", None),
            "bars": getattr(self, "radio_eff_bars", None),
            "bars_full": getattr(self, "radio_eff_bars_full", None),
            "none": getattr(self, "radio_eff_none", None),
        }
        target = radio_map.get(eff)
        if target and not target.isChecked():
            self.effect_group.blockSignals(True)
            target.setChecked(True)
            self.effect_group.blockSignals(False)

    def _on_player_state_changed(self, state: str) -> None:
        self._player_state = state
        self._update_sleep_inhibition()
        if state == "playing" and getattr(self, "_status_is_alert", False):
            self._status_is_alert = False
            self.status_label.setText(tr("status.ready"))
            self.status_label.setToolTip("")
            self.status_label.setCursor(Qt.CursorShape.ArrowCursor)

    def _on_settings_logs_clicked(self) -> None:
        """Bascule sur la page Paramètres > Logs."""
        self._current_active_page = "logs"
        self.stacked_widget.setCurrentWidget(self.page_logs)
        self.page_logs.refresh_if_dirty()

    def show_logs_page(self) -> None:
        """Sélectionne le bouton de navigation Logs et ouvre la page Paramètres > Logs."""
        if hasattr(self, "drawer_settings"):
            self.drawer_settings.set_expanded(True)
        if hasattr(self, "btn_settings_logs"):
            self.btn_settings_logs.setChecked(True)
        self._on_settings_logs_clicked()

    def _on_settings_about_clicked(self) -> None:
        """Bascule sur la page Paramètres > À propos."""
        self._current_active_page = "settings_about"
        self.stacked_widget.setCurrentWidget(self.page_settings_about)
        if hasattr(self, "drawer_settings"):
            self.drawer_settings.set_expanded(True)
        if hasattr(self, "btn_settings_about"):
            self.btn_settings_about.setChecked(True)

    def show_about_page(self) -> None:
        """Sélectionne le bouton de navigation À propos et ouvre la page Paramètres > À propos."""
        self._on_settings_about_clicked()

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

    def _on_table_context_menu(self, pos: QPoint) -> None:
        index = self.table_view.indexAt(pos)
        menu = QMenu(self)

        if index.isValid():
            selected_tracks = self._get_selected_tracks(self.table_view, self.table_model, index.row())
            if selected_tracks:
                act_next = QAction(tr("context_menu.play_next"), self)
                act_next.triggered.connect(lambda: self._insert_next_with_vlc_check(selected_tracks))
                menu.addAction(act_next)

                act_add = QAction(tr("context_menu.add_to_playlist"), self)
                act_add.triggered.connect(lambda: self._append_tracks_with_vlc_check(selected_tracks))
                menu.addAction(act_add)

                menu.addSeparator()

            track: TrackRecord | None = self.table_model.get_track_at(index.row())
            if track:
                action_open_dir = QAction(tr("context_menu.open_file_location"), self)
                action_open_dir.triggered.connect(lambda: self._open_file_location(track.source_path))
                menu.addAction(action_open_dir)

                menu.addSeparator()

                action_del = QAction(tr("context_menu.delete_track"), self)
                action_del.triggered.connect(lambda: self._delete_track_from_lib(track))
                menu.addAction(action_del)

                menu.addSeparator()

        # Personnalisation des colonnes accessible directement depuis le tableau
        cols_submenu = self._build_columns_menu(self.table_view, self.table_model, "all_tracks")
        cols_submenu.setTitle("⚙️  " + tr("table.menu_columns"))
        menu.addMenu(cols_submenu)

        menu.exec(QCursor.pos())

    def _open_file_location(self, file_path: str | None) -> None:
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

        self.table_model.reload_data()
        self.folder_table_model.reload_data()
        self._update_track_count()
        self._refresh_stats_view()
        self._refresh_folders_tree()

    def _remove_track_from_player(self, track: TrackRecord) -> None:
        """Retire le morceau de la file d'attente du lecteur audio s'il y figure."""
        if not hasattr(self, "player_service") or not self.player_service:
            return
        pl = self.player_service.playlist
        for i in range(len(pl) - 1, -1, -1):
            t = pl[i]
            if (track.id is not None and t.id == track.id) or (
                track.source_path and t.source_path == track.source_path
            ):
                self.player_service.remove_at(i)

    # -------------------------------------------------------------------------
    # Interactions du Lecteur Audio (Double-clic, Playlist, Multi-sélection)
    # -------------------------------------------------------------------------

    def _on_player_error(self, message: str) -> None:
        """Affiche les avertissements ou erreurs du lecteur dans la barre d'état et les consigne dans les logs."""
        self._status_is_alert = True
        self.status_label.setText(f"⚠️ {message}")
        self.status_label.setToolTip(f"{message}\n({tr('status.click_to_view_logs')})")
        self.status_label.setCursor(Qt.CursorShape.PointingHandCursor)

        source_name = tr("sidebar.nav_player").replace("🎵", "").strip()
        self.db.add_activity_log(
            action=tr("logs.action_player_error"),
            level="WARNING",
            category="PLAYER",
            source_name=source_name,
            details=message,
            items_errors=1,
        )

        if hasattr(self, "page_logs") and self.page_logs:
            self.page_logs.mark_dirty()

    def _on_table_view_double_clicked(self, index) -> None:
        """Double-clic sur un morceau dans la table principale."""
        if not index.isValid():
            return
        self.table_view.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtCenter)
        self._play_from_table(self.table_model, index.row())

    def _on_folder_table_view_double_clicked(self, index) -> None:
        """Double-clic sur un morceau dans la table par dossier."""
        if not index.isValid():
            return
        self.folder_table_view.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtCenter)
        self._play_from_table(self.folder_table_model, index.row())

    def _play_from_table(self, model: Any, start_row: int) -> None:
        """Lance la lecture du morceau cliqué et charge la sélection dans la playlist (avec confirmation si > 1 000 morceaux)."""
        if not self.player_service.is_vlc_available:
            if not self._ensure_vlc_available():
                return

        clicked_track = model.get_track_at(start_row)
        if clicked_track is None:
            return

        total_rows = model.rowCount()

        # Si la sélection dépasse 1 000 titres, afficher le dialogue de décision
        if total_rows > 1000:
            folder_count = 0
            if clicked_track.folder_path:
                try:
                    folder_count = self.db.count_tracks_by_folder(
                        clicked_track.folder_path,
                        source_id=clicked_track.source_id,
                        recursive=False,
                    )
                except Exception:
                    folder_count = 0

            dialog = LargeSelectionDialog(
                track=clicked_track,
                total_count=total_rows,
                folder_track_count=folder_count,
                parent=self,
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return

            choice = dialog.get_choice()
            if choice == "folder":
                tracks_to_play = self.db.get_tracks_by_folder(
                    folder_path=clicked_track.folder_path,
                    source_id=clicked_track.source_id,
                    recursive=False,
                )
                if not tracks_to_play:
                    tracks_to_play = [clicked_track]
                target_idx = 0
                for idx, t in enumerate(tracks_to_play):
                    if (t.id is not None and t.id == clicked_track.id) or (t.source_path and t.source_path == clicked_track.source_path):
                        target_idx = idx
                        break
                self.player_service.play_tracks(tracks_to_play, start_index=target_idx)
                return

            elif choice == "limit_1000":
                limit_tracks: list[TrackRecord] = []
                end_row = min(total_rows, start_row + 1000)
                for r in range(start_row, end_row):
                    t = model.get_track_at(r)
                    if t is not None:
                        limit_tracks.append(t)
                if limit_tracks:
                    self.player_service.play_tracks(limit_tracks, start_index=0)
                return

            elif choice == "play_all":
                # Poursuit vers le chargement complet ci-dessous
                pass
            else:
                return

        # Cas <= 1 000 ou choix "play_all" : tous les titres du modèle sont ajoutés, lecture démarrant au titre cliqué
        all_tracks: list[TrackRecord] = []
        target_index = 0
        for r in range(total_rows):
            t = model.get_track_at(r)
            if t is not None:
                if r == start_row:
                    target_index = len(all_tracks)
                all_tracks.append(t)

        if all_tracks:
            self.player_service.play_tracks(all_tracks, start_index=target_index)

    def _insert_next_with_vlc_check(self, tracks: list[TrackRecord]) -> None:
        if not self.player_service.is_vlc_available:
            if not self._ensure_vlc_available():
                return
        self.player_service.insert_next(tracks)

    def _append_tracks_with_vlc_check(self, tracks: list[TrackRecord]) -> None:
        if not self.player_service.is_vlc_available:
            if not self._ensure_vlc_available():
                return
        self.player_service.append_tracks(tracks)

    def _get_selected_tracks(self, table_view: QTableView, model: Any, clicked_row: int) -> list[TrackRecord]:
        """Récupère la liste ordonnée des pistes sélectionnées (avec prise en charge de la multi-sélection)."""
        selection_model = table_view.selectionModel()
        selected_rows: set[int] = set()
        if selection_model:
            selected_rows = {idx.row() for idx in selection_model.selectedRows()}
        if not selected_rows:
            selected_rows = {clicked_row}
        ordered_rows = sorted(selected_rows)
        tracks: list[TrackRecord] = []
        for r in ordered_rows:
            t = model.get_track_at(r)
            if t is not None:
                tracks.append(t)
        return tracks
