"""Schéma SQLite : base neuve identique à la référence, migration d'une ancienne base, idempotence."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from amso.core.database import DatabaseManager
from amso.core.db.schema import ADDED_COLUMNS

REFERENCE = Path(__file__).parent / "data" / "schema_reference.json"


def _dump_schema(db_path: Path) -> dict[str, object]:
    conn = sqlite3.connect(db_path)
    try:
        out: dict[str, object] = {
            "master": sorted(
                conn.execute(
                    "SELECT type, name, tbl_name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'"
                ).fetchall(),
                key=str,
            )
        }
        for (table,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
            out["cols_" + table] = conn.execute(f"PRAGMA table_info('{table}')").fetchall()
        return json.loads(json.dumps(out, default=str))
    finally:
        conn.close()


def _columns(db_path: Path, table: str) -> set[str]:
    conn = sqlite3.connect(db_path)
    try:
        return {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    finally:
        conn.close()


def _create_legacy_db(path: Path) -> None:
    """Base telle que créée avant l'ajout des colonnes de ADDED_COLUMNS."""
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT, source_type TEXT NOT NULL, name TEXT NOT NULL,
            path_or_uri TEXT NOT NULL UNIQUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_scanned_at TIMESTAMP);
        CREATE TABLE tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, source_ref TEXT NOT NULL UNIQUE, source_type TEXT NOT NULL,
            source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE, source_path TEXT,
            title TEXT, artist TEXT, album_artist TEXT, album TEXT, genre TEXT, year INTEGER,
            track_number INTEGER, disc_number INTEGER, duration_seconds REAL, bitrate INTEGER,
            sample_rate INTEGER, channels INTEGER, format TEXT, file_size INTEGER, file_mtime REAL,
            file_hash TEXT, audio_fingerprint TEXT, isrc TEXT, quality_score INTEGER DEFAULT 0,
            duplicate_cluster_id INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, source_type TEXT DEFAULT 'local',
            external_id TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE playlist_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT, playlist_id INTEGER NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
            position INTEGER NOT NULL, raw_path TEXT NOT NULL, resolved_path TEXT NOT NULL,
            track_id INTEGER REFERENCES tracks(id) ON DELETE SET NULL, title TEXT, artist TEXT,
            duration_seconds REAL, is_missing INTEGER DEFAULT 0);
        CREATE TABLE activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            level TEXT NOT NULL DEFAULT 'INFO', category TEXT NOT NULL DEFAULT 'SYNC', source_name TEXT,
            action TEXT NOT NULL, details TEXT, items_added INTEGER DEFAULT 0, items_updated INTEGER DEFAULT 0,
            items_deleted INTEGER DEFAULT 0, items_errors INTEGER DEFAULT 0);
        INSERT INTO sources (source_type, name, path_or_uri) VALUES ('local', 'Musique', 'C:/Musique');
        INSERT INTO tracks (source_ref, source_type, source_id, source_path, title, duration_seconds)
            VALUES ('a', 'local', 1, 'C:/Musique/Rock/a.flac', 'Titre A', 180.0);
        INSERT INTO tracks (source_ref, source_type, source_id, source_path, title)
            VALUES ('b', 'local', 1, 'C:/Musique/b.mp3', 'Titre B');
        INSERT INTO playlists (name) VALUES ('Ancienne');
        INSERT INTO playlist_entries (playlist_id, position, raw_path, resolved_path)
            VALUES (1, 0, 'a.flac', 'C:/Musique/Rock/a.flac');
        INSERT INTO activity_logs (action) VALUES ('scan');
        """
    )
    conn.commit()
    conn.close()


def test_schema_fresh_db_matches_reference(tmp_path: Path) -> None:
    db = tmp_path / "new.db"
    DatabaseManager(db).close()
    expected = json.loads(REFERENCE.read_text(encoding="utf-8"))
    assert _dump_schema(db) == expected


def test_schema_legacy_db_migration_adds_columns_and_keeps_data(tmp_path: Path) -> None:
    db = tmp_path / "old.db"
    _create_legacy_db(db)
    DatabaseManager(db).close()

    for table, column, _ in ADDED_COLUMNS:
        assert column in _columns(db, table), f"{table}.{column} manquante"

    conn = sqlite3.connect(db)
    try:
        assert conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0] == 2
        assert conn.execute("SELECT title FROM tracks WHERE source_ref='a'").fetchone()[0] == "Titre A"
        assert conn.execute("SELECT COUNT(*) FROM playlist_entries").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM activity_logs").fetchone()[0] == 1
        assert conn.execute("SELECT sync_mode, sync_interval_minutes FROM sources").fetchone() == ("manual", 60)
        # Piste déjà analysée (durée connue) marquée comme telle, l'autre non
        flags = dict(conn.execute("SELECT source_ref, metadata_extracted FROM tracks").fetchall())
        assert flags == {"a": 1, "b": 0}
        row = conn.execute("SELECT file_name, folder_path, folder_name FROM tracks WHERE source_ref='a'").fetchone()
        assert row == ("a.flac", "C:/Musique/Rock", "Rock")
    finally:
        conn.close()


def test_schema_legacy_db_migration_is_idempotent(tmp_path: Path) -> None:
    db = tmp_path / "old.db"
    _create_legacy_db(db)
    DatabaseManager(db).close()
    first = _dump_schema(db)
    conn = sqlite3.connect(db)
    rows_first = conn.execute("SELECT * FROM tracks ORDER BY id").fetchall()
    conn.close()

    DatabaseManager(db).close()

    assert _dump_schema(db) == first
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT * FROM tracks ORDER BY id").fetchall() == rows_first
    conn.close()
