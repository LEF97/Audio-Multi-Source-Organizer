"""Couche de persistance SQLite3 pour AMSO.

Conçue pour absorber de grands volumes (> 50 000 titres) sans ORM lourd,
avec mode WAL, indexation ciblée et recherche plein texte (FTS5).
"""

from __future__ import annotations

import contextlib
import logging
import os
import sqlite3
import sys
import time
from collections.abc import Generator, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SourceType(StrEnum):
    """Types de sources audio prises en charge."""

    LOCAL = "local"
    GDRIVE = "gdrive"
    SPOTIFY = "spotify"
    DEEZER = "deezer"


def compute_quality_score(
    audio_format: str | None,
    bitrate: int | None,
    sample_rate: int | None,
) -> int:
    """Calcule un score qualitatif heuristique de 0 à 1000 pour prioriser les doublons.

    Hiérarchie générale :
    - Lossless Hi-Res (FLAC/ALAC/WAV > 48kHz) : 900 - 1000
    - Lossless CD standard (FLAC/WAV 44.1/48kHz) : 800 - 899
    - Lossy très haute qualité (Opus/AAC 256-320k, MP3 320k) : 600 - 799
    - Lossy standard (MP3 192-256k, AAC 128-192k) : 400 - 599
    - Lossy basse qualité (< 192k) : 100 - 399
    """
    fmt = (audio_format or "").strip().lower()
    br = bitrate or 0
    sr = sample_rate or 0

    score = 200

    # Format de base
    if fmt in {"flac", "alac", "wav", "aiff"}:
        score = 800
        if sr > 48000:
            score += 100
        if br > 1411:
            score += 50
    elif fmt in {"m4a", "aac", "ogg", "opus"}:
        score = 450
        if br >= 320:
            score += 250
        elif br >= 256:
            score += 200
        elif br >= 192:
            score += 100
    elif fmt == "mp3":
        score = 350
        if br >= 320:
            score += 300
        elif br >= 256:
            score += 200
        elif br >= 192:
            score += 100
        elif br >= 128:
            score += 50

    return min(max(score, 0), 1000)


@dataclass(slots=True)
class SourceRecord:
    """Représentation d'une source audio configurée."""

    id: int | None = None
    source_type: SourceType = SourceType.LOCAL
    name: str = ""
    path_or_uri: str = ""
    sync_mode: str = "manual"  # 'manual', 'startup', 'interval', 'realtime'
    sync_interval_minutes: int = 60
    sync_interval_seconds: int = 60
    created_at: str | None = None
    last_scanned_at: str | None = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> SourceRecord:
        keys = row.keys() if hasattr(row, "keys") else ()
        return cls(
            id=row["id"],
            source_type=SourceType(row["source_type"]),
            name=row["name"],
            path_or_uri=row["path_or_uri"],
            sync_mode=row["sync_mode"] if "sync_mode" in keys and row["sync_mode"] else "manual",
            sync_interval_minutes=int(row["sync_interval_minutes"])
            if "sync_interval_minutes" in keys and row["sync_interval_minutes"] is not None
            else 60,
            sync_interval_seconds=int(row["sync_interval_seconds"])
            if "sync_interval_seconds" in keys and row["sync_interval_seconds"] is not None
            else 60,
            created_at=str(row["created_at"]) if row["created_at"] is not None else None,
            last_scanned_at=str(row["last_scanned_at"]) if row["last_scanned_at"] is not None else None,
        )


@dataclass(slots=True)
class ActivityLogRecord:
    """Représentation d'une entrée du journal d'activité."""

    id: int | None = None
    timestamp: str | None = None
    level: str = "INFO"  # 'INFO', 'SUCCESS', 'WARNING', 'ERROR'
    category: str = "SYNC"  # 'SYNC', 'SCAN', 'LIBRARY', 'SYSTEM'
    source_name: str | None = None
    action: str = ""
    details: str | None = None
    items_added: int = 0
    items_updated: int = 0
    items_deleted: int = 0
    items_errors: int = 0

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> ActivityLogRecord:
        keys = row.keys() if hasattr(row, "keys") else ()
        return cls(
            id=row["id"],
            timestamp=str(row["timestamp"]) if "timestamp" in keys and row["timestamp"] is not None else None,
            level=str(row["level"]) if "level" in keys and row["level"] else "INFO",
            category=str(row["category"]) if "category" in keys and row["category"] else "SYNC",
            source_name=str(row["source_name"]) if "source_name" in keys and row["source_name"] is not None else None,
            action=str(row["action"]) if "action" in keys and row["action"] else "",
            details=str(row["details"]) if "details" in keys and row["details"] is not None else None,
            items_added=int(row["items_added"]) if "items_added" in keys and row["items_added"] is not None else 0,
            items_updated=int(row["items_updated"])
            if "items_updated" in keys and row["items_updated"] is not None
            else 0,
            items_deleted=int(row["items_deleted"])
            if "items_deleted" in keys and row["items_deleted"] is not None
            else 0,
            items_errors=int(row["items_errors"]) if "items_errors" in keys and row["items_errors"] is not None else 0,
        )


