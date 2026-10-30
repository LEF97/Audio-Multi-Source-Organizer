"""Transitions fluides, gapless/fondu enchaîné et boucle du timer (mixin de PlayerService)."""

from __future__ import annotations

import logging
import os
import time
from typing import TYPE_CHECKING, Any

from amso.core.config import get_config_manager
from amso.services.player_cue import start_track_decode, stream_key
from amso.services.vlc_binding import vlc

logger = logging.getLogger(__name__)

# Le décodeur livre l'audio en temps réel : la piste entrante doit être décodée assez tôt pour que sa tête existe
# quand la zone de fondu commence.
CROSSFADE_PRELOAD_LEAD_MS = 8000


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

    def _on_standby_decoder_ready(self, file_path: str, initial_pcm: bytes, duration_ms: int) -> None:
        """Réceptionne le premier bloc du décodeur standby."""
        self._on_standby_decoder_chunk(file_path, initial_pcm)

    def _on_standby_decoder_chunk(self, file_path: str, chunk: bytes) -> None:
        """Réceptionne les blocs au fur et à mesure sur le décodeur standby."""
        if self.sender() is self._decoder:
            # Émis par le décodeur standby avant sa promotion mais livré après : la connexion est choisie à l'émission
            # (thread audio de VLC). Sans ce routage, ce bloc (~93 ms) serait perdu dans le tampon standby abandonné.
            self._engine.append_chunk(file_path, chunk)
            return
        if self._engine.is_crossfade_armed:
            self._engine.feed_crossfade_incoming(chunk)
            return
        if not hasattr(self, "_standby_pcm"):
            self._standby_pcm = bytearray()
        self._standby_pcm.extend(chunk)

    def _preload_track(self, index: int) -> None:
        """Précharge la piste suivante en mémoire tampon sur le lecteur standby ou décodeur."""
        if not (0 <= index < len(self._playlist)):
            return

        track = self._playlist[index]
        if not track.source_path or not os.path.exists(track.source_path):
            return

        use_buffer = get_config_manager().get_audio_engine() == "buffer" and self._engine and self._engine.is_available
        if use_buffer:
            if get_config_manager().get_transition_mode() == "standard":
                return
            from amso.services.audio_decoder import AsyncAudioDecoder

            if not getattr(self, "_standby_decoder", None):
                self._standby_decoder = AsyncAudioDecoder(vlc_instance=self._vlc_instance, parent=self)
                self._standby_pcm = bytearray()
                self._standby_decoder.ready_to_play.connect(self._on_standby_decoder_ready)
                self._standby_decoder.chunk_decoded.connect(self._on_standby_decoder_chunk)
            self._standby_pcm.clear()
            self._preloaded_index = index
            start_track_decode(self._standby_decoder, track, 0)
            logger.info("Piste suivante pré-décodée dans le tampon continu (index %d) : %s", index, track.title)
            return

        if not self._vlc_instance or not self._standby_player:
            return

        try:
            if hasattr(self, "_apply_vlc_audio_output"):
                self._apply_vlc_audio_output(self._standby_player)
                if get_config_manager().get_transition_mode() == "crossfade" and self._media_player:
                    self._apply_vlc_audio_output(self._media_player)
            norm_path = os.path.normpath(track.source_path)
            media = self._vlc_instance.media_new_path(norm_path)
            media.add_option(":file-caching=60")
            media.add_option(":network-caching=1000")
            media.add_option(":no-video")
            media.add_option(":start-paused")
            try:
                media.parse_with_options(vlc.MediaParseFlag.local, 0)
            except Exception:
                pass
            self._standby_player.set_media(media)
            if get_config_manager().get_transition_mode() == "crossfade":
                self._standby_player.audio_set_volume(0)
            self._standby_player.play()
            if get_config_manager().get_transition_mode() == "crossfade":
                self._standby_player.audio_set_volume(0)
            self._preloaded_index = index
            logger.info(
                "Piste suivante préchargée à chaud en standby (:start-paused, index %d) : %s", index, track.title
            )
        except Exception as exc:
            logger.warning("Échec du préchargement de la piste standby : %s", exc)
            self._preloaded_index = None

    def _promote_standby_decoder(self) -> None:
        """Transfère le décodeur standby comme décodeur principal et nettoie l'ancien."""
        if getattr(self, "_standby_decoder", None):
            old = self._decoder
            self._decoder = self._standby_decoder
            self._standby_decoder = None
            for sig, slot in (
                (self._decoder.ready_to_play, self._on_standby_decoder_ready),
                (self._decoder.chunk_decoded, self._on_standby_decoder_chunk),
            ):
                try:
                    sig.disconnect(slot)
                except Exception:
                    pass
            self._decoder.ready_to_play.connect(self._on_decoder_ready_to_play)
            self._decoder.chunk_decoded.connect(self._on_decoder_chunk_decoded)
            self._decoder.decoding_finished.connect(self._on_decoder_finished)
            if old:
                for sig, slot in (
                    (old.ready_to_play, self._on_decoder_ready_to_play),
                    (old.chunk_decoded, self._on_decoder_chunk_decoded),
                    (old.decoding_finished, self._on_decoder_finished),
                ):
                    try:
                        sig.disconnect(slot)
                    except Exception:
                        pass
                old.stop()
        if hasattr(self, "_standby_pcm"):
            self._standby_pcm.clear()

    def _complete_buffer_transition(self, next_idx: int) -> None:
        """Raccorde immédiatement la piste suivante au sample près (Gapless 0)."""
        if not (0 <= next_idx < len(self._playlist)):
            return
        track = self._playlist[next_idx]
        dur_ms = int((track.duration_seconds or 0) * 1000)
        pcm = bytes(getattr(self, "_standby_pcm", bytearray()))
        self._engine.append_gapless(pcm, dur_ms, file_path=stream_key(track))
        self._promote_standby_decoder()
        self._current_index = next_idx
        self._preloaded_index = None
        self._current_time_ms = 0
        self._total_time_ms = dur_ms
        self.track_changed.emit(track)
        self.playlist_updated.emit()
        logger.info("Transition tampon réussie (gapless) vers : %s", track.title)

    def _arm_buffer_crossfade(self, next_idx: int, fade_ms: int) -> None:
        """Arme le fondu croisé : le moteur le mixe à l'arrivée des blocs décodés, sans changer l'UI avant son terme."""
        if not (0 <= next_idx < len(self._playlist)):
            return
        track = self._playlist[next_idx]
        self._engine.arm_crossfade(fade_ms, stream_key(track))
        self._engine.feed_crossfade_incoming(bytes(self._standby_pcm))
        self._standby_pcm.clear()
        self._is_buffer_crossfading = True
        self._buffer_crossfade_next_idx = next_idx
        self._buffer_crossfade_dur_ms = int((track.duration_seconds or 0) * 1000)
        logger.info("Fondu croisé armé vers : %s (durée: %.1fs)", track.title, fade_ms / 1000.0)

    def _finish_buffer_crossfade(self) -> None:
        """Bascule l'UI et la position temporelle quand la lecture a traversé la zone de fondu."""
        self._is_buffer_crossfading = False
        next_idx = getattr(self, "_buffer_crossfade_next_idx", None)
        if next_idx is None or not (0 <= next_idx < len(self._playlist)):
            return
        track = self._playlist[next_idx]
        dur_ms = getattr(self, "_buffer_crossfade_dur_ms", int((track.duration_seconds or 0) * 1000))

        position_ms = self._engine.finish_crossfade(stream_key(track), dur_ms)

        self._current_index = next_idx
        self._preloaded_index = None
        self._current_time_ms = position_ms
        self._total_time_ms = dur_ms

        ratio = min(1.0, position_ms / dur_ms) if dur_ms > 0 else 0.0
        self.position_changed.emit(position_ms, dur_ms, ratio)
        self.track_changed.emit(track)
        self.playlist_updated.emit()
        logger.info("Fondu croisé achevé vers : %s (position calée à %d ms)", track.title, position_ms)

    def _handle_buffer_crossfade(self, next_idx: int, remaining_ms: int, total_ms: int) -> None:
        """Précharge et arme le fondu ; le mixage lui-même est fait par le moteur, bloc par bloc."""
        if self._is_buffer_crossfading:
            if self._engine.crossfade_played_through():
                self._finish_buffer_crossfade()
            elif not self._engine.crossfade_pending:
                self._is_buffer_crossfading = False
            return
        fade_ms = int(min(float(get_config_manager().get_crossfade_duration()), total_ms * 0.4 / 1000.0) * 1000)
        if self._preloaded_index != next_idx:
            if remaining_ms <= fade_ms + CROSSFADE_PRELOAD_LEAD_MS:
                self._preload_track(next_idx)
                if self._preloaded_index == next_idx:
                    self._arm_buffer_crossfade(next_idx, fade_ms)
        elif not self._engine.is_crossfade_armed:
            self._arm_buffer_crossfade(next_idx, fade_ms)

    def _handle_transitions(self, remaining_ms: int, total_ms: int = 0) -> None:
        """Gère le préchargement, le passage gapless immédiat et le fondu enchaîné."""
        cfg = get_config_manager()
        mode = cfg.get_transition_mode()

        next_idx = self.get_next_index()
        if next_idx is None or next_idx < 0 or next_idx >= len(self._playlist):
            return

        use_buffer = cfg.get_audio_engine() == "buffer" and self._engine and self._engine.is_available
        if use_buffer:
            buffer_avail_bytes = max(0, len(self._engine._current_pcm) - self._engine._play_offset)
            buffer_remaining_ms = int((buffer_avail_bytes / 4) / 44.1)

            if mode == "gapless":
                if remaining_ms <= 8000 and self._preloaded_index != next_idx:
                    self._preload_track(next_idx)

                trigger_gapless = False
                if self._preloaded_index == next_idx:
                    if remaining_ms <= 150:
                        trigger_gapless = True
                    elif getattr(self._engine, "is_feed_complete", False) and buffer_remaining_ms <= 250:
                        trigger_gapless = True

                if trigger_gapless:
                    self._complete_buffer_transition(next_idx)
            elif mode == "crossfade":
                self._handle_buffer_crossfade(next_idx, remaining_ms, total_ms)
            return

        if not self._standby_player:
            return

        if mode == "gapless":
            # Préchargement anticipé (8s avant la fin)
            if remaining_ms <= 8000 and self._preloaded_index != next_idx:
                self._preload_track(next_idx)

            # Basculement anticipé pour compenser la latence DirectSound (configurable, 250ms par défaut)
            gapless_latency = getattr(self, "gapless_directsound_latency_ms", 250)
            if remaining_ms <= gapless_latency and self._preloaded_index == next_idx:
                self._complete_transition(next_idx)

        elif mode == "standard":
            # Préchargement anticipé (8s avant la fin) sur le second lecteur pour ne jamais écraser le décodeur
            if remaining_ms <= 8000 and self._preloaded_index != next_idx:
                self._preload_track(next_idx)

        elif mode == "crossfade":
            fade_sec = float(cfg.get_crossfade_duration())
            # Si le morceau est court (ex: piste de 15s), ne pas dépasser 45% de la durée
            if total_ms > 0:
                max_fade = max(1.0, (total_ms * 0.45) / 1000.0)
                fade_sec = min(float(fade_sec), max_fade)

            fade_ms = int(fade_sec * 1000)

            # 1. Préchargement anticipé
            preload_threshold_ms = fade_ms + 3000
            if remaining_ms <= preload_threshold_ms and self._preloaded_index != next_idx and not self._is_crossfading:
                self._preload_track(next_idx)

            # 2. Déclenchement du fondu sonore haute précision à puissance égale
            # La piste standby démarre à volume 0 au début exact du fondu
            if remaining_ms <= fade_ms and not self._is_crossfading:
                if self._preloaded_index != next_idx:
                    self._preload_track(next_idx)

                if self._preloaded_index == next_idx and self._standby_player:
                    self._is_crossfading = True
                    self._crossfade_next_index = next_idx
                    self._fade_duration_sec = float(fade_sec)
                    self._fade_start_time = time.time()
                    self._fade_paused_elapsed = 0.0

                    try:
                        self._standby_player.audio_set_volume(0)
                        if (
                            hasattr(self._standby_player, "get_state")
                            and self._standby_player.get_state() == vlc.State.Paused
                        ):
                            if hasattr(self._standby_player, "set_pause"):
                                self._standby_player.set_pause(0)
                            elif hasattr(self._standby_player, "play"):
                                self._standby_player.play()
                        elif hasattr(self._standby_player, "play"):
                            self._standby_player.play()
                        self._standby_player.audio_set_volume(0)
                    except Exception as exc:
                        logger.warning("Erreur au lancement du standby player : %s", exc)

                    self._last_fade_curr_vol = None
                    self._last_fade_next_vol = None
                    self._fade_timer.start(25)

    # -------------------------------------------------------------------------
    # Boucle interne (Tick du timer)
    # -------------------------------------------------------------------------

    def _on_tick(self) -> None:
        use_buffer = (
            get_config_manager().get_audio_engine() == "buffer"
            and self._engine
            and self._engine.is_available
            and (self._engine.is_playing or getattr(self._decoder, "is_decoding", False))
        )
        if use_buffer:
            self._engine.poll_progress()
            current_ms = self._engine.current_time_ms
            total_ms = self._engine.total_duration_ms
            self._current_time_ms = current_ms
            if total_ms > 0:
                self._total_time_ms = total_ms
            ratio = (current_ms / total_ms) if total_ms > 0 else 0.0
            if not self._is_seeking:
                self.position_changed.emit(current_ms, total_ms, min(1.0, ratio))
            if total_ms > 2000:
                remaining_ms = total_ms - current_ms
                self._handle_transitions(remaining_ms, total_ms)
            return

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
            if hasattr(self, "_timer") and self._timer.interval() != 100:
                self._timer.setInterval(100)
            if self._is_crossfading or getattr(self, "_is_paused_requested", False):
                return

            if self._preloaded_index is not None:
                self._complete_transition(self._preloaded_index)
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
                    if curr_vol != -1 and abs(curr_vol - target_vol) > 2:
                        self._media_player.audio_set_volume(target_vol)
                except Exception:
                    pass

        current_ms = max(0, self._media_player.get_time())
        total_ms = max(0, self._media_player.get_length())
        self._current_time_ms = current_ms
        if total_ms > 0:
            self._total_time_ms = total_ms
        ratio = max(0.0, self._media_player.get_position())

        if not self._is_seeking:
            self.position_changed.emit(current_ms, total_ms, ratio)

        if total_ms > 2000:
            remaining_ms = total_ms - current_ms
            # Accélération du timer de suivi en fin de piste (< 1.5s) pour transition ultra-réactive
            if remaining_ms <= 1500 and self._timer.interval() != 20:
                self._timer.setInterval(20)
            elif remaining_ms > 1500 and self._timer.interval() != 100:
                self._timer.setInterval(100)
            self._handle_transitions(remaining_ms, total_ms)
        elif self._timer.interval() != 100:
            self._timer.setInterval(100)
