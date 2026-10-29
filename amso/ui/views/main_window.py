"""Fenêtre principale de l'application AMSO en PySide6."""

from __future__ import annotations

import logging
import subprocess
import sys
from typing import Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from amso.core.database import (
    DatabaseManager,
    get_default_data_dir,
)
from amso.core.i18n import get_i18n, tr
from amso.core.scheduler import SyncScheduler
from amso.core.startup_timing import get_startup_clock
from amso.services.player_service import PlayerService
from amso.services.sleep_inhibitor import SleepInhibitor
from amso.services.update_checker import UpdateCheckerWorker
from amso.ui.dialogs.vlc_download_dialog import VlcDownloadDialog
from amso.ui.models import FolderTrackTableModel, TrackTableModel
from amso.ui.pages.folders_page import FoldersPageMixin
from amso.ui.pages.folders_trash import FoldersTrashMixin
from amso.ui.pages.folders_tree import FoldersTreeMixin
from amso.ui.pages.navigation import NavigationMixin
from amso.ui.pages.playback_settings import PlaybackSettingsMixin
from amso.ui.pages.retranslate import RetranslateMixin
from amso.ui.pages.scan_controller import ScanControllerMixin
from amso.ui.pages.session_state import SessionStateMixin
from amso.ui.pages.settings_about import SettingsAboutPageMixin
from amso.ui.pages.settings_general import SettingsGeneralPageMixin
from amso.ui.pages.settings_player import SettingsPlayerPageMixin
from amso.ui.pages.settings_sources import SettingsSourcesPageMixin
from amso.ui.pages.sidebar_layout import SidebarLayoutMixin
from amso.ui.pages.sources_list import SourcesListMixin
from amso.ui.pages.stats_page import StatsPageMixin
from amso.ui.pages.table_columns import TableColumnsMixin
from amso.ui.pages.track_actions import TrackActionsMixin
from amso.ui.pages.update_controller import UpdateControllerMixin
from amso.ui.theme import DARK_THEME_QSS
from amso.ui.views.cover_helper import wait_for_cover_workers
from amso.ui.views.update_banner import UpdateBannerWidget
from amso.ui.workers import ScanWorker

logger = logging.getLogger(__name__)


class MainWindow(
    SettingsPlayerPageMixin,
    SettingsAboutPageMixin,
    StatsPageMixin,
    SettingsGeneralPageMixin,
    SettingsSourcesPageMixin,
    ScanControllerMixin,
    FoldersPageMixin,
    FoldersTreeMixin,
    FoldersTrashMixin,
    UpdateControllerMixin,
    SessionStateMixin,
    RetranslateMixin,
    SidebarLayoutMixin,
    TableColumnsMixin,
    SourcesListMixin,
    NavigationMixin,
    PlaybackSettingsMixin,
    TrackActionsMixin,
    QMainWindow,
):
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
        self.table_model = TrackTableModel(db=self.db, parent=self, defer_loading=True)
        self.folder_table_model = FolderTrackTableModel(db=self.db, parent=self)

        # Service audio central python-vlc
        if progress_callback:
            progress_callback(45, tr("splash.loading_audio"))
        clock = get_startup_clock()
        clock.mark("MainWindow: modèles")
        self.player_service = PlayerService(parent=self)
        clock.mark("PlayerService (VLC, audio)")
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
        clock.mark("MainWindow: interface")

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
        self._update_track_count()
        clock.mark("bibliothèque (sources, dossiers, pistes)")

        if progress_callback:
            progress_callback(90, tr("splash.restoring_session"))
        self._restore_saved_playlist()
        clock.mark("restauration playlist")
        self._restore_active_page()
        clock.mark("restauration page active")

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
            self.player_service.release_audio_output()
        if (
            hasattr(self, "update_worker")
            and self.update_worker
            and getattr(self.update_worker, "isRunning", lambda: False)()
        ):
            if hasattr(self.update_worker, "cancel"):
                self.update_worker.cancel()
            if hasattr(self.update_worker, "wait"):
                self.update_worker.wait(1000)
        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.cancel()
            self.scan_worker.wait(2000)
        still_running = wait_for_cover_workers()
        # Trace les threads qui survivent à la fermeture (E/S réseau bloquées) pour les identifier.
        get_startup_clock().note(
            "fermeture: scan actif=%s, mise à jour active=%s, pochettes actives=%d",
            bool(self.scan_worker and self.scan_worker.isRunning()),
            bool(self.update_worker and getattr(self.update_worker, "isRunning", lambda: False)()),
            still_running,
        )
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

    def _ensure_vlc_available(self) -> bool:
        """Vérifie si VLC est disponible. Si non, propose le téléchargement automatique."""
        if self.player_service.is_vlc_available:
            return True
        dlg = VlcDownloadDialog(self.player_service, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            return self.player_service.is_vlc_available
        return False

    def _on_open_data_folder(self) -> None:
        """Ouvre le répertoire de données de l'application dans l'explorateur."""
        data_dir = get_default_data_dir()
        if sys.platform == "win32":
            subprocess.run(f'explorer "{data_dir}"')
        elif sys.platform == "darwin":
            subprocess.run(["open", str(data_dir)])
        else:
            subprocess.run(["xdg-open", str(data_dir)])
