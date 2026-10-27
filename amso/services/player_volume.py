"""Gestion du volume et du mode muet (mixin de PlayerService)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from amso.core.config import get_config_manager

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from amso.services.player_types import PlayerStateBase

    _MixinBase = PlayerStateBase
else:
    _MixinBase = object


class PlayerVolumeMixin(_MixinBase):
    """Commandes et application du volume sonore et mode muet."""

    if TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any: ...

    def set_volume(self, volume: int) -> None:
        """Définit le volume sonore (0 à 100)."""
        self._volume = max(0, min(100, volume))
        self._is_temporary_volume = False
        if self._engine:
            self._engine.set_volume(self._volume)
        if self._media_player and not self._is_muted and not self._is_crossfading:
            self._apply_player_volume(self._volume)
        try:
            get_config_manager().set_player_volume(self._volume)
        except Exception:
            pass
        self.volume_changed.emit(self._volume, self._is_muted)

    def audio_set_temporary_volume(self, volume: int) -> None:
        """Applique temporairement un volume matériel sans altérer la configuration."""
        self._is_temporary_volume = True
        if self._uses_buffer_engine and not self._is_muted:
            self._engine.set_volume(max(0, min(100, volume)))
        if self._media_player and not self._is_muted and not self._is_crossfading:
            self._apply_player_volume(max(0, min(100, volume)))

    def restore_volume(self) -> None:
        """Rétablit le volume nominal enregistré après un fondu temporaire."""
        self._is_temporary_volume = False
        if self._uses_buffer_engine and not self._is_muted:
            self._engine.set_volume(self._volume)
        if self._media_player and not self._is_muted and not self._is_crossfading:
            self._apply_player_volume(self._volume)

    @property
    def _uses_buffer_engine(self) -> bool:
        """Les fondus de volume temporaires (Blind Test) doivent agir sur le moteur réellement actif."""
        return bool(get_config_manager().get_audio_engine() == "buffer" and self._engine and self._engine.is_available)

    def toggle_mute(self) -> None:
        """Bascule le mode silencieux (Mute/Unmute)."""
        self._is_muted = not self._is_muted
        if self._engine:
            self._engine.set_muted(self._is_muted)
        if self._media_player:
            self._apply_player_volume(0 if self._is_muted else self._volume)
        if self._standby_player and self._is_muted:
            try:
                self._standby_player.audio_set_volume(0)
            except Exception:
                pass
        try:
            get_config_manager().set_player_muted(self._is_muted)
        except Exception:
            pass
        self.volume_changed.emit(self._volume, self._is_muted)

    def _apply_player_volume(self, target: int) -> None:
        """Applique le volume cible au lecteur principal sans doublon d'appel."""
        if self._last_set_volume != target and self._media_player:
            self._last_set_volume = target
            try:
                self._media_player.audio_set_volume(target)
            except Exception:
                pass
