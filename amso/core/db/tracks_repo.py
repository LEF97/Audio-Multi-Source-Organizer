"""Requêtes sur les pistes (écriture par lot, lecture, recherche, purge)."""

from __future__ import annotations

import contextlib
import logging
import sqlite3
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from amso.core.db.models import (
    SourceType,
    TrackRecord,
    compute_quality_score,
)

logger = logging.getLogger(__name__)


class TracksRepoMixin:
    """Requêtes sur les pistes (écriture par lot, lecture, recherche, purge)."""

    if TYPE_CHECKING:
        # Fournis par DatabaseManager (typage uniquement)
        def get_connection(self) -> contextlib.AbstractContextManager[sqlite3.Connection]: ...

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
