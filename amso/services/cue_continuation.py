"""Enchaînement continu des pistes CUE d'un même fichier dans le moteur à tampon.

Un seek LibVLC sur un MP3 en débit variable tombe à plusieurs centaines de millisecondes (parfois secondes) de la cible
demandée. Relancer un décodage à chaque piste CUE faisait donc rejouer la fin de la piste précédente. Ici le fichier est
décodé une seule fois pour toute une suite de pistes contiguës ; les frontières sont des positions en octets dans le
tampon PCM, calculées depuis les durées du CUE, donc indépendantes de la précision du seek.
"""

from __future__ import annotations

import os
from collections import deque
from collections.abc import Sequence
from typing import TYPE_CHECKING

from amso.core.pcm_mixer import ms_to_bytes

if TYPE_CHECKING:
    from amso.core.database import TrackRecord


def continues_stream(current: TrackRecord, following: TrackRecord) -> bool:
    """Vrai si `following` prolonge le décodage de `current` sans trou ni recouvrement dans le fichier source."""
    if not (current.is_cue_segment and following.is_cue_segment):
        return False
    if current.cue_end_ms is None or current.cue_end_ms != following.cue_start_ms:
        return False
    left = os.path.normcase(os.path.normpath(current.source_path or ""))
    right = os.path.normcase(os.path.normpath(following.source_path or ""))
    return bool(left) and left == right


def continuation_after(playlist: Sequence[TrackRecord], index: int) -> list[TrackRecord]:
    """Pistes qui suivent `playlist[index]` dans le même flux de décodage (ordre de la file, sans saut)."""
    run: list[TrackRecord] = []
    previous = playlist[index]
    for track in playlist[index + 1 :]:
        if not continues_stream(previous, track):
            break
        run.append(track)
        previous = track
    return run


class CueContinuation:
    """Durées des pistes à enchaîner dans le flux en cours ; la frontière de la piste courante se déduit de sa durée."""

    def __init__(self) -> None:
        self._next_durations_ms: deque[int] = deque()

    def arm(self, durations_ms: Sequence[int]) -> None:
        self._next_durations_ms = deque(durations_ms)

    def clear(self) -> None:
        self._next_durations_ms.clear()

    @property
    def active(self) -> bool:
        return bool(self._next_durations_ms)

    def crossing(self, play_offset: int, total_ms: int, base_ms: int) -> tuple[int, int] | None:
        """Si la lecture a franchi la fin de la piste courante : (octets à retirer du tampon, durée de la piste suivante).

        `base_ms` est la position de la piste correspondant au premier octet du tampon (non nulle après un seek).
        """
        if not self._next_durations_ms:
            return None
        boundary = ms_to_bytes(total_ms - base_ms)
        if boundary <= 0 or play_offset < boundary:
            return None
        return boundary, self._next_durations_ms.popleft()
