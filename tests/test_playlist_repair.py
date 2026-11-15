"""Tests pour la recherche automatique et la validation de réparation de playlists."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from amso.core.database import (
    DatabaseManager,
    PlaylistEntryRecord,
    PlaylistSummaryRecord,
    SourceType,
    TrackRecord,
)
from amso.core.playlist_parser import ParsedPlaylistEntry
from amso.core.playlist_repair import (
    AUTO_CHECK_SCORE,
    EntryRepairProposal,
    RepairCandidate,
    find_most_effective_folder,
    find_playlist_repair_proposals,
    normalize_match_text,
)
from amso.ui.dialogs.playlist_editor_dialog import PlaylistEditorDialog


def _get_qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    assert isinstance(app, QApplication)
    return app


def test_normalize_match_text_strips_accents_and_track_prefix() -> None:
    assert normalize_match_text("01. Café_Crème - Ft. Artist", strip_track_prefix=True) == "cafe creme artist"
    assert normalize_match_text("02 - Wait Your Turn", strip_track_prefix=True) == "wait your turn"


def test_find_proposals_matches_renamed_file_in_playlist_dir(tmp_path: Path) -> None:
    db = DatabaseManager(":memory:")
    pl_dir = tmp_path / "Rihanna" / "2009 - Rated R"
    pl_dir.mkdir(parents=True)
    pl_file = pl_dir / "Rihanna - Rated R.m3u"
    pl_file.write_text("#EXTM3U\n", encoding="utf-8")

    renamed = pl_dir / "01 - Mad House.mp3"
    renamed.write_bytes(b"")
    other = pl_dir / "02 - Wait Your Turn.mp3"
    other.write_bytes(b"")

    entries = [
        PlaylistEntryRecord(
            position=1,
            raw_path="01. Mad House - Rihanna -.mp3",
            resolved_path=str(pl_dir / "01. Mad House - Rihanna -.mp3"),
            title="Mad House",
            artist="Rihanna",
            is_missing=True,
        )
    ]

    proposals = find_playlist_repair_proposals(db, str(pl_file), entries)
    assert len(proposals) == 1
    best = proposals[0].best
    assert best is not None
    assert Path(best.path) == renamed
    assert best.source_kind == "local_dir"
    assert best.score >= AUTO_CHECK_SCORE


def test_find_proposals_matches_moved_track_in_library_db(tmp_path: Path) -> None:
    db = DatabaseManager(":memory:")
    src = db.add_source(SourceType.LOCAL, "NAS", str(tmp_path))
    assert src.id is not None
    src_id = src.id

    moved_file = tmp_path / "Archive" / "Rihanna - Rude Boy.flac"
    moved_file.parent.mkdir(parents=True)
    moved_file.write_bytes(b"")

    db.upsert_track(
        TrackRecord(
            source_id=src_id,
            source_type=SourceType.LOCAL,
            source_ref=str(moved_file),
            title="Rude Boy",
            artist="Rihanna",
            duration_seconds=223.0,
        )
    )

    pl_file = tmp_path / "Playlists" / "Mix.m3u"
    pl_file.parent.mkdir(parents=True)
    pl_file.write_text("#EXTM3U\n", encoding="utf-8")

    entries = [
        PlaylistEntryRecord(
            position=1,
            raw_path="08. Rude Boy - Rihanna -.mp3",
            resolved_path=str(pl_file.parent / "08. Rude Boy - Rihanna -.mp3"),
            title="Rude Boy",
            artist="Rihanna",
            duration_seconds=223.0,
            is_missing=True,
        )
    ]

    proposals = find_playlist_repair_proposals(db, str(pl_file), entries)
    assert len(proposals) == 1
    best = proposals[0].best
    assert best is not None
    assert Path(best.path) == moved_file
    assert best.source_kind == "library_db"
    assert best.score >= AUTO_CHECK_SCORE


def test_find_proposals_skips_nonexistent_db_tracks(tmp_path: Path) -> None:
    db = DatabaseManager(":memory:")
    src = db.add_source(SourceType.LOCAL, "NAS", str(tmp_path))
    assert src.id is not None
    src_id = src.id
    ghost_file = tmp_path / "Ghost - Track.mp3"

    db.upsert_track(
        TrackRecord(
            source_id=src_id,
            source_type=SourceType.LOCAL,
            source_ref=str(ghost_file),
            title="Ghost Track",
            artist="Ghost",
            duration_seconds=180.0,
        )
    )

    pl_file = tmp_path / "Mix.m3u"
    pl_file.write_text("#EXTM3U\n", encoding="utf-8")
    entries = [
        PlaylistEntryRecord(
            position=1,
            raw_path="Ghost Track.mp3",
            resolved_path=str(tmp_path / "Ghost Track.mp3"),
            title="Ghost Track",
            artist="Ghost",
            duration_seconds=180.0,
            is_missing=True,
        )
    ]

    proposals = find_playlist_repair_proposals(db, str(pl_file), entries)
    assert len(proposals) == 1
    assert proposals[0].best is None


def test_repair_panel_prechecks_without_collision_and_applies_to_dialog(tmp_path: Path) -> None:
    _get_qapp()
    db = DatabaseManager(":memory:")
    pl_dir = tmp_path / "Album"
    pl_dir.mkdir()
    pl_file = pl_dir / "Album.m3u"
    pl_file.write_text("01. Missing.mp3\n02. MissingDup.mp3\n", encoding="utf-8")

    found_file = pl_dir / "01 - Found.mp3"
    found_file.write_bytes(b"")

    src = db.add_source(SourceType.LOCAL, "AlbumSrc", str(tmp_path))
    assert src.id is not None
    pl_id = db.upsert_playlist(
        source_id=src.id,
        file_path=str(pl_file),
        file_name="Album.m3u",
        folder_path=str(pl_dir),
        format_str="m3u",
        file_mtime=100.0,
        file_size=50,
        entries=[
            ParsedPlaylistEntry(
                position=1,
                raw_path="01. Missing.mp3",
                resolved_path=str(pl_dir / "01. Missing.mp3"),
                title="Found",
                artist="Artist",
                is_missing=True,
            ),
            ParsedPlaylistEntry(
                position=2,
                raw_path="02. MissingDup.mp3",
                resolved_path=str(pl_dir / "02. MissingDup.mp3"),
                title="Found",
                artist="Artist",
                is_missing=True,
            ),
        ],
    )
    summary = PlaylistSummaryRecord(
        id=pl_id,
        source_id=src.id,
        name="Album.m3u",
        file_path=str(pl_file),
        format="m3u",
        track_count=2,
        missing_count=2,
        total_duration_seconds=0.0,
        updated_at="2026-11-15T09:00:00",
    )

    dialog = PlaylistEditorDialog(db, summary)
    try:
        panel = dialog.repair_panel
        proposals = [
            EntryRepairProposal(
                entry_index=0,
                entry=dialog._entries[0],
                candidates=[RepairCandidate(path=str(found_file), score=92, source_kind="local_dir")],
            ),
            EntryRepairProposal(
                entry_index=1,
                entry=dialog._entries[1],
                candidates=[RepairCandidate(path=str(found_file), score=88, source_kind="local_dir")],
            ),
        ]
        panel._on_worker_finished(proposals)

        # Un seul des deux doublons doit être pré-coché (celui au meilleur score)
        assert panel._row_checkboxes[0] is not None and panel._row_checkboxes[0].isChecked()
        assert panel._row_checkboxes[1] is not None and not panel._row_checkboxes[1].isChecked()

        panel._on_apply_clicked()
        assert not dialog._entries[0].is_missing
        assert dialog._entries[0].raw_path == "01 - Found.mp3"
        assert dialog._entries[1].is_missing
        assert dialog.stacked_views.currentIndex() == 0
    finally:
        dialog.close()


def test_false_positive_different_title_same_artist_and_duration_is_rejected(tmp_path: Path) -> None:
    db = DatabaseManager(":memory:")
    src = db.add_source(SourceType.LOCAL, "NAS", str(tmp_path))
    assert src.id is not None

    pl_dir = tmp_path / "Rihanna" / "2009 - Rated R"
    pl_dir.mkdir(parents=True)
    pl_file = pl_dir / "Rated R.m3u"
    pl_file.write_text("#EXTM3U\n", encoding="utf-8")

    other_song = pl_dir / "06. Rihanna - Russian Roulette.mp3"
    other_song.write_bytes(b"")
    db.upsert_track(
        TrackRecord(
            source_id=src.id,
            source_type=SourceType.LOCAL,
            source_ref=str(other_song),
            title="Russian Roulette",
            artist="Rihanna",
            duration_seconds=228.0,
        )
    )

    entries = [
        PlaylistEntryRecord(
            position=2,
            raw_path="02. Wait Your Turn - Rihanna -.mp3",
            resolved_path=str(pl_dir / "02. Wait Your Turn - Rihanna -.mp3"),
            title="Wait Your Turn",
            artist="Rihanna",
            duration_seconds=227.0,
            is_missing=True,
        )
    ]

    proposals = find_playlist_repair_proposals(db, str(pl_file), entries)
    assert len(proposals) == 1
    assert proposals[0].best is None


def test_find_most_effective_folder_and_radio_strategies(tmp_path: Path) -> None:
    _get_qapp()
    db = DatabaseManager(":memory:")
    pl_dir = tmp_path / "Playlists"
    pl_dir.mkdir()
    alt_dir = tmp_path / "AltAlbum"
    alt_dir.mkdir()
    pl_file = pl_dir / "Mix.m3u"
    pl_file.write_text("01.mp3\n02.mp3\n", encoding="utf-8")

    f1_pl = pl_dir / "Track 1.mp3"
    f1_alt = alt_dir / "Track 1.mp3"
    f2_alt = alt_dir / "Track 2.mp3"
    for f in (f1_pl, f1_alt, f2_alt):
        f.write_bytes(b"")

    src = db.add_source(SourceType.LOCAL, "Src", str(tmp_path))
    assert src.id is not None
    pl_id = db.upsert_playlist(
        source_id=src.id,
        file_path=str(pl_file),
        file_name="Mix.m3u",
        folder_path=str(pl_dir),
        format_str="m3u",
        file_mtime=100.0,
        file_size=50,
        entries=[
            ParsedPlaylistEntry(position=1, raw_path="01.mp3", resolved_path=str(pl_dir / "01.mp3"), is_missing=True),
            ParsedPlaylistEntry(position=2, raw_path="02.mp3", resolved_path=str(pl_dir / "02.mp3"), is_missing=True),
        ],
    )
    summary = PlaylistSummaryRecord(
        id=pl_id,
        source_id=src.id,
        name="Mix.m3u",
        file_path=str(pl_file),
        format="m3u",
        track_count=2,
        missing_count=2,
        total_duration_seconds=0.0,
        updated_at="2026-11-15T09:00:00",
    )

    dialog = PlaylistEditorDialog(db, summary)
    try:
        panel = dialog.repair_panel
        proposals = [
            EntryRepairProposal(
                entry_index=0,
                entry=dialog._entries[0],
                candidates=[
                    RepairCandidate(path=str(f1_alt), score=100, source_kind="library_db"),
                    RepairCandidate(path=str(f1_pl), score=92, source_kind="local_dir"),
                ],
            ),
            EntryRepairProposal(
                entry_index=1,
                entry=dialog._entries[1],
                candidates=[
                    RepairCandidate(path=str(f2_alt), score=90, source_kind="library_db"),
                ],
            ),
        ]
        best_dir, count = find_most_effective_folder(proposals, pl_dir)
        assert Path(best_dir) == alt_dir
        assert count == 2

        panel._on_worker_finished(proposals)
        # AltAlbum couvre 2/2 vs 1/2 pour le dossier playlist -> radio_best_dir sélectionné par défaut
        assert panel.radio_best_dir.isChecked()
        assert panel.radio_playlist_dir.isEnabled()
        assert panel.radio_exact_100.isEnabled()
        assert panel._row_combos[0] is not None and panel._row_combos[0].currentIndex() == 0
        assert panel._row_checkboxes[0] is not None and panel._row_checkboxes[0].isChecked()
        assert panel._row_checkboxes[1] is not None and panel._row_checkboxes[1].isChecked()

        # Mode 0 (dossier de la playlist) : piste 0 sélectionne f1_pl (92 %) et est cochée, piste 1 non cochée
        panel.radio_playlist_dir.setChecked(True)
        panel._on_strategy_changed(0)
        assert panel._row_combos[0].currentIndex() == 1
        assert panel._row_checkboxes[0].isChecked()
        assert not panel._row_checkboxes[1].isChecked()

        # Mode 2 (privilégier les 100 %) : seule la piste 0 (100 %) est cochée
        panel.radio_exact_100.setChecked(True)
        panel._on_strategy_changed(2)
        assert panel._row_checkboxes[0].isChecked()
        assert not panel._row_checkboxes[1].isChecked()

        # Cas _Playlists/ : 0 fichier dans le dossier playlist, 0 match à 100 % -> radios grisés, best_dir par défaut
        centralized_proposals = [
            EntryRepairProposal(
                entry_index=0,
                entry=dialog._entries[0],
                candidates=[RepairCandidate(path=str(f1_alt), score=93, source_kind="library_db")],
            ),
            EntryRepairProposal(
                entry_index=1,
                entry=dialog._entries[1],
                candidates=[RepairCandidate(path=str(f2_alt), score=93, source_kind="library_db")],
            ),
        ]
        panel._on_worker_finished(centralized_proposals)
        assert not panel.radio_playlist_dir.isEnabled()
        assert not panel.radio_exact_100.isEnabled()
        assert panel.radio_best_dir.isEnabled()
        assert panel.radio_best_dir.isChecked()
        assert panel._row_checkboxes[0].isChecked()
        assert panel._row_checkboxes[1].isChecked()
    finally:
        dialog.close()


def test_cue_apply_repair_proposals_updates_file_directives(tmp_path: Path) -> None:
    _get_qapp()
    cue_path = tmp_path / "album.cue"
    cue_path.write_text(
        'PERFORMER "Steven Wilson"\n'
        'TITLE "To The Bone"\n'
        'FILE "B2 - Rufge.flac" WAVE\n'
        "  TRACK 01 AUDIO\n"
        '    TITLE "Refuge"\n'
        "    INDEX 01 00:00:00\n",
        encoding="utf-8",
    )
    fixed_audio = tmp_path / "B2 - Refuge.flac"
    fixed_audio.write_bytes(b"flac")

    db = DatabaseManager(db_path=tmp_path / "cue_repair.db")
    src = db.add_source(SourceType.LOCAL, "Music", str(tmp_path))
    assert src.id is not None

    pl_id = db.upsert_playlist(
        source_id=src.id,
        file_path=str(cue_path),
        file_name="album.cue",
        folder_path=str(tmp_path),
        format_str="cue",
        file_mtime=100.0,
        file_size=50,
        entries=[
            ParsedPlaylistEntry(
                position=1,
                raw_path="B2 - Rufge.flac",
                resolved_path=str(tmp_path / "B2 - Rufge.flac"),
                title="Refuge",
                artist="Steven Wilson",
                is_missing=True,
                start_ms=0,
            )
        ],
    )
    summary = PlaylistSummaryRecord(
        id=pl_id,
        source_id=src.id,
        name="album.cue",
        file_path=str(cue_path),
        format="cue",
        track_count=1,
        missing_count=1,
        total_duration_seconds=0.0,
        updated_at="2026-11-15T09:00:00",
    )

    dialog = PlaylistEditorDialog(db, summary)
    try:
        assert dialog.btn_auto_search.isEnabled()
        assert not dialog.btn_save.isEnabled()
        dialog._on_apply_repair_proposals({0: str(fixed_audio)})
        assert dialog.btn_save.isEnabled()
        # Appliquer ne doit pas écrire sur disque avant Enregistrer
        assert 'FILE "B2 - Rufge.flac" WAVE' in cue_path.read_text(encoding="utf-8")
        assert not dialog._entries[0].is_missing

        dialog._on_save()
        assert dialog.was_modified is True
        assert 'FILE "B2 - Refuge.flac" WAVE' in cue_path.read_text(encoding="utf-8")
    finally:
        dialog.close()


def test_track_number_and_folder_proximity_boost_same_album_track(tmp_path: Path) -> None:
    """Le numéro de piste entier (ex. 001 -> 1) et le dossier de la playlist font passer le bon fichier devant."""
    from amso.core.playlist_repair import _extract_track_number

    assert _extract_track_number("001 - Intro") == 1
    assert _extract_track_number("16 - Religious Experience") == 16
    assert _extract_track_number("[05] Song") == 5
    assert _extract_track_number("No Number") is None

    db = DatabaseManager(":memory:")
    src = db.add_source(SourceType.LOCAL, "NAS", str(tmp_path))
    assert src.id is not None

    pl_dir = tmp_path / "Ayers, Kevin" / "1975 - Odd Ditties"
    other_dir = tmp_path / "Ayers, Kevin" / "1974 - Confessions"
    pl_dir.mkdir(parents=True)
    other_dir.mkdir(parents=True)

    pl_file = pl_dir / "Odd Ditties.cue"
    pl_file.write_text('FILE "16 - Religious Experience.wav" WAVE\n', encoding="utf-8")

    right_file = pl_dir / "16 - Religious Experience.flac"
    wrong_bonus = other_dir / "04 - Religious Experience (Singing A Song In The Morning) [bonus track].flac"
    right_file.write_bytes(b"")
    wrong_bonus.write_bytes(b"")

    db.upsert_track(
        TrackRecord(
            source_id=src.id,
            source_type=SourceType.LOCAL,
            source_ref=str(right_file),
            title="Religious Experience",
            artist="Kevin Ayers",
            track_number=16,
        )
    )
    db.upsert_track(
        TrackRecord(
            source_id=src.id,
            source_type=SourceType.LOCAL,
            source_ref=str(wrong_bonus),
            title="Religious Experience (Singing A Song In The Morning) [bonus track]",
            artist="Kevin Ayers",
            track_number=4,
        )
    )

    entries = [
        PlaylistEntryRecord(
            position=16,
            raw_path="16 - Religious Experience (Singing A Song In The Morning) (bonus track).wav",
            resolved_path=str(pl_dir / "16 - Religious Experience (Singing A Song In The Morning) (bonus track).wav"),
            title="Religious Experience (Singing A Song In The Morning) (bonus track)",
            artist="Kevin Ayers",
            duration_seconds=None,
            is_missing=True,
        )
    ]

    proposals = find_playlist_repair_proposals(db, str(pl_file), entries)
    assert len(proposals) == 1
    best = proposals[0].best
    assert best is not None
    assert Path(best.path) == right_file
    assert best.score >= 85
