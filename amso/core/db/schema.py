"""Schéma SQLite d'AMSO : DDL des tables, colonnes ajoutées après coup et index.

Les DDL sont conservés à l'identique (SQLite stocke le texte du DDL dans sqlite_master) afin
qu'une base neuve garde exactement le même schéma qu'avant l'extraction de ce module.
"""

from __future__ import annotations

import sqlite3

SOURCES_DDL = """
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    path_or_uri TEXT NOT NULL UNIQUE,
                    sync_mode TEXT NOT NULL DEFAULT 'manual',
                    sync_interval_minutes INTEGER DEFAULT 60,
                    sync_interval_seconds INTEGER DEFAULT 60,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_scanned_at TIMESTAMP
                );
                """

TRACKS_DDL = """
                CREATE TABLE IF NOT EXISTS tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_ref TEXT NOT NULL UNIQUE,
                    source_type TEXT NOT NULL,
                    source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,
                    source_path TEXT,
                    file_name TEXT,
                    folder_path TEXT,
                    folder_name TEXT,

                    title TEXT,
                    artist TEXT,
                    album_artist TEXT,
                    album TEXT,
                    genre TEXT,
                    year INTEGER,
                    track_number INTEGER,
                    disc_number INTEGER,

                    duration_seconds REAL,
                    bitrate INTEGER,
                    sample_rate INTEGER,
                    channels INTEGER,
                    format TEXT,

                    file_size INTEGER,
                    file_mtime REAL,
                    file_hash TEXT,
                    audio_fingerprint TEXT,
                    isrc TEXT,

                    quality_score INTEGER DEFAULT 0,
                    duplicate_cluster_id INTEGER,
                    metadata_extracted INTEGER DEFAULT 0,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """

TRACKS_FTS_DDL = """
                CREATE VIRTUAL TABLE IF NOT EXISTS tracks_fts USING fts5(
                    title,
                    artist,
                    album,
                    album_artist,
                    genre,
                    content='tracks',
                    content_rowid='id'
                );
                """

TRACKS_FTS_TRIGGERS_DDL = (
    """
                CREATE TRIGGER IF NOT EXISTS tracks_ai AFTER INSERT ON tracks BEGIN
                    INSERT INTO tracks_fts(rowid, title, artist, album, album_artist, genre)
                    VALUES (new.id, new.title, new.artist, new.album, new.album_artist, new.genre);
                END;
                """,
    """
                CREATE TRIGGER IF NOT EXISTS tracks_ad AFTER DELETE ON tracks BEGIN
                    INSERT INTO tracks_fts(tracks_fts, rowid, title, artist, album, album_artist, genre)
                    VALUES ('delete', old.id, old.title, old.artist, old.album, old.album_artist, old.genre);
                END;
                """,
    """
                CREATE TRIGGER IF NOT EXISTS tracks_au AFTER UPDATE ON tracks BEGIN
                    INSERT INTO tracks_fts(tracks_fts, rowid, title, artist, album, album_artist, genre)
                    VALUES ('delete', old.id, old.title, old.artist, old.album, old.album_artist, old.genre);
                    INSERT INTO tracks_fts(rowid, title, artist, album, album_artist, genre)
                    VALUES (new.id, new.title, new.artist, new.album, new.album_artist, new.genre);
                END;
                """,
)

PLAYLISTS_DDL = """
                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    file_path TEXT UNIQUE,
                    folder_path TEXT,
                    format TEXT,
                    track_count INTEGER DEFAULT 0,
                    file_mtime REAL DEFAULT 0,
                    file_size INTEGER DEFAULT 0,
                    source_type TEXT DEFAULT 'local',
                    external_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """

PLAYLIST_ENTRIES_DDL = """
                CREATE TABLE IF NOT EXISTS playlist_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    playlist_id INTEGER NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
                    position INTEGER NOT NULL,
                    raw_path TEXT NOT NULL,
                    resolved_path TEXT NOT NULL,
                    track_id INTEGER REFERENCES tracks(id) ON DELETE SET NULL,
                    title TEXT,
                    artist TEXT,
                    duration_seconds REAL,
                    is_missing INTEGER DEFAULT 0,
                    start_ms INTEGER,
                    end_ms INTEGER
                );
                """

