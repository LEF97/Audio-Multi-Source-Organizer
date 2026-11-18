"""Mixin et widget de construction de l'en-tête lecteur et de la vue Playlist."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from amso.core.config import get_config_manager
from amso.core.database import TrackRecord
from amso.core.i18n import tr
from amso.core.playlist_exporter import export_playlist, index_exported_playlist_in_db
from amso.services.player_service import PlayerService
from amso.ui.models import format_duration
from amso.ui.styles import (
    COLOR_BG_CARD,
    COLOR_BG_DARK,
    COLOR_BG_HOVER,
    COLOR_BG_SLATE,
    COLOR_BORDER,
    COLOR_BORDER_LIGHT,
    COLOR_DANGER,
    COLOR_DANGER_SOFT,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_TEXT,
    COLOR_TEXT_BRIGHT,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_SOFT,
    COLOR_WHITE,
)
from amso.ui.table_settings import apply_default_columns
from amso.ui.views.cover_helper import (
    get_default_cover_pixmap,
    get_track_cover_hash,
    has_cached_cover,
    load_cover_async,
)
from amso.ui.widgets.common import ClickableSlider
from amso.ui.widgets.cover_transition_label import CoverTransitionLabel
from amso.ui.widgets.help_guide_popup import HelpButton
from amso.ui.widgets.play_pause_button import PlayPauseButton
from amso.ui.widgets.playlist_table_view import PlaylistTableView
from amso.ui.widgets.transport_mixin import TransportViewMixin

if TYPE_CHECKING:
    _MixinBase = TransportViewMixin
else:
    _MixinBase = object

_SHUFFLE_TRACKS_BTN_QSS = f"""
    QPushButton {{
        background-color: {COLOR_BG_CARD};
        color: {COLOR_PRIMARY_HOVER};
        border: 1px solid {COLOR_BORDER_LIGHT};
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: 500;
        margin-right: 8px;
    }}
    QPushButton:hover {{
        background-color: {COLOR_BG_SLATE};
        border-color: {COLOR_PRIMARY_HOVER};
        color: #7DD3FC;
    }}
    QPushButton:disabled {{
        background-color: #161920;
        border-color: #262B37;
        color: #4B5563;
    }}
"""

_CLEAR_PLAYLIST_BTN_QSS = f"""
    QPushButton {{
        background-color: {COLOR_BG_CARD};
        color: {COLOR_DANGER};
        border: 1px solid {COLOR_BORDER_LIGHT};
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: #2E1A1A;
        border-color: {COLOR_DANGER};
        color: {COLOR_DANGER_SOFT};
    }}
"""

_VOLUME_SLIDER_QSS = f"""
    QSlider::groove:horizontal {{
        height: 4px;
        background-color: {COLOR_BORDER};
        border-radius: 2px;
    }}
    QSlider::sub-page:horizontal {{
        background-color: {COLOR_PRIMARY_HOVER};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background-color: {COLOR_TEXT_SOFT};
        width: 10px;
        height: 10px;
        margin: -3px 0;
        border-radius: 5px;
    }}
"""

_SEEK_SLIDER_QSS = f"""
    QSlider::groove:horizontal {{
        height: 5px;
        background-color: {COLOR_BORDER};
        border-radius: 2px;
    }}
    QSlider::sub-page:horizontal {{
        background-color: {COLOR_PRIMARY};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background-color: {COLOR_TEXT_BRIGHT};
        width: 12px;
        height: 12px;
        margin: -3px 0;
        border-radius: 6px;
    }}
