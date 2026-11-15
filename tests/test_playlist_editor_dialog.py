"""Tests pour le dialogue de gestion/réparation de playlist et la relocalisation CUE."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from amso.core.database import DatabaseManager, PlaylistSummaryRecord, SourceType
from amso.core.playlist_exporter import replace_cue_file_target
from amso.core.playlist_parser import ParsedPlaylistEntry
from amso.ui.dialogs.playlist_editor_dialog import PlaylistEditorDialog


def _ensure_qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    assert isinstance(app, QApplication)
    return app


def test_replace_cue_file_target_updates_file_directive_and_keeps_tracks(tmp_path: Path) -> None:
    """Vérifie que replace_cue_file_target met à jour FILE sans altérer les TRACK/INDEX."""
    cue_path = tmp_path / "album.cue"
    cue_path.write_text(
        'PERFORMER "Artist"\n'
        'TITLE "Album"\n'
        'FILE "album.wav" WAVE\n'
        "  TRACK 01 AUDIO\n"
        '    TITLE "Intro"\n'
        "    INDEX 01 00:00:00\n",
        encoding="utf-8",
    )
    new_audio = tmp_path / "album.flac"
    new_audio.write_bytes(b"fake-flac")

    ok = replace_cue_file_target(cue_path, "album.wav", new_audio)
    assert ok is True
    updated = cue_path.read_text(encoding="utf-8")
    assert 'FILE "album.flac" WAVE' in updated
    assert "INDEX 01 00:00:00" in updated


def test_playlist_editor_dialog_filter_move_clean_and_save(tmp_path: Path) -> None:
    """Vérifie le filtrage des anomalies, le déplacement, le nettoyage et la sauvegarde."""
    _ensure_qapp()

    audio1 = tmp_path / "01.mp3"
    audio2 = tmp_path / "02.mp3"
    audio1.write_bytes(b"a")
    audio2.write_bytes(b"b")

    pl_path = tmp_path / "mix.m3u8"
    pl_path.write_text("#EXTM3U\n01.mp3\nmissing.mp3\n02.mp3\n", encoding="utf-8")

    db = DatabaseManager(db_path=tmp_path / "pl_editor.db")
    src = db.add_source(SourceType.LOCAL, "Music", str(tmp_path))
    assert src.id is not None

    pl_id = db.upsert_playlist(
        source_id=src.id,
        file_path=str(pl_path),
        file_name="mix.m3u8",
        folder_path=str(tmp_path),
        format_str="m3u8",
        file_mtime=100.0,
        file_size=50,
        entries=[
            ParsedPlaylistEntry(
                position=1,
                raw_path="01.mp3",
                resolved_path=str(audio1),
                title="Track 1",
                duration_seconds=100.0,
                is_missing=False,
            ),
            ParsedPlaylistEntry(
                position=2,
                raw_path="missing.mp3",
                resolved_path=str(tmp_path / "missing.mp3"),
                title="Missing",
                duration_seconds=50.0,
                is_missing=True,
            ),
            ParsedPlaylistEntry(
                position=3,
                raw_path="02.mp3",
                resolved_path=str(audio2),
                title="Track 2",
                duration_seconds=200.0,
                is_missing=False,
            ),
        ],
    )

    summary = PlaylistSummaryRecord(
        id=pl_id,
        source_id=src.id,
        name="mix.m3u8",
        file_path=str(pl_path),
        format="m3u8",
        track_count=3,
        total_duration_seconds=350.0,
        missing_count=1,
        updated_at=None,
    )

    dlg = PlaylistEditorDialog(db=db, playlist=summary)
    try:
        assert dlg.table.rowCount() == 3

        # Filtre anomalies uniquement
        dlg._set_filter(True)
        assert dlg.table.rowCount() == 1

        # Retour à tout afficher puis nettoyage des introuvables
        dlg._set_filter(False)
        assert dlg.table.rowCount() == 3
        dlg._on_clean_missing()
        assert dlg.table.rowCount() == 2

        # Déplacement : monter la 2e piste en 1re position
        dlg.table.selectRow(1)
        dlg._move_selected(-1)
        assert dlg.table.item(0, 2).text() == "Track 2"

        # Sauvegarde sur disque et réindexation DB
        dlg._on_save()
        assert dlg.was_modified is True

        entries_after = db.get_playlist_entries(pl_id)
        assert len(entries_after) == 2
        assert all(not e.is_missing for e in entries_after)
        assert Path(entries_after[0].resolved_path).name == "02.mp3"
    finally:
        dlg.close()
        dlg.deleteLater()


def test_playlist_editor_dialog_cue_locks_reorder_and_delete(tmp_path: Path) -> None:
    """Vérifie qu'une feuille CUE verrouille le déplacement et la suppression."""
    _ensure_qapp()
    cue_path = tmp_path / "set.cue"
    cue_path.write_text('FILE "set.wav" WAVE\n  TRACK 01 AUDIO\n    INDEX 01 00:00:00\n', encoding="utf-8")

    db = DatabaseManager(db_path=tmp_path / "cue_editor.db")
    src = db.add_source(SourceType.LOCAL, "Music", str(tmp_path))
    assert src.id is not None

    pl_id = db.upsert_playlist(
        source_id=src.id,
        file_path=str(cue_path),
        file_name="set.cue",
        folder_path=str(tmp_path),
        format_str="cue",
        file_mtime=100.0,
        file_size=50,
        entries=[
            ParsedPlaylistEntry(
                position=1,
                raw_path="set.wav",
                resolved_path=str(tmp_path / "set.wav"),
                title="Track 1",
                duration_seconds=120.0,
                is_missing=True,
                start_ms=0,
                end_ms=120000,
            )
        ],
    )
    summary = PlaylistSummaryRecord(
        id=pl_id,
        source_id=src.id,
        name="set.cue",
        file_path=str(cue_path),
        format="cue",
        track_count=1,
        total_duration_seconds=120.0,
        missing_count=1,
        updated_at=None,
    )

    dlg = PlaylistEditorDialog(db=db, playlist=summary)
    try:
        assert dlg._is_cue is True
        assert not hasattr(dlg, "btn_move_up")
        assert not hasattr(dlg, "btn_clean_missing")
        assert dlg.table.rowCount() == 1
    finally:
        dlg.close()
        dlg.deleteLater()


