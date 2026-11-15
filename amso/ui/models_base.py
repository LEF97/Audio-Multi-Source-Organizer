"""Modèles de données PySide6 virtualisés pour AMSO.

Utilise QAbstractTableModel pour garantir une navigation instantanée
et une fluidité parfaite sur de très grands volumes (> 50 000 titres).
Toutes les tables partagent une structure de colonnes harmonisée représentant
l'intégralité des champs de la table SQLite 'tracks'.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QObject, QPersistentModelIndex, Qt
from PySide6.QtGui import QColor, QFont

from amso.core.database import DatabaseManager, TrackRecord
from amso.core.i18n import tr


def format_duration(seconds: float | None, *, always_hours: bool = False) -> str:
    """Formate une durée en secondes sous la forme MM:SS, H:MM:SS ou Jj HH:MM:SS."""
    if seconds is None or seconds <= 0:
        return "0:00:00" if always_hours else "--:--"
    total_sec = int(round(seconds))
    days, rem = divmod(total_sec, 86400)
    hrs, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    if days > 0:
        return f"{days}{tr('unit.days_short')} {hrs:02d}:{mins:02d}:{secs:02d}"
    if hrs > 0 or always_hours:
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
        return tr("unit.size_bytes", value=size_bytes)
    elif size_bytes < 1024 * 1024:
        return tr("unit.size_kb", value=f"{size_bytes / 1024:.1f}")
    elif size_bytes < 1024 * 1024 * 1024:
        return tr("unit.size_mb", value=f"{size_bytes / (1024 * 1024):.1f}")
    return tr("unit.size_gb", value=f"{size_bytes / (1024 * 1024 * 1024):.2f}")


# Spécification unifiée de toutes les colonnes représentant l'ensemble des champs de la table 'tracks' :
# (clé_traduction, nom_champ_bdd, largeur_initiale_px, visible_par_defaut)
UNIFIED_TRACK_COLUMNS: list[tuple[str, str, int, bool]] = [
    ("table.col_playing", "is_playing", 30, True),
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
        self._player_service: Any = None
        self._sources_cache: dict[int, str] = {}
        self._current_sort_col = 1
        self._current_sort_order = Qt.SortOrder.AscendingOrder
        self._refresh_sources_cache()

    def set_player_service(self, player_service: Any) -> None:
        """Associe le service de lecture pour mettre en évidence la piste en cours dans le tableau."""
        self._player_service = player_service
        if player_service is not None:
            player_service.track_changed.connect(self._on_playback_indicator_changed)
            player_service.state_changed.connect(self._on_playback_indicator_changed)

    def _on_playback_indicator_changed(self, *_: Any) -> None:
        r_cnt = self.rowCount()
        if r_cnt > 0:
            self.dataChanged.emit(
                self.index(0, 0),
                self.index(r_cnt - 1, len(self.COLUMNS) - 1),
                [
                    Qt.ItemDataRole.DisplayRole,
                    Qt.ItemDataRole.ForegroundRole,
                    Qt.ItemDataRole.FontRole,
                ],
            )

    def _is_current_track(self, track: TrackRecord) -> bool:
        """Indique si la piste correspond au morceau actuellement chargé dans le lecteur."""
        if self._player_service is None:
            return False
        curr: TrackRecord | None = getattr(self._player_service, "current_track", None)
        if curr is None:
            return False
        if curr.is_cue_segment and track.is_cue_segment:
            if track.cue_start_ms != curr.cue_start_ms:
                return False
        elif not curr.is_cue_segment and track.is_cue_segment:
            return False
        if track.id is not None and curr.id is not None and track.id == curr.id:
            return True
        if track.source_path and curr.source_path:
            return os.path.normcase(os.path.normpath(track.source_path)) == os.path.normcase(
                os.path.normpath(curr.source_path)
            )
        return False

    def current_track_row(self) -> int:
        """Retourne l'indice de ligne de la piste en cours de lecture, ou -1 si absente."""
        for row in range(self.rowCount()):
            trk = self._get_track_at_index(row)
            if trk is not None and self._is_current_track(trk):
                return row
        return -1

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
                key = self.COLUMNS[section][0]
                if key == "table.col_playing":
                    return " "
                return tr(key)
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
        is_current = self._is_current_track(track)

        if role == Qt.ItemDataRole.DisplayRole:
            return self._display_data(track, field, is_current)
        if role == Qt.ItemDataRole.ToolTipRole:
            return self._tooltip_data(track, field)
        if role == Qt.ItemDataRole.ForegroundRole:
            if is_current:
                return QColor("#38BDF8")
            if getattr(track, "is_missing", False):
                return QColor("#F87171")
            return None
        if role == Qt.ItemDataRole.FontRole:
            if is_current:
                font = QFont()
                font.setBold(True)
                return font
            return None
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return self._alignment_data(field)
        if role == Qt.ItemDataRole.UserRole:
            return track
        return None

    def _display_data(self, track: TrackRecord, field: str, is_current: bool) -> Any:
        if field == "is_playing":
            if is_current:
                is_playing = bool(self._player_service and getattr(self._player_service, "is_playing", False))
                return "▶" if is_playing else "⏸"
            return ""
        if field == "file_name":
            prefix = "⚠️ " if getattr(track, "is_missing", False) else ""
            fn = track.file_name or (track.source_path.rsplit("/", 1)[-1] if track.source_path else "--")
            return f"{prefix}{fn}"
        if field == "title":
            prefix = "⚠️ " if getattr(track, "is_missing", False) else ""
            return prefix + (track.title or tr("track.untitled"))
        if field == "artist":
            return track.artist or tr("track.unknown_artist")
        if field == "album_artist":
            return track.album_artist or "--"
        if field == "album":
            return track.album or "--"
        if field == "genre":
            return track.genre or "--"
        if field == "year":
            return str(track.year) if track.year else ""
        if field == "track_number":
            return str(track.track_number) if track.track_number else ""
        if field == "disc_number":
            return str(track.disc_number) if track.disc_number else ""
        if field == "duration_seconds":
            return format_duration(track.duration_seconds)
        if field == "format":
            return (track.format or "").upper()
        if field == "bitrate":
            return f"{track.bitrate} kbps" if track.bitrate else "--"
        if field == "sample_rate":
            return f"{track.sample_rate / 1000:.1f} kHz" if track.sample_rate else "--"
        return self._display_extended_data(track, field)

    def _display_extended_data(self, track: TrackRecord, field: str) -> Any:
        if field == "channels":
            if track.channels == 2:
                return tr("table.channels_stereo")
            if track.channels == 1:
                return tr("table.channels_mono")
            return f"{track.channels} ch" if track.channels else "--"
        if field == "quality_score":
            return format_quality(track.quality_score, track.format, track.bitrate)
        if field == "file_size":
            return format_file_size(track.file_size)
        if field == "source_id":
            if track.source_id in self._sources_cache:
                return self._sources_cache[track.source_id]
            return f"#{track.source_id}" if track.source_id else "--"
        if field == "source_type":
            st = track.source_type.value if hasattr(track.source_type, "value") else str(track.source_type)
            return st.capitalize()
        if field in {"folder_name", "folder_path", "source_path", "isrc"}:
            return getattr(track, field, None) or "--"
        if field == "file_mtime":
            if track.file_mtime:
                try:
                    return datetime.fromtimestamp(track.file_mtime).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    return str(track.file_mtime)
            return "--"
        if field in {"created_at", "updated_at"}:
            val = getattr(track, field, None)
            return val[:16] if val and len(val) >= 16 else (val or "--")
        if field == "file_hash":
            return (
                (track.file_hash[:10] + "...")
                if track.file_hash and len(track.file_hash) > 10
                else (track.file_hash or "--")
            )
        if field == "audio_fingerprint":
            return (
                (track.audio_fingerprint[:12] + "...")
                if track.audio_fingerprint and len(track.audio_fingerprint) > 12
                else (track.audio_fingerprint or "--")
            )
        if field == "duplicate_cluster_id":
            return f"#{track.duplicate_cluster_id}" if track.duplicate_cluster_id else "--"
        if field == "id":
            return str(track.id) if track.id is not None else ""
        return None

    def _tooltip_data(self, track: TrackRecord, field: str) -> Any:
        if getattr(track, "is_missing", False):
            return tr("table.file_missing_tooltip", path=track.source_path or track.source_ref)
        if field in {"source_path", "folder_path", "file_name", "title", "artist", "album"}:
            return getattr(track, field, "")
        if field == "file_hash":
            return track.file_hash or ""
        if field == "audio_fingerprint":
            return track.audio_fingerprint or ""
        return None

    def _alignment_data(self, field: str) -> int:
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
        if field in {"is_playing", "format", "channels", "quality_score", "source_type", "duplicate_cluster_id"}:
            return int(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
