"""Modèle de table virtualisé adapté à la vue par dossiers avec filtre local instantané."""

from __future__ import annotations

from PySide6.QtCore import QModelIndex, QObject, QPersistentModelIndex, Qt

from amso.core.database import DatabaseManager, TrackRecord
from amso.ui.models_base import BaseTrackTableModel


class FolderTrackTableModel(BaseTrackTableModel):
    """Modèle de table virtualisé adapté à la vue par dossiers avec filtre local instantané."""

    def __init__(self, db: DatabaseManager, parent: QObject | None = None) -> None:
        super().__init__(db, parent)
        self._all_tracks: list[TrackRecord] = []
        self._displayed_tracks: list[TrackRecord] = []
        self._current_folder_path: str | None = None
        self._current_playlist_id: int | None = None
        self._current_source_id: int | None = None
        self._recursive: bool = False
        self._search_query: str = ""

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._displayed_tracks)

    def _get_track_at_index(self, row: int) -> TrackRecord | None:
        if 0 <= row < len(self._displayed_tracks):
            return self._displayed_tracks[row]
        return None

    def set_folder(
        self,
        folder_path: str | None,
        source_id: int | None = None,
        recursive: bool = False,
    ) -> None:
        """Définit le dossier actif et charge ses pistes."""
        self._current_playlist_id = None
        self._current_folder_path = folder_path
        self._current_source_id = source_id
        self._recursive = recursive
        self.reload_data()

    def set_playlist(self, playlist_id: int | None) -> None:
        """Définit la playlist active et charge ses pistes ordonnées."""
        self._current_playlist_id = playlist_id
        self._playlist_explicit_sort = False
        self._current_folder_path = None
        self._current_source_id = None
        self._recursive = False
        self.reload_data()

    def set_search_query(self, query: str) -> None:
        """Applique un filtre textuel rapide sur les pistes du dossier."""
        self._search_query = query.strip().lower()
        self._apply_filter()

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        if not (0 <= column < len(self.COLUMNS)):
            return
        self._current_sort_col = column
        self._current_sort_order = order
        self._playlist_explicit_sort = True
        self.reload_data()

    def reload_data(self) -> None:
        """Recharge les pistes du dossier ou de la playlist actif depuis SQLite."""
        self._refresh_sources_cache()

        if self._current_playlist_id is not None:
            raw_tracks = self.db.get_playlist_tracks(self._current_playlist_id)
            if getattr(self, "_playlist_explicit_sort", False):
                col = self.COLUMNS[self._current_sort_col][1]
                if col != "track_number":
                    reverse = self._current_sort_order == Qt.SortOrder.DescendingOrder
                    self._all_tracks = sorted(
                        raw_tracks,
                        key=lambda t: (getattr(t, col, None) is None, str(getattr(t, col, "") or "").lower()),
                        reverse=reverse,
                    )
                else:
                    if self._current_sort_order == Qt.SortOrder.DescendingOrder:
                        self._all_tracks = list(reversed(raw_tracks))
                    else:
                        self._all_tracks = list(raw_tracks)
            else:
                self._all_tracks = list(raw_tracks)
            self._apply_filter()
            return

        if not self._current_folder_path:
            self.beginResetModel()
            self._all_tracks = []
            self._displayed_tracks = []
            self.endResetModel()
            return

        col = self.COLUMNS[self._current_sort_col][1]
        direction = "DESC" if self._current_sort_order == Qt.SortOrder.DescendingOrder else "ASC"

        self._all_tracks = self.db.get_tracks_by_folder(
            folder_path=self._current_folder_path,
            source_id=self._current_source_id,
            recursive=self._recursive,
            sort_by=col,
            sort_order=direction,
        )
        self._apply_filter()

    def _apply_filter(self) -> None:
        self.beginResetModel()
        if not self._search_query:
            self._displayed_tracks = list(self._all_tracks)
        else:
            q = self._search_query
            self._displayed_tracks = [
                t
                for t in self._all_tracks
                if (t.file_name and q in t.file_name.lower())
                or (t.title and q in t.title.lower())
                or (t.artist and q in t.artist.lower())
                or (t.album and q in t.album.lower())
                or (t.genre and q in t.genre.lower())
            ]
        self.endResetModel()
