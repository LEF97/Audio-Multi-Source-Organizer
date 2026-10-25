"""Couche de persistance SQLite3 pour AMSO.

Conçue pour absorber de grands volumes (> 50 000 titres) sans ORM lourd,
avec mode WAL, indexation ciblée et recherche plein texte (FTS5).
"""

from __future__ import annotations

import contextlib
import logging
import sqlite3
import time
from collections.abc import Generator
from pathlib import Path

from amso.core.db.activity_repo import ActivityRepoMixin
from amso.core.db.curation_repo import TrackCurationMixin
from amso.core.db.library_queries import LibraryQueriesMixin
from amso.core.db.models import (
    ActivityLogRecord,
    PlaylistEntryRecord,
    PlaylistRecord,
    SourceRecord,
    SourceType,
    TrackRecord,
    compute_quality_score,
)
from amso.core.db.paths import (
    get_database_path,
    get_default_data_dir,
    get_saved_playlist_path,
)
from amso.core.db.playlists_repo import PlaylistsRepoMixin
from amso.core.db.sources_repo import SourcesRepoMixin
from amso.core.db.tracks_repo import TracksRepoMixin

__all__ = [
    "ActivityLogRecord",
    "PlaylistEntryRecord",
    "PlaylistRecord",
    "SourceRecord",
    "SourceType",
    "TrackRecord",
    "compute_quality_score",
    "get_database_path",
    "get_default_data_dir",
    "get_saved_playlist_path",
    "DatabaseManager",
]

logger = logging.getLogger(__name__)


