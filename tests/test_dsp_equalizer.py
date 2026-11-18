"""Tests unitaires pour l'égaliseur graphique 10 bandes (DSP PCM Int16)."""

from __future__ import annotations

import math

import numpy as np

from amso.core.dsp_equalizer import EQ_PRESETS, Equalizer10Band


def _sine_pcm(freq_hz: float, duration_s: float = 0.2, amp: float = 8000.0, sample_rate: int = 44100) -> bytes:
    n_samples = int(sample_rate * duration_s)
    t = np.arange(n_samples, dtype=np.float32) / float(sample_rate)
    wave = (amp * np.sin(2.0 * math.pi * freq_hz * t)).astype(np.int16)
    stereo = np.empty(n_samples * 2, dtype=np.int16)
    stereo[0::2] = wave
    stereo[1::2] = wave
    return stereo.tobytes()


def _rms(pcm: bytes) -> float:
    arr = np.frombuffer(pcm, dtype=np.int16).astype(np.float64)
    return float(np.sqrt(np.mean(arr * arr)))


def test_equalizer_passthrough_when_disabled_or_flat() -> None:
    eq = Equalizer10Band()
    pcm = _sine_pcm(1000.0)
    assert eq.process_pcm(pcm) == pcm

    eq.set_enabled(True)
    assert eq.process_pcm(pcm) == pcm  # toutes les bandes à 0 dB


def test_equalizer_boost_and_cut_at_1khz() -> None:
    pcm = _sine_pcm(1000.0, duration_s=0.3)
    base_rms = _rms(pcm)

    eq_boost = Equalizer10Band()
    eq_boost.set_gains([0.0, 0.0, 0.0, 0.0, 0.0, 9.0, 0.0, 0.0, 0.0, 0.0])  # bande 1 kHz = index 5
    eq_boost.set_enabled(True)
    boosted_rms = _rms(eq_boost.process_pcm(pcm))
    assert boosted_rms > base_rms * 1.8

    eq_cut = Equalizer10Band()
    eq_cut.set_gains([0.0, 0.0, 0.0, 0.0, 0.0, -9.0, 0.0, 0.0, 0.0, 0.0])
    eq_cut.set_enabled(True)
    cut_rms = _rms(eq_cut.process_pcm(pcm))
    assert cut_rms < base_rms * 0.6


def test_equalizer_chunk_continuity_matches_single_pass() -> None:
    pcm = _sine_pcm(1000.0, duration_s=0.2)
    gains = list(EQ_PRESETS["rock"])

    eq_whole = Equalizer10Band()
    eq_whole.set_gains(gains)
    eq_whole.set_enabled(True)
    whole_out = eq_whole.process_pcm(pcm)

    eq_chunked = Equalizer10Band()
    eq_chunked.set_gains(gains)
    eq_chunked.set_enabled(True)
    mid = (len(pcm) // 4) * 2  # aligné sur une trame stéréo (4 octets)
    chunked_out = eq_chunked.process_pcm(pcm[:mid]) + eq_chunked.process_pcm(pcm[mid:])

    assert whole_out == chunked_out


def test_equalizer_clamps_extreme_signal_without_overflow() -> None:
    pcm = _sine_pcm(64.0, duration_s=0.1, amp=32000.0)
    eq = Equalizer10Band()
    eq.set_gains([12.0] * 10)
    eq.set_enabled(True)
    out = eq.process_pcm(pcm)
    assert len(out) == len(pcm)
    arr = np.frombuffer(out, dtype=np.int16)
    assert int(arr.max()) <= 32767
    assert int(arr.min()) >= -32768
