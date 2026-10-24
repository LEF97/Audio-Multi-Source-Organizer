"""Service audio central d'AMSO basé sur python-vlc.

Gère la file d'attente (playlist), le moteur de lecture VLC,
les signaux d'état, de temps et les modes shuffle / repeat.
"""

from __future__ import annotations

import importlib
import logging
import sys
import time

from PySide6.QtCore import QObject, QTimer, Signal

from amso.core.config import get_config_manager
from amso.core.database import TrackRecord
from amso.services.player_queue import PlayerQueueMixin
from amso.services.player_transitions import PlayerTransitionsMixin
from amso.services.player_transport import PlayerTransportMixin
from amso.services.player_types import RepeatMode  # noqa: F401  (réexporté)
from amso.services.vlc_binding import vlc
from amso.services.vlc_downloader import setup_vlc_environment
from amso.services.windows_audio import ensure_windows_audio_session_active

logger = logging.getLogger(__name__)

# Configuration de l'environnement VLC local si présent
setup_vlc_environment()


# Essai d'import de python-vlc
try:
    import vlc as _vlc_module

    vlc.module = _vlc_module
    vlc.available = True
except Exception as _err:
    vlc.module = None
    vlc.available = False
    logger.warning("python-vlc n'a pas pu être chargé : %s", _err)


