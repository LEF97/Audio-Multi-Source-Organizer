"""Sortie audio factice pour la non-régression des transitions : consomme en temps réel et enregistre ce qui serait joué.

Remplace `QAudioSink` dans `ContinuousAudioEngine`. Si le moteur n'alimente pas la sortie à temps, la carte son
jouerait du silence : on insère ce silence dans l'enregistrement (`underruns`) pour que l'analyse l'entende comme un
trou, exactement comme à l'oreille.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from PySide6.QtCore import QByteArray

from amso.core.pcm_mixer import BYTES_PER_FRAME, SAMPLE_RATE, bytes_to_ms

BYTES_PER_SECOND = SAMPLE_RATE * BYTES_PER_FRAME


@dataclass(slots=True)
class Underrun:
    output_ms: float  # position dans la sortie où le silence a été inséré
    duration_ms: float


@dataclass(slots=True)
class CaptureSink:
    buffer_bytes: int = 32768
    output: bytearray = field(default_factory=bytearray)
    underruns: list[Underrun] = field(default_factory=list)
    start_count: int = 0
    stop_count: int = 0
    _queued: int = 0
    _deficit: int = 0
    _last: float | None = None
    _running: bool = False
    _suspended: bool = False
    _has_data: bool = False

    def _advance(self) -> None:
        now = time.monotonic()
        last, self._last = self._last, now
        if last is None or not self._running or self._suspended:
            return
        want = int((now - last) * BYTES_PER_SECOND) // BYTES_PER_FRAME * BYTES_PER_FRAME
        take = min(want, self._queued)
        self._queued -= take
        if self._has_data:
            self._deficit += want - take

    def start(self) -> _CaptureIO:
        self.start_count += 1
        self._running = True
        self._queued = 0
        self._last = time.monotonic()
        return _CaptureIO(self)

    def stop(self) -> None:
        # Seules les fermetures pendant la lecture comptent : l'arrêt initial d'un moteur au repos est sans effet.
        self.stop_count += self._running
        self._running = False
        self._queued = 0
        self._deficit = 0

    def suspend(self) -> None:
        self._advance()
        self._suspended = True

    def resume(self) -> None:
        self._advance()
        self._suspended = False

    def bytesFree(self) -> int:
        self._advance()
        return max(0, self.buffer_bytes - self._queued)

    def setVolume(self, volume: float) -> None:
        return None

    def setBufferSize(self, size: int) -> None:
        self.buffer_bytes = size

    def write(self, data: QByteArray) -> int:
        self._advance()
        raw = bytes(data)
        count = min(len(raw), self.bytesFree()) // BYTES_PER_FRAME * BYTES_PER_FRAME
        if count <= 0:
            return 0
        if self._deficit >= BYTES_PER_FRAME:
            missing = self._deficit // BYTES_PER_FRAME * BYTES_PER_FRAME
            self.underruns.append(Underrun(bytes_to_ms(len(self.output)), bytes_to_ms(missing)))
            self.output.extend(bytes(missing))
        self._deficit = 0
        self._has_data = True
        self.output.extend(raw[:count])
        self._queued += count
        return count

    @property
    def output_ms(self) -> float:
        return bytes_to_ms(len(self.output))


class _CaptureIO:
    """Équivalent du QIODevice retourné par `QAudioSink.start()`."""

    def __init__(self, sink: CaptureSink) -> None:
        self._sink = sink

    def write(self, data: QByteArray) -> int:
        return self._sink.write(data)
