"""Tests unitaires et d'intégration pour le scanner local AMSO."""

from pathlib import Path
import time
import pytest

from mutagen.id3 import ID3, TIT2, TPE1

from amso.core.database import DatabaseManager, SourceType
from amso.core.scanner import LocalScanner, ScanSummary


@pytest.fixture
def db() -> DatabaseManager:
    """Fixture fournissant une base SQLite en mémoire."""
    return DatabaseManager(":memory:")


@pytest.fixture
def scanner(db: DatabaseManager) -> LocalScanner:
    """Fixture fournissant une instance de LocalScanner."""
    return LocalScanner(db=db, max_workers=2, batch_size=5)


def test_scan_nonexistent_directory(db: DatabaseManager, scanner: LocalScanner):
    """Vérifie le comportement si le dossier source n'existe pas."""
    src = db.add_source(SourceType.LOCAL, "Inexistant", "D:/Dossier/Qui/Nexiste/Pas")
    summary = scanner.scan_source(src)
    assert len(summary.errors) > 0
    assert summary.total_found == 0


def test_scan_empty_directory(tmp_path: Path, db: DatabaseManager, scanner: LocalScanner):
    """Vérifie le comportement sur un dossier vide."""
    src = db.add_source(SourceType.LOCAL, "Vide", str(tmp_path))
    summary = scanner.scan_source(src)
    assert summary.total_found == 0
    assert summary.added == 0
    assert len(summary.errors) == 0


def test_scan_and_incremental(tmp_path: Path, db: DatabaseManager, scanner: LocalScanner):
    """Vérifie le scan récursif, l'indexation initiale puis le scan incrémental."""
    # Création d'une arborescence de test
    sub1 = tmp_path / "Rock" / "Queen"
    sub1.mkdir(parents=True)
    sub2 = tmp_path / "Jazz"
    sub2.mkdir(parents=True)

    # Fichiers audio
    f1 = sub1 / "track1.mp3"
    f1.write_bytes(b"\x00" * 1024)
    id3 = ID3()
    id3.add(TIT2(encoding=3, text=["Bohemian Rhapsody"]))
    id3.add(TPE1(encoding=3, text=["Queen"]))
    id3.save(str(f1))

    f2 = sub1 / "track2.flac"
    f2.write_bytes(b"\x00" * 2048)

    f3 = sub2 / "jazz1.ogg"
    f3.write_bytes(b"\x00" * 512)

    # Fichier non-audio à ignorer
    ignored_txt = sub1 / "cover.jpg"
    ignored_txt.write_bytes(b"image")

    src = db.add_source(SourceType.LOCAL, "Ma Musique", str(tmp_path))

    # 1. Premier scan
    progress_calls = []

    def on_prog(done, total, current):
        progress_calls.append((done, total))

    summary1 = scanner.scan_source(src, on_progress=on_prog)
    assert summary1.total_found == 3
    assert summary1.added == 3
    assert summary1.updated == 0
    assert summary1.unchanged == 0
    assert summary1.deleted == 0

    tracks, count = db.get_tracks(source_id=src.id)
    assert count == 3

    # Vérification des tags du fichier MP3
    t1 = db.get_track_by_ref(f1.resolve().as_posix())
    assert t1 is not None
    assert t1.title == "Bohemian Rhapsody"
    assert t1.artist == "Queen"

    # 2. Deuxième scan immédiat (aucun changement) -> Tout doit être 'unchanged'
    summary2 = scanner.scan_source(src)
    assert summary2.total_found == 3
    assert summary2.added == 0
    assert summary2.updated == 0
    assert summary2.unchanged == 3
    assert summary2.deleted == 0

    # 3. Modification d'un fichier (modification du contenu)
    time.sleep(0.01)  # Assurer mtime différent
    f2.write_bytes(b"\x00" * 4096)
    summary3 = scanner.scan_source(src)
    assert summary3.updated == 1
    assert summary3.unchanged == 2
    assert summary3.added == 0

    # 4. Suppression d'un fichier du disque
    f3.unlink()
    summary4 = scanner.scan_source(src)
    assert summary4.total_found == 2
    assert summary4.unchanged == 2
    assert summary4.deleted == 1

    tracks, count = db.get_tracks(source_id=src.id)
    assert count == 2
