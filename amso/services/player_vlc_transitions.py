"""Gestion des transitions et du fondu enchaîné matériel pour le moteur VLC direct (mixin)."""

from __future__ import annotations

import logging
import math
import time
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QTimer

from amso.services.vlc_binding import vlc

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from amso.services.player_types import PlayerStateBase

    _MixinBase = PlayerStateBase
else:
    _MixinBase = object


class PlayerVlcTransitionsMixin(_MixinBase):
    """Transitions et fondu enchaîné matériel sur double lecteur VLC direct."""

    if TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any: ...

    def _complete_transition(self, next_idx: int) -> None:
        """Finalise le basculement instantané ou la fin de fondu vers le lecteur standby."""
        if hasattr(self, "_fade_timer") and self._fade_timer.isActive():
            self._fade_timer.stop()

        if not (0 <= next_idx < len(self._playlist)):
            self._reset_standby_player()
            self.next()
            return

        if self._standby_player is None or self._media_player is None:
            self._reset_standby_player()
            self.next()
            return

        try:
            # Démarrer ou désactiver la pause du lecteur standby
            state = self._standby_player.get_state() if hasattr(self._standby_player, "get_state") else None
            if state == vlc.State.Paused and hasattr(self._standby_player, "set_pause"):
                self._standby_player.set_pause(0)
            elif hasattr(self._standby_player, "play"):
                self._standby_player.play()

            # Permuter les lecteurs principal et standby
            old_player = self._media_player
            self._media_player = self._standby_player
            self._standby_player = old_player

            # Arrêt différé (1.5s) de l'ancien lecteur pour laisser s'éteindre son outro
            try:
                if hasattr(old_player, "stop"):
                    QTimer.singleShot(1500, lambda p=old_player: self._safe_stop_player(p))
            except Exception:
                pass

            self._current_index = next_idx
            self._preloaded_index = None
            self._is_crossfading = False
            self._crossfade_next_index = None
            self._fade_start_time = 0.0
            self._fade_paused_elapsed = 0.0
            self._last_fade_curr_vol = None
            self._last_fade_next_vol = None

            if hasattr(self, "_timer") and self._timer.interval() != 100:
                self._timer.setInterval(100)

            if not getattr(self, "_is_temporary_volume", False):
                self._volume_enforce_ticks = 2
                self._enforce_volume()

            track = self._playlist[next_idx]
            dur_ms = int((track.duration_seconds or 0) * 1000)
            self._current_time_ms = 0
            if dur_ms > 0:
                self._total_time_ms = dur_ms
            self.position_changed.emit(0, self._total_time_ms, 0.0)
            self.track_changed.emit(track)
            self.state_changed.emit("playing")
            self.playlist_updated.emit()
            logger.info("Transition réussie vers la piste index %d : %s", next_idx, track.title)
        except Exception as exc:
            logger.error("Erreur lors de la transition : %s", exc)
            self._reset_standby_player()
            self.play_index(next_idx)

    def _safe_stop_player(self, player_obj: Any) -> None:
        """Arrête le lecteur après vidage complet des tampons matériels de la carte son."""
        if player_obj is not None and player_obj != self._media_player:
            try:
                if hasattr(player_obj, "stop"):
                    player_obj.stop()
            except Exception:
                pass

    def _finish_standard_transition(self, idx: int) -> None:
        """Finalise le passage à la piste suivante en mode Pas de fondu après vidage du tampon matériel."""
        if not getattr(self, "_is_draining_standard_end", False):
            return
        self._is_draining_standard_end = False
        if getattr(self, "_is_paused_requested", False):
            return
        if self._preloaded_index == idx and self._standby_player:
            self._complete_transition(idx)
        else:
            self.play_index(idx)

    def _on_fade_tick(self) -> None:
        """Gère la rampe de volume haute fréquence à puissance égale (Equal-Power Crossfade).

        Exécuté à 40 FPS (toutes les 25ms) sur horloge système haute résolution.
        Garantit une transition sans saccades et un volume perçu constant sans creux acoustique.
        """
        if not self._is_crossfading or self._crossfade_next_index is None:
            if hasattr(self, "_fade_timer"):
                self._fade_timer.stop()
            return

        if not self._media_player or not self._standby_player:
            if hasattr(self, "_fade_timer"):
                self._fade_timer.stop()
            return

        if self._fade_duration_sec <= 0:
            if hasattr(self, "_fade_timer"):
                self._fade_timer.stop()
            self._complete_transition(self._crossfade_next_index)
            return

        elapsed = time.time() - self._fade_start_time
        progress = max(0.0, min(1.0, elapsed / self._fade_duration_sec))

        angle = progress * (math.pi / 2.0)
        base_vol = 0 if self._is_muted else self._volume
        curr_vol = int(round(base_vol * math.cos(angle)))
        next_vol = int(round(base_vol * math.sin(angle)))

        if getattr(self, "_last_fade_curr_vol", None) != curr_vol:
            try:
                self._media_player.audio_set_volume(curr_vol)
                self._last_fade_curr_vol = curr_vol
            except Exception:
                pass

        if getattr(self, "_last_fade_next_vol", None) != next_vol:
            try:
                self._standby_player.audio_set_volume(next_vol)
                self._last_fade_next_vol = next_vol
            except Exception:
                pass

        if progress >= 1.0:
            if hasattr(self, "_fade_timer"):
                self._fade_timer.stop()
            self._complete_transition(self._crossfade_next_index)
