"""Modèles de données persistés (types de source, enregistrements pistes/sources/playlists/journal)."""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class SourceType(StrEnum):
    """Types de sources audio prises en charge."""

    LOCAL = "local"
    GDRIVE = "gdrive"
    SPOTIFY = "spotify"
    DEEZER = "deezer"


def compute_quality_score(
    audio_format: str | None,
    bitrate: int | None,
    sample_rate: int | None,
) -> int:
    """Calcule un score qualitatif heuristique de 0 à 1000 pour prioriser les doublons.

    Hiérarchie générale :
    - Lossless Hi-Res (FLAC/ALAC/WAV > 48kHz) : 900 - 1000
    - Lossless CD standard (FLAC/WAV 44.1/48kHz) : 800 - 899
    - Lossy très haute qualité (Opus/AAC 256-320k, MP3 320k) : 600 - 799
    - Lossy standard (MP3 192-256k, AAC 128-192k) : 400 - 599
    - Lossy basse qualité (< 192k) : 100 - 399
    """
    fmt = (audio_format or "").strip().lower()
    br = bitrate or 0
    sr = sample_rate or 0

    score = 200

    # Format de base
    if fmt in {"flac", "alac", "wav", "aiff"}:
        score = 800
        if sr > 48000:
            score += 100
        if br > 1411:
            score += 50
    elif fmt in {"m4a", "aac", "ogg", "opus"}:
        score = 450
        if br >= 320:
            score += 250
        elif br >= 256:
            score += 200
        elif br >= 192:
            score += 100
    elif fmt == "mp3":
        score = 350
        if br >= 320:
            score += 300
        elif br >= 256:
            score += 200
        elif br >= 192:
            score += 100
        elif br >= 128:
            score += 50

    return min(max(score, 0), 1000)


@dataclass(slots=True)
class SourceRecord:
    """Représentation d'une source audio configurée."""

    id: int | None = None
    source_type: SourceType = SourceType.LOCAL
    name: str = ""
    path_or_uri: str = ""
    sync_mode: str = "manual"  # 'manual', 'startup', 'interval', 'realtime'
    sync_interval_minutes: int = 60
    sync_interval_seconds: int = 60
    created_at: str | None = None
    last_scanned_at: str | None = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> SourceRecord:
        keys = row.keys() if hasattr(row, "keys") else ()
        return cls(
            id=row["id"],
            source_type=SourceType(row["source_type"]),
            name=row["name"],
            path_or_uri=row["path_or_uri"],
            sync_mode=row["sync_mode"] if "sync_mode" in keys and row["sync_mode"] else "manual",
            sync_interval_minutes=int(row["sync_interval_minutes"])
            if "sync_interval_minutes" in keys and row["sync_interval_minutes"] is not None
            else 60,
            sync_interval_seconds=int(row["sync_interval_seconds"])
            if "sync_interval_seconds" in keys and row["sync_interval_seconds"] is not None
            else 60,
            created_at=str(row["created_at"]) if row["created_at"] is not None else None,
            last_scanned_at=str(row["last_scanned_at"]) if row["last_scanned_at"] is not None else None,
        )


@dataclass(slots=True)
class ActivityLogRecord:
    """Représentation d'une entrée du journal d'activité."""

    id: int | None = None
    timestamp: str | None = None
    level: str = "INFO"  # 'INFO', 'SUCCESS', 'WARNING', 'ERROR'
    category: str = "SYNC"  # 'SYNC', 'SCAN', 'LIBRARY', 'SYSTEM'
    source_name: str | None = None
    action: str = ""
    details: str | None = None
    items_added: int = 0
    items_updated: int = 0
    items_deleted: int = 0
    items_errors: int = 0
    i18n: str | None = None  # JSON clé + paramètres (voir core/activity_messages.py)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> ActivityLogRecord:
        keys = row.keys() if hasattr(row, "keys") else ()
        return cls(
            id=row["id"],
            timestamp=str(row["timestamp"]) if "timestamp" in keys and row["timestamp"] is not None else None,
            level=str(row["level"]) if "level" in keys and row["level"] else "INFO",
            category=str(row["category"]) if "category" in keys and row["category"] else "SYNC",
            source_name=str(row["source_name"]) if "source_name" in keys and row["source_name"] is not None else None,
            action=str(row["action"]) if "action" in keys and row["action"] else "",
            details=str(row["details"]) if "details" in keys and row["details"] is not None else None,
            items_added=int(row["items_added"]) if "items_added" in keys and row["items_added"] is not None else 0,
            items_updated=int(row["items_updated"])
            if "items_updated" in keys and row["items_updated"] is not None
            else 0,
            items_deleted=int(row["items_deleted"])
            if "items_deleted" in keys and row["items_deleted"] is not None
            else 0,
            items_errors=int(row["items_errors"]) if "items_errors" in keys and row["items_errors"] is not None else 0,
            i18n=str(row["i18n"]) if "i18n" in keys and row["i18n"] else None,
        )


