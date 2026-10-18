"""Analyseur et extracteur de formats de playlists pour AMSO.

Prend en charge les formats :
- M3U et M3U8 (texte simple ou UTF-8 avec directives #EXTINF)
- PLS (format INI standard)
- XSPF (XML Shareable Playlist Format)
- WPL (Windows Media Player XML)
Garantit la résolution des chemins relatifs par rapport au dossier de la playlist
et la détection des fichiers manquants.
"""

from __future__ import annotations

import configparser
import os
import re
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

# Formats de playlists pris en charge
SUPPORTED_PLAYLIST_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".m3u",
        ".m3u8",
        ".pls",
        ".xspf",
        ".wpl",
    }
)


@dataclass(slots=True)
class ParsedPlaylistEntry:
    """Représentation d'un élément contenu dans une playlist."""

    position: int
    raw_path: str
    resolved_path: str
    title: str | None = None
    artist: str | None = None
    duration_seconds: float | None = None
    is_missing: bool = False


def resolve_playlist_path(raw_path: str, playlist_dir: Path) -> tuple[str, bool]:
    """Résout un chemin de fichier (relatif ou absolu) par rapport au dossier de la playlist.

    Retourne : (chemin_résolu_normalisé, est_manquant).
    """
    clean_p = raw_path.strip().strip('"').strip("'")
    if not clean_p:
        return "", True

    # Gestion des URLs de type file://
    if clean_p.lower().startswith("file://"):
        parsed_url = urllib.parse.urlparse(clean_p)
        if parsed_url.netloc:
            # Chemin UNC réseau : file://server/share/file -> //server/share/file
            clean_p = urllib.parse.unquote(f"//{parsed_url.netloc}{parsed_url.path}")
        else:
            url_path = urllib.parse.unquote(parsed_url.path)
            # Sous Windows, file:///D:/Musique/ -> /D:/Musique/ -> D:/Musique/
            if os.name == "nt" and len(url_path) >= 3 and url_path[0] == "/" and url_path[2] == ":":
                url_path = url_path[1:]
            clean_p = url_path

    # Si c'est une URL de flux distant (http://, https://, rtsp://)
    if clean_p.lower().startswith(("http://", "https://", "rtsp://", "mms://")):
        return clean_p, False

    p = Path(clean_p)
    if p.is_absolute():
        resolved = p.resolve()
    else:
        resolved = (playlist_dir / p).resolve()

    resolved_str = str(resolved).replace("\\", "/")
    is_missing = not resolved.exists()
    return resolved_str, is_missing


def parse_m3u_content(content: str, playlist_dir: Path) -> list[ParsedPlaylistEntry]:
    """Parse le contenu d'un fichier M3U / M3U8."""
    entries: list[ParsedPlaylistEntry] = []
    lines = [line.strip() for line in content.splitlines()]

    current_duration: float | None = None
    current_title: str | None = None
    current_artist: str | None = None

    pos = 1
    for line in lines:
        if not line:
            continue

        if line.startswith("#EXTINF:"):
            # Exemple : #EXTINF:245,Artist - Title ou #EXTINF:180,Title
            info = line[8:].strip()
            parts = info.split(",", 1)
            try:
                dur_str = parts[0].strip()
                # Peut être négatif ou flottant
                dur_val = float(dur_str)
                current_duration = dur_val if dur_val > 0 else None
            except ValueError:
                current_duration = None

            if len(parts) > 1:
                label = parts[1].strip()
                if " - " in label:
                    art, tit = label.split(" - ", 1)
                    current_artist = art.strip() or None
                    current_title = tit.strip() or None
                else:
                    current_title = label or None
                    current_artist = None
            continue

        if line.startswith("#"):
            # Autre directive / commentaire M3U
            continue

        # Ligne de chemin de fichier
        resolved_path, is_missing = resolve_playlist_path(line, playlist_dir)
        entries.append(
            ParsedPlaylistEntry(
                position=pos,
                raw_path=line,
                resolved_path=resolved_path,
                title=current_title,
                artist=current_artist,
                duration_seconds=current_duration,
                is_missing=is_missing,
            )
        )
        pos += 1
        current_duration = None
        current_title = None
        current_artist = None

    return entries


