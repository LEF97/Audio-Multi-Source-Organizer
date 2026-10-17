"""Vue plein écran du Lecteur Audio pour AMSO."""

from __future__ import annotations

import os

from PySide6.QtCore import QFileSystemWatcher, Qt, QTimer, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from amso.core.config import get_config_manager
from amso.core.database import TrackRecord
from amso.core.i18n import tr
from amso.services.player_service import PlayerService, RepeatMode
from amso.ui.models import format_duration
from amso.ui.views.cover_helper import (
    get_default_cover_pixmap,
    load_cover_async,
)
from amso.ui.views.visual_effects import VisualEffectWidget


class EffectContainer(QWidget):
    """Conteneur qui maintient le VisualEffectWidget redimensionné en arrière-plan."""

    def __init__(self, effect_canvas: VisualEffectWidget, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.effect_canvas = effect_canvas
        self.effect_canvas.setParent(self)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.effect_canvas.setGeometry(0, 0, self.width(), self.height())
        self.effect_canvas.lower()


class ClickableSlider(QSlider):
    """QSlider permettant de cliquer directement à n'importe quel endroit de la barre."""

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            val = self.minimum() + ((self.maximum() - self.minimum()) * event.position().x()) / max(1, self.width())
            self.setValue(int(round(val)))
            self.sliderMoved.emit(self.value())
        super().mousePressEvent(event)


class PlayerView(QWidget):
    """Page dédiée au Lecteur Audio grand format avec jaquette et contrôles complets."""

    effect_changed = Signal(str)

    def __init__(self, player_service: PlayerService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.player = player_service

        self._setup_ui()
        self._connect_signals()

        # Surveillance dynamique du dossier pour recharger la pochette si folder.png change
        self._folder_watcher = QFileSystemWatcher(self)
        self._folder_watcher.directoryChanged.connect(self._on_current_folder_changed)
        self._folder_watch_timer = QTimer(self)
        self._folder_watch_timer.setSingleShot(True)
        self._folder_watch_timer.setInterval(300)
        self._folder_watch_timer.timeout.connect(self._on_folder_change_debounced)

        # État initial
        self.update_track_info(self.player.current_track)
        self.update_playback_state("playing" if self.player.is_playing else "stopped")

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

        self.lbl_page_title = QLabel(tr("player.title"))
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

        # Toile d'effet visuel dynamique en fond
        cfg = get_config_manager()
        initial_effect = cfg.get_visual_effect()
        self.effect_canvas = VisualEffectWidget(initial_effect)

        # Zone défilante centrale pour garantir la lisibilité sur toutes résolutions
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area = scroll

        center_container = EffectContainer(self.effect_canvas)
        self.center_container = center_container
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
        self.slider_seek.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background-color: #282C37;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background-color: #0284C7;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background-color: #F8FAFC;
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background-color: #38BDF8;
                transform: scale(1.2);
            }
        """)
        seek_layout.addWidget(self.slider_seek, 1)

        self.lbl_time_total = QLabel("00:00")
        self.lbl_time_total.setStyleSheet("color: #94A3B8; font-size: 12px; font-family: monospace;")
        seek_layout.addWidget(self.lbl_time_total)

        card_layout.addWidget(seek_container)

        # 4. Commandes principales de lecture
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(12)
        ctrl_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_shuffle = QPushButton("🔀")
        self.btn_shuffle.setFixedSize(36, 36)
        self.btn_shuffle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_shuffle.setToolTip(tr("player.btn_shuffle"))
        self._style_icon_button(self.btn_shuffle)
        ctrl_layout.addWidget(self.btn_shuffle)

        self.btn_prev = QPushButton("⏮")
        self.btn_prev.setFixedSize(40, 40)
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.setToolTip(tr("player.btn_previous"))
        self._style_icon_button(self.btn_prev, font_size=14)
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
        self._style_icon_button(self.btn_stop, font_size=12)
        ctrl_layout.addWidget(self.btn_stop)

        self.btn_next = QPushButton("⏭")
        self.btn_next.setFixedSize(40, 40)
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.setToolTip(tr("player.btn_next"))
        self._style_icon_button(self.btn_next, font_size=14)
        ctrl_layout.addWidget(self.btn_next)

        self.btn_repeat = QPushButton("🔁")
        self.btn_repeat.setFixedSize(36, 36)
        self.btn_repeat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_repeat.setToolTip(tr("player.btn_repeat"))
        self._style_icon_button(self.btn_repeat)
        ctrl_layout.addWidget(self.btn_repeat)

        card_layout.addLayout(ctrl_layout)

        # 5. Contrôle du volume sonore
        vol_container = QWidget()
        vol_layout = QHBoxLayout(vol_container)
        vol_layout.setContentsMargins(0, 2, 0, 0)
        vol_layout.setSpacing(8)
        vol_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_mute = QPushButton("🔊")
        self.btn_mute.setFixedSize(30, 30)
        self.btn_mute.setCursor(Qt.CursorShape.PointingHandCursor)
        self._style_icon_button(self.btn_mute, font_size=13)
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
            QSlider::handle:horizontal:hover {
                background-color: #38BDF8;
            }
        """)
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
        # Signaux émis par le PlayerService
        self.player.track_changed.connect(self.update_track_info)
        self.player.state_changed.connect(self.update_playback_state)
        self.player.position_changed.connect(self.update_position)
        self.player.volume_changed.connect(self.update_volume)
        self.player.shuffle_changed.connect(self.update_shuffle_ui)
        self.player.repeat_changed.connect(self.update_repeat_ui)

        # Contrôles utilisateur
        self.btn_play_pause.clicked.connect(self.player.toggle_play_pause)
        self.btn_stop.clicked.connect(self.player.stop)
        self.btn_next.clicked.connect(self.player.next)
        self.btn_prev.clicked.connect(self.player.previous)
        self.btn_shuffle.clicked.connect(self.player.toggle_shuffle)
        self.btn_repeat.clicked.connect(self.player.toggle_repeat)
        self.btn_mute.clicked.connect(self.player.toggle_mute)

        # Seekbar
        self.slider_seek.sliderPressed.connect(lambda: self.player.set_seeking(True))
        self.slider_seek.sliderReleased.connect(self._on_seek_released)
        self.slider_seek.sliderMoved.connect(self._on_seek_moved)

        # Volume
        self.slider_volume.valueChanged.connect(self.player.set_volume)

        # Synchronisation de l'état initial
        self.update_shuffle_ui(self.player.is_shuffle)
        self.update_repeat_ui(self.player.repeat_mode)
        self.update_volume(self.player.volume, self.player.is_muted)
        if self.player.current_track:
            self.update_track_info(self.player.current_track)

    def _on_seek_released(self) -> None:
        val = self.slider_seek.value()
        ratio = val / 1000.0
        self.player.seek_ratio(ratio)
        self.player.set_seeking(False)

    def _on_seek_moved(self, value: int) -> None:
        track = self.player.current_track
        if track and track.duration_seconds:
            curr_sec = (value / 1000.0) * track.duration_seconds
            self.lbl_time_cur.setText(format_duration(curr_sec))

    def _on_cover_loaded(self, path: str, pixmap: QPixmap) -> None:
        """Appelé dès que la pochette asynchrone a fini de charger."""
        if getattr(self, "_displayed_track_path", None) == path:
            self._current_pixmap = pixmap
            self._update_scaled_cover()

    def _on_current_folder_changed(self, path: str) -> None:
        """Appelé dès qu'un fichier (ex: folder.png) est ajouté ou modifié dans le dossier courant."""
        if hasattr(self, "_folder_watch_timer"):
            self._folder_watch_timer.start()

    def _on_folder_change_debounced(self) -> None:
        """Recharge la pochette du morceau en cours après modification du dossier."""
        if self.player.current_track:
            load_cover_async(
                self.player.current_track,
                size=320,
                radius=12,
                callback=self._on_cover_loaded,
                force_check=True,
            )

    def _update_scaled_cover(self) -> None:
        """Applique l'image actuelle à la taille exacte du lbl_cover avec anticrénelage fluide."""
        pixmap = getattr(self, "_current_pixmap", None)
        size = self.lbl_cover.width()
        if not pixmap or pixmap.isNull():
            pixmap = get_default_cover_pixmap(size, radius=12)
            self._current_pixmap = pixmap
            self.lbl_cover.setPixmap(pixmap)
            return

        if pixmap.width() != size or pixmap.height() != size:
            scaled = pixmap.scaled(
                size,
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.lbl_cover.setPixmap(scaled)
        else:
            self.lbl_cover.setPixmap(pixmap)

    def _adjust_layout(self) -> None:
        """Ajuste dynamiquement la hauteur de la pochette et décale les blocs verticaux
        pour garantir un affichage intégral (titre et auteur multi-lignes, commandes,
        curseur de volume) sans coupure ni défilement superflu."""
        if not hasattr(self, "scroll_area") or not hasattr(self, "card"):
            return

        viewport_h = self.scroll_area.viewport().height()
        if viewport_h <= 100:
            top_h = self.top_bar.height() if hasattr(self, "top_bar") and self.top_bar.height() > 0 else 44
            viewport_h = max(300, self.height() - top_h)

        c_margins = self.center_layout.contentsMargins()
        net_available = viewport_h - c_margins.top() - c_margins.bottom()

        # Hauteur requise pour les composants de la carte hors pochette
        card_hint = self.card.sizeHint().height()
        current_cover_h = self.lbl_cover.height()
        non_cover_h = max(160, card_hint - current_cover_h)

        # Taille idéale de la pochette carrée
        target_size = net_available - non_cover_h - 4
        # Borner entre une taille minimale lisible (150px) et maximale (300px)
        target_size = max(150, min(300, target_size))

        if target_size != self.lbl_cover.width():
            self.lbl_cover.setFixedSize(target_size, target_size)
            self._update_scaled_cover()

    def update_track_info(self, track: TrackRecord | None) -> None:
        """Met à jour l'affichage avec la piste en cours de lecture de façon instantanée et non-bloquante."""
        track_path = (track.source_path or track.source_ref or track.folder_path or "") if track else ""
        self._displayed_track_path = track_path

        # Mise à jour de la surveillance du dossier contenant la piste
        if hasattr(self, "_folder_watcher"):
            existing = self._folder_watcher.directories()
            if existing:
                self._folder_watcher.removePaths(existing)

            folder_to_watch: str | None = None
            if track:
                if track.folder_path and os.path.isdir(track.folder_path):
                    folder_to_watch = track.folder_path
                elif track.source_path:
                    parent_dir = os.path.dirname(track.source_path)
                    if os.path.isdir(parent_dir):
                        folder_to_watch = parent_dir
            if folder_to_watch:
                self._folder_watcher.addPath(folder_to_watch)

        if hasattr(self, "effect_canvas") and self.effect_canvas:
            self.effect_canvas.set_track(track)

        # Chargement immédiat (en cache) ou asynchrone (défaut puis cover) sans bloquer
        pixmap = load_cover_async(track, size=320, radius=12, callback=self._on_cover_loaded, force_check=True)
        self._current_pixmap = pixmap

        if not track:
            self.lbl_title.setText(tr("player.no_track"))
            self.lbl_title.setToolTip("")
            self.lbl_artist_album.setText("")
            self.lbl_artist_album.setToolTip("")
            self.lbl_file_name.setText("")
            self.lbl_file_name.setToolTip("")
            self.lbl_file_name.setVisible(False)
            self.lbl_badge.setVisible(False)
            self.lbl_time_cur.setText("00:00")
            self.lbl_time_total.setText("00:00")
            self.slider_seek.setValue(0)
            self._adjust_layout()
            self._update_scaled_cover()
            return

        title_text = track.title or track.file_name or tr("track.untitled")
        self.lbl_title.setText(title_text)
        self.lbl_title.setToolTip(title_text)

        artist_part = track.artist or tr("track.unknown_artist")
        album_part = f" — {track.album}" if track.album else ""
        sub_text = f"{artist_part}{album_part}"
        self.lbl_artist_album.setText(sub_text)
        self.lbl_artist_album.setToolTip(sub_text)

        # Nom du fichier (entre auteur/album et le badge de format)
        file_name_text = track.file_name or (
            os.path.basename(track.source_path.replace("\\", "/")) if track.source_path else ""
        )
        if file_name_text:
            self.lbl_file_name.setText(file_name_text)
            self.lbl_file_name.setToolTip(file_name_text)
            self.lbl_file_name.setVisible(True)
        else:
            self.lbl_file_name.setText("")
            self.lbl_file_name.setToolTip("")
            self.lbl_file_name.setVisible(False)

        # Badge de format
        details = []
        if track.format:
            details.append(track.format.upper())
        if track.bitrate:
            details.append(f"{track.bitrate} kbps")
        if track.sample_rate:
            details.append(f"{track.sample_rate / 1000:.1f} kHz")

        if details:
            self.lbl_badge.setText(" • ".join(details))
            self.lbl_badge.setVisible(True)
        else:
            self.lbl_badge.setVisible(False)

        total_sec = track.duration_seconds or 0
        self.lbl_time_total.setText(format_duration(total_sec))

        # Recalcul de l'ajustement vertical pour s'adapter aux textes (titre/auteur sur plusieurs lignes)
        self._adjust_layout()
        self._update_scaled_cover()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._adjust_layout()
        if hasattr(self, "effect_canvas"):
            self.effect_canvas.showEvent(event)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._adjust_layout()

    def hideEvent(self, event) -> None:
        super().hideEvent(event)
        if hasattr(self, "effect_canvas"):
            self.effect_canvas.hideEvent(event)

    def _populate_effects_combo(self) -> None:
        """Remplit le menu déroulant des effets visuels."""
        current_data = self.effect_canvas.effect_type if hasattr(self, "effect_canvas") else "particles"
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
        """Appelé lors du changement de sélection dans la combobox de la barre supérieure."""
        key = self.combo_effect.itemData(index)
        if key:
            self.set_effect_type(key)

    def set_effect_type(self, effect: str) -> None:
        """Applique l'effet visuel, met à jour la combobox et sauvegarde la préférence."""
        if hasattr(self, "effect_canvas"):
            self.effect_canvas.set_effect_type(effect)

        # Synchronisation combobox sans boucle infinie
        if hasattr(self, "combo_effect"):
            self.combo_effect.blockSignals(True)
            idx = self.combo_effect.findData(effect)
            if idx >= 0 and self.combo_effect.currentIndex() != idx:
                self.combo_effect.setCurrentIndex(idx)
            self.combo_effect.blockSignals(False)

        cfg = get_config_manager()
        cfg.set_visual_effect(effect)
        self.effect_changed.emit(effect)

    @property
    def effect_type(self) -> str:
        """Retourne le type d'effet visuel actuellement actif dans le lecteur."""
        if hasattr(self, "effect_canvas") and self.effect_canvas:
            return self.effect_canvas.effect_type
        return "particles"

    def update_playback_state(self, state: str) -> None:
        """Met à jour l'icône et l'état du bouton Play/Pause ainsi que l'animation."""
        if hasattr(self, "effect_canvas"):
            self.effect_canvas.set_playback_state(state)
        if state == "playing":
            self.btn_play_pause.setText("⏸")
            self.btn_play_pause.setToolTip(tr("player.btn_pause"))
            if self.player.current_track:
                load_cover_async(
                    self.player.current_track,
                    size=320,
                    radius=12,
                    callback=self._on_cover_loaded,
                    force_check=True,
                )
        else:
            self.btn_play_pause.setText("▶")
            self.btn_play_pause.setToolTip(tr("player.btn_play"))

    def update_position(self, current_ms: int, total_ms: int, ratio: float) -> None:
        """Met à jour la position courante et la barre de progression."""
        self.lbl_time_cur.setText(format_duration(current_ms / 1000.0))
        if total_ms > 0:
            self.lbl_time_total.setText(format_duration(total_ms / 1000.0))
        val = int(ratio * 1000)
        self.slider_seek.blockSignals(True)
        self.slider_seek.setValue(val)
        self.slider_seek.blockSignals(False)
        if hasattr(self, "effect_canvas") and self.effect_canvas:
            self.effect_canvas.update_audio_time(current_ms, ratio)

    def update_volume(self, volume: int, is_muted: bool) -> None:
        """Met à jour le curseur de volume et l'icône de sourdine."""
        self.slider_volume.blockSignals(True)
        self.slider_volume.setValue(volume)
        self.slider_volume.blockSignals(False)

        if hasattr(self, "effect_canvas") and self.effect_canvas:
            self.effect_canvas.update_audio_volume(volume, is_muted)

        if is_muted or volume == 0:
            self.btn_mute.setText("🔇")
            self.lbl_volume.setText(tr("player.btn_mute"))
        else:
            self.btn_mute.setText("🔊")
            self.lbl_volume.setText(f"{volume}%")

    def update_shuffle_ui(self, active: bool) -> None:
        """Met en valeur le bouton aléatoire si actif."""
        if active:
            self.btn_shuffle.setStyleSheet("""
                background-color: #0284C7;
                color: #FFFFFF;
                border: 1px solid #38BDF8;
                border-radius: 6px;
                font-size: 14px;
            """)
        else:
            self._style_icon_button(self.btn_shuffle)

    def update_repeat_ui(self, mode: int) -> None:
        """Met à jour l'icône du mode de répétition."""
        if mode == RepeatMode.OFF:
            self.btn_repeat.setText("🔁")
            self._style_icon_button(self.btn_repeat)
        elif mode == RepeatMode.ALL:
            self.btn_repeat.setText("🔁")
            self.btn_repeat.setStyleSheet("""
                background-color: #0284C7;
                color: #FFFFFF;
                border: 1px solid #38BDF8;
                border-radius: 6px;
                font-size: 14px;
            """)
        elif mode == RepeatMode.ONE:
            self.btn_repeat.setText("🔂")
            self.btn_repeat.setStyleSheet("""
                background-color: #0284C7;
                color: #FFFFFF;
                border: 1px solid #38BDF8;
                border-radius: 6px;
                font-size: 14px;
            """)

    def retranslate_ui(self) -> None:
        """Met à jour l'ensemble des textes et infobulles du lecteur selon la langue active."""
        self.lbl_page_title.setText(tr("player.title"))
        if hasattr(self, "lbl_effect_badge"):
            self.lbl_effect_badge.setText(tr("player.visual_effect"))
        if hasattr(self, "combo_effect"):
            self._populate_effects_combo()

        if not self.player.current_track:
            self.lbl_title.setText(tr("player.no_track"))
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
        if self.player.is_muted or self.player.volume == 0:
            self.lbl_volume.setText(tr("player.btn_mute"))
