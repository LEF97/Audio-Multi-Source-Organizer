"""Lecture des pistes virtuelles CUE (portions d'un fichier audio) par le moteur à tampon continu.

Le moteur et le décodeur travaillent dans le temps relatif à la piste : position 0 = début de la portion, durée = durée
de la portion. Seul le décodage ajoute le décalage `cue_start_ms` dans le fichier source et s'arrête à `cue_end_ms`.
Chaque portion a son propre identifiant de flux (`stream_key`) : deux pistes CUE d'un même fichier se suivent donc sans
que leurs blocs PCM soient confondus.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from amso.services.cue_continuation import continuation_after

if TYPE_CHECKING:
    from amso.core.database import TrackRecord
    from amso.services.audio_decoder import AsyncAudioDecoder
    from amso.services.audio_engine import ContinuousAudioEngine


def stream_key(track: TrackRecord) -> str:
    """Identifiant du flux d'une piste : son fichier, complété du début pour une piste CUE."""
    path = track.source_path or ""
    return f"{path}#cue{track.cue_start_ms}" if track.is_cue_segment else path


def start_track_decode(
    decoder: AsyncAudioDecoder, track: TrackRecord, seek_ms: int = 0, following: Sequence[TrackRecord] = ()
) -> None:
    """Lance le décodage de `track` à partir de `seek_ms` (relatif au début de la piste).

    `following` : pistes CUE contiguës décodées dans le même flux ; le décodage s'arrête à la fin de la dernière.
    """
    path = track.source_path or ""
    dur_ms = int((track.duration_seconds or 0) * 1000)
    if not track.is_cue_segment:
        decoder.start_decode(path, start_offset_ms=seek_ms, duration_ms=dur_ms)
        return
    start = track.cue_start_ms or 0
    stop = (following[-1] if following else track).cue_end_ms or 0
    decoder.start_decode(
        path, start_offset_ms=start + seek_ms, duration_ms=dur_ms, stop_offset_ms=stop, key=stream_key(track)
    )


def start_track_run(
    engine: ContinuousAudioEngine,
    decoder: AsyncAudioDecoder,
    playlist: Sequence[TrackRecord],
    index: int,
    seek_ms: int = 0,
    chain_next: bool = True,
) -> None:
    """Décode `playlist[index]` et, pour une piste CUE, les pistes contiguës du même fichier dans un seul flux.

    Le moteur doit avoir été arrêté (ou son tampon réinitialisé) avant : il efface ses frontières à ce moment-là.
    `chain_next=False` (répétition d'une piste) : la suivante est la piste elle-même, rien à enchaîner.
    """
    following = continuation_after(playlist, index) if chain_next else []
    start_track_decode(decoder, playlist[index], seek_ms, following)
    engine.arm_cue_continuation([int((t.duration_seconds or 0) * 1000) for t in following])


# Un flux CUE se décode en temps réel jusqu'à la fin de la suite de pistes : en pause, l'avance sur la lecture grossirait
# sans limite (~10 Mo par minute). Au-delà de MAX, le décodeur est suspendu ; il reprend sous RESUME (marge pour que la
# lecture ne manque jamais de PCM le temps de la reprise).
MAX_DECODE_LEAD_MS = 20_000
RESUME_DECODE_LEAD_MS = 10_000


def limit_decode_lead(engine: ContinuousAudioEngine, decoder: AsyncAudioDecoder) -> None:
    """Suspend le décodage d'un flux CUE trop en avance sur la lecture, le reprend quand l'avance retombe."""
    if not engine.cue_continues:
        decoder.set_throttled(False)
        return
    lead_ms = engine.buffered_ahead_ms
    if lead_ms > MAX_DECODE_LEAD_MS:
        decoder.set_throttled(True)
    elif lead_ms < RESUME_DECODE_LEAD_MS:
        decoder.set_throttled(False)
