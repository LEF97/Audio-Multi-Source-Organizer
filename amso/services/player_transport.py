"""Commandes de lecture, seek et volume (mixin de PlayerService)."""

from __future__ import annotations

import logging
import os
import time
from typing import TYPE_CHECKING, Any

from amso.core.config import get_config_manager
from amso.services.player_types import RepeatMode
from amso.services.vlc_binding import vlc
from amso.services.windows_audio import ensure_windows_audio_session_active

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from amso.services.player_types import PlayerStateBase

    _MixinBase = PlayerStateBase
else:
    _MixinBase = object


class PlayerTransportMixin(_MixinBase):
    """Commandes de lecture, seek et volume (mixin de PlayerService)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de PlayerService sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    # -------------------------------------------------------------------------
    # Commandes de Lecture
    # -------------------------------------------------------------------------

    def get_next_index(self) -> int | None:
        """Détermine l'index de la prochaine piste selon le mode de répétition."""
        if not self._playlist:
            return None

        if self._repeat_mode == RepeatMode.ONE and self._current_index >= 0:
            return self._current_index

        if self._current_index + 1 < len(self._playlist):
            return self._current_index + 1
        return 0 if self._repeat_mode == RepeatMode.ALL else None

    def _reset_standby_player(self) -> None:
        """Réinitialise et stoppe le lecteur de préchargement / transition."""
        if hasattr(self, "_fade_timer") and self._fade_timer.isActive():
            self._fade_timer.stop()
        if self._standby_player:
            try:
                self._standby_player.stop()
                self._standby_player.audio_set_volume(0)
            except Exception:
                pass
        if getattr(self, "_standby_decoder", None):
            try:
                self._standby_decoder.stop()
            except Exception:
                pass
            self._standby_decoder = None
        if hasattr(self, "_standby_pcm"):
            self._standby_pcm.clear()
        self._preloaded_index = None
        self._is_crossfading = False
        self._is_buffer_crossfading = False
        if getattr(self, "_engine", None):
            self._engine._crossfade_next_path = ""
        self._crossfade_next_index = None
        self._fade_start_time = 0.0
        self._fade_paused_elapsed = 0.0
        self._is_draining_standard_end = False
        # Rétablir le volume nominal sur le lecteur principal s'il avait été atténué
        if self._media_player and not self._is_muted:
            try:
                self._media_player.audio_set_volume(self._volume)
            except Exception:
                pass

    def load_index(self, index: int, seek_ms: int = 0) -> None:
        """Charge un morceau à l'index donné sans démarrer la lecture (en pause silencieuse)."""
        if not (0 <= index < len(self._playlist)):
            return

        self._reset_standby_player()
        if self._media_player:
            try:
                self._media_player.stop()
            except Exception:
                pass

        self._is_paused_requested = True
        self._current_index = index
        self._pending_seek_ms = max(0, seek_ms)
        self._current_time_ms = max(0, seek_ms)
        track = self._playlist[index]
        file_path = track.source_path

        use_buffer = get_config_manager().get_audio_engine() == "buffer" and bool(self._engine and self._decoder)
        if use_buffer:
            if self._media_player:
                try:
                    self._media_player.stop()
                except Exception:
                    pass
            self._engine.stop()
            dur_ms = int((track.duration_seconds or 0) * 1000)
            self._pending_seek_ms = seek_ms
            self._current_time_ms = seek_ms
            if file_path and os.path.exists(file_path):
                self._decoder.start_decode(file_path, start_offset_ms=seek_ms, duration_ms=dur_ms)
            self.track_changed.emit(track)
            self.state_changed.emit("paused")
            if dur_ms > 0:
                ratio = min(1.0, seek_ms / dur_ms)
                self.position_changed.emit(seek_ms, dur_ms, ratio)
            return

        if file_path and os.path.exists(file_path) and self._vlc_instance and self._media_player:
            try:
                if hasattr(self, "_apply_vlc_audio_output"):
                    self._apply_vlc_audio_output(self._media_player)
                norm_path = os.path.normpath(file_path)
                media = self._vlc_instance.media_new_path(norm_path)
                media.add_option(":file-caching=2000")
                media.add_option(":network-caching=2000")
                if seek_ms > 0:
                    start_sec = seek_ms / 1000.0
                    media.add_option(f":start-time={start_sec:.2f}")
                self._media_player.set_media(media)
            except Exception as exc:
                logger.debug("load_index set_media: %s", exc)

        self.track_changed.emit(track)
        self.state_changed.emit("paused")
        if self._total_time_ms > 0:
            ratio = min(1.0, seek_ms / self._total_time_ms) if self._total_time_ms else 0.0
            self.position_changed.emit(seek_ms, self._total_time_ms, ratio)

    def play_index(self, index: int, resume_pending: bool = False) -> None:
        """Charge et joue le morceau à l'index donné dans la playlist."""
        if not self.is_vlc_available:
            self.error_occurred.emit("VLC n'est pas disponible ou installé sur ce système.")
            return

        if getattr(self, "_is_loading_track", False):
            return

        if not (0 <= index < len(self._playlist)):
            return

        # S'assurer que le mélangeur Windows n'est pas sourdine ou ducké
        ensure_windows_audio_session_active()

        self._is_paused_requested = False
        self._is_loading_track = True
        try:
            seek_ms = self._pending_seek_ms if resume_pending else 0
            self._pending_seek_ms = 0
            self._reset_standby_player()
            self._current_index = index
            track = self._playlist[index]

            file_path = track.source_path
            if not file_path or not os.path.exists(file_path):
                self.error_occurred.emit(f"Fichier audio introuvable : {file_path}")
                return

            use_buffer = (
                get_config_manager().get_audio_engine() == "buffer"
                and self._engine
                and self._decoder
                and self._engine.is_available
            )
            if use_buffer:
                if self._media_player:
                    try:
                        self._media_player.stop()
                    except Exception:
                        pass
                self._engine.stop()
                dur_ms = int((track.duration_seconds or 0) * 1000)
                self._pending_seek_ms = seek_ms
                self._current_time_ms = seek_ms
                self._decoder.start_decode(file_path, start_offset_ms=seek_ms, duration_ms=dur_ms)
                self._timer.start()
                self.track_changed.emit(track)
                self.state_changed.emit("playing")
                self.playlist_updated.emit()
                return

            if self._engine:
                self._engine.stop()

            if self._vlc_instance is None or self._media_player is None:
                return

            if hasattr(self, "_apply_vlc_audio_output"):
                self._apply_vlc_audio_output(self._media_player)

            media = self._vlc_instance.media_new_path(os.path.normpath(file_path))
            media.add_option(":file-caching=60")
            media.add_option(":network-caching=1000")
            media.add_option(":no-video")
            if seek_ms > 0:
                media.add_option(f":start-time={seek_ms / 1000.0:.2f}")
            self._pending_seek_ms = seek_ms if seek_ms > 0 else 0
            self._media_player.set_media(media)
            self._media_player.play()
            self._apply_player_volume(0 if self._is_muted else self._volume)
            self._timer.start()
            self.track_changed.emit(track)
            self.state_changed.emit("playing")
            self.playlist_updated.emit()
        except Exception as exc:
            logger.error("Erreur lors de la lecture VLC : %s", exc)
            self.error_occurred.emit(f"Erreur de lecture : {exc}")
        finally:
            self._is_loading_track = False

    def toggle_play_pause(self) -> None:
        """Bascule entre Lecture et Pause."""
        if not self.is_vlc_available:
            return

        if not self._playlist:
            return

        if self._current_index < 0:
            self.play_index(0)
            return

        use_buffer = get_config_manager().get_audio_engine() == "buffer" and self._engine and self._engine.is_available
        if use_buffer:
            if self._engine.is_playing:
                self._is_paused_requested = True
                self._engine.pause()
                self.state_changed.emit("paused")
                return
            if self._engine.is_paused:
                self._is_paused_requested = False
                self._engine.resume()
                self.state_changed.emit("playing")
                return
            self._is_paused_requested = False
            self.play_index(self._current_index, resume_pending=True)
            return

        if self._media_player is None:
            return

        state = self._media_player.get_state()
        if state == vlc.State.Playing:
            self._stop_playback_fade_in()
            try:
                self._media_player.audio_set_volume(0)
            except Exception:
                pass
            self._media_player.pause()
            if self._is_crossfading:
                if self._standby_player:
                    try:
                        self._standby_player.pause()
                    except Exception:
                        pass
                if hasattr(self, "_fade_timer") and self._fade_timer.isActive():
                    self._fade_timer.stop()
                    self._fade_paused_elapsed = max(0.0, time.time() - self._fade_start_time)
            self._is_paused_requested = True
            self.state_changed.emit("paused")
        elif state == vlc.State.Paused:
            self._resume_from_paused()
        else:
            self.play_index(self._current_index, resume_pending=True)

    def _resume_from_paused(self) -> None:
        """Reprend la lecture après une pause."""
        self._is_paused_requested = False
        use_buffer = get_config_manager().get_audio_engine() == "buffer" and self._engine and self._engine.is_available
        if use_buffer:
            self._engine.resume()
            self.state_changed.emit("playing")
            return
        if not self._media_player:
            return
        self._media_player.play()
        self._volume_enforce_ticks = 10
        self._enforce_volume()

        if self._is_crossfading and self._standby_player:
            try:
                self._standby_player.play()
            except Exception:
                pass
            if hasattr(self, "_fade_timer") and not self._fade_timer.isActive():
                self._fade_start_time = time.time() - self._fade_paused_elapsed
                self._fade_timer.start(40)
        self.state_changed.emit("playing")

    def play(self) -> None:
        """Lance ou reprend la lecture."""
        if not self.is_vlc_available:
            return
        if getattr(self, "_is_loading_track", False):
            return
        self._is_paused_requested = False
        if self._current_index < 0 and self._playlist:
            self.play_index(0)
            return
        if self._media_player and self._media_player.get_state() == vlc.State.Paused:
            self._resume_from_paused()
        elif 0 <= self._current_index < len(self._playlist):
            self.play_index(self._current_index, resume_pending=True)

    def pause(self) -> None:
        """Met en pause la lecture."""
        self._stop_playback_fade_in()
        self._reset_standby_player()
        if self._engine and self._engine.is_available:
            self._engine.pause()
            self.state_changed.emit("paused")
            return
        if not self.is_vlc_available or not self._media_player:
            return
        state = self._media_player.get_state()
        if state in (vlc.State.Playing, vlc.State.Opening, vlc.State.Buffering):
            try:
                self._media_player.set_pause(1)
            except Exception:
                self._media_player.pause()
        self._is_paused_requested = True
        self.state_changed.emit("paused")

    def stop(self) -> None:
        """Arrête la lecture et réinitialise la position."""
        self._stop_playback_fade_in()
        self._is_paused_requested = False
        if self._engine:
            self._engine.stop()
        if self._decoder:
            self._decoder.stop()
        if self._media_player:
            try:
                if hasattr(self._media_player, "stop"):
                    self._media_player.stop()
            except Exception:
                pass
        self._reset_standby_player()
        self._volume_enforce_ticks = 0
        self._timer.stop()
        self._pending_seek_ms = 0
        self._current_time_ms = 0
        self.state_changed.emit("stopped")
        self.position_changed.emit(0, 0, 0.0)

    def next(self) -> None:
        """Passe au morceau suivant dans la file d'attente."""
        if not self._playlist:
            return

        next_idx = self.get_next_index()
        if next_idx is None:
            self.stop()
            return

        # Si la piste suivante est déjà préchargée sur le standby_player ou standby_decoder
        if self._standby_player and self._preloaded_index == next_idx:
            self._complete_transition(next_idx)
            return

        use_buffer = get_config_manager().get_audio_engine() == "buffer" and self._engine and self._engine.is_available
        if use_buffer and getattr(self, "_standby_decoder", None) and self._preloaded_index == next_idx:
            mode = get_config_manager().get_transition_mode()
            if mode == "gapless":
                self._complete_buffer_transition(next_idx)
                return

        self._reset_standby_player()

        if self._repeat_mode == RepeatMode.ONE and self._current_index >= 0:
            self.play_index(self._current_index)
            return

        if self._current_index + 1 < len(self._playlist):
            self.play_index(self._current_index + 1)
        elif self._repeat_mode == RepeatMode.ALL:
            if self._shuffle:
                self.shuffle_playlist(below_current=False)
            self.play_index(0)
        else:
            self.stop()

    def previous(self) -> None:
        """Passe au morceau précédent ou redémarre si déjà avancé de > 3s."""
        if not self._playlist or self._current_index < 0:
            return

        self._reset_standby_player()
        was_playing = self.is_playing and not getattr(self, "_is_paused_requested", False)

        # Si on a déjà joué plus de 3 secondes, revenir au début du morceau actuel
        if self.current_time_ms > 3000:
            self.seek_ms(0) if was_playing else self.load_index(self._current_index, seek_ms=0)
            return

        target_idx: int | None = self._current_index - 1 if self._current_index > 0 else None
        if target_idx is None and self._repeat_mode == RepeatMode.ALL:
            target_idx = len(self._playlist) - 1

        if target_idx is not None:
            self.play_index(target_idx) if was_playing else self.load_index(target_idx)
        elif was_playing:
            self.seek_ms(0)
        else:
            self.load_index(self._current_index, seek_ms=0)

    # -------------------------------------------------------------------------
    # Navigation temporelle (Seek) & Volume
    # -------------------------------------------------------------------------

    def set_seeking(self, seeking: bool) -> None:
        """Indique si l'utilisateur est en train de glisser la seekbar."""
        self._is_seeking = seeking
        if seeking:
            self._reset_standby_player()
            if self._media_player and not self._is_muted:
                try:
                    self._media_player.audio_set_volume(self._volume)
                except Exception:
                    pass

    def seek_ratio(self, ratio: float) -> None:
        """Positionne la tête de lecture à un ratio entre 0.0 et 1.0."""
        dur = (self.current_track.duration_seconds or 0) * 1000 if self.current_track else 0
        target_ms = int(max(0.0, min(1.0, ratio)) * dur)
        self.seek_ms(target_ms)

    def seek_ms(self, ms: int) -> None:
        """Positionne la tête de lecture en millisecondes."""
        ms = max(0, ms)
        self._reset_standby_player()

        dur = (self.current_track.duration_seconds or 0) * 1000 if self.current_track else 0
        ratio = min(1.0, ms / dur) if dur > 0 else 0.0
        self._current_time_ms = ms
        self._pending_seek_ms = ms

        use_buffer = get_config_manager().get_audio_engine() == "buffer" and self._engine and self._engine.is_available
        if use_buffer:
            was_playing = self.is_playing and not getattr(self, "_is_paused_requested", False)
            if not was_playing:
                self.load_index(self._current_index, seek_ms=ms)
                return

            base_ms = getattr(self._engine, "base_offset_ms", 0)
            target_byte = int(((ms - base_ms) / 1000.0) * 44100 * 4)
            in_mem = (
                getattr(self._engine, "is_feed_complete", False)
                and ms >= base_ms
                and 0 <= target_byte <= len(self._engine._current_pcm)
            )
            if in_mem:
                self._engine.seek_ms(ms)
            else:
                self._engine.reset_buffer_for_seek(ms)
                if self.current_track and self.current_track.source_path and self._decoder:
                    self._pending_seek_ms = ms
                    self._decoder.start_decode(
                        self.current_track.source_path,
                        start_offset_ms=ms,
                        duration_ms=int(dur),
                    )

            self.position_changed.emit(ms, int(dur), ratio)
            return

        if not self.is_vlc_available or not self._media_player:
            self.position_changed.emit(ms, int(dur), ratio)
            return

        state = self._media_player.get_state() if self._media_player else None
        if state in (vlc.State.Playing, vlc.State.Paused):
            try:
                self._media_player.set_time(ms)
            except Exception:
                pass
        elif state == vlc.State.Ended:
            if self._is_paused_requested or not self.is_playing:
                self.load_index(self._current_index, seek_ms=ms)
            else:
                self.play_index(self._current_index, resume_pending=True)
        else:
            self._pending_seek_ms = ms
        self.position_changed.emit(ms, int(dur), ratio)
