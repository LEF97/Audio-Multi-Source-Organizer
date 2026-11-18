"""Égaliseur graphique 10 bandes en Python/NumPy pur (zéro dépendance Qt).

Utilise des filtres biquad IIR (RBJ Audio EQ Cookbook, type peaking EQ) en cascade
sur du PCM Int16 stéréo 44100 Hz, avec conservation de l'état entre blocs consécutifs
pour éviter tout clic audio.
"""

from __future__ import annotations

import math
import threading

import numpy as np

from amso.core.pcm_mixer import SAMPLE_RATE

EQ_FREQUENCIES: tuple[int, ...] = (32, 64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000)
EQ_MIN_DB = -12.0
EQ_MAX_DB = 12.0
_BIQUAD_Q = 1.4142135623730951

EQ_PRESETS: dict[str, tuple[float, ...]] = {
    "flat": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    "rock": (4.5, 3.0, 1.5, -1.0, -1.5, 0.5, 2.5, 3.5, 4.0, 4.0),
    "jazz": (3.0, 2.0, 1.0, 1.5, -1.5, -1.5, 0.0, 1.5, 2.5, 3.0),
    "classical": (4.0, 3.0, 2.0, 1.0, -1.0, -1.0, 0.0, 2.0, 3.0, 3.5),
    "bass_boost": (6.0, 5.0, 3.5, 1.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    "vocal": (-2.0, -2.0, -1.0, 1.5, 3.5, 4.0, 3.0, 1.5, 0.0, -1.0),
    "electronic": (4.5, 3.5, 1.0, 0.0, -1.5, 1.5, 1.0, 2.5, 4.0, 4.5),
}


def compute_peaking_coeffs(
    freq_hz: float,
    gain_db: float,
    sample_rate: int = SAMPLE_RATE,
    q: float = _BIQUAD_Q,
) -> tuple[float, float, float, float, float]:
    """Calcule les coefficients biquad normalisés (b0, b1, b2, a1, a2) d'un filtre peaking EQ."""
    if abs(gain_db) < 1e-3:
        return (1.0, 0.0, 0.0, 0.0, 0.0)
    a_amp = 10.0 ** (gain_db / 40.0)
    omega = 2.0 * math.pi * freq_hz / float(sample_rate)
    sin_w = math.sin(omega)
    cos_w = math.cos(omega)
    alpha = sin_w / (2.0 * q)

    b0 = 1.0 + alpha * a_amp
    b1 = -2.0 * cos_w
    b2 = 1.0 - alpha * a_amp
    a0 = 1.0 + alpha / a_amp
    a1 = -2.0 * cos_w
    a2 = 1.0 - alpha / a_amp
    return (b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)


def _apply_biquad_channel(
    samples: list[float],
    coeffs: tuple[float, float, float, float, float],
    z1: float,
    z2: float,
) -> tuple[list[float], float, float]:
    b0, b1, b2, a1, a2 = coeffs
    out = [0.0] * len(samples)
    for idx, x in enumerate(samples):
        y = b0 * x + z1
        z1 = b1 * x - a1 * y + z2
        z2 = b2 * x - a2 * y
        out[idx] = y
    return out, z1, z2


class Equalizer10Band:
    """Égaliseur graphique 10 bandes thread-safe pour flux PCM Int16 stéréo."""

    def __init__(self, sample_rate: int = SAMPLE_RATE) -> None:
        self._sample_rate = sample_rate
        self._lock = threading.Lock()
        self._enabled = False
        self._gains: list[float] = [0.0] * len(EQ_FREQUENCIES)
        self._coeffs: list[tuple[float, float, float, float, float]] = [
            (1.0, 0.0, 0.0, 0.0, 0.0) for _ in EQ_FREQUENCIES
        ]
        self._active_indices: list[int] = []
        # État (z1, z2) par bande et par canal (0=gauche, 1=droite)
        self._state_l: list[tuple[float, float]] = [(0.0, 0.0) for _ in EQ_FREQUENCIES]
        self._state_r: list[tuple[float, float]] = [(0.0, 0.0) for _ in EQ_FREQUENCIES]

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def gains(self) -> list[float]:
        with self._lock:
            return list(self._gains)

    def set_enabled(self, enabled: bool) -> None:
        with self._lock:
            if self._enabled != enabled:
                self._enabled = bool(enabled)
                if not self._enabled:
                    self._reset_states_locked()

    def set_gains(self, gains: list[float]) -> None:
        clamped = [max(EQ_MIN_DB, min(EQ_MAX_DB, float(g))) for g in (gains[:10] + [0.0] * 10)[:10]]
        coeffs = [
            compute_peaking_coeffs(freq, g, self._sample_rate) for freq, g in zip(EQ_FREQUENCIES, clamped, strict=True)
        ]
        active = [i for i, g in enumerate(clamped) if abs(g) >= 0.05]
        with self._lock:
            self._gains = clamped
            self._coeffs = coeffs
            self._active_indices = active

    def reset_state(self) -> None:
        with self._lock:
            self._reset_states_locked()

    def _reset_states_locked(self) -> None:
        self._state_l = [(0.0, 0.0) for _ in EQ_FREQUENCIES]
        self._state_r = [(0.0, 0.0) for _ in EQ_FREQUENCIES]

    def process_pcm(self, pcm: bytes) -> bytes:
        """Applique l'égaliseur sur un bloc PCM Int16 stéréo ; passe-plat si inactif."""
        if not pcm:
            return pcm
        with self._lock:
            if not self._enabled or not self._active_indices:
                return pcm
            active = list(self._active_indices)
            coeffs = [self._coeffs[i] for i in active]
            states_l = [self._state_l[i] for i in active]
            states_r = [self._state_r[i] for i in active]

        arr = np.frombuffer(pcm, dtype=np.int16).astype(np.float32)
        if arr.size < 2:
            return pcm
        left = arr[0::2].tolist()
        right = arr[1::2].tolist()

        new_states_l: list[tuple[float, float]] = []
        new_states_r: list[tuple[float, float]] = []
        for c, (zl1, zl2), (zr1, zr2) in zip(coeffs, states_l, states_r, strict=True):
            left, zl1, zl2 = _apply_biquad_channel(left, c, zl1, zl2)
            right, zr1, zr2 = _apply_biquad_channel(right, c, zr1, zr2)
            new_states_l.append((zl1, zl2))
            new_states_r.append((zr1, zr2))

        with self._lock:
            for idx, st_l, st_r in zip(active, new_states_l, new_states_r, strict=True):
                self._state_l[idx] = st_l
                self._state_r[idx] = st_r

        out = np.empty(arr.size, dtype=np.float32)
        out[0::2] = left
        out[1::2] = right
        np.clip(out, -32768.0, 32767.0, out=out)
        return out.astype(np.int16).tobytes()
