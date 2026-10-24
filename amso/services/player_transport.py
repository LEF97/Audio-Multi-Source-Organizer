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
        elif self._repeat_mode == RepeatMode.ALL:
            return 0
        return None

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
        self._preloaded_index = None
        self._is_crossfading = False
        self._crossfade_next_index = None
        self._fade_start_time = 0.0
        self._fade_paused_elapsed = 0.0
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
        if file_path and os.path.exists(file_path) and self._vlc_instance and self._media_player:
            try:
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

            if self._vlc_instance is None or self._media_player is None:
                return

            # Préparation du média VLC avec options de mise en cache fluide
            norm_path = os.path.normpath(file_path)
            media = self._vlc_instance.media_new_path(norm_path)
            media.add_option(":file-caching=2000")
            media.add_option(":network-caching=2000")
            if seek_ms > 0:
                start_sec = seek_ms / 1000.0
                media.add_option(f":start-time={start_sec:.2f}")
                self._pending_seek_ms = seek_ms
            else:
                self._pending_seek_ms = 0
            self._media_player.set_media(media)
            self._media_player.play()

            if getattr(self, "_is_temporary_volume", False):
                self._volume_enforce_ticks = 0
                self._media_player.audio_set_volume(0)
            else:
                self._start_playback_fade_in()

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

        if self._media_player is None:
            return

        state = self._media_player.get_state()
        if state == vlc.State.Playing:
            self._stop_playback_fade_in()
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
            self.state_changed.emit("paused")
        elif state == vlc.State.Paused:
            self._media_player.play()
            if not getattr(self, "_is_temporary_volume", False):
                self._start_playback_fade_in()
            else:
                self._volume_enforce_ticks = 10
                self._enforce_volume()
            if self._is_crossfading:
                if self._standby_player:
                    try:
                        self._standby_player.play()
                    except Exception:
                        pass
                if hasattr(self, "_fade_timer") and not self._fade_timer.isActive():
                    self._fade_start_time = time.time() - self._fade_paused_elapsed
                    self._fade_timer.start(40)
            self.state_changed.emit("playing")
        else:
            self.play_index(self._current_index, resume_pending=True)

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
            self._media_player.play()
            if not getattr(self, "_is_temporary_volume", False):
                self._start_playback_fade_in()
            else:
                self._volume_enforce_ticks = 10
                self._enforce_volume()
            if self._is_crossfading:
                if self._standby_player:
                    try:
                        self._standby_player.play()
                    except Exception:
                        pass
                if hasattr(self, "_fade_timer") and not self._fade_timer.isActive():
                    self._fade_start_time = time.time() - self._fade_paused_elapsed
                    self._fade_timer.start(40)
            self.state_changed.emit("playing")
        elif 0 <= self._current_index < len(self._playlist):
            self.play_index(self._current_index, resume_pending=True)

    def pause(self) -> None:
        """Met en pause la lecture."""
        if not self.is_vlc_available or not self._media_player:
            return
        self._stop_playback_fade_in()
        state = self._media_player.get_state()
        if state == vlc.State.Playing:
            self._is_paused_requested = False
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
            self.state_changed.emit("paused")
        elif state in (vlc.State.Opening, vlc.State.Buffering):
            try:
                self._media_player.set_pause(1)
            except Exception:
                pass
            self._is_paused_requested = True
            self.state_changed.emit("paused")

    def stop(self) -> None:
        """Arrête la lecture et réinitialise la position."""
        self._stop_playback_fade_in()
        self._is_paused_requested = False
        self._reset_standby_player()
        if self._media_player:
            try:
                self._media_player.stop()
                self._media_player.audio_set_volume(0 if self._is_muted else self._volume)
            except Exception:
                pass
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

        # Si la piste suivante est déjà préchargée sur le standby_player
        if self._standby_player and self._preloaded_index == next_idx:
            self._complete_transition(next_idx)
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

        # Si on a déjà joué plus de 3 secondes, revenir au début du morceau actuel
        current_time_ms = self._media_player.get_time() if self._media_player else 0
        if current_time_ms > 3000:
            self.seek_ms(0)
            return

        if self._current_index > 0:
            self.play_index(self._current_index - 1)
        elif self._repeat_mode == RepeatMode.ALL:
            self.play_index(len(self._playlist) - 1)
        else:
            self.seek_ms(0)

    # -------------------------------------------------------------------------
    # Navigation temporelle (Seek) & Volume
    # -------------------------------------------------------------------------

    def set_seeking(self, seeking: bool) -> None:
        """Indique si l'utilisateur est en train de glisser la seekbar."""
        self._is_seeking = seeking
        if seeking and self._is_crossfading:
            self._reset_standby_player()
            if self._media_player and not self._is_muted:
                try:
                    self._media_player.audio_set_volume(self._volume)
                except Exception:
                    pass

    def seek_ratio(self, ratio: float) -> None:
        """Positionne la tête de lecture à un ratio entre 0.0 et 1.0."""
        ratio = max(0.0, min(1.0, ratio))
        if self._is_crossfading:
            self._reset_standby_player()
            if not self._is_muted and self._media_player:
                try:
                    self._media_player.audio_set_volume(self._volume)
                except Exception:
                    pass

        if not self.is_vlc_available or not self._media_player:
            return

        state = self._media_player.get_state() if self._media_player else None
        if state in (vlc.State.Playing, vlc.State.Paused):
            try:
                self._media_player.set_position(ratio)
            except Exception:
                pass
        else:
            dur = (self.current_track.duration_seconds or 0) * 1000 if self.current_track else 0
            self._pending_seek_ms = int(ratio * dur)
            self._current_time_ms = self._pending_seek_ms
            self.position_changed.emit(self._pending_seek_ms, int(dur), ratio)

    def seek_ms(self, ms: int) -> None:
        """Positionne la tête de lecture en millisecondes."""
        ms = max(0, ms)
        if self._is_crossfading:
            self._reset_standby_player()
            if not self._is_muted and self._media_player:
                try:
                    self._media_player.audio_set_volume(self._volume)
                except Exception:
                    pass

        if not self.is_vlc_available or not self._media_player:
            return

        state = self._media_player.get_state() if self._media_player else None
        if state in (vlc.State.Playing, vlc.State.Paused):
            try:
                self._media_player.set_time(ms)
            except Exception:
                pass
        else:
            self._pending_seek_ms = ms
            self._current_time_ms = ms
            dur = (self.current_track.duration_seconds or 0) * 1000 if self.current_track else 0
            ratio = min(1.0, ms / dur) if dur > 0 else 0.0
            self.position_changed.emit(ms, int(dur), ratio)

    def set_volume(self, volume: int) -> None:
        """Définit le volume sonore (0 à 100)."""
        self._volume = max(0, min(100, volume))
        self._is_temporary_volume = False
        if self._media_player and not self._is_muted and not self._is_crossfading:
            if self._last_set_volume != self._volume:
                self._last_set_volume = self._volume
                try:
                    self._media_player.audio_set_volume(self._volume)
                except Exception:
                    pass
        try:
            get_config_manager().set_player_volume(self._volume)
        except Exception:
            pass
        self.volume_changed.emit(self._volume, self._is_muted)

    def audio_set_temporary_volume(self, volume: int) -> None:
        """Applique temporairement un volume matériel (ex: fondu Blind Test) sans altérer la configuration."""
        vol = max(0, min(100, volume))
        self._is_temporary_volume = True
        if self._media_player and not self._is_muted and not self._is_crossfading:
            if self._last_set_volume != vol:
                self._last_set_volume = vol
                try:
                    self._media_player.audio_set_volume(vol)
                except Exception:
                    pass

    def restore_volume(self) -> None:
        """Rétablit le volume nominal enregistré après un fondu temporaire."""
        self._is_temporary_volume = False
        if self._media_player and not self._is_muted and not self._is_crossfading:
            target = self._volume
            if self._last_set_volume != target:
                self._last_set_volume = target
                try:
                    self._media_player.audio_set_volume(target)
                except Exception:
                    pass

    def toggle_mute(self) -> None:
        """Bascule le mode silencieux (Mute/Unmute)."""
        self._is_muted = not self._is_muted
        if self._media_player:
            target = 0 if self._is_muted else self._volume
            if self._last_set_volume != target:
                self._last_set_volume = target
                try:
                    self._media_player.audio_set_volume(target)
                except Exception:
                    pass
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
