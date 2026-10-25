"""Playlists et liaison des entrées aux pistes."""

from __future__ import annotations

import contextlib
import logging
import os
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING, Any

from amso.core.db.models import (
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

    def get_playlist_tracks(self, playlist_id: int) -> list[TrackRecord]:
        """Retourne la liste ordonnée des pistes composant une playlist."""
        with self.get_connection() as conn:
            query = """
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
                WHERE pe.playlist_id = ?
                ORDER BY pe.position ASC;
            """
            rows = conn.execute(query, (playlist_id,)).fetchall()
            tracks: list[TrackRecord] = []
            for r in rows:
                is_missing = bool(r["pe_is_missing"])
                resolved = r["pe_resolved_path"]
                if not is_missing and resolved and not os.path.exists(resolved):
                    is_missing = True

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
            cur = conn.execute(
                """
                UPDATE playlist_entries
                SET track_id = (
                    SELECT t.id FROM tracks t
                    WHERE t.source_path = playlist_entries.resolved_path
                       OR t.source_ref = playlist_entries.resolved_path
                    LIMIT 1
                )
                WHERE track_id IS NULL;
                """
            )
            return cur.rowcount
