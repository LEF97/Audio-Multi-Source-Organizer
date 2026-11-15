"""Playlists et liaison des entrées aux pistes."""

from __future__ import annotations

import contextlib
import logging
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING, Any

from amso.core.db.models import (
    PlaylistEntryRecord,
    PlaylistRecord,
    TrackRecord,
)

logger = logging.getLogger(__name__)


def _apply_cue_segment(rec: TrackRecord, row: Any) -> None:
    """Transforme `rec` en piste virtuelle CUE (début/fin, titre, artiste, durée de la portion) si l'entrée en est une."""
    start = row["pe_start_ms"]
    if start is None:
        return
    start_ms = int(start)
    end_ms = int(row["pe_end_ms"]) if row["pe_end_ms"] is not None else None
    file_ms = int((rec.duration_seconds or 0) * 1000)  # durée du fichier entier (piste indexée)
    if end_ms is None and file_ms > start_ms:
        end_ms = file_ms  # dernière piste : jusqu'à la fin du fichier
    if row["pe_title"]:
        rec.title = row["pe_title"]
    if row["pe_artist"]:
        rec.artist = row["pe_artist"]
    rec.cue_start_ms = start_ms
    rec.cue_end_ms = end_ms
    rec.duration_seconds = (end_ms - start_ms) / 1000.0 if end_ms is not None else None


