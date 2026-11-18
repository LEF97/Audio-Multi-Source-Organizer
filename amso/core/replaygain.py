"""Lecture des tags ReplayGain et normalisation PCM Int16 (logique pure, sans Qt)."""

from __future__ import annotations

import logging
import re

import numpy as np

from amso.core.pcm_mixer import BYTES_PER_SAMPLE

logger = logging.getLogger(__name__)

_GAIN_RE = re.compile(r"([+-]?\d+(?:[.,]\d+)?)")
_MIN_GAIN_DB = -18.0
_MAX_GAIN_DB = 12.0


def parse_replaygain_db(raw_value: object) -> float | None:
    """Extrait une valeur en dB depuis un tag ReplayGain (ex: '-6.42 dB')."""
    if raw_value is None:
        return None
    text = str(raw_value).strip()
    match = _GAIN_RE.search(text)
    if not match:
        return None
    try:
        db = float(match.group(1).replace(",", "."))
        return max(_MIN_GAIN_DB, min(_MAX_GAIN_DB, db))
    except ValueError:
        return None


def read_replaygain_db(file_path: str) -> float:
    """Lit REPLAYGAIN_TRACK_GAIN depuis les tags audio ; retourne 0.0 si absent."""
    if not file_path:
        return 0.0
    try:
        import mutagen

        audio = mutagen.File(file_path, easy=False)
    except Exception as exc:
        logger.debug("Impossible de lire ReplayGain pour %s : %s", file_path, exc)
        return 0.0
    if audio is None or not getattr(audio, "tags", None):
        return 0.0

    tags = audio.tags
    for key in (
        "REPLAYGAIN_TRACK_GAIN",
        "replaygain_track_gain",
        "TXXX:REPLAYGAIN_TRACK_GAIN",
        "TXXX:replaygain_track_gain",
        "----:com.apple.iTunes:replaygain_track_gain",
        "----:com.apple.iTunes:REPLAYGAIN_TRACK_GAIN",
    ):
        if key in tags:
            val = tags[key]
            first = val[0] if isinstance(val, (list, tuple)) and val else val
            if isinstance(first, bytes):
                first = first.decode("utf-8", errors="ignore")
            parsed = parse_replaygain_db(first)
            if parsed is not None:
                return parsed
    return 0.0


def replaygain_db_to_linear(gain_db: float) -> float:
    """Convertit un gain ReplayGain en dB vers un multiplicateur linéaire borné."""
    clamped = max(_MIN_GAIN_DB, min(_MAX_GAIN_DB, float(gain_db)))
    return float(10.0 ** (clamped / 20.0))


def apply_gain_pcm(pcm: bytes, gain_linear: float) -> bytes:
    """Applique un gain linéaire sur un bloc PCM Int16 avec saturation sans débordement."""
    if not pcm or abs(gain_linear - 1.0) < 1e-3:
        return pcm
    count = len(pcm) // BYTES_PER_SAMPLE
    if count == 0:
        return pcm
    arr = np.frombuffer(pcm, dtype="<i2", count=count).astype(np.float32)
    arr *= float(gain_linear)
    np.clip(arr, -32768.0, 32767.0, out=arr)
    return arr.astype("<i2").tobytes()
