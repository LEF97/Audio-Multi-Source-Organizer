"""Logique de transport commune au lecteur et à la mini-barre de la playlist (mixin de vue)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtWidgets import QPushButton, QWidget

from amso.core.i18n import tr
from amso.services.player_types import RepeatMode
from amso.ui.models import format_duration
from amso.ui.styles import active_button_qss, icon_button_qss
from amso.ui.views.cover_helper import load_cover_async

if TYPE_CHECKING:
    _MixinBase = QWidget
else:
    _MixinBase = object


class TransportViewMixin(_MixinBase):
    """Seek, volume, play/pause, aléatoire et répétition partagés par PlayerView et PlaylistView.

    Les vues fixent `_transport_*` et surchargent les méthodes `update_*` pour leurs extras
    (en appelant `super()`).
    """

    if TYPE_CHECKING:
        # Les widgets (btn_*, slider_*, lbl_*) et `player` sont fournis par la vue (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    _transport_btn_radius: int = 6
    _transport_btn_font: int = 14
    _transport_cover_size: int = 320
    _transport_cover_radius: int = 12

    def _style_transport_button(self, btn: QPushButton, font_size: int | None = None) -> None:
        """Applique le style bouton-icône avec le rayon propre à la vue."""
        size = font_size if font_size is not None else self._transport_btn_font
        btn.setStyleSheet(icon_button_qss(self._transport_btn_radius, size))

    def _style_transport_active(self, btn: QPushButton) -> None:
        """Applique le style « actif » (aléatoire, répétition)."""
        btn.setStyleSheet(active_button_qss(self._transport_btn_radius, self._transport_btn_font))

    def _connect_transport_signals(self) -> None:
        """Connecte les signaux du PlayerService et les contrôles de transport."""
        self.player.track_changed.connect(self.update_track_info)
        self.player.state_changed.connect(self.update_playback_state)
        self.player.position_changed.connect(self.update_position)
        self.player.volume_changed.connect(self.update_volume)
        self.player.shuffle_changed.connect(self.update_shuffle_ui)
        self.player.repeat_changed.connect(self.update_repeat_ui)

        self.btn_play_pause.clicked.connect(self.player.toggle_play_pause)
        self.btn_stop.clicked.connect(self.player.stop)
        self.btn_next.clicked.connect(self.player.next)
        self.btn_prev.clicked.connect(self.player.previous)
        self.btn_shuffle.clicked.connect(self.player.toggle_shuffle)
        self.btn_repeat.clicked.connect(self.player.toggle_repeat)
        self.btn_mute.clicked.connect(self.player.toggle_mute)

        self.slider_seek.sliderPressed.connect(lambda: self.player.set_seeking(True))
        self.slider_seek.sliderReleased.connect(self._on_seek_released)
        self.slider_seek.sliderMoved.connect(self._on_seek_moved)

        self.slider_volume.valueChanged.connect(self.player.set_volume)

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

    def update_playback_state(self, state: str) -> None:
        """Met à jour l'icône Play/Pause et recharge la pochette à la lecture."""
        try:
            if state == "playing":
                self.btn_play_pause.setText("⏸")
                self.btn_play_pause.setToolTip(tr("player.btn_pause"))
                if self.player.current_track:
                    load_cover_async(
                        self.player.current_track,
                        size=self._transport_cover_size,
                        radius=self._transport_cover_radius,
                        callback=self._on_cover_loaded,
                        force_check=True,
                    )
            else:
                self.btn_play_pause.setText("▶")
                self.btn_play_pause.setToolTip(tr("player.btn_play"))
        except RuntimeError:
            pass

    def update_position(self, current_ms: int, total_ms: int, ratio: float) -> None:
        """Met à jour les temps et la barre de progression."""
        try:
            self.lbl_time_cur.setText(format_duration(current_ms / 1000.0))
            if total_ms > 0:
                self.lbl_time_total.setText(format_duration(total_ms / 1000.0))
            val = int(ratio * 1000)
            self.slider_seek.blockSignals(True)
            self.slider_seek.setValue(val)
            self.slider_seek.blockSignals(False)
        except RuntimeError:
            pass

    def update_volume(self, volume: int, is_muted: bool) -> None:
        """Met à jour le curseur de volume et l'icône de sourdine."""
        try:
            self.slider_volume.blockSignals(True)
            self.slider_volume.setValue(volume)
            self.slider_volume.blockSignals(False)
            self.btn_mute.setText("🔇" if is_muted or volume == 0 else "🔊")
        except RuntimeError:
            pass

    def update_shuffle_ui(self, active: bool) -> None:
        """Met en valeur le bouton aléatoire si actif."""
        if active:
            self._style_transport_active(self.btn_shuffle)
        else:
            self._style_transport_button(self.btn_shuffle)

    def update_repeat_ui(self, mode: int) -> None:
        """Met à jour l'icône et le style du mode de répétition."""
        if mode == RepeatMode.OFF:
            self.btn_repeat.setText("🔁")
            self._style_transport_button(self.btn_repeat)
        elif mode == RepeatMode.ALL:
            self.btn_repeat.setText("🔁")
            self._style_transport_active(self.btn_repeat)
        elif mode == RepeatMode.ONE:
            self.btn_repeat.setText("🔂")
            self._style_transport_active(self.btn_repeat)