def test_playlist_editor_reload_from_disk_updates_entries(tmp_path: Path) -> None:
    """Le bouton Relire depuis le disque réanalyse le fichier et rafraîchit la table et la base."""
    _ensure_qapp()
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    audio1 = src_dir / "01.mp3"
    audio2 = src_dir / "02.mp3"
    audio1.write_bytes(b"ID3")
    audio2.write_bytes(b"ID3")
    m3u_path = src_dir / "mix.m3u"
    m3u_path.write_text("01.mp3\n", encoding="utf-8")

    db = DatabaseManager(db_path=tmp_path / "reload_editor.db")
    src = db.add_source(SourceType.LOCAL, "Src", str(src_dir))
    assert src.id is not None
    pl_id = db.upsert_playlist(
        source_id=src.id,
        file_path=str(m3u_path),
        file_name="mix.m3u",
        folder_path=str(src_dir),
        format_str="m3u",
        file_mtime=10.0,
        file_size=7,
        entries=[
            ParsedPlaylistEntry(
                position=1,
                raw_path="01.mp3",
                resolved_path=str(audio1),
                title="01",
                is_missing=False,
            )
        ],
    )
    summary = PlaylistSummaryRecord(
        id=pl_id,
        source_id=src.id,
        name="mix.m3u",
        file_path=str(m3u_path),
        format="m3u",
        track_count=1,
        total_duration_seconds=None,
        missing_count=0,
        updated_at=None,
    )

    dlg = PlaylistEditorDialog(db=db, playlist=summary)
    try:
        assert dlg.table.rowCount() == 1
        assert dlg.btn_reload_disk.isEnabled()

        m3u_path.write_text("01.mp3\n02.mp3\n", encoding="utf-8")
        dlg._on_reload_from_disk()

        assert dlg.table.rowCount() == 2
        assert dlg.was_modified is True
        assert len(db.get_playlist_entries(pl_id)) == 2
    finally:
        dlg.close()
        dlg.deleteLater()


def test_playlist_editor_remove_missing_from_library(tmp_path: Path, monkeypatch) -> None:
    """Le bouton Retirer de la bibliothèque supprime la playlist absente du disque."""
    from PySide6.QtWidgets import QMessageBox

    _ensure_qapp()
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    missing_cue = src_dir / "deleted.cue"

    db = DatabaseManager(db_path=tmp_path / "remove_editor.db")
    src = db.add_source(SourceType.LOCAL, "Src", str(src_dir))
    assert src.id is not None
    pl_id = db.upsert_playlist(
        source_id=src.id,
        file_path=str(missing_cue),
        file_name="deleted.cue",
        folder_path=str(src_dir),
        format_str="cue",
        file_mtime=10.0,
        file_size=7,
        entries=[],
    )
    summary = PlaylistSummaryRecord(
        id=pl_id,
        source_id=src.id,
        name="deleted.cue",
        file_path=str(missing_cue),
        format="cue",
        track_count=0,
        total_duration_seconds=None,
        missing_count=0,
        updated_at=None,
    )

    monkeypatch.setattr(QMessageBox, "question", lambda *a, **kw: QMessageBox.StandardButton.Yes)

    dlg = PlaylistEditorDialog(db=db, playlist=summary)
    try:
        assert hasattr(dlg, "btn_remove_from_library")
        dlg._on_remove_from_library()
        assert dlg.was_modified is True
        assert db.get_playlist_by_path(str(missing_cue)) is None
    finally:
        dlg.close()
        dlg.deleteLater()
