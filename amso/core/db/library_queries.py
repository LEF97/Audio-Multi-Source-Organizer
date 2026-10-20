"""Statistiques de bibliothèque et vues par dossier."""

from __future__ import annotations

import contextlib
import logging
import sqlite3
from typing import TYPE_CHECKING, Any

from amso.core.db.models import (
    TrackRecord,
)

logger = logging.getLogger(__name__)


class LibraryQueriesMixin:
    """Statistiques de bibliothèque et vues par dossier."""

    if TYPE_CHECKING:
        # Fournis par DatabaseManager (typage uniquement)
        def get_connection(self) -> contextlib.AbstractContextManager[sqlite3.Connection]: ...

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
