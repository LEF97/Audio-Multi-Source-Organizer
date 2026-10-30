"""Sortie audio factice pour la non-régression des transitions : consomme en temps réel et enregistre ce qui serait joué.

Remplace `SinkOutput` dans `ContinuousAudioEngine`. Comme la vraie sortie, elle tire le PCM depuis un thread à elle
(`read_pcm`) : si le moteur n'a pas de données à temps, la carte son jouerait du silence. Ce silence est conservé
dans l'enregistrement et signalé dans `underruns`, pour que l'analyse l'entende comme un trou, exactement comme à
l'oreille.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass

from amso.core.pcm_mixer import BYTES_PER_FRAME, SAMPLE_RATE, bytes_to_ms

BYTES_PER_SECOND = SAMPLE_RATE * BYTES_PER_FRAME
PULL_INTERVAL_S = 0.010


@dataclass(slots=True)
class Underrun:
    output_ms: float  # position dans la sortie où le silence a été inséré
    duration_ms: float


class CaptureOutput:
    available = True

    def __init__(self, read_pcm: Callable[[int], tuple[bytes, int]]) -> None:
        self._read_pcm = read_pcm
        self.output = bytearray()
        self.underruns: list[Underrun] = []
        self.start_count = 0
        self.stop_count = 0
        self._running = False
        self._suspended = False
        self._has_data = False
        self._starving = False
        self._last: float | None = None
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, name="tnr-capture-output", daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop_event.wait(PULL_INTERVAL_S):
            self._pull()

    def _pull(self) -> None:
        with self._lock:
            now = time.monotonic()
            last, self._last = self._last, now
            if last is None or not self._running or self._suspended:
                return
            want = int((now - last) * BYTES_PER_SECOND) // BYTES_PER_FRAME * BYTES_PER_FRAME
            if want <= 0:
                self._last = last
                return
            data, padded = self._read_pcm(want)
            if padded >= want and not self._has_data:
                return  # rien n'a encore été joué : pas de trou à signaler
            self._has_data = True
            if padded:
                if not self._starving:
                    self.underruns.append(Underrun(bytes_to_ms(len(self.output) + want - padded), 0.0))
                self.underruns[-1].duration_ms += bytes_to_ms(padded)
            self._starving = padded > 0
            self.output.extend(data)

    # Interface de SinkOutput
    def start(self, paused: bool = False) -> None:
        with self._lock:
            self.start_count += 1
            self._running = True
            self._suspended = paused
            self._has_data = False
            self._starving = False
            self._last = time.monotonic()

    def stop(self) -> None:
        with self._lock:
            # Seules les fermetures pendant la lecture comptent : l'arrêt initial d'un moteur au repos est sans effet.
            self.stop_count += self._running
            self._running = False

    def suspend(self) -> None:
        self._pull()
        with self._lock:
            self._suspended = True

    def resume(self) -> None:
        with self._lock:
            self._suspended = False
            self._last = time.monotonic()

    def set_volume(self, volume: float) -> None:
        return None

    def shutdown(self) -> None:
        self._stop_event.set()

    @property
    def output_ms(self) -> float:
        return bytes_to_ms(len(self.output))
