"""Construction de la barre latérale, du panneau droit, de la barre de statut et du menu (mixin de MainWindow)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from amso.core.i18n import tr
from amso.ui.views.activity_feed_popover import ActivityFeedPopover
from amso.ui.views.blind_test_view import BlindTestView
from amso.ui.views.logs_view import LogsView
from amso.ui.views.player_view import PlayerView
from amso.ui.views.playlist_view import PlaylistView
from amso.ui.widgets.common import ClickableLabel, CollapsibleDrawer, HoverBadgeButton

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    _MixinBase = QMainWindow
else:
    _MixinBase = object


class SidebarLayoutMixin(_MixinBase):
    """Construction de la barre latérale, du panneau droit, de la barre de statut et du menu (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de MainWindow sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

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
