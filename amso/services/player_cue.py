"""Lecture des pistes virtuelles CUE (portions d'un fichier audio) par le moteur à tampon continu.

Le moteur et le décodeur travaillent dans le temps relatif à la piste : position 0 = début de la portion, durée = durée
de la portion. Seul le décodage ajoute le décalage `cue_start_ms` dans le fichier source et s'arrête à `cue_end_ms`.
Chaque portion a son propre identifiant de flux (`stream_key`) : deux pistes CUE d'un même fichier se suivent donc sans
que leurs blocs PCM soient confondus.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amso.core.database import TrackRecord
    from amso.services.audio_decoder import AsyncAudioDecoder


def stream_key(track: TrackRecord) -> str:
    """Identifiant du flux d'une piste : son fichier, complété du début pour une piste CUE."""
    path = track.source_path or ""
    return f"{path}#cue{track.cue_start_ms}" if track.is_cue_segment else path


def start_track_decode(decoder: AsyncAudioDecoder, track: TrackRecord, seek_ms: int = 0) -> None:
    """Lance le décodage de `track` à partir de `seek_ms` (relatif au début de la piste)."""
    path = track.source_path or ""
    dur_ms = int((track.duration_seconds or 0) * 1000)
    if not track.is_cue_segment:
        decoder.start_decode(path, start_offset_ms=seek_ms, duration_ms=dur_ms)
        return
    start = track.cue_start_ms or 0
    stop = track.cue_end_ms or 0
    decoder.start_decode(
        path, start_offset_ms=start + seek_ms, duration_ms=dur_ms, stop_offset_ms=stop, key=stream_key(track)
    )