class PlaylistsRepoMixin:
    """Playlists et liaison des entrées aux pistes."""

    if TYPE_CHECKING:
        # Fournis par DatabaseManager (typage uniquement)
        def get_connection(self) -> contextlib.AbstractContextManager[sqlite3.Connection]: ...

    def upsert_playlist(
        self,
        source_id: int,
        file_path: str,
        file_name: str,
        folder_path: str,
        format_str: str,
        file_mtime: float,
        file_size: int,
        entries: list[Any],
        source_type: str = "local",
    ) -> int:
        """Insère ou met à jour une playlist et ses entrées ordonnées associées."""
        clean_fp = file_path.replace("\\", "/")
        clean_folder = folder_path.replace("\\", "/")
        track_cnt = len(entries)

        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO playlists (
                    source_id, name, file_path, folder_path, format,
                    track_count, file_mtime, file_size, source_type, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ON CONFLICT(file_path) DO UPDATE SET
                    source_id = excluded.source_id,
                    name = excluded.name,
                    folder_path = excluded.folder_path,
                    format = excluded.format,
                    track_count = excluded.track_count,
                    file_mtime = excluded.file_mtime,
                    file_size = excluded.file_size,
                    source_type = excluded.source_type,
                    updated_at = datetime('now');
                """,
                (
                    source_id,
                    file_name,
                    clean_fp,
                    clean_folder,
                    format_str.lower(),
                    track_cnt,
                    file_mtime,
                    file_size,
                    source_type,
                ),
            )
            row = conn.execute("SELECT id FROM playlists WHERE file_path = ?;", (clean_fp,)).fetchone()
            if not row:
                return 0
            playlist_id = int(row["id"])

            # Supprimer les anciennes entrées associées
            conn.execute("DELETE FROM playlist_entries WHERE playlist_id = ?;", (playlist_id,))

            entries_to_insert = []
            for e in entries:
                raw_p = getattr(e, "raw_path", "") or ""
                resolved_p = getattr(e, "resolved_path", "") or raw_p or ""
                pos = getattr(e, "position", 1)
                title = getattr(e, "title", None)
                artist = getattr(e, "artist", None)
                dur = getattr(e, "duration_seconds", None)
                is_missing = 1 if getattr(e, "is_missing", False) else 0
                start_ms = getattr(e, "start_ms", None)
                end_ms = getattr(e, "end_ms", None)

                # Recherche automatique du track_id correspondant dans la base tracks
                t_row = conn.execute(
                    "SELECT id FROM tracks WHERE source_path = ? OR source_ref = ? LIMIT 1;",
                    (resolved_p, resolved_p),
                ).fetchone()
                t_id = t_row["id"] if t_row else None

                entries_to_insert.append(
                    (playlist_id, pos, raw_p, resolved_p, t_id, title, artist, dur, is_missing, start_ms, end_ms)
                )

            if entries_to_insert:
                conn.executemany(
                    """
                    INSERT INTO playlist_entries (
                        playlist_id, position, raw_path, resolved_path,
                        track_id, title, artist, duration_seconds, is_missing, start_ms, end_ms
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    entries_to_insert,
                )

            return playlist_id

    def get_playlists(self, source_id: int | None = None) -> list[PlaylistRecord]:
        """Retourne la liste des playlists indexées ordonnées par dossier et nom."""
        query = """
            SELECT * FROM playlists
            WHERE (:source_id IS NULL OR source_id = :source_id)
            ORDER BY folder_path ASC, name ASC;
        """
        with self.get_connection() as conn:
            rows = conn.execute(query, {"source_id": source_id}).fetchall()
            return [PlaylistRecord.from_row(r) for r in rows]

    def get_playlist(self, playlist_id: int) -> PlaylistRecord | None:
        """Retourne une playlist spécifique par son ID."""
        with self.get_connection() as conn:
            r = conn.execute("SELECT * FROM playlists WHERE id = ?;", (playlist_id,)).fetchone()
            return PlaylistRecord.from_row(r) if r else None

    def get_playlist_by_path(self, file_path: str) -> PlaylistRecord | None:
        """Retourne une playlist par son chemin absolu."""
        clean_fp = file_path.replace("\\", "/")
        with self.get_connection() as conn:
            r = conn.execute("SELECT * FROM playlists WHERE file_path = ?;", (clean_fp,)).fetchone()
            return PlaylistRecord.from_row(r) if r else None

    def get_playlist_entries(self, playlist_id: int) -> list[PlaylistEntryRecord]:
        """Retourne toutes les entrées brutes d'une playlist (y compris les pistes introuvables)."""
        with self.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    pe.*,
                    COALESCE(pe.duration_seconds, t.duration_seconds) AS eff_duration,
                    COALESCE(pe.title, t.title) AS eff_title,
                    COALESCE(pe.artist, t.artist) AS eff_artist
                FROM playlist_entries pe
                LEFT JOIN tracks t ON t.id = pe.track_id
                WHERE pe.playlist_id = ?
                ORDER BY pe.position ASC;
                """,
                (playlist_id,),
            ).fetchall()
            entries: list[PlaylistEntryRecord] = []
            for r in rows:
                rec = PlaylistEntryRecord.from_row(r)
                if rec.duration_seconds is None and r["eff_duration"] is not None:
                    rec.duration_seconds = float(r["eff_duration"])
                if not rec.title and r["eff_title"]:
                    rec.title = str(r["eff_title"])
                if not rec.artist and r["eff_artist"]:
                    rec.artist = str(r["eff_artist"])
                entries.append(rec)
            return entries

    def delete_playlist(self, playlist_id: int) -> None:
        """Supprime une playlist et toutes ses entrées."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM playlists WHERE id = ?;", (playlist_id,))

    def delete_playlist_by_path(self, file_path: str) -> None:
        """Supprime une playlist par son chemin de fichier."""
        clean_fp = file_path.replace("\\", "/")
        with self.get_connection() as conn:
            conn.execute("DELETE FROM playlists WHERE file_path = ?;", (clean_fp,))

    def delete_playlists_not_in(self, source_id: int, current_file_paths: set[str]) -> int:
        """Supprime les playlists d'une source qui n'existent plus sur le disque."""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT id, file_path FROM playlists WHERE source_id = ? AND file_path IS NOT NULL AND file_path != '';",
                (source_id,),
            ).fetchall()
            to_delete = [r["id"] for r in rows if r["file_path"] not in current_file_paths]
            if to_delete:
                placeholders = ",".join(["?"] * len(to_delete))
                conn.execute(f"DELETE FROM playlists WHERE id IN ({placeholders});", to_delete)
            return len(to_delete)

    def get_playlist_album_groups(self, playlist_id: int) -> list[tuple[str, int]]:
        """Retourne les albums (nom brut ou '' si inconnu) et le nombre de titres dans une playlist."""
        with self.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    COALESCE(NULLIF(TRIM(t.album), ''), '') AS album_name,
                    COUNT(*) AS cnt
                FROM playlist_entries pe
                LEFT JOIN tracks t ON pe.track_id = t.id
                WHERE pe.playlist_id = ?
                GROUP BY album_name
                ORDER BY MIN(pe.position) ASC;
                """,
                (playlist_id,),
            ).fetchall()
            return [(str(r["album_name"]), int(r["cnt"])) for r in rows]

    def get_playlist_tracks(self, playlist_id: int, album: str | None = None) -> list[TrackRecord]:
        """Retourne la liste ordonnée des pistes composant une playlist (filtrée par album si fourni)."""
        with self.get_connection() as conn:
            album_clause = ""
            params: list[Any] = [playlist_id]
            if album is not None:
                if album == "":
                    album_clause = " AND (t.album IS NULL OR TRIM(t.album) = '')"
                else:
                    album_clause = " AND t.album = ?"
                    params.append(album)

            query = f"""
                SELECT
                    pe.position as pe_position,
                    pe.raw_path as pe_raw_path,
                    pe.resolved_path as pe_resolved_path,
                    pe.title as pe_title,
                    pe.artist as pe_artist,
                    pe.duration_seconds as pe_duration,
                    pe.is_missing as pe_is_missing,
                    pe.start_ms as pe_start_ms,
                    pe.end_ms as pe_end_ms,
                    t.*
                FROM playlist_entries pe
                LEFT JOIN tracks t ON pe.track_id = t.id
                WHERE pe.playlist_id = ?{album_clause}
                ORDER BY pe.position ASC;
            """
            rows = conn.execute(query, params).fetchall()
            tracks: list[TrackRecord] = []
            for r in rows:
                is_missing = bool(r["pe_is_missing"])
                resolved = r["pe_resolved_path"]

                pos = int(r["pe_position"])

                if r["id"] is not None:
                    # Morceau présent dans la table tracks : on récupère ses métadonnées riches
                    rec = TrackRecord.from_row(r)
                    rec.track_number = pos
                    rec.is_missing = is_missing
                    _apply_cue_segment(rec, r)
                    tracks.append(rec)
                else:
                    # Morceau non indexé dans tracks ou fichier manquant/externe
                    fn = Path(resolved).name if resolved else (r["pe_title"] or "Titre inconnu")
                    tit = r["pe_title"] or (Path(resolved).stem if resolved else "Titre inconnu")
                    fmt = Path(resolved).suffix.lstrip(".").lower() if resolved else "audio"
                    rec = TrackRecord(
                        source_ref=resolved or r["pe_raw_path"],
                        source_path=resolved or r["pe_raw_path"],
                        file_name=fn,
                        title=tit,
                        artist=r["pe_artist"] or "",
                        duration_seconds=r["pe_duration"],
                        track_number=pos,
                        format=fmt,
                        is_missing=is_missing,
                    )
                    _apply_cue_segment(rec, r)
                    tracks.append(rec)
            return tracks

    def link_playlist_entries_to_tracks(self, source_id: int | None = None) -> int:
        """Associe les entrées de playlist orphelines aux pistes nouvellement indexées."""
        with self.get_connection() as conn:
            # Deux sous-requêtes indexées (source_ref UNIQUE, idx_tracks_source_path) plutôt qu'un OR
            # qui force un scan complet de `tracks` pour chaque entrée orpheline.
            cur = conn.execute(
                """
                UPDATE playlist_entries
                SET track_id = COALESCE(
                    (
                        SELECT t.id FROM tracks t
                        WHERE t.source_ref = playlist_entries.resolved_path
                        LIMIT 1
                    ),
                    (
                        SELECT t.id FROM tracks t
                        WHERE t.source_path = playlist_entries.resolved_path
                        LIMIT 1
                    )
                )
                WHERE track_id IS NULL;
                """
            )
            return cur.rowcount

    def find_matching_playlist_id(
        self,
        current_track: TrackRecord,
        playlist_tracks: list[TrackRecord],
    ) -> int | None:
        """Identifie la playlist indexée (CUE, M3U, PLS, XSPF, WPL) correspondant à la lecture en cours."""
        with self.get_connection() as conn:
            if current_track.is_cue_segment or any(t.is_cue_segment for t in playlist_tracks):
                return self._find_cue_playlist_id(conn, current_track)
            return self._find_standard_playlist_id(conn, current_track, playlist_tracks)

    def _find_cue_playlist_id(self, conn: sqlite3.Connection, track: TrackRecord) -> int | None:
        norm_path = (track.source_path or track.source_ref or "").replace("\\", "/").lower()
        rows = conn.execute(
            """
            SELECT p.id, pe.start_ms
            FROM playlists p
            JOIN playlist_entries pe ON pe.playlist_id = p.id
            WHERE LOWER(p.format) = 'cue'
              AND (
                (pe.track_id IS NOT NULL AND pe.track_id = :track_id)
                OR LOWER(REPLACE(pe.resolved_path, '\\', '/')) = :norm_path
              );
            """,
            {"track_id": track.id, "norm_path": norm_path},
        ).fetchall()
        if rows:
            for r in rows:
                if track.cue_start_ms is not None and r["start_ms"] == track.cue_start_ms:
                    return int(r["id"])
            return int(rows[0]["id"])

        norm_folder = (track.folder_path or "").replace("\\", "/").rstrip("/").lower()
        if norm_folder:
            row = conn.execute(
                """
                SELECT id FROM playlists
                WHERE LOWER(format) = 'cue'
                  AND LOWER(RTRIM(REPLACE(folder_path, '\\', '/'), '/')) = :norm_folder
                LIMIT 1;
                """,
                {"norm_folder": norm_folder},
            ).fetchone()
            if row:
                return int(row["id"])
        return None

    def _find_standard_playlist_id(
        self,
        conn: sqlite3.Connection,
        current_track: TrackRecord,
        playlist_tracks: list[TrackRecord],
    ) -> int | None:
        if not playlist_tracks:
            return None
        norm_cur = (current_track.source_path or current_track.source_ref or "").replace("\\", "/").lower()
        cand_rows = conn.execute(
            """
            SELECT DISTINCT p.id
            FROM playlists p
            JOIN playlist_entries pe ON pe.playlist_id = p.id
            WHERE LOWER(p.format) != 'cue'
              AND (
                (pe.track_id IS NOT NULL AND pe.track_id = :track_id)
                OR LOWER(REPLACE(pe.resolved_path, '\\', '/')) = :norm_path
              );
            """,
            {"track_id": current_track.id, "norm_path": norm_cur},
        ).fetchall()
        if not cand_rows:
            return None

        target_paths = [(t.source_path or t.source_ref or "").replace("\\", "/").lower() for t in playlist_tracks]
        target_counter: dict[str, int] = {}
        for p in target_paths:
            target_counter[p] = target_counter.get(p, 0) + 1

        for cand in cand_rows:
            pl_id = int(cand["id"])
            entries = conn.execute(
                """
                SELECT pe.resolved_path, t.source_path
                FROM playlist_entries pe
                LEFT JOIN tracks t ON pe.track_id = t.id
                WHERE pe.playlist_id = ?
                ORDER BY pe.position ASC;
                """,
                (pl_id,),
            ).fetchall()
            if len(entries) != len(playlist_tracks):
                continue
            entry_paths = [(r["source_path"] or r["resolved_path"] or "").replace("\\", "/").lower() for r in entries]
            if entry_paths == target_paths:
                return pl_id
            entry_counter: dict[str, int] = {}
            for p in entry_paths:
                entry_counter[p] = entry_counter.get(p, 0) + 1
            if entry_counter == target_counter:
                return pl_id
        return None