class DatabaseManager(
    SourcesRepoMixin, TracksRepoMixin, TrackCurationMixin, LibraryQueriesMixin, ActivityRepoMixin, PlaylistsRepoMixin
):
    """Gestionnaire de persistance SQLite pour la bibliothèque AMSO."""

    SCHEMA_VERSION = 1

    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path is None:
            self.db_path = str(get_database_path())
        else:
            self.db_path = str(db_path)

        self._memory_conn: sqlite3.Connection | None = None
        if self.db_path == ":memory:":
            self._memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._memory_conn.row_factory = sqlite3.Row
            self._memory_conn.execute("PRAGMA foreign_keys = ON;")
        else:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._init_db_file()

        self.init_schema()

    def _init_db_file(self) -> None:
        """Active le mode WAL et le mode synchrone NORMAL une seule fois au niveau du fichier DB."""
        if self.db_path == ":memory:":
            return
        for attempt in range(5):
            try:
                conn = sqlite3.connect(self.db_path, timeout=30.0)
                try:
                    conn.execute("PRAGMA busy_timeout = 30000;")
                    conn.execute("PRAGMA journal_mode = WAL;")
                    conn.execute("PRAGMA synchronous = NORMAL;")
                finally:
                    conn.close()
                break
            except sqlite3.OperationalError as e:
                if attempt == 4:
                    logger.warning("Impossible d'activer le mode WAL sur %s: %s", self.db_path, e)
                time.sleep(0.05 * (2**attempt))

    def checkpoint(self) -> None:
        """Force un checkpoint WAL passif pour réintégrer les pages dans le fichier principal."""
        if self.db_path == ":memory:":
            return
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            try:
                conn.execute("PRAGMA wal_checkpoint(PASSIVE);")
            finally:
                conn.close()
        except Exception as e:
            logger.debug("wal_checkpoint non exécuté: %s", e)

    def close(self) -> None:
        """Ferme la base de données (utile pour libérer la mémoire ou effectuer un checkpoint final)."""
        if self._memory_conn is not None:
            self._memory_conn.close()
            self._memory_conn = None
        else:
            self.checkpoint()

    @contextlib.contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Fournit une connexion configurée avec gestion automatique de transaction et résilience."""
        if self._memory_conn is not None:
            try:
                yield self._memory_conn
                self._memory_conn.commit()
            except Exception:
                self._memory_conn.rollback()
                raise
            return

        conn: sqlite3.Connection | None = None
        for attempt in range(5):
            try:
                conn = sqlite3.connect(
                    self.db_path,
                    timeout=30.0,
                )
                conn.row_factory = sqlite3.Row

                # Optimisations SQLite par connexion (ne re-déclenche pas de changement de journal_mode)
                conn.execute("PRAGMA busy_timeout = 30000;")
                conn.execute("PRAGMA foreign_keys = ON;")
                conn.execute("PRAGMA temp_store = MEMORY;")
                conn.execute("PRAGMA cache_size = -64000;")  # 64 Mo de cache mémoire
                break
            except sqlite3.OperationalError:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
                    conn = None
                if attempt == 4:
                    raise
                time.sleep(0.05 * (2**attempt))

        if conn is None:
            raise sqlite3.OperationalError(f"Impossible de se connecter à la base SQLite : {self.db_path}")

        try:
            yield conn
            conn.commit()
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            raise
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def init_schema(self) -> None:
        """Initialise le schéma relationnel, les index et l'index FTS5."""
        with self.get_connection() as conn:
            # 1. Sources
            conn.execute(
                """
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
            )

            # 2. Tracks
            conn.execute(
                """
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
            )

            # Migration incrémentale sources
            cur_s = conn.execute("PRAGMA table_info(sources);")
            cols_s = {r["name"] for r in cur_s.fetchall()}
            if "sync_mode" not in cols_s:
                conn.execute("ALTER TABLE sources ADD COLUMN sync_mode TEXT NOT NULL DEFAULT 'manual';")
            if "sync_interval_minutes" not in cols_s:
                conn.execute("ALTER TABLE sources ADD COLUMN sync_interval_minutes INTEGER DEFAULT 60;")
            if "sync_interval_seconds" not in cols_s:
                conn.execute("ALTER TABLE sources ADD COLUMN sync_interval_seconds INTEGER DEFAULT 60;")

            # Migration incrémentale tracks
            cur = conn.execute("PRAGMA table_info(tracks);")
            cols = {r["name"] for r in cur.fetchall()}
            if "file_name" not in cols:
                conn.execute("ALTER TABLE tracks ADD COLUMN file_name TEXT;")
            if "folder_path" not in cols:
                conn.execute("ALTER TABLE tracks ADD COLUMN folder_path TEXT;")
            if "folder_name" not in cols:
                conn.execute("ALTER TABLE tracks ADD COLUMN folder_name TEXT;")
            if "metadata_extracted" not in cols:
                conn.execute("ALTER TABLE tracks ADD COLUMN metadata_extracted INTEGER DEFAULT 0;")
                # Les pistes préexistantes ayant déjà une durée sont considérées comme analysées
                conn.execute(
                    "UPDATE tracks SET metadata_extracted = 1 WHERE duration_seconds IS NOT NULL OR file_hash IS NOT NULL;"
                )

            # Backfill des colonnes de chemin/nom pour les enregistrements existants
            existing_unfilled = conn.execute(
                "SELECT id, source_path FROM tracks WHERE source_path IS NOT NULL AND (file_name IS NULL OR folder_path IS NULL);"
            ).fetchall()
            for r in existing_unfilled:
                sp = str(r["source_path"]).replace("\\", "/")
                parts = sp.rsplit("/", 1)
                fn = parts[-1] if parts else ""
                fp = parts[0] if len(parts) > 1 else ""
                f_parent = fp.rsplit("/", 1)[-1] if fp else ""
                conn.execute(
                    "UPDATE tracks SET file_name = ?, folder_path = ?, folder_name = ? WHERE id = ?;",
                    (fn, fp, f_parent, r["id"]),
                )

            # 3. Index de performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_source ON tracks(source_id, source_type);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_folder ON tracks(source_id, folder_path);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_file_name ON tracks(file_name);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_folder_name ON tracks(folder_name);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_artist_album ON tracks(artist, album);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_title ON tracks(title);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_file_hash ON tracks(file_hash);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_cluster ON tracks(duplicate_cluster_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_isrc ON tracks(isrc);")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_tracks_meta_extracted ON tracks(metadata_extracted, source_id);"
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sources_sync_mode ON sources(sync_mode);")

            # 4. Table virtuelle FTS5 pour recherche plein texte ultra-rapide
            conn.execute(
                """
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
            )

            # 5. Triggers de synchronisation FTS5
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS tracks_ai AFTER INSERT ON tracks BEGIN
                    INSERT INTO tracks_fts(rowid, title, artist, album, album_artist, genre)
                    VALUES (new.id, new.title, new.artist, new.album, new.album_artist, new.genre);
                END;
                """
            )
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS tracks_ad AFTER DELETE ON tracks BEGIN
                    INSERT INTO tracks_fts(tracks_fts, rowid, title, artist, album, album_artist, genre)
                    VALUES ('delete', old.id, old.title, old.artist, old.album, old.album_artist, old.genre);
                END;
                """
            )
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS tracks_au AFTER UPDATE ON tracks BEGIN
                    INSERT INTO tracks_fts(tracks_fts, rowid, title, artist, album, album_artist, genre)
                    VALUES ('delete', old.id, old.title, old.artist, old.album, old.album_artist, old.genre);
                    INSERT INTO tracks_fts(rowid, title, artist, album, album_artist, genre)
                    VALUES (new.id, new.title, new.artist, new.album, new.album_artist, new.genre);
                END;
                """
            )

            # 6. Playlists & Entrées de Playlist (M3U, PLS, XSPF, WPL)
            conn.execute(
                """
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
            )
            # Migration incrémentale playlists
            cur_pl = conn.execute("PRAGMA table_info(playlists);")
            cols_pl = {r["name"] for r in cur_pl.fetchall()}
            if "source_id" not in cols_pl:
                conn.execute(
                    "ALTER TABLE playlists ADD COLUMN source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE;"
                )
            if "file_path" not in cols_pl:
                conn.execute("ALTER TABLE playlists ADD COLUMN file_path TEXT;")
            if "folder_path" not in cols_pl:
                conn.execute("ALTER TABLE playlists ADD COLUMN folder_path TEXT;")
            if "format" not in cols_pl:
                conn.execute("ALTER TABLE playlists ADD COLUMN format TEXT;")
            if "track_count" not in cols_pl:
                conn.execute("ALTER TABLE playlists ADD COLUMN track_count INTEGER DEFAULT 0;")
            if "file_mtime" not in cols_pl:
                conn.execute("ALTER TABLE playlists ADD COLUMN file_mtime REAL DEFAULT 0;")
            if "file_size" not in cols_pl:
                conn.execute("ALTER TABLE playlists ADD COLUMN file_size INTEGER DEFAULT 0;")

            conn.execute("CREATE INDEX IF NOT EXISTS idx_playlists_source ON playlists(source_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_playlists_folder ON playlists(source_id, folder_path);")
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_playlists_path ON playlists(file_path);")

            conn.execute(
                """
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
            )
            # Migration incrémentale playlist_entries (pistes virtuelles CUE : début/fin dans le fichier audio)
            cols_pe = {r["name"] for r in conn.execute("PRAGMA table_info(playlist_entries);").fetchall()}
            if "start_ms" not in cols_pe:
                conn.execute("ALTER TABLE playlist_entries ADD COLUMN start_ms INTEGER;")
            if "end_ms" not in cols_pe:
                conn.execute("ALTER TABLE playlist_entries ADD COLUMN end_ms INTEGER;")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pl_entries_pl ON playlist_entries(playlist_id, position);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pl_entries_track ON playlist_entries(track_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pl_entries_resolved ON playlist_entries(resolved_path);")
            # 7. Activity Logs
            conn.execute(
                """
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
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_activity_logs_ts ON activity_logs(timestamp DESC);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_activity_logs_level ON activity_logs(level);")

            # 8. Table des pistes exclues/ignorées pour éviter leur réimportation lors des synchronisations
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ignored_tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_ref TEXT NOT NULL UNIQUE,
                    source_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ignored_tracks_ref ON ignored_tracks(source_ref);")

    # -------------------------------------------------------------------------
    # Sources CRUD
    # -------------------------------------------------------------------------
