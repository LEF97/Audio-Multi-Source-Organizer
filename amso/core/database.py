"""Couche de persistance SQLite3 pour AMSO.

Conçue pour absorber de grands volumes (> 50 000 titres) sans ORM lourd,
avec mode WAL, indexation ciblée et recherche plein texte (FTS5).
"""

from __future__ import annotations

import contextlib
import logging
import sqlite3
import time
from collections.abc import Generator
from pathlib import Path

from amso.core.db.activity_repo import ActivityRepoMixin
from amso.core.db.curation_repo import TrackCurationMixin
from amso.core.db.library_queries import LibraryQueriesMixin
from amso.core.db.models import (
    ActivityLogRecord,
    FormatBreakdown,
    PlaylistEntryRecord,
    PlaylistRecord,
    PlaylistSummaryRecord,
    SourceLibrarySummary,
    SourceRecord,
    SourceType,
    TrackRecord,
    compute_quality_score,
)
from amso.core.db.paths import (
    get_database_path,
    get_default_data_dir,
    get_saved_playlist_path,
)
from amso.core.db.playlists_repo import PlaylistsRepoMixin
from amso.core.db.schema import apply_schema
from amso.core.db.sources_repo import SourcesRepoMixin
from amso.core.db.tracks_repo import TracksRepoMixin

__all__ = [
    "ActivityLogRecord",
    "PlaylistEntryRecord",
    "FormatBreakdown",
    "PlaylistRecord",
    "PlaylistSummaryRecord",
    "SourceLibrarySummary",
    "SourceRecord",
    "SourceType",
    "TrackRecord",
    "compute_quality_score",
    "get_database_path",
    "get_default_data_dir",
    "get_saved_playlist_path",
    "DatabaseManager",
]

logger = logging.getLogger(__name__)


class DatabaseManager(
    SourcesRepoMixin, TracksRepoMixin, TrackCurationMixin, LibraryQueriesMixin, ActivityRepoMixin, PlaylistsRepoMixin
):
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
        """Initialise le schéma relationnel, les index et l'index FTS5 (voir `db/schema.py`)."""
        with self.get_connection() as conn:
            apply_schema(conn)

    # -------------------------------------------------------------------------
    # Sources CRUD
    # -------------------------------------------------------------------------
