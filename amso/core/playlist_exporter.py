"""Exporteur de playlists AMSO vers les formats M3U8, M3U, PLS, XSPF et WPL."""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from collections.abc import Sequence
from pathlib import Path

from amso.core.database import TrackRecord

EXPORTABLE_PLAYLIST_EXTENSIONS: tuple[str, ...] = (".m3u8", ".m3u", ".pls", ".xspf", ".wpl")


def _format_track_path(track: TrackRecord, playlist_dir: Path, relative_paths: bool) -> str:
    """Retourne le chemin (relatif si possible, sinon absolu) normalisé pour une piste."""
    raw = (track.source_path or track.source_ref or "").strip()
    if not raw:
        return ""
    if raw.lower().startswith(("http://", "https://", "rtsp://", "mms://")):
        return raw
    if relative_paths:
        try:
            rel = os.path.relpath(os.path.normpath(raw), os.path.normpath(str(playlist_dir)))
            return rel.replace("\\", "/")
        except ValueError:
            pass
    return raw.replace("\\", "/")


def _track_label(track: TrackRecord) -> str:
    """Construit le libellé « Artiste - Titre » ou le nom de fichier en repli."""
    title = (track.title or track.file_name or "Unknown").strip()
    artist = (track.artist or "").strip()
    return f"{artist} - {title}" if artist else title


def _duration_int(track: TrackRecord) -> int:
    if track.duration_seconds and track.duration_seconds > 0:
        return int(round(track.duration_seconds))
    return -1


def _build_m3u(tracks: Sequence[TrackRecord], playlist_dir: Path, relative_paths: bool) -> str:
    lines = ["#EXTM3U"]
    for trk in tracks:
        path_str = _format_track_path(trk, playlist_dir, relative_paths)
        if not path_str:
            continue
        lines.append(f"#EXTINF:{_duration_int(trk)},{_track_label(trk)}")
        lines.append(path_str)
    return "\n".join(lines) + "\n"


def _build_pls(tracks: Sequence[TrackRecord], playlist_dir: Path, relative_paths: bool) -> str:
    lines = ["[playlist]"]
    count = 0
    for trk in tracks:
        path_str = _format_track_path(trk, playlist_dir, relative_paths)
        if not path_str:
            continue
        count += 1
        lines.append(f"File{count}={path_str}")
        lines.append(f"Title{count}={_track_label(trk)}")
        lines.append(f"Length{count}={_duration_int(trk)}")
    lines.append(f"NumberOfEntries={count}")
    lines.append("Version=2")
    return "\n".join(lines) + "\n"


def _build_xspf(tracks: Sequence[TrackRecord], playlist_dir: Path, relative_paths: bool, title: str) -> str:
    root = ET.Element("playlist", version="1", xmlns="http://xspf.org/ns/0/")
    ET.SubElement(root, "title").text = title
    track_list = ET.SubElement(root, "trackList")
    for trk in tracks:
        path_str = _format_track_path(trk, playlist_dir, relative_paths)
        if not path_str:
            continue
        node = ET.SubElement(track_list, "track")
        if path_str.lower().startswith(("http://", "https://", "rtsp://", "mms://")):
            ET.SubElement(node, "location").text = path_str
        elif Path(path_str).is_absolute():
            ET.SubElement(node, "location").text = Path(path_str).as_uri()
        else:
            ET.SubElement(node, "location").text = path_str
        if trk.title:
            ET.SubElement(node, "title").text = trk.title
        if trk.artist:
            ET.SubElement(node, "creator").text = trk.artist
        if trk.album:
            ET.SubElement(node, "album").text = trk.album
        if trk.duration_seconds and trk.duration_seconds > 0:
            ET.SubElement(node, "duration").text = str(int(round(trk.duration_seconds * 1000)))
    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"


def _build_wpl(tracks: Sequence[TrackRecord], playlist_dir: Path, relative_paths: bool, title: str) -> str:
    smil = ET.Element("smil")
    head = ET.SubElement(smil, "head")
    ET.SubElement(head, "title").text = title
    body = ET.SubElement(smil, "body")
    seq = ET.SubElement(body, "seq")
    for trk in tracks:
        path_str = _format_track_path(trk, playlist_dir, relative_paths)
        if not path_str:
            continue
        ET.SubElement(seq, "media", src=path_str)
    ET.indent(smil, space="  ")
    return '<?wpl version="1.0"?>\n' + ET.tostring(smil, encoding="unicode") + "\n"


