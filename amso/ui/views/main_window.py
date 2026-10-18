"""Fenêtre principale de l'application AMSO en PySide6."""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, cast

from PySide6.QtCore import QAbstractTableModel, QPoint, QSettings, Qt, QThread, QTimer, QUrl, Signal
from PySide6.QtGui import QAction, QCursor, QDesktopServices, QKeySequence, QMouseEvent, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
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
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from amso import __version__
from amso.core.config import get_config_manager, get_config_path
from amso.core.constants import (
    URL_GITHUB_RELEASES,
    URL_GITHUB_REPO,
    URL_GITHUB_SPONSORS,
    URL_ITCH_IO,
    URL_KO_FI,
)
from amso.core.database import (
    DatabaseManager,
    SourceRecord,
    SourceType,
    TrackRecord,
    get_default_data_dir,
    get_saved_playlist_path,
)
from amso.core.i18n import SUPPORTED_LANGUAGES, get_i18n, tr
from amso.core.scanner import ScanSummary
from amso.core.scheduler import SyncScheduler
from amso.services.player_service import PlayerService
from amso.services.sleep_inhibitor import SleepInhibitor
from amso.services.update_checker import UpdateCheckerWorker
from amso.ui.dialogs.delete_track_dialog import DeleteTrackDialog, send_file_to_trash
from amso.ui.dialogs.large_selection_dialog import LargeSelectionDialog
from amso.ui.dialogs.source_config_dialog import SourceConfigDialog
from amso.ui.dialogs.vlc_download_dialog import VlcDownloadDialog
from amso.ui.models import FolderTrackTableModel, TrackTableModel
from amso.ui.theme import DARK_THEME_QSS, get_app_logo_pixmap
from amso.ui.views.activity_feed_popover import ActivityFeedPopover
from amso.ui.views.blind_test_view import BlindTestView
from amso.ui.views.logs_view import LogsView
from amso.ui.views.player_view import PlayerView
from amso.ui.views.playlist_view import PlaylistView
from amso.ui.views.update_banner import UpdateBannerWidget
from amso.ui.views.visual_effects import VisualEffectWidget
from amso.ui.workers import ScanWorker

logger = logging.getLogger(__name__)


class HoverBadgeButton(QPushButton):
    """Bouton interactif de barre d'état émettant des signaux au survol pour les popovers."""

    hover_entered = Signal()
    hover_left = Signal()

    def enterEvent(self, event: Any) -> None:
        self.hover_entered.emit()
        super().enterEvent(event)

    def leaveEvent(self, event: Any) -> None:
        self.hover_left.emit()
        super().leaveEvent(event)


