"""Modèles de données PySide6 virtualisés pour AMSO.

Utilise QAbstractTableModel pour garantir une navigation instantanée
et une fluidité parfaite sur de très grands volumes (> 50 000 titres).
Toutes les tables partagent une structure de colonnes harmonisée représentant
l'intégralité des champs de la table SQLite 'tracks'.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from datetime import datetime
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QByteArray, QMimeData, QModelIndex, QObject, QPersistentModelIndex, Qt
from PySide6.QtGui import QColor, QFont

from amso.core.database import DatabaseManager, TrackRecord
from amso.core.i18n import tr


def format_duration(seconds: float | None) -> str:
    """Formate une durée en secondes sous la forme MM:SS ou HH:MM:SS."""
    if seconds is None or seconds <= 0:
        return "--:--"
    total_sec = int(round(seconds))
    hrs = total_sec // 3600
    mins = (total_sec % 3600) // 60
    secs = total_sec % 60
    if hrs > 0:
        return f"{hrs}:{mins:02d}:{secs:02d}"
    return f"{mins}:{secs:02d}"


def format_quality(score: int, fmt: str | None, bitrate: int | None) -> str:
    """Génère un libellé lisible de qualité audio."""
    f = (fmt or "").upper()
    if score >= 900:
        return tr("quality.hires", format=f)
    elif score >= 800:
        return tr("quality.lossless", format=f)
    elif score >= 600:
        return tr("quality.bitrate", format=f, bitrate=bitrate) if bitrate else tr("quality.hq", format=f)
    elif score >= 400:
        return tr("quality.bitrate", format=f, bitrate=bitrate) if bitrate else f
    return f if f else tr("quality.audio")


def format_file_size(size_bytes: int | None) -> str:
    """Formate une taille en octets en Ko, Mo ou Go."""
    if not size_bytes or size_bytes <= 0:
        return "--"
    if size_bytes < 1024:
        return f"{size_bytes} o"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} Ko"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} Mo"
    return f"{size_bytes / (1024 * 1024 * 1024):.2f} Go"


# Spécification unifiée de toutes les colonnes représentant l'ensemble des champs de la table 'tracks' :
# (clé_traduction, nom_champ_bdd, largeur_initiale_px, visible_par_defaut)
UNIFIED_TRACK_COLUMNS: list[tuple[str, str, int, bool]] = [
    ("table.col_filename", "file_name", 190, True),
    ("table.col_title", "title", 180, True),
    ("table.col_artist", "artist", 140, True),
    ("table.col_album", "album", 140, True),
    ("table.col_album_artist", "album_artist", 140, False),
    ("table.col_genre", "genre", 100, True),
    ("table.col_year", "year", 65, True),
    ("table.col_track", "track_number", 60, True),
    ("table.col_disc", "disc_number", 60, False),
    ("table.col_duration", "duration_seconds", 65, True),
    ("table.col_format", "format", 65, True),
    ("table.col_bitrate", "bitrate", 75, True),
    ("table.col_sample_rate", "sample_rate", 85, False),
    ("table.col_channels", "channels", 65, False),
    ("table.col_quality", "quality_score", 95, True),
    ("table.col_size", "file_size", 75, True),
    ("table.col_source", "source_id", 100, True),
    ("table.col_source_type", "source_type", 90, False),
    ("table.col_folder_name", "folder_name", 120, False),
    ("table.col_folder_path", "folder_path", 160, False),
    ("table.col_source_path", "source_path", 200, False),
    ("table.col_file_mtime", "file_mtime", 120, False),
    ("table.col_created_at", "created_at", 120, False),
    ("table.col_updated_at", "updated_at", 120, False),
    ("table.col_file_hash", "file_hash", 90, False),
    ("table.col_audio_fingerprint", "audio_fingerprint", 90, False),
    ("table.col_isrc", "isrc", 80, False),
    ("table.col_duplicate_cluster_id", "duplicate_cluster_id", 70, False),
    ("table.col_id", "id", 50, False),
]


class BaseTrackTableModel(QAbstractTableModel):
    """Classe de base unifiée pour tous les modèles de tables affichant des pistes audio."""

    COLUMNS: list[tuple[str, str, int, bool]] = UNIFIED_TRACK_COLUMNS

    def __init__(self, db: DatabaseManager, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.db = db
        self._sources_cache: dict[int, str] = {}
        self._current_sort_col = 0
        self._current_sort_order = Qt.SortOrder.AscendingOrder
        self._refresh_sources_cache()

    def _refresh_sources_cache(self) -> None:
        try:
            sources = self.db.get_sources()
            self._sources_cache = {s.id: s.name for s in sources if s.id is not None}
        except Exception:
            pass

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self.COLUMNS)

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if 0 <= section < len(self.COLUMNS):
                return tr(self.COLUMNS[section][0])
        return None

    def notify_language_changed(self) -> None:
        """Notifie la vue du changement de langue pour réactualiser en-têtes et données."""
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, len(self.COLUMNS) - 1)
        r_cnt = self.rowCount()
        if r_cnt > 0:
            top_left = self.index(0, 0)
            bottom_right = self.index(r_cnt - 1, len(self.COLUMNS) - 1)
            self.dataChanged.emit(top_left, bottom_right)

    def _get_track_at_index(self, row: int) -> TrackRecord | None:
        """À implémenter par les classes dérivées."""
        raise NotImplementedError

    def get_track_at(self, row: int) -> TrackRecord | None:
        """Retourne la piste située à la ligne spécifiée."""
        return self._get_track_at_index(row)

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        track = self._get_track_at_index(index.row())
        if not track:
            return None

        col = index.column()
        if not (0 <= col < len(self.COLUMNS)):
            return None

        field = self.COLUMNS[col][1]

        if role == Qt.ItemDataRole.DisplayRole:
            if field == "file_name":
                return track.file_name or (track.source_path.rsplit("/", 1)[-1] if track.source_path else "--")
            elif field == "title":
                return track.title or tr("track.untitled")
            elif field == "artist":
                return track.artist or tr("track.unknown_artist")
            elif field == "album_artist":
                return track.album_artist or "--"
            elif field == "album":
                return track.album or "--"
            elif field == "genre":
                return track.genre or "--"
            elif field == "year":
                return str(track.year) if track.year else ""
            elif field == "track_number":
                return str(track.track_number) if track.track_number else ""
            elif field == "disc_number":
                return str(track.disc_number) if track.disc_number else ""
            elif field == "duration_seconds":
                return format_duration(track.duration_seconds)
            elif field == "format":
                return (track.format or "").upper()
            elif field == "bitrate":
                return f"{track.bitrate} kbps" if track.bitrate else "--"
            elif field == "sample_rate":
                return f"{track.sample_rate / 1000:.1f} kHz" if track.sample_rate else "--"
            elif field == "channels":
                if track.channels == 2:
                    return "Stéréo"
                elif track.channels == 1:
                    return "Mono"
                elif track.channels:
                    return f"{track.channels} ch"
                return "--"
            elif field == "quality_score":
                return format_quality(track.quality_score, track.format, track.bitrate)
            elif field == "file_size":
                return format_file_size(track.file_size)
            elif field == "source_id":
                if track.source_id in self._sources_cache:
                    return self._sources_cache[track.source_id]
                return f"#{track.source_id}" if track.source_id else "--"
            elif field == "source_type":
                st = track.source_type.value if hasattr(track.source_type, "value") else str(track.source_type)
                return st.capitalize()
            elif field == "folder_name":
                return track.folder_name or "--"
            elif field == "folder_path":
                return track.folder_path or "--"
            elif field == "source_path":
                return track.source_path or "--"
            elif field == "file_mtime":
                if track.file_mtime:
                    try:
                        return datetime.fromtimestamp(track.file_mtime).strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        return str(track.file_mtime)
                return "--"
            elif field == "created_at":
                return (
                    track.created_at[:16]
                    if track.created_at and len(track.created_at) >= 16
                    else (track.created_at or "--")
                )
            elif field == "updated_at":
                return (
                    track.updated_at[:16]
                    if track.updated_at and len(track.updated_at) >= 16
                    else (track.updated_at or "--")
                )
            elif field == "file_hash":
                return (
                    (track.file_hash[:10] + "...")
                    if track.file_hash and len(track.file_hash) > 10
                    else (track.file_hash or "--")
                )
            elif field == "audio_fingerprint":
                return (
                    (track.audio_fingerprint[:12] + "...")
                    if track.audio_fingerprint and len(track.audio_fingerprint) > 12
                    else (track.audio_fingerprint or "--")
                )
            elif field == "isrc":
                return track.isrc or "--"
            elif field == "duplicate_cluster_id":
                return f"#{track.duplicate_cluster_id}" if track.duplicate_cluster_id else "--"
            elif field == "id":
                return str(track.id) if track.id is not None else ""

        elif role == Qt.ItemDataRole.ToolTipRole:
            if field in {"source_path", "folder_path"}:
                return getattr(track, field, "")
            elif field == "file_hash":
                return track.file_hash or ""
            elif field == "audio_fingerprint":
                return track.audio_fingerprint or ""
            elif field in {"file_name", "title", "artist", "album"}:
                return getattr(track, field, "")

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if field in {
                "year",
                "track_number",
                "disc_number",
                "duration_seconds",
                "bitrate",
                "sample_rate",
                "file_size",
                "id",
            }:
                return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            elif field in {"format", "channels", "quality_score", "source_type", "duplicate_cluster_id"}:
                return int(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        elif role == Qt.ItemDataRole.UserRole:
            return track

        return None


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


class FolderTrackTableModel(BaseTrackTableModel):
    """Modèle de table virtualisé adapté à la vue par dossiers avec filtre local instantané."""

    def __init__(self, db: DatabaseManager, parent: QObject | None = None) -> None:
        super().__init__(db, parent)
        self._all_tracks: list[TrackRecord] = []
        self._displayed_tracks: list[TrackRecord] = []
        self._current_folder_path: str | None = None
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
        self._current_folder_path = folder_path
        self._current_source_id = source_id
        self._recursive = recursive
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
        self.reload_data()

    def reload_data(self) -> None:
        """Recharge les pistes du dossier actif depuis SQLite."""
        self._refresh_sources_cache()
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

