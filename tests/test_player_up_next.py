"""Tests pour l'affichage progressif du titre suivant ('À suivre') dans PlayerView."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication

from amso.core.database import TrackRecord
from amso.services.player_service import PlayerService, RepeatMode
from amso.ui.views.player_view import UP_NEXT_THRESHOLD_MS, PlayerView


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def tracks() -> list[TrackRecord]:
    return [
        TrackRecord(
            source_ref="D:/Music/t1.mp3",
            source_path="D:/Music/t1.mp3",
            title="Track One",
            artist="Artist A",
            duration_seconds=180.0,
        ),
        TrackRecord(
            source_ref="D:/Music/t2.flac",
            source_path="D:/Music/t2.flac",
            title="Track Two",
            artist="Artist B",
            duration_seconds=200.0,
        ),
        TrackRecord(
            source_ref="D:/Music/t3.ogg",
            source_path="D:/Music/t3.ogg",
            title="Track Three",
            artist="Artist C",
            duration_seconds=150.0,
        ),
    ]


@pytest.fixture
def player(qapp: QApplication, tracks: list[TrackRecord]) -> PlayerService:
    svc = PlayerService()
    svc._playlist = list(tracks)
    svc._current_index = 0
    svc._repeat_mode = RepeatMode.OFF
    svc._shuffle = False
    return svc


def test_next_track_normal_and_end_of_queue(player: PlayerService, tracks: list[TrackRecord]) -> None:
    assert player.next_track == tracks[1]

    player._current_index = 2
    assert player.next_track is None

    player._repeat_mode = RepeatMode.ALL
    assert player.next_track == tracks[0]


def test_next_track_repeat_one_returns_current(player: PlayerService, tracks: list[TrackRecord]) -> None:
    player._repeat_mode = RepeatMode.ONE
    assert player.next_track == tracks[0]


def test_next_track_shuffle_uses_shuffled_order(player: PlayerService, tracks: list[TrackRecord]) -> None:
    player._shuffle = True
    player._playlist = [tracks[0], tracks[2], tracks[1]]
    player._current_index = 0
    assert player.next_track == tracks[2]


def test_player_view_up_next_appears_near_end_and_hides_at_start(
    qapp: QApplication, player: PlayerService, tracks: list[TrackRecord]
) -> None:
    view = PlayerView(player)
    view.update_track_info(tracks[0])

    assert view._up_next_visible is False
    assert "Track Two" in view.up_next_bar.text()
    assert "⏭" in view.up_next_bar.text()

    # Avant le seuil des 15 dernières secondes -> reste masqué
    view.update_position(100_000, 180_000, 100_000 / 180_000)
    assert view._up_next_visible is False

    # Dans les 15 dernières secondes -> s'affiche
    near_end_ms = 180_000 - UP_NEXT_THRESHOLD_MS + 1000
    view.update_position(near_end_ms, 180_000, near_end_ms / 180_000)
    assert view._up_next_visible is True

    # Changement de piste -> se masque à nouveau
    player._current_index = 1
    view.update_track_info(tracks[1])
    assert view._up_next_visible is False
    assert "Track Three" in view.up_next_bar.text()


def test_player_view_up_next_repeat_one_shows_loop_icon(
    qapp: QApplication, player: PlayerService, tracks: list[TrackRecord]
) -> None:
    view = PlayerView(player)
    player._repeat_mode = RepeatMode.ONE
    view._on_queue_or_mode_changed()

    assert "🔂" in view.up_next_bar.text()
    assert "Track One" in view.up_next_bar.text()


def test_player_view_up_next_hidden_at_end_without_repeat(
    qapp: QApplication, player: PlayerService, tracks: list[TrackRecord]
) -> None:
    view = PlayerView(player)
    player._current_index = 2
    player._repeat_mode = RepeatMode.OFF
    view.update_track_info(tracks[2])

    assert view.up_next_bar.text() == ""
    view.update_position(145_000, 150_000, 145_000 / 150_000)
    assert view._up_next_visible is False


def test_player_view_up_next_hover_btn_next_and_click(
    qapp: QApplication, player: PlayerService, tracks: list[TrackRecord]
) -> None:
    view = PlayerView(player)
    view.update_track_info(tracks[0])

    view.eventFilter(view.btn_next, QEvent(QEvent.Type.Enter))
    assert view._up_next_visible is True

    view.eventFilter(view.btn_next, QEvent(QEvent.Type.Leave))
    assert view._up_next_visible is False

    with patch.object(player, "next") as mock_next:
        view.up_next_bar.click()
        mock_next.assert_called_once()
