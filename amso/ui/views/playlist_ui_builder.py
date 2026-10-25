"""Mixin de construction de l'interface utilisateur pour la vue Playlist."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from amso.core.i18n import tr
from amso.ui.widgets.common import ClickableSlider
from amso.ui.widgets.playlist_table_view import PlaylistTableView

if TYPE_CHECKING:
    _MixinBase = QWidget
else:
    _MixinBase = object


class PlaylistUiMixin(_MixinBase):
    """Construction de l'en-tête, du mini-lecteur et de la table de playlist."""

    if TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any: ...

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. En-tête de page
        top_bar = QFrame()
        top_bar.setObjectName("topBarFrame")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 12, 20, 12)

        self.lbl_page_title = QLabel(tr("playlist.page_title"))
        self.lbl_page_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        top_layout.addWidget(self.lbl_page_title)

        top_layout.addStretch()

        self.lbl_playlist_stats = QLabel("")
        self.lbl_playlist_stats.setStyleSheet("color: #94A3B8; font-size: 13px; font-weight: 500; margin-right: 12px;")
        top_layout.addWidget(self.lbl_playlist_stats)

        self.btn_shuffle_tracks = QPushButton(tr("playlist.btn_shuffle_tracks"))
        self.btn_shuffle_tracks.setProperty("class", "secondary-btn")
        self.btn_shuffle_tracks.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_shuffle_tracks.setStyleSheet("""
            QPushButton {
                background-color: #20242D;
                color: #38BDF8;
                border: 1px solid #333846;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
                margin-right: 8px;
            }
            QPushButton:hover {
                background-color: #1E293B;
                border-color: #38BDF8;
                color: #7DD3FC;
            }
            QPushButton:disabled {
                background-color: #161920;
                border-color: #262B37;
                color: #4B5563;
            }
        """)
        top_layout.addWidget(self.btn_shuffle_tracks)
        self.btn_shuffle_below = self.btn_shuffle_tracks

        self.btn_clear_playlist = QPushButton(tr("player.btn_clear_playlist"))
        self.btn_clear_playlist.setProperty("class", "secondary-btn")
        self.btn_clear_playlist.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_playlist.setStyleSheet("""
            QPushButton {
                background-color: #20242D;
                color: #EF4444;
                border: 1px solid #333846;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2E1A1A;
                border-color: #EF4444;
                color: #FCA5A5;
            }
        """)
        top_layout.addWidget(self.btn_clear_playlist)

        main_layout.addWidget(top_bar)

        # 2. Bannière Lecteur Compacte en haut
        player_banner = QFrame()
        player_banner.setObjectName("playerBanner")
        player_banner.setStyleSheet("""
            QFrame#playerBanner {
                background-color: #1A1D24;
                border-bottom: 1px solid #282C37;
                padding: 10px 16px;
            }
        """)
        banner_layout = QVBoxLayout(player_banner)
        banner_layout.setContentsMargins(16, 10, 16, 10)
        banner_layout.setSpacing(8)

        # Ligne supérieure : Miniature + Titre + Boutons + Volume
        top_row = QHBoxLayout()
        top_row.setSpacing(14)

        # Miniature de pochette
        self.lbl_thumb = QLabel()
        self.lbl_thumb.setFixedSize(56, 56)
        self.lbl_thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_thumb.setStyleSheet("border-radius: 8px;")
        top_row.addWidget(self.lbl_thumb)

        # Titre et Artiste
        track_info_layout = QVBoxLayout()
        track_info_layout.setSpacing(2)
        track_info_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.lbl_track_title = QLabel(tr("player.no_track"))
        self.lbl_track_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        track_info_layout.addWidget(self.lbl_track_title)

        self.lbl_track_artist = QLabel("")
        self.lbl_track_artist.setStyleSheet("color: #94A3B8; font-size: 12px;")
        track_info_layout.addWidget(self.lbl_track_artist)

        top_row.addLayout(track_info_layout, 1)

        # Contrôles de lecture
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
        self._style_mini_button(self.btn_prev, font_size=13)
        ctrl_layout.addWidget(self.btn_prev)

        self.btn_play_pause = QPushButton("▶")
        self.btn_play_pause.setFixedSize(40, 40)
        self.btn_play_pause.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_play_pause.setToolTip(tr("player.btn_play"))
        self.btn_play_pause.setStyleSheet("""
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                border-radius: 20px;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0369A1;
            }
        """)
        ctrl_layout.addWidget(self.btn_play_pause)

        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setFixedSize(32, 32)
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.setToolTip(tr("player.btn_stop"))
        self._style_mini_button(self.btn_stop, font_size=11)
        ctrl_layout.addWidget(self.btn_stop)

        self.btn_next = QPushButton("⏭")
        self.btn_next.setFixedSize(34, 34)
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.setToolTip(tr("player.btn_next"))
        self._style_mini_button(self.btn_next, font_size=13)
        ctrl_layout.addWidget(self.btn_next)

        self.btn_repeat = QPushButton("🔁")
        self.btn_repeat.setFixedSize(32, 32)
        self.btn_repeat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_repeat.setToolTip(tr("player.btn_repeat"))
        self._style_mini_button(self.btn_repeat)
        ctrl_layout.addWidget(self.btn_repeat)

        top_row.addLayout(ctrl_layout)

        # Contrôle du volume compact
        vol_layout = QHBoxLayout()
        vol_layout.setSpacing(6)
        vol_layout.setContentsMargins(16, 0, 0, 0)

        self.btn_mute = QPushButton("🔊")
        self.btn_mute.setFixedSize(28, 28)
        self.btn_mute.setCursor(Qt.CursorShape.PointingHandCursor)
        self._style_mini_button(self.btn_mute, font_size=11)
        vol_layout.addWidget(self.btn_mute)

        self.slider_volume = ClickableSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(self.player.volume)
        self.slider_volume.setFixedWidth(90)
        self.slider_volume.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider_volume.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background-color: #282C37;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background-color: #38BDF8;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background-color: #E2E8F0;
                width: 10px;
                height: 10px;
                margin: -3px 0;
                border-radius: 5px;
            }
        """)
        vol_layout.addWidget(self.slider_volume)

        top_row.addLayout(vol_layout)
        banner_layout.addLayout(top_row)

        # Ligne inférieure : Seekbar
        seek_row = QHBoxLayout()
        seek_row.setSpacing(8)
        seek_row.setContentsMargins(4, 0, 4, 0)

        self.lbl_time_cur = QLabel("00:00")
        self.lbl_time_cur.setStyleSheet("color: #94A3B8; font-size: 11px; font-family: monospace;")
        seek_row.addWidget(self.lbl_time_cur)

        self.slider_seek = ClickableSlider(Qt.Orientation.Horizontal)
        self.slider_seek.setRange(0, 1000)
        self.slider_seek.setValue(0)
        self.slider_seek.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider_seek.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 5px;
                background-color: #282C37;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background-color: #0284C7;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background-color: #F8FAFC;
                width: 12px;
                height: 12px;
                margin: -3px 0;
                border-radius: 6px;
            }
        """)
        seek_row.addWidget(self.slider_seek, 1)

        self.lbl_time_total = QLabel("00:00")
        self.lbl_time_total.setStyleSheet("color: #94A3B8; font-size: 11px; font-family: monospace;")
        seek_row.addWidget(self.lbl_time_total)

        banner_layout.addLayout(seek_row)
        main_layout.addWidget(player_banner)

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
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self._on_header_context_menu)

        for idx in range(len(self.playlist_model.COLUMNS)):
            header.setSectionResizeMode(idx, QHeaderView.ResizeMode.Interactive)

        if not self.restore_table_state():
            for idx, col_def in enumerate(self.playlist_model.COLUMNS):
                header.resizeSection(idx, col_def[1])

        header.sectionResized.connect(lambda *_: self.save_table_state())
        header.sectionMoved.connect(lambda *_: self.save_table_state())

        main_layout.addWidget(self.table_view, 1)

    def _style_mini_button(self, btn: QPushButton, font_size: int = 12) -> None:
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #20242D;
                color: #CBD5E1;
                border: 1px solid #282C37;
                border-radius: 4px;
                font-size: {font_size}px;
            }}
            QPushButton:hover {{
                background-color: #2B303C;
                color: #F8FAFC;
                border-color: #38BDF8;
            }}
            QPushButton:pressed {{
                background-color: #0284C7;
                color: #FFFFFF;
            }}
        """)