"""


class PlaylistHeaderMixin(_MixinBase):
    """Construction et logique partagées du bloc Liste de lecture + mini-lecteur."""

    _header_title_key: str = "playlist.page_title"

    if TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any: ...

    def _setup_playlist_header_ui(self, main_layout: QVBoxLayout) -> None:
        """Ajoute la barre d'en-tête Liste de lecture et la bannière du mini-lecteur au layout."""
        main_layout.addWidget(self._build_playlist_top_bar())
        main_layout.addWidget(self._build_player_banner())

    def _build_playlist_top_bar(self) -> QFrame:
        top_bar = QFrame()
        top_bar.setObjectName("topBarFrame")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 12, 20, 12)

        self.lbl_page_title = QLabel(tr(self._header_title_key))
        self.lbl_page_title.setStyleSheet(f"color: {COLOR_TEXT_BRIGHT}; font-size: 16px; font-weight: 700;")
        top_layout.addWidget(self.lbl_page_title)

        top_layout.addStretch()

        self.lbl_playlist_stats = QLabel("")
        self.lbl_playlist_stats.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 13px; font-weight: 500; margin-right: 12px;"
        )
        top_layout.addWidget(self.lbl_playlist_stats)

        self.btn_save_playlist = QPushButton(tr("playlist.btn_save"))
        self.btn_save_playlist.setProperty("class", "secondary-btn")
        self.btn_save_playlist.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save_playlist.setStyleSheet(_SHUFFLE_TRACKS_BTN_QSS)
        top_layout.addWidget(self.btn_save_playlist)

        self.btn_shuffle_tracks = QPushButton(tr("playlist.btn_shuffle_tracks"))
        self.btn_shuffle_tracks.setProperty("class", "secondary-btn")
        self.btn_shuffle_tracks.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_shuffle_tracks.setStyleSheet(_SHUFFLE_TRACKS_BTN_QSS)
        top_layout.addWidget(self.btn_shuffle_tracks)
        self.btn_shuffle_below = self.btn_shuffle_tracks

        self.btn_clear_playlist = QPushButton(tr("player.btn_clear_playlist"))
        self.btn_clear_playlist.setProperty("class", "secondary-btn")
        self.btn_clear_playlist.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_playlist.setStyleSheet(_CLEAR_PLAYLIST_BTN_QSS)
        top_layout.addWidget(self.btn_clear_playlist)

        self.btn_help = HelpButton("playlist.help_title", "playlist.help_body", parent=top_bar)
        top_layout.addWidget(self.btn_help)
        return top_bar

    def _build_player_banner(self) -> QFrame:
        player_banner = QFrame()
        player_banner.setObjectName("playerBanner")
        player_banner.setStyleSheet(f"""
            QFrame#playerBanner {{
                background-color: {COLOR_BG_DARK};
                border-bottom: 1px solid {COLOR_BORDER};
                padding: 10px 16px;
            }}
        """)
        banner_layout = QVBoxLayout(player_banner)
        banner_layout.setContentsMargins(16, 10, 16, 10)
        banner_layout.setSpacing(8)
        banner_layout.addLayout(self._build_banner_top_row())
        banner_layout.addLayout(self._build_banner_seek_row())
        return player_banner

    def _build_banner_top_row(self) -> QHBoxLayout:
        top_row = QHBoxLayout()
        top_row.setSpacing(14)

        self.lbl_thumb = CoverTransitionLabel()
        self.lbl_thumb.setFixedSize(56, 56)
        self.lbl_thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_thumb.setStyleSheet("border-radius: 8px;")
        top_row.addWidget(self.lbl_thumb)

        track_info_layout = QVBoxLayout()
        track_info_layout.setSpacing(2)
        track_info_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.lbl_track_title = QLabel(tr("player.no_track"))
        self.lbl_track_title.setStyleSheet(f"color: {COLOR_TEXT_BRIGHT}; font-size: 14px; font-weight: 700;")
        track_info_layout.addWidget(self.lbl_track_title)

        self.lbl_track_artist = QLabel("")
        self.lbl_track_artist.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px;")
        track_info_layout.addWidget(self.lbl_track_artist)

        top_row.addLayout(track_info_layout, 1)
        top_row.addLayout(self._build_transport_buttons())
        top_row.addLayout(self._build_volume_controls())
        return top_row

    def _build_transport_buttons(self) -> QHBoxLayout:
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(8)

        self.btn_shuffle = QPushButton("🔀")
        self.btn_shuffle.setFixedSize(32, 32)
        self.btn_shuffle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_shuffle.setToolTip(tr("player.btn_shuffle"))
        self._style_mini_button(self.btn_shuffle)
        ctrl_layout.addWidget(self.btn_shuffle)

        self.btn_prev = QPushButton("⏮")
        self.btn_prev.setFixedSize(34, 34)
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.setToolTip(tr("player.btn_previous"))
        self._style_mini_button(self.btn_prev, font_size=20)
        ctrl_layout.addWidget(self.btn_prev)

        self.btn_play_pause = PlayPauseButton(diameter=40)
        self.btn_play_pause.setToolTip(tr("player.btn_play"))
        ctrl_layout.addWidget(self.btn_play_pause)

        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setFixedSize(32, 32)
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.setToolTip(tr("player.btn_stop"))
        self._style_mini_button(self.btn_stop, font_size=19)
        ctrl_layout.addWidget(self.btn_stop)

        self.btn_next = QPushButton("⏭")
        self.btn_next.setFixedSize(34, 34)
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.setToolTip(tr("player.btn_next"))
        self._style_mini_button(self.btn_next, font_size=20)
        ctrl_layout.addWidget(self.btn_next)

        self.btn_repeat = QPushButton("🔁")
        self.btn_repeat.setFixedSize(32, 32)
        self.btn_repeat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_repeat.setToolTip(tr("player.btn_repeat"))
        self._style_mini_button(self.btn_repeat, font_size=19)
        ctrl_layout.addWidget(self.btn_repeat)
        return ctrl_layout

    def _build_volume_controls(self) -> QHBoxLayout:
        vol_layout = QHBoxLayout()
        vol_layout.setSpacing(6)
        vol_layout.setContentsMargins(16, 0, 0, 0)

        self.btn_mute = QPushButton("🔊")
        self.btn_mute.setFixedSize(28, 28)
        self.btn_mute.setCursor(Qt.CursorShape.PointingHandCursor)
        self._style_mini_button(self.btn_mute, font_size=17)
        vol_layout.addWidget(self.btn_mute)

        self.slider_volume = ClickableSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(self.player.volume)
        self.slider_volume.setFixedWidth(90)
        self.slider_volume.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider_volume.setStyleSheet(_VOLUME_SLIDER_QSS)
        vol_layout.addWidget(self.slider_volume)
        return vol_layout

    def _build_banner_seek_row(self) -> QHBoxLayout:
        seek_row = QHBoxLayout()
        seek_row.setSpacing(8)
        seek_row.setContentsMargins(4, 0, 4, 0)

        self.lbl_time_cur = QLabel("00:00")
        self.lbl_time_cur.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; font-family: monospace;")
        seek_row.addWidget(self.lbl_time_cur)

        self.slider_seek = ClickableSlider(Qt.Orientation.Horizontal)
        self.slider_seek.setRange(0, 1000)
        self.slider_seek.setValue(0)
        self.slider_seek.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider_seek.setStyleSheet(_SEEK_SLIDER_QSS)
        seek_row.addWidget(self.slider_seek, 1)

        self.lbl_time_total = QLabel("00:00")
        self.lbl_time_total.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; font-family: monospace;")
        seek_row.addWidget(self.lbl_time_total)
        return seek_row

    def _style_mini_button(self, btn: QPushButton, font_size: int = 19) -> None:
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BG_CARD};
                color: {COLOR_TEXT};
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                font-size: {font_size}px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BG_HOVER};
                color: {COLOR_TEXT_BRIGHT};
                border-color: {COLOR_PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_PRIMARY};
                color: {COLOR_WHITE};
            }}
        """)

    def _connect_playlist_header_signals(self) -> None:
        """Connecte les signaux du PlayerService et des boutons d'en-tête."""
        self._connect_transport_signals()
        self.player.playlist_updated.connect(self._on_playlist_updated)
        self.btn_save_playlist.clicked.connect(self._on_save_playlist_clicked)
        self.btn_shuffle_tracks.clicked.connect(self._on_shuffle_tracks_clicked)
        self.btn_clear_playlist.clicked.connect(self.player.clear_playlist)

        self.update_shuffle_ui(self.player.is_shuffle)
        self.update_repeat_ui(self.player.repeat_mode)
        self.update_volume(self.player.volume, self.player.is_muted)
        self._update_stats_label()
        if self.player.current_track:
            self.update_track_info(self.player.current_track)

    def _on_save_playlist_clicked(self) -> None:
        """Ouvre le dialogue d'enregistrement et exporte la playlist active."""
        tracks = list(self.player.playlist)
        if not tracks:
            return
        filters = ";;".join(
            [
                "M3U8 UTF-8 (*.m3u8)",
                "M3U (*.m3u)",
                "PLS (*.pls)",
                "XSPF (*.xspf)",
                "WPL (*.wpl)",
            ]
        )
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            tr("playlist.save_dialog_title"),
            "playlist.m3u8",
            filters,
        )
        if not file_path:
            return
        try:
            dest = export_playlist(tracks, Path(file_path), relative_paths=True)
        except Exception as exc:
            QMessageBox.warning(
                self,
                tr("playlist.save_dialog_title"),
                tr("playlist.save_error", error=str(exc)),
            )
            return

        win = self.window()
        if hasattr(win, "db") and index_exported_playlist_in_db(win.db, dest):
            if hasattr(win, "_refresh_folders_tree"):
                win._refresh_folders_tree()
        if hasattr(win, "status_label"):
            win.status_label.setText(tr("playlist.save_success", name=dest.name))

    def _on_shuffle_tracks_clicked(self) -> None:
        """Déclenche le mélange complet des titres de la playlist."""
        if not self.player.is_shuffle:
            return
        self.player.shuffle_all_tracks()

    def _on_shuffle_below_clicked(self) -> None:
        """Alias de rétrocompatibilité."""
        self._on_shuffle_tracks_clicked()

    def _update_shuffle_tracks_state(self) -> None:
        """Active ou désactive le bouton et actions de mélange selon le mode aléatoire."""
        can_shuffle = bool(self.player.is_shuffle) and len(self.player.playlist) > 1
        if hasattr(self, "btn_shuffle_tracks"):
            self.btn_shuffle_tracks.setEnabled(can_shuffle)

    def _update_stats_label(self) -> None:
        self._update_shuffle_tracks_state()
        tracks = self.player.playlist
        count = len(tracks)
        if hasattr(self, "btn_save_playlist"):
            self.btn_save_playlist.setEnabled(count > 0)
        if count == 0:
            self.lbl_playlist_stats.setText(tr("player.empty_playlist"))
            return

        total_sec = sum(t.duration_seconds or 0 for t in tracks)
        dur_str = format_duration(total_sec)
        key = "playlist.stats_count_singular" if count == 1 else "playlist.stats_count"
        self.lbl_playlist_stats.setText(tr(key, count=f"{count:,}", duration=dur_str))

    def _on_playlist_updated(self) -> None:
        """Appelé lorsque la composition de la playlist change."""
        self._update_stats_label()

    def _apply_thumb_pixmap(self, pixmap: QPixmap, cover_hash: int | None) -> None:
        if isinstance(self.lbl_thumb, CoverTransitionLabel):
            transition = get_config_manager().get_cover_transition()
            self.lbl_thumb.set_cover_pixmap(pixmap, cover_hash=cover_hash, transition=transition, animate=True)
        else:
            self.lbl_thumb.setPixmap(pixmap)

    def _on_cover_loaded(self, path: str, pixmap: QPixmap) -> None:
        """Appelé dès que la vignette asynchrone a fini de charger."""
        if getattr(self, "_displayed_track_path", None) == path:
            cover_hash = get_track_cover_hash(self.player.current_track)
            self._apply_thumb_pixmap(pixmap, cover_hash)

    def update_track_info(self, track: TrackRecord | None) -> None:
        """Met à jour l'affichage avec la piste en cours de lecture de façon instantanée."""
        try:
            track_path = track.source_path if track else ""
            self._displayed_track_path = track_path

            if not track:
                self._apply_thumb_pixmap(get_default_cover_pixmap(56, 8), 0)
            elif has_cached_cover(track, size=56):
                pixmap = load_cover_async(track, size=56, radius=8, callback=self._on_cover_loaded, force_check=True)
                self._apply_thumb_pixmap(pixmap, get_track_cover_hash(track))
            else:
                pixmap = load_cover_async(track, size=56, radius=8, callback=self._on_cover_loaded, force_check=True)
                if self.lbl_thumb.pixmap().isNull():
                    self._apply_thumb_pixmap(pixmap, None)

            if not track:
                self.lbl_track_title.setText(tr("player.no_track"))
                self.lbl_track_artist.setText("")
                self.lbl_time_cur.setText("00:00")
                self.lbl_time_total.setText("00:00")
                self.slider_seek.setValue(0)
                return

            title_text = track.title or track.file_name or tr("track.untitled")
            self.lbl_track_title.setText(title_text)

            artist_part = track.artist or tr("track.unknown_artist")
            album_part = f" — {track.album}" if track.album else ""
            self.lbl_track_artist.setText(f"{artist_part}{album_part}")

            total_sec = track.duration_seconds or 0
            self.lbl_time_total.setText(format_duration(total_sec))
        except RuntimeError:
            pass

    def update_shuffle_ui(self, active: bool) -> None:
        """Met en valeur le bouton aléatoire puis met à jour l'état du bouton de mélange."""
        super().update_shuffle_ui(active)
        self._update_shuffle_tracks_state()

    def retranslate_header_ui(self) -> None:
        """Met à jour les libellés et infobulles du bloc en-tête + mini-lecteur."""
        self.lbl_page_title.setText(tr(self._header_title_key))
        if hasattr(self, "btn_save_playlist"):
            self.btn_save_playlist.setText(tr("playlist.btn_save"))
        if hasattr(self, "btn_shuffle_tracks"):
            self.btn_shuffle_tracks.setText(tr("playlist.btn_shuffle_tracks"))
        elif hasattr(self, "btn_shuffle_below"):
            self.btn_shuffle_below.setText(tr("playlist.btn_shuffle_tracks"))
        self.btn_clear_playlist.setText(tr("player.btn_clear_playlist"))
        self._update_stats_label()

        if not self.player.current_track:
            self.lbl_track_title.setText(tr("player.no_track"))
        else:
            self.update_track_info(self.player.current_track)

        self.btn_shuffle.setToolTip(tr("player.btn_shuffle"))
        self.btn_prev.setToolTip(tr("player.btn_previous"))
        if self.player.is_playing:
            self.btn_play_pause.setToolTip(tr("player.btn_pause"))
        else:
            self.btn_play_pause.setToolTip(tr("player.btn_play"))
        self.btn_stop.setToolTip(tr("player.btn_stop"))
        self.btn_next.setToolTip(tr("player.btn_next"))
        self.btn_repeat.setToolTip(tr("player.btn_repeat"))