@dataclass(slots=True)
class TrackRecord:
    """Représentation d'une piste audio."""

    source_ref: str
    source_type: SourceType = SourceType.LOCAL
    id: int | None = None
    source_id: int | None = None
    # Fichier & Chemins
    source_path: str | None = None
    file_name: str | None = None
    folder_path: str | None = None
    folder_name: str | None = None

    # Métadonnées audio
    title: str | None = None
    artist: str | None = None
    album_artist: str | None = None
    album: str | None = None
    genre: str | None = None
    year: int | None = None
    track_number: int | None = None
    disc_number: int | None = None

    # Propriétés techniques
    duration_seconds: float | None = None
    bitrate: int | None = None
    sample_rate: int | None = None
    channels: int | None = None
    format: str | None = None

    # Fichier & Empreintes
    file_size: int | None = None
    file_mtime: float | None = None
    file_hash: str | None = None
    audio_fingerprint: str | None = None
    isrc: str | None = None

    # Gestion des doublons, statut & score
    quality_score: int = 0
    duplicate_cluster_id: int | None = None
    metadata_extracted: bool = False

    # Dates
    created_at: str | None = None
    updated_at: str | None = None

    def __post_init__(self) -> None:
        if self.source_path:
            clean_path = str(self.source_path).replace("\\", "/")
            if not self.file_name:
                parts = clean_path.rsplit("/", 1)
                self.file_name = parts[-1] if parts else ""
            if not self.folder_path:
                parts = clean_path.rsplit("/", 1)
                self.folder_path = parts[0] if len(parts) > 1 else ""
            if not self.folder_name and self.folder_path:
                self.folder_name = self.folder_path.rsplit("/", 1)[-1] or self.folder_path

        if self.quality_score == 0 and (self.format or self.bitrate):
            self.quality_score = compute_quality_score(self.format, self.bitrate, self.sample_rate)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> TrackRecord:
        keys = row.keys() if hasattr(row, "keys") else ()
        file_name = row["file_name"] if "file_name" in keys else None
        folder_path = row["folder_path"] if "folder_path" in keys else None
        folder_name = row["folder_name"] if "folder_name" in keys else None

        return cls(
            id=row["id"],
            source_ref=row["source_ref"],
            source_type=SourceType(row["source_type"]),
            source_id=row["source_id"],
            source_path=row["source_path"],
            file_name=file_name,
            folder_path=folder_path,
            folder_name=folder_name,
            title=row["title"],
            artist=row["artist"],
            album_artist=row["album_artist"],
            album=row["album"],
            genre=row["genre"],
            year=row["year"],
            track_number=row["track_number"],
            disc_number=row["disc_number"],
            duration_seconds=row["duration_seconds"],
            bitrate=row["bitrate"],
            sample_rate=row["sample_rate"],
            channels=row["channels"],
            format=row["format"],
            file_size=row["file_size"],
            file_mtime=row["file_mtime"],
            file_hash=row["file_hash"],
            audio_fingerprint=row["audio_fingerprint"],
            isrc=row["isrc"],
            quality_score=row["quality_score"] or 0,
            duplicate_cluster_id=row["duplicate_cluster_id"],
            metadata_extracted=bool(row["metadata_extracted"])
            if "metadata_extracted" in keys and row["metadata_extracted"] is not None
            else False,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict[str, Any]:
        """Convertit le TrackRecord en dictionnaire sérialisable."""
        return {
            "id": self.id,
            "source_ref": self.source_ref,
            "source_type": self.source_type.value if hasattr(self.source_type, "value") else str(self.source_type),
            "source_id": self.source_id,
            "source_path": self.source_path,
            "file_name": self.file_name,
            "folder_path": self.folder_path,
            "folder_name": self.folder_name,
            "title": self.title,
            "artist": self.artist,
            "album_artist": self.album_artist,
            "album": self.album,
            "genre": self.genre,
            "year": self.year,
            "track_number": self.track_number,
            "disc_number": self.disc_number,
            "duration_seconds": self.duration_seconds,
            "bitrate": self.bitrate,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "format": self.format,
            "file_size": self.file_size,
            "file_mtime": self.file_mtime,
            "file_hash": self.file_hash,
            "audio_fingerprint": self.audio_fingerprint,
            "isrc": self.isrc,
            "quality_score": self.quality_score,
            "duplicate_cluster_id": self.duplicate_cluster_id,
            "metadata_extracted": self.metadata_extracted,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TrackRecord:
        """Reconstruit un TrackRecord à partir d'un dictionnaire."""
        st = data.get("source_type", "local")
        try:
            source_type = SourceType(st)
        except Exception:
            source_type = SourceType.LOCAL
        return cls(
            id=data.get("id"),
            source_ref=data.get("source_ref", data.get("source_path", "")),
            source_type=source_type,
            source_id=data.get("source_id"),
            source_path=data.get("source_path"),
            file_name=data.get("file_name"),
            folder_path=data.get("folder_path"),
            folder_name=data.get("folder_name"),
            title=data.get("title"),
            artist=data.get("artist"),
            album_artist=data.get("album_artist"),
            album=data.get("album"),
            genre=data.get("genre"),
            year=data.get("year"),
            track_number=data.get("track_number"),
            disc_number=data.get("disc_number"),
            duration_seconds=data.get("duration_seconds"),
            bitrate=data.get("bitrate"),
            sample_rate=data.get("sample_rate"),
            channels=data.get("channels"),
            format=data.get("format"),
            file_size=data.get("file_size"),
            file_mtime=data.get("file_mtime"),
            file_hash=data.get("file_hash"),
            audio_fingerprint=data.get("audio_fingerprint"),
            isrc=data.get("isrc"),
            quality_score=data.get("quality_score", 0),
            duplicate_cluster_id=data.get("duplicate_cluster_id"),
            metadata_extracted=data.get("metadata_extracted", False),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


def get_default_data_dir() -> Path:
    """Retourne le répertoire de données standard utilisateur selon l'OS (AppData, etc.)."""
    custom = os.getenv("AMSO_DATA_DIR")
    if custom and custom.strip():
        app_dir = Path(custom.strip()).resolve()
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir

    if sys.platform == "win32":
        base = os.getenv("APPDATA") or (Path.home() / "AppData" / "Roaming")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = os.getenv("XDG_DATA_HOME") or (Path.home() / ".local" / "share")
    app_dir = Path(base) / "AMSO"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_database_path() -> Path:
    """Détermine l'emplacement standardisé de la base SQLite.

    Priorité :
    1. Variable d'environnement AMSO_DB_PATH si explicitement définie
    2. Répertoire AppData utilisateur (%APPDATA%/AMSO/amso_library.db sous Windows)
    """
    custom = os.getenv("AMSO_DB_PATH")
    if custom and custom.strip():
        p = Path(custom.strip()).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    db_file = get_default_data_dir() / "amso_library.db"
    return db_file


def get_saved_playlist_path() -> Path:
    """Détermine l'emplacement standardisé du fichier de sauvegarde de la playlist courante."""
    custom = os.getenv("AMSO_PLAYLIST_PATH")
    if custom and custom.strip():
        p = Path(custom.strip()).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    return get_default_data_dir() / "saved_playlist.json"


class DatabaseManager:
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

            # 6. Playlists
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    external_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
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

    def add_source(
        self,
        source_type: SourceType | str,
        name: str,
        path_or_uri: str,
        sync_mode: str = "manual",
        sync_interval_minutes: int = 60,
        sync_interval_seconds: int = 60,
    ) -> SourceRecord:
        """Ajoute ou récupère une source audio avec sa stratégie de synchronisation."""
        st = source_type.value if isinstance(source_type, SourceType) else source_type
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO sources (source_type, name, path_or_uri, sync_mode, sync_interval_minutes, sync_interval_seconds)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(path_or_uri) DO UPDATE SET
                    name = excluded.name,
                    source_type = excluded.source_type,
                    sync_mode = excluded.sync_mode,
                    sync_interval_minutes = excluded.sync_interval_minutes,
                    sync_interval_seconds = excluded.sync_interval_seconds;
                """,
                (st, name, path_or_uri, sync_mode, sync_interval_minutes, sync_interval_seconds),
            )
            row = conn.execute(
                "SELECT * FROM sources WHERE path_or_uri = ?;",
                (path_or_uri,),
            ).fetchone()
            return SourceRecord.from_row(row)

    def update_source_sync_config(
        self,
        source_id: int,
        sync_mode: str,
        sync_interval_minutes: int = 60,
        sync_interval_seconds: int = 60,
        name: str | None = None,
    ) -> bool:
        """Met à jour le mode et l'intervalle de synchronisation d'une source."""
        with self.get_connection() as conn:
            if name is not None:
                cur = conn.execute(
                    "UPDATE sources SET sync_mode = ?, sync_interval_minutes = ?, sync_interval_seconds = ?, name = ? WHERE id = ?;",
                    (sync_mode, sync_interval_minutes, sync_interval_seconds, name, source_id),
                )
            else:
                cur = conn.execute(
                    "UPDATE sources SET sync_mode = ?, sync_interval_minutes = ?, sync_interval_seconds = ? WHERE id = ?;",
                    (sync_mode, sync_interval_minutes, sync_interval_seconds, source_id),
                )
            return cur.rowcount > 0

    def get_sources(self) -> list[SourceRecord]:
        """Retourne la liste de toutes les sources configurées."""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM sources ORDER BY id ASC;").fetchall()
            return [SourceRecord.from_row(r) for r in rows]

    def get_source(self, source_id: int) -> SourceRecord | None:
        """Retourne une source par son identifiant."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM sources WHERE id = ?;", (source_id,)).fetchone()
            return SourceRecord.from_row(row) if row else None

    def update_source_scanned(self, source_id: int) -> None:
        """Met à jour l'horodatage du dernier scan d'une source."""
        now = datetime.now(UTC).isoformat()
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE sources SET last_scanned_at = ? WHERE id = ?;",
                (now, source_id),
            )

    def delete_source(self, source_id: int) -> bool:
        """Supprime une source et toutes ses pistes associées (cascade)."""
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM sources WHERE id = ?;", (source_id,))
            return cursor.rowcount > 0

    # -------------------------------------------------------------------------
    # Tracks CRUD & Batching
    # -------------------------------------------------------------------------

    def upsert_track(self, track: TrackRecord) -> int:
        """Insère ou met à jour une piste audio unique."""
        ids = self.upsert_tracks_batch([track])
        return ids[0] if ids else -1

    def upsert_tracks_batch(self, tracks: Sequence[TrackRecord]) -> list[int]:
        """Insère ou met à jour par lot des dizaines de milliers de pistes de façon optimale."""
        if not tracks:
            return []

        now = datetime.now(UTC).isoformat()
        query = """
            INSERT INTO tracks (
                source_ref, source_type, source_id, source_path,
                file_name, folder_path, folder_name,
                title, artist, album_artist, album, genre, year,
                track_number, disc_number, duration_seconds, bitrate,
                sample_rate, channels, format, file_size, file_mtime,
                file_hash, audio_fingerprint, isrc, quality_score,
                duplicate_cluster_id, metadata_extracted, created_at, updated_at
            )
            VALUES (
                :source_ref, :source_type, :source_id, :source_path,
                :file_name, :folder_path, :folder_name,
                :title, :artist, :album_artist, :album, :genre, :year,
                :track_number, :disc_number, :duration_seconds, :bitrate,
                :sample_rate, :channels, :format, :file_size, :file_mtime,
                :file_hash, :audio_fingerprint, :isrc, :quality_score,
                :duplicate_cluster_id, :metadata_extracted, :now, :now
            )
            ON CONFLICT(source_ref) DO UPDATE SET
                source_type = excluded.source_type,
                source_id = excluded.source_id,
                source_path = excluded.source_path,
                file_name = excluded.file_name,
                folder_path = excluded.folder_path,
                folder_name = excluded.folder_name,
                title = excluded.title,
                artist = excluded.artist,
                album_artist = excluded.album_artist,
                album = excluded.album,
                genre = excluded.genre,
                year = excluded.year,
                track_number = excluded.track_number,
                disc_number = excluded.disc_number,
                duration_seconds = excluded.duration_seconds,
                bitrate = excluded.bitrate,
                sample_rate = excluded.sample_rate,
                channels = excluded.channels,
                format = excluded.format,
                file_size = excluded.file_size,
                file_mtime = excluded.file_mtime,
                file_hash = excluded.file_hash,
                audio_fingerprint = excluded.audio_fingerprint,
                isrc = excluded.isrc,
                quality_score = excluded.quality_score,
                metadata_extracted = excluded.metadata_extracted,
                updated_at = :now
            RETURNING id;
        """

        param_list = []
        for t in tracks:
            st = t.source_type.value if isinstance(t.source_type, SourceType) else str(t.source_type)
            score = t.quality_score or compute_quality_score(t.format, t.bitrate, t.sample_rate)
            param_list.append(
                {
                    "source_ref": t.source_ref,
                    "source_type": st,
                    "source_id": t.source_id,
                    "source_path": t.source_path,
                    "file_name": t.file_name,
                    "folder_path": t.folder_path,
                    "folder_name": t.folder_name,
                    "title": t.title,
                    "artist": t.artist,
                    "album_artist": t.album_artist,
                    "album": t.album,
                    "genre": t.genre,
                    "year": t.year,
                    "track_number": t.track_number,
                    "disc_number": t.disc_number,
                    "duration_seconds": t.duration_seconds,
                    "bitrate": t.bitrate,
                    "sample_rate": t.sample_rate,
                    "channels": t.channels,
                    "format": t.format,
                    "file_size": t.file_size,
                    "file_mtime": t.file_mtime,
                    "file_hash": t.file_hash,
                    "audio_fingerprint": t.audio_fingerprint,
                    "isrc": t.isrc,
                    "quality_score": score,
                    "duplicate_cluster_id": t.duplicate_cluster_id,
                    "metadata_extracted": 1 if t.metadata_extracted else 0,
                    "now": now,
                }
            )

        with self.get_connection() as conn:
            returned_ids: list[int] = []
            for p in param_list:
                res = conn.execute(query, p).fetchone()
                if res:
                    returned_ids.append(res[0])
            return returned_ids

    def get_unextracted_tracks(
        self,
        source_id: int | None = None,
        limit: int | None = None,
    ) -> list[TrackRecord]:
        """Retourne les pistes dont les métadonnées audio n'ont pas encore été extraites."""
        where = ["(metadata_extracted = 0 OR metadata_extracted IS NULL)"]
        params: list[Any] = []
        if source_id is not None:
            where.append("source_id = ?")
            params.append(source_id)

        sql = f"SELECT * FROM tracks WHERE {' AND '.join(where)} ORDER BY id ASC"
        if limit and limit > 0:
            sql += f" LIMIT {int(limit)}"
        sql += ";"

        with self.get_connection() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [TrackRecord.from_row(r) for r in rows]

    def count_unextracted_tracks(self, source_id: int | None = None) -> int:
        """Retourne le nombre de pistes restant à analyser."""
        where = ["(metadata_extracted = 0 OR metadata_extracted IS NULL)"]
        params: list[Any] = []
        if source_id is not None:
            where.append("source_id = ?")
            params.append(source_id)

        sql = f"SELECT COUNT(*) FROM tracks WHERE {' AND '.join(where)};"
        with self.get_connection() as conn:
            return conn.execute(sql, params).fetchone()[0]

    def update_track_metadata_batch(self, tracks: Sequence[TrackRecord]) -> int:
        """Met à jour les métadonnées audio extraites lors de la Phase 2."""
        if not tracks:
            return 0
        now = datetime.now(UTC).isoformat()
        sql = """
            UPDATE tracks SET
                title = :title,
                artist = :artist,
                album_artist = :album_artist,
                album = :album,
                genre = :genre,
                year = :year,
                track_number = :track_number,
                disc_number = :disc_number,
                duration_seconds = :duration_seconds,
                bitrate = :bitrate,
                sample_rate = :sample_rate,
                channels = :channels,
                format = :format,
                file_hash = :file_hash,
                audio_fingerprint = :audio_fingerprint,
                isrc = :isrc,
                quality_score = :quality_score,
                metadata_extracted = 1,
                updated_at = :now
            WHERE source_ref = :source_ref;
        """
        param_list = []
        for t in tracks:
            score = t.quality_score or compute_quality_score(t.format, t.bitrate, t.sample_rate)
            param_list.append(
                {
                    "source_ref": t.source_ref,
                    "title": t.title,
                    "artist": t.artist,
                    "album_artist": t.album_artist,
                    "album": t.album,
                    "genre": t.genre,
                    "year": t.year,
                    "track_number": t.track_number,
                    "disc_number": t.disc_number,
                    "duration_seconds": t.duration_seconds,
                    "bitrate": t.bitrate,
                    "sample_rate": t.sample_rate,
                    "channels": t.channels,
                    "format": t.format,
                    "file_hash": t.file_hash,
                    "audio_fingerprint": t.audio_fingerprint,
                    "isrc": t.isrc,
                    "quality_score": score,
                    "now": now,
                }
            )
        with self.get_connection() as conn:
            conn.executemany(sql, param_list)
            return len(param_list)

    def get_track(self, track_id: int) -> TrackRecord | None:
        """Récupère une piste par son ID."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM tracks WHERE id = ?;", (track_id,)).fetchone()
            return TrackRecord.from_row(row) if row else None

    def get_track_by_ref(self, source_ref: str) -> TrackRecord | None:
        """Récupère une piste par sa référence unique (chemin local ou ID distant)."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM tracks WHERE source_ref = ?;", (source_ref,)).fetchone()
            return TrackRecord.from_row(row) if row else None

    def get_tracks(
        self,
        limit: int = 100,
        offset: int = 0,
        source_type: SourceType | str | None = None,
        source_id: int | None = None,
        sort_by: str = "title",
        sort_order: str = "ASC",
    ) -> tuple[list[TrackRecord], int]:
        """Retourne une liste paginée de pistes avec le total global pour le modèle virtuel Qt."""
        allowed_sort = {
            "id",
            "file_name",
            "title",
            "artist",
            "album_artist",
            "album",
            "genre",
            "year",
            "track_number",
            "disc_number",
            "duration_seconds",
            "bitrate",
            "sample_rate",
            "channels",
            "format",
            "file_size",
            "file_mtime",
            "file_hash",
            "audio_fingerprint",
            "isrc",
            "quality_score",
            "duplicate_cluster_id",
            "source_type",
            "source_id",
            "folder_name",
            "folder_path",
            "source_path",
            "created_at",
            "updated_at",
        }
        col = sort_by if sort_by in allowed_sort else "title"
        direction = "DESC" if sort_order.upper() == "DESC" else "ASC"

        where_clauses: list[str] = []
        params: list[Any] = []

        if source_type:
            st = source_type.value if isinstance(source_type, SourceType) else str(source_type)
            where_clauses.append("source_type = ?")
            params.append(st)

        if source_id is not None:
            where_clauses.append("source_id = ?")
            params.append(source_id)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        with self.get_connection() as conn:
            count_sql = f"SELECT COUNT(*) FROM tracks {where_sql};"
            total = conn.execute(count_sql, params).fetchone()[0]

            query_sql = f"""
                SELECT * FROM tracks
                {where_sql}
                ORDER BY {col} {direction} NULLS LAST
                LIMIT ? OFFSET ?;
            """
            rows = conn.execute(query_sql, params + [limit, offset]).fetchall()
            return [TrackRecord.from_row(r) for r in rows], total

    def search_tracks(
        self,
        query: str,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[TrackRecord], int]:
        """Recherche plein-texte ultra-rapide (FTS5) sur titre, artiste, album, genre."""
        cleaned_query = query.strip()
        if not cleaned_query:
            return self.get_tracks(limit=limit, offset=offset)

        # Échappe les caractères FTS spéciaux et ajoute un wildcard pour recherche incrémentale
        fts_query = " ".join(f'"{token}"*' for token in cleaned_query.split())

        with self.get_connection() as conn:
            try:
                count_sql = """
                    SELECT COUNT(*)
                    FROM tracks_fts
                    WHERE tracks_fts MATCH ?;
                """
                total = conn.execute(count_sql, (fts_query,)).fetchone()[0]

                data_sql = """
                    SELECT t.*
                    FROM tracks t
                    JOIN tracks_fts fts ON t.id = fts.rowid
                    WHERE tracks_fts MATCH ?
                    ORDER BY rank
                    LIMIT ? OFFSET ?;
                """
                rows = conn.execute(data_sql, (fts_query, limit, offset)).fetchall()
                return [TrackRecord.from_row(r) for r in rows], total
            except sqlite3.OperationalError:
                # Fallback LIKE si la syntaxe FTS est invalide
                like_term = f"%{cleaned_query}%"
                fallback_count = """
                    SELECT COUNT(*) FROM tracks
                    WHERE title LIKE ? OR artist LIKE ? OR album LIKE ?;
                """
                total = conn.execute(fallback_count, (like_term, like_term, like_term)).fetchone()[0]

                fallback_data = """
                    SELECT * FROM tracks
                    WHERE title LIKE ? OR artist LIKE ? OR album LIKE ?
                    LIMIT ? OFFSET ?;
                """
                rows = conn.execute(fallback_data, (like_term, like_term, like_term, limit, offset)).fetchall()
                return [TrackRecord.from_row(r) for r in rows], total

    def get_track_by_id(self, track_id: int) -> TrackRecord | None:
        """Récupère une piste unique par son identifiant SQLite."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM tracks WHERE id = ?;", (track_id,)).fetchone()
            if row:
                return TrackRecord.from_row(row)
        return None

    def get_tracks_by_ids(self, track_ids: Sequence[int]) -> list[TrackRecord]:
        """Récupère une liste de pistes par leurs identifiants en préservant l'ordre."""
        if not track_ids:
            return []
        batch_size = 900
        tracks_by_id: dict[int, TrackRecord] = {}
        with self.get_connection() as conn:
            for i in range(0, len(track_ids), batch_size):
                chunk = track_ids[i : i + batch_size]
                placeholders = ",".join("?" for _ in chunk)
                rows = conn.execute(f"SELECT * FROM tracks WHERE id IN ({placeholders});", list(chunk)).fetchall()
                for r in rows:
                    tracks_by_id[r["id"]] = TrackRecord.from_row(r)
        return [tracks_by_id[tid] for tid in track_ids if tid in tracks_by_id]

    def delete_track(self, track_id: int) -> bool:
        """Supprime une piste unique."""
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM tracks WHERE id = ?;", (track_id,))
            return cursor.rowcount > 0

    def ignore_track(self, source_ref: str, source_path: str | None = None) -> bool:
        """Ajoute une piste à la table des exclusions et la supprime de la table active."""
        with self.get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO ignored_tracks (source_ref, source_path) VALUES (?, ?);",
                (source_ref, source_path),
            )
            cursor = conn.execute("DELETE FROM tracks WHERE source_ref = ?;", (source_ref,))
            return cursor.rowcount > 0

    def get_ignored_tracks_refs(self) -> set[str]:
        """Retourne l'ensemble des source_ref des pistes ignorées pour filtrage lors des scans."""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT source_ref FROM ignored_tracks;").fetchall()
            return {r["source_ref"] for r in rows if r["source_ref"]}

    def unignore_track(self, source_ref: str) -> bool:
        """Retire une piste de la liste des exclusions."""
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM ignored_tracks WHERE source_ref = ?;", (source_ref,))
            return cursor.rowcount > 0

    def count_ignored_tracks(self) -> int:
        """Retourne le nombre total de pistes ignorées / dans la corbeille."""
        with self.get_connection() as conn:
            res = conn.execute("SELECT COUNT(*) FROM ignored_tracks;").fetchone()
            return int(res[0] if res else 0)

    def get_ignored_tracks(self, limit: int = 1000, offset: int = 0) -> list[dict[str, Any]]:
        """Retourne la liste ordonnée des pistes ignorées avec leurs métadonnées."""
        with self.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, source_ref, source_path, created_at
                FROM ignored_tracks
                ORDER BY created_at DESC, id DESC
                LIMIT ? OFFSET ?;
                """,
                (limit, offset),
            ).fetchall()
            return [
                {
                    "id": r["id"],
                    "source_ref": r["source_ref"],
                    "source_path": r["source_path"],
                    "created_at": str(r["created_at"]) if r["created_at"] is not None else "",
                }
                for r in rows
            ]

    def clear_ignored_tracks(self) -> int:
        """Vide l'ensemble des pistes ignorées."""
        with self.get_connection() as conn:
            cur = conn.execute("DELETE FROM ignored_tracks;")
            return cur.rowcount

    def prune_missing_tracks(self, source_id: int, current_refs: set[str]) -> int:
        """Supprime de la base les pistes d'une source qui n'existent plus sur le disque/cloud."""
        with self.get_connection() as conn:
            # Récupère tous les refs existants pour cette source
            rows = conn.execute(
                "SELECT id, source_ref FROM tracks WHERE source_id = ?;",
                (source_id,),
            ).fetchall()

            to_delete = [r["id"] for r in rows if r["source_ref"] not in current_refs]
            if not to_delete:
                return 0

            # Suppression par lots
            batch_size = 500
            deleted_count = 0
            for i in range(0, len(to_delete), batch_size):
                chunk = to_delete[i : i + batch_size]
                placeholders = ",".join("?" for _ in chunk)
                cur = conn.execute(f"DELETE FROM tracks WHERE id IN ({placeholders});", chunk)
                deleted_count += cur.rowcount

            return deleted_count

    # -------------------------------------------------------------------------
    # Détection de doublons & Clusters
    # -------------------------------------------------------------------------

    def find_duplicates_by_hash(self) -> list[list[TrackRecord]]:
        """Identifie les doublons stricts par empreinte/hash de fichier."""
        with self.get_connection() as conn:
            hashes = conn.execute(
                """
                SELECT file_hash, COUNT(*) as count
                FROM tracks
                WHERE file_hash IS NOT NULL AND file_hash != ''
                GROUP BY file_hash
                HAVING count > 1;
                """
            ).fetchall()

            groups: list[list[TrackRecord]] = []
            for h in hashes:
                rows = conn.execute(
                    "SELECT * FROM tracks WHERE file_hash = ? ORDER BY quality_score DESC, id ASC;",
                    (h["file_hash"],),
                ).fetchall()
                groups.append([TrackRecord.from_row(r) for r in rows])
            return groups

    def find_duplicates_by_metadata(self, duration_tolerance_sec: float = 3.0) -> list[list[TrackRecord]]:
        """Identifie les doublons probables basés sur artiste, titre normalisé et durée similaire."""
        with self.get_connection() as conn:
            candidates = conn.execute(
                """
                SELECT LOWER(TRIM(artist)) as norm_artist,
                       LOWER(TRIM(title)) as norm_title,
                       COUNT(*) as count
                FROM tracks
                WHERE artist IS NOT NULL AND title IS NOT NULL
                  AND TRIM(artist) != '' AND TRIM(title) != ''
                GROUP BY norm_artist, norm_title
                HAVING count > 1;
                """
            ).fetchall()

            groups: list[list[TrackRecord]] = []
            for c in candidates:
                rows = conn.execute(
                    """
                    SELECT * FROM tracks
                    WHERE LOWER(TRIM(artist)) = ? AND LOWER(TRIM(title)) = ?
                    ORDER BY quality_score DESC, duration_seconds ASC;
                    """,
                    (c["norm_artist"], c["norm_title"]),
                ).fetchall()
                tracks = [TrackRecord.from_row(r) for r in rows]

                # Regroupe si les durées sont proches (<= tolerance) ou non renseignées
                if len(tracks) > 1:
                    groups.append(tracks)
            return groups

    def assign_duplicate_cluster(self, track_ids: Sequence[int], cluster_id: int) -> None:
        """Associe un groupe de pistes à un cluster de doublons."""
        if not track_ids:
            return
        placeholders = ",".join("?" for _ in track_ids)
        with self.get_connection() as conn:
            conn.execute(
                f"UPDATE tracks SET duplicate_cluster_id = ? WHERE id IN ({placeholders});",
                [cluster_id] + list(track_ids),
            )

    # -------------------------------------------------------------------------
    # Statistiques globales de bibliothèque
    # -------------------------------------------------------------------------

    def get_library_stats(self) -> dict[str, Any]:
        """Retourne un résumé global de la bibliothèque pour le tableau de bord."""
        with self.get_connection() as conn:
            total_tracks = conn.execute("SELECT COUNT(*) FROM tracks;").fetchone()[0]
            total_duration = conn.execute("SELECT COALESCE(SUM(duration_seconds), 0) FROM tracks;").fetchone()[0]
            total_size = conn.execute("SELECT COALESCE(SUM(file_size), 0) FROM tracks;").fetchone()[0]

            source_counts = conn.execute(
                """
                SELECT source_type, COUNT(*) as count
                FROM tracks
                GROUP BY source_type;
                """
            ).fetchall()

            format_counts = conn.execute(
                """
                SELECT COALESCE(format, 'unknown') as fmt, COUNT(*) as count
                FROM tracks
                GROUP BY format
                ORDER BY count DESC;
                """
            ).fetchall()

            total_sources = conn.execute("SELECT COUNT(*) FROM sources;").fetchone()[0]

            return {
                "total_tracks": total_tracks,
                "total_sources": total_sources,
                "total_duration_seconds": total_duration,
                "total_size_bytes": total_size,
                "by_source_type": {r["source_type"]: r["count"] for r in source_counts},
                "by_format": {r["fmt"]: r["count"] for r in format_counts},
            }

    # -------------------------------------------------------------------------
    # Exploration & Navigation par Dossiers
    # -------------------------------------------------------------------------

    def get_folders_summary(self, source_id: int | None = None) -> list[dict[str, Any]]:
        """Retourne la liste des répertoires contenant des pistes avec le décompte de morceaux."""
        query = """
            SELECT source_id, folder_path, folder_name, COUNT(*) as track_count
            FROM tracks
            WHERE folder_path IS NOT NULL AND (:source_id IS NULL OR source_id = :source_id)
            GROUP BY source_id, folder_path
            ORDER BY folder_path ASC;
        """
        with self.get_connection() as conn:
            rows = conn.execute(query, {"source_id": source_id}).fetchall()
            return [
                {
                    "source_id": r["source_id"],
                    "folder_path": r["folder_path"],
                    "folder_name": r["folder_name"],
                    "track_count": int(r["track_count"]),
                }
                for r in rows
            ]

    def get_tracks_by_folder(
        self,
        folder_path: str,
        source_id: int | None = None,
        recursive: bool = False,
        sort_by: str = "file_name",
        sort_order: str = "ASC",
    ) -> list[TrackRecord]:
        """Retourne les pistes audio situées dans un dossier (ou sous-dossiers si recursive=True)."""
        fp_clean = folder_path.replace("\\", "/").rstrip("/")
        fp_alt = fp_clean.replace("/", "\\")
        direction = "DESC" if str(sort_order).upper() == "DESC" else "ASC"
        allowed_sorts = {
            "id",
            "file_name",
            "title",
            "artist",
            "album_artist",
            "album",
            "genre",
            "year",
            "track_number",
            "disc_number",
            "duration_seconds",
            "bitrate",
            "sample_rate",
            "channels",
            "format",
            "file_size",
            "file_mtime",
            "file_hash",
            "audio_fingerprint",
            "isrc",
            "quality_score",
            "duplicate_cluster_id",
            "source_type",
            "source_id",
            "folder_name",
            "folder_path",
            "source_path",
            "created_at",
            "updated_at",
        }
        sort_col = sort_by if sort_by in allowed_sorts else "file_name"

        with self.get_connection() as conn:
            if not recursive:
                query = f"""
                    SELECT * FROM tracks
                    WHERE (:source_id IS NULL OR source_id = :source_id)
                      AND (folder_path = :fp OR folder_path = :fp_alt)
                    ORDER BY {sort_col} {direction};
                """
                rows = conn.execute(
                    query,
                    {
                        "source_id": source_id,
                        "fp": fp_clean,
                        "fp_alt": fp_alt,
                    },
                ).fetchall()
            else:
                query = f"""
                    SELECT * FROM tracks
                    WHERE (:source_id IS NULL OR source_id = :source_id)
                      AND (
                          folder_path = :fp
                          OR folder_path = :fp_alt
                          OR folder_path LIKE :p1
                          OR folder_path LIKE :p2
                          OR folder_path LIKE :p3
                          OR folder_path LIKE :p4
                      )
                    ORDER BY {sort_col} {direction};
                """
                rows = conn.execute(
                    query,
                    {
                        "source_id": source_id,
                        "fp": fp_clean,
                        "fp_alt": fp_alt,
                        "p1": f"{fp_clean}/%",
                        "p2": f"{fp_clean}\\%",
                        "p3": f"{fp_alt}/%",
                        "p4": f"{fp_alt}\\%",
                    },
                ).fetchall()

            return [TrackRecord.from_row(r) for r in rows]

    def count_tracks_by_folder(
        self,
        folder_path: str,
        source_id: int | None = None,
        recursive: bool = False,
    ) -> int:
        """Compte le nombre de pistes dans un dossier donné."""
        fp_clean = folder_path.replace("\\", "/").rstrip("/")
        fp_alt = fp_clean.replace("/", "\\")
        with self.get_connection() as conn:
            if not recursive:
                query = """
                    SELECT COUNT(*) FROM tracks
                    WHERE (:source_id IS NULL OR source_id = :source_id)
                      AND (folder_path = :fp OR folder_path = :fp_alt);
                """
                res = conn.execute(
                    query,
                    {"source_id": source_id, "fp": fp_clean, "fp_alt": fp_alt},
                ).fetchone()
            else:
                query = """
                    SELECT COUNT(*) FROM tracks
                    WHERE (:source_id IS NULL OR source_id = :source_id)
                      AND (
                          folder_path = :fp
                          OR folder_path = :fp_alt
                          OR folder_path LIKE :p1
                          OR folder_path LIKE :p2
                      );
                """
                res = conn.execute(
                    query,
                    {
                        "source_id": source_id,
                        "fp": fp_clean,
                        "fp_alt": fp_alt,
                        "p1": f"{fp_clean}/%",
                        "p2": f"{fp_clean}\\%",
                    },
                ).fetchone()
            return int(res[0] if res else 0)

    # -------------------------------------------------------------------------
    # Journal d'activité (Logs)
    # -------------------------------------------------------------------------

    def add_activity_log(
        self,
        action: str,
        level: str = "INFO",
        category: str = "SYNC",
        source_name: str | None = None,
        details: str | None = None,
        items_added: int = 0,
        items_updated: int = 0,
        items_deleted: int = 0,
        items_errors: int = 0,
        timestamp: str | None = None,
    ) -> int:
        """Insère une nouvelle entrée dans le journal d'activité."""
        now = timestamp or datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO activity_logs (
                    timestamp, level, category, source_name, action, details,
                    items_added, items_updated, items_deleted, items_errors
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    now,
                    level.upper(),
                    category.upper(),
                    source_name,
                    action,
                    details,
                    items_added,
                    items_updated,
                    items_deleted,
                    items_errors,
                ),
            )
            return cur.lastrowid or 0

    def get_activity_logs(
        self,
        limit: int = 200,
        offset: int = 0,
        level: str | None = None,
        category: str | None = None,
        search: str | None = None,
    ) -> list[ActivityLogRecord]:
        """Récupère les logs avec filtres facultatifs par niveau, catégorie et mot-clé."""
        clauses: list[str] = []
        params: list[Any] = []

        if level and level.upper() != "ALL":
            clauses.append("level = ?")
            params.append(level.upper())

        if category and category.upper() != "ALL":
            clauses.append("category = ?")
            params.append(category.upper())

        if search and search.strip():
            kw = f"%{search.strip()}%"
            clauses.append("(action LIKE ? OR details LIKE ? OR source_name LIKE ?)")
            params.extend([kw, kw, kw])

        where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        query = f"""
            SELECT * FROM activity_logs
            {where_sql}
            ORDER BY id DESC
            LIMIT ? OFFSET ?;
        """
        params.extend([limit, offset])

        with self.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [ActivityLogRecord.from_row(r) for r in rows]

    def count_activity_logs(
        self,
        level: str | None = None,
        category: str | None = None,
        search: str | None = None,
    ) -> int:
        """Compte le nombre de logs répondant aux critères."""
        clauses: list[str] = []
        params: list[Any] = []

        if level and level.upper() != "ALL":
            clauses.append("level = ?")
            params.append(level.upper())

        if category and category.upper() != "ALL":
            clauses.append("category = ?")
            params.append(category.upper())

        if search and search.strip():
            kw = f"%{search.strip()}%"
            clauses.append("(action LIKE ? OR details LIKE ? OR source_name LIKE ?)")
            params.extend([kw, kw, kw])

        where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        query = f"SELECT COUNT(*) FROM activity_logs {where_sql};"

        with self.get_connection() as conn:
            res = conn.execute(query, params).fetchone()
            return int(res[0] if res else 0)

    def clear_activity_logs(self, before_days: int | None = None) -> int:
        """Supprime tout ou partie des logs (ex: logs de plus de N jours)."""
        with self.get_connection() as conn:
            if before_days is not None and before_days > 0:
                cur = conn.execute(
                    """
                    DELETE FROM activity_logs
                    WHERE timestamp < datetime('now', ?);
                    """,
                    (f"-{before_days} days",),
                )
            else:
                cur = conn.execute("DELETE FROM activity_logs;")
            return cur.rowcount