def export_playlist(
    tracks: Sequence[TrackRecord],
    destination: Path | str,
    *,
    relative_paths: bool = True,
) -> Path:
    """Exporte une liste de pistes vers un fichier playlist (.m3u8, .m3u, .pls, .xspf, .wpl)."""
    if not tracks:
        raise ValueError("Cannot export an empty playlist")

    dest = Path(destination)
    ext = dest.suffix.lower()
    if not ext:
        ext = ".m3u8"
        dest = dest.with_suffix(ext)
    if ext not in EXPORTABLE_PLAYLIST_EXTENSIONS:
        raise ValueError(f"Unsupported playlist format: {ext}")

    dest.parent.mkdir(parents=True, exist_ok=True)
    title = dest.stem or "AMSO Playlist"

    if ext in {".m3u8", ".m3u"}:
        content = _build_m3u(tracks, dest.parent, relative_paths)
    elif ext == ".pls":
        content = _build_pls(tracks, dest.parent, relative_paths)
    elif ext == ".xspf":
        content = _build_xspf(tracks, dest.parent, relative_paths, title)
    else:
        content = _build_wpl(tracks, dest.parent, relative_paths, title)

    tmp_path = dest.with_suffix(f"{ext}.tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(dest)
    return dest


def index_exported_playlist_in_db(
    db: object,
    dest: Path,
    *,
    precomputed_entries: Sequence[object] | None = None,
) -> bool:
    """Indexe immédiatement la playlist exportée si elle se trouve dans une source connue."""
    from amso.core.database import DatabaseManager
    from amso.core.playlist_parser import ParsedPlaylistEntry, parse_playlist_file

    if not isinstance(db, DatabaseManager):
        return False
    norm_dest = os.path.normcase(os.path.normpath(str(dest)))
    matched_source_id: int | None = None
    for src in db.get_sources():
        if not src.path_or_uri or src.id is None:
            continue
        norm_root = os.path.normcase(os.path.normpath(src.path_or_uri))
        if norm_dest == norm_root or norm_dest.startswith(norm_root + os.sep):
            matched_source_id = src.id
            break
    if matched_source_id is None:
        return False

    if precomputed_entries is not None:
        entries = [e for e in precomputed_entries if isinstance(e, ParsedPlaylistEntry)]
    else:
        entries = parse_playlist_file(dest)
    stat = dest.stat()
    db.upsert_playlist(
        source_id=matched_source_id,
        file_path=str(dest),
        file_name=dest.name,
        folder_path=str(dest.parent),
        format_str=dest.suffix.lstrip(".").lower(),
        file_mtime=stat.st_mtime,
        file_size=stat.st_size,
        entries=entries,
    )
    db.link_playlist_entries_to_tracks(matched_source_id)
    return True


def entries_to_track_records(entries: Sequence[object]) -> list[TrackRecord]:
    """Convertit des PlaylistEntryRecord en TrackRecord pour l'export playlist."""
    from amso.core.db.models import PlaylistEntryRecord

    tracks: list[TrackRecord] = []
    for item in entries:
        if not isinstance(item, PlaylistEntryRecord):
            continue
        target = item.resolved_path or item.raw_path
        tracks.append(
            TrackRecord(
                source_ref=target,
                source_path=target,
                file_name=Path(target).name if target else None,
                title=item.title,
                artist=item.artist,
                duration_seconds=item.duration_seconds,
            )
        )
    return tracks


def replace_cue_file_target(
    cue_path: Path | str,
    old_raw_path: str,
    new_audio_path: Path | str,
) -> bool:
    """Met à jour la directive FILE d'une feuille CUE vers un nouveau fichier audio."""
    import re

    cue = Path(cue_path)
    if not cue.exists():
        return False

    raw_bytes = cue.read_bytes()
    encoding = "utf-8"
    text: str | None = None
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            text = raw_bytes.decode(enc)
            encoding = "utf-8-sig" if enc == "utf-8-sig" else enc
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        return False

    new_target_path = Path(new_audio_path)
    try:
        rel = os.path.relpath(str(new_target_path), str(cue.parent))
        new_ref = rel.replace("\\", "/")
    except ValueError:
        new_ref = str(new_target_path)

    file_re = re.compile(r'^(\s*FILE\s+)(?:"([^"]+)"|(\S+))(.*)$', re.IGNORECASE)
    old_norm = os.path.normcase(old_raw_path.replace("\\", "/"))

    replaced = False
    new_lines: list[str] = []
    for line in text.splitlines(keepends=True):
        m = file_re.match(line.rstrip("\r\n"))
        if m:
            prefix, quoted_val, unquoted_val, suffix = m.groups()
            current_val = quoted_val if quoted_val is not None else (unquoted_val or "")
            cur_norm = os.path.normcase(current_val.replace("\\", "/"))
            if cur_norm == old_norm or (not old_raw_path and not (cue.parent / current_val).exists()):
                ending = line[len(line.rstrip("\r\n")) :]
                line = f'{prefix}"{new_ref}"{suffix}{ending}'
                replaced = True
        new_lines.append(line)

    if not replaced:
        return False

    tmp_path = cue.with_suffix(".cue.tmp")
    tmp_path.write_text("".join(new_lines), encoding=encoding)
    tmp_path.replace(cue)
    return True