ACTIVITY_LOGS_DDL = """
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    level TEXT NOT NULL DEFAULT 'INFO',
                    category TEXT NOT NULL DEFAULT 'SYNC',
                    source_name TEXT,
                    action TEXT NOT NULL,
                    details TEXT,
                    items_added INTEGER DEFAULT 0,
                    items_updated INTEGER DEFAULT 0,
                    items_deleted INTEGER DEFAULT 0,
                    items_errors INTEGER DEFAULT 0
                );
                """

IGNORED_TRACKS_DDL = """
                CREATE TABLE IF NOT EXISTS ignored_tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_ref TEXT NOT NULL UNIQUE,
                    source_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """

# Colonnes absentes des bases créées par d'anciennes versions : (table, colonne, définition).
# Ajouter une colonne = une ligne ici + la colonne dans le CREATE TABLE ; la valeur par défaut est
# obligatoire pour les lignes existantes. Jamais de suppression ni de réécriture de données.
ADDED_COLUMNS: tuple[tuple[str, str, str], ...] = (
    ("sources", "sync_mode", "TEXT NOT NULL DEFAULT 'manual'"),
    ("sources", "sync_interval_minutes", "INTEGER DEFAULT 60"),
    ("sources", "sync_interval_seconds", "INTEGER DEFAULT 60"),
    ("tracks", "file_name", "TEXT"),
    ("tracks", "folder_path", "TEXT"),
    ("tracks", "folder_name", "TEXT"),
    ("tracks", "metadata_extracted", "INTEGER DEFAULT 0"),
    ("playlists", "source_id", "INTEGER REFERENCES sources(id) ON DELETE CASCADE"),
    ("playlists", "file_path", "TEXT"),
    ("playlists", "folder_path", "TEXT"),
    ("playlists", "format", "TEXT"),
    ("playlists", "track_count", "INTEGER DEFAULT 0"),
    ("playlists", "file_mtime", "REAL DEFAULT 0"),
    ("playlists", "file_size", "INTEGER DEFAULT 0"),
    # Pistes virtuelles CUE : début/fin dans le fichier audio
    ("playlist_entries", "start_ms", "INTEGER"),
    ("playlist_entries", "end_ms", "INTEGER"),
    ("activity_logs", "i18n", "TEXT"),
)

TRACKS_INDEXES: tuple[str, ...] = (
    "CREATE INDEX IF NOT EXISTS idx_tracks_source ON tracks(source_id, source_type);",
    "CREATE INDEX IF NOT EXISTS idx_tracks_source_path ON tracks(source_path);",
    "CREATE INDEX IF NOT EXISTS idx_tracks_folder ON tracks(source_id, folder_path);",
    "CREATE INDEX IF NOT EXISTS idx_tracks_file_name ON tracks(file_name);",
    "CREATE INDEX IF NOT EXISTS idx_tracks_folder_name ON tracks(folder_name);",
    "CREATE INDEX IF NOT EXISTS idx_tracks_artist_album ON tracks(artist, album);",
    "CREATE INDEX IF NOT EXISTS idx_tracks_title ON tracks(title);",
    "CREATE INDEX IF NOT EXISTS idx_tracks_file_hash ON tracks(file_hash);",
    "CREATE INDEX IF NOT EXISTS idx_tracks_cluster ON tracks(duplicate_cluster_id);",
    "CREATE INDEX IF NOT EXISTS idx_tracks_isrc ON tracks(isrc);",
    "CREATE INDEX IF NOT EXISTS idx_tracks_meta_extracted ON tracks(metadata_extracted, source_id);",
    "CREATE INDEX IF NOT EXISTS idx_sources_sync_mode ON sources(sync_mode);",
)

PLAYLISTS_INDEXES: tuple[str, ...] = (
    "CREATE INDEX IF NOT EXISTS idx_playlists_source ON playlists(source_id);",
    "CREATE INDEX IF NOT EXISTS idx_playlists_folder ON playlists(source_id, folder_path);",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_playlists_path ON playlists(file_path);",
)