def parse_pls_content(content: str, playlist_dir: Path) -> list[ParsedPlaylistEntry]:
    """Parse le contenu d'un fichier PLS (format type INI)."""
    entries: list[ParsedPlaylistEntry] = []
    parser = configparser.ConfigParser(interpolation=None)
    try:
        parser.read_string(content)
    except Exception:
        # Fallback analyse ligne par ligne si non-conforme
        pass

    section_name = None
    for s in parser.sections():
        if s.lower() == "playlist":
            section_name = s
            break

    files_dict: dict[int, str] = {}
    titles_dict: dict[int, str] = {}
    lengths_dict: dict[int, float] = {}

    if section_name:
        for key, val in parser.items(section_name):
            k = key.lower()
            m_file = re.match(r"^file(\d+)$", k)
            if m_file:
                idx = int(m_file.group(1))
                files_dict[idx] = val.strip()
                continue
            m_title = re.match(r"^title(\d+)$", k)
            if m_title:
                idx = int(m_title.group(1))
                titles_dict[idx] = val.strip()
                continue
            m_len = re.match(r"^length(\d+)$", k)
            if m_len:
                idx = int(m_len.group(1))
                try:
                    l_val = float(val.strip())
                    if l_val > 0:
                        lengths_dict[idx] = l_val
                except ValueError:
                    pass
    else:
        # Analyse manuelle de secours
        for line in content.splitlines():
            line = line.strip()
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip().lower()
                v = v.strip()
                m_file = re.match(r"^file(\d+)$", k)
                if m_file:
                    files_dict[int(m_file.group(1))] = v
                m_title = re.match(r"^title(\d+)$", k)
                if m_title:
                    titles_dict[int(m_title.group(1))] = v
                m_len = re.match(r"^length(\d+)$", k)
                if m_len:
                    try:
                        lengths_dict[int(m_len.group(1))] = float(v)
                    except ValueError:
                        pass

    for pos, idx in enumerate(sorted(files_dict.keys()), start=1):
        raw_path = files_dict[idx]
        resolved_path, is_missing = resolve_playlist_path(raw_path, playlist_dir)
        raw_title = titles_dict.get(idx)
        art, tit = None, raw_title
        if raw_title and " - " in raw_title:
            p_art, p_tit = raw_title.split(" - ", 1)
            art = p_art.strip() or None
            tit = p_tit.strip() or None

        entries.append(
            ParsedPlaylistEntry(
                position=pos,
                raw_path=raw_path,
                resolved_path=resolved_path,
                title=tit,
                artist=art,
                duration_seconds=lengths_dict.get(idx),
                is_missing=is_missing,
            )
        )

    return entries


def parse_xspf_content(content: str, playlist_dir: Path) -> list[ParsedPlaylistEntry]:
    """Parse le contenu d'un fichier XSPF (XML Shareable Playlist Format)."""
    entries: list[ParsedPlaylistEntry] = []
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return entries

    # Retirer les namespaces éventuels pour un parcours simplifié
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]

    pos = 1
    for track_elem in root.iter("track"):
        loc_elem = track_elem.find("location")
        if loc_elem is None or not loc_elem.text:
            continue

        raw_path = loc_elem.text.strip()
        resolved_path, is_missing = resolve_playlist_path(raw_path, playlist_dir)

        tit_elem = track_elem.find("title")
        title = tit_elem.text.strip() if tit_elem is not None and tit_elem.text else None

        art_elem = track_elem.find("creator")
        artist = art_elem.text.strip() if art_elem is not None and art_elem.text else None

        dur_elem = track_elem.find("duration")
        duration: float | None = None
        if dur_elem is not None and dur_elem.text:
            try:
                # XSPF stocke la durée en millisecondes
                duration = float(dur_elem.text.strip()) / 1000.0
            except ValueError:
                duration = None

        entries.append(
            ParsedPlaylistEntry(
                position=pos,
                raw_path=raw_path,
                resolved_path=resolved_path,
                title=title,
                artist=artist,
                duration_seconds=duration,
                is_missing=is_missing,
            )
        )
        pos += 1

    return entries


def parse_wpl_content(content: str, playlist_dir: Path) -> list[ParsedPlaylistEntry]:
    """Parse le contenu d'un fichier WPL (Windows Media Player XML Playlist)."""
    entries: list[ParsedPlaylistEntry] = []
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return entries

    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]

    pos = 1
    for media_elem in root.iter("media"):
        src = media_elem.get("src")
        if not src:
            continue

        raw_path = src.strip()
        resolved_path, is_missing = resolve_playlist_path(raw_path, playlist_dir)

        title = media_elem.get("trackTitle")
        artist = media_elem.get("trackArtist")

        entries.append(
            ParsedPlaylistEntry(
                position=pos,
                raw_path=raw_path,
                resolved_path=resolved_path,
                title=title,
                artist=artist,
                duration_seconds=None,
                is_missing=is_missing,
            )
        )
        pos += 1

    return entries


def parse_playlist_file(file_path: str | Path) -> list[ParsedPlaylistEntry]:
    """Charge et analyse n'importe quel fichier de playlist pris en charge."""
    p = Path(file_path)
    if not p.is_file():
        return []

    ext = p.suffix.lower()
    if ext not in SUPPORTED_PLAYLIST_EXTENSIONS:
        return []

    playlist_dir = p.parent

    # Lecture sécurisée avec repli d'encodage (UTF-8, UTF-8-sig, CP1252, Latin-1)
    content = ""
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            with open(p, encoding=enc, errors="strict") as f:
                content = f.read()
            break
        except (UnicodeDecodeError, OSError):
            continue

    if not content:
        try:
            with open(p, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except OSError:
            return []

    if ext in (".m3u", ".m3u8"):
        return parse_m3u_content(content, playlist_dir)
    elif ext == ".pls":
        return parse_pls_content(content, playlist_dir)
    elif ext == ".xspf":
        return parse_xspf_content(content, playlist_dir)
    elif ext == ".wpl":
        return parse_wpl_content(content, playlist_dir)

    return []
