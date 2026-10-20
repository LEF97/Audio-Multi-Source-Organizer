"""Construction de l'interface, signaux et sélecteur d'effets du Blind Test."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import (
    Qt,
)
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from amso.core.config import get_config_manager
from amso.core.i18n import tr
from amso.ui.views.blind_test.zoom_fade_label import ZoomFadeLabel
from amso.ui.views.player_view import ClickableSlider, EffectContainer
from amso.ui.views.visual_effects import VisualEffectWidget

if TYPE_CHECKING:
    _MixinBase = QWidget
else:
    _MixinBase = object


class BlindTestUiMixin(_MixinBase):
    """Construction de l'interface, signaux et sélecteur d'effets du Blind Test."""

    if TYPE_CHECKING:
        # Attributs de BlindTestView résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. En-tête de la page
        top_bar = QFrame()
        top_bar.setObjectName("topBarFrame")
        self.top_bar = top_bar
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 10, 20, 10)
        top_layout.setSpacing(8)

        self.lbl_page_title = QLabel("🎭  " + tr("blind_test.title"))
        self.lbl_page_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        top_layout.addWidget(self.lbl_page_title)

        top_layout.addSpacing(16)

        # Contrôle du volume sonore intégré dans la barre supérieure
        self.btn_mute = QPushButton("🔊")
        self.btn_mute.setFixedSize(30, 30)
        self.btn_mute.setCursor(Qt.CursorShape.PointingHandCursor)
        self._style_icon_button(self.btn_mute, font_size=13)
        self.btn_mute.clicked.connect(self._toggle_mute)
        top_layout.addWidget(self.btn_mute)

        self.slider_volume = ClickableSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(self.player.volume)
        self.slider_volume.setFixedWidth(120)
        self.slider_volume.setFixedHeight(22)
        self.slider_volume.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider_volume.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 5px;
                background-color: #282C37;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background-color: #38BDF8;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background-color: #E2E8F0;
                width: 12px;
                height: 12px;
                margin: -3px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background-color: #38BDF8;
            }
        """)
        self.slider_volume.valueChanged.connect(self._on_volume_changed)
        top_layout.addWidget(self.slider_volume)

        self.lbl_volume = QLabel(f"{self.player.volume}%")
        self.lbl_volume.setStyleSheet("color: #94A3B8; font-size: 12px; min-width: 38px;")
        top_layout.addWidget(self.lbl_volume)

        top_layout.addStretch()

        self.lbl_effect_badge = QLabel(tr("player.visual_effect"))
        self.lbl_effect_badge.setStyleSheet("color: #94A3B8; font-size: 12.5px; font-weight: 500; margin-right: 4px;")
        top_layout.addWidget(self.lbl_effect_badge)

        self.combo_effect = QComboBox()
        self.combo_effect.setCursor(Qt.CursorShape.PointingHandCursor)
        self.combo_effect.setFixedWidth(250)
        self.combo_effect.view().setMinimumWidth(260)
        self.combo_effect.setStyleSheet("""
            QComboBox {
                background-color: #20242D;
                color: #F8FAFC;
                border: 1px solid #38BDF8;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: 500;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #1A1D24;
                color: #F8FAFC;
                selection-background-color: #0284C7;
                border: 1px solid #282C37;
            }
        """)
        top_layout.addWidget(self.combo_effect)
        layout.addWidget(top_bar)

        # Sous-barre de progression globale de la session Blind Test
        sub_bar = QFrame()
        sub_bar.setObjectName("subBarFrame")
        self.sub_bar = sub_bar
        sub_layout = QHBoxLayout(sub_bar)
        sub_layout.setContentsMargins(20, 10, 20, 8)
        sub_layout.setSpacing(8)

        sub_layout.addStretch()
        self.lbl_session_progress = QLabel("")
        self.lbl_session_progress.setObjectName("lblSessionProgress")
        self.lbl_session_progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_session_progress.setStyleSheet("""
            QLabel#lblSessionProgress {
                color: #94A3B8;
                font-size: 13px;
                font-weight: 600;
                padding: 4px 16px;
                border-radius: 12px;
                background-color: rgba(30, 41, 59, 0.7);
                border: 1px solid rgba(56, 189, 248, 0.22);
                margin-top: 2px;
            }
        """)
        sub_layout.addWidget(self.lbl_session_progress)
        sub_layout.addStretch()
        layout.addWidget(sub_bar)

        # 2. Toile d'effet visuel dynamique en fond
        cfg = get_config_manager()
        initial_effect = cfg.get_visual_effect()
        self.effect_canvas = VisualEffectWidget(initial_effect)

        # Zone défilante centrale
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        center_container = EffectContainer(self.effect_canvas)
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(16, 12, 16, 12)
        center_layout.setSpacing(12)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 3. Carte centrale du Blind Test
        self.card = QFrame()
        self.card.setObjectName("blindTestCard")
        self.card.setMinimumWidth(500)
        self.card.setMaximumWidth(580)
        self.card.setStyleSheet("""
            QFrame#blindTestCard {
                background-color: rgba(26, 29, 36, 0.94);
                border: 1px solid rgba(56, 189, 248, 0.28);
                border-radius: 16px;
            }
        """)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(24, 18, 24, 18)
        card_layout.setSpacing(12)

        # Zone d'affichage de la Pochette / Décompte
        self.cover_box = QFrame()
        self.cover_box.setFixedSize(280, 280)
        self.cover_box.setStyleSheet("""
            QFrame {
                background-color: #12151B;
                border: 2px dashed rgba(56, 189, 248, 0.4);
                border-radius: 16px;
            }
        """)

        cover_layout = QGridLayout(self.cover_box)
        cover_layout.setContentsMargins(0, 0, 0, 0)
        cover_layout.setSpacing(0)

        # Label de la pochette réelle (initialement cachée avec opacité 0.0)
        self.lbl_cover = QLabel()
        self.lbl_cover.setFixedSize(280, 280)
        self.lbl_cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_cover.setStyleSheet("border-radius: 16px;")
        self.cover_opacity = QGraphicsOpacityEffect(self.lbl_cover)
        self.cover_opacity.setOpacity(0.0)
        self.lbl_cover.setGraphicsEffect(self.cover_opacity)
        cover_layout.addWidget(self.lbl_cover, 0, 0)

        # Chiffre géant animé superposé
        self.lbl_countdown = ZoomFadeLabel()
        self.lbl_countdown.setFixedSize(280, 280)
        font = self.lbl_countdown.font()
        font.setPixelSize(88)
        font.setWeight(QFont.Weight.ExtraBold)
        self.lbl_countdown.setFont(font)
        self.lbl_countdown.setText("20")
        self.lbl_countdown.setStyleSheet("""
            color: #38BDF8;
            font-size: 88px;
            font-weight: 800;
            background: transparent;
        """)
        cover_layout.addWidget(self.lbl_countdown, 0, 0)

        card_layout.addWidget(self.cover_box, 0, Qt.AlignmentFlag.AlignCenter)

        # Jauge de manche
        self.round_progress = QProgressBar()
        self.round_progress.setRange(0, 100)
        self.round_progress.setValue(0)
        self.round_progress.setFixedHeight(6)
        self.round_progress.setTextVisible(False)
        self.round_progress.setStyleSheet("""
            QProgressBar {
                background-color: #20242D;
                border-radius: 3px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #38BDF8;
                border-radius: 3px;
            }
        """)
        card_layout.addWidget(self.round_progress)

        # Badge de statut (ex: "À vous de deviner !", "Révélé !")
        self.lbl_status_badge = QLabel(tr("blind_test.status_searching"))
        self.lbl_status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status_badge.setStyleSheet("""
            color: #38BDF8;
            font-size: 12px;
            font-weight: 600;
            padding: 3px 12px;
            border-radius: 10px;
            background-color: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.3);
        """)
        card_layout.addWidget(self.lbl_status_badge, 0, Qt.AlignmentFlag.AlignCenter)

        # Zone textes Titre et Artiste
        info_container = QWidget()
        info_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        self.lbl_title = QLabel("❓  " + tr("blind_test.mystery_title"))
        self.lbl_title.setStyleSheet("color: #F8FAFC; font-size: 19px; font-weight: 700;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setWordWrap(True)
        info_layout.addWidget(self.lbl_title)

        self.lbl_artist_album = QLabel("👥  " + tr("blind_test.mystery_artist"))
        self.lbl_artist_album.setStyleSheet("color: #94A3B8; font-size: 14px;")
        self.lbl_artist_album.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_artist_album.setWordWrap(True)
        info_layout.addWidget(self.lbl_artist_album)

        self.lbl_file_name = QLabel("📁  " + tr("blind_test.mystery_file"))
        self.lbl_file_name.setStyleSheet("color: #64748B; font-size: 12px; margin-top: 4px; margin-bottom: 12px;")
        self.lbl_file_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_file_name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.lbl_file_name.setWordWrap(True)
        info_layout.addWidget(self.lbl_file_name)

        card_layout.addWidget(info_container)
        card_layout.addSpacing(6)

        # 4. Commandes de jeu du Blind Test
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(10)
        ctrl_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Bouton Morceau précédent
        self.btn_prev = QPushButton(tr("blind_test.btn_prev"))
        self.btn_prev.setFixedHeight(46)
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.setStyleSheet("""
            QPushButton {
                background-color: #20242D;
                color: #F8FAFC;
                border: 1px solid #333846;
                border-radius: 12px;
                padding: 0 14px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2B303C;
                border-color: #38BDF8;
            }
        """)
        self.btn_prev.clicked.connect(self._on_prev_track_clicked)
        ctrl_layout.addWidget(self.btn_prev)

        # Bouton Play / Pause (pour lancer ou figer le chrono)
        self.btn_play_pause = QPushButton("▶")
        self.btn_play_pause.setFixedSize(46, 46)
        self.btn_play_pause.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_play_pause.setStyleSheet("""
            QPushButton {
                background-color: #20242D;
                color: #CBD5E1;
                border: 1px solid #333846;
                border-radius: 23px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #2B303C;
                color: #F8FAFC;
                border-color: #38BDF8;
            }
        """)
        self.btn_play_pause.clicked.connect(self._on_play_pause_clicked)
        ctrl_layout.addWidget(self.btn_play_pause)

        # Bouton Révéler immédiatement
        self.btn_reveal = QPushButton(tr("blind_test.btn_reveal"))
        self.btn_reveal.setFixedHeight(46)
        self.btn_reveal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reveal.setStyleSheet("""
            QPushButton {
                background-color: #20242D;
                color: #F8FAFC;
                border: 1px solid #333846;
                border-radius: 12px;
                padding: 0 18px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2B303C;
                border-color: #38BDF8;
            }
            QPushButton:disabled {
                background-color: #16181F;
                color: #475569;
                border-color: #242832;
            }
        """)
        self.btn_reveal.clicked.connect(self._on_reveal_clicked)
        ctrl_layout.addWidget(self.btn_reveal)

        # Bouton Piste suivante
        self.btn_next = QPushButton(tr("blind_test.btn_next"))
        self.btn_next.setFixedHeight(46)
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.setStyleSheet("""
            QPushButton {
                background-color: #20242D;
                color: #F8FAFC;
                border: 1px solid #333846;
                border-radius: 12px;
                padding: 0 14px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2B303C;
                border-color: #38BDF8;
            }
        """)
        self.btn_next.clicked.connect(self._on_next_track_clicked)
        ctrl_layout.addWidget(self.btn_next)

        card_layout.addLayout(ctrl_layout)

        center_layout.addWidget(self.card)
        scroll.setWidget(center_container)
        layout.addWidget(scroll, 1)

        self._populate_effects_combo()
        self.combo_effect.currentIndexChanged.connect(self._on_effect_combo_changed)

    def _style_icon_button(self, btn: QPushButton, font_size: int = 14) -> None:
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #20242D;
                color: #CBD5E1;
                border: 1px solid #282C37;
                border-radius: 6px;
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

    def _connect_signals(self) -> None:
        self.player.track_changed.connect(self._on_track_changed)
        self.player.state_changed.connect(self._on_playback_state_changed)
        self.player.volume_changed.connect(self._on_player_volume_changed)
        self.player.position_changed.connect(self._on_player_position_changed)
        self.player.playlist_updated.connect(self._on_playlist_updated)

    def _populate_effects_combo(self) -> None:
        """Remplit le menu déroulant des effets visuels."""
        current_data = getattr(self, "current_effect", None) or (
            self.effect_canvas.effect_type if hasattr(self, "effect_canvas") else "particles"
        )
        self.combo_effect.blockSignals(True)
        self.combo_effect.clear()
        effects = [
            ("particles", f"✨ {tr('effects.particles')}"),
            ("waves", f"🌊 {tr('effects.waves')}"),
            ("stars", f"☄️ {tr('effects.stars')}"),
            ("warp", f"🚀 {tr('effects.warp')}"),
            ("warp_dynamic", f"🛸 {tr('effects.warp_dynamic')}"),
            ("aurora", f"🌌 {tr('effects.aurora')}"),
            ("bars", f"📊 {tr('effects.bars')}"),
            ("bars_full", f"📶 {tr('effects.bars_full')}"),
            ("none", f"🚫 {tr('effects.none')}"),
        ]
        target_idx = 0
        for i, (key, label) in enumerate(effects):
            self.combo_effect.addItem(label, key)
            if key == current_data:
                target_idx = i
        self.combo_effect.setCurrentIndex(target_idx)
        self.combo_effect.blockSignals(False)

    def _on_effect_combo_changed(self, index: int) -> None:
        effect_key = self.combo_effect.itemData(index)
        if effect_key:
            self.set_effect_type(effect_key)
            self.effect_changed.emit(effect_key)

    def set_effect_type(self, effect_name: str) -> None:
        self.current_effect = effect_name
        if hasattr(self, "effect_canvas") and self.effect_canvas:
            self.effect_canvas.set_effect_type(effect_name)
        if hasattr(self, "combo_effect"):
            self.combo_effect.blockSignals(True)
            for i in range(self.combo_effect.count()):
                if self.combo_effect.itemData(i) == effect_name:
                    self.combo_effect.setCurrentIndex(i)
                    break
            self.combo_effect.blockSignals(False)
        cfg = get_config_manager()
        cfg.set_visual_effect(effect_name)

    # -------------------------------------------------------------------------
    # Alias et accesseurs de compatibilité pour les tests
    # -------------------------------------------------------------------------
