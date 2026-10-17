"""Service audio central d'AMSO basé sur python-vlc.

Gère la file d'attente (playlist), le moteur de lecture VLC,
les signaux d'état, de temps et les modes shuffle / repeat.
"""

from __future__ import annotations

import importlib
import logging
import math
import os
import random
import sys
import time
from collections.abc import Sequence

from PySide6.QtCore import QObject, QTimer, Signal

from amso.core.config import get_config_manager
from amso.core.database import TrackRecord
from amso.services.vlc_downloader import setup_vlc_environment

logger = logging.getLogger(__name__)

# Configuration de l'environnement VLC local si présent
setup_vlc_environment()


def ensure_windows_audio_session_active() -> None:
    """S'assure sous Windows que la session audio du processus n'est pas mise en sourdine
    ou atténuée par le mélangeur de volume Windows (CoreAudio / WASAPI).

    Corrige le problème où Windows Audio Mixer attenue une nouvelle version ou un nouvel
    exécutable déployé (ex: communications ducking ou ancienne session à 0%).
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes
        from ctypes import POINTER, Structure, byref, c_float, c_int, c_void_p, cast, wintypes

        class GUID(Structure):
            _fields_ = [
                ("Data1", wintypes.DWORD),
                ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD),
                ("Data4", wintypes.BYTE * 8),
            ]

            def __init__(self, d1, d2, d3, d4):
                super().__init__(d1, d2, d3, (wintypes.BYTE * 8)(*d4))

        CLSID_MMDeviceEnumerator = GUID(0xBCDE0395, 0xE52F, 0x467C, [0x8E, 0x3D, 0xC4, 0x57, 0x92, 0x91, 0x69, 0x2E])
        IID_IMMDeviceEnumerator = GUID(0xA95664D2, 0x9614, 0x4F35, [0xA7, 0x46, 0xDE, 0x8D, 0xB6, 0x36, 0x17, 0xE6])
        IID_IAudioSessionManager2 = GUID(0x77AA99A0, 0x1BD6, 0x484F, [0x8B, 0xC7, 0x2C, 0x65, 0x4C, 0x9A, 0x9B, 0x6F])

        ole32 = ctypes.windll.ole32
        ole32.CoInitialize(None)
        enumerator = c_void_p()
        if ole32.CoCreateInstance(byref(CLSID_MMDeviceEnumerator), None, 1, byref(IID_IMMDeviceEnumerator), byref(enumerator)) == 0:
            vtable = cast(enumerator, POINTER(POINTER(c_void_p))).contents
            GetDefaultAudioEndpoint = ctypes.WINFUNCTYPE(c_int, c_void_p, c_int, c_int, POINTER(c_void_p))(vtable[4])
            device = c_void_p()
            if GetDefaultAudioEndpoint(enumerator, 0, 0, byref(device)) == 0:
                dev_vtable = cast(device, POINTER(POINTER(c_void_p))).contents
                Activate = ctypes.WINFUNCTYPE(c_int, c_void_p, POINTER(GUID), c_int, c_void_p, POINTER(c_void_p))(dev_vtable[3])
                session_manager = c_void_p()
                if Activate(device, byref(IID_IAudioSessionManager2), 1, None, byref(session_manager)) == 0:
                    mgr_vtable = cast(session_manager, POINTER(POINTER(c_void_p))).contents
                    GetSimpleAudioVolume = ctypes.WINFUNCTYPE(c_int, c_void_p, c_void_p, wintypes.DWORD, POINTER(c_void_p))(mgr_vtable[4])
                    simple_vol = c_void_p()
                    if GetSimpleAudioVolume(session_manager, None, 0, byref(simple_vol)) == 0 and simple_vol.value:
                        vol_vtable = cast(simple_vol, POINTER(POINTER(c_void_p))).contents
                        GetMasterVolume = ctypes.WINFUNCTYPE(c_int, c_void_p, POINTER(c_float))(vol_vtable[4])
                        GetMute = ctypes.WINFUNCTYPE(c_int, c_void_p, POINTER(wintypes.BOOL))(vol_vtable[6])
                        SetMasterVolume = ctypes.WINFUNCTYPE(c_int, c_void_p, c_float, c_void_p)(vol_vtable[3])
                        SetMute = ctypes.WINFUNCTYPE(c_int, c_void_p, wintypes.BOOL, c_void_p)(vol_vtable[5])

                        curr_vol = c_float()
                        curr_mute = wintypes.BOOL()
                        GetMasterVolume(simple_vol, byref(curr_vol))
                        GetMute(simple_vol, byref(curr_mute))

                        if curr_mute.value:
                            SetMute(simple_vol, False, None)
                        if curr_vol.value < 0.8:
                            SetMasterVolume(simple_vol, 1.0, None)
    except Exception as exc:
        logger.debug("Vérification audio session Windows non disponible : %s", exc)


# Essai d'import de python-vlc
try:
    import vlc

    VLC_AVAILABLE = True
except Exception as _err:
    vlc = None
    VLC_AVAILABLE = False
    logger.warning("python-vlc n'a pas pu être chargé : %s", _err)


class RepeatMode:
    OFF = 0  # Pas de répétition (s'arrête à la fin de la playlist)
    ALL = 1  # Répéter toute la playlist
    ONE = 2  # Répéter en boucle la piste active


class PlayerService(QObject):
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
        self._volume_enforce_ticks: int = 0
        self._is_seeking: bool = False
        self._pending_seek_ms: int = 0
        self._current_time_ms: int = 0
        self._total_time_ms: int = 0

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

    def _attach_player_events(self, player) -> None:
        """Attache un écouteur sur MediaPlayerPlaying pour réappliquer le volume nominal dès l'ouverture matérielle du flux."""
        if not player or not hasattr(player, "event_manager"):
            return
        try:
            em = player.event_manager()
            if em and hasattr(em, "event_attach"):

                def _on_playing(event) -> None:
                    try:
                        if not self._is_crossfading and self._media_player == player:
                            target = 0 if self._is_muted else self._volume
                            player.audio_set_volume(target)
                    except Exception:
                        pass

                em.event_attach(vlc.EventType.MediaPlayerPlaying, _on_playing)
        except Exception as exc:
            logger.debug("Impossible d'attacher l'événement MediaPlayerPlaying : %s", exc)

    def _enforce_volume(self) -> None:
        """Applique sans délai le volume nominal vers le lecteur principal s'il n'est pas en fondu."""
        if self._media_player and not self._is_crossfading:
            try:
                target = 0 if self._is_muted else self._volume
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
        global vlc, VLC_AVAILABLE
        if not VLC_AVAILABLE:
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
                self._attach_player_events(self._media_player)
                self._media_player.audio_set_volume(0 if self._is_muted else self._volume)
            try:
                self._standby_player = self._vlc_instance.media_player_new()
                if self._standby_player is not None:
                    if sys.platform == "win32" and hasattr(self._standby_player, "audio_output_set"):
                        try:
                            self._standby_player.audio_output_set("directsound")
                        except Exception:
                            pass
                    self._attach_player_events(self._standby_player)
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
        global vlc, VLC_AVAILABLE
        setup_vlc_environment()
        try:
            if "vlc" in sys.modules:
                importlib.reload(sys.modules["vlc"])
                vlc = sys.modules["vlc"]
            else:
                import vlc
            VLC_AVAILABLE = True
        except Exception as err:
            logger.warning("Échec du rechargement de python-vlc : %s", err)
            VLC_AVAILABLE = False
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
        return VLC_AVAILABLE and self._media_player is not None

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

    # -------------------------------------------------------------------------
    # Gestion de la Playlist
    # -------------------------------------------------------------------------

    def play_tracks(self, tracks: Sequence[TrackRecord], start_index: int = 0) -> None:
        """Remplace la playlist courante par une nouvelle liste et lance la lecture."""
        if not tracks:
            self.clear_playlist()
            return

        self._playlist = list(tracks)
        valid_index = max(0, min(start_index, len(self._playlist) - 1))

        if self._shuffle:
            self._unshuffled_playlist = list(tracks)
        else:
            self._unshuffled_playlist = None

        self._shuffle_order = list(range(len(self._playlist)))
        self._pending_seek_ms = 0
        self._current_index = -1
        self.play_index(valid_index)
        self.playlist_updated.emit()

    def load_playlist(
        self, tracks: Sequence[TrackRecord], current_index: int = 0, initial_position_ms: int = 0
    ) -> None:
        """Charge une playlist en mémoire sans lancer la lecture automatiquement."""
        if not tracks:
            self.clear_playlist()
            return

        self._playlist = list(tracks)
        self._current_index = max(0, min(current_index, len(self._playlist) - 1))
        self._unshuffled_playlist = list(tracks) if self._shuffle else None
        self._shuffle_order = list(range(len(self._playlist)))
        dur_ms = int((self.current_track.duration_seconds or 0) * 1000) if self.current_track else 0
        clamped_pos_ms = max(0, initial_position_ms)
        if dur_ms > 0 and clamped_pos_ms >= dur_ms:
            clamped_pos_ms = 0

        self._pending_seek_ms = clamped_pos_ms
        self._current_time_ms = clamped_pos_ms

        self.playlist_updated.emit()
        if self.current_track:
            self.track_changed.emit(self.current_track)
            self._total_time_ms = dur_ms
            ratio = min(1.0, max(0.0, self._pending_seek_ms / dur_ms)) if dur_ms > 0 else 0.0
            self.position_changed.emit(self._pending_seek_ms, dur_ms, ratio)

    def play_track_now(self, track: TrackRecord) -> None:
        """Joue immédiatement une piste unique (l'ajoute si nécessaire)."""
        if not track:
            return

        self._pending_seek_ms = 0

        # Si déjà présente, on s'y positionne
        for idx, t in enumerate(self._playlist):
            if (
                t.source_path
                and track.source_path
                and os.path.normcase(t.source_path) == os.path.normcase(track.source_path)
            ):
                self._current_index = -1
                self.play_index(idx)
                return

        # Sinon on l'insère après la piste courante et on la joue
        insert_pos = self._current_index + 1 if self._current_index >= 0 else 0
        self._playlist.insert(insert_pos, track)
        self._rebuild_shuffle_order()
        self.playlist_updated.emit()
        self._current_index = -1
        self.play_index(insert_pos)

    def insert_next(self, tracks: Sequence[TrackRecord], auto_play: bool = False) -> None:
        """Insère une ou plusieurs pistes juste après la piste en cours de lecture sans forcer la lecture."""
        if not tracks:
            return

        if not self._playlist:
            self._playlist = list(tracks)
            if self._shuffle:
                self._unshuffled_playlist = list(tracks)
            self._current_index = 0
            self._rebuild_shuffle_order()
            self.playlist_updated.emit()
            self.track_changed.emit(self.current_track)
            if auto_play:
                self.play_index(0)
            return

        if self._current_index < 0:
            insert_pos = 0
            for i, t in enumerate(tracks):
                self._playlist.insert(insert_pos + i, t)
            if self._unshuffled_playlist is not None:
                for i, t in enumerate(tracks):
                    self._unshuffled_playlist.insert(insert_pos + i, t)
            self._current_index = 0
            self._rebuild_shuffle_order()
            self.playlist_updated.emit()
            self.track_changed.emit(self.current_track)
            if auto_play:
                self.play_index(0)
            return

        insert_pos = self._current_index + 1
        for i, t in enumerate(tracks):
            self._playlist.insert(insert_pos + i, t)

        if self._unshuffled_playlist is not None:
            cur = self.current_track
            unshuf_pos = len(self._unshuffled_playlist)
            if cur and cur in self._unshuffled_playlist:
                unshuf_pos = self._unshuffled_playlist.index(cur) + 1
            for i, t in enumerate(tracks):
                self._unshuffled_playlist.insert(unshuf_pos + i, t)

        self._rebuild_shuffle_order()
        self.playlist_updated.emit()

    def append_tracks(self, tracks: Sequence[TrackRecord], auto_play: bool = False) -> None:
        """Ajoute des pistes à la fin de la file d'attente sans forcer la lecture."""
        if not tracks:
            return

        was_empty = len(self._playlist) == 0
        self._playlist.extend(tracks)
        if self._unshuffled_playlist is not None:
            self._unshuffled_playlist.extend(tracks)
        elif self._shuffle and was_empty:
            self._unshuffled_playlist = list(self._playlist)
        self._rebuild_shuffle_order()

        if was_empty or self._current_index < 0:
            self._current_index = 0
            self.track_changed.emit(self.current_track)
            if auto_play:
                self.play_index(0)

        self.playlist_updated.emit()

    def remove_at(self, index: int) -> None:
        """Supprime une piste de la playlist à l'index donné."""
        if not (0 <= index < len(self._playlist)):
            return

        track_to_remove = self._playlist[index]
        if self._unshuffled_playlist is not None and track_to_remove in self._unshuffled_playlist:
            try:
                self._unshuffled_playlist.remove(track_to_remove)
            except ValueError:
                pass

        is_current = index == self._current_index
        del self._playlist[index]

        if not self._playlist:
            self.stop()
            self._unshuffled_playlist = None
            self._current_index = -1
            self.playlist_updated.emit()
            self.track_changed.emit(None)
            return

        if index < self._current_index:
            self._current_index -= 1
        elif is_current:
            # On rejoue la nouvelle piste qui a pris cet index (ou la dernière si on était au bout)
            new_idx = min(index, len(self._playlist) - 1)
            self._current_index = -1
            self.play_index(new_idx)

        self._rebuild_shuffle_order()
        self.playlist_updated.emit()

    def clear_playlist(self) -> None:
        """Vide entièrement la playlist et stoppe la lecture."""
        self.stop()
        self._playlist.clear()
        self._unshuffled_playlist = None
        self._shuffle_order.clear()
        self._current_index = -1
        self.playlist_updated.emit()
        self.track_changed.emit(None)

    def shuffle_all_tracks(self) -> None:
        """Mélange l'ensemble complet des titres de la playlist et repositionne l'index de la piste active."""
        if len(self._playlist) <= 1:
            return

        if self._shuffle and self._unshuffled_playlist is None:
            self._unshuffled_playlist = list(self._playlist)

        current_track = self.current_track
        random.shuffle(self._playlist)

        if current_track is not None:
            try:
                for idx, t in enumerate(self._playlist):
                    if t is current_track:
                        self._current_index = idx
                        break
                else:
                    self._current_index = self._playlist.index(current_track)
            except ValueError:
                self._current_index = max(0, min(self._current_index, len(self._playlist) - 1))

        self._shuffle_order = list(range(len(self._playlist)))
        self.playlist_updated.emit()

    def shuffle_playlist(self, below_current: bool = False) -> None:
        """Mélange les pistes de la file d'attente (playlist).

        Si below_current est True et qu'un morceau est en cours de lecture, les morceaux
        situés avant et le morceau en cours restent inchangés, et seuls tous les morceaux
        en dessous sont mélangés aléatoirement.
        Sinon (comportement par défaut), toute la playlist est mélangée et la piste en cours
        peut se retrouver à n'importe quelle position.
        """
        if len(self._playlist) <= 1:
            return

        if below_current and 0 <= self._current_index < len(self._playlist) - 1:
            to_shuffle = self._playlist[self._current_index + 1 :]
            if len(to_shuffle) > 1:
                random.shuffle(to_shuffle)
                self._playlist = self._playlist[: self._current_index + 1] + to_shuffle
            self._shuffle_order = list(range(len(self._playlist)))
            self.playlist_updated.emit()
        else:
            self.shuffle_all_tracks()

    def move_tracks(self, from_rows: list[int], to_row: int) -> None:
        """Déplace un groupe de pistes vers une nouvelle position dans la playlist (Drag & Drop)."""
        if not from_rows or not self._playlist:
            return

        current_track = self.current_track
        from_rows = sorted({r for r in from_rows if 0 <= r < len(self._playlist)})
        if not from_rows:
            return

        moving_tracks = [self._playlist[r] for r in from_rows]
        remaining = [t for i, t in enumerate(self._playlist) if i not in from_rows]

        offset = sum(1 for r in from_rows if r < to_row)
        insert_idx = max(0, min(to_row - offset, len(remaining)))

        remaining[insert_idx:insert_idx] = moving_tracks
        self._playlist = remaining

        if current_track and current_track in self._playlist:
            self._current_index = self._playlist.index(current_track)

        if self._unshuffled_playlist is not None:
            self._unshuffled_playlist = list(self._playlist)

        self._shuffle_order = list(range(len(self._playlist)))
        self.playlist_updated.emit()

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

    def play_index(self, index: int, resume_pending: bool = False) -> None:
        """Charge et joue le morceau à l'index donné dans la playlist."""
        if not self.is_vlc_available:
            self.error_occurred.emit("VLC n'est pas disponible ou installé sur ce système.")
            return

        if not (0 <= index < len(self._playlist)):
            return

        # S'assurer que le mélangeur Windows n'est pas sourdine ou ducké
        ensure_windows_audio_session_active()

        seek_ms = self._pending_seek_ms if (resume_pending and index == self._current_index) else 0
        self._pending_seek_ms = 0
        self._reset_standby_player()
        self._current_index = index
        track = self._playlist[index]
        self.track_changed.emit(track)
        self.playlist_updated.emit()

        file_path = track.source_path
        if not file_path or not os.path.exists(file_path):
            self.error_occurred.emit(f"Fichier audio introuvable : {file_path}")
            return

        if self._vlc_instance is None or self._media_player is None:
            return

        try:
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

            # Enforcer immédiatement et via les ticks/timers le volume nominal
            # Résout la condition de course LibVLC asynchrone où le volume initial est ignoré
            self._volume_enforce_ticks = 25  # Force le volume sur les 2.5 premières secondes (25 ticks de 100ms)
            self._enforce_volume()
            QTimer.singleShot(50, self._enforce_volume)
            QTimer.singleShot(150, self._enforce_volume)
            QTimer.singleShot(300, self._enforce_volume)
            QTimer.singleShot(600, self._enforce_volume)
            QTimer.singleShot(1200, self._enforce_volume)

            self._timer.start()
            self.track_changed.emit(track)
            self.state_changed.emit("playing")
            self.playlist_updated.emit()
        except Exception as exc:
            logger.error("Erreur lors de la lecture VLC : %s", exc)
            self.error_occurred.emit(f"Erreur de lecture : {exc}")

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
            self._volume_enforce_ticks = 15
            self._enforce_volume()
            QTimer.singleShot(50, self._enforce_volume)
            QTimer.singleShot(150, self._enforce_volume)
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
        if self._current_index < 0 and self._playlist:
            self.play_index(0)
            return
        if self._media_player and self._media_player.get_state() == vlc.State.Paused:
            self._media_player.play()
            self._volume_enforce_ticks = 15
            self._enforce_volume()
            QTimer.singleShot(50, self._enforce_volume)
            QTimer.singleShot(150, self._enforce_volume)
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
        if self._media_player.get_state() == vlc.State.Playing:
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

    def stop(self) -> None:
        """Arrête la lecture et réinitialise la position."""
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

        self._reset_standby_player()
        if self._media_player and not self._is_muted:
            try:
                self._media_player.audio_set_volume(self._volume)
            except Exception:
                pass

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
        if self._media_player and not self._is_muted:
            try:
                self._media_player.audio_set_volume(self._volume)
            except Exception:
                pass

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
        if self._media_player and not self._is_muted and not self._is_crossfading:
            try:
                self._media_player.audio_set_volume(self._volume)
            except Exception:
                pass
        try:
            get_config_manager().set_player_volume(self._volume)
        except Exception:
            pass
        self.volume_changed.emit(self._volume, self._is_muted)

    def toggle_mute(self) -> None:
        """Bascule le mode silencieux (Mute/Unmute)."""
        self._is_muted = not self._is_muted
        if self._media_player:
            try:
                self._media_player.audio_set_volume(0 if self._is_muted else self._volume)
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

    def set_shuffle(self, shuffle: bool) -> None:
        """Définit l'état de lecture aléatoire."""
        if self._shuffle != shuffle:
            self._shuffle = shuffle
            try:
                get_config_manager().set_player_shuffle(self._shuffle)
            except Exception:
                pass

            if self._shuffle:
                # Activation : mémorise l'ordre initial et mélange toute la playlist
                if self._unshuffled_playlist is None:
                    self._unshuffled_playlist = list(self._playlist)
                self.shuffle_all_tracks()
            else:
                # Désactivation : reprend l'ordre des pistes initial
                if self._unshuffled_playlist is not None:
                    current_track = self.current_track
                    self._playlist = list(self._unshuffled_playlist)
                    self._unshuffled_playlist = None
                    if current_track is not None:
                        try:
                            for idx, t in enumerate(self._playlist):
                                if t is current_track:
                                    self._current_index = idx
                                    break
                            else:
                                self._current_index = self._playlist.index(current_track)
                        except ValueError:
                            self._current_index = max(0, min(self._current_index, len(self._playlist) - 1))
                    self._shuffle_order = list(range(len(self._playlist)))
                    self.playlist_updated.emit()

            self.shuffle_changed.emit(self._shuffle)

    def toggle_shuffle(self) -> None:
        """Active ou désactive la lecture aléatoire."""
        self.set_shuffle(not self._shuffle)

    def set_repeat_mode(self, mode: int) -> None:
        """Définit le mode de répétition (RepeatMode.OFF, ALL, ONE)."""
        new_mode = mode % 3
        if self._repeat_mode != new_mode:
            self._repeat_mode = new_mode
            self.repeat_changed.emit(self._repeat_mode)

    def toggle_repeat(self) -> None:
        """Bascule le mode de répétition : OFF -> ALL -> ONE -> OFF."""
        self.set_repeat_mode((self._repeat_mode + 1) % 3)

    # -------------------------------------------------------------------------
    # Transitions fluides (Gapless & Fondu enchaîné)
    # -------------------------------------------------------------------------

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
            self._standby_player.set_media(media)
            self._standby_player.audio_set_volume(0)
            self._preloaded_index = index
            logger.debug("Piste suivante préchargée en standby (index %d) : %s", index, track.title)
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

            # Verrouiller le volume nominal sur le nouveau lecteur principal
            self._volume_enforce_ticks = 15
            self._enforce_volume()
            QTimer.singleShot(50, self._enforce_volume)
            QTimer.singleShot(150, self._enforce_volume)

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
            fade_sec = cfg.get_crossfade_duration()
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

        if not self._is_crossfading:
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

    def _rebuild_shuffle_order(self) -> None:
        self._shuffle_order = list(range(len(self._playlist)))
