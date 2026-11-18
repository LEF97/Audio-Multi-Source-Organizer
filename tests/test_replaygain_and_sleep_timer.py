"""Tests unitaires pour ReplayGain (PCM) et SleepTimerController."""

from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from amso.core.replaygain import apply_gain_pcm, parse_replaygain_db, replaygain_db_to_linear
from amso.services.sleep_timer import SleepTimerController


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    assert isinstance(app, QApplication)
    return app


def test_parse_replaygain_db_handles_formats_and_clamping() -> None:
    assert parse_replaygain_db("-6.50 dB") == -6.5
    assert parse_replaygain_db("+3,25 dB") == 3.25
    assert parse_replaygain_db("-30 dB") == -18.0
    assert parse_replaygain_db("+25 dB") == 12.0
    assert parse_replaygain_db("invalid") is None
    assert parse_replaygain_db(None) is None


def test_apply_gain_pcm_scales_and_clamps_without_overflow() -> None:
    samples = np.array([1000, -1000, 20000, -20000], dtype="<i2")
    pcm = samples.tobytes()

    assert apply_gain_pcm(pcm, 1.0) == pcm

    halved = np.frombuffer(apply_gain_pcm(pcm, replaygain_db_to_linear(-6.0206)), dtype="<i2")
    assert 490 <= int(halved[0]) <= 510
    assert -510 <= int(halved[1]) <= -490

    boosted = np.frombuffer(apply_gain_pcm(pcm, 4.0), dtype="<i2")
    assert int(boosted[2]) == 32767
    assert int(boosted[3]) == -32768


def test_sleep_timer_end_of_track_and_end_of_queue(qapp: QApplication) -> None:
    timer = SleepTimerController()
    triggered: list[bool] = []
    timer.triggered.connect(lambda: triggered.append(True))

    timer.set_mode("end_of_track")
    assert timer.mode == "end_of_track"
    assert timer.on_track_finished(queue_ended=False) is True
    assert len(triggered) == 1
    assert timer.mode == "off"

    timer.set_mode("end_of_queue")
    assert timer.on_track_finished(queue_ended=False) is False
    assert len(triggered) == 1
    assert timer.on_track_finished(queue_ended=True) is True
    assert len(triggered) == 2
    assert timer.mode == "off"


def test_sleep_timer_timed_mode_and_tick(qapp: QApplication) -> None:
    timer = SleepTimerController()
    triggered: list[bool] = []
    timer.triggered.connect(lambda: triggered.append(True))

    timer.set_mode("15m")
    assert timer.mode == "15m"
    assert timer.remaining_seconds == 900

    timer._remaining_s = 2
    timer._on_tick()
    assert timer.remaining_seconds == 1
    assert len(triggered) == 0

    timer._on_tick()
    assert timer.mode == "off"
    assert timer.remaining_seconds == 0
    assert len(triggered) == 1
