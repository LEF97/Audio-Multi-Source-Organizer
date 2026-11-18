"""Non-régression : pas de retour à 00:00 de la barre de lecture lors de la reprise d'une position sauvegardée."""

from __future__ import annotations

import time
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

from amso.core.config import get_config_manager
from amso.core.database import SourceType, TrackRecord
from amso.services import player_transitions
from amso.services.player_service import PlayerService


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        app = QApplication([])
    return app


def _track() -> TrackRecord:
    return TrackRecord(
        source_type=SourceType.LOCAL,
        source_ref="C:/absent/a.flac",
        source_path="C:/absent/a.flac",
        file_name="a.flac",
        title="A",
        artist="B",
        duration_seconds=240.0,
    )


def test_buffer_on_tick_pendant_decodage_initial_ne_remet_pas_position_a_zero(qapp: QApplication) -> None:
    get_config_manager().set_audio_engine("buffer")
    player = PlayerService()
    player.load_playlist([_track()], 0, initial_position_ms=90_000)

    fake_engine = MagicMock()
    fake_engine.is_available = True
    fake_engine.is_playing = False
    fake_engine.cue_continues = False
    fake_engine.current_time_ms = 0
    fake_engine.total_duration_ms = 0
    player._engine = fake_engine
    player._decoder = SimpleNamespace(is_decoding=True, set_throttled=lambda _v: None)

    emitted: list[tuple[int, int, float]] = []
    player.position_changed.connect(lambda cur, tot, ratio: emitted.append((cur, tot, ratio)))

    player._on_tick()

    assert emitted == []
    assert player._current_time_ms == 90_000

    fake_engine.is_playing = True
    fake_engine.current_time_ms = 90_000
    fake_engine.total_duration_ms = 240_000
    player._on_tick()

    assert len(emitted) == 1
    assert emitted[0][0] == 90_000
    assert emitted[0][1] == 240_000


def test_vlc_direct_on_tick_apres_pending_seek_ne_remet_pas_position_a_zero(
    qapp: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    get_config_manager().set_audio_engine("vlc_direct")
    player = PlayerService()
    player.load_playlist([_track()], 0, initial_position_ms=90_000)

    fake_vlc = SimpleNamespace(State=SimpleNamespace(Playing=3, Paused=4, Ended=6))
    monkeypatch.setattr(player_transitions, "vlc", fake_vlc)

    fake_mp = MagicMock()
    fake_mp.get_state.return_value = 3
    fake_mp.get_length.return_value = 240_000
    fake_mp.audio_get_volume.return_value = 80
    # LibVLC renvoie 0 pendant le seek asynchrone, puis la position cible
    fake_mp.get_time.side_effect = [0, 90_000]
    fake_mp.get_position.side_effect = [0.375]
    player._media_player = fake_mp
    player._vlc_instance = object()
    player._pending_seek_ms = 90_000

    emitted: list[tuple[int, int, float]] = []
    player.position_changed.connect(lambda cur, tot, ratio: emitted.append((cur, tot, ratio)))

    player._on_tick()
    fake_mp.set_time.assert_called_once_with(90_000)
    assert emitted == []
    assert player._current_time_ms == 90_000

    player._on_tick()
    assert emitted == [(90_000, 240_000, 0.375)]


def test_vlc_direct_on_tick_expire_hold_si_seek_echoue(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    get_config_manager().set_audio_engine("vlc_direct")
    player = PlayerService()
    player.load_playlist([_track()], 0, initial_position_ms=90_000)

    fake_vlc = SimpleNamespace(State=SimpleNamespace(Playing=3, Paused=4, Ended=6))
    monkeypatch.setattr(player_transitions, "vlc", fake_vlc)

    fake_mp = MagicMock()
    fake_mp.get_state.return_value = 3
    fake_mp.get_length.return_value = 240_000
    fake_mp.audio_get_volume.return_value = 80
    fake_mp.get_time.return_value = 0
    fake_mp.get_position.return_value = 0.0
    player._media_player = fake_mp
    player._vlc_instance = object()
    player._pending_seek_ms = 0
    player._vlc_seek_hold_ms = 90_000
    player._vlc_seek_hold_deadline = time.monotonic() - 0.1

    emitted: list[tuple[int, int, float]] = []
    player.position_changed.connect(lambda cur, tot, ratio: emitted.append((cur, tot, ratio)))

    player._on_tick()
    assert player._vlc_seek_hold_ms == 0
    assert emitted == [(0, 240_000, 0.0)]
