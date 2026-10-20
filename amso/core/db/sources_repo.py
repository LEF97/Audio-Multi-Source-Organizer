"""Requêtes sur les sources (dossiers locaux, Drive, ...)."""

from __future__ import annotations

import contextlib
import logging
import sqlite3
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from amso.core.db.models import (
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

    # -------------------------------------------------------------------------
    # Tracks CRUD & Batching
    # -------------------------------------------------------------------------
