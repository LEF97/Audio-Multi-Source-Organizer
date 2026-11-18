"""Le détecteur de pops de la TNR repère les coupures brutales et ignore les signaux continus ou fondus."""

from __future__ import annotations

import numpy as np

from tests.tnr.clicks import SAMPLE_RATE, find_discontinuities, find_silence_edges, jump_near


def _tone(seconds: float, freq: float = 60.0, amp: float = 12000.0) -> np.ndarray:
    t = np.arange(int(seconds * SAMPLE_RATE)) / SAMPLE_RATE
    mono = (amp * np.sin(2 * np.pi * freq * t)).astype("<i2")
    return np.stack([mono, mono], axis=1)


def _with_cut(tone: np.ndarray, at_frame: int, fade_frames: int = 0) -> np.ndarray:
    out = tone.copy()
    if fade_frames:
        ramp = np.linspace(1.0, 0.0, fade_frames)[:, None]
        out[at_frame : at_frame + fade_frames] = (out[at_frame : at_frame + fade_frames] * ramp).astype("<i2")
        out[at_frame + fade_frames :] = 0
    else:
        out[at_frame:] = 0
    return out


def test_find_discontinuities_signal_continu_aucune_detection() -> None:
    assert find_discontinuities(_tone(1.0)) == []


def test_find_discontinuities_silence_aucune_detection() -> None:
    assert find_discontinuities(np.zeros((SAMPLE_RATE, 2), dtype="<i2")) == []


def test_find_discontinuities_coupure_en_pleine_onde_une_detection_a_la_bonne_position() -> None:
    tone = _tone(1.0)
    # quart de période d'un 60 Hz après le début d'une seconde : amplitude maximale, pas de passage par zéro
    cut = int(0.5 * SAMPLE_RATE + SAMPLE_RATE / 240)

    clicks = find_discontinuities(_with_cut(tone, cut))

    assert len(clicks) == 1
    assert abs(clicks[0].position_ms - cut * 1000 / SAMPLE_RATE) < 1.0


def test_find_discontinuities_coupure_avec_micro_fondu_aucune_detection() -> None:
    cut = int(0.5 * SAMPLE_RATE + SAMPLE_RATE / 240)

    assert find_discontinuities(_with_cut(_tone(1.0), cut, fade_frames=SAMPLE_RATE // 100)) == []


def test_find_discontinuities_reprise_abrupte_apres_silence_une_detection() -> None:
    tone = _tone(1.0)
    start = int(0.5 * SAMPLE_RATE + SAMPLE_RATE / 240)
    out = tone.copy()
    out[:start] = 0

    assert len(find_discontinuities(out)) == 1


def test_find_silence_edges_coupure_brutale_suivie_de_silence_une_detection() -> None:
    cut = int(0.5 * SAMPLE_RATE + SAMPLE_RATE / 240)

    edges = find_silence_edges(_with_cut(_tone(1.0), cut))

    assert len(edges) == 1
    assert edges[0].jump > 10000


def test_find_silence_edges_coupure_fondue_aucune_detection() -> None:
    cut = int(0.5 * SAMPLE_RATE + SAMPLE_RATE / 240)

    assert find_silence_edges(_with_cut(_tone(1.0), cut, fade_frames=SAMPLE_RATE // 100)) == []


def test_jump_near_coupure_connue_retrouve_la_position_et_un_rapport_eleve() -> None:
    cut = int(0.5 * SAMPLE_RATE + SAMPLE_RATE / 240)
    out = _tone(1.0)
    out[cut:] = _tone(1.0)[: len(out) - cut][::-1]  # reprise sur une autre phase : saut sans silence

    amplitude, position_ms, ratio = jump_near(out, cut * 1000 / SAMPLE_RATE)

    assert abs(position_ms - cut * 1000 / SAMPLE_RATE) < 1.0
    assert amplitude > 1000
    assert ratio > 10
