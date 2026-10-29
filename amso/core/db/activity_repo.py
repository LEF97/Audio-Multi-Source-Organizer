"""Journal d'activité."""

from __future__ import annotations

import contextlib
import logging
import sqlite3
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from amso.core.activity_messages import LogMessage, encode, render_source_language
from amso.core.db.models import (
    ActivityLogRecord,
)

logger = logging.getLogger(__name__)


class ActivityRepoMixin:
    """Journal d'activité."""

    if TYPE_CHECKING:
        # Fournis par DatabaseManager (typage uniquement)
        def get_connection(self) -> contextlib.AbstractContextManager[sqlite3.Connection]: ...

    def add_activity_log(
        self,
        action: str | LogMessage,
        level: str = "INFO",
        category: str = "SYNC",
        source_name: str | None = None,
        details: str | list[LogMessage] | None = None,
        items_added: int = 0,
        items_updated: int = 0,
        items_deleted: int = 0,
        items_errors: int = 0,
        timestamp: str | None = None,
    ) -> int:
        """Insère une nouvelle entrée dans le journal d'activité."""
        now = timestamp or datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        i18n_payload: str | None = None
        if isinstance(action, LogMessage):
            lines = details if isinstance(details, list) else None
            i18n_payload = encode(action, lines)
            # Rendu français conservé : recherche SQL, export et repli si le JSON devenait illisible
            action = render_source_language(action)
            if lines is not None:
                details = "\n".join(render_source_language(m) for m in lines)
        elif isinstance(details, list):
            details = "\n".join(render_source_language(m) for m in details)
        with self.get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO activity_logs (
                    timestamp, level, category, source_name, action, details,
                    items_added, items_updated, items_deleted, items_errors, i18n
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
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
                    i18n_payload,
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

    # -------------------------------------------------------------------------
    # Gestion des Playlists (M3U, PLS, XSPF, WPL)
    # -------------------------------------------------------------------------
