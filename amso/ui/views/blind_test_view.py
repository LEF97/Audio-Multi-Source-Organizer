"""Vue dédiée au mode Blind Test interactif pour AMSO."""

from __future__ import annotations

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QHideEvent, QPixmap
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
    """QLabel animé effectuant un zoom et un fondu à chaque changement de valeur."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)

        self._anim_opacity = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._anim_opacity.setDuration(800)
        self._anim_opacity.setStartValue(1.0)
        self._anim_opacity.setEndValue(0.4)
        self._anim_opacity.setEasingCurve(QEasingCurve.Type.OutQuad)

    def trigger_tick_animation(self) -> None:
        """Déclenche l'animation de pulse et fondu à chaque seconde."""
        self._anim_opacity.stop()
        self._opacity_effect.setOpacity(1.0)
        self._anim_opacity.start()

    def show_number(self, val: int) -> None:
        """Affiche le nombre et déclenche l'animation de zoom et fondu."""
        self.setText(str(val))
        self.trigger_tick_animation()


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
        self._countdown_remain: int = self._configured_countdown
        self._reveal_remain: int = self._configured_reveal
        self._total_round_duration: int = self._countdown_remain + self._reveal_remain
        self._current_round_elapsed: int = 0
        self._is_active_page: bool = False
        self.current_effect: str = cfg.get_visual_effect()

        self._setup_ui()
        self._connect_signals()

        # Timer d'horloge de seconde en seconde pour le Blind Test
        self._game_timer = QTimer(self)
        self._game_timer.setInterval(1000)
        self._game_timer.timeout.connect(self._on_game_tick)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. En-tête de la page
        top_bar = QFrame()
        top_bar.setObjectName("topBarFrame")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 10, 20, 10)

        self.lbl_page_title = QLabel("🎭  " + tr("blind_test.title"))
        self.lbl_page_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        top_layout.addWidget(self.lbl_page_title)
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

        card_layout.addWidget(info_container)

        # 4. Commandes de jeu du Blind Test
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(12)
        ctrl_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Bouton Play / Pause (pour figer le chrono)
        self.btn_play_pause = QPushButton("⏸")
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
                padding: 0 20px;
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
                padding: 0 16px;
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

        # Contrôle du volume
        vol_container = QWidget()
        vol_layout = QHBoxLayout(vol_container)
        vol_layout.setContentsMargins(0, 4, 0, 0)
        vol_layout.setSpacing(8)
        vol_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_mute = QPushButton("🔊")
        self.btn_mute.setFixedSize(30, 30)
        self.btn_mute.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mute.setStyleSheet("""
            QPushButton {
                background-color: #20242D;
                color: #CBD5E1;
                border: 1px solid #282C37;
                border-radius: 6px;
                font-size: 13px;
            }
        """)
        self.btn_mute.clicked.connect(self._toggle_mute)
        vol_layout.addWidget(self.btn_mute)

        self.slider_volume = ClickableSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(self.player.volume)
        self.slider_volume.setFixedWidth(140)
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
        """)
        self.slider_volume.valueChanged.connect(self._on_volume_changed)
        vol_layout.addWidget(self.slider_volume)

        self.lbl_volume = QLabel(f"{self.player.volume}%")
        self.lbl_volume.setStyleSheet("color: #94A3B8; font-size: 12px; min-width: 38px;")
        vol_layout.addWidget(self.lbl_volume)

        card_layout.addWidget(vol_container)

        center_layout.addWidget(self.card)
        scroll.setWidget(center_container)
        layout.addWidget(scroll, 1)

        self._populate_effects_combo()
        self.combo_effect.currentIndexChanged.connect(self._on_effect_combo_changed)

    def _connect_signals(self) -> None:
        self.player.track_changed.connect(self._on_track_changed)
        self.player.state_changed.connect(self._on_playback_state_changed)
        self.player.volume_changed.connect(self._on_player_volume_changed)

    def showEvent(self, event) -> None:
        """Déclenché lorsque l'utilisateur affiche la page Blind Test."""
        super().showEvent(event)
        self._is_active_page = True

        # Synchroniser l'effet visuel actif avec le ConfigManager
        cfg = get_config_manager()
        eff = cfg.get_visual_effect()
        self.set_effect_type(eff)

        # Si le lecteur est arrêté ou pas de manche en cours, lancer une manche
        if self.player.current_track:
            self._start_round_for_track(self.player.current_track)
            if not self.player.is_playing:
                self.player.play()
        else:
            self._reset_to_empty_state()

    def hideEvent(self, event: QHideEvent) -> None:
        """Déclenché lorsque l'utilisateur quitte la page Blind Test."""
        self._is_active_page = False
        # Stopper le timer automatique pour ne pas forcer de saut de piste sur les autres vues
        self._game_timer.stop()
        try:
            super().hideEvent(event)
        except Exception:
            pass

    def set_durations(self, countdown_seconds: int, reveal_seconds: int) -> None:
        """Met à jour les durées configurées du Blind Test."""
        self._configured_countdown = countdown_seconds
        self._configured_reveal = reveal_seconds
        self._countdown_remain = countdown_seconds
        self._reveal_remain = reveal_seconds
        self._total_round_duration = countdown_seconds + reveal_seconds

    def _start_round_for_track(self, track: TrackRecord | None) -> None:
        """Initialise et lance une manche de Blind Test sur la piste fournie."""
        if not track:
            self._reset_to_empty_state()
            return

        self._countdown_remain = self._configured_countdown
        self._reveal_remain = self._configured_reveal
        self._total_round_duration = self._countdown_remain + self._reveal_remain
        self._current_round_elapsed = 0

        self._state = "countdown"
        self.lbl_countdown.setVisible(True)
        self.lbl_countdown.setText(str(self._countdown_remain))
        self.lbl_countdown.trigger_tick_animation()

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

        self.btn_reveal.setEnabled(True)
        self.round_progress.setValue(0)

        # Précharger l'image de couverture en arrière-plan sans l'afficher encore
        pix = load_cover_async(track, size=280, radius=16, callback=self._on_cover_loaded)
        if pix and not pix.isNull():
            self.lbl_cover.setPixmap(pix)

        # Assurer la lecture
        if self._is_active_page:
            self._game_timer.start(1000)

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
            else:
                # Fin de la phase de découverte : passage automatique à la piste suivante !
                self._game_timer.stop()
                self.player.next()

    def _trigger_reveal(self) -> None:
        """Déclenche l'animation de révélation (Fade-In de la pochette et textes)."""
        self._state = "revealed"
        self.lbl_countdown.setVisible(False)
        self.btn_reveal.setEnabled(False)

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

        # Révélation des vrais titres et artistes
        track = self.player.current_track
        if track:
            title_str = track.title or track.file_name or tr("track.untitled")
            art_str = track.artist or tr("track.unknown_artist")
            if track.album:
                art_str += f" — {track.album}"
            self.lbl_title.setText(title_str)
            self.lbl_artist_album.setText(art_str)

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

    def _on_reveal_clicked(self) -> None:
        """Révèle immédiatement la piste si les joueurs ont trouvé avant la fin des 20s."""
        if self._state == "countdown":
            self._trigger_reveal()

    def _on_next_track_clicked(self) -> None:
        """Passe immédiatement au titre suivant."""
        self._game_timer.stop()
        self.player.next()

    def _on_play_pause_clicked(self) -> None:
        """Met en pause ou reprend la lecture et le décompte."""
        if self.player.is_playing:
            self.player.pause()
            self._game_timer.stop()
            self.btn_play_pause.setText("▶")
            self.lbl_status_badge.setText(tr("blind_test.status_paused"))
        else:
            self.player.play()
            if self._is_active_page:
                self._game_timer.start(1000)
            self.btn_play_pause.setText("⏸")
            if self._state == "countdown":
                self.lbl_status_badge.setText(tr("blind_test.status_searching"))
            elif self._state == "revealed":
                self.lbl_status_badge.setText(tr("blind_test.status_revealed", remain=self._reveal_remain))

    def _on_track_changed(self, track: TrackRecord | None) -> None:
        """Appelé lors d'un changement de piste dans le PlayerService."""
        if self._is_active_page:
            self._start_round_for_track(track)

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
        self.lbl_countdown.setVisible(False)
        self.lbl_cover.setPixmap(get_default_cover_pixmap())
        self.cover_opacity.setOpacity(0.3)
        self.lbl_title.setText(tr("blind_test.no_track"))
        self.lbl_artist_album.setText("")
        self.lbl_status_badge.setText(tr("blind_test.no_track"))
        self.btn_reveal.setEnabled(False)
        self.round_progress.setValue(0)

    # -------------------------------------------------------------------------
    # Gestion du volume et effets visuels
    # -------------------------------------------------------------------------

    def _toggle_mute(self) -> None:
        self.player.toggle_mute()

    def _on_volume_changed(self, val: int) -> None:
        self.player.set_volume(val)
        self.lbl_volume.setText(f"{val}%")

    def _on_player_volume_changed(self, vol: int, muted: bool) -> None:
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
    def cover_label(self) -> QLabel:
        return self.lbl_cover

    @property
    def lbl_header_title(self) -> QLabel:
        return self.lbl_page_title

    @property
    def cover_opacity_effect(self) -> QGraphicsOpacityEffect:
        return self.cover_opacity

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
    def _remaining_seconds(self) -> int:
        return self._countdown_remain if self._state == "countdown" else self._reveal_remain

    @_remaining_seconds.setter
    def _remaining_seconds(self, val: int) -> None:
        if self._state == "countdown":
            self._countdown_remain = val
        else:
            self._reveal_remain = val

    def _on_track_loaded(self, track: TrackRecord | None) -> None:
        self._start_round_for_track(track)

    def _tick(self) -> None:
        self._on_game_tick()

    def _on_state_changed(self, state: str) -> None:
        self._on_playback_state_changed(state)

    def retranslate_ui(self) -> None:
        """Met à jour les textes traduits lors d'un changement de langue."""
        self.lbl_page_title.setText("🎭  " + tr("blind_test.title"))
        self.lbl_effect_badge.setText(tr("player.visual_effect"))
        self.btn_reveal.setText(tr("blind_test.btn_reveal"))
        self.btn_next.setText(tr("blind_test.btn_next"))
        if self._state == "countdown":
            self.lbl_title.setText("❓  " + tr("blind_test.mystery_title"))
            self.lbl_artist_album.setText("👥  " + tr("blind_test.mystery_artist"))
            self.lbl_status_badge.setText(tr("blind_test.status_searching"))
        elif self._state == "revealed":
            self.lbl_status_badge.setText(tr("blind_test.status_revealed", remain=self._reveal_remain))
        elif self._state == "idle":
            self._reset_to_empty_state()
