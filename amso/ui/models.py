"""Modèles de données PySide6 virtualisés pour AMSO.

Ce module réexporte l'ensemble des modèles de tables de pistes audio
pour garantir la compatibilité ascendante.
"""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QModelIndex, QObject, QPersistentModelIndex, Qt

from amso.core.database import DatabaseManager, TrackRecord
from amso.ui.folder_track_model import FolderTrackTableModel
from amso.ui.models_base import (
    UNIFIED_TRACK_COLUMNS,
    BaseTrackTableModel,
    format_duration,
    format_file_size,
    format_quality,
)
from amso.ui.playlist_table_model import PlaylistTableModel


class TrackTableModel(BaseTrackTableModel):
    """Modèle de table virtualisé pour l'affichage haute performance des pistes de la bibliothèque."""

    def __init__(self, db: DatabaseManager, parent: QObject | None = None) -> None:
        super().__init__(db, parent)
        self._tracks: list[TrackRecord] = []
        self._source_id_filter: int | None = None
        self._source_type_filter: str | None = None
        self._search_query: str = ""

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._tracks)

    def _get_track_at_index(self, row: int) -> TrackRecord | None:
        if 0 <= row < len(self._tracks):
            return self._tracks[row]
        return None

    def set_tracks(self, tracks: Sequence[TrackRecord]) -> None:
        """Remplace directement la collection de pistes du modèle (ex: doublons)."""
        self.beginResetModel()
        self._tracks = list(tracks)
        self.endResetModel()

    def set_filter(
        self,
        source_id: int | None = None,
        source_type: str | None = None,
        search_query: str = "",
    ) -> None:
        """Applique des critères de filtre et recharge les données."""
        self._source_id_filter = source_id
        self._source_type_filter = source_type
        self._search_query = search_query.strip()
        self.reload_data()

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        """Effectue le tri des données selon la colonne sélectionnée."""
        if not (0 <= column < len(self.COLUMNS)):
            return

        self._current_sort_col = column
        self._current_sort_order = order
        db_col_name = self.COLUMNS[column][1]
        sort_dir = "DESC" if order == Qt.SortOrder.DescendingOrder else "ASC"

        self.reload_data(sort_by=db_col_name, sort_order=sort_dir)

    def reload_data(
        self,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> None:
        """Recharge les pistes depuis la base de données SQLite."""
        self._refresh_sources_cache()
        col = sort_by or self.COLUMNS[self._current_sort_col][1]
        direction = sort_order or ("DESC" if self._current_sort_order == Qt.SortOrder.DescendingOrder else "ASC")

        if self._search_query:
            tracks, _ = self.db.search_tracks(
                query=self._search_query,
                limit=10000,
                offset=0,
            )
            # Tri en mémoire pour les résultats de recherche plein texte
            reverse = direction == "DESC"
            try:
                tracks.sort(key=lambda t: (getattr(t, col, None) is None, getattr(t, col, "")), reverse=reverse)
            except Exception:
                pass
        else:
            tracks, _ = self.db.get_tracks(
                limit=50000,
                offset=0,
                source_type=self._source_type_filter,
                source_id=self._source_id_filter,
                sort_by=col,
                sort_order=direction,
            )

        self.set_tracks(tracks)


__all__ = [
    "format_duration",
    "format_quality",
    "format_file_size",
    "UNIFIED_TRACK_COLUMNS",
    "BaseTrackTableModel",
    "TrackTableModel",
    "FolderTrackTableModel",
    "PlaylistTableModel",
]
