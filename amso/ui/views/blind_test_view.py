"""Vue dédiée au mode Blind Test interactif pour AMSO."""

from __future__ import annotations

import os
import time

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QColor, QFont, QHideEvent, QPainter, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGraphicsOpacityEffect,
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
from amso.core.database import TrackRecord
from amso.core.i18n import tr
from amso.services.player_service import PlayerService
from amso.ui.views.cover_helper import get_default_cover_pixmap, load_cover_async
from amso.ui.views.player_view import ClickableSlider, EffectContainer
from amso.ui.views.visual_effects import VisualEffectWidget


class ZoomFadeLabel(QLabel):
    """QLabel animé effectuant un zoom dynamique et un fondu à chaque changement de valeur."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scale: float = 1.0

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)

        # Animation d'opacité (fondu doux)
        self._anim_opacity = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._anim_opacity.setDuration(750)
        self._anim_opacity.setStartValue(1.0)
        self._anim_opacity.setEndValue(0.4)
        self._anim_opacity.setEasingCurve(QEasingCurve.Type.OutQuad)

        # Animation d'échelle (Zoom dynamique de 1.45 vers 1.0)
        self._anim_scale = QPropertyAnimation(self, b"scale_factor", self)
        self._anim_scale.setDuration(750)
        self._anim_scale.setStartValue(1.45)
        self._anim_scale.setEndValue(1.0)
        self._anim_scale.setEasingCurve(QEasingCurve.Type.OutCubic)

    def get_scale_factor(self) -> float:
        return self._scale

    def set_scale_factor(self, s: float) -> None:
        self._scale = s
        self.update()

    scale_factor = Property(float, get_scale_factor, set_scale_factor)

    def trigger_tick_animation(self) -> None:
        """Déclenche l'animation de pulse (zoom dynamique) et fondu à chaque seconde."""
        self._anim_opacity.stop()
        self._anim_scale.stop()
        self._opacity_effect.setOpacity(1.0)
        self._scale = 1.45
        self._anim_opacity.start()
        self._anim_scale.start()

    def show_number(self, val: int) -> None:
        """Affiche le nombre et déclenche l'animation de zoom et fondu."""
        self.setText(str(val))
        self.trigger_tick_animation()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = float(self.width())
        h = float(self.height())
        painter.translate(w / 2.0, h / 2.0)
        painter.scale(self._scale, self._scale)
        painter.translate(-w / 2.0, -h / 2.0)

        painter.setFont(self.font())
        painter.setPen(QColor("#38BDF8"))
        painter.drawText(self.rect(), int(self.alignment()), self.text())
        painter.end()