class PlayerService(PlayerQueueMixin, PlayerTransportMixin, PlayerTransitionsMixin, QObject):
    """Moteur de lecture audio centralisé avec gestionnaire de playlist."""

    # Signaux d'état émis vers l'interface
    track_changed = Signal(object)  # Optionnel[TrackRecord]
    state_changed = Signal(str)  # "playing", "paused", "stopped"
    position_changed = Signal(int, int, float)  # current_ms, total_ms, ratio (0.0 à 1.0)
    volume_changed = Signal(int, bool)  # volume (0 à 100), is_muted
    playlist_updated = Signal()  # notification de modification de la liste
    shuffle_changed = Signal(bool)  # état aléatoire actif ou inactif
    repeat_changed = Signal(int)  # RepeatMode (0, 1, 2)
    error_occurred = Signal(str)  # message d'erreur utilisateur

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        cfg = get_config_manager()

        # File d'attente
        self._playlist: list[TrackRecord] = []
        self._unshuffled_playlist: list[TrackRecord] | None = None
        self._current_index: int = -1
        self._shuffle: bool = cfg.get_player_shuffle()
        self._shuffle_order: list[int] = []
        self._repeat_mode: int = cfg.get_player_repeat_mode()

        # Volume et état
        self._volume: int = cfg.get_player_volume()
        self._is_muted: bool = cfg.get_player_muted()
        self._is_temporary_volume: bool = False
        self._last_set_volume: int = -1
        self._volume_enforce_ticks: int = 0
        self._is_seeking: bool = False
        self._pending_seek_ms: int = 0
        self._current_time_ms: int = 0
        self._total_time_ms: int = 0
        self._is_paused_requested: bool = False

        # Vérification préventive de la session audio Windows (mélangeur système)
        ensure_windows_audio_session_active()

        # État de transition & préchargement (Gapless / Crossfade)
        self._standby_player = None
        self._preloaded_index: int | None = None
        self._is_crossfading: bool = False
        self._crossfade_next_index: int | None = None
        self._fade_start_time: float = 0.0
        self._fade_duration_sec: float = 0.0
        self._fade_paused_elapsed: float = 0.0

        # Initialisation VLC
        self._vlc_instance = None
        self._media_player = None
        self._init_vlc()

        # Timer pour mise à jour fluide de la progression (100ms)
        self._timer = QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._on_tick)

        # Timer haute fréquence dédié au fondu enchaîné (40ms = 25 FPS)
        self._fade_timer = QTimer(self)
        self._fade_timer.setInterval(40)
        self._fade_timer.timeout.connect(self._on_fade_tick)

        # Timer dédié au fondu progressif de démarrage/reprise de lecture (1s fade-in)
        self._is_fading_in: bool = False
        self._fade_in_start_time: float = 0.0
        self._fade_in_duration: float = 1.0
        self._playback_fade_in_timer = QTimer(self)
        self._playback_fade_in_timer.setInterval(40)
        self._playback_fade_in_timer.timeout.connect(self._on_playback_fade_in_tick)

    def _start_playback_fade_in(self) -> None:
        """Démarre une rampe de volume progressive de 0% vers le volume cible sur 1 seconde."""
        if getattr(self, "_is_temporary_volume", False) or self._is_crossfading:
            return

        target_vol = 0 if self._is_muted else self._volume
        if target_vol <= 0 or not self._media_player:
            return

        self._stop_playback_fade_in()
        self._is_fading_in = True
        self._fade_in_start_time = time.time()
        self._fade_in_duration = 1.0

        try:
            self._media_player.audio_set_volume(0)
            self._last_set_volume = 0
        except Exception:
            pass

        self._playback_fade_in_timer.start(40)

    def _stop_playback_fade_in(self) -> None:
        """Arrête le timer de fondu progressif à la lecture."""
        if hasattr(self, "_playback_fade_in_timer") and self._playback_fade_in_timer.isActive():
            self._playback_fade_in_timer.stop()
        self._is_fading_in = False

    def _on_playback_fade_in_tick(self) -> None:
        """Incrémente le volume du lecteur principal jusqu'au volume nominal."""
        if not self._is_fading_in or not self._media_player or getattr(self, "_is_temporary_volume", False):
            self._stop_playback_fade_in()
            return

        elapsed = time.time() - getattr(self, "_fade_in_start_time", 0.0)
        dur = max(0.1, getattr(self, "_fade_in_duration", 1.0))
        progress = max(0.0, min(1.0, elapsed / dur))
        target_vol = 0 if self._is_muted else self._volume
        curr_vol = int(round(target_vol * progress))

        try:
            self._media_player.audio_set_volume(curr_vol)
            self._last_set_volume = curr_vol
        except Exception:
            pass

        if progress >= 1.0:
            self._stop_playback_fade_in()
            self._volume_enforce_ticks = 5
            self._enforce_volume()

    def _enforce_volume(self) -> None:
        """Applique sans délai le volume nominal vers le lecteur principal s'il n'est pas en fondu."""
        if self._media_player and not self._is_crossfading and not self._is_temporary_volume and not self._is_fading_in:
            try:
                target = 0 if self._is_muted else self._volume
                if self._last_set_volume != target:
                    self._last_set_volume = target
                    self._media_player.audio_set_volume(target)
            except Exception:
                pass

    def _init_vlc(self) -> bool:
        """Initialise l'instance VLC et les lecteurs multimédias principal et standby.

        Sous Windows, on active explicitement le module de sortie '--aout=directsound'.
        Le backend par défaut (mmdevice / WASAPI) agit au niveau de la session audio
        du processus Windows tout entier, ce qui empêchait les 2 lecteurs d'avoir des
        volumes distincts et provoquait un conflit destructeur (battement/saccades).
        DirectSound fournit des canaux de mixage et de volume logiciel 100% indépendants.
        On ajoute également '--reset-config' et '--no-volume-save' pour isoler AMSO de toute
        interférence avec les réglages globaux du VLC de bureau et éviter les volumes corrompus.
        """
        if not vlc.available:
            return False
        try:
            vlc_args = ["--no-xlib", "--quiet", "--reset-config", "--no-volume-save"]
            if sys.platform == "win32":
                vlc_args.append("--aout=directsound")
            try:
                self._vlc_instance = vlc.Instance(*vlc_args)
            except Exception:
                self._vlc_instance = vlc.Instance("--no-xlib", "--quiet")
            if self._vlc_instance is None:
                raise RuntimeError("Échec de création de l'instance VLC")
            self._media_player = self._vlc_instance.media_player_new()
            if self._media_player is not None:
                if sys.platform == "win32" and hasattr(self._media_player, "audio_output_set"):
                    try:
                        self._media_player.audio_output_set("directsound")
                    except Exception:
                        pass
                initial_vol = 0 if self._is_muted else self._volume
                self._last_set_volume = initial_vol
                self._media_player.audio_set_volume(initial_vol)
            try:
                self._standby_player = self._vlc_instance.media_player_new()
                if self._standby_player is not None:
                    if sys.platform == "win32" and hasattr(self._standby_player, "audio_output_set"):
                        try:
                            self._standby_player.audio_output_set("directsound")
                        except Exception:
                            pass
                    self._standby_player.audio_set_volume(0)
            except Exception:
                self._standby_player = None
            return True
        except Exception as exc:
            logger.error("Erreur à l'initialisation de VLC : %s", exc)
            self._vlc_instance = None
            self._media_player = None
            self._standby_player = None
            return False

    def reload_vlc(self) -> bool:
        """Tente de recharger VLC (après un téléchargement automatique ou changement de chemin)."""
        setup_vlc_environment()
        try:
            if "vlc" in sys.modules:
                importlib.reload(sys.modules["vlc"])
                vlc.module = sys.modules["vlc"]
            else:
                vlc.module = importlib.import_module("vlc")
            vlc.available = True
        except Exception as err:
            logger.warning("Échec du rechargement de python-vlc : %s", err)
            vlc.available = False
            return False

        success = self._init_vlc()
        if success:
            self.state_changed.emit("stopped")
            self.playlist_updated.emit()
            if self.current_track:
                self.track_changed.emit(self.current_track)
        return success

    # -------------------------------------------------------------------------
    # Propriétés publiques
    # -------------------------------------------------------------------------

    @property
    def is_vlc_available(self) -> bool:
        return vlc.available and self._media_player is not None

    @property
    def current_track(self) -> TrackRecord | None:
        if 0 <= self._current_index < len(self._playlist):
            return self._playlist[self._current_index]
        return None

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def playlist(self) -> list[TrackRecord]:
        return list(self._playlist)

    @property
    def is_shuffle(self) -> bool:
        return self._shuffle

    @property
    def repeat_mode(self) -> int:
        return self._repeat_mode

    @property
    def volume(self) -> int:
        return self._volume

    @property
    def is_muted(self) -> bool:
        return self._is_muted

    @property
    def is_playing(self) -> bool:
        if not self._media_player:
            return False
        return bool(self._media_player.is_playing())

    @property
    def current_time_ms(self) -> int:
        """Retourne la position temporelle courante en millisecondes."""
        if self._media_player:
            try:
                t = self._media_player.get_time()
                if t > 0:
                    return t
            except Exception:
                pass
        if self._pending_seek_ms > 0:
            return self._pending_seek_ms
        return getattr(self, "_current_time_ms", 0)

    @property
    def position_ms(self) -> int:
        """Alias pratique de current_time_ms."""
        return self.current_time_ms

    @property
    def total_time_ms(self) -> int:
        """Retourne la durée totale du morceau en millisecondes."""
        if self._media_player:
            try:
                length_ms = self._media_player.get_length()
                if length_ms > 0:
                    return length_ms
            except Exception:
                pass
        if self.current_track and self.current_track.duration_seconds:
            return int(self.current_track.duration_seconds * 1000)
        return getattr(self, "_total_time_ms", 0)