@dataclass(slots=True)
class TrackRecord:
    """Représentation d'une piste audio."""

    source_ref: str
    source_type: SourceType = SourceType.LOCAL
    id: int | None = None
    source_id: int | None = None
    # Fichier & Chemins
    source_path: str | None = None
    file_name: str | None = None
    folder_path: str | None = None
    folder_name: str | None = None

    # Métadonnées audio
    title: str | None = None
    artist: str | None = None
    album_artist: str | None = None
    album: str | None = None
    genre: str | None = None
    year: int | None = None
    track_number: int | None = None
    disc_number: int | None = None

    # Propriétés techniques
    duration_seconds: float | None = None
    bitrate: int | None = None
    sample_rate: int | None = None
    channels: int | None = None
    format: str | None = None

    # Fichier & Empreintes
    file_size: int | None = None
    file_mtime: float | None = None
    file_hash: str | None = None
    audio_fingerprint: str | None = None
    isrc: str | None = None

    # Gestion des doublons, statut & score
    quality_score: int = 0
    duplicate_cluster_id: int | None = None
    metadata_extracted: bool = False

    # Dates
    created_at: str | None = None
    updated_at: str | None = None

    # Statut fichier manquant (ex: référencé dans une playlist mais absent du disque)
    is_missing: bool = False

    # Piste virtuelle d'une feuille CUE : portion [cue_start_ms, cue_end_ms[ du fichier source_path
    # (non stockée dans la table tracks ; cue_end_ms None = jusqu'à la fin du fichier)
    cue_start_ms: int | None = None
    cue_end_ms: int | None = None

    def __post_init__(self) -> None:
        if self.source_path:
            clean_path = str(self.source_path).replace("\\", "/")
            if not self.file_name:
                parts = clean_path.rsplit("/", 1)
                self.file_name = parts[-1] if parts else ""
            if not self.folder_path:
                parts = clean_path.rsplit("/", 1)
                self.folder_path = parts[0] if len(parts) > 1 else ""
            if not self.folder_name and self.folder_path:
                self.folder_name = self.folder_path.rsplit("/", 1)[-1] or self.folder_path

        if self.quality_score == 0 and (self.format or self.bitrate):
            self.quality_score = compute_quality_score(self.format, self.bitrate, self.sample_rate)

    @property
    def is_cue_segment(self) -> bool:
        """Vrai si la piste est une portion d'un fichier audio décrite par une feuille CUE."""
        return self.cue_start_ms is not None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> TrackRecord:
        keys = row.keys() if hasattr(row, "keys") else ()
        file_name = row["file_name"] if "file_name" in keys else None
        folder_path = row["folder_path"] if "folder_path" in keys else None
        folder_name = row["folder_name"] if "folder_name" in keys else None

        return cls(
            id=row["id"],
            source_ref=row["source_ref"],
            source_type=SourceType(row["source_type"]),
            source_id=row["source_id"],
            source_path=row["source_path"],
            file_name=file_name,
            folder_path=folder_path,
            folder_name=folder_name,
            title=row["title"],
            artist=row["artist"],
            album_artist=row["album_artist"],
            album=row["album"],
            genre=row["genre"],
            year=row["year"],
            track_number=row["track_number"],
            disc_number=row["disc_number"],
            duration_seconds=row["duration_seconds"],
            bitrate=row["bitrate"],
            sample_rate=row["sample_rate"],
            channels=row["channels"],
            format=row["format"],
            file_size=row["file_size"],
            file_mtime=row["file_mtime"],
            file_hash=row["file_hash"],
            audio_fingerprint=row["audio_fingerprint"],
            isrc=row["isrc"],
            quality_score=row["quality_score"] or 0,
            duplicate_cluster_id=row["duplicate_cluster_id"],
            metadata_extracted=bool(row["metadata_extracted"])
            if "metadata_extracted" in keys and row["metadata_extracted"] is not None
            else False,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            is_missing=bool(row["is_missing"]) if "is_missing" in keys and row["is_missing"] is not None else False,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convertit le TrackRecord en dictionnaire sérialisable."""
        return {
            "id": self.id,
            "source_ref": self.source_ref,
            "source_type": self.source_type.value if hasattr(self.source_type, "value") else str(self.source_type),
            "source_id": self.source_id,
            "source_path": self.source_path,
            "file_name": self.file_name,
            "folder_path": self.folder_path,
            "folder_name": self.folder_name,
            "title": self.title,
            "artist": self.artist,
            "album_artist": self.album_artist,
            "album": self.album,
            "genre": self.genre,
            "year": self.year,
            "track_number": self.track_number,
            "disc_number": self.disc_number,
            "duration_seconds": self.duration_seconds,
            "bitrate": self.bitrate,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "format": self.format,
            "file_size": self.file_size,
            "file_mtime": self.file_mtime,
            "file_hash": self.file_hash,
            "audio_fingerprint": self.audio_fingerprint,
            "isrc": self.isrc,
            "quality_score": self.quality_score,
            "duplicate_cluster_id": self.duplicate_cluster_id,
            "metadata_extracted": self.metadata_extracted,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_missing": self.is_missing,
            "cue_start_ms": self.cue_start_ms,
            "cue_end_ms": self.cue_end_ms,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TrackRecord:
        """Reconstruit un TrackRecord à partir d'un dictionnaire."""
        st = data.get("source_type", "local")
        try:
            source_type = SourceType(st)
        except Exception:
            source_type = SourceType.LOCAL
        return cls(
            id=data.get("id"),
            source_ref=data.get("source_ref", data.get("source_path", "")),
            source_type=source_type,
            source_id=data.get("source_id"),
            source_path=data.get("source_path"),
            file_name=data.get("file_name"),
            folder_path=data.get("folder_path"),
            folder_name=data.get("folder_name"),
            title=data.get("title"),
            artist=data.get("artist"),
            album_artist=data.get("album_artist"),
            album=data.get("album"),
            genre=data.get("genre"),
            year=data.get("year"),
            track_number=data.get("track_number"),
            disc_number=data.get("disc_number"),
            duration_seconds=data.get("duration_seconds"),
            bitrate=data.get("bitrate"),
            sample_rate=data.get("sample_rate"),
            channels=data.get("channels"),
            format=data.get("format"),
            file_size=data.get("file_size"),
            file_mtime=data.get("file_mtime"),
            file_hash=data.get("file_hash"),
            audio_fingerprint=data.get("audio_fingerprint"),
            isrc=data.get("isrc"),
            quality_score=data.get("quality_score", 0),
            duplicate_cluster_id=data.get("duplicate_cluster_id"),
            metadata_extracted=data.get("metadata_extracted", False),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            is_missing=bool(data.get("is_missing", False)),
            cue_start_ms=data.get("cue_start_ms"),
            cue_end_ms=data.get("cue_end_ms"),
        )


@dataclass(slots=True)
class PlaylistRecord:
    """Représentation d'une playlist indexée (M3U, PLS, XSPF, WPL)."""

    file_path: str
    file_name: str
    folder_path: str
    format: str
    id: int | None = None
    source_id: int | None = None
    track_count: int = 0
    file_mtime: float = 0.0
    file_size: int = 0
    source_type: SourceType = SourceType.LOCAL
    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> PlaylistRecord:
        keys = row.keys() if hasattr(row, "keys") else ()
        st = row["source_type"] if "source_type" in keys and row["source_type"] else "local"
        try:
            source_type = SourceType(st)
        except Exception:
            source_type = SourceType.LOCAL
        return cls(
            id=row["id"],
            source_id=row["source_id"] if "source_id" in keys else None,
            file_path=row["file_path"] if "file_path" in keys else "",
            file_name=row["file_name"] if "file_name" in keys else (row["name"] if "name" in keys else ""),
            folder_path=row["folder_path"] if "folder_path" in keys else "",
            format=row["format"] if "format" in keys else "",
            track_count=int(row["track_count"]) if "track_count" in keys and row["track_count"] is not None else 0,
            file_mtime=float(row["file_mtime"]) if "file_mtime" in keys and row["file_mtime"] is not None else 0.0,
            file_size=int(row["file_size"]) if "file_size" in keys and row["file_size"] is not None else 0,
            source_type=source_type,
            created_at=str(row["created_at"]) if "created_at" in keys and row["created_at"] is not None else None,
            updated_at=str(row["updated_at"]) if "updated_at" in keys and row["updated_at"] is not None else None,
        )

    @property
    def name(self) -> str:
        """Alias pratique pour le nom de la playlist."""
        return self.file_name


@dataclass(slots=True)
class PlaylistEntryRecord:
    """Représentation d'un élément contenu dans une playlist."""

    position: int
    raw_path: str
    resolved_path: str
    id: int | None = None
    playlist_id: int | None = None
    track_id: int | None = None
    title: str | None = None
    artist: str | None = None
    duration_seconds: float | None = None
    is_missing: bool = False
    start_ms: int | None = None  # CUE : début de la piste dans le fichier audio
    end_ms: int | None = None  # CUE : fin de la piste (None = fin du fichier)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> PlaylistEntryRecord:
        keys = row.keys() if hasattr(row, "keys") else ()
        return cls(
            id=row["id"],
            playlist_id=row["playlist_id"] if "playlist_id" in keys else None,
            position=int(row["position"]) if "position" in keys and row["position"] is not None else 1,
            raw_path=row["raw_path"] if "raw_path" in keys else "",
            resolved_path=row["resolved_path"] if "resolved_path" in keys else "",
            track_id=row["track_id"] if "track_id" in keys else None,
            title=row["title"] if "title" in keys else None,
            artist=row["artist"] if "artist" in keys else None,
            duration_seconds=float(row["duration_seconds"])
            if "duration_seconds" in keys and row["duration_seconds"] is not None
            else None,
            is_missing=bool(row["is_missing"]) if "is_missing" in keys and row["is_missing"] is not None else False,
            start_ms=int(row["start_ms"]) if "start_ms" in keys and row["start_ms"] is not None else None,
            end_ms=int(row["end_ms"]) if "end_ms" in keys and row["end_ms"] is not None else None,
        )