class BlindTestView(QWidget):
    """Page dédiée au jeu de Blind Test musical grand format."""

    effect_changed = Signal(str)

    def __init__(self, player_service: PlayerService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.player = player_service

        # États du Blind Test : "countdown", "revealed", "idle"
        self._state: str = "idle"
        cfg = get_config_manager()
        self._configured_countdown: int = cfg.get_blind_test_countdown()
        self._configured_reveal: int = cfg.get_blind_test_reveal()
        self._configured_fade: int = cfg.get_blind_test_fade()
        self._countdown_remain: int = self._configured_countdown
        self._reveal_remain: int = self._configured_reveal
        self._total_round_duration: int = self._countdown_remain + self._reveal_remain
        self._current_round_elapsed: int = 0
        self._is_active_page: bool = False
        self.current_effect: str = cfg.get_visual_effect()
        self._nominal_volume: int = getattr(self.player, "volume", 100)
        self._is_fading: bool = False
        self._fade_start_time: float = 0.0
        self._fade_duration: float = float(self._configured_fade)

        # Fondu entrant (Fade-in 0% -> 100% sur 2.0 secondes)
        self._is_fading_in: bool = False
        self._fade_in_duration: float = 2.0
        self._fade_in_start_time: float = 0.0
        self._fade_in_paused_elapsed: float = 0.0

        self._setup_ui()
        self._connect_signals()

        # Timer d'horloge de seconde en seconde pour le Blind Test
        self._game_timer = QTimer(self)
        self._game_timer.setInterval(1000)
        self._game_timer.timeout.connect(self._on_game_tick)

        # Timer pour fondu sonore progressif sortant (fin de manche)
        self._fade_timer = QTimer(self)
        self._fade_timer.setInterval(50)
        self._fade_timer.timeout.connect(self._on_fade_tick)

        # Timer pour fondu sonore progressif entrant (0% -> 100% en 2 secondes au début)
        self._fade_in_timer = QTimer(self)
        self._fade_in_timer.setInterval(50)
        self._fade_in_timer.timeout.connect(self._on_fade_in_tick)

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
        self.combo_effect.setFixedWidth(175)
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
        sub_layout.setContentsMargins(20, 2, 20, 6)
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
        cover_container = QWidget()
        cover_container.setFixedSize(280, 280)

        self.cover_box = QFrame(cover_container)
        self.cover_box.setFixedSize(280, 280)
        self.cover_box.setStyleSheet("""
            QFrame {
                background-color: #12151B;
                border: 2px dashed rgba(56, 189, 248, 0.4);
                border-radius: 16px;
            }
        """)

        # Label de la pochette réelle (initialement cachée avec opacité 0.0)
        self.lbl_cover = QLabel(self.cover_box)
        self.lbl_cover.setFixedSize(280, 280)
        self.lbl_cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_cover.setStyleSheet("border-radius: 16px;")
        self.cover_opacity = QGraphicsOpacityEffect(self.lbl_cover)
        self.cover_opacity.setOpacity(0.0)
        self.lbl_cover.setGraphicsEffect(self.cover_opacity)

        # Chiffre géant animé superposé
        self.lbl_countdown = ZoomFadeLabel(self.cover_box)
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

        card_layout.addWidget(cover_container, 0, Qt.AlignmentFlag.AlignCenter)

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
        self.lbl_file_name.setStyleSheet("color: #64748B; font-size: 12px; margin-top: 2px;")
        self.lbl_file_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_file_name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.lbl_file_name.setWordWrap(True)
        info_layout.addWidget(self.lbl_file_name)

        card_layout.addWidget(info_container)

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
                background-color: #0284C7;
                color: #FFFFFF;
                border: 1px solid #38BDF8;
                border-radius: 12px;
                padding: 0 18px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #0369A1;
                border-color: #7DD3FC;
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
        self.player.playlist_updated.connect(self._on_playlist_updated)

    def _on_playlist_updated(self) -> None:
        if self._is_active_page:
            self._update_session_progress()

    def showEvent(self, event) -> None:
        """Déclenché lorsque l'utilisateur affiche la page Blind Test.
        Sauvegarde l'état du lecteur sans démarrer la musique automatiquement."""
        super().showEvent(event)
        self._is_active_page = True

        # Sauvegarder l'état exact du lecteur (piste sélectionnée, position, lecture en cours)
        # pour le restaurer fidèlement lorsqu'on quitte le Blind Test
        self._saved_player_index = self.player.current_index
        self._saved_player_position_ms = getattr(self.player, "current_time_ms", 0)
        self._saved_player_was_playing = self.player.is_playing

        # La musique ne doit PAS démarrer de suite lors de l'arrivée sur la page
        if self.player.is_playing:
            self.player.pause()

        # Synchroniser l'effet visuel actif avec le ConfigManager
        cfg = get_config_manager()
        eff = cfg.get_visual_effect()
        self.set_effect_type(eff)

        # Préparer la manche sur le morceau courant à 0 seconde, en attente de play
        if self.player.current_track:
            self._start_round_for_track(self.player.current_track, auto_play=False)
        elif self.player.playlist:
            self.player.play_index(0)
            self.player.pause()
            self._start_round_for_track(self.player.current_track, auto_play=False)
        else:
            self._reset_to_empty_state()

        self._update_session_progress()

    def hideEvent(self, event: QHideEvent) -> None:
        """Déclenché lorsque l'utilisateur quitte la page Blind Test.
        Restaure fidèlement l'état initial du lecteur (morceau et position d'origine)."""
        self._is_active_page = False
        # Stopper les timers et rétablir le volume nominal
        self._game_timer.stop()
        self._stop_fade_out()
        self._stop_fade_in()
        self._stop_fade_and_restore_volume()

        # Restauration de l'état du lecteur enregistré avant le Blind Test
        self._restore_saved_player_state()

        try:
            super().hideEvent(event)
        except Exception:
            pass

    def _restore_saved_player_state(self) -> None:
        """Restaure la piste et la position de lecture qui étaient actives avant d'entrer en Blind Test."""
        if not hasattr(self, "_saved_player_index") or self._saved_player_index is None:
            return

        saved_idx = self._saved_player_index
        saved_ms = getattr(self, "_saved_player_position_ms", 0)
        saved_was_playing = getattr(self, "_saved_player_was_playing", False)
        self._saved_player_index = None

        if not self.player.playlist or saved_idx < 0 or saved_idx >= len(self.player.playlist):
            return

        # Si le Blind Test a changé de piste ou si la position a changé :
        if self.player.current_index != saved_idx:
            if saved_ms > 0:
                self.player._pending_seek_ms = saved_ms
                self.player.play_index(saved_idx, resume_pending=True)
            else:
                self.player.play_index(saved_idx)
            if not saved_was_playing:
                self.player.pause()
        else:
            self.player.seek_ms(saved_ms)
            if not saved_was_playing and self.player.is_playing:
                self.player.pause()
            elif saved_was_playing and not self.player.is_playing:
                self.player.play()

    def set_durations(
        self, countdown_seconds: int, reveal_seconds: int, fade_seconds: int | None = None
    ) -> None:
        """Met à jour les durées configurées du Blind Test."""
        self._configured_countdown = countdown_seconds
        self._configured_reveal = reveal_seconds
        if fade_seconds is not None:
            self._configured_fade = fade_seconds
        self._countdown_remain = countdown_seconds
        self._reveal_remain = reveal_seconds
        self._total_round_duration = countdown_seconds + reveal_seconds
        self._fade_duration = float(self._configured_fade)

    def _update_session_progress(self) -> None:
        """Calcule et affiche la progression de la session : 'Extrait x / y — reste z minutes'."""
        if not hasattr(self, "lbl_session_progress"):
            return

        playlist = getattr(self.player, "playlist", None)
        total_tracks = len(playlist) if isinstance(playlist, (list, tuple)) else 0
        if total_tracks == 0:
            self.lbl_session_progress.setText(tr("blind_test.session_empty"))
            return

        cur_idx = getattr(self.player, "current_index", 0)
        if not isinstance(cur_idx, int) or cur_idx < 0:
            cur_idx = 0
        current_track_num = cur_idx + 1

        # Temps restant dans la manche actuelle
        current_round_remain = max(0, self._total_round_duration - self._current_round_elapsed)
        future_tracks = max(0, total_tracks - current_track_num)
        total_remain_sec = current_round_remain + (future_tracks * self._total_round_duration)

        if total_remain_sec >= 90:
            mins = max(1, round(total_remain_sec / 60))
            remain_str = tr("blind_test.minutes_plural", count=mins)
        elif total_remain_sec >= 45:
            remain_str = tr("blind_test.minutes_singular")
        elif total_remain_sec > 0:
            remain_str = tr("blind_test.less_than_minute")
        else:
            remain_str = tr("blind_test.less_than_minute")

        text = tr("blind_test.session_progress", current=current_track_num, total=total_tracks, remain=remain_str)
        self.lbl_session_progress.setText(text)

    def _preload_next_track(self) -> None:
        """Précharge en tâche de fond le prochain fichier de la playlist sur le lecteur standby."""
        if not hasattr(self.player, "get_next_index") or not hasattr(self.player, "preload_track"):
            return
        next_idx = self.player.get_next_index()
        if next_idx is not None and next_idx != self.player.current_index:
            self.player.preload_track(next_idx)

    def _start_round_for_track(self, track: TrackRecord | None, auto_play: bool = False) -> None:
        """Initialise une manche de Blind Test sur la piste fournie, démarrant à 0 seconde."""
        if not track:
            self._reset_to_empty_state()
            return

        self._stop_fade_out()
        self._stop_fade_in()
        self._nominal_volume = getattr(self.player, "volume", 100)
        self._countdown_remain = self._configured_countdown
        self._reveal_remain = self._configured_reveal
        self._fade_duration = float(self._configured_fade)
        self._total_round_duration = self._countdown_remain + self._reveal_remain
        self._current_round_elapsed = 0

        self._state = "countdown"
        self.lbl_countdown.setVisible(True)
        self.lbl_countdown.show_number(self._countdown_remain)

        # Pochette masquée
        self.cover_opacity.setOpacity(0.0)
        self.cover_box.setStyleSheet("""
            QFrame {
                background-color: #12151B;
                border: 2px dashed rgba(56, 189, 248, 0.4);
                border-radius: 16px;
            }
        """)

        # Textes mystère
        self.lbl_title.setText("❓  " + tr("blind_test.mystery_title"))
        self.lbl_artist_album.setText("👥  " + tr("blind_test.mystery_artist"))
        self.lbl_file_name.setText("📁  " + tr("blind_test.mystery_file"))
        self.lbl_file_name.setToolTip("")
        self.lbl_file_name.setVisible(True)

        self.btn_reveal.setEnabled(True)
        if hasattr(self, "btn_prev"):
            self.btn_prev.setEnabled(True)
        self.btn_next.setEnabled(True)
        self.round_progress.setValue(0)

        # Précharger l'image de couverture
        pix = load_cover_async(track, size=280, radius=16, callback=self._on_cover_loaded)
        if pix and not pix.isNull():
            self.lbl_cover.setPixmap(pix)

        # Positionner la lecture impérativement à 0 seconde
        self.player.seek_ratio(0.0)

        # Précharger immédiatement le fichier suivant en mémoire tampon
        self._preload_next_track()
        self._update_session_progress()

        if auto_play:
            # Démarrer à 0% et monter en fondu progressif de 2 secondes vers 100%
            self._apply_temporary_volume(0)
            if not self.player.is_playing:
                self.player.play()
                self.player.seek_ratio(0.0)
            self._start_fade_in(2.0)
            self.btn_play_pause.setText("⏸")
            self.lbl_status_badge.setText(tr("blind_test.status_searching"))
            self.lbl_status_badge.setStyleSheet("""
                color: #38BDF8;
                font-size: 12px;
                font-weight: 600;
                padding: 3px 12px;
                border-radius: 10px;
                background-color: rgba(56, 189, 248, 0.12);
                border: 1px solid rgba(56, 189, 248, 0.3);
            """)
            if self._is_active_page:
                self._game_timer.start(1000)
        else:
            self._game_timer.stop()
            self.btn_play_pause.setText("▶")
            self.lbl_status_badge.setText(tr("blind_test.status_paused"))
            self.lbl_status_badge.setStyleSheet("""
                color: #94A3B8;
                font-size: 12px;
                font-weight: 600;
                padding: 3px 12px;
                border-radius: 10px;
                background-color: rgba(148, 163, 184, 0.12);
                border: 1px solid rgba(148, 163, 184, 0.3);
            """)

    def _restart_current_round(self) -> None:
        """Remet à zéro la manche courante du Blind Test avec fondu entrant de 2s."""
        self._stop_fade_out()
        self._stop_fade_in()
        self._current_round_elapsed = 0
        self._countdown_remain = self._configured_countdown
        self._reveal_remain = self._configured_reveal
        self._state = "countdown"
        self.round_progress.setValue(0)
        self.lbl_countdown.setVisible(True)
        self.lbl_countdown.show_number(self._countdown_remain)
        self.cover_opacity.setOpacity(0.0)
        self.cover_box.setStyleSheet("""
            QFrame {
                background-color: #12151B;
                border: 2px dashed rgba(56, 189, 248, 0.4);
                border-radius: 16px;
            }
        """)
        self.lbl_title.setText("❓  " + tr("blind_test.mystery_title"))
        self.lbl_artist_album.setText("👥  " + tr("blind_test.mystery_artist"))
        self.lbl_file_name.setText("📁  " + tr("blind_test.mystery_file"))
        self.lbl_file_name.setToolTip("")
        self.lbl_file_name.setVisible(True)
        self.btn_reveal.setEnabled(True)
        self.player.seek_ratio(0.0)
        self._preload_next_track()
        self._update_session_progress()

        if self.player.is_playing:
            self._apply_temporary_volume(0)
            self._start_fade_in(2.0)
            self.lbl_status_badge.setText(tr("blind_test.status_searching"))
            self.lbl_status_badge.setStyleSheet("""
                color: #38BDF8;
                font-size: 12px;
                font-weight: 600;
                padding: 3px 12px;
                border-radius: 10px;
                background-color: rgba(56, 189, 248, 0.12);
                border: 1px solid rgba(56, 189, 248, 0.3);
            """)
            self._game_timer.start(1000)
        else:
            self.lbl_status_badge.setText(tr("blind_test.status_paused"))
            self.lbl_status_badge.setStyleSheet("""
                color: #94A3B8;
                font-size: 12px;
                font-weight: 600;
                padding: 3px 12px;
                border-radius: 10px;
                background-color: rgba(148, 163, 184, 0.12);
                border: 1px solid rgba(148, 163, 184, 0.3);
            """)

    def _on_cover_loaded(self, target_path: str, pix: QPixmap | None) -> None:
        if not pix or pix.isNull():
            pix = get_default_cover_pixmap(280, 16)
        scaled = pix.scaled(
            280,
            280,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.lbl_cover.setPixmap(scaled)

    def _on_game_tick(self) -> None:
        """Tic régulier de 1 seconde pour animer le décompte et orchestrer la révélation."""
        if not self._is_active_page or not self.player.is_playing:
            return

        self._current_round_elapsed += 1
        pct = min(100, int((self._current_round_elapsed / max(1, self._total_round_duration)) * 100))
        self.round_progress.setValue(pct)
        self._update_session_progress()

        if self._state == "countdown":
            self._countdown_remain -= 1
            if self._countdown_remain > 0:
                self.lbl_countdown.setText(str(self._countdown_remain))
                self.lbl_countdown.trigger_tick_animation()
            else:
                self._trigger_reveal()

        elif self._state == "revealed":
            self._reveal_remain -= 1
            if self._reveal_remain > 0:
                self.lbl_status_badge.setText(tr("blind_test.status_revealed", remain=self._reveal_remain))
                # Vérifier et appliquer le fondu sonore si on est dans la période finale
                eff_fade = min(self._configured_fade, self._configured_reveal)
                if eff_fade > 0 and self._reveal_remain <= eff_fade:
                    if not self._is_fading:
                        self._start_fade(eff_fade)
                    fraction = max(0.0, float(self._reveal_remain) / max(1, eff_fade))
                    target_vol = max(0, int(round(self._nominal_volume * fraction)))
                    self._apply_temporary_volume(target_vol)
            else:
                # Fin de la phase de découverte : extinction propre et passage automatique au suivant !
                self._game_timer.stop()
                self._stop_fade_out()
                # S'assurer que le morceau en cours s'éteint complètement à 0% sans rebond sonore
                self._apply_temporary_volume(0)
                self.player.next()

    def _start_fade_in(self, duration_sec: float = 2.0) -> None:
        """Déclenche la montée progressive du volume sonore de 0% vers 100% sur 2 secondes."""
        self._stop_fade_out()
        self._is_fading_in = True
        self._fade_in_duration = max(0.2, float(duration_sec))
        self._fade_in_start_time = time.time()
        self._fade_in_paused_elapsed = 0.0
        self._apply_temporary_volume(0)
        self._fade_in_timer.start(50)

    def _on_fade_in_tick(self) -> None:
        """Applique la montée progressive du volume toutes les 50ms."""
        if not self._is_active_page or not self.player.is_playing or not self._is_fading_in:
            return
        if self._fade_in_duration <= 0:
            return
        elapsed = time.time() - self._fade_in_start_time
        progress = max(0.0, min(1.0, elapsed / self._fade_in_duration))
        target_vol = max(0, min(self._nominal_volume, int(round(self._nominal_volume * progress))))
        self._apply_temporary_volume(target_vol)
        if progress >= 1.0:
            self._fade_in_timer.stop()
            self._is_fading_in = False
            if hasattr(self.player, "restore_volume"):
                self.player.restore_volume()

    def _stop_fade_in(self) -> None:
        """Arrête le timer de montée progressive sans forcer le volume nominal."""
        if hasattr(self, "_fade_in_timer"):
            self._fade_in_timer.stop()
        self._is_fading_in = False

    def _start_fade(self, duration_sec: int | float) -> None:
        """Déclenche le fondu progressif de fin de manche (extinction vers 0%)."""
        self._stop_fade_in()
        self._is_fading = True
        self._fade_duration = max(0.2, float(duration_sec))
        self._fade_start_time = time.time()
        self._last_fade_vol = -1
        self._fade_timer.start(50)

    def _on_fade_tick(self) -> None:
        """Applique une atténuation continue et fluide toutes les 50ms."""
        if not self._is_active_page or not self.player.is_playing or not self._is_fading:
            return
        if self._fade_duration <= 0:
            return
        elapsed = time.time() - self._fade_start_time
        progress = max(0.0, min(1.0, elapsed / self._fade_duration))
        remaining_ratio = 1.0 - progress
        target_vol = max(0, int(round(self._nominal_volume * remaining_ratio)))
        if getattr(self, "_last_fade_vol", -1) != target_vol:
            self._last_fade_vol = target_vol
            self._apply_temporary_volume(target_vol)
        if progress >= 1.0:
            self._fade_timer.stop()
            self._apply_temporary_volume(0)

    def _stop_fade_out(self) -> None:
        """Arrête le timer de fondu descendant sans rétablir le volume nominal."""
        if hasattr(self, "_fade_timer"):
            self._fade_timer.stop()
        self._is_fading = False
        self._last_fade_vol = -1

    def _apply_temporary_volume(self, vol: int) -> None:
        """Transmet le volume atténué au lecteur sans écraser la configuration."""
        if hasattr(self.player, "audio_set_temporary_volume"):
            self.player.audio_set_temporary_volume(vol)

    def _stop_fade_and_restore_volume(self) -> None:
        """Arrête les fondus et rétablit instantanément 100% du volume nominal."""
        self._stop_fade_out()
        self._stop_fade_in()
        if hasattr(self.player, "restore_volume"):
            self.player.restore_volume()

    def _trigger_reveal(self) -> None:
        """Déclenche l'animation de révélation (Fade-In de la pochette et textes)."""
        self._state = "revealed"
        self.lbl_countdown.setVisible(False)
        self.btn_reveal.setEnabled(False)

        # Repositionner au début de la phase de découverte (10s restantes par défaut)
        self._countdown_remain = 0
        self._reveal_remain = self._configured_reveal
        self._current_round_elapsed = self._configured_countdown
        pct = min(100, int((self._current_round_elapsed / max(1, self._total_round_duration)) * 100))
        self.round_progress.setValue(pct)

        # Animation fondu de la pochette
        self.anim_cover = QPropertyAnimation(self.cover_opacity, b"opacity", self)
        self.anim_cover.setDuration(450)
        self.anim_cover.setStartValue(0.0)
        self.anim_cover.setEndValue(1.0)
        self.anim_cover.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim_cover.start()

        self.cover_box.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 2px solid rgba(56, 189, 248, 0.4);
                border-radius: 16px;
            }
        """)

        # Révélation des vrais titres, artistes et nom de fichier
        track = self.player.current_track
        if track:
            title_str = track.title or track.file_name or tr("track.untitled")
            art_str = track.artist or tr("track.unknown_artist")
            if track.album:
                art_str += f" — {track.album}"
            self.lbl_title.setText(title_str)
            self.lbl_artist_album.setText(art_str)
            file_name_text = track.file_name or (
                os.path.basename(track.source_path.replace("\\", "/")) if track.source_path else ""
            )
            if file_name_text:
                self.lbl_file_name.setText(file_name_text)
                self.lbl_file_name.setToolTip(file_name_text)
                self.lbl_file_name.setVisible(True)
            else:
                self.lbl_file_name.setVisible(False)

        self.lbl_status_badge.setText(tr("blind_test.status_revealed", remain=self._reveal_remain))
        self.lbl_status_badge.setStyleSheet("""
            color: #4ADE80;
            font-size: 12px;
            font-weight: 600;
            padding: 3px 12px;
            border-radius: 10px;
            background-color: rgba(74, 222, 128, 0.12);
            border: 1px solid rgba(74, 222, 128, 0.3);
        """)

        # Précharger immédiatement la piste suivante en tâche de fond sur standby
        self._preload_next_track()

        # Si le fondu configuré est supérieur ou égal au temps de découverte restant, lancer le fondu
        eff_fade = min(self._configured_fade, self._configured_reveal)
        if eff_fade >= self._reveal_remain and eff_fade > 0 and not self._is_fading:
            self._start_fade(eff_fade)

    def _on_reveal_clicked(self) -> None:
        """Révèle immédiatement la piste si les joueurs ont trouvé avant la fin des 20s.
        Garantit qu'il reste la durée complète de découverte (10s par défaut)."""
        if self._state == "countdown":
            self._trigger_reveal()

    def _on_prev_track_clicked(self) -> None:
        """Revient à 0 d'abord si la manche a déjà démarré (> 2s ou révélée),
        ou passe réellement au morceau précédent si au tout début."""
        if self._current_round_elapsed > 2 or self._state == "revealed":
            self._restart_current_round()
        else:
            self._stop_fade_out()
            self._stop_fade_in()
            self._apply_temporary_volume(0)
            self._game_timer.stop()
            self.player.previous()

    def _on_next_track_clicked(self) -> None:
        """Passe immédiatement au titre suivant dans le Blind Test (démarre à 0s)."""
        self._game_timer.stop()
        self._stop_fade_out()
        self._stop_fade_in()
        self._apply_temporary_volume(0)
        self.player.next()

    def _on_play_pause_clicked(self) -> None:
        """Met en pause ou reprend la lecture et le décompte."""
        if self.player.is_playing:
            self.player.pause()
            self._game_timer.stop()
            if self._is_fading and hasattr(self, "_fade_timer"):
                self._fade_timer.stop()
                self._fade_paused_elapsed = max(0.0, time.time() - self._fade_start_time)
            if self._is_fading_in and hasattr(self, "_fade_in_timer"):
                self._fade_in_timer.stop()
                self._fade_in_paused_elapsed = max(0.0, time.time() - self._fade_in_start_time)
            self.btn_play_pause.setText("▶")
            self.lbl_status_badge.setText(tr("blind_test.status_paused"))
            self.lbl_status_badge.setStyleSheet("""
                color: #94A3B8;
                font-size: 12px;
                font-weight: 600;
                padding: 3px 12px;
                border-radius: 10px;
                background-color: rgba(148, 163, 184, 0.12);
                border: 1px solid rgba(148, 163, 184, 0.3);
            """)
        else:
            # Démarrer ou reprendre la lecture
            is_start_of_round = self._current_round_elapsed == 0 and self._state == "countdown"
            if is_start_of_round:
                self.player.seek_ratio(0.0)
                self._apply_temporary_volume(0)

            self.player.play()

            if self._is_active_page:
                self._game_timer.start(1000)
                if is_start_of_round:
                    self._start_fade_in(2.0)
                elif self._is_fading_in and hasattr(self, "_fade_in_timer"):
                    self._fade_in_start_time = time.time() - getattr(self, "_fade_in_paused_elapsed", 0.0)
                    self._fade_in_timer.start(50)
                elif self._is_fading and hasattr(self, "_fade_timer"):
                    self._fade_start_time = time.time() - getattr(self, "_fade_paused_elapsed", 0.0)
                    self._fade_timer.start(50)

            self.btn_play_pause.setText("⏸")
            if self._state == "countdown":
                self.lbl_status_badge.setText(tr("blind_test.status_searching"))
                self.lbl_status_badge.setStyleSheet("""
                    color: #38BDF8;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 3px 12px;
                    border-radius: 10px;
                    background-color: rgba(56, 189, 248, 0.12);
                    border: 1px solid rgba(56, 189, 248, 0.3);
                """)
            elif self._state == "revealed":
                self.lbl_status_badge.setText(tr("blind_test.status_revealed", remain=self._reveal_remain))
                self.lbl_status_badge.setStyleSheet("""
                    color: #4ADE80;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 3px 12px;
                    border-radius: 10px;
                    background-color: rgba(74, 222, 128, 0.12);
                    border: 1px solid rgba(74, 222, 128, 0.3);
                """)

    def _on_track_changed(self, track: TrackRecord | None) -> None:
        """Appelé lors d'un changement de piste dans le PlayerService."""
        if self._is_active_page:
            self._start_round_for_track(track, auto_play=self.player.is_playing)

    def _on_playback_state_changed(self, state: str) -> None:
        is_playing = state == "playing"
        self.btn_play_pause.setText("⏸" if is_playing else "▶")
        if not is_playing:
            self._game_timer.stop()
        elif self._is_active_page and self._state != "idle":
            self._game_timer.start(1000)

    def _reset_to_empty_state(self) -> None:
        self._state = "idle"
        self._game_timer.stop()
        self._stop_fade_out()
        self._stop_fade_in()
        self.lbl_countdown.setVisible(False)
        self.lbl_cover.setPixmap(get_default_cover_pixmap())
        self.cover_opacity.setOpacity(0.3)
        self.lbl_title.setText(tr("blind_test.no_track"))
        self.lbl_artist_album.setText("")
        if hasattr(self, "lbl_file_name"):
            self.lbl_file_name.setText("")
            self.lbl_file_name.setVisible(False)
        self.lbl_status_badge.setText(tr("blind_test.no_track"))
        self.btn_reveal.setEnabled(False)
        self.round_progress.setValue(0)
        self._update_session_progress()

    # -------------------------------------------------------------------------
    # Gestion du volume et effets visuels
    # -------------------------------------------------------------------------

    def _toggle_mute(self) -> None:
        self.player.toggle_mute()

    def _on_volume_changed(self, val: int) -> None:
        self._nominal_volume = val
        self.player.set_volume(val)
        self.lbl_volume.setText(f"{val}%")

    def _on_player_volume_changed(self, vol: int, muted: bool) -> None:
        if not self._is_fading and not getattr(self, "_is_fading_in", False):
            self._nominal_volume = vol
        self.slider_volume.blockSignals(True)
        self.slider_volume.setValue(vol)
        self.slider_volume.blockSignals(False)
        self.lbl_volume.setText(tr("player.btn_mute") if (muted or vol == 0) else f"{vol}%")
        self.btn_mute.setText("🔇" if (muted or vol == 0) else "🔊")

    def _populate_effects_combo(self) -> None:
        effects = [
            ("none", "Désactivé"),
            ("particles", "Particules"),
            ("waves", "Vagues"),
            ("stars", "Étoiles"),
            ("warp", "Warp"),
            ("warp_dynamic", "Warp dynamique"),
            ("aurora", "Aurore boréale"),
            ("bars", "Spectre"),
            ("bars_full", "Spectre plein"),
        ]
        self.combo_effect.blockSignals(True)
        self.combo_effect.clear()
        cfg = get_config_manager()
        cur_effect = cfg.get_visual_effect()
        sel_idx = 0
        for i, (key, label) in enumerate(effects):
            self.combo_effect.addItem(label, key)
            if key == cur_effect:
                sel_idx = i
        self.combo_effect.setCurrentIndex(sel_idx)
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

    # -------------------------------------------------------------------------
    # Alias et accesseurs de compatibilité pour les tests
    # -------------------------------------------------------------------------

    @property
    def countdown_label(self) -> ZoomFadeLabel:
        return self.lbl_countdown

    @property
    def btn_previous(self) -> QPushButton:
        return self.btn_prev

    @property
    def cover_label(self) -> QLabel:
        return self.lbl_cover

    @property
    def lbl_header_title(self) -> QLabel:
        return self.lbl_page_title

    @property
    def cover_opacity_effect(self) -> QGraphicsOpacityEffect:
        return self.cover_opacity

    @property
    def session_progress_label(self) -> QLabel:
        return self.lbl_session_progress

    @property
    def file_name_label(self) -> QLabel:
        return self.lbl_file_name

    @property
    def _is_revealed(self) -> bool:
        return self._state == "revealed"

    @property
    def _countdown_duration(self) -> int:
        return self._countdown_remain

    @property
    def _reveal_duration(self) -> int:
        return self._reveal_remain

    @property
    def _fade_duration_prop(self) -> int:
        return self._configured_fade

    @property
    def _is_fade_active(self) -> bool:
        return self._is_fading

    @property
    def _remaining_seconds(self) -> int:
        return self._countdown_remain if self._state == "countdown" else self._reveal_remain

    @_remaining_seconds.setter
    def _remaining_seconds(self, val: int) -> None:
        if self._state == "countdown":
            self._countdown_remain = val
        else:
            self._reveal_remain = val

    def _on_track_loaded(self, track: TrackRecord | None) -> None:
        self._start_round_for_track(track, auto_play=self.player.is_playing)

    def _tick(self) -> None:
        self._on_game_tick()

    def _on_state_changed(self, state: str) -> None:
        self._on_playback_state_changed(state)

    def retranslate_ui(self) -> None:
        """Met à jour les textes traduits lors d'un changement de langue."""
        self.lbl_page_title.setText("🎭  " + tr("blind_test.title"))
        self.lbl_effect_badge.setText(tr("player.visual_effect"))
        if hasattr(self, "btn_prev"):
            self.btn_prev.setText(tr("blind_test.btn_prev"))
        self.btn_reveal.setText(tr("blind_test.btn_reveal"))
        self.btn_next.setText(tr("blind_test.btn_next"))
        if self._state == "countdown":
            self.lbl_title.setText("❓  " + tr("blind_test.mystery_title"))
            self.lbl_artist_album.setText("👥  " + tr("blind_test.mystery_artist"))
            if hasattr(self, "lbl_file_name"):
                self.lbl_file_name.setText("📁  " + tr("blind_test.mystery_file"))
            self.lbl_status_badge.setText(tr("blind_test.status_searching"))
        elif self._state == "revealed":
            self.lbl_status_badge.setText(tr("blind_test.status_revealed", remain=self._reveal_remain))
        elif self._state == "idle":
            self._reset_to_empty_state()

        self._update_session_progress()
