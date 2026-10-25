"""Analyseur de feuilles CUE (.cue) pour AMSO.

Une feuille CUE décrit des pistes « virtuelles » découpées dans un fichier audio (ou plusieurs) :
chaque `TRACK` commence à son `INDEX 01` (minutes:secondes:images, 75 images par seconde) et se termine
au début de la piste suivante du même fichier ; la dernière piste va jusqu'à la fin du fichier.
Chaque piste est retournée comme une `ParsedPlaylistEntry` portant `start_ms` / `end_ms`.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from amso.core.metadata import SUPPORTED_AUDIO_EXTENSIONS
from amso.core.playlist_parser import ParsedPlaylistEntry

FRAMES_PER_SECOND = 75

_FILE_RE = re.compile(r'^FILE\s+(?:"([^"]*)"|(\S+))', re.IGNORECASE)
_TRACK_RE = re.compile(r"^TRACK\s+(\d+)\s+(\S+)", re.IGNORECASE)
_INDEX_RE = re.compile(r"^INDEX\s+(\d+)\s+(\d+):(\d{1,2}):(\d{1,2})", re.IGNORECASE)
_TEXT_RE = re.compile(r'^(TITLE|PERFORMER)\s+(?:"([^"]*)"|(.+))$', re.IGNORECASE)


def cue_time_to_ms(minutes: int, seconds: int, frames: int) -> int:
    """Convertit un temps CUE (MM:SS:FF, 75 images/s) en millisecondes."""
    return (minutes * 60 + seconds) * 1000 + round(frames * 1000 / FRAMES_PER_SECOND)


def resolve_cue_audio_file(raw_path: str, cue_dir: Path) -> tuple[str, bool]:
    """Résout le fichier audio référencé par une ligne FILE ; retourne (chemin, est_manquant).

    Le chemin n'est pas « résolu » par le système (un lecteur réseau mappé W: reste W: au lieu d'un chemin UNC),
    afin de coïncider avec les chemins indexés par le scanner. Si la cible n'existe pas ou n'est pas un fichier audio
    (ex. FILE qui pointe vers le .cue lui-même), repli sur le fichier audio du même nom dans le dossier, puis sur
    l'unique fichier audio du dossier.
    """
    clean = raw_path.strip().strip('"')
    if clean.lower().startswith(("http://", "https://", "rtsp://", "mms://")):
        return clean, False
    target = Path(clean)
    direct = Path(os.path.normpath(target if target.is_absolute() else cue_dir / target))
    if direct.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS and direct.is_file():
        return direct.as_posix(), False
    try:
        audio = sorted(p for p in cue_dir.iterdir() if p.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS)
    except OSError:
        audio = []
    same_stem = [p for p in audio if p.stem.lower() == target.stem.lower()]
    candidate = same_stem[0] if same_stem else (audio[0] if len(audio) == 1 else None)
    if candidate is not None:
        return Path(os.path.normpath(candidate)).as_posix(), False
    return direct.as_posix(), True


@dataclass(slots=True)
class _TrackDraft:
    """Piste en cours de lecture dans la feuille CUE."""

    number: int
    is_audio: bool
    title: str = ""
    artist: str = ""


def parse_cue_content(content: str, cue_dir: Path) -> list[ParsedPlaylistEntry]:
    """Analyse le texte d'une feuille CUE et retourne ses pistes (positions 1..n, début/fin en ms)."""
    sheet_performer = ""
    files: list[tuple[str, str, bool]] = []  # (chemin brut, chemin résolu, manquant)
    tracks: list[tuple[int, int, str, str, int]] = []  # (index du fichier, numéro, titre, artiste, début ms)
    current: _TrackDraft | None = None

    for raw_line in content.splitlines():
        line = raw_line.strip().lstrip("﻿")
        if not line or line.upper().startswith("REM"):
            continue
        if m := _FILE_RE.match(line):
            raw = m.group(1) if m.group(1) is not None else m.group(2)
            files.append((raw, *resolve_cue_audio_file(raw, cue_dir)))
            current = None
        elif m := _TRACK_RE.match(line):
            current = _TrackDraft(number=int(m.group(1)), is_audio=m.group(2).upper() == "AUDIO")
        elif m := _INDEX_RE.match(line):
            if current is not None and current.is_audio and int(m.group(1)) == 1 and files:
                start = cue_time_to_ms(int(m.group(2)), int(m.group(3)), int(m.group(4)))
                tracks.append((len(files) - 1, current.number, current.title, current.artist, start))
        elif m := _TEXT_RE.match(line):
            value = (m.group(2) if m.group(2) is not None else m.group(3)).strip()
            is_title = m.group(1).upper() == "TITLE"
            if current is None:
                sheet_performer = sheet_performer if is_title else value
            elif is_title:
                current.title = value
            else:
                current.artist = value
    return _build_entries(tracks, files, sheet_performer)


def _build_entries(
    tracks: list[tuple[int, int, str, str, int]], files: list[tuple[str, str, bool]], sheet_performer: str
) -> list[ParsedPlaylistEntry]:
    """Assemble les entrées : la fin d'une piste est le début de la suivante dans le même fichier."""
    entries: list[ParsedPlaylistEntry] = []
    for pos, (f_idx, number, title, artist, start) in enumerate(tracks, start=1):
        nxt = tracks[pos] if pos < len(tracks) else None
        end = nxt[4] if nxt is not None and nxt[0] == f_idx and nxt[4] > start else None
        raw, path, missing = files[f_idx]
        entries.append(
            ParsedPlaylistEntry(
                position=pos,
                raw_path=raw,
                resolved_path=path,
                title=title or f"Piste {number:02d}",
                artist=artist or sheet_performer or None,
                duration_seconds=(end - start) / 1000.0 if end is not None else None,
                is_missing=missing,
                start_ms=start,
                end_ms=end,
            )
        )
    return entries
