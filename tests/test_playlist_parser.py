"""Tests unitaires pour le parser de playlists (M3U, M3U8, PLS, XSPF, WPL)."""

from __future__ import annotations

from pathlib import Path

from amso.core.playlist_parser import (
    SUPPORTED_PLAYLIST_EXTENSIONS,
    parse_playlist_file,
)


def test_supported_extensions() -> None:
    assert ".m3u" in SUPPORTED_PLAYLIST_EXTENSIONS
    assert ".m3u8" in SUPPORTED_PLAYLIST_EXTENSIONS
    assert ".pls" in SUPPORTED_PLAYLIST_EXTENSIONS
    assert ".xspf" in SUPPORTED_PLAYLIST_EXTENSIONS
    assert ".wpl" in SUPPORTED_PLAYLIST_EXTENSIONS


def test_parse_m3u_with_extinf(tmp_path: Path) -> None:
    # Création de deux fichiers audio fictifs
    f1 = tmp_path / "song1.mp3"
    f1.write_text("audio1")
    f2 = tmp_path / "sub" / "song2.flac"
    f2.parent.mkdir(parents=True, exist_ok=True)
    f2.write_text("audio2")

    m3u_content = """#EXTM3U
#EXTINF:180,Daft Punk - One More Time
song1.mp3
#EXTINF:240,Sub Folder Track
sub/song2.flac
#EXTINF:120,Missing Track
missing_file.mp3
"""
    pl_file = tmp_path / "test.m3u"
    pl_file.write_text(m3u_content, encoding="utf-8")

    entries = parse_playlist_file(pl_file)
    assert len(entries) == 3

    # Entrée 1
    assert entries[0].position == 1
    assert entries[0].artist == "Daft Punk"
    assert entries[0].title == "One More Time"
    assert entries[0].duration_seconds == 180.0
    assert entries[0].is_missing is False
    assert entries[0].resolved_path == str(f1).replace("\\", "/")

    # Entrée 2
    assert entries[1].position == 2
    assert entries[1].title == "Sub Folder Track"
    assert entries[1].is_missing is False
    assert entries[1].resolved_path == str(f2).replace("\\", "/")

    # Entrée 3 (Manquante)
    assert entries[2].position == 3
    assert entries[2].title == "Missing Track"
    assert entries[2].is_missing is True


def test_parse_pls_format(tmp_path: Path) -> None:
    f1 = tmp_path / "trackA.mp3"
    f1.write_text("audioA")

    pls_content = """[playlist]
NumberOfEntries=2
File1=trackA.mp3
Title1=Queen - Bohemian Rhapsody
Length1=354
File2=non_existent.ogg
Title2=Ghost Song
Length2=200
Version=2
"""
    pls_file = tmp_path / "test.pls"
    pls_file.write_text(pls_content, encoding="utf-8")

    entries = parse_playlist_file(pls_file)
    assert len(entries) == 2
    assert entries[0].position == 1
    assert entries[0].artist == "Queen"
    assert entries[0].title == "Bohemian Rhapsody"
    assert entries[0].duration_seconds == 354.0
    assert entries[0].is_missing is False

    assert entries[1].position == 2
    assert entries[1].title == "Ghost Song"
    assert entries[1].is_missing is True


def test_parse_xspf_format(tmp_path: Path) -> None:
    f1 = tmp_path / "song.mp3"
    f1.write_text("audio")

    xspf_content = """<?xml version="1.0" encoding="UTF-8"?>
<playlist version="1" xmlns="http://xspf.org/ns/0/">
    <trackList>
        <track>
            <location>song.mp3</location>
            <title>Stairway to Heaven</title>
            <creator>Led Zeppelin</creator>
            <duration>482000</duration>
        </track>
    </trackList>
</playlist>
"""
    xspf_file = tmp_path / "test.xspf"
    xspf_file.write_text(xspf_content, encoding="utf-8")

    entries = parse_playlist_file(xspf_file)
    assert len(entries) == 1
    assert entries[0].position == 1
    assert entries[0].artist == "Led Zeppelin"
    assert entries[0].title == "Stairway to Heaven"
    assert entries[0].duration_seconds == 482.0
    assert entries[0].is_missing is False


def test_parse_wpl_format(tmp_path: Path) -> None:
    f1 = tmp_path / "wpl_track.mp3"
    f1.write_text("wpl")

    wpl_content = """<?wpl version="1.0"?>
<smil>
    <head>
        <title>Mon Album WPL</title>
    </head>
    <body>
        <seq>
            <media src="wpl_track.mp3" trackTitle="Imagine" trackArtist="John Lennon"/>
            <media src="missing.mp3" trackTitle="Lost" trackArtist="Unknown"/>
        </seq>
    </body>
</smil>
"""
    wpl_file = tmp_path / "test.wpl"
    wpl_file.write_text(wpl_content, encoding="utf-8")

    entries = parse_playlist_file(wpl_file)
    assert len(entries) == 2
    assert entries[0].title == "Imagine"
    assert entries[0].artist == "John Lennon"
    assert entries[0].is_missing is False

    assert entries[1].title == "Lost"
    assert entries[1].is_missing is True
