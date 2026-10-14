"""Module d'extraction et d'écriture des métadonnées audio via Mutagen.

Prend en charge MP3 (ID3v1/v2), FLAC, M4A/AAC, OGG Vorbis/Opus, WAV, WMA, etc.
Garantit une extraction robuste même sur des fichiers corrompus ou sans tags.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
from typing import Any, Optional, Sequence

import mutagen
from mutagen.flac import FLAC
from mutagen.id3 import (
    ID3,
    ID3NoHeaderError,
    TALB,
    TCON,
    TDRC,
    TIT2,
    TPE1,
    TPE2,
    TPOS,
    TRCK,
    TSRC,
)
from mutagen.mp4 import MP4, MP4Tags

from amso.core.database import SourceType, TrackRecord, compute_quality_score

# Extensions audio prises en charge
SUPPORTED_AUDIO_EXTENSIONS: frozenset[str] = frozenset({
    ".mp3",
    ".flac",
    ".m4a",
    ".aac",
    ".ogg",
    ".oga",
    ".opus",
    ".wav",
    ".wave",
    ".wma",
    ".aiff",
    ".aif",
    ".alac",
    ".ape",
})


def is_audio_file(file_path: str | Path) -> bool:
    """Vérifie si le fichier possède une extension audio prise en charge."""
    return Path(file_path).suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS


def compute_file_hash(file_path: str | Path, chunk_size: int = 65536) -> str:
    """Calcule une empreinte rapide et robuste adaptée aux disques locaux et partages réseau."""
    sha256 = hashlib.sha256()
    size = os.path.getsize(file_path)
    sha256.update(str(size).encode("ascii"))

    threshold = 4 * 1024 * 1024  # 4 Mo
    with open(file_path, "rb") as f:
        if size <= threshold:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        else:
            # Pour les gros fichiers (FLAC Hi-Res, WAV, etc.) : hachage début + fin
            sha256.update(f.read(1024 * 1024))
            f.seek(max(0, size - (1024 * 1024)))
            sha256.update(f.read(1024 * 1024))
    return sha256.hexdigest()


def _clean_str(val: Any) -> Optional[str]:
    """Nettoie une chaîne de caractères ou retourne None si vide."""
    if val is None:
        return None
    if isinstance(val, (list, tuple)):
        val = val[0] if val else None
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def _parse_int_pair(val: Any) -> Optional[int]:
    """Extrait un numéro entier à partir de formats divers (ex: 5, '05', '5/12', (5, 12))."""
    if val is None:
        return None
    if isinstance(val, (list, tuple)):
        val = val[0] if val else None
    if val is None:
        return None

    if isinstance(val, int):
        return val

    s = str(val).strip()
    match = re.match(r"^(\d+)", s)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def _parse_year(val: Any) -> Optional[int]:
    """Extrait une année à 4 chiffres à partir d'une chaîne ou date (ex: '2023-05-14', 2023)."""
    if val is None:
        return None
    if isinstance(val, (list, tuple)):
        val = val[0] if val else None
    if val is None:
        return None

    if isinstance(val, int) and 1900 <= val <= 2100:
        return val

    s = str(val).strip()
    match = re.search(r"\b(19\d\d|20\d\d)\b", s)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def _get_tag_value(tags: Any, keys: Sequence[str]) -> Optional[str]:
    """Recherche la première valeur non nulle parmi une liste de clés de tags."""
    if not tags:
        return None
    for k in keys:
        try:
            if k in tags:
                val = tags[k]
                res = _clean_str(val)
                if res:
                    return res
        except (KeyError, ValueError, TypeError):
            continue
    return None


