"""Tests unitaires et d'intégration pour le scanner local AMSO."""

import time
from pathlib import Path

import pytest
from mutagen.id3 import ID3, TIT2, TPE1

from amso.core.database import DatabaseManager, SourceType
from amso.core.scanner import LocalScanner


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


def test_two_phase_scan(tmp_path: Path, db: DatabaseManager, scanner: LocalScanner):
    """Vérifie le découpage précis entre Phase 1 (inventaire rapide) et Phase 2 (enrichissement audio)."""
    p = tmp_path / "song.mp3"
    p.write_bytes(b"\x00" * 1024)
    id3 = ID3()
    id3.add(TIT2(encoding=3, text=["My Song Title"]))
    id3.add(TPE1(encoding=3, text=["My Artist"]))
    id3.save(str(p))

    src = db.add_source(SourceType.LOCAL, "Test 2-Phase", str(tmp_path))

    # 1. Exécution de la Phase 1 uniquement
    inv_sum, files = scanner.scan_inventory(src)
    assert inv_sum.total_found == 1
    assert inv_sum.added == 1
    assert inv_sum.phase == 1

    # Morceau présent en BDD mais non extrait
    t = db.get_track_by_ref(p.resolve().as_posix())
    assert t is not None
    assert t.metadata_extracted is False
    assert t.title == "song"  # Titre temporaire = nom de fichier sans extension
    assert db.count_unextracted_tracks(src.id) == 1

    # 2. Exécution de la Phase 2
    ext_sum = scanner.extract_audio_metadata(src)
    assert ext_sum.analyzed == 1
    assert ext_sum.phase == 2

    # Morceau enrichi
    t_after = db.get_track_by_ref(p.resolve().as_posix())
    assert t_after is not None
    assert t_after.metadata_extracted is True
    assert t_after.title == "My Song Title"
    assert t_after.artist == "My Artist"
    assert db.count_unextracted_tracks(src.id) == 0

    # 3. Test callback on_phase1_finished lors du scan global
    phase1_notified = []
    scanner.scan_source(src, on_phase1_finished=lambda s: phase1_notified.append(s.phase))
    assert phase1_notified == [1]


def test_scan_skips_ignored_tracks(tmp_path: Path, db: DatabaseManager, scanner: LocalScanner):
    """Vérifie que les morceaux répertoriés dans ignored_tracks sont exclus dès l'inventaire."""
    f1 = tmp_path / "valid.mp3"
    f1.write_bytes(b"\x00" * 512)
    f2 = tmp_path / "deleted_ignored.mp3"
    f2.write_bytes(b"\x00" * 512)

    src = db.add_source(SourceType.LOCAL, "Test Ignored", str(tmp_path))

    # On ignore explicitement f2 avant le scan
    db.ignore_track(f2.resolve().as_posix(), str(f2.resolve()))

    inv_sum, files = scanner.scan_inventory(src)
    # Seul f1 doit être inventorié
    assert inv_sum.total_found == 1
    assert len(files) == 1
    assert files[0].name == "valid.mp3"
    assert db.get_track_by_ref(f2.resolve().as_posix()) is None