PLAYLIST_ENTRIES_INDEXES: tuple[str, ...] = (
    "CREATE INDEX IF NOT EXISTS idx_pl_entries_pl ON playlist_entries(playlist_id, position);",
    "CREATE INDEX IF NOT EXISTS idx_pl_entries_track ON playlist_entries(track_id);",
    "CREATE INDEX IF NOT EXISTS idx_pl_entries_resolved ON playlist_entries(resolved_path);",
)

ACTIVITY_LOGS_INDEXES: tuple[str, ...] = (
    "CREATE INDEX IF NOT EXISTS idx_activity_logs_ts ON activity_logs(timestamp DESC);",
    "CREATE INDEX IF NOT EXISTS idx_activity_logs_level ON activity_logs(level);",
)

IGNORED_TRACKS_INDEXES: tuple[str, ...] = (
    "CREATE INDEX IF NOT EXISTS idx_ignored_tracks_ref ON ignored_tracks(source_ref);",
)


def add_missing_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    """Ajoute à `table` les colonnes de ADDED_COLUMNS absentes ; renvoie les colonnes ajoutées."""
    present = {r[1] for r in conn.execute(f"PRAGMA table_info({table});").fetchall()}
    added: set[str] = set()
    for tbl, column, ddl in ADDED_COLUMNS:
        if tbl == table and column not in present:
            # Noms issus de la constante ADDED_COLUMNS (jamais d'entrée utilisateur)
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl};")
            added.add(column)
    return added


def _backfill_tracks(conn: sqlite3.Connection, added: set[str]) -> None:
    if "metadata_extracted" in added:
        # Les pistes préexistantes ayant déjà une durée sont considérées comme analysées
        conn.execute(
            "UPDATE tracks SET metadata_extracted = 1 WHERE duration_seconds IS NOT NULL OR file_hash IS NOT NULL;"
        )
    # Backfill des colonnes de chemin/nom pour les enregistrements existants
    unfilled = conn.execute(
        "SELECT id, source_path FROM tracks WHERE source_path IS NOT NULL AND (file_name IS NULL OR folder_path IS NULL);"
    ).fetchall()
    for row in unfilled:
        sp = str(row[1]).replace("\\", "/")
        parts = sp.rsplit("/", 1)
        fn = parts[-1] if parts else ""
        fp = parts[0] if len(parts) > 1 else ""
        f_parent = fp.rsplit("/", 1)[-1] if fp else ""
        conn.execute(
            "UPDATE tracks SET file_name = ?, folder_path = ?, folder_name = ? WHERE id = ?;",
            (fn, fp, f_parent, row[0]),
        )


def _create_table(conn: sqlite3.Connection, ddl: str, table: str, indexes: tuple[str, ...]) -> None:
    conn.execute(ddl)
    add_missing_columns(conn, table)
    for stmt in indexes:
        conn.execute(stmt)


def apply_schema(conn: sqlite3.Connection) -> None:
    """Crée le schéma (tables, FTS5, triggers, index) et migre les anciennes bases, de façon idempotente."""
    conn.execute(SOURCES_DDL)
    add_missing_columns(conn, "sources")
    conn.execute(TRACKS_DDL)
    _backfill_tracks(conn, add_missing_columns(conn, "tracks"))
    # Les index de tracks/sources viennent après l'ajout des colonnes qu'ils référencent
    for stmt in TRACKS_INDEXES:
        conn.execute(stmt)
    conn.execute(TRACKS_FTS_DDL)
    for trigger in TRACKS_FTS_TRIGGERS_DDL:
        conn.execute(trigger)
    _create_table(conn, PLAYLISTS_DDL, "playlists", PLAYLISTS_INDEXES)
    _create_table(conn, PLAYLIST_ENTRIES_DDL, "playlist_entries", PLAYLIST_ENTRIES_INDEXES)
    _create_table(conn, ACTIVITY_LOGS_DDL, "activity_logs", ACTIVITY_LOGS_INDEXES)
    _create_table(conn, IGNORED_TRACKS_DDL, "ignored_tracks", IGNORED_TRACKS_INDEXES)