def extract_metadata(
    file_path: str | Path,
    source_id: Optional[int] = None,
    source_type: SourceType = SourceType.LOCAL,
    compute_hash: bool = True,
) -> TrackRecord:
    """Extrait l'ensemble des métadonnées d'un fichier audio local.

    Ne lève jamais d'exception fatale : en cas d'erreur de lecture de tags,
    le fichier est tout de même indexé avec son nom et ses propriétés physiques.
    """
    path = Path(file_path).resolve()
    source_ref = path.as_posix()
    fmt = path.suffix.lstrip(".").lower()

    # Métadonnées système
    stat = path.stat()
    file_size = stat.st_size
    file_mtime = stat.st_mtime

    file_hash: Optional[str] = None
    if compute_hash:
        try:
            file_hash = compute_file_hash(path)
        except (OSError, PermissionError):
            file_hash = None

    # Valeurs par défaut
    title = path.stem
    artist: Optional[str] = None
    album_artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    track_number: Optional[int] = None
    disc_number: Optional[int] = None
    duration_seconds: Optional[float] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    isrc: Optional[str] = None

    # Analyse Mutagen
    try:
        audio = mutagen.File(str(path))
    except Exception:
        audio = None

    tags = None
    if audio is not None:
        # Propriétés audio physiques
        if hasattr(audio, "info") and audio.info is not None:
            duration_seconds = round(float(getattr(audio.info, "length", 0.0)), 2)
            raw_br = getattr(audio.info, "bitrate", 0)
            if raw_br:
                bitrate = raw_br // 1000 if raw_br > 5000 else raw_br
            elif duration_seconds and duration_seconds > 0:
                # Estimation pour WAV / AIFF sans champ bitrate explicite
                bitrate = int((file_size * 8) / (duration_seconds * 1000))

            sample_rate = getattr(audio.info, "sample_rate", None)
            channels = getattr(audio.info, "channels", None)

        tags = getattr(audio, "tags", None)
    else:
        # Fallback pour lire les tags si les trames audio sont incomplètes ou corrompues
        if fmt in {"mp3", "aac"}:
            try:
                tags = ID3(str(path))
            except Exception:
                tags = None
        elif fmt == "flac":
            try:
                tags = FLAC(str(path))
            except Exception:
                tags = None

    if tags is not None:
        # Titre
        t = _get_tag_value(tags, ["TIT2", "title", "TITLE", "\xa9nam", "Title"])
        if t:
            title = t

        # Artiste
        artist = _get_tag_value(tags, ["TPE1", "artist", "ARTIST", "\xa9ART", "Author"])

        # Artiste de l'album
        album_artist = _get_tag_value(tags, ["TPE2", "albumartist", "ALBUMARTIST", "album_artist", "aART", "WM/AlbumArtist"])

        # Album
        album = _get_tag_value(tags, ["TALB", "album", "ALBUM", "\xa9alb", "WM/AlbumTitle"])

        # Genre
        genre = _get_tag_value(tags, ["TCON", "genre", "GENRE", "\xa9gen", "WM/Genre"])

        # ISRC
        isrc = _get_tag_value(tags, ["TSRC", "isrc", "ISRC"])

        # Année / Date
        y_val = _get_tag_value(tags, ["TDRC", "TYER", "date", "DATE", "year", "YEAR", "\xa9day", "WM/Year"])
        year = _parse_year(y_val)

        # Numéro de piste & Disque
        if fmt in {"m4a", "mp4"}:
            try:
                trkn_val = tags.get("\xa9trkn") or tags.get("trkn")
                if isinstance(trkn_val, (list, tuple)) and trkn_val and isinstance(trkn_val[0], tuple):
                    track_number = trkn_val[0][0]
                else:
                    track_number = _parse_int_pair(trkn_val)
            except Exception:
                pass

            try:
                disk_val = tags.get("\xa9disk") or tags.get("disk")
                if isinstance(disk_val, (list, tuple)) and disk_val and isinstance(disk_val[0], tuple):
                    disc_number = disk_val[0][0]
                else:
                    disc_number = _parse_int_pair(disk_val)
            except Exception:
                pass
        else:
            tr_val = _get_tag_value(tags, ["TRCK", "tracknumber", "TRACKNUMBER", "WM/TrackNumber"])
            track_number = _parse_int_pair(tr_val)

            disc_val = _get_tag_value(tags, ["TPOS", "discnumber", "DISCNUMBER"])
            disc_number = _parse_int_pair(disc_val)

    quality_score = compute_quality_score(fmt, bitrate, sample_rate)

    return TrackRecord(
        source_ref=source_ref,
        source_type=source_type,
        source_id=source_id,
        source_path=str(path),
        title=title,
        artist=artist,
        album_artist=album_artist,
        album=album,
        genre=genre,
        year=year,
        track_number=track_number,
        disc_number=disc_number,
        duration_seconds=duration_seconds,
        bitrate=bitrate,
        sample_rate=sample_rate,
        channels=channels,
        format=fmt,
        file_size=file_size,
        file_mtime=file_mtime,
        file_hash=file_hash,
        isrc=isrc,
        quality_score=quality_score,
    )


