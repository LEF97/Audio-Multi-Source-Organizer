"""Tests de la prise en charge des feuilles CUE : analyse, indexation, pistes virtuelles et lecture par portions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from PySide6.QtWidgets import QApplication

from amso.core.config import get_config_manager
from amso.core.cue_parser import cue_time_to_ms, parse_cue_content, resolve_cue_audio_file
from amso.core.database import DatabaseManager, SourceType, TrackRecord
from amso.core.playlist_parser import parse_playlist_file
from amso.core.scanner import LocalScanner
from amso.services.player_cue import start_track_decode, stream_key
from amso.services.player_service import PlayerService

CUE_TEXT = """REM GENRE "Rock"
PERFORMER "Mike Oldfield"
TITLE "Amarok"
FILE "album.mp3" WAVE
  TRACK 01 AUDIO
    TITLE "Intro"
    PERFORMER "Mike Oldfield"
    INDEX 01 00:00:00
  TRACK 02 AUDIO
    TITLE "Suite"
    INDEX 00 02:30:00
    INDEX 01 02:32:00
  TRACK 03 DATA
    INDEX 01 05:00:00
  TRACK 04 AUDIO
    TITLE "Finale"
    INDEX 01 05:46:38
"""


def test_cue_time_to_ms_uses_75_frames_per_second() -> None:
    assert cue_time_to_ms(0, 0, 0) == 0
    assert cue_time_to_ms(2, 32, 0) == 152_000
    assert cue_time_to_ms(0, 1, 75) == 2_000
    assert cue_time_to_ms(0, 0, 38) == 507


def test_parse_cue_content_builds_virtual_tracks(tmp_path: Path) -> None:
    (tmp_path / "album.mp3").write_text("x")
    entries = parse_cue_content(CUE_TEXT, tmp_path)
    assert [e.title for e in entries] == ["Intro", "Suite", "Finale"]  # la piste DATA est ignorée
    assert [e.position for e in entries] == [1, 2, 3]
    assert [(e.start_ms, e.end_ms) for e in entries] == [(0, 152_000), (152_000, 346_507), (346_507, None)]
    assert entries[0].duration_seconds == 152.0
    assert entries[2].duration_seconds is None  # dernière piste : jusqu'à la fin du fichier
    assert entries[1].artist == "Mike Oldfield"  # artiste de la feuille en repli
    assert all(e.resolved_path.endswith("album.mp3") and not e.is_missing for e in entries)


def test_parse_cue_content_multiple_files_restart_at_zero(tmp_path: Path) -> None:
    (tmp_path / "a.flac").write_text("x")
    (tmp_path / "b.flac").write_text("x")
    text = (
        'FILE "a.flac" WAVE\n TRACK 01 AUDIO\n  TITLE "A1"\n  INDEX 01 00:00:00\n'
        ' TRACK 02 AUDIO\n  TITLE "A2"\n  INDEX 01 03:00:00\n'
        'FILE "b.flac" WAVE\n TRACK 03 AUDIO\n  TITLE "B1"\n  INDEX 01 00:00:00\n'
    )
    entries = parse_cue_content(text, tmp_path)
    assert [(e.title, e.start_ms, e.end_ms) for e in entries] == [
        ("A1", 0, 180_000),
        ("A2", 180_000, None),  # fin du fichier a.flac : la piste suivante est dans un autre fichier
        ("B1", 0, None),
    ]
    assert entries[0].resolved_path.endswith("a.flac") and entries[2].resolved_path.endswith("b.flac")


def test_resolve_cue_audio_file_falls_back_when_file_line_points_to_the_cue(tmp_path: Path) -> None:
    (tmp_path / "01 - Amarok.mp3").write_text("x")
    (tmp_path / "01 - Amarok.cue").write_text("x")
    path, missing = resolve_cue_audio_file("01 - Amarok.cue", tmp_path)
    assert path.endswith("01 - Amarok.mp3") and not missing
    # FILE absent et plusieurs fichiers audio : introuvable
    (tmp_path / "other.mp3").write_text("x")
    _path, missing = resolve_cue_audio_file("inconnu.wav", tmp_path)
    assert missing


def test_cue_is_indexed_as_playlist_with_virtual_tracks(tmp_path: Path) -> None:
    music = tmp_path / "Music" / "Album"
    music.mkdir(parents=True)
    (music / "album.mp3").write_text("fake audio")
    (music / "album.cue").write_text(CUE_TEXT, encoding="utf-8")

    db = DatabaseManager(str(tmp_path / "cue.db"))
    src = db.add_source(SourceType.LOCAL, "Musique", str(tmp_path / "Music"))
    summary, _ = LocalScanner(db=db).scan_inventory(source=src)
    assert summary.total_found == 1  # seul le fichier audio est une piste de la bibliothèque

    playlists = db.get_playlists(source_id=src.id)
    assert len(playlists) == 1 and playlists[0].format == "cue" and playlists[0].track_count == 3

    # Durée du fichier entier : sert à borner la dernière piste
    with db.get_connection() as conn:
        conn.execute("UPDATE tracks SET duration_seconds = 600.0;")
    tracks = db.get_playlist_tracks(playlists[0].id or 0)
    assert [t.title for t in tracks] == ["Intro", "Suite", "Finale"]
    assert [t.cue_start_ms for t in tracks] == [0, 152_000, 346_507]
    assert [t.cue_end_ms for t in tracks] == [152_000, 346_507, 600_000]
    assert [round(t.duration_seconds or 0, 1) for t in tracks] == [152.0, 194.5, 253.5]
    assert all(t.is_cue_segment and t.file_name == "album.mp3" for t in tracks)
    assert [t.track_number for t in tracks] == [1, 2, 3]


def test_cue_reindexed_when_file_changes_and_playlist_table_migrates(tmp_path: Path) -> None:
    music = tmp_path / "Music"
    music.mkdir()
    (music / "album.mp3").write_text("fake")
    cue = music / "album.cue"
    cue.write_text(CUE_TEXT, encoding="utf-8")
    db = DatabaseManager(str(tmp_path / "cue2.db"))
    src = db.add_source(SourceType.LOCAL, "Musique", str(music))
    scanner = LocalScanner(db=db)
    scanner.scan_inventory(source=src)
    cue.write_text(CUE_TEXT.replace("Suite", "Suite modifiée") + "\n", encoding="utf-8")
    scanner.scan_inventory(source=src)
    pl = db.get_playlists(source_id=src.id)[0]
    assert [t.title for t in db.get_playlist_tracks(pl.id or 0)][1] == "Suite modifiée"
    with db.get_connection() as conn:
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(playlist_entries);").fetchall()}
    assert {"start_ms", "end_ms"} <= cols


def test_parse_playlist_file_dispatches_cue_with_cp1252_encoding(tmp_path: Path) -> None:
    (tmp_path / "a.mp3").write_text("x")
    cue = tmp_path / "a.cue"
    cue.write_bytes('FILE "a.mp3" MP3\n TRACK 01 AUDIO\n  TITLE "Été"\n  INDEX 01 00:00:00\n'.encode("cp1252"))
    entries = parse_playlist_file(cue)
    assert [e.title for e in entries] == ["Été"]


class _FakeDecoder:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def start_decode(self, file_path: str, **kwargs: Any) -> None:
        self.calls.append((file_path, kwargs))


def test_start_track_decode_applies_cue_offsets_only_to_cue_tracks() -> None:
    plain = TrackRecord(source_ref="/m/a.mp3", source_path="/m/a.mp3", duration_seconds=200.0)
    segment = TrackRecord(
        source_ref="/m/a.mp3",
        source_path="/m/a.mp3",
        duration_seconds=194.0,
        cue_start_ms=152_000,
        cue_end_ms=346_000,
    )
    dec = _FakeDecoder()
    start_track_decode(dec, plain, 5_000)  # type: ignore[arg-type]
    start_track_decode(dec, segment, 5_000)  # type: ignore[arg-type]
    assert dec.calls[0] == ("/m/a.mp3", {"start_offset_ms": 5_000, "duration_ms": 200_000})
    assert dec.calls[1] == (
        "/m/a.mp3",
        {"start_offset_ms": 157_000, "duration_ms": 194_000, "stop_offset_ms": 346_000, "key": stream_key(segment)},
    )


def test_stream_key_distinguishes_segments_of_the_same_file() -> None:
    def seg(start: int) -> TrackRecord:
        return TrackRecord(source_ref="/m/a.mp3", source_path="/m/a.mp3", cue_start_ms=start, cue_end_ms=start + 10)

    plain = TrackRecord(source_ref="/m/a.mp3", source_path="/m/a.mp3")
    assert stream_key(plain) == "/m/a.mp3"
    assert len({stream_key(seg(0)), stream_key(seg(10)), stream_key(plain)}) == 3


def test_track_record_cue_fields_survive_dict_roundtrip() -> None:
    track = TrackRecord(source_ref="/m/a.mp3", source_path="/m/a.mp3", cue_start_ms=1000, cue_end_ms=2000)
    clone = TrackRecord.from_dict(track.to_dict())
    assert clone.cue_start_ms == 1000 and clone.cue_end_ms == 2000 and clone.is_cue_segment


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_cue_track_is_refused_by_the_vlc_direct_engine(
    qapp: QApplication, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Le moteur vlc_direct (figé) ne lit pas les portions : message explicite au lieu de lire le fichier entier."""
    monkeypatch.setattr(PlayerService, "is_vlc_available", property(lambda self: True))
    get_config_manager().set_audio_engine("vlc_direct")
    audio = tmp_path / "a.mp3"
    audio.write_text("x")
    track = TrackRecord(
        source_ref=audio.as_posix(), source_path=str(audio), duration_seconds=1.0, cue_start_ms=0, cue_end_ms=1000
    )
    player = PlayerService()
    errors: list[str] = []
    player.error_occurred.connect(errors.append)
    player.load_playlist([track])
    player.play_index(0)
    assert errors and "CUE" in errors[0]