class ClickableLabel(QLabel):
    """QLabel cliquable émettant un signal clicked lors d'un clic gauche."""

    clicked = Signal()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class CollapsibleDrawer(QWidget):
    """Tiroir pliable/dépliable regroupant des boutons de navigation."""

    def __init__(
        self,
        title: str,
        parent: QWidget | None = None,
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

    def title(self) -> str:
        return self._title

    def set_title(self, title: str) -> None:
        self._title = title
        self._update_header()

    def _update_header(self) -> None:
        arrow = "▼" if self._is_expanded else "▶"
        self.header_btn.setText(f"{arrow}  {self._title.upper()}")

    @property
    def is_expanded(self) -> bool:
        return self._is_expanded

    def toggle(self) -> None:
        self.set_expanded(not self._is_expanded)

    def set_expanded(self, expanded: bool) -> None:
        self._is_expanded = expanded
        self.content_widget.setVisible(self._is_expanded)
        self._update_header()

    def add_widget(self, widget: QWidget) -> None:
        self.content_layout.addWidget(widget)


class MainWindow(QMainWindow):
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

    def _save_active_page(self) -> None:
        """Supprimé : la page active n'est plus persistée, l'appli démarre systématiquement sur le Lecteur."""
        pass

    def _restore_active_page(self) -> None:
        """Au démarrage de l'appli, on bascule systématiquement sur la page Lecteur."""
        cfg = get_config_manager()
        cfg.remove_active_page()
        page_id = "player"
        self._current_active_page = page_id

        mapping = {
            "tracks": (
                getattr(self, "btn_all_tracks", None),
                getattr(self, "drawer_library", None),
                self._on_all_tracks_clicked,
            ),
            "folders": (
                getattr(self, "btn_by_folder", None),
                getattr(self, "drawer_library", None),
                self._on_by_folder_clicked,
            ),
            "duplicates": (
                getattr(self, "btn_duplicates", None),
                getattr(self, "drawer_tools", None),
                self._on_duplicates_clicked,
            ),
            "stats": (
                getattr(self, "btn_stats_page", None),
                getattr(self, "drawer_stats", None),
                self._on_stats_page_clicked,
            ),
            "player": (
                getattr(self, "btn_player", None),
                getattr(self, "drawer_player", None),
                self._on_player_nav_clicked,
            ),
            "blind_test": (
                getattr(self, "btn_blind_test", None),
                getattr(self, "drawer_games", None),
                self._on_blind_test_nav_clicked,
            ),
            "playlist": (
                getattr(self, "btn_playlist", None),
                getattr(self, "drawer_player", None),
                self._on_playlist_nav_clicked,
            ),
            "settings_general": (
                getattr(self, "btn_settings_general", None),
                getattr(self, "drawer_settings", None),
                self._on_settings_general_clicked,
            ),
            "settings_sources": (
                getattr(self, "btn_settings_sources", None),
                getattr(self, "drawer_settings", None),
                self._on_settings_sources_clicked,
            ),
            "settings_player": (
                getattr(self, "btn_settings_player", None),
                getattr(self, "drawer_settings", None),
                self._on_settings_player_clicked,
            ),
            "logs": (
                getattr(self, "btn_settings_logs", None),
                getattr(self, "drawer_settings", None),
                self._on_settings_logs_clicked,
            ),
            "settings_about": (
                getattr(self, "btn_settings_about", None),
                getattr(self, "drawer_settings", None),
                self._on_settings_about_clicked,
            ),
        }

        if page_id in mapping:
            btn, drawer, handler = mapping[page_id]
            if drawer and page_id != "tracks":
                drawer.set_expanded(True)
            if btn:
                btn.setChecked(True)
            if handler is not None:
                handler()

    def _save_all_tables_state(self) -> None:
        """Sauvegarde l'état des tableaux de l'application (taille, visibilité, ordre des colonnes, tri)."""
        if hasattr(self, "table_view") and self.table_view:
            self._save_table_header_state(self.table_view, "all_tracks")
        if hasattr(self, "folder_table_view") and self.folder_table_view:
            self._save_table_header_state(self.folder_table_view, "folders")
        if hasattr(self, "page_playlist") and self.page_playlist:
            self.page_playlist.save_table_state()

    def _save_player_state(self) -> None:
        """Sauvegarde les paramètres du lecteur (shuffle, repeat, volume, mute, effet visuel, position) dans la configuration."""
        cfg = get_config_manager()
        if hasattr(self, "player_service") and self.player_service:
            cfg.set_player_shuffle(self.player_service.is_shuffle)
            cfg.set_player_repeat_mode(self.player_service.repeat_mode)
            cfg.set_player_volume(self.player_service.volume)
            cfg.set_player_muted(self.player_service.is_muted)
            cfg.set_player_position_ms(self.player_service.current_time_ms)
        if hasattr(self, "page_player") and self.page_player:
            eff = getattr(self.page_player, "effect_type", None)
            if not eff and hasattr(self.page_player, "effect_canvas") and self.page_player.effect_canvas:
                eff = self.page_player.effect_canvas.effect_type
            if eff:
                cfg.set_visual_effect(eff)

    def _on_player_track_changed_for_save(self, _track: TrackRecord | None) -> None:
        """Déclenché lors d'un changement de morceau pour sauvegarder l'état après stabilisation."""
        if hasattr(self, "_playlist_save_timer"):
            self._playlist_save_timer.start()

    def _on_playlist_updated_for_save(self) -> None:
        """Déclenché lors d'une modification de la file d'attente (ajout, suppression, réordonnancement)."""
        if hasattr(self, "_playlist_save_timer"):
            self._playlist_save_timer.start()

    def _save_current_playlist(self, immediate: bool = False) -> None:
        """Sauvegarde la file d'attente (playlist), l'index de lecture et la position en cours dans un fichier JSON.

        Optimisé pour les très grandes bibliothèques (> 10 000 titres) :
        - Sauvegarde compacte par identifiants SQLite (track_ids) réduisant le fichier de 99%.
        - Écriture asynchrone non-bloquante pour garantir 0 saccade sur l'interface graphique.
        """
        if not hasattr(self, "player_service") or not self.player_service:
            return
        playlist = self.player_service.playlist
        curr_idx = self.player_service.current_index
        curr_pos_ms = self.player_service.current_time_ms
        playlist_path = get_saved_playlist_path()

        if not playlist:
            data: dict[str, Any] = {
                "version": 2,
                "current_index": 0,
                "position_ms": 0,
                "track_ids": [],
            }
        elif all(t.id is not None for t in playlist):
            data = {
                "version": 2,
                "current_index": curr_idx,
                "position_ms": curr_pos_ms,
                "track_ids": [t.id for t in playlist],
            }
        else:
            data = {
                "version": 1,
                "current_index": curr_idx,
                "position_ms": curr_pos_ms,
                "tracks": [t.to_dict() for t in playlist],
            }

        def _do_write() -> None:
            try:
                playlist_path.parent.mkdir(parents=True, exist_ok=True)
                temp_path = playlist_path.with_suffix(".tmp")
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
                temp_path.replace(playlist_path)
            except Exception as exc:
                logger.warning("Impossible de sauvegarder la playlist courante : %s", exc)

        if immediate:
            _do_write()
        else:
            threading.Thread(target=_do_write, daemon=True, name="PlaylistSaveThread").start()

    def _restore_saved_playlist(self) -> None:
        """Restaure la playlist, l'index et la position temporelle sauvegardés lors de la session précédente."""
        playlist_path = get_saved_playlist_path()
        if not playlist_path.exists():
            return

        try:
            with open(playlist_path, encoding="utf-8") as f:
                data = json.load(f)

            saved_index = data.get("current_index", 0)
            saved_pos_ms = data.get("position_ms", 0)
            if saved_pos_ms <= 0:
                saved_pos_ms = get_config_manager().get_player_position_ms()

            restored_tracks: list[TrackRecord] = []
            db_tracks: dict[int, TrackRecord] = {}

            # Format version 2 : liste compacte d'identifiants
            if "track_ids" in data:
                track_ids = data.get("track_ids", [])
                if track_ids and self.db:
                    try:
                        restored_tracks = self.db.get_tracks_by_ids(track_ids)
                        db_tracks = {t.id: t for t in restored_tracks if t.id is not None}
                    except Exception as e:
                        logger.warning("Erreur lors de la récupération des pistes par ID : %s", e)
            else:
                # Format version 1 : liste de dictionnaires complets
                raw_tracks = data.get("tracks", [])
                if not raw_tracks:
                    return

                track_ids = [t.get("id") for t in raw_tracks if t.get("id") is not None]
                if track_ids and self.db:
                    try:
                        for trk in self.db.get_tracks_by_ids(track_ids):
                            if trk.id is not None:
                                db_tracks[trk.id] = trk
                    except Exception:
                        pass

                for t_dict in raw_tracks:
                    tid = t_dict.get("id")
                    if tid is not None and tid in db_tracks:
                        restored_tracks.append(db_tracks[tid])
                    else:
                        restored_tracks.append(TrackRecord.from_dict(t_dict))

            # Filtrage des pistes orphelines ou fantômes (ex. mocks de tests ou fichiers locaux inexistants)
            # Optimisation majeure : si la piste provient de la base SQLite active (db_tracks),
            # elle est déjà validée en mémoire (O(1)) et on évite des milliers d'I/O disque bloquantes (Path.exists).
            valid_tracks: list[TrackRecord] = []
            for trk in restored_tracks:
                if trk.id is not None and trk.id in db_tracks:
                    valid_tracks.append(trk)
                elif trk.source_type != SourceType.LOCAL:
                    valid_tracks.append(trk)
                else:
                    path_str = trk.source_path or trk.source_ref
                    if path_str and Path(path_str).exists():
                        valid_tracks.append(trk)
                    elif self.db and path_str and self.db.get_track_by_ref(path_str):
                        valid_tracks.append(trk)

            if not valid_tracks:
                logger.info("Playlist sauvegardée ignorée : aucun fichier valide trouvé.")
                return

            saved_index = max(0, min(saved_index, len(valid_tracks) - 1))
            current_track = valid_tracks[saved_index]
            if current_track.duration_seconds and current_track.duration_seconds > 0:
                dur_ms = int(current_track.duration_seconds * 1000)
                if saved_pos_ms >= dur_ms:
                    saved_pos_ms = 0
                else:
                    saved_pos_ms = max(0, saved_pos_ms)

            self.player_service.load_playlist(
                valid_tracks,
                current_index=saved_index,
                initial_position_ms=saved_pos_ms,
            )
            if hasattr(self, "page_playlist") and self.page_playlist:
                self.page_playlist._update_stats_label()
        except Exception as exc:
            logger.warning("Erreur lors de la restauration de la playlist : %s", exc)

    # -------------------------------------------------------------------------
    # Construction de l'interface graphique
    # -------------------------------------------------------------------------

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
        top_bar.setFixedHeight(50)
        top_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 12, 20, 12)

        self.lbl_settings_title = QLabel(tr("settings.page_title"))
        self.lbl_settings_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        top_layout.addWidget(self.lbl_settings_title)
        top_layout.addStretch()
        main_layout.addWidget(top_bar, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

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
        content_layout.addStretch(1)

        # Alias de compatibilité pour tests existants
        self.btn_open_about_dialog = getattr(self, "btn_settings_about", None)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

        return container

    def _create_settings_sources_page(self) -> QWidget:
        """Page dédiée Paramètres > Sources (Configuration des sources et synchronisation)."""
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        top_bar = QFrame()
        top_bar.setObjectName("topBarFrame")
        top_bar.setFixedHeight(50)
        top_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 12, 20, 12)

        self.lbl_settings_sources_page_title = QLabel(tr("settings.page_sources_title"))
        self.lbl_settings_sources_page_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        top_layout.addWidget(self.lbl_settings_sources_page_title)
        top_layout.addStretch()
        main_layout.addWidget(top_bar, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Carte Sources configurées et synchronisation
        card_sources = QFrame()
        card_sources.setProperty("class", "dashboard-card")
        card_sources.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        l_sources = QVBoxLayout(card_sources)
        l_sources.setContentsMargins(18, 16, 18, 16)
        l_sources.setSpacing(10)
        l_sources.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.lbl_card_sources_title = QLabel(tr("settings.section_sources_title"))
        self.lbl_card_sources_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        self.lbl_card_sources_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        l_sources.addWidget(self.lbl_card_sources_title)

        self.lbl_card_sources_desc = QLabel(tr("settings.section_sources_desc"))
        self.lbl_card_sources_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        self.lbl_card_sources_desc.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        l_sources.addWidget(self.lbl_card_sources_desc)

        self.table_settings_sources = QTableWidget()
        self.table_settings_sources.setColumnCount(5)
        self.table_settings_sources.verticalHeader().setVisible(False)
        self.table_settings_sources.verticalHeader().setDefaultSectionSize(40)
        self.table_settings_sources.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table_settings_sources.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_settings_sources.setShowGrid(False)
        self.table_settings_sources.setAlternatingRowColors(True)
        self.table_settings_sources.setMinimumHeight(140)
        self.table_settings_sources.setStyleSheet(
            "QTableWidget { background-color: #0F172A; border: 1px solid #334155; border-radius: 6px; } "
            "QHeaderView::section { background-color: #1E293B; color: #94A3B8; font-weight: 600; padding: 8px 6px; border: none; }"
        )
        self.table_settings_sources.cellDoubleClicked.connect(self._on_settings_source_double_clicked)
        l_sources.addWidget(self.table_settings_sources)

        btn_add_box = QHBoxLayout()
        self.btn_add_source_settings = QPushButton(tr("sidebar.btn_add_source"))
        self.btn_add_source_settings.setProperty("class", "secondary-btn")
        self.btn_add_source_settings.clicked.connect(self._on_add_local_folder)
        btn_add_box.addWidget(self.btn_add_source_settings)
        btn_add_box.addStretch()
        l_sources.addLayout(btn_add_box)

        content_layout.addWidget(card_sources)
        content_layout.addStretch(1)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

        self._refresh_settings_sources_table()
        return container

    def _create_settings_player_page(self) -> QWidget:
        """Page Paramètres > Lecteur (Options de veille et moteur de lecture)."""
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. En-tête
        top_bar = QFrame()
        top_bar.setObjectName("topBarFrame")
        top_bar.setFixedHeight(50)
        top_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 12, 20, 12)

        self.lbl_settings_player_page_title = QLabel(tr("settings.page_player_title"))
        self.lbl_settings_player_page_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        top_layout.addWidget(self.lbl_settings_player_page_title)
        top_layout.addStretch()
        main_layout.addWidget(top_bar, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Carte 1 : Alimentation et Veille
        card_sleep = QFrame()
        card_sleep.setProperty("class", "dashboard-card")
        l_sleep = QVBoxLayout(card_sleep)
        l_sleep.setContentsMargins(18, 16, 18, 16)
        l_sleep.setSpacing(10)

        self.lbl_card_player_title = QLabel(tr("settings.player_playback_title"))
        self.lbl_card_player_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        l_sleep.addWidget(self.lbl_card_player_title)

        self.lbl_card_player_desc = QLabel(tr("settings.player_playback_desc"))
        self.lbl_card_player_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        l_sleep.addWidget(self.lbl_card_player_desc)

        cfg = get_config_manager()

        radio_qss = """
            QRadioButton {
                color: #F8FAFC;
                font-size: 13.5px;
                font-weight: 600;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 1px solid #333846;
                background-color: #121418;
            }
            QRadioButton::indicator:hover {
                border-color: #38BDF8;
            }
            QRadioButton::indicator:checked {
                background-color: #0284C7;
                border-color: #38BDF8;
            }
        """

        self.sleep_group = QButtonGroup(self)

        # Choix 1 : Autoriser la veille
        box_allow = QVBoxLayout()
        box_allow.setSpacing(3)
        self.radio_sleep_allow = QRadioButton(tr("settings.sleep_mode_allow"))
        self.radio_sleep_allow.setStyleSheet(radio_qss)
        self.sleep_group.addButton(self.radio_sleep_allow)
        box_allow.addWidget(self.radio_sleep_allow)

        self.lbl_sleep_allow_hint = QLabel(tr("settings.sleep_mode_allow_hint"))
        self.lbl_sleep_allow_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_sleep_allow_hint.setWordWrap(True)
        box_allow.addWidget(self.lbl_sleep_allow_hint)
        l_sleep.addLayout(box_allow)

        # Choix 2 (par défaut) : Ne pas autoriser la veille sur les écrans Lecteur et Playlist
        box_screens = QVBoxLayout()
        box_screens.setSpacing(3)
        self.radio_sleep_screens = QRadioButton(tr("settings.sleep_mode_player_playlist"))
        self.radio_sleep_screens.setStyleSheet(radio_qss)
        self.sleep_group.addButton(self.radio_sleep_screens)
        box_screens.addWidget(self.radio_sleep_screens)

        self.lbl_sleep_screens_hint = QLabel(tr("settings.sleep_mode_player_playlist_hint"))
        self.lbl_sleep_screens_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_sleep_screens_hint.setWordWrap(True)
        box_screens.addWidget(self.lbl_sleep_screens_hint)
        l_sleep.addLayout(box_screens)

        # Choix 3 : Ne pas autoriser la veille
        box_always = QVBoxLayout()
        box_always.setSpacing(3)
        self.radio_sleep_always = QRadioButton(tr("settings.sleep_mode_always"))
        self.radio_sleep_always.setStyleSheet(radio_qss)
        self.sleep_group.addButton(self.radio_sleep_always)
        box_always.addWidget(self.radio_sleep_always)

        self.lbl_sleep_always_hint = QLabel(tr("settings.sleep_mode_always_hint"))
        self.lbl_sleep_always_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_sleep_always_hint.setWordWrap(True)
        box_always.addWidget(self.lbl_sleep_always_hint)
        l_sleep.addLayout(box_always)

        sleep_mode = cfg.get_sleep_mode()
        if sleep_mode == "allow":
            self.radio_sleep_allow.setChecked(True)
        elif sleep_mode == "always":
            self.radio_sleep_always.setChecked(True)
        else:
            self.radio_sleep_screens.setChecked(True)

        self.radio_sleep_allow.toggled.connect(self._on_sleep_mode_changed)
        self.radio_sleep_screens.toggled.connect(self._on_sleep_mode_changed)
        self.radio_sleep_always.toggled.connect(self._on_sleep_mode_changed)

        content_layout.addWidget(card_sleep)

        # Carte 2 : Transitions et enchaînement des pistes
        card_transitions = QFrame()
        card_transitions.setProperty("class", "dashboard-card")
        l_trans = QVBoxLayout(card_transitions)
        l_trans.setContentsMargins(18, 16, 18, 16)
        l_trans.setSpacing(12)

        self.lbl_card_transitions_title = QLabel(tr("settings.player_transitions_title"))
        self.lbl_card_transitions_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        l_trans.addWidget(self.lbl_card_transitions_title)

        self.lbl_card_transitions_desc = QLabel(tr("settings.player_transitions_desc"))
        self.lbl_card_transitions_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        l_trans.addWidget(self.lbl_card_transitions_desc)

        radio_qss = """
            QRadioButton {
                color: #F8FAFC;
                font-size: 13.5px;
                font-weight: 600;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 1px solid #333846;
                background-color: #121418;
            }
            QRadioButton::indicator:hover {
                border-color: #38BDF8;
            }
            QRadioButton::indicator:checked {
                background-color: #0284C7;
                border-color: #38BDF8;
            }
        """

        self.transition_group = QButtonGroup(self)

        # Choix 1 : Pas de fondu enchaîné (standard)
        box_standard = QVBoxLayout()
        box_standard.setSpacing(3)
        self.radio_trans_standard = QRadioButton(tr("settings.transition_standard"))
        self.radio_trans_standard.setStyleSheet(radio_qss)
        self.transition_group.addButton(self.radio_trans_standard)
        box_standard.addWidget(self.radio_trans_standard)

        self.lbl_trans_standard_hint = QLabel(tr("settings.transition_standard_hint"))
        self.lbl_trans_standard_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_trans_standard_hint.setWordWrap(True)
        box_standard.addWidget(self.lbl_trans_standard_hint)
        l_trans.addLayout(box_standard)

        # Choix 2 (par défaut) : Enchaînement instantané (gapless)
        box_gapless = QVBoxLayout()
        box_gapless.setSpacing(3)
        self.radio_trans_gapless = QRadioButton(tr("settings.transition_gapless"))
        self.radio_trans_gapless.setStyleSheet(radio_qss)
        self.transition_group.addButton(self.radio_trans_gapless)
        box_gapless.addWidget(self.radio_trans_gapless)

        self.lbl_trans_gapless_hint = QLabel(tr("settings.transition_gapless_hint"))
        self.lbl_trans_gapless_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_trans_gapless_hint.setWordWrap(True)
        box_gapless.addWidget(self.lbl_trans_gapless_hint)
        l_trans.addLayout(box_gapless)

        # Choix 3 : Fondu enchaîné (crossfade avec curseur)
        box_crossfade = QVBoxLayout()
        box_crossfade.setSpacing(3)
        self.radio_trans_crossfade = QRadioButton(tr("settings.transition_crossfade"))
        self.radio_trans_crossfade.setStyleSheet(radio_qss)
        self.transition_group.addButton(self.radio_trans_crossfade)
        box_crossfade.addWidget(self.radio_trans_crossfade)

        self.lbl_trans_crossfade_hint = QLabel(tr("settings.transition_crossfade_hint"))
        self.lbl_trans_crossfade_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_trans_crossfade_hint.setWordWrap(True)
        box_crossfade.addWidget(self.lbl_trans_crossfade_hint)

        # Conteneur curseur de durée de fondu (indenté)
        self.crossfade_container = QWidget()
        h_cf = QHBoxLayout(self.crossfade_container)
        h_cf.setContentsMargins(26, 6, 12, 4)
        h_cf.setSpacing(12)

        self.lbl_crossfade_duration = QLabel(tr("settings.crossfade_duration"))
        self.lbl_crossfade_duration.setStyleSheet("color: #CBD5E1; font-size: 12.5px; font-weight: 500;")
        h_cf.addWidget(self.lbl_crossfade_duration)

        self.slider_crossfade = QSlider(Qt.Orientation.Horizontal)
        self.slider_crossfade.setRange(1, 20)
        self.slider_crossfade.setSingleStep(1)
        self.slider_crossfade.setPageStep(2)
        self.slider_crossfade.setFixedWidth(200)
        self.slider_crossfade.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #1E293B;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #0284C7;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #38BDF8;
                border: 2px solid #0F172A;
                width: 16px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #7DD3FC;
            }
        """)
        h_cf.addWidget(self.slider_crossfade)

        self.lbl_crossfade_value = QLabel()
        self.lbl_crossfade_value.setStyleSheet("color: #38BDF8; font-size: 12.5px; font-weight: 600; min-width: 90px;")
        h_cf.addWidget(self.lbl_crossfade_value)
        h_cf.addStretch()

        box_crossfade.addWidget(self.crossfade_container)
        l_trans.addLayout(box_crossfade)

        # État initial selon la configuration
        trans_mode = cfg.get_transition_mode()
        if trans_mode == "standard":
            self.radio_trans_standard.setChecked(True)
        elif trans_mode == "crossfade":
            self.radio_trans_crossfade.setChecked(True)
        else:
            self.radio_trans_gapless.setChecked(True)

        cf_dur = cfg.get_crossfade_duration()
        self.slider_crossfade.setValue(cf_dur)
        self.lbl_crossfade_value.setText(tr("settings.crossfade_duration_val", seconds=str(cf_dur)))
        self._update_crossfade_controls_state()

        # Connexions des signaux
        self.radio_trans_standard.toggled.connect(self._on_transition_mode_changed)
        self.radio_trans_gapless.toggled.connect(self._on_transition_mode_changed)
        self.radio_trans_crossfade.toggled.connect(self._on_transition_mode_changed)
        self.slider_crossfade.valueChanged.connect(self._on_crossfade_slider_changed)

        content_layout.addWidget(card_transitions)

        # Carte 3 : Effets visuels d'ambiance
        card_effects = QFrame()
        card_effects.setProperty("class", "dashboard-card")
        l_eff = QVBoxLayout(card_effects)
        l_eff.setContentsMargins(18, 16, 18, 16)
        l_eff.setSpacing(12)

        self.lbl_card_effects_title = QLabel(tr("settings.player_effects_title"))
        self.lbl_card_effects_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        l_eff.addWidget(self.lbl_card_effects_title)

        self.lbl_card_effects_desc = QLabel(tr("settings.player_effects_desc"))
        self.lbl_card_effects_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        l_eff.addWidget(self.lbl_card_effects_desc)

        self.effect_group = QButtonGroup(self)

        # Effet 1 : Poussière d'étoiles & particules
        box_eff_part = QVBoxLayout()
        box_eff_part.setSpacing(3)
        self.radio_eff_particles = QRadioButton(f"✨ {tr('effects.particles')}")
        self.radio_eff_particles.setStyleSheet(radio_qss)
        self.effect_group.addButton(self.radio_eff_particles)
        box_eff_part.addWidget(self.radio_eff_particles)

        self.lbl_eff_particles_hint = QLabel(tr("effects.particles_hint"))
        self.lbl_eff_particles_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_eff_particles_hint.setWordWrap(True)
        box_eff_part.addWidget(self.lbl_eff_particles_hint)
        l_eff.addLayout(box_eff_part)

        # Effet 2 : Ondes néon spectrales
        box_eff_waves = QVBoxLayout()
        box_eff_waves.setSpacing(3)
        self.radio_eff_waves = QRadioButton(f"🌊 {tr('effects.waves')}")
        self.radio_eff_waves.setStyleSheet(radio_qss)
        self.effect_group.addButton(self.radio_eff_waves)
        box_eff_waves.addWidget(self.radio_eff_waves)

        self.lbl_eff_waves_hint = QLabel(tr("effects.waves_hint"))
        self.lbl_eff_waves_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_eff_waves_hint.setWordWrap(True)
        box_eff_waves.addWidget(self.lbl_eff_waves_hint)
        l_eff.addLayout(box_eff_waves)

        # Effet 3 : Pluie de comètes filantes
        box_eff_stars = QVBoxLayout()
        box_eff_stars.setSpacing(3)
        self.radio_eff_stars = QRadioButton(f"☄️ {tr('effects.stars')}")
        self.radio_eff_stars.setStyleSheet(radio_qss)
        self.effect_group.addButton(self.radio_eff_stars)
        box_eff_stars.addWidget(self.radio_eff_stars)

        self.lbl_eff_stars_hint = QLabel(tr("effects.stars_hint"))
        self.lbl_eff_stars_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_eff_stars_hint.setWordWrap(True)
        box_eff_stars.addWidget(self.lbl_eff_stars_hint)
        l_eff.addLayout(box_eff_stars)

        # Effet 4 : Hyperespace (Voyage spatial 3D)
        box_eff_warp = QVBoxLayout()
        box_eff_warp.setSpacing(3)
        self.radio_eff_warp = QRadioButton(f"🚀 {tr('effects.warp')}")
        self.radio_eff_warp.setStyleSheet(radio_qss)
        self.effect_group.addButton(self.radio_eff_warp)
        box_eff_warp.addWidget(self.radio_eff_warp)

        self.lbl_eff_warp_hint = QLabel(tr("effects.warp_hint"))
        self.lbl_eff_warp_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_eff_warp_hint.setWordWrap(True)
        box_eff_warp.addWidget(self.lbl_eff_warp_hint)
        l_eff.addLayout(box_eff_warp)

        # Effet 4b : Hyperespace dynamique (Navigation 3D avec changements de trajectoire)
        box_eff_warp_dyn = QVBoxLayout()
        box_eff_warp_dyn.setSpacing(3)
        self.radio_eff_warp_dynamic = QRadioButton(f"🛸 {tr('effects.warp_dynamic')}")
        self.radio_eff_warp_dynamic.setStyleSheet(radio_qss)
        self.effect_group.addButton(self.radio_eff_warp_dynamic)
        box_eff_warp_dyn.addWidget(self.radio_eff_warp_dynamic)

        self.lbl_eff_warp_dynamic_hint = QLabel(tr("effects.warp_dynamic_hint"))
        self.lbl_eff_warp_dynamic_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_eff_warp_dynamic_hint.setWordWrap(True)
        box_eff_warp_dyn.addWidget(self.lbl_eff_warp_dynamic_hint)
        l_eff.addLayout(box_eff_warp_dyn)

        # Effet 5 : Aurore boréale
        box_eff_aurora = QVBoxLayout()
        box_eff_aurora.setSpacing(3)
        self.radio_eff_aurora = QRadioButton(f"🌌 {tr('effects.aurora')}")
        self.radio_eff_aurora.setStyleSheet(radio_qss)
        self.effect_group.addButton(self.radio_eff_aurora)
        box_eff_aurora.addWidget(self.radio_eff_aurora)

        self.lbl_eff_aurora_hint = QLabel(tr("effects.aurora_hint"))
        self.lbl_eff_aurora_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_eff_aurora_hint.setWordWrap(True)
        box_eff_aurora.addWidget(self.lbl_eff_aurora_hint)
        l_eff.addLayout(box_eff_aurora)

        # Effet 6 : Barres rétro (Égaliseur de spectre)
        box_eff_bars = QVBoxLayout()
        box_eff_bars.setSpacing(3)
        self.radio_eff_bars = QRadioButton(f"📊 {tr('effects.bars')}")
        self.radio_eff_bars.setStyleSheet(radio_qss)
        self.effect_group.addButton(self.radio_eff_bars)
        box_eff_bars.addWidget(self.radio_eff_bars)

        self.lbl_eff_bars_hint = QLabel(tr("effects.bars_hint"))
        self.lbl_eff_bars_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_eff_bars_hint.setWordWrap(True)
        box_eff_bars.addWidget(self.lbl_eff_bars_hint)
        l_eff.addLayout(box_eff_bars)

        # Effet 7 : Barres rétro plein écran
        box_eff_bars_full = QVBoxLayout()
        box_eff_bars_full.setSpacing(3)
        self.radio_eff_bars_full = QRadioButton(f"📶 {tr('effects.bars_full')}")
        self.radio_eff_bars_full.setStyleSheet(radio_qss)
        self.effect_group.addButton(self.radio_eff_bars_full)
        box_eff_bars_full.addWidget(self.radio_eff_bars_full)

        self.lbl_eff_bars_full_hint = QLabel(tr("effects.bars_full_hint"))
        self.lbl_eff_bars_full_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_eff_bars_full_hint.setWordWrap(True)
        box_eff_bars_full.addWidget(self.lbl_eff_bars_full_hint)
        l_eff.addLayout(box_eff_bars_full)

        # Effet 8 : Aucun effet (désactivé)
        box_eff_none = QVBoxLayout()
        box_eff_none.setSpacing(3)
        self.radio_eff_none = QRadioButton(f"🚫 {tr('effects.none')}")
        self.radio_eff_none.setStyleSheet(radio_qss)
        self.effect_group.addButton(self.radio_eff_none)
        box_eff_none.addWidget(self.radio_eff_none)

        self.lbl_eff_none_hint = QLabel(tr("effects.none_hint"))
        self.lbl_eff_none_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_eff_none_hint.setWordWrap(True)
        box_eff_none.addWidget(self.lbl_eff_none_hint)
        l_eff.addLayout(box_eff_none)

        # État initial selon la configuration
        cur_eff = cfg.get_visual_effect()
        if cur_eff == "waves":
            self.radio_eff_waves.setChecked(True)
        elif cur_eff == "stars":
            self.radio_eff_stars.setChecked(True)
        elif cur_eff == "warp":
            self.radio_eff_warp.setChecked(True)
        elif cur_eff == "warp_dynamic":
            self.radio_eff_warp_dynamic.setChecked(True)
        elif cur_eff == "aurora":
            self.radio_eff_aurora.setChecked(True)
        elif cur_eff == "bars":
            self.radio_eff_bars.setChecked(True)
        elif cur_eff == "bars_full":
            self.radio_eff_bars_full.setChecked(True)
        elif cur_eff == "none":
            self.radio_eff_none.setChecked(True)
        else:
            self.radio_eff_particles.setChecked(True)

        self.radio_eff_particles.toggled.connect(self._on_visual_effect_changed)
        self.radio_eff_waves.toggled.connect(self._on_visual_effect_changed)
        self.radio_eff_stars.toggled.connect(self._on_visual_effect_changed)
        self.radio_eff_warp.toggled.connect(self._on_visual_effect_changed)
        self.radio_eff_warp_dynamic.toggled.connect(self._on_visual_effect_changed)
        self.radio_eff_aurora.toggled.connect(self._on_visual_effect_changed)
        self.radio_eff_bars.toggled.connect(self._on_visual_effect_changed)
        self.radio_eff_bars_full.toggled.connect(self._on_visual_effect_changed)
        self.radio_eff_none.toggled.connect(self._on_visual_effect_changed)

        content_layout.addWidget(card_effects)

        # Carte 3 : Moteur de lecture (VLC)
        card_vlc = QFrame()
        card_vlc.setProperty("class", "dashboard-card")
        l_vlc = QVBoxLayout(card_vlc)
        l_vlc.setContentsMargins(18, 16, 18, 16)
        l_vlc.setSpacing(10)

        self.lbl_card_vlc_title = QLabel(tr("settings.player_engine_title"))
        self.lbl_card_vlc_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        l_vlc.addWidget(self.lbl_card_vlc_title)

        self.lbl_card_vlc_desc = QLabel(tr("settings.player_engine_desc"))
        self.lbl_card_vlc_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        l_vlc.addWidget(self.lbl_card_vlc_desc)

        is_avail = self.player_service.is_vlc_available
        status_txt = tr("settings.player_engine_active") if is_avail else tr("settings.player_engine_inactive")
        status_color = "#34D399" if is_avail else "#EF4444"
        self.lbl_vlc_status_val = QLabel(
            f"• <b>{tr('settings.player_engine_status')}</b> <span style='color: {status_color}; font-weight: 600;'>{status_txt}</span>"
        )
        self.lbl_vlc_status_val.setStyleSheet("font-size: 12.5px; color: #CBD5E1;")
        l_vlc.addWidget(self.lbl_vlc_status_val)

        content_layout.addWidget(card_vlc)

        # Carte 4 : Paramètres du Blind Test
        card_bt = QFrame()
        card_bt.setProperty("class", "dashboard-card")
        self.card_settings_blind_test = card_bt
        l_bt = QVBoxLayout(card_bt)
        l_bt.setContentsMargins(18, 16, 18, 16)
        l_bt.setSpacing(12)

        self.lbl_card_bt_title = QLabel("🎭  " + tr("blind_test.settings_title"))
        self.lbl_card_bt_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        l_bt.addWidget(self.lbl_card_bt_title)

        self.lbl_card_bt_desc = QLabel(tr("settings.blind_test_desc"))
        self.lbl_card_bt_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        l_bt.addWidget(self.lbl_card_bt_desc)

        spin_qss = """
            QSpinBox {
                background-color: #20242D;
                color: #F8FAFC;
                border: 1px solid #333846;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 12.5px;
                font-weight: 600;
            }
            QSpinBox:focus {
                border-color: #38BDF8;
            }
        """

        inputs_layout = QHBoxLayout()
        inputs_layout.setSpacing(20)

        # 1. Durée du décompte
        cd_box = QHBoxLayout()
        cd_box.setSpacing(8)
        self.lbl_bt_countdown = QLabel(tr("blind_test.countdown_label"))
        self.lbl_bt_countdown.setStyleSheet("color: #CBD5E1; font-size: 12.5px; font-weight: 500;")
        cd_box.addWidget(self.lbl_bt_countdown)

        self.spin_bt_countdown = QSpinBox()
        self.spin_bt_countdown.setRange(5, 120)
        self.spin_bt_countdown.setSingleStep(5)
        self.spin_bt_countdown.setSuffix(" s")
        self.spin_bt_countdown.setValue(cfg.get_blind_test_countdown())
        self.spin_bt_countdown.setFixedWidth(80)
        self.spin_bt_countdown.setStyleSheet(spin_qss)
        self.spin_bt_countdown.valueChanged.connect(self._on_blind_test_settings_changed)
        cd_box.addWidget(self.spin_bt_countdown)
        inputs_layout.addLayout(cd_box)

        # 2. Durée de la découverte
        rev_box = QHBoxLayout()
        rev_box.setSpacing(8)
        self.lbl_bt_reveal = QLabel(tr("blind_test.reveal_label"))
        self.lbl_bt_reveal.setStyleSheet("color: #CBD5E1; font-size: 12.5px; font-weight: 500;")
        rev_box.addWidget(self.lbl_bt_reveal)

        self.spin_bt_reveal = QSpinBox()
        self.spin_bt_reveal.setRange(3, 60)
        self.spin_bt_reveal.setSingleStep(1)
        self.spin_bt_reveal.setSuffix(" s")
        self.spin_bt_reveal.setValue(cfg.get_blind_test_reveal())
        self.spin_bt_reveal.setFixedWidth(80)
        self.spin_bt_reveal.setStyleSheet(spin_qss)
        self.spin_bt_reveal.valueChanged.connect(self._on_blind_test_settings_changed)
        rev_box.addWidget(self.spin_bt_reveal)
        inputs_layout.addLayout(rev_box)

        # 3. Durée du fondu sonore de transition
        fade_box = QHBoxLayout()
        fade_box.setSpacing(8)
        self.lbl_bt_fade = QLabel(tr("blind_test.fade_label"))
        self.lbl_bt_fade.setStyleSheet("color: #CBD5E1; font-size: 12.5px; font-weight: 500;")
        fade_box.addWidget(self.lbl_bt_fade)

        self.spin_bt_fade = QSpinBox()
        self.spin_bt_fade.setRange(0, 10)
        self.spin_bt_fade.setSingleStep(1)
        self.spin_bt_fade.setSuffix(" s")
        self.spin_bt_fade.setValue(cfg.get_blind_test_fade())
        self.spin_bt_fade.setFixedWidth(80)
        self.spin_bt_fade.setStyleSheet(spin_qss)
        self.spin_bt_fade.valueChanged.connect(self._on_blind_test_settings_changed)
        fade_box.addWidget(self.spin_bt_fade)
        inputs_layout.addLayout(fade_box)

        inputs_layout.addStretch()
        l_bt.addLayout(inputs_layout)

        # Label d'information résumé de la manche
        self.lbl_bt_total = QLabel()
        self.lbl_bt_total.setStyleSheet("color: #38BDF8; font-size: 12px; font-weight: 500; margin-top: 4px;")
        self._update_blind_test_summary_label()
        l_bt.addWidget(self.lbl_bt_total)

        content_layout.addWidget(card_bt)
        content_layout.addStretch(1)

        # Rendre accessibles les contrôles sur le widget de page
        setattr(container, "spin_bt_countdown", self.spin_bt_countdown)  # noqa: B010
        setattr(container, "spin_bt_reveal", self.spin_bt_reveal)  # noqa: B010
        setattr(container, "spin_bt_fade", self.spin_bt_fade)  # noqa: B010
        setattr(container, "lbl_bt_total", self.lbl_bt_total)  # noqa: B010

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

        return container

    def _update_blind_test_summary_label(self) -> None:
        if not hasattr(self, "spin_bt_countdown") or not hasattr(self, "lbl_bt_total"):
            return
        cd = self.spin_bt_countdown.value()
        rev = self.spin_bt_reveal.value()
        fade = self.spin_bt_fade.value()
        tot = cd + rev
        self.lbl_bt_total.setText(
            tr("blind_test.total_duration", total=tot, countdown=cd, reveal=rev, fade=fade)
        )

    def _on_blind_test_settings_changed(self) -> None:
        if not hasattr(self, "spin_bt_countdown"):
            return
        cd = self.spin_bt_countdown.value()
        rev = self.spin_bt_reveal.value()
        fade = self.spin_bt_fade.value()

        # Le fondu ne peut excéder la durée de la découverte
        if fade > rev:
            fade = rev
            self.spin_bt_fade.blockSignals(True)
            self.spin_bt_fade.setValue(fade)
            self.spin_bt_fade.blockSignals(False)

        cfg = get_config_manager()
        cfg.set_blind_test_countdown(cd)
        cfg.set_blind_test_reveal(rev)
        cfg.set_blind_test_fade(fade)

        self._update_blind_test_summary_label()

        if hasattr(self, "page_blind_test") and self.page_blind_test:
            self.page_blind_test.set_durations(cd, rev, fade)

    def _create_settings_about_page(self) -> QWidget:
        """Page dédiée Paramètres > À propos d'AMSO."""
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # En-tête de page standardisé
        top_bar = QFrame()
        top_bar.setObjectName("topBarFrame")
        top_bar.setFixedHeight(50)
        top_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 12, 20, 12)

        self.lbl_settings_about_page_title = QLabel(tr("settings.about_page_title"))
        self.lbl_settings_about_page_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        top_layout.addWidget(self.lbl_settings_about_page_title)
        top_layout.addStretch()
        main_layout.addWidget(top_bar, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 1. En-tête Identité AMSO & Version unifié (Logo à gauche + Colonne droite : Titre + Description + Rétro-bars sous le texte)
        top_card = QFrame()
        top_card.setFixedHeight(172)
        top_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        top_card.setStyleSheet("""
            QFrame#aboutTopCard {
                background-color: #15181E;
                border: 1px solid #282C37;
                border-radius: 18px;
            }
        """)
        top_card.setObjectName("aboutTopCard")

        top_layout = QHBoxLayout(top_card)
        top_layout.setContentsMargins(20, 16, 16, 16)
        top_layout.setSpacing(22)
        top_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Logo officiel AMSO (aligné tout en haut)
        lbl_logo = QLabel()
        icon_pm = get_app_logo_pixmap()
        if not icon_pm.isNull():
            lbl_logo.setPixmap(
                icon_pm.scaled(
                    132,
                    132,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            lbl_logo.setText("🎵")
            lbl_logo.setStyleSheet("font-size: 64px;")
        lbl_logo.setFixedSize(132, 132)
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        lbl_logo.setStyleSheet("background: transparent; border: none; padding: 0px; margin: 0px;")
        top_layout.addWidget(lbl_logo, 0, Qt.AlignmentFlag.AlignTop)

        # Colonne droite : Titre aligné en haut avec l'icône, puis description, puis barres en dessous
        right_col = QVBoxLayout()
        right_col.setContentsMargins(0, 0, 0, 0)
        right_col.setSpacing(6)
        right_col.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Ligne 1 : Nom complet + AMSO + Badge Version (aligné tout en haut du cadre)
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(10)
        title_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.lbl_about_app_name = QLabel(tr("dialog.about_app_name"))
        self.lbl_about_app_name.setStyleSheet(
            "color: #F8FAFC; font-size: 20px; font-weight: 800; letter-spacing: 0.5px; padding: 0px; margin: 0px;"
        )
        title_row.addWidget(self.lbl_about_app_name)

        acronym_lbl = QLabel("AMSO")
        acronym_lbl.setStyleSheet("color: #38BDF8; font-size: 14px; font-weight: 700; padding: 0px; margin: 0px;")
        title_row.addWidget(acronym_lbl)

        ver_badge = QLabel(f"v{__version__}")
        ver_badge.setStyleSheet("""
            background-color: #0369A1;
            color: #FFFFFF;
            padding: 2px 10px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 700;
        """)
        title_row.addWidget(ver_badge)
        title_row.addStretch()
        right_col.addLayout(title_row)

        # Ligne 2 : Description
        self.lbl_about_desc = QLabel(tr("dialog.about_description"))
        self.lbl_about_desc.setWordWrap(True)
        self.lbl_about_desc.setStyleSheet(
            "color: #CBD5E1; font-size: 13px; line-height: 1.45; padding: 0px; margin: 0px;"
        )
        right_col.addWidget(self.lbl_about_desc)

        # Ligne 3 : Barres de spectre rétro sous le texte (alignées à gauche avec le texte, collant au cadre à droite)
        self.about_visual_effect = VisualEffectWidget(
            VisualEffectWidget.EFFECT_BARS,
            parent=top_card,
        )
        self.about_visual_effect.set_demo_mode(False)
        self.about_visual_effect.set_bars_aligned_left(True)
        self.about_visual_effect.setFixedHeight(62)
        self.about_visual_effect.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.about_visual_effect.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.about_visual_effect.setStyleSheet("background: transparent; border: none;")

        # Synchronisation immédiate avec l'état actuel de lecture
        if self.player_service.is_playing:
            self.about_visual_effect.set_playback_state("playing")
        else:
            self.about_visual_effect.set_playback_state("stopped")
        self.about_visual_effect.update_audio_volume(
            self.player_service.volume,
            getattr(self.player_service, "is_muted", False),
        )
        if self.player_service.current_track:
            self.about_visual_effect.set_track(self.player_service.current_track)

        # Écoute réactive des événements de lecture audio
        self.player_service.state_changed.connect(self.about_visual_effect.set_playback_state)
        self.player_service.position_changed.connect(self.about_visual_effect.update_audio_time)
        self.player_service.track_changed.connect(self.about_visual_effect.set_track)
        self.player_service.volume_changed.connect(self.about_visual_effect.update_audio_volume)

        right_col.addWidget(self.about_visual_effect, 0, Qt.AlignmentFlag.AlignBottom)
        top_layout.addLayout(right_col, 1)

        content_layout.addWidget(top_card)

        # 2. Carte de vérification des mises à jour & statut
        card_update = QFrame()
        card_update.setProperty("class", "dashboard-card")
        update_row = QHBoxLayout(card_update)
        update_row.setContentsMargins(20, 14, 20, 14)
        update_row.setSpacing(14)
        update_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.btn_check_updates_about = QPushButton(tr("settings.btn_check_updates"))
        self.btn_check_updates_about.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_check_updates_about.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #E2E8F0;
                font-size: 12px;
                font-weight: 600;
                padding: 7px 16px;
                border: 1px solid #334155;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #334155;
                border-color: #475569;
                color: #FFFFFF;
            }
        """)
        self.btn_check_updates_about.clicked.connect(lambda: self._check_for_updates(manual=True))
        update_row.addWidget(self.btn_check_updates_about)

        self.lbl_update_status_about = QLabel("")
        self.lbl_update_status_about.setStyleSheet("color: #94A3B8; font-size: 12.5px; font-weight: 500;")
        update_row.addWidget(self.lbl_update_status_about)

        self.btn_update_download = QPushButton(tr("settings.btn_download_update"))
        self.btn_update_download.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_update_download.setStyleSheet("""
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 700;
                padding: 7px 14px;
                border: 1px solid #38BDF8;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #0369A1;
                border-color: #7DD3FC;
            }
        """)
        self.btn_update_download.setVisible(False)
        self.btn_update_download.clicked.connect(self._open_latest_release_url)
        update_row.addWidget(self.btn_update_download)

        update_row.addStretch()
        content_layout.addWidget(card_update)

        # 3. Carte Soutenir le projet (Faire un don)
        card_support = QFrame()
        card_support.setProperty("class", "dashboard-card")
        l_support = QVBoxLayout(card_support)
        l_support.setContentsMargins(22, 18, 22, 18)
        l_support.setSpacing(14)

        # Sous-titre Soutien
        self.lbl_about_support_title = QLabel("💖  " + tr("dialog.about_support_title"))
        self.lbl_about_support_title.setStyleSheet("color: #F1F5F9; font-size: 14px; font-weight: 700;")
        l_support.addWidget(self.lbl_about_support_title)

        # Ligne de dons : Ko-fi et GitHub Sponsors
        donate_row = QHBoxLayout()
        donate_row.setSpacing(12)

        # Bouton Ko-fi
        self.btn_about_kofi = QPushButton(tr("dialog.about_btn_kofi"))
        self.btn_about_kofi.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_about_kofi.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF5E5B, stop:1 #D9413E);
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 700;
                padding: 10px 22px;
                border: 1px solid #FFA4A2;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF7673, stop:1 #FF5E5B);
                border-color: #FFFFFF;
            }
        """)
        self.btn_about_kofi.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(URL_KO_FI)))
        donate_row.addWidget(self.btn_about_kofi)

        # Bouton GitHub Sponsors
        self.btn_about_sponsors = QPushButton(tr("dialog.about_btn_sponsors"))
        self.btn_about_sponsors.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_about_sponsors.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #EA4AAA, stop:1 #C5288B);
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 700;
                padding: 10px 22px;
                border: 1px solid #F9A8D4;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F062BA, stop:1 #EA4AAA);
                border-color: #FFFFFF;
            }
        """)
        self.btn_about_sponsors.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(URL_GITHUB_SPONSORS)))
        donate_row.addWidget(self.btn_about_sponsors)

        donate_row.addStretch()
        l_support.addLayout(donate_row)

        # Alias de compatibilité
        self.btn_about_donate = self.btn_about_kofi
        content_layout.addWidget(card_support)

        # 4. Carte Pages officielles (séparée par l'espacement standard, sans ligne horizontale)
        card_official = QFrame()
        card_official.setProperty("class", "dashboard-card")
        l_official = QVBoxLayout(card_official)
        l_official.setContentsMargins(22, 18, 22, 18)
        l_official.setSpacing(14)

        # Sous-titre Pages officielles
        self.lbl_about_official_title = QLabel("🌐  " + tr("dialog.about_official_pages_title"))
        self.lbl_about_official_title.setStyleSheet("color: #F1F5F9; font-size: 14px; font-weight: 700;")
        l_official.addWidget(self.lbl_about_official_title)

        # Ligne de pages officielles : Dépôt GitHub et Page Itch.io
        official_row = QHBoxLayout()
        official_row.setSpacing(12)

        self.btn_about_github = QPushButton(tr("dialog.about_btn_github"))
        self.btn_about_github.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_about_github.setProperty("class", "secondary-btn")
        self.btn_about_github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(URL_GITHUB_REPO)))
        official_row.addWidget(self.btn_about_github)

        self.btn_about_itch = QPushButton(tr("dialog.about_btn_itch"))
        self.btn_about_itch.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_about_itch.setProperty("class", "secondary-btn")
        self.btn_about_itch.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(URL_ITCH_IO)))
        official_row.addWidget(self.btn_about_itch)

        official_row.addStretch()
        l_official.addLayout(official_row)
        content_layout.addWidget(card_official)

        # 5. Carte Crédits & Technologies Open Source (placée après Pages officielles)
        card_credits = QFrame()
        card_credits.setProperty("class", "dashboard-card")
        l_credits = QVBoxLayout(card_credits)
        l_credits.setContentsMargins(22, 18, 22, 18)
        l_credits.setSpacing(10)

        self.lbl_about_credits_title = QLabel("👍  " + tr("dialog.about_credits_title"))
        self.lbl_about_credits_title.setStyleSheet("color: #F1F5F9; font-size: 14px; font-weight: 700;")
        l_credits.addWidget(self.lbl_about_credits_title)

        self.lbl_about_credits_tech = QLabel(tr("dialog.about_credits_tech"))
        self.lbl_about_credits_tech.setWordWrap(True)
        self.lbl_about_credits_tech.setStyleSheet("color: #94A3B8; font-size: 13px; line-height: 1.4;")
        l_credits.addWidget(self.lbl_about_credits_tech)

        self.lbl_about_license = QLabel(tr("dialog.about_license"))
        self.lbl_about_license.setStyleSheet("color: #64748B; font-size: 11px; font-style: italic; margin-top: 4px;")
        l_credits.addWidget(self.lbl_about_license)

        content_layout.addWidget(card_credits)
        content_layout.addStretch(1)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

        self._refresh_update_ui()
        return container

    def _refresh_settings_sources_table(self) -> None:
        """Remplit le tableau des sources dans la page Paramètres > Sources."""
        if not hasattr(self, "table_settings_sources"):
            return

        self.table_settings_sources.setHorizontalHeaderLabels(
            [
                tr("settings.col_source_name"),
                tr("settings.col_source_path"),
                tr("settings.col_source_mode"),
                tr("settings.col_source_last_scan"),
                tr("settings.col_source_actions"),
            ]
        )
        header = self.table_settings_sources.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table_settings_sources.setColumnWidth(4, 135)

        sources = self.db.get_sources()
        self.table_settings_sources.setRowCount(len(sources))

        mode_labels = {
            "manual": tr("sync_mode.manual"),
            "startup": tr("sync_mode.startup"),
            "interval": tr("sync_mode.interval"),
            "realtime": tr("sync_mode.realtime"),
        }

        for row, src in enumerate(sources):
            # Nom
            icon_str = "📁" if src.source_type == SourceType.LOCAL else "☁️"
            name_item = QTableWidgetItem(f"{icon_str}  {src.name}")
            name_item.setToolTip(src.name)
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table_settings_sources.setItem(row, 0, name_item)

            # Chemin
            path_item = QTableWidgetItem(src.path_or_uri)
            path_item.setToolTip(src.path_or_uri)
            path_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            path_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table_settings_sources.setItem(row, 1, path_item)

            raw_mode = getattr(src, "sync_mode", "manual") or "manual"
            interval_m = getattr(src, "sync_interval_minutes", 60) or 60
            interval_s = getattr(src, "sync_interval_seconds", 60) or 60
            if raw_mode == "interval":
                mode_text = f"⏱️  {interval_m} min"
            elif raw_mode == "realtime":
                mode_text = f"⚡  {mode_labels.get('realtime', 'En continu')} ({interval_s}s)"
            elif raw_mode == "startup":
                mode_text = "🚀  " + mode_labels.get("startup", "Au démarrage")
            else:
                mode_text = "✋  " + mode_labels.get("manual", "Manuel")

            mode_item = QTableWidgetItem(mode_text)
            mode_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            mode_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table_settings_sources.setItem(row, 2, mode_item)

            # Dernière synchro
            if src.last_scanned_at:
                date_str = src.last_scanned_at[:16].replace("T", " ")
            else:
                date_str = tr("settings.last_scan_never")
            last_item = QTableWidgetItem(date_str)
            last_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            last_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
            self.table_settings_sources.setItem(row, 3, last_item)

            # Action : Bouton Modifier (largeur garantie 135px, aucune troncature)
            btn_edit = QPushButton(tr("settings.btn_edit_source"))
            btn_edit.setProperty("class", "secondary-btn")
            btn_edit.setStyleSheet("padding: 4px 12px; font-size: 11.5px; margin: 2px;")
            btn_edit.clicked.connect(lambda checked=False, s=src: self._on_edit_source_properties(s))
            self.table_settings_sources.setCellWidget(row, 4, btn_edit)

        total_h = 42 + len(sources) * 40
        self.table_settings_sources.setFixedHeight(max(140, min(total_h, 400)))

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
        self.trash_table.setHorizontalHeaderLabels([
            tr("trash.col_filename"),
            tr("trash.col_path"),
            tr("trash.col_deleted_at"),
            tr("trash.col_status"),
        ])
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

    def _check_for_updates(self, manual: bool = False) -> None:
        """Lance une vérification non bloquante de mise à jour sur GitHub Releases."""
        if hasattr(self, "update_worker") and self.update_worker and self.update_worker.isRunning():
            return

        if manual:
            self._last_update_check["status"] = "checking"
            self._refresh_update_ui()
            self.status_label.setText(tr("settings.update_checking"))

        self.update_worker = UpdateCheckerWorker(parent=self)
        self.update_worker.update_available.connect(self._on_update_available)
        self.update_worker.check_finished.connect(
            lambda has_update, detail: self._on_update_check_finished(has_update, detail, manual=manual)
        )
        self.update_worker.start()

    def _on_update_available(self, latest_version: str, release_url: str) -> None:
        """Affiche la bannière discrète de mise à jour au bas de la fenêtre."""
        if hasattr(self, "update_banner") and self.update_banner:
            self.update_banner.show_update(latest_version, release_url)

    def _on_update_check_finished(self, has_update: bool, detail: str, manual: bool = False) -> None:
        """Met à jour l'état de l'application après toute vérification (automatique ou manuelle)."""
        worker = getattr(self, "update_worker", None)
        latest_tag = getattr(worker, "latest_tag", "") or detail
        release_url = getattr(worker, "release_url", "") or URL_GITHUB_RELEASES
        published_date = getattr(worker, "published_date", "")

        if has_update:
            self._last_update_check = {
                "status": "available",
                "version": latest_tag,
                "date": published_date,
                "url": release_url,
                "checked_at": time.time(),
            }
        elif detail and not detail.lower().startswith("status") and "error" not in detail.lower() and "exception" not in detail.lower():
            # Vérification réussie sans mise à jour plus récente
            self._last_update_check = {
                "status": "latest",
                "version": __version__,
                "date": published_date,
                "url": release_url,
                "checked_at": time.time(),
            }
        else:
            # Erreur de connexion ou API indisponible
            self._last_update_check = {
                "status": "error",
                "version": "",
                "date": "",
                "url": "",
                "error": detail,
                "checked_at": time.time(),
            }

        self._refresh_update_ui()

        if manual:
            self._on_manual_update_check_finished(has_update, detail)

    def _refresh_update_ui(self) -> None:
        """Met à jour les éléments de la page À propos et les boutons selon l'état actuel de mise à jour."""
        if not hasattr(self, "lbl_update_status_about"):
            return

        status = self._last_update_check.get("status", "pending")
        if status == "checking":
            self.lbl_update_status_about.setText(f"⏳ {tr('settings.update_checking')}")
            self.lbl_update_status_about.setStyleSheet("color: #38BDF8; font-size: 12px; font-weight: 500;")
            if hasattr(self, "btn_update_download"):
                self.btn_update_download.setVisible(False)
        elif status == "latest":
            msg = tr("settings.update_latest").format(version=__version__)
            self.lbl_update_status_about.setText(msg)
            self.lbl_update_status_about.setStyleSheet("color: #4ADE80; font-size: 12px; font-weight: 600;")
            if hasattr(self, "btn_update_download"):
                self.btn_update_download.setVisible(False)
        elif status == "available":
            ver = self._last_update_check.get("version", "")
            date_str = self._last_update_check.get("date", "")
            current_lang = get_i18n().current_language
            if date_str:
                date_formatted = f" du {date_str}" if current_lang == "fr" else f" ({date_str})"
            else:
                date_formatted = ""
            msg = tr("settings.update_available").format(version=ver, date=date_formatted)
            self.lbl_update_status_about.setText(msg)
            self.lbl_update_status_about.setStyleSheet("color: #FBBF24; font-size: 12px; font-weight: 700;")
            if hasattr(self, "btn_update_download"):
                self.btn_update_download.setVisible(True)
                self.btn_update_download.setText(tr("settings.btn_download_update"))
        elif status == "error":
            self.lbl_update_status_about.setText(tr("settings.update_error"))
            self.lbl_update_status_about.setStyleSheet("color: #94A3B8; font-size: 12px;")
            if hasattr(self, "btn_update_download"):
                self.btn_update_download.setVisible(False)
        else:
            # "pending"
            self.lbl_update_status_about.setText("")
            if hasattr(self, "btn_update_download"):
                self.btn_update_download.setVisible(False)

    def _open_latest_release_url(self) -> None:
        """Ouvre la page GitHub Releases de la dernière version dans le navigateur."""
        url = self._last_update_check.get("url") or URL_GITHUB_RELEASES
        QDesktopServices.openUrl(QUrl(url))

    def _on_manual_update_check_finished(self, has_update: bool, detail: str) -> None:
        """Affiche le retour d'une vérification manuelle initiée par l'utilisateur."""
        if not has_update:
            status = self._last_update_check.get("status")
            if status == "error":
                self.status_label.setText(tr("settings.update_error"))
            else:
                msg = tr("update.already_latest").format(version=__version__)
                self.status_label.setText(f"✓ {msg}")
            QTimer.singleShot(4000, lambda: self.status_label.setText(tr("status.ready")))

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

    def retranslate_ui(self) -> None:
        """Applique les traductions de la langue active à l'ensemble de l'interface."""
        self.setWindowTitle(f"{tr('app.window_title')} v{__version__}")

        # Tiroirs
        if hasattr(self, "drawer_player"):
            self.drawer_player.set_title(tr("sidebar.drawer_player"))
        if hasattr(self, "drawer_games"):
            self.drawer_games.set_title(tr("sidebar.drawer_games"))
        self.drawer_library.set_title(tr("sidebar.drawer_library"))
        self.drawer_tools.set_title(tr("sidebar.drawer_tools"))
        self.drawer_stats.set_title(tr("sidebar.drawer_stats"))
        self.drawer_sources.set_title(tr("sidebar.drawer_sources"))
        self.drawer_settings.set_title(tr("sidebar.drawer_settings"))

        # Boutons de tiroir
        if hasattr(self, "btn_player"):
            self.btn_player.setText(tr("sidebar.nav_player"))
        if hasattr(self, "btn_blind_test"):
            self.btn_blind_test.setText(tr("sidebar.nav_blind_test"))
        if hasattr(self, "btn_playlist"):
            self.btn_playlist.setText(tr("sidebar.nav_playlist"))
        self.btn_all_tracks.setText(tr("sidebar.nav_all_tracks"))
        self.btn_by_folder.setText(tr("sidebar.nav_by_folder"))
        self.btn_duplicates.setText(tr("sidebar.nav_duplicates"))
        self.btn_stats_page.setText(tr("sidebar.nav_stats_page"))
        self.btn_settings_general.setText(tr("sidebar.nav_settings_general"))
        if hasattr(self, "btn_settings_sources"):
            self.btn_settings_sources.setText(tr("sidebar.nav_settings_sources"))
        if hasattr(self, "btn_settings_player"):
            self.btn_settings_player.setText(tr("sidebar.nav_settings_player"))
        if hasattr(self, "btn_settings_logs"):
            self.btn_settings_logs.setText(tr("sidebar.nav_settings_logs"))
        if hasattr(self, "btn_settings_about"):
            self.btn_settings_about.setText(tr("sidebar.nav_settings_about"))
        if hasattr(self, "btn_activity_feed") and not (self.scan_worker and self.scan_worker.isRunning()):
            self.btn_activity_feed.setText("⚡ " + tr("status.activity_feed"))
        self.btn_add_source.setText(tr("sidebar.btn_add_source"))

        # Page Morceaux
        self.search_edit.setPlaceholderText(tr("topbar.search_placeholder"))
        self.btn_cancel_scan.setText(tr("status.cancel"))

        if not (self.scan_worker and self.scan_worker.isRunning()):
            if not getattr(self, "_status_is_alert", False):
                self.status_label.setText(tr("status.ready"))
                self.status_label.setToolTip("")
                self.status_label.setCursor(Qt.CursorShape.ArrowCursor)

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

        # Page Par dossiers
        self.lbl_folders_page_title.setText(tr("folders.page_title"))
        self.lbl_tree_title.setText(tr("folders.tree_title"))
        self.btn_refresh_tree.setToolTip(tr("folders.btn_refresh"))
        self.btn_expand_tree.setToolTip(tr("folders.btn_expand_all"))
        self.btn_collapse_tree.setToolTip(tr("folders.btn_collapse_all"))
        self.cb_recursive.setText(tr("folders.include_subfolders"))
        self.folder_search_edit.setPlaceholderText(tr("folders.search_placeholder"))
        self.lbl_placeholder_title.setText(tr("folders.empty_selection_title"))
        self.lbl_placeholder_desc.setText(tr("folders.empty_selection_desc"))
        self.folder_tree.setHeaderLabels([tr("folders.tree_col_folder"), tr("folders.tree_col_count")])
        self.folder_table_model.notify_language_changed()
        cnt = self.folder_table_model.rowCount()
        count_key = "folders.track_count_singular" if cnt == 1 else "folders.track_count"
        self.lbl_folder_count_badge.setText(tr(count_key, count=f"{cnt:,}"))

        cur_item = self.folder_tree.currentItem()
        if cur_item:
            cdata = cur_item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(cdata, dict) and cdata.get("folder_path"):
                fp = cdata.get("folder_path")
                self.lbl_folder_breadcrumb.setToolTip(f"{fp}\n({tr('folders.breadcrumb_tooltip')})")

        # Page Paramètres
        self.lbl_settings_title.setText(tr("settings.page_title"))
        if hasattr(self, "lbl_settings_sources_page_title"):
            self.lbl_settings_sources_page_title.setText(tr("settings.page_sources_title"))
        if hasattr(self, "lbl_card_sources_title"):
            self.lbl_card_sources_title.setText(tr("settings.section_sources_title"))
            self.lbl_card_sources_desc.setText(tr("settings.section_sources_desc"))
            self.btn_add_source_settings.setText(tr("sidebar.btn_add_source"))
            self._refresh_settings_sources_table()
        self.lbl_card_lang_title.setText(tr("settings.section_language"))
        self.lbl_card_lang_desc.setText(tr("settings.language_desc"))
        self.lbl_card_storage_title.setText(tr("settings.section_storage"))
        self.btn_open_data_folder.setText(tr("settings.btn_open_folder"))

        # Page Paramètres > À propos
        if hasattr(self, "lbl_settings_about_page_title"):
            self.lbl_settings_about_page_title.setText(tr("settings.about_page_title"))
        if hasattr(self, "lbl_about_app_name"):
            self.lbl_about_app_name.setText(tr("dialog.about_app_name"))
        if hasattr(self, "lbl_about_desc"):
            self.lbl_about_desc.setText(tr("dialog.about_description"))
        if hasattr(self, "btn_check_updates_about"):
            self.btn_check_updates_about.setText(tr("settings.btn_check_updates"))
        if hasattr(self, "btn_update_download"):
            self.btn_update_download.setText(tr("settings.btn_download_update"))
        self._refresh_update_ui()
        if hasattr(self, "lbl_about_credits_title"):
            self.lbl_about_credits_title.setText("👍  " + tr("dialog.about_credits_title"))
        if hasattr(self, "lbl_about_credits_tech"):
            self.lbl_about_credits_tech.setText(tr("dialog.about_credits_tech"))
        if hasattr(self, "lbl_about_license"):
            self.lbl_about_license.setText(tr("dialog.about_license"))
        if hasattr(self, "lbl_about_support_title"):
            self.lbl_about_support_title.setText("💖  " + tr("dialog.about_support_title"))
        if hasattr(self, "btn_about_kofi"):
            self.btn_about_kofi.setText(tr("dialog.about_btn_kofi"))
        if hasattr(self, "btn_about_donate"):
            self.btn_about_donate.setText(tr("dialog.about_btn_kofi"))
        if hasattr(self, "btn_about_sponsors"):
            self.btn_about_sponsors.setText(tr("dialog.about_btn_sponsors"))
        if hasattr(self, "lbl_about_official_title"):
            self.lbl_about_official_title.setText("🌐  " + tr("dialog.about_official_pages_title"))
        if hasattr(self, "btn_about_github"):
            self.btn_about_github.setText(tr("dialog.about_btn_github"))
        if hasattr(self, "btn_about_itch"):
            self.btn_about_itch.setText(tr("dialog.about_btn_itch"))

        if hasattr(self, "btn_quick_about"):
            self.btn_quick_about.setToolTip(tr("dialog.about_title") + " (F1)")
        if hasattr(self, "menu_help") and self.menu_help is not None:
            self.menu_help.setTitle(tr("menu.help"))
        if hasattr(self, "action_about") and self.action_about is not None:
            self.action_about.setText(tr("menu.about"))
        if hasattr(self, "action_check_updates") and self.action_check_updates is not None:
            self.action_check_updates.setText(tr("menu.check_updates"))
        if hasattr(self, "update_banner"):
            self.update_banner.retranslate_ui()

        cfg_p = str(get_config_path())
        db_p = str(self.db.db_path)
        self.lbl_config_path_val.setText(f"• <b>{tr('settings.config_file')}</b> <code>{cfg_p}</code>")
        self.lbl_db_path_val.setText(f"• <b>{tr('settings.db_file')}</b> <code>{db_p}</code>")

        if hasattr(self, "lbl_settings_player_page_title"):
            self.lbl_settings_player_page_title.setText(tr("settings.page_player_title"))
            self.lbl_card_player_title.setText(tr("settings.player_playback_title"))
            self.lbl_card_player_desc.setText(tr("settings.player_playback_desc"))
            if hasattr(self, "radio_sleep_allow"):
                self.radio_sleep_allow.setText(tr("settings.sleep_mode_allow"))
                self.lbl_sleep_allow_hint.setText(tr("settings.sleep_mode_allow_hint"))
                self.radio_sleep_screens.setText(tr("settings.sleep_mode_player_playlist"))
                self.lbl_sleep_screens_hint.setText(tr("settings.sleep_mode_player_playlist_hint"))
                self.radio_sleep_always.setText(tr("settings.sleep_mode_always"))
                self.lbl_sleep_always_hint.setText(tr("settings.sleep_mode_always_hint"))

            if hasattr(self, "lbl_card_transitions_title"):
                self.lbl_card_transitions_title.setText(tr("settings.player_transitions_title"))
                self.lbl_card_transitions_desc.setText(tr("settings.player_transitions_desc"))
                self.radio_trans_standard.setText(tr("settings.transition_standard"))
                self.lbl_trans_standard_hint.setText(tr("settings.transition_standard_hint"))
                self.radio_trans_gapless.setText(tr("settings.transition_gapless"))
                self.lbl_trans_gapless_hint.setText(tr("settings.transition_gapless_hint"))
                self.radio_trans_crossfade.setText(tr("settings.transition_crossfade"))
                self.lbl_trans_crossfade_hint.setText(tr("settings.transition_crossfade_hint"))
                self.lbl_crossfade_duration.setText(tr("settings.crossfade_duration"))
                self.lbl_crossfade_value.setText(
                    tr("settings.crossfade_duration_val", seconds=str(self.slider_crossfade.value()))
                )

            if hasattr(self, "lbl_card_effects_title"):
                self.lbl_card_effects_title.setText(tr("settings.player_effects_title"))
                self.lbl_card_effects_desc.setText(tr("settings.player_effects_desc"))
                self.radio_eff_particles.setText(f"✨ {tr('effects.particles')}")
                self.lbl_eff_particles_hint.setText(tr("effects.particles_hint"))
                self.radio_eff_waves.setText(f"🌊 {tr('effects.waves')}")
                self.lbl_eff_waves_hint.setText(tr("effects.waves_hint"))
                self.radio_eff_stars.setText(f"☄️ {tr('effects.stars')}")
                self.lbl_eff_stars_hint.setText(tr("effects.stars_hint"))
                self.radio_eff_warp.setText(f"🚀 {tr('effects.warp')}")
                self.lbl_eff_warp_hint.setText(tr("effects.warp_hint"))
                self.radio_eff_warp_dynamic.setText(f"🛸 {tr('effects.warp_dynamic')}")
                self.lbl_eff_warp_dynamic_hint.setText(tr("effects.warp_dynamic_hint"))
                self.radio_eff_aurora.setText(f"🌌 {tr('effects.aurora')}")
                self.lbl_eff_aurora_hint.setText(tr("effects.aurora_hint"))
                self.radio_eff_bars.setText(f"📊 {tr('effects.bars')}")
                self.lbl_eff_bars_hint.setText(tr("effects.bars_hint"))
                self.radio_eff_bars_full.setText(f"📶 {tr('effects.bars_full')}")
                self.lbl_eff_bars_full_hint.setText(tr("effects.bars_full_hint"))
                self.radio_eff_none.setText(f"🚫 {tr('effects.none')}")
                self.lbl_eff_none_hint.setText(tr("effects.none_hint"))

            self.lbl_card_vlc_title.setText(tr("settings.player_engine_title"))
            self.lbl_card_vlc_desc.setText(tr("settings.player_engine_desc"))
            is_avail = self.player_service.is_vlc_available
            status_txt = tr("settings.player_engine_active") if is_avail else tr("settings.player_engine_inactive")
            status_color = "#34D399" if is_avail else "#EF4444"
            self.lbl_vlc_status_val.setText(
                f"• <b>{tr('settings.player_engine_status')}</b> <span style='color: {status_color}; font-weight: 600;'>{status_txt}</span>"
            )

            if hasattr(self, "lbl_card_bt_title"):
                self.lbl_card_bt_title.setText("🎭  " + tr("blind_test.settings_title"))
                self.lbl_card_bt_desc.setText(tr("settings.blind_test_desc"))
                self.lbl_bt_countdown.setText(tr("blind_test.countdown_label"))
                self.lbl_bt_reveal.setText(tr("blind_test.reveal_label"))
                self.lbl_bt_fade.setText(tr("blind_test.fade_label"))
                self._update_blind_test_summary_label()

        # Vues Lecteur, Blind Test et Playlist
        if hasattr(self, "page_player") and self.page_player:
            self.page_player.retranslate_ui()
        if hasattr(self, "page_blind_test") and self.page_blind_test:
            self.page_blind_test.retranslate_ui()
        if hasattr(self, "page_playlist") and self.page_playlist:
            self.page_playlist.retranslate_ui()

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
            fmts_lines = [f"• <b>{k.upper()}</b> : {v:,} morceaux" for k, v in stats["by_format"].items()]
            self.lbl_formats_breakdown.setText("<br>".join(fmts_lines))
        else:
            self.lbl_formats_breakdown.setText(f"<i>{tr('dialog.stats_none')}</i>")

        # Détail Sources
        if stats["by_source_type"]:
            srcs_lines = [f"• <b>{k.capitalize()}</b> : {v:,} morceaux" for k, v in stats["by_source_type"].items()]
            self.lbl_sources_breakdown.setText("<br>".join(srcs_lines))
        else:
            self.lbl_sources_breakdown.setText(f"<i>{tr('dialog.stats_none')}</i>")

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

    def _on_add_local_folder(self) -> None:
        """Permet à l'utilisateur de sélectionner un dossier audio local et de configurer sa synchronisation."""
        folder = QFileDialog.getExistingDirectory(
            self,
            tr("dialog.select_folder_title"),
            str(Path.home()),
        )
        if not folder:
            return

        folder_path = Path(folder).resolve()
        dlg = SourceConfigDialog(initial_path=str(folder_path), parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        data = dlg.get_data()
        source = self.db.add_source(
            source_type=SourceType.LOCAL,
            name=data["name"],
            path_or_uri=data["path_or_uri"],
            sync_mode=data["sync_mode"],
            sync_interval_minutes=data.get("sync_interval_minutes", 60),
            sync_interval_seconds=data.get("sync_interval_seconds", 60),
        )
        self.refresh_sources_list()
        self._refresh_folders_tree()
        self._refresh_settings_sources_table()
        if hasattr(self, "scheduler") and self.scheduler:
            self.scheduler.refresh_watched_directories()

        self.db.add_activity_log(
            action=f"Source ajoutée : {source.name}",
            level="INFO",
            category="LIBRARY",
            source_name=source.name,
            details=f"Emplacement: {source.path_or_uri}\nMode de synchronisation: {source.sync_mode}",
        )
        if hasattr(self, "page_logs") and self.page_logs:
            self.page_logs.mark_dirty()

        # Lancement immédiat de l'indexation de la nouvelle source en arrière-plan
        self._start_scan(source, user_initiated=True)

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
                self._start_scan(src, user_initiated=True)
                break

    def _on_scheduler_request_scan(self, source_or_id: SourceRecord | int) -> None:
        """Callback déclenché par le planificateur de synchronisation automatique."""
        source: SourceRecord | None
        if isinstance(source_or_id, SourceRecord):
            source = source_or_id
        else:
            source = self.db.get_source(source_or_id)
        if source:
            started = self._start_scan(source, user_initiated=False)
            if not started and hasattr(self, "scheduler") and self.scheduler and source.id:
                # Si le scan ne peut démarrer (ex. worker actif), libérer la file
                self.scheduler.notify_scan_finished(source.id)

    def _start_scan(self, source: SourceRecord, user_initiated: bool = False) -> bool:
        """Démarre le worker asynchrone de scan (Étape 1 inventaire rapide + Étape 2 analyse audio)."""
        if self.scan_worker and self.scan_worker.isRunning():
            if hasattr(self, "scheduler") and self.scheduler and source.id:
                self.scheduler.enqueue_source(source.id)
            return False

        self._current_scan_user_initiated = user_initiated
        self._current_scanning_source_id = source.id
        if hasattr(self, "scheduler") and self.scheduler and source.id:
            self.scheduler.notify_scan_started(source.id)

        self._status_is_alert = False
        self.status_label.setCursor(Qt.CursorShape.ArrowCursor)
        self.status_label.setToolTip("")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.btn_cancel_scan.setVisible(True)
        self.status_label.setText(tr("status.scanning", source=source.name))

        if hasattr(self, "btn_activity_feed") and self.btn_activity_feed:
            self.btn_activity_feed.setText(f"🔄 {source.name}")
            self.btn_activity_feed.setStyleSheet(
                """
                QPushButton {
                    background-color: rgba(2, 132, 199, 0.25);
                    color: #38BDF8;
                    border: 1px solid #0284C7;
                    border-radius: 6px;
                    padding: 2px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #0284C7;
                    color: #FFFFFF;
                }
                """
            )
        if hasattr(self, "activity_popover") and self.activity_popover:
            self.activity_popover.update_progress(tr("status.scanning", source=source.name), pct=0)

        self.scan_worker = ScanWorker(db=self.db, source=source, compute_hash=True, parent=self)
        self.scan_worker.progress.connect(self._on_scan_progress)
        self.scan_worker.status_message.connect(self.status_label.setText)
        self.scan_worker.phase1_finished.connect(self._on_phase1_scan_finished)
        self.scan_worker.scan_finished.connect(self._on_scan_finished)
        self.scan_worker.scan_error.connect(self._on_scan_error)
        self.scan_worker.start(QThread.Priority.LowPriority)
        return True

    def _cancel_current_scan(self) -> None:
        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.cancel()
            self.status_label.setText(tr("status.cancelling"))
            if hasattr(self, "activity_popover") and self.activity_popover:
                self.activity_popover.update_progress(tr("status.cancelling"), pct=None)

    def _on_scan_progress(self, current: int, total: int, current_file: str) -> None:
        now = time.perf_counter()
        # Throttling des rafraîchissements IHM (max 8 FPS) pour ne pas engorger la boucle Qt
        if hasattr(self, "_last_scan_progress_time"):
            if (now - self._last_scan_progress_time) < 0.12 and current < total:
                return
        self._last_scan_progress_time = now

        if total > 0:
            pct = int((current / total) * 100)
            self.progress_bar.setValue(pct)
            fn = Path(current_file).name
            status_txt = tr("status.indexing", current=current, total=total, file=fn)
            self.status_label.setText(status_txt)
            if hasattr(self, "activity_popover") and self.activity_popover:
                self.activity_popover.update_progress(status_txt, pct=pct)

    def _on_phase1_scan_finished(self, summary: ScanSummary) -> None:
        """Appelé dès que l'étape 1 (inventaire rapide des fichiers) est achevée."""
        has_structural_changes = summary.added > 0 or summary.deleted > 0
        has_any_changes = has_structural_changes or summary.updated > 0

        if has_any_changes:
            self._tracks_dirty = True
            self._folders_dirty = True
            self._stats_dirty = True
            self._sources_dirty = True

        total_indexed = summary.added + summary.updated + summary.unchanged
        self.status_label.setText(tr("status.phase1_done", count=total_indexed))
        if hasattr(self, "activity_popover") and self.activity_popover:
            self.activity_popover.update_progress(tr("status.phase1_done", count=total_indexed), pct=50)

        # Si l'utilisateur consulte activement la vue Morceaux (0) ou Dossiers (3), rafraîchir intelligemment
        curr_page = self.stacked_widget.currentIndex()
        if curr_page == 0:
            if has_any_changes:
                self.table_model.reload_data()
                self._update_track_count()
            self._tracks_dirty = False
        elif curr_page == 3:
            if has_structural_changes:
                self._refresh_folders_tree()
            if has_any_changes:
                self.folder_table_model.reload_data()
            self._folders_dirty = False

    def _on_scan_finished(self, summary: ScanSummary) -> None:
        self.progress_bar.setVisible(False)
        self.btn_cancel_scan.setVisible(False)

        has_structural_changes = summary.added > 0 or summary.deleted > 0
        has_any_changes = has_structural_changes or summary.updated > 0

        # Marquer les vues pour un rafraîchissement à la demande uniquement si des changements existent
        if has_any_changes:
            self._tracks_dirty = True
            self._folders_dirty = True
            self._stats_dirty = True
            self._sources_dirty = True

        # Rafraîchir UNIQUEMENT la vue actuellement visible s'il y a eu des modifications
        curr_page = self.stacked_widget.currentIndex()
        if curr_page == 0:
            if has_any_changes:
                self.table_model.reload_data()
                self._update_track_count()
            self._tracks_dirty = False
        elif curr_page == 3:
            # Ne rafraîchir l'arborescence des dossiers que si un dossier a été ajouté ou supprimé
            if has_structural_changes:
                self._refresh_folders_tree()
            if has_any_changes:
                self.folder_table_model.reload_data()
            self._folders_dirty = False
        elif curr_page == 4:
            if has_any_changes:
                self._refresh_settings_sources_table()
            self._sources_dirty = False

        if has_any_changes:
            self.refresh_sources_list()

        # Récupération du nom de la source scannée
        source_name = "Source"
        if self._current_scanning_source_id is not None:
            s_rec = self.db.get_source(self._current_scanning_source_id)
            if s_rec:
                source_name = s_rec.name

        if hasattr(self, "scheduler") and self.scheduler and self._current_scanning_source_id is not None:
            self.scheduler.notify_scan_finished(self._current_scanning_source_id)

        # Réinitialisation de l'affichage du badge d'état
        if hasattr(self, "btn_activity_feed") and self.btn_activity_feed:
            self.btn_activity_feed.setText("⚡ " + tr("status.activity_feed"))
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

        if summary.cancelled:
            self.status_label.setText(tr("status.cancelled"))
            self.db.add_activity_log(
                action=f"Synchronisation annulée : {source_name}",
                level="WARNING",
                category="SYNC",
                source_name=source_name,
                details="Le scan a été interrompu par l'utilisateur.",
            )
        elif summary.errors and summary.added == 0 and summary.updated == 0 and summary.unchanged == 0:
            err_msg = tr("status.scan_errors", count=len(summary.errors))
            self.status_label.setText(err_msg)
            self.db.add_activity_log(
                action=f"Échec de synchronisation : {source_name}",
                level="ERROR",
                category="SYNC",
                source_name=source_name,
                details="\n".join(summary.errors),
                items_errors=len(summary.errors),
            )
            if getattr(self, "_current_scan_user_initiated", False):
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
            lvl = "WARNING" if summary.errors else "SUCCESS"
            detail_lines = [
                f"Durée : {summary.elapsed_seconds:.1f}s",
                f"Morceaux ajoutés : {summary.added}",
                f"Morceaux mis à jour : {summary.updated}",
                f"Morceaux inchangés : {summary.unchanged}",
                f"Morceaux supprimés : {summary.deleted}",
            ]
            if summary.errors:
                detail_lines.append(f"Erreurs ({len(summary.errors)}) :")
                detail_lines.extend(summary.errors[:10])

            self.db.add_activity_log(
                action=f"Synchronisation réussie : {source_name}",
                level=lvl,
                category="SYNC",
                source_name=source_name,
                details="\n".join(detail_lines),
                items_added=summary.added,
                items_updated=summary.updated,
                items_deleted=summary.deleted,
                items_errors=len(summary.errors),
            )

        if hasattr(self, "activity_popover") and self.activity_popover:
            self.activity_popover.update_progress("", pct=None)

        if hasattr(self, "page_logs") and self.page_logs:
            self.page_logs.mark_dirty()

    def _on_scan_error(self, err_msg: str) -> None:
        self.progress_bar.setVisible(False)
        self.btn_cancel_scan.setVisible(False)
        self._status_is_alert = True
        self.status_label.setText(tr("status.scan_error", error=err_msg))
        self.status_label.setToolTip(f"{err_msg}\n({tr('status.click_to_view_logs')})")
        self.status_label.setCursor(Qt.CursorShape.PointingHandCursor)

        source_name = "Source"
        if self._current_scanning_source_id is not None:
            s_rec = self.db.get_source(self._current_scanning_source_id)
            if s_rec:
                source_name = s_rec.name

        if hasattr(self, "scheduler") and self.scheduler and self._current_scanning_source_id is not None:
            self.scheduler.notify_scan_finished(self._current_scanning_source_id)

        if hasattr(self, "btn_activity_feed") and self.btn_activity_feed:
            self.btn_activity_feed.setText("⚡ " + tr("status.activity_feed"))
        if hasattr(self, "activity_popover") and self.activity_popover:
            self.activity_popover.update_progress("", pct=None)

        self.db.add_activity_log(
            action=f"Erreur critique de scan : {source_name}",
            level="ERROR",
            category="SYNC",
            source_name=source_name,
            details=err_msg,
            items_errors=1,
        )

        if hasattr(self, "page_logs") and self.page_logs:
            self.page_logs.mark_dirty()

        if getattr(self, "_current_scan_user_initiated", False):
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
