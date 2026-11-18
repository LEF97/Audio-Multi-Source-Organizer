"""Modèle de tableau pour la liste de lecture (Playlist) en cours."""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

from PySide6.QtCore import QByteArray, QMimeData, QModelIndex, QObject, QPersistentModelIndex, Qt

from amso.core.database import DatabaseManager, TrackRecord
from amso.ui.models_base import UNIFIED_TRACK_COLUMNS, BaseTrackTableModel


def _build_playlist_columns() -> list[tuple[str, str, int, bool]]:
    """Construit les colonnes de la liste de lecture à partir de UNIFIED_TRACK_COLUMNS."""
    default_specs: dict[str, tuple[int, bool]] = {
        "title": (240, True),
        "artist": (180, True),
        "album": (180, True),
        "duration_seconds": (80, True),
        "format": (80, True),
    }
    by_field = {field: (key, field, width, visible) for key, field, width, visible in UNIFIED_TRACK_COLUMNS}

    cols: list[tuple[str, str, int, bool]] = [
        ("table.col_playing", "is_playing", 30, True),
        ("table.col_order", "playlist_order", 45, True),
    ]
    for field, (width, visible) in default_specs.items():
        cols.append((by_field[field][0], field, width, visible))

    excluded = {"is_playing", *default_specs.keys()}
    for key, field, width, _ in UNIFIED_TRACK_COLUMNS:
        if field not in excluded:
            cols.append((key, field, width, False))
    return cols


class PlaylistTableModel(BaseTrackTableModel):
    """Modèle de tableau pour la liste de lecture (Playlist) en cours."""

    COLUMNS: list[tuple[str, str, int, bool]] = _build_playlist_columns()

    def __init__(
        self,
        player_service: Any,
        parent: QObject | None = None,
        db: DatabaseManager | None = None,
    ) -> None:
        super().__init__(db, parent)
        self.player = player_service
        self.set_player_service(player_service)
        self.player.playlist_updated.connect(self._on_playlist_updated)

    def _on_playlist_updated(self) -> None:
        self.beginResetModel()
        self.endResetModel()

    def _on_playback_indicator_changed(self, *_: Any) -> None:
        super()._on_playback_indicator_changed()

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self.player.playlist)

    def _get_track_at_index(self, row: int) -> TrackRecord | None:
        playlist = self.player.playlist
        if 0 <= row < len(playlist):
            return playlist[row]
        return None

    def _is_current_row(self, row: int, track: TrackRecord) -> bool:
        return row == self.player.current_index

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if 0 <= section < len(self.COLUMNS) and self.COLUMNS[section][0] == "table.col_order":
                return "#"
        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        col = index.column()
        if 0 <= col < len(self.COLUMNS) and self.COLUMNS[col][1] == "playlist_order":
            if role == Qt.ItemDataRole.DisplayRole:
                return str(index.row() + 1)
            if role == Qt.ItemDataRole.TextAlignmentRole:
                return int(Qt.AlignmentFlag.AlignCenter)
        return super().data(index, role)

    MIME_TYPE = "application/x-amso-playlist-rows"

    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        default_flags = super().flags(index)
        if index.isValid():
            return default_flags | Qt.ItemFlag.ItemIsDragEnabled
        return default_flags | Qt.ItemFlag.ItemIsDropEnabled

    def supportedDropActions(self) -> Qt.DropAction:
        return Qt.DropAction.MoveAction

    def mimeTypes(self) -> list[str]:
        return [self.MIME_TYPE]

    def mimeData(self, indexes: Iterable[QModelIndex | QPersistentModelIndex]) -> QMimeData:
        mime_data = QMimeData()
        rows = sorted({idx.row() for idx in indexes if idx.isValid()})
        mime_data.setData(self.MIME_TYPE, QByteArray(json.dumps(rows).encode("utf-8")))
        return mime_data
