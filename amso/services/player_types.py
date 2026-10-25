"""Types simples partagés par le lecteur audio."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject

from amso.core.database import TrackRecord


class RepeatMode:
    """Modes de répétition de la playlist."""

    OFF = 0  # Pas de répétition (s'arrête à la fin de la playlist)
    ALL = 1  # Répéter toute la playlist
    ONE = 2  # Répéter en boucle la piste active


class PlayerStateBase(QObject):
    """Déclaration typée de l'état de PlayerService (utilisée uniquement pour le typage des mixins)."""

    _playlist: list[TrackRecord]
    _unshuffled_playlist: list[TrackRecord] | None
    _current_index: int
    _shuffle: bool
    _shuffle_order: list[int]
    _repeat_mode: int
    _volume: int
    _is_muted: bool
    _is_temporary_volume: bool
    _last_set_volume: int
    _volume_enforce_ticks: int
    _is_seeking: bool
    _pending_seek_ms: int
    _current_time_ms: int
    _total_time_ms: int
    _is_paused_requested: bool
    _standby_player: Any
    _preloaded_index: int | None
    _is_crossfading: bool
    _crossfade_next_index: int | None
    _fade_start_time: float
    _fade_duration_sec: float
    _fade_paused_elapsed: float
    _vlc_instance: Any
    _media_player: Any
    _is_fading_in: bool
    _fade_in_start_time: float
    _fade_in_duration: float
    _last_fade_curr_vol: int | None
    _last_fade_next_vol: int | None
    _engine: Any
    _decoder: Any
    _standby_decoder: Any
    _standby_pcm: bytearray
    gapless_directsound_latency_ms: int
    _is_draining_standard_end: bool
