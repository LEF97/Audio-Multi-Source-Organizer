"""Modèles de données PySide6 virtualisés pour AMSO.

Utilise QAbstractTableModel pour garantir une navigation instantanée
et une fluidité parfaite sur de très grands volumes (> 50 000 titres).
Toutes les tables partagent une structure de colonnes harmonisée représentant
l'intégralité des champs de la table SQLite 'tracks'.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QObject, QPersistentModelIndex, Qt
from PySide6.QtGui import QColor

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
                prefix = "⚠️ " if getattr(track, "is_missing", False) else ""
                fn = track.file_name or (track.source_path.rsplit("/", 1)[-1] if track.source_path else "--")
                return prefix + fn
            elif field == "title":
                prefix = "⚠️ " if getattr(track, "is_missing", False) else ""
                return prefix + (track.title or tr("track.untitled"))
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
            if getattr(track, "is_missing", False):
                return f"⚠️ Fichier introuvable sur le disque :\n{track.source_path or track.source_ref}"
            elif field in {"source_path", "folder_path"}:
                return getattr(track, field, "")
            elif field == "file_hash":
                return track.file_hash or ""
            elif field == "audio_fingerprint":
                return track.audio_fingerprint or ""
            elif field in {"file_name", "title", "artist", "album"}:
                return getattr(track, field, "")

        elif role == Qt.ItemDataRole.ForegroundRole:
            if getattr(track, "is_missing", False):
                return QColor("#F87171")

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
