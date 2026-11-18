"""Requêtes sur les sources (dossiers locaux, Drive, ...)."""

from __future__ import annotations

import contextlib
import logging
import sqlite3
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from amso.core.db.models import (
    FormatBreakdown,
    PlaylistSummaryRecord,
    SourceLibrarySummary,
    SourceRecord,
    SourceType,
)

logger = logging.getLogger(__name__)


class SourcesRepoMixin:
    """Requêtes sur les sources (dossiers locaux, Drive, ...)."""

    if TYPE_CHECKING:
        # Fournis par DatabaseManager (typage uniquement)
        def get_connection(self) -> contextlib.AbstractContextManager[sqlite3.Connection]: ...

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

    def get_sources_library_summary(self) -> list[SourceLibrarySummary]:
        """Retourne le résumé agrégé (pistes, playlists, durée, erreurs) pour chaque source."""
        with self.get_connection() as conn:
            source_rows = conn.execute("SELECT * FROM sources ORDER BY id ASC;").fetchall()
            sources = [SourceRecord.from_row(r) for r in source_rows]

            track_rows = conn.execute(
                """
                SELECT
                    source_id,
                    COUNT(*) AS cnt,
                    COALESCE(SUM(duration_seconds), 0.0) AS dur,
                    COALESCE(SUM(file_size), 0) AS sz
                FROM tracks
                GROUP BY source_id;
                """
            ).fetchall()
            track_stats: dict[int, tuple[int, float, int]] = {
                int(r["source_id"]): (int(r["cnt"]), float(r["dur"] or 0.0), int(r["sz"] or 0))
                for r in track_rows
                if r["source_id"] is not None
            }

            format_rows = conn.execute(
                """
                SELECT
                    source_id,
                    COALESCE(NULLIF(LOWER(TRIM(format)), ''), 'unknown') AS fmt,
                    COUNT(*) AS cnt,
                    COALESCE(SUM(duration_seconds), 0.0) AS dur,
                    COALESCE(SUM(file_size), 0) AS sz
                FROM tracks
                WHERE source_id IS NOT NULL
                GROUP BY source_id, fmt
                ORDER BY cnt DESC, fmt ASC;
                """
            ).fetchall()
            formats_by_source: dict[int, list[FormatBreakdown]] = {}
            for r in format_rows:
                sid = int(r["source_id"])
                formats_by_source.setdefault(sid, []).append(
                    FormatBreakdown(
                        format=str(r["fmt"]),
                        track_count=int(r["cnt"] or 0),
                        duration_seconds=float(r["dur"] or 0.0),
                        size_bytes=int(r["sz"] or 0),
                    )
                )

            pl_rows = conn.execute(
                """
                SELECT
                    p.id,
                    p.source_id,
                    p.name,
                    p.file_path,
                    p.format,
                    p.track_count,
                    p.updated_at,
                    COUNT(pe.id) AS entry_count,
                    COALESCE(
                        SUM(
                            COALESCE(
                                pe.duration_seconds,
                                CASE
                                    WHEN pe.start_ms IS NOT NULL AND pe.end_ms IS NOT NULL
                                    THEN (pe.end_ms - pe.start_ms) / 1000.0
                                    ELSE t.duration_seconds
                                END,
                                0.0
                            )
                        ),
                        0.0
                    ) AS total_dur,
                    COALESCE(SUM(CASE WHEN pe.is_missing = 1 THEN 1 ELSE 0 END), 0) AS missing_cnt
                FROM playlists p
                LEFT JOIN playlist_entries pe ON pe.playlist_id = p.id
                LEFT JOIN tracks t ON t.id = pe.track_id
                WHERE p.source_id IS NOT NULL
                GROUP BY p.id
                ORDER BY p.name COLLATE NOCASE ASC;
                """
            ).fetchall()

            playlists_by_source: dict[int, list[PlaylistSummaryRecord]] = {}
            for r in pl_rows:
                sid = int(r["source_id"])
                entry_count = int(r["entry_count"] or 0)
                fallback_count = int(r["track_count"] or 0)
                playlists_by_source.setdefault(sid, []).append(
                    PlaylistSummaryRecord(
                        id=int(r["id"]),
                        source_id=sid,
                        name=str(r["name"] or ""),
                        file_path=str(r["file_path"] or ""),
                        format=str(r["format"] or ""),
                        track_count=entry_count if entry_count > 0 else fallback_count,
                        total_duration_seconds=float(r["total_dur"] or 0.0),
                        missing_count=int(r["missing_cnt"] or 0),
                        updated_at=str(r["updated_at"]) if r["updated_at"] is not None else None,
                    )
                )

            scan_err_rows = conn.execute(
                """
                SELECT a.source_name, a.level, a.items_errors
                FROM activity_logs a
                INNER JOIN (
                    SELECT source_name, MAX(id) AS max_id
                    FROM activity_logs
                    WHERE category = 'SCAN' AND source_name IS NOT NULL
                    GROUP BY source_name
                ) latest ON latest.max_id = a.id;
                """
            ).fetchall()
            errors_by_name: dict[str, int] = {}
            for r in scan_err_rows:
                sname = str(r["source_name"])
                err_cnt = int(r["items_errors"] or 0)
                if err_cnt == 0 and str(r["level"] or "").upper() == "ERROR":
                    err_cnt = 1
                errors_by_name[sname] = err_cnt

            result: list[SourceLibrarySummary] = []
            for src in sources:
                sid = src.id or 0
                t_cnt, t_dur, t_sz = track_stats.get(sid, (0, 0.0, 0))
                result.append(
                    SourceLibrarySummary(
                        source=src,
                        track_count=t_cnt,
                        track_duration_seconds=t_dur,
                        playlists=playlists_by_source.get(sid, []),
                        last_scan_errors=errors_by_name.get(src.name, 0),
                        track_size_bytes=t_sz,
                        formats=formats_by_source.get(sid, []),
                    )
                )
            return result

    # -------------------------------------------------------------------------
    # Tracks CRUD & Batching
    # -------------------------------------------------------------------------
