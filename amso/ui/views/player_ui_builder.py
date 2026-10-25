"""Mixin de construction de l'interface graphique du Lecteur Audio grand format."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from amso.core.i18n import tr
from amso.ui.styles import (
    seek_slider_qss,
    volume_label_qss,
    volume_slider_qss,
)
from amso.ui.widgets.common import ClickableSlider
from amso.ui.widgets.effects_view_mixin import EffectsViewMixin

if TYPE_CHECKING:
    _MixinBase = QWidget
else:
    _MixinBase = object


class PlayerUiMixin(EffectsViewMixin, _MixinBase):
    """Construction de l'en-tête, carte centrale, contrôles et conteneurs du lecteur."""

    if TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any: ...

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # En-tête de la page
        top_bar = QFrame()
        top_bar.setObjectName("topBarFrame")
        self.top_bar = top_bar
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 10, 20, 10)
        top_layout.setSpacing(8)

        self.lbl_page_title = QLabel(tr("player.title"))
        self.lbl_page_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        top_layout.addWidget(self.lbl_page_title)

        top_layout.addSpacing(16)

        # Contrôle du volume sonore intégré dans la barre supérieure
        self.btn_mute = QPushButton("🔊")
        self.btn_mute.setFixedSize(30, 30)
        self.btn_mute.setCursor(Qt.CursorShape.PointingHandCursor)
        self._style_transport_button(self.btn_mute, font_size=13)
        top_layout.addWidget(self.btn_mute)

        self.slider_volume = ClickableSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(self.player.volume)
        self.slider_volume.setFixedWidth(120)
        self.slider_volume.setFixedHeight(22)
        self.slider_volume.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider_volume.setStyleSheet(volume_slider_qss(groove_height=5, handle_size=12))
        top_layout.addWidget(self.slider_volume)

        self.lbl_volume = QLabel(f"{self.player.volume}%")
        self.lbl_volume.setStyleSheet(volume_label_qss(min_width=38))
        top_layout.addWidget(self.lbl_volume)

        top_layout.addStretch()

        self.lbl_effect_badge, self.combo_effect = self._create_effects_combo()
        top_layout.addWidget(self.lbl_effect_badge)
        top_layout.addWidget(self.combo_effect)
        layout.addWidget(top_bar)

        # Toile d'effet visuel dynamique en fond
        self.effect_canvas, center_container = self._create_effect_container()
        self.effect_widget = self.effect_canvas
        self.center_container = center_container

        # Zone défilante centrale pour garantir la lisibilité sur toutes résolutions
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area = scroll

        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(16, 6, 16, 6)
        center_layout.setSpacing(8)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout = center_layout

        # Carte centrale contenant le lecteur
        self.card = QFrame()
        self.card.setObjectName("playerCard")
        self.card.setMinimumWidth(500)
        self.card.setMaximumWidth(580)
        self.card.setStyleSheet("""
            QFrame#playerCard {
                background-color: rgba(26, 29, 36, 0.92);
                border: 1px solid rgba(56, 189, 248, 0.25);
                border-radius: 16px;
            }
        """)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(20, 10, 20, 10)
        card_layout.setSpacing(8)
        self.card_layout = card_layout

        # 1. Grande Jaquette (taille adaptative calculée dynamiquement)
        self.lbl_cover = QLabel()
        self.lbl_cover.setFixedSize(280, 280)
        self.lbl_cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_cover.setStyleSheet("border-radius: 12px;")
        card_layout.addWidget(self.lbl_cover, 0, Qt.AlignmentFlag.AlignCenter)

        # 2. Informations du morceau (prennent toute la largeur de la carte, texte centré)
        info_container = QWidget()
        self.info_container = info_container
        info_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        self.lbl_title = QLabel(tr("player.no_track"))
        self.lbl_title.setStyleSheet("color: #F8FAFC; font-size: 19px; font-weight: 700;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.lbl_title.setWordWrap(True)
        info_layout.addWidget(self.lbl_title)

        self.lbl_artist_album = QLabel("")
        self.lbl_artist_album.setStyleSheet("color: #94A3B8; font-size: 14px;")
        self.lbl_artist_album.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_artist_album.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.lbl_artist_album.setWordWrap(True)
        info_layout.addWidget(self.lbl_artist_album)

        self.lbl_file_name = QLabel("")
        self.lbl_file_name.setStyleSheet("color: #64748B; font-size: 12px; margin-top: 1px;")
        self.lbl_file_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_file_name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.lbl_file_name.setWordWrap(True)
        self.lbl_file_name.setVisible(False)
        info_layout.addWidget(self.lbl_file_name)

        self.lbl_badge = QLabel("")
        self.lbl_badge.setStyleSheet("""
            color: #38BDF8;
            font-size: 11px;
            font-weight: 600;
            padding: 2px 10px;
            border-radius: 9px;
            background-color: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.3);
            margin-top: 2px;
        """)
        self.lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_badge.setVisible(False)
        info_layout.addWidget(self.lbl_badge, 0, Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(info_container)

        # 3. Barre de progression temporelle (Seekbar)
        seek_container = QWidget()
        self.seek_container = seek_container
        seek_layout = QHBoxLayout(seek_container)
        seek_layout.setContentsMargins(0, 2, 0, 0)
        seek_layout.setSpacing(8)

        self.lbl_time_cur = QLabel("00:00")
        self.lbl_time_cur.setStyleSheet("color: #94A3B8; font-size: 12px; font-family: monospace;")
        seek_layout.addWidget(self.lbl_time_cur)

        self.slider_seek = ClickableSlider(Qt.Orientation.Horizontal)
        self.slider_seek.setRange(0, 1000)
        self.slider_seek.setValue(0)
        self.slider_seek.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider_seek.setStyleSheet(seek_slider_qss(groove_height=6, handle_size=14))
        seek_layout.addWidget(self.slider_seek, 1)

        self.lbl_time_total = QLabel("00:00")
        self.lbl_time_total.setStyleSheet("color: #94A3B8; font-size: 12px; font-family: monospace;")
        seek_layout.addWidget(self.lbl_time_total)

        card_layout.addWidget(seek_container)

        # 4. Commandes principales de lecture
        self.ctrl_container = QWidget()
        ctrl_layout = QHBoxLayout(self.ctrl_container)
        ctrl_layout.setContentsMargins(0, 0, 0, 0)
        ctrl_layout.setSpacing(12)
        ctrl_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_shuffle = QPushButton("🔀")
        self.btn_shuffle.setFixedSize(36, 36)
        self.btn_shuffle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_shuffle.setToolTip(tr("player.btn_shuffle"))
        self._style_transport_button(self.btn_shuffle)
        ctrl_layout.addWidget(self.btn_shuffle)

        self.btn_prev = QPushButton("⏮")
        self.btn_prev.setFixedSize(40, 40)
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.setToolTip(tr("player.btn_previous"))
        self._style_transport_button(self.btn_prev, font_size=14)
        ctrl_layout.addWidget(self.btn_prev)

        self.btn_play_pause = QPushButton("▶")
        self.btn_play_pause.setFixedSize(50, 50)
        self.btn_play_pause.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_play_pause.setToolTip(tr("player.btn_play"))
        self.btn_play_pause.setStyleSheet("""
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                border-radius: 25px;
                font-size: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0369A1;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #075985;
            }
        """)
        ctrl_layout.addWidget(self.btn_play_pause)

        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setFixedSize(36, 36)
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.setToolTip(tr("player.btn_stop"))
        self._style_transport_button(self.btn_stop, font_size=12)
        ctrl_layout.addWidget(self.btn_stop)

        self.btn_next = QPushButton("⏭")
        self.btn_next.setFixedSize(40, 40)
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.setToolTip(tr("player.btn_next"))
        self._style_transport_button(self.btn_next, font_size=14)
        ctrl_layout.addWidget(self.btn_next)

        self.btn_repeat = QPushButton("🔁")
        self.btn_repeat.setFixedSize(36, 36)
        self.btn_repeat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_repeat.setToolTip(tr("player.btn_repeat"))
        self._style_transport_button(self.btn_repeat)
        ctrl_layout.addWidget(self.btn_repeat)

        card_layout.addWidget(self.ctrl_container)

        # 5. État vide accueillant (quand aucune source audio n'est configurée)
        self.empty_container = QWidget()
        empty_layout = QVBoxLayout(self.empty_container)
        empty_layout.setContentsMargins(16, 20, 16, 20)
        empty_layout.setSpacing(12)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_empty_icon = QLabel("📁")
        self.lbl_empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_empty_icon.setStyleSheet("""
            QLabel {
                font-size: 50px;
                background-color: rgba(56, 189, 248, 0.08);
                border: 2px dashed rgba(56, 189, 248, 0.35);
                border-radius: 20px;
                padding: 18px;
                min-width: 90px;
                min-height: 90px;
            }
        """)
        empty_layout.addWidget(self.lbl_empty_icon, 0, Qt.AlignmentFlag.AlignCenter)

        self.lbl_empty_title = QLabel(tr("player.empty_title"))
        self.lbl_empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_empty_title.setStyleSheet("color: #F8FAFC; font-size: 18px; font-weight: 700;")
        self.lbl_empty_title.setWordWrap(True)
        empty_layout.addWidget(self.lbl_empty_title)

        self.lbl_empty_desc = QLabel(tr("player.empty_desc"))
        self.lbl_empty_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_empty_desc.setStyleSheet("color: #94A3B8; font-size: 13px; line-height: 1.5;")
        self.lbl_empty_desc.setWordWrap(True)
        empty_layout.addWidget(self.lbl_empty_desc)

        empty_layout.addSpacing(6)

        self.btn_add_first_folder = QPushButton(tr("player.btn_add_first_folder"))
        self.btn_add_first_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_first_folder.setStyleSheet("""
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                border: 1px solid #38BDF8;
                border-radius: 8px;
                font-size: 13.5px;
                font-weight: 600;
                padding: 10px 22px;
            }
            QPushButton:hover {
                background-color: #38BDF8;
                color: #0F172A;
            }
            QPushButton:pressed {
                background-color: #0369A1;
                color: #FFFFFF;
            }
        """)
        self.btn_add_first_folder.clicked.connect(self._on_add_folder_clicked)
        empty_layout.addWidget(self.btn_add_first_folder, 0, Qt.AlignmentFlag.AlignCenter)

        self.empty_container.setVisible(False)
        card_layout.addWidget(self.empty_container)

        center_layout.addWidget(self.card)
        scroll.setWidget(center_container)
        layout.addWidget(scroll, 1)

        self._populate_effects_combo()