def save_metadata(
    file_path: str | Path,
    *,
    title: Optional[str] = None,
    artist: Optional[str] = None,
    album: Optional[str] = None,
    album_artist: Optional[str] = None,
    genre: Optional[str] = None,
    year: Optional[int] = None,
    track_number: Optional[int] = None,
    disc_number: Optional[int] = None,
) -> bool:
    """Enregistre les métadonnées dans le fichier audio (MP3, FLAC, M4A).

    Retourne True en cas de succès, False en cas d'échec ou format non modifiable.
    """
    path = Path(file_path).resolve()
    fmt = path.suffix.lower()

    try:
        if fmt == ".mp3":
            try:
                tags = ID3(str(path))
            except ID3NoHeaderError:
                tags = ID3()

            if title is not None:
                tags["TIT2"] = TIT2(encoding=3, text=title)
            if artist is not None:
                tags["TPE1"] = TPE1(encoding=3, text=artist)
            if album is not None:
                tags["TALB"] = TALB(encoding=3, text=album)
            if album_artist is not None:
                tags["TPE2"] = TPE2(encoding=3, text=album_artist)
            if genre is not None:
                tags["TCON"] = TCON(encoding=3, text=genre)
            if year is not None:
                tags["TDRC"] = TDRC(encoding=3, text=str(year))
            if track_number is not None:
                tags["TRCK"] = TRCK(encoding=3, text=str(track_number))
            if disc_number is not None:
                tags["TPOS"] = TPOS(encoding=3, text=str(disc_number))

            tags.save(str(path))
            return True

        elif fmt in {".flac", ".ogg", ".opus"}:
            audio = mutagen.File(str(path))
            if audio is None:
                return False

            if title is not None:
                audio["title"] = [title]
            if artist is not None:
                audio["artist"] = [artist]
            if album is not None:
                audio["album"] = [album]
            if album_artist is not None:
                audio["albumartist"] = [album_artist]
            if genre is not None:
                audio["genre"] = [genre]
            if year is not None:
                audio["date"] = [str(year)]
            if track_number is not None:
                audio["tracknumber"] = [str(track_number)]
            if disc_number is not None:
                audio["discnumber"] = [str(disc_number)]

            audio.save()
            return True

        elif fmt in {".m4a", ".mp4"}:
            mp4 = MP4(str(path))
            if mp4.tags is None:
                mp4.add_tags()

            if title is not None:
                mp4.tags["\xa9nam"] = [title]
            if artist is not None:
                mp4.tags["\xa9ART"] = [artist]
            if album is not None:
                mp4.tags["\xa9alb"] = [album]
            if album_artist is not None:
                mp4.tags["aART"] = [album_artist]
            if genre is not None:
                mp4.tags["\xa9gen"] = [genre]
            if year is not None:
                mp4.tags["\xa9day"] = [str(year)]
            if track_number is not None:
                mp4.tags["trkn"] = [(track_number, 0)]
            if disc_number is not None:
                mp4.tags["disk"] = [(disc_number, 0)]

            mp4.save()
            return True

        return False
    except Exception:
        return False
