"""Modèle de tableau pour la liste de lecture (Playlist) en cours."""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QByteArray, QMimeData, QModelIndex, QObject, QPersistentModelIndex, Qt
from PySide6.QtGui import QColor, QFont

from amso.core.database import TrackRecord
from amso.core.i18n import tr
from amso.ui.models_base import format_duration


class PlaylistTableModel(QAbstractTableModel):
    """Modèle de tableau pour la liste de lecture (Playlist) en cours."""

    COLUMNS: list[tuple[str, int]] = [
        ("table.col_playing", 40),
        ("table.col_order", 45),
        ("table.col_title", 240),
        ("table.col_artist", 180),
        ("table.col_album", 180),
        ("table.col_duration", 80),
        ("table.col_format", 80),
    ]

    def __init__(self, player_service: Any, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.player = player_service
        self.player.playlist_updated.connect(self._on_playlist_updated)
        self.player.track_changed.connect(self._on_track_changed)

    def _on_playlist_updated(self) -> None:
        self.beginResetModel()
        self.endResetModel()

    def _on_track_changed(self, track: Any) -> None:
        if self.rowCount() > 0:
            self.dataChanged.emit(
                self.index(0, 0),
                self.index(self.rowCount() - 1, len(self.COLUMNS) - 1),
                [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ForegroundRole, Qt.ItemDataRole.FontRole],
            )

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self.player.playlist)

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self.COLUMNS)

    def notify_language_changed(self) -> None:
        """Notifie la vue que les en-têtes de colonnes ont changé de langue."""
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, len(self.COLUMNS) - 1)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if 0 <= section < len(self.COLUMNS):
                key = self.COLUMNS[section][0]
                if key == "table.col_playing":
                    return " "
                if key == "table.col_order":
                    return "#"
                return tr(key)
        return None

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        row = index.row()
        playlist = self.player.playlist
        if not (0 <= row < len(playlist)):
            return None

        track = playlist[row]
        col = index.column()
        is_current = row == self.player.current_index

        # Style de mise en surbrillance pour la piste en cours
        if role == Qt.ItemDataRole.ForegroundRole:
            if is_current:
                return QColor("#38BDF8")  # Bleu ciel accentué
            return QColor("#E2E8F0")

        if role == Qt.ItemDataRole.FontRole:
            if is_current:
                font = QFont()
                font.setBold(True)
                return font

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if col in {0, 1, 5, 6}:
                return int(Qt.AlignmentFlag.AlignCenter)
            return int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                if is_current:
                    return "▶" if self.player.is_playing else "⏸"
                return ""
            elif col == 1:
                return str(row + 1)
            elif col == 2:
                return track.title or track.file_name or tr("track.untitled")
            elif col == 3:
                return track.artist or "--"
            elif col == 4:
                return track.album or "--"
            elif col == 5:
                return format_duration(track.duration_seconds)
            elif col == 6:
                return (track.format or "").upper()

        return None

    def get_track_at(self, row: int) -> TrackRecord | None:
        playlist = self.player.playlist
        if 0 <= row < len(playlist):
            return playlist[row]
        return None

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
