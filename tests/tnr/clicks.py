"""Détection des discontinuités brutales (« pop ») dans un enregistrement de la sortie audio.

Un pop est un saut d'amplitude d'un échantillon au suivant très supérieur à la variation habituelle autour de lui :
coupure d'un son en pleine onde, reprise abrupte après un silence. La musique réelle a des attaques franches, d'où
deux détecteurs :
- `find_silence_edges` : bords d'un silence numérique exact (coupure ou reprise sans fondu), très spécifique ;
- `find_discontinuities` : saut local sans silence, sensible aux attaques musicales, à réserver à un point connu
  (`jump_near`) plutôt qu'à un balayage de toute la piste.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

SAMPLE_RATE = 44100
MIN_JUMP = 800  # saut minimal (échelle 16 bits) en deçà duquel rien n'est audible
NEIGHBOURHOOD = SAMPLE_RATE // 50  # 20 ms de part et d'autre pour estimer la variation habituelle
RATIO = 10.0  # saut / variation moyenne du voisinage
MERGE_FRAMES = SAMPLE_RATE // 200  # des sauts distants de moins de 5 ms forment un seul événement


@dataclass(slots=True)
class Click:
    position_ms: float
    jump: int  # amplitude du saut (16 bits)
    ratio: float


def find_discontinuities(frames: np.ndarray, min_jump: int = MIN_JUMP, ratio: float = RATIO) -> list[Click]:
    """Retourne les discontinuités de `frames` (tableau (n, 2) d'entiers 16 bits), triées par position."""
    if len(frames) < 3:
        return []
    jumps = np.abs(np.diff(frames.astype(np.int32), axis=0)).max(axis=1).astype(np.float64)
    csum = np.concatenate(([0.0], np.cumsum(jumps)))
    idx = np.arange(len(jumps))
    lo = np.maximum(idx - NEIGHBOURHOOD, 0)
    hi = np.minimum(idx + NEIGHBOURHOOD + 1, len(jumps))
    # voisinage sans le saut lui-même : un pic isolé ne doit pas relever sa propre référence
    local = (csum[hi] - csum[lo] - jumps) / np.maximum(hi - lo - 1, 1)
    scores = jumps / (local + 50.0)
    flagged = np.nonzero((jumps >= min_jump) & (scores >= ratio))[0]
    clicks: list[Click] = []
    last = -MERGE_FRAMES - 1
    for pos in flagged:
        if pos - last > MERGE_FRAMES:
            clicks.append(Click(pos * 1000.0 / SAMPLE_RATE, int(jumps[pos]), float(scores[pos])))
        last = int(pos)
    return clicks


def find_silence_edges(frames: np.ndarray, min_run_ms: float = 2.0, min_edge: int = 200, floor: int = 0) -> list[Click]:
    """Bords des silences numériques exacts d'au moins `min_run_ms` dont l'amplitude de bord dépasse `min_edge`.

    Une coupure fondue finit à quelques unités de zéro ; une coupure brutale laisse l'amplitude du signal au bord.
    """
    peak = np.abs(frames.astype(np.int32)).max(axis=1)
    quiet = peak <= floor
    min_run = int(min_run_ms * SAMPLE_RATE / 1000)
    padded = np.concatenate(([False], quiet, [False]))
    starts = np.nonzero(~padded[:-2] & padded[1:-1])[0]
    ends = np.nonzero(padded[1:-1] & ~padded[2:])[0] + 1
    clicks: list[Click] = []
    for start, end in zip(starts, ends, strict=True):
        if end - start < min_run:
            continue
        if start > 0 and int(peak[start - 1]) >= min_edge:
            clicks.append(Click(start * 1000.0 / SAMPLE_RATE, int(peak[start - 1]), float("inf")))
        if end < len(peak) and int(peak[end]) >= min_edge:
            clicks.append(Click(end * 1000.0 / SAMPLE_RATE, int(peak[end]), float("inf")))
    return sorted(clicks, key=lambda c: c.position_ms)


def jump_near(frames: np.ndarray, position_ms: float, window_ms: float = 30.0) -> tuple[int, float, float]:
    """Plus grand saut d'échantillon près de `position_ms` : (amplitude, position en ms, rapport au voisinage)."""
    jumps = np.abs(np.diff(frames.astype(np.int32), axis=0)).max(axis=1)
    centre = int(position_ms * SAMPLE_RATE / 1000)
    half = int(window_ms * SAMPLE_RATE / 1000)
    lo, hi = max(centre - half, 0), min(centre + half, len(jumps))
    best = lo + int(np.argmax(jumps[lo:hi]))
    around = np.concatenate((jumps[max(best - NEIGHBOURHOOD, 0) : best], jumps[best + 1 : best + NEIGHBOURHOOD]))
    return int(jumps[best]), best * 1000.0 / SAMPLE_RATE, float(jumps[best] / (around.mean() + 50.0))
