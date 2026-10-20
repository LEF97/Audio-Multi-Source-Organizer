"""Fondus audio (entrée/sortie) du Blind Test."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from PySide6.QtWidgets import (
    QWidget,
)

if TYPE_CHECKING:
    _MixinBase = QWidget
else:
    _MixinBase = object


class BlindTestFadesMixin(_MixinBase):
    """Fondus audio (entrée/sortie) du Blind Test."""

    if TYPE_CHECKING:
        # Attributs de BlindTestView résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

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
            if hasattr(self, "effect_canvas") and self.effect_canvas:
                self.effect_canvas.update_audio_volume(self._nominal_volume, self.player.is_muted)

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
        if hasattr(self, "effect_canvas") and self.effect_canvas:
            self.effect_canvas.update_audio_volume(vol, self.player.is_muted)

    def _stop_fade_and_restore_volume(self) -> None:
        """Arrête les fondus et rétablit instantanément 100% du volume nominal."""
        self._stop_fade_out()
        self._stop_fade_in()
        if hasattr(self.player, "restore_volume"):
            self.player.restore_volume()
        if hasattr(self, "effect_canvas") and self.effect_canvas:
            self.effect_canvas.update_audio_volume(self._nominal_volume, self.player.is_muted)
