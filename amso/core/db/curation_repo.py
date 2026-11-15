"""Pistes ignorées et détection des doublons."""

from __future__ import annotations

import contextlib
import logging
import sqlite3
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from amso.core.db.models import (
    TrackRecord,
)

logger = logging.getLogger(__name__)


class TrackCurationMixin:
    """Pistes ignorées et détection des doublons."""

    if TYPE_CHECKING:
        # Fournis par DatabaseManager (typage uniquement)
        def get_connection(self) -> contextlib.AbstractContextManager[sqlite3.Connection]: ...

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

    @staticmethod
    def find_duplicates_in_tracks(
        tracks: Sequence[TrackRecord],
        duration_tolerance_sec: float = 3.0,
    ) -> tuple[list[list[TrackRecord]], list[list[TrackRecord]], list[TrackRecord]]:
        """Identifie les doublons stricts (hash) et probables (métadonnées) au sein d'une séquence de pistes."""
        by_hash: dict[str, list[tuple[int, TrackRecord]]] = {}
        by_meta: dict[tuple[str, str], list[tuple[int, TrackRecord]]] = {}

        for idx, track in enumerate(tracks):
            if track.file_hash:
                by_hash.setdefault(track.file_hash, []).append((idx, track))
            artist_norm = (track.artist or "").strip().lower()
            title_norm = (track.title or "").strip().lower()
            if artist_norm and title_norm:
                by_meta.setdefault((artist_norm, title_norm), []).append((idx, track))

        hash_groups = [[t for _, t in grp] for grp in by_hash.values() if len(grp) > 1]
        meta_groups: list[list[TrackRecord]] = []
        seen_indices: set[int] = {idx for grp in by_hash.values() if len(grp) > 1 for idx, _ in grp}

        for grp in by_meta.values():
            if len(grp) < 2:
                continue
            durations = [t.duration_seconds for _, t in grp if t.duration_seconds and t.duration_seconds > 0]
            if len(durations) >= 2 and (max(durations) - min(durations)) > duration_tolerance_sec:
                continue
            meta_groups.append([t for _, t in grp])
            for idx, _ in grp:
                seen_indices.add(idx)

        unique_tracks = [tracks[idx] for idx in sorted(seen_indices)]
        return hash_groups, meta_groups, unique_tracks

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
