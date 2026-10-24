"""Transitions fluides, gapless/fondu enchaîné et boucle du timer (mixin de PlayerService)."""

from __future__ import annotations

import logging
import math
import os
import time
from typing import TYPE_CHECKING, Any

from amso.core.config import get_config_manager
from amso.services.vlc_binding import vlc

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from amso.services.player_types import PlayerStateBase

    _MixinBase = PlayerStateBase
else:
    _MixinBase = object


class PlayerTransitionsMixin(_MixinBase):
    """Transitions fluides, gapless/fondu enchaîné et boucle du timer (mixin de PlayerService)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de PlayerService sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    # -------------------------------------------------------------------------
    # Transitions fluides (Gapless & Fondu enchaîné)
    # -------------------------------------------------------------------------

    def preload_track(self, index: int) -> None:
        """Précharge la piste à l'index donné en mémoire tampon sur le lecteur standby."""
        self._preload_track(index)

    def _preload_track(self, index: int) -> None:
        """Précharge la piste suivante en mémoire tampon sur le lecteur standby."""
        if not self._vlc_instance or not self._standby_player:
            return
        if not (0 <= index < len(self._playlist)):
            return

        track = self._playlist[index]
        if not track.source_path or not os.path.exists(track.source_path):
            return

        try:
            norm_path = os.path.normpath(track.source_path)
            media = self._vlc_instance.media_new_path(norm_path)
            # Mise en cache 2000ms pour assurer une lecture fluide même sur réseau local/NAS (SMB)
            media.add_option(":file-caching=2000")
            media.add_option(":network-caching=2000")
            try:
                media.parse_with_options(vlc.MediaParseFlag.local, 0)
            except Exception:
                pass
            self._standby_player.set_media(media)
            self._standby_player.audio_set_volume(0)
            self._preloaded_index = index
            logger.info("Piste suivante préchargée en standby (index %d) : %s", index, track.title)
        except Exception as exc:
            logger.warning("Échec du préchargement de la piste standby : %s", exc)
            self._preloaded_index = None

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
            # Démarrer standby s'il ne jouait pas déjà
            if self._standby_player.get_state() != vlc.State.Playing:
                self._standby_player.play()

            if getattr(self, "_is_temporary_volume", False):
                base_vol = 0
            else:
                base_vol = 0 if self._is_muted else self._volume
            self._standby_player.audio_set_volume(base_vol)

            # Arrêter l'ancien lecteur principal
            try:
                self._media_player.stop()
            except Exception:
                pass

            # Permuter les lecteurs principal et standby
            self._media_player, self._standby_player = self._standby_player, self._media_player
            self._standby_player.audio_set_volume(0)

            self._current_index = next_idx
            self._preloaded_index = None
            self._is_crossfading = False
            self._crossfade_next_index = None
            self._fade_start_time = 0.0
            self._fade_paused_elapsed = 0.0

            # Verrouiller le volume nominal sur le nouveau lecteur principal (sauf si volume temporaire)
            if not getattr(self, "_is_temporary_volume", False):
                self._volume_enforce_ticks = 10
                self._enforce_volume()

            track = self._playlist[next_idx]
            self.track_changed.emit(track)
            self.state_changed.emit("playing")
            self.playlist_updated.emit()
            logger.info("Transition réussie vers la piste index %d : %s", next_idx, track.title)
        except Exception as exc:
            logger.error("Erreur lors de la transition : %s", exc)
            self._reset_standby_player()
            self.play_index(next_idx)

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

        # Formule Equal-Power (quart de sinus / cosinus) : cos²(θ) + sin²(θ) == 1
        # Évite l'affaissement perçu de -6dB provoqué par un fondu linéaire classique
        angle = progress * (math.pi / 2.0)
        base_vol = 0 if self._is_muted else self._volume
        curr_vol = int(round(base_vol * math.cos(angle)))
        next_vol = int(round(base_vol * math.sin(angle)))

        try:
            self._media_player.audio_set_volume(curr_vol)
        except Exception:
            pass

        try:
            self._standby_player.audio_set_volume(next_vol)
        except Exception:
            pass

        if progress >= 1.0:
            if hasattr(self, "_fade_timer"):
                self._fade_timer.stop()
            self._complete_transition(self._crossfade_next_index)

    def _handle_transitions(self, remaining_ms: int, total_ms: int = 0) -> None:
        """Gère le préchargement, le passage gapless immédiat et le fondu enchaîné."""
        cfg = get_config_manager()
        mode = cfg.get_transition_mode()

        if mode == "standard":
            if self._is_crossfading or self._preloaded_index is not None:
                self._reset_standby_player()
            return

        next_idx = self.get_next_index()
        if next_idx is None or next_idx < 0 or next_idx >= len(self._playlist):
            return

        if not self._standby_player:
            return

        if mode == "gapless":
            # 1. Préchargement anticipé (8s avant la fin)
            if remaining_ms <= 8000 and self._preloaded_index != next_idx:
                self._preload_track(next_idx)

            # 2. Transition immédiate à la fin (seuil 150ms pour éliminer toute coupure)
            if remaining_ms <= 150 and self._preloaded_index == next_idx:
                self._complete_transition(next_idx)

        elif mode == "crossfade":
            fade_sec: float = cfg.get_crossfade_duration()
            # Si le morceau est court (ex: piste de 15s), ne pas dépasser 45% de la durée
            if total_ms > 0:
                max_fade = max(1.0, (total_ms * 0.45) / 1000.0)
                fade_sec = min(float(fade_sec), max_fade)

            fade_ms = int(fade_sec * 1000)

            # 1. Préchargement anticipé (3s avant le début effectif du fondu)
            preload_threshold_ms = fade_ms + 3000
            if remaining_ms <= preload_threshold_ms and self._preloaded_index != next_idx and not self._is_crossfading:
                self._preload_track(next_idx)

            # 2. Déclenchement du fondu sonore haute précision à puissance égale
            if remaining_ms <= fade_ms and not self._is_crossfading:
                if self._preloaded_index != next_idx:
                    self._preload_track(next_idx)

                if self._preloaded_index == next_idx:
                    self._is_crossfading = True
                    self._crossfade_next_index = next_idx
                    self._fade_duration_sec = float(fade_sec)
                    self._fade_start_time = time.time()
                    self._fade_paused_elapsed = 0.0

                    try:
                        self._standby_player.audio_set_volume(0)
                        self._standby_player.play()
                    except Exception as exc:
                        logger.warning("Erreur au lancement du standby player : %s", exc)

                    self._fade_timer.start(40)

    # -------------------------------------------------------------------------
    # Boucle interne (Tick du timer)
    # -------------------------------------------------------------------------

    def _on_tick(self) -> None:
        if not self.is_vlc_available or not self._media_player:
            return

        state = self._media_player.get_state()
        if getattr(self, "_is_paused_requested", False):
            if state in (vlc.State.Playing, vlc.State.Buffering):
                try:
                    self._media_player.set_pause(1)
                except Exception:
                    self._media_player.pause()
                self._is_paused_requested = False
                self.state_changed.emit("paused")
            return

        if state == vlc.State.Ended:
            if self._is_crossfading and self._crossfade_next_index is not None:
                self._complete_transition(self._crossfade_next_index)
            else:
                self.next()
            return

        if state != vlc.State.Playing:
            return

        if self._pending_seek_ms > 0:
            target_ms = self._pending_seek_ms
            self._pending_seek_ms = 0
            try:
                self._media_player.set_time(target_ms)
            except Exception:
                pass

        if not self._is_crossfading and not self._is_temporary_volume and not self._is_fading_in:
            target_vol = 0 if self._is_muted else self._volume
            if getattr(self, "_volume_enforce_ticks", 0) > 0:
                self._volume_enforce_ticks -= 1
                try:
                    self._media_player.audio_set_volume(target_vol)
                except Exception:
                    pass
            else:
                try:
                    curr_vol = self._media_player.audio_get_volume()
                    if curr_vol != target_vol and curr_vol != -1:
                        self._media_player.audio_set_volume(target_vol)
                except Exception:
                    pass

        current_ms = max(0, self._media_player.get_time())
        total_ms = max(0, self._media_player.get_length())
        self._current_time_ms = current_ms
        if total_ms > 0:
            self._total_time_ms = total_ms
        ratio = self._media_player.get_position()
        if ratio < 0:
            ratio = 0.0

        if not self._is_seeking:
            self.position_changed.emit(current_ms, total_ms, ratio)

        if total_ms > 2000:
            remaining_ms = total_ms - current_ms
            self._handle_transitions(remaining_ms, total_ms)