class PlaylistHeaderWidget(PlaylistHeaderMixin, TransportViewMixin, QWidget):
    """Widget autonome regroupant l'en-tête Liste de lecture et le mini-lecteur."""

    _transport_btn_radius = 4
    _transport_btn_font = 19
    _transport_cover_size = 56
    _transport_cover_radius = 8

    def __init__(
        self,
        player_service: PlayerService,
        parent: QWidget | None = None,
        *,
        title_key: str = "playlist.page_title",
    ) -> None:
        super().__init__(parent)
        self.player = player_service
        self._header_title_key = title_key
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self._setup_playlist_header_ui(main_layout)
        self._connect_playlist_header_signals()
        self.update_track_info(self.player.current_track)
        self.update_playback_state("playing" if self.player.is_playing else "stopped")
        self._update_stats_label()

    def retranslate_ui(self) -> None:
        """Retraduit les textes du widget."""
        self.retranslate_header_ui()


class PlaylistUiMixin(PlaylistHeaderMixin):
    """Construction de l'en-tête, du mini-lecteur et de la table de playlist."""

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._setup_playlist_header_ui(main_layout)

        # 3. Tableau de la playlist
        self.table_view = PlaylistTableView()
        self.table_view.setModel(self.playlist_model)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setShowGrid(False)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.setCursor(Qt.CursorShape.PointingHandCursor)

        # Tailles et configuration des colonnes
        header = self.table_view.horizontalHeader()
        header.setSectionsMovable(True)
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(28)
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self._on_header_context_menu)

        for idx in range(len(self.playlist_model.COLUMNS)):
            header.setSectionResizeMode(idx, QHeaderView.ResizeMode.Interactive)

        if not self.restore_table_state():
            apply_default_columns(self.table_view, self.playlist_model)

        header.sectionResized.connect(lambda *_: self.save_table_state())
        header.sectionMoved.connect(lambda *_: self.save_table_state())

        main_layout.addWidget(self.table_view, 1)
