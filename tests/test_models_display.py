"""Affichage des cellules de BaseTrackTableModel : dispatch par champ et cache des libellés traduits."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from PySide6.QtCore import QModelIndex, QObject, QPersistentModelIndex, Qt, Signal
from PySide6.QtWidgets import QApplication

from amso.core.database import TrackRecord
from amso.core.i18n import get_i18n
from amso.ui.models_base import UNIFIED_TRACK_COLUMNS, BaseTrackTableModel, format_quality

DISPLAY = Qt.ItemDataRole.DisplayRole


class _ListModel(BaseTrackTableModel):
    def __init__(self, tracks: list[TrackRecord]) -> None:
        super().__init__(db=None)
        self._tracks = tracks

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._tracks)

    def _get_track_at_index(self, row: int) -> TrackRecord | None:
        return self._tracks[row] if 0 <= row < len(self._tracks) else None


class _FakePlayer(QObject):
    track_changed = Signal(object)
    state_changed = Signal(object)

    def __init__(self, track: TrackRecord | None) -> None:
        super().__init__()
        self.current_track = track
        self.is_playing = False
        self.is_stopped = False


def _col(field: str) -> int:
    return next(i for i, c in enumerate(UNIFIED_TRACK_COLUMNS) if c[1] == field)


def _cell(model: BaseTrackTableModel, row: int, field: str, role: int = DISPLAY) -> Any:
    return model.data(model.index(row, _col(field)), role)


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    return app if isinstance(app, QApplication) else QApplication([])


@pytest.fixture
def french() -> Iterator[None]:
    i18n = get_i18n()
    previous = i18n.current_language
    i18n.set_language("fr", save_to_config=False)
    yield
    i18n.set_language(previous, save_to_config=False)


def _track(**kwargs: Any) -> TrackRecord:
    base: dict[str, Any] = {"source_ref": "D:/Music/a.flac", "id": 1, "source_path": "D:/Music/a.flac"}
    base.update(kwargs)
    return TrackRecord(**base)


def test_display_unknown_artist_language_changed_label_refreshed(qapp: QApplication, french: None) -> None:
    model = _ListModel([_track(artist=None, channels=2)])
    assert _cell(model, 0, "artist") == "Artiste inconnu"
    assert _cell(model, 0, "channels") == "Stéréo"

    get_i18n().set_language("en", save_to_config=False)
    # Sans notification, le libellé mémorisé est conservé (pas de tr() par cellule).
    assert _cell(model, 0, "artist") == "Artiste inconnu"

    model.notify_language_changed()
    assert _cell(model, 0, "artist") == "Unknown Artist"
    assert _cell(model, 0, "channels") == "Stereo"


def test_display_fields_dispatch_matches_expected_formatting(qapp: QApplication, french: None) -> None:
    track = _track(
        title="Song",
        year=1975,
        track_number=None,
        bitrate=320,
        sample_rate=44100,
        format="mp3",
        file_hash="0123456789abcdef",
        file_mtime=None,
        created_at="2026-11-18 12:34:56",
        duplicate_cluster_id=7,
    )
    model = _ListModel([track])
    assert _cell(model, 0, "title") == "Song"
    assert _cell(model, 0, "year") == "1975"
    assert _cell(model, 0, "track_number") == ""
    assert _cell(model, 0, "bitrate") == "320 kbps"
    assert _cell(model, 0, "sample_rate") == "44.1 kHz"
    assert _cell(model, 0, "format") == "MP3"
    assert _cell(model, 0, "file_hash") == "0123456789..."
    assert _cell(model, 0, "file_mtime") == "--"
    assert _cell(model, 0, "created_at") == "2026-11-18 12:34"
    assert _cell(model, 0, "duplicate_cluster_id") == "#7"
    assert _cell(model, 0, "album") == "--"
    assert _cell(model, 0, "id") == "1"
    assert _cell(model, 0, "source_id") == "--"
    assert _cell(model, 0, "quality_score") == format_quality(track.quality_score, track.format, track.bitrate)
    assert _cell(model, 0, "year", Qt.ItemDataRole.TextAlignmentRole) == int(
        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
    )


def test_display_playing_column_player_state_icon_follows(qapp: QApplication, french: None) -> None:
    current = _track()
    other = _track(id=2, source_ref="D:/Music/b.flac", source_path="D:/Music/b.flac")
    model = _ListModel([current, other])
    player = _FakePlayer(current)
    model.set_player_service(player)

    player.is_playing = True
    assert _cell(model, 0, "is_playing") == "▶"
    assert _cell(model, 1, "is_playing") == ""
    player.is_playing = False
    assert _cell(model, 0, "is_playing") == "⏸"
    player.is_stopped = True
    assert _cell(model, 0, "is_playing") == "⏹"
    assert _cell(model, 0, "title", Qt.ItemDataRole.FontRole).bold()
    assert _cell(model, 1, "title", Qt.ItemDataRole.FontRole) is None
