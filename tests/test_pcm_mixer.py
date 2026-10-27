"""Tests du mixage PCM des transitions et du fondu croisé au fil du décodage (sans carte son)."""

from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtCore import QCoreApplication

from amso.core.pcm_mixer import (
    BYTES_PER_FRAME,
    SAMPLE_RATE,
    StreamingCrossfade,
    equal_power_crossfade,
    equal_power_mix,
    ms_to_bytes,
)
from amso.services.audio_engine import ContinuousAudioEngine


def _tone(frames: int, level: int) -> bytes:
    return np.full((frames, 2), level, dtype="<i2").tobytes()


def _frames(pcm: bytes) -> np.ndarray:
    return np.frombuffer(pcm, dtype="<i2").reshape(-1, 2)


def test_equal_power_crossfade_constant_signals_keeps_constant_power() -> None:
    frames = SAMPLE_RATE
    mixed = _frames(equal_power_crossfade(_tone(frames, 10000), _tone(frames, 10000)))
    # Deux signaux identiques mixés à puissance égale : somme des gains = cos + sin, entre 1 et sqrt(2)
    assert mixed.min() >= 10000 - 1
    assert mixed.max() <= int(10000 * 2**0.5) + 1


def test_equal_power_crossfade_endpoints_follow_outgoing_then_incoming() -> None:
    frames = SAMPLE_RATE
    mixed = _frames(equal_power_crossfade(_tone(frames, 8000), _tone(frames, -8000)))
    assert mixed[0, 0] > 7900
    assert mixed[-1, 0] < -7900


def test_equal_power_crossfade_length_mismatch_raises() -> None:
    with pytest.raises(ValueError):
        equal_power_crossfade(_tone(10, 1), _tone(11, 1))


def test_equal_power_mix_chunked_equals_single_pass() -> None:
    rng = np.random.default_rng(1)
    a = rng.integers(-20000, 20000, size=(4000, 2), dtype="<i2").tobytes()
    b = rng.integers(-20000, 20000, size=(4000, 2), dtype="<i2").tobytes()
    whole = equal_power_mix(a, b, 0, 4000)
    cut = 1234 * BYTES_PER_FRAME
    parts = equal_power_mix(a[:cut], b[:cut], 0, 4000) + equal_power_mix(a[cut:], b[cut:], 1234, 4000)
    assert parts == whole


def test_streaming_crossfade_incoming_too_short_fades_outgoing_alone() -> None:
    fade = StreamingCrossfade(ms_to_bytes(100))
    fade.incoming.extend(_tone(10, 5000))
    mixed, used = fade.mix_outgoing(_tone(ms_to_bytes(100) // BYTES_PER_FRAME, 5000))
    out = _frames(mixed)
    assert used == len(mixed)
    assert abs(int(out[-1, 0])) < 100  # sortant éteint à la fin, sans reste à plein niveau


def test_streaming_crossfade_stops_consuming_at_end_of_fade() -> None:
    fade = StreamingCrossfade(ms_to_bytes(10))
    fade.incoming.extend(_tone(SAMPLE_RATE, 1000))
    mixed, used = fade.mix_outgoing(_tone(SAMPLE_RATE, 1000))
    assert fade.complete
    assert used == len(mixed) == ms_to_bytes(10)
    assert len(fade.incoming) == (SAMPLE_RATE - ms_to_bytes(10) // BYTES_PER_FRAME) * BYTES_PER_FRAME


@pytest.fixture
def engine() -> ContinuousAudioEngine:
    QCoreApplication.instance() or QCoreApplication([])
    return ContinuousAudioEngine()


def _start_track(engine: ContinuousAudioEngine, path: str, duration_ms: int) -> None:
    engine._current_file_path = path
    engine._total_duration_ms = duration_ms
    engine._base_offset_ms = 0
    engine._current_pcm = bytearray()


def test_engine_crossfade_mixes_last_seconds_of_outgoing_track_exactly(engine: ContinuousAudioEngine) -> None:
    _start_track(engine, "a.flac", 4000)
    engine.arm_crossfade(1000, "b.flac")
    engine.feed_crossfade_incoming(_tone(2 * SAMPLE_RATE, -6000))
    mixed_signals: list[bool] = []
    engine.crossfade_mixed.connect(lambda: mixed_signals.append(True))
    block = SAMPLE_RATE // 10 * BYTES_PER_FRAME
    for _ in range(40):  # 4 s de piste sortante livrée par blocs de 100 ms
        engine.append_chunk("a.flac", _tone(block // BYTES_PER_FRAME, 6000))

    pcm = _frames(bytes(engine._current_pcm))
    zone = 3 * SAMPLE_RATE
    assert mixed_signals == [True]
    assert engine._current_file_path == "b.flac"
    assert np.all(pcm[:zone] == 6000)  # sortante intacte jusqu'au début de la zone
    assert abs(int(pcm[zone, 0]) - 6000) < 200
    assert np.all(pcm[zone + SAMPLE_RATE :] == -6000)  # entrante seule ensuite, sans trou ni recouvrement
    assert engine._xfade_end_offset == (zone + SAMPLE_RATE) * BYTES_PER_FRAME


def test_engine_crossfade_split_inside_chunk_is_sample_exact(engine: ContinuousAudioEngine) -> None:
    _start_track(engine, "a.flac", 1000)
    engine.arm_crossfade(500, "b.flac")
    engine.feed_crossfade_incoming(_tone(SAMPLE_RATE, 0))
    engine.append_chunk("a.flac", _tone(SAMPLE_RATE // 2 + 1000, 8000) + _tone(SAMPLE_RATE // 2 - 1000, 8000))
    pcm = _frames(bytes(engine._current_pcm))
    boundary = SAMPLE_RATE // 2
    assert np.all(pcm[:boundary] == 8000)
    assert 0 < pcm[boundary + 5000, 0] < 8000  # le fondu commence exactement à la frame prévue


def test_engine_crossfade_outgoing_ending_early_finalizes_with_incoming_tail(engine: ContinuousAudioEngine) -> None:
    _start_track(engine, "a.flac", 4000)
    engine.arm_crossfade(1000, "b.flac")
    engine.feed_crossfade_incoming(_tone(2 * SAMPLE_RATE, -6000))
    engine.append_chunk("a.flac", _tone(3 * SAMPLE_RATE + SAMPLE_RATE // 2, 6000))
    engine.mark_feed_complete("a.flac")
    assert engine._current_file_path == "b.flac"
    assert engine.crossfade_pending
    assert not engine.is_feed_complete


def test_engine_finish_crossfade_recalibrates_position_on_incoming_track(engine: ContinuousAudioEngine) -> None:
    _start_track(engine, "a.flac", 2000)
    engine.arm_crossfade(1000, "b.flac")
    engine.feed_crossfade_incoming(_tone(2 * SAMPLE_RATE, -6000))
    engine.append_chunk("a.flac", _tone(2 * SAMPLE_RATE, 6000))
    engine._play_offset = engine._xfade_end_offset or 0
    assert engine.crossfade_played_through()
    position = engine.finish_crossfade("b.flac", 5000)
    assert position == 1000
    assert engine.total_duration_ms == 5000
    assert not engine.crossfade_pending


def test_engine_seek_reset_cancels_pending_crossfade(engine: ContinuousAudioEngine) -> None:
    _start_track(engine, "a.flac", 4000)
    engine.arm_crossfade(1000, "b.flac")
    engine.reset_buffer_for_seek(500)
    assert not engine.crossfade_pending
