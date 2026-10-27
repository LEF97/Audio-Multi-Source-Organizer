"""Décodage de référence d'un fichier audio en PCM Int16 stéréo 44,1 kHz, plus rapide que le temps réel.

Le décodeur de lecture (LibVLC `amem`) livre l'audio au rythme de la lecture ; la référence passe par une
transcodage `sout` vers un WAV, indépendant du moteur testé, et mis en cache entre deux exécutions.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
import time
import wave
from pathlib import Path

import numpy as np

from amso.services.vlc_binding import vlc

CACHE_DIR = Path(tempfile.gettempdir()) / "amso_tnr_cache"
DECODE_TIMEOUT_S = 600.0


class ReferenceDecodeError(RuntimeError):
    pass


def _cache_path(source: Path) -> Path:
    stat = source.stat()
    digest = hashlib.sha1(f"{source}|{stat.st_size}|{stat.st_mtime_ns}".encode()).hexdigest()[:16]
    return CACHE_DIR / f"{digest}.wav"


def _transcode_to_wav(source: Path, target: Path) -> None:
    instance = vlc.Instance("--no-video", "--quiet")
    dst = str(target).replace("\\", "/")
    media = instance.media_new_path(os.path.normpath(source))
    media.add_option(
        f":sout=#transcode{{acodec=s16l,channels=2,samplerate=44100}}:std{{access=file,mux=wav,dst={dst}}}"
    )
    media.add_option(":no-sout-all")
    media.add_option(":sout-keep")
    player = instance.media_player_new()
    player.set_media(media)
    player.play()
    deadline = time.monotonic() + DECODE_TIMEOUT_S
    try:
        while time.monotonic() < deadline:
            time.sleep(0.1)
            state = player.get_state()
            if state in (vlc.State.Ended, vlc.State.Stopped):
                return
            if state == vlc.State.Error:
                break
    finally:
        player.stop()
        player.release()
    raise ReferenceDecodeError(f"Transcodage de référence impossible : {source}")


def load_reference(source: Path) -> np.ndarray:
    """Retourne le PCM de `source` en tableau (frames, 2) d'entiers 16 bits."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached = _cache_path(source)
    if not cached.exists():
        partial = cached.with_suffix(".part")
        partial.unlink(missing_ok=True)
        _transcode_to_wav(source, partial)
        partial.replace(cached)
    with wave.open(str(cached), "rb") as wav:
        if wav.getnchannels() != 2 or wav.getsampwidth() != 2 or wav.getframerate() != 44100:
            raise ReferenceDecodeError(f"Format de référence inattendu pour {source}")
        raw = wav.readframes(wav.getnframes())
    return np.frombuffer(raw, dtype="<i2").reshape(-1, 2)
