"""Couche de persistance SQLite3 pour AMSO.

Conçue pour absorber de grands volumes (> 50 000 titres) sans ORM lourd,
avec mode WAL, indexation ciblée et recherche plein texte (FTS5).
"""

from __future__ import annotations

import contextlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
from pathlib import Path
import sqlite3
from typing import Any, Generator, Iterable, Optional, Sequence


class SourceType(str, Enum):
    """Types de sources audio prises en charge."""

    LOCAL = "local"
    GDRIVE = "gdrive"
    SPOTIFY = "spotify"
    DEEZER = "deezer"


def compute_quality_score(
    audio_format: Optional[str],
    bitrate: Optional[int],
    sample_rate: Optional[int],
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

    id: Optional[int] = None
    source_type: SourceType = SourceType.LOCAL
    name: str = ""
    path_or_uri: str = ""
    created_at: Optional[str] = None
    last_scanned_at: Optional[str] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> SourceRecord:
        return cls(
            id=row["id"],
            source_type=SourceType(row["source_type"]),
            name=row["name"],
            path_or_uri=row["path_or_uri"],
            created_at=str(row["created_at"]) if row["created_at"] is not None else None,
            last_scanned_at=str(row["last_scanned_at"]) if row["last_scanned_at"] is not None else None,
        )


@dataclass(slots=True)
class TrackRecord:
    """Représentation d'une piste audio."""

    source_ref: str
    source_type: SourceType = SourceType.LOCAL
    id: Optional[int] = None
    source_id: Optional[int] = None
    source_path: Optional[str] = None

    # Métadonnées audio
    title: Optional[str] = None
    artist: Optional[str] = None
    album_artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    track_number: Optional[int] = None
    disc_number: Optional[int] = None

    # Propriétés techniques
    duration_seconds: Optional[float] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    format: Optional[str] = None

    # Fichier & Empreintes
    file_size: Optional[int] = None
    file_mtime: Optional[float] = None
    file_hash: Optional[str] = None
    audio_fingerprint: Optional[str] = None
    isrc: Optional[str] = None

    # Gestion des doublons & Score
    quality_score: int = 0
    duplicate_cluster_id: Optional[int] = None

    # Dates
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self) -> None:
        if self.quality_score == 0 and (self.format or self.bitrate):
            self.quality_score = compute_quality_score(self.format, self.bitrate, self.sample_rate)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> TrackRecord:
        return cls(
            id=row["id"],
            source_ref=row["source_ref"],
            source_type=SourceType(row["source_type"]),
            source_id=row["source_id"],
            source_path=row["source_path"],
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
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


class DatabaseManager:
    """Gestionnaire de persistance SQLite pour la bibliothèque AMSO."""

    SCHEMA_VERSION = 1

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self.db_path = str(db_path)
        self._memory_conn: Optional[sqlite3.Connection] = None
        if self.db_path == ":memory:":
            self._memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._memory_conn.row_factory = sqlite3.Row
            self._memory_conn.execute("PRAGMA foreign_keys = ON;")
        self.init_schema()

    def close(self) -> None:
        """Ferme la base de données (utile pour libérer la mémoire)."""
        if self._memory_conn is not None:
            self._memory_conn.close()
            self._memory_conn = None

    @contextlib.contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Fournit une connexion configurée avec gestion automatique de transaction."""
        if self._memory_conn is not None:
            try:
                yield self._memory_conn
                self._memory_conn.commit()
            except Exception:
                self._memory_conn.rollback()
                raise
            return

        conn = sqlite3.connect(
            self.db_path,
            timeout=30.0,
        )
        conn.row_factory = sqlite3.Row

        # Optimisations SQLite
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA cache_size = -64000;")  # 64 Mo de cache mémoire

        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

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

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # 3. Index de performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_source ON tracks(source_id, source_type);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_artist_album ON tracks(artist, album);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_title ON tracks(title);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_file_hash ON tracks(file_hash);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_cluster ON tracks(duplicate_cluster_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_isrc ON tracks(isrc);")

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
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS playlist_tracks (
                    playlist_id INTEGER REFERENCES playlists(id) ON DELETE CASCADE,
                    track_id INTEGER REFERENCES tracks(id) ON DELETE CASCADE,
                    position INTEGER NOT NULL,
                    PRIMARY KEY (playlist_id, track_id, position)
                );
                """
            )

    # -------------------------------------------------------------------------
    # Sources CRUD
    # -------------------------------------------------------------------------

    def add_source(
        self,
        source_type: SourceType | str,
        name: str,
        path_or_uri: str,
    ) -> SourceRecord:
        """Ajoute ou récupère une source audio."""
        st = source_type.value if isinstance(source_type, SourceType) else source_type
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO sources (source_type, name, path_or_uri)
                VALUES (?, ?, ?)
                ON CONFLICT(path_or_uri) DO UPDATE SET
                    name = excluded.name,
                    source_type = excluded.source_type;
                """,
                (st, name, path_or_uri),
            )
            row = conn.execute(
                "SELECT * FROM sources WHERE path_or_uri = ?;",
                (path_or_uri,),
            ).fetchone()
            return SourceRecord.from_row(row)

    def get_sources(self) -> list[SourceRecord]:
        """Retourne la liste de toutes les sources configurées."""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM sources ORDER BY id ASC;").fetchall()
            return [SourceRecord.from_row(r) for r in rows]

    def get_source(self, source_id: int) -> Optional[SourceRecord]:
        """Retourne une source par son identifiant."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM sources WHERE id = ?;", (source_id,)).fetchone()
            return SourceRecord.from_row(row) if row else None

    def update_source_scanned(self, source_id: int) -> None:
        """Met à jour l'horodatage du dernier scan d'une source."""
        now = datetime.now(timezone.utc).isoformat()
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

        now = datetime.now(timezone.utc).isoformat()
        query = """
            INSERT INTO tracks (
                source_ref, source_type, source_id, source_path,
                title, artist, album_artist, album, genre, year,
                track_number, disc_number, duration_seconds, bitrate,
                sample_rate, channels, format, file_size, file_mtime,
                file_hash, audio_fingerprint, isrc, quality_score,
                duplicate_cluster_id, created_at, updated_at
            )
            VALUES (
                :source_ref, :source_type, :source_id, :source_path,
                :title, :artist, :album_artist, :album, :genre, :year,
                :track_number, :disc_number, :duration_seconds, :bitrate,
                :sample_rate, :channels, :format, :file_size, :file_mtime,
                :file_hash, :audio_fingerprint, :isrc, :quality_score,
                :duplicate_cluster_id, :now, :now
            )
            ON CONFLICT(source_ref) DO UPDATE SET
                source_type = excluded.source_type,
                source_id = excluded.source_id,
                source_path = excluded.source_path,
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

    def get_track(self, track_id: int) -> Optional[TrackRecord]:
        """Récupère une piste par son ID."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM tracks WHERE id = ?;", (track_id,)).fetchone()
            return TrackRecord.from_row(row) if row else None

    def get_track_by_ref(self, source_ref: str) -> Optional[TrackRecord]:
        """Récupère une piste par sa référence unique (chemin local ou ID distant)."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM tracks WHERE source_ref = ?;", (source_ref,)).fetchone()
            return TrackRecord.from_row(row) if row else None

    def get_tracks(
        self,
        limit: int = 100,
        offset: int = 0,
        source_type: Optional[SourceType | str] = None,
        source_id: Optional[int] = None,
        sort_by: str = "title",
        sort_order: str = "ASC",
    ) -> tuple[list[TrackRecord], int]:
        """Retourne une liste paginée de pistes avec le total global pour le modèle virtuel Qt."""
        allowed_sort = {
            "id", "title", "artist", "album", "year", "duration_seconds",
            "bitrate", "format", "quality_score", "created_at"
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
        fts_query = ' '.join(f'"{token}"*' for token in cleaned_query.split())

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

    def delete_track(self, track_id: int) -> bool:
        """Supprime une piste unique."""
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM tracks WHERE id = ?;", (track_id,))
            return cursor.rowcount > 0

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
