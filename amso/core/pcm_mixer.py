"""Mixage PCM Int16 stéréo des transitions du moteur à tampon continu (logique pure, sans Qt).

Le moteur manipule des octets Int16 stéréo entrelacés à 44,1 kHz. Isoler le calcul ici permet de le tester sans
carte son et de le vectoriser : une boucle Python par échantillon, exécutée sous verrou dans le thread UI, vidait le
tampon de la carte son (~185 ms) et provoquait des saccades pendant les fondus.
"""

from __future__ import annotations

import numpy as np

SAMPLE_RATE = 44100
CHANNELS = 2
BYTES_PER_SAMPLE = 2
BYTES_PER_FRAME = CHANNELS * BYTES_PER_SAMPLE


def ms_to_bytes(duration_ms: float) -> int:
    """Convertit une durée en octets PCM, alignée sur une frame stéréo entière."""
    return int(duration_ms / 1000.0 * SAMPLE_RATE) * BYTES_PER_FRAME


def bytes_to_ms(num_bytes: int) -> float:
    return num_bytes / BYTES_PER_FRAME / SAMPLE_RATE * 1000.0


def silence(duration_ms: float) -> bytes:
    return bytes(ms_to_bytes(duration_ms))


def equal_power_mix(outgoing: bytes, incoming: bytes, start_frame: int, total_frames: int) -> bytes:
    """Mixe deux blocs de même longueur appartenant à un fondu de `total_frames` frames, à partir de `start_frame`.

    Gains cos/sin (puissance constante) évalués au centre de chaque frame : la courbe est symétrique
    (gain_a(i) == gain_b(n-1-i)), sans point à exactement 0 ni 1, ce qui évite un saut au raccord avec les données
    avant et après la zone. Un fondu traité en plusieurs blocs successifs donne le même résultat qu'en un seul.
    """
    if len(outgoing) != len(incoming):
        raise ValueError("Les deux blocs de fondu doivent avoir la même longueur")
    frames = len(outgoing) // BYTES_PER_FRAME
    if frames == 0:
        return b""
    usable = frames * BYTES_PER_FRAME
    a = np.frombuffer(outgoing, dtype="<i2", count=usable // BYTES_PER_SAMPLE).reshape(frames, CHANNELS)
    b = np.frombuffer(incoming, dtype="<i2", count=usable // BYTES_PER_SAMPLE).reshape(frames, CHANNELS)
    phase = (np.arange(start_frame, start_frame + frames, dtype=np.float64) + 0.5) / total_frames * (np.pi / 2.0)
    mixed = a * np.cos(phase)[:, None] + b * np.sin(phase)[:, None]
    return np.clip(np.rint(mixed), -32768, 32767).astype("<i2").tobytes()


def equal_power_crossfade(tail_a: bytes, head_b: bytes) -> bytes:
    """Mixe `tail_a` (sortant) et `head_b` (entrant) de même longueur sur toute la durée du fondu."""
    return equal_power_mix(tail_a, head_b, 0, max(1, len(tail_a) // BYTES_PER_FRAME))


class StreamingCrossfade:
    """Fondu croisé calculé au fil de l'arrivée des blocs décodés.

    Le décodeur livre l'audio au rythme de la lecture : la fin de la piste sortante n'existe pas en mémoire avant
    d'être décodée. Chaque bloc sortant est donc mixé à son arrivée avec la tête de la piste entrante, déjà préchargée.
    """

    def __init__(self, fade_bytes: int) -> None:
        self.total_frames = max(1, fade_bytes // BYTES_PER_FRAME)
        self.done_frames = 0
        self.incoming = bytearray()

    @property
    def complete(self) -> bool:
        return self.done_frames >= self.total_frames

    @property
    def mixed_ms(self) -> float:
        return self.done_frames / SAMPLE_RATE * 1000.0

    def mix_outgoing(self, chunk: bytes) -> tuple[bytes, int]:
        """Mixe le début de `chunk` ; retourne (octets mixés, octets sortants consommés).

        Si la piste entrante est plus courte que le bloc, elle est complétée par du silence : la piste sortante
        s'éteint seule plutôt que de rester à plein niveau.
        """
        frames = min(len(chunk) // BYTES_PER_FRAME, self.total_frames - self.done_frames)
        if frames <= 0:
            return b"", 0
        size = frames * BYTES_PER_FRAME
        head = bytes(self.incoming[:size])
        head += bytes(size - len(head))
        del self.incoming[:size]
        mixed = equal_power_mix(chunk[:size], head, self.done_frames, self.total_frames)
        self.done_frames += frames
        return mixed, size
