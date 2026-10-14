"""Modèles de données PySide6 virtualisés pour AMSO.

Utilise QAbstractTableModel pour garantir une navigation instantanée
et une fluidité parfaite sur de très grands volumes (> 50 000 titres).
"""

from __future__ import annotations

from typing import Any, Optional, Sequence

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QObject, Qt

from amso.core.database import DatabaseManager, TrackRecord
from amso.core.i18n import tr


def format_duration(seconds: Optional[float]) -> str:
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


def format_quality(score: int, fmt: Optional[str], bitrate: Optional[int]) -> str:
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


class TrackTableModel(QAbstractTableModel):
    """Modèle de table virtualisé pour l'affichage haute performance des pistes."""

    COLUMNS: list[tuple[str, str]] = [
        ("table.col_title", "title"),
        ("table.col_artist", "artist"),
        ("table.col_album", "album"),
        ("table.col_duration", "duration_seconds"),
        ("table.col_quality", "quality_score"),
        ("table.col_format", "format"),
        ("table.col_source", "source_type"),
        ("table.col_year", "year"),
        ("table.col_track", "track_number"),
    ]

    def __init__(self, db: DatabaseManager, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.db = db
        self._tracks: list[TrackRecord] = []
        self._current_sort_col = 0
        self._current_sort_order = Qt.SortOrder.AscendingOrder
        self._source_id_filter: Optional[int] = None
        self._source_type_filter: Optional[str] = None
        self._search_query: str = ""

    # -------------------------------------------------------------------------
    # Méthodes QAbstractTableModel
    # -------------------------------------------------------------------------

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._tracks)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self.COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or not (0 <= index.row() < len(self._tracks)):
            return None

        track = self._tracks[index.row()]
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return track.title or tr("track.untitled")
            elif col == 1:
                return track.artist or tr("track.unknown_artist")
            elif col == 2:
                return track.album or "--"
            elif col == 3:
                return format_duration(track.duration_seconds)
            elif col == 4:
                return format_quality(track.quality_score, track.format, track.bitrate)
            elif col == 5:
                return (track.format or "").upper()
            elif col == 6:
                st = track.source_type.value if hasattr(track.source_type, "value") else str(track.source_type)
                return st.capitalize()
            elif col == 7:
                return str(track.year) if track.year else ""
            elif col == 8:
                return str(track.track_number) if track.track_number else ""

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if col in {3, 7, 8}:  # Durée, année, piste alignés à droite
                return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            elif col in {4, 5, 6}:  # Qualité, format, source centrés
                return int(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        elif role == Qt.ItemDataRole.UserRole:
            # Retourne l'objet TrackRecord complet pour les actions contextuelles
            return track

        return None

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
        """Notifie la vue que les en-têtes et les libellés de qualité/titres ont changé."""
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, len(self.COLUMNS) - 1)
        if self._tracks:
            top_left = self.index(0, 0)
            bottom_right = self.index(len(self._tracks) - 1, len(self.COLUMNS) - 1)
            self.dataChanged.emit(top_left, bottom_right)

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        """Effectue le tri des données selon la colonne sélectionnée."""
        if not (0 <= column < len(self.COLUMNS)):
            return

        self._current_sort_col = column
        self._current_sort_order = order
        db_col_name = self.COLUMNS[column][1]
        sort_dir = "DESC" if order == Qt.SortOrder.DescendingOrder else "ASC"

        self.reload_data(sort_by=db_col_name, sort_order=sort_dir)

    # -------------------------------------------------------------------------
    # Gestion des données & Rafraîchissement
    # -------------------------------------------------------------------------

    def set_tracks(self, tracks: Sequence[TrackRecord]) -> None:
        """Remplace la collection de données du modèle."""
        self.beginResetModel()
        self._tracks = list(tracks)
        self.endResetModel()

    def get_track_at(self, row: int) -> Optional[TrackRecord]:
        """Retourne la piste située à la ligne spécifiée."""
        if 0 <= row < len(self._tracks):
            return self._tracks[row]
        return None

    def set_filter(
        self,
        source_id: Optional[int] = None,
        source_type: Optional[str] = None,
        search_query: str = "",
    ) -> None:
        """Applique un filtre et recharge les données."""
        self._source_id_filter = source_id
        self._source_type_filter = source_type
        self._search_query = search_query.strip()
        self.reload_data()

    def reload_data(
        self,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> None:
        """Recharge les pistes depuis la base de données SQLite."""
        col = sort_by or self.COLUMNS[self._current_sort_col][1]
        direction = sort_order or ("DESC" if self._current_sort_order == Qt.SortOrder.DescendingOrder else "ASC")

        # Recherche plein texte FTS5 si une requête est saisie
        if self._search_query:
            tracks, _ = self.db.search_tracks(
                query=self._search_query,
                limit=10000,
                offset=0,
            )
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
