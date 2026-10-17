"""Tests unitaires pour l'extraction et l'écriture des métadonnées audio."""

from pathlib import Path

from mutagen.id3 import ID3, TALB, TCON, TDRC, TIT2, TPE1, TRCK

from amso.core.metadata import (
    _clean_str,
    _parse_int_pair,
    _parse_year,
    compute_file_hash,
    extract_metadata,
    is_audio_file,
    save_metadata,
)


def test_is_audio_file():
    """Vérifie la détection des extensions audio."""
    assert is_audio_file("song.mp3") is True
    assert is_audio_file("track.FLAC") is True
    assert is_audio_file("audio.m4a") is True
    assert is_audio_file("sound.ogg") is True
    assert is_audio_file("file.wav") is True
    assert is_audio_file("document.txt") is False
    assert is_audio_file("image.png") is False
    assert is_audio_file("app.exe") is False


def test_compute_file_hash(tmp_path: Path):
    """Vérifie le calcul de l'empreinte SHA-256."""
    file = tmp_path / "sample.bin"
    file.write_bytes(b"Audio Multi-Source Organizer")
    h1 = compute_file_hash(file)
    assert len(h1) == 64
    assert h1 == compute_file_hash(file)

    # Modification du fichier -> empreinte modifiée
    file.write_bytes(b"Modified content")
    h2 = compute_file_hash(file)
    assert h1 != h2


def test_helper_parsers():
    """Vérifie le nettoyage et l'extraction des nombres et années."""
    assert _clean_str(["Queen"]) == "Queen"
    assert _clean_str("   ") is None
    assert _clean_str(None) is None

    # Extraction numéros de piste
    assert _parse_int_pair(5) == 5
    assert _parse_int_pair("03") == 3
    assert _parse_int_pair("12/20") == 12
    assert _parse_int_pair((7, 10)) == 7
    assert _parse_int_pair("invalid") is None

    # Extraction années
    assert _parse_year(1995) == 1995
    assert _parse_year("2021-04-12") == 2021
    assert _parse_year(["1975"]) == 1975
    assert _parse_year("Date inconnue") is None


def test_extract_metadata_without_tags(tmp_path: Path):
    """Vérifie le comportement robuste sur un fichier brut sans tags."""
    dummy = tmp_path / "unknown_track.mp3"
    dummy.write_bytes(b"\x00" * 1024)

    record = extract_metadata(dummy, source_id=1, compute_hash=True)
    assert record.title == "unknown_track"  # Nom par défaut issu du fichier
    assert record.artist is None
    assert record.format == "mp3"
    assert record.file_size == 1024
    assert record.file_hash is not None
    assert record.source_ref == dummy.resolve().as_posix()


def test_extract_and_save_mp3_metadata(tmp_path: Path):
    """Vérifie l'écriture et l'extraction des tags ID3."""
    mp3_file = tmp_path / "song.mp3"
    mp3_file.write_bytes(b"\x00" * 2048)

    # Initialisation de tags ID3
    id3 = ID3()
    id3.add(TIT2(encoding=3, text=["Under Pressure"]))
    id3.add(TPE1(encoding=3, text=["Queen & David Bowie"]))
    id3.add(TALB(encoding=3, text=["Hot Space"]))
    id3.add(TDRC(encoding=3, text=["1981"]))
    id3.add(TRCK(encoding=3, text=["11"]))
    id3.add(TCON(encoding=3, text=["Rock"]))
    id3.save(str(mp3_file))

    # Extraction
    record = extract_metadata(mp3_file)
    assert record.title == "Under Pressure"
    assert record.artist == "Queen & David Bowie"
    assert record.album == "Hot Space"
    assert record.year == 1981
    assert record.track_number == 11
    assert record.genre == "Rock"
    assert record.format == "mp3"
    assert record.quality_score > 0

    # Test modification via save_metadata
    ok = save_metadata(
        mp3_file,
        title="Under Pressure (2011 Remaster)",
        artist="Queen",
        year=2011,
    )
    assert ok is True

    updated_record = extract_metadata(mp3_file)
    assert updated_record.title == "Under Pressure (2011 Remaster)"
    assert updated_record.artist == "Queen"
    assert updated_record.year == 2011
    assert updated_record.album == "Hot Space"  # Préservé
