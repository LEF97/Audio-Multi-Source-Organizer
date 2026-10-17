"""Tests unitaires pour la couche de base de données AMSO."""

import pytest

from amso.core.database import (
    DatabaseManager,
    SourceType,
    TrackRecord,
    compute_quality_score,
)


@pytest.fixture
def db() -> DatabaseManager:
    """Fixture fournissant une base SQLite en mémoire pour chaque test."""
    return DatabaseManager(":memory:")


def test_compute_quality_score():
    """Vérifie la hiérarchie des scores qualitatifs."""
    # FLAC Hi-Res > FLAC standard > MP3 320 > MP3 128
    flac_hires = compute_quality_score("flac", bitrate=2500, sample_rate=96000)
    flac_cd = compute_quality_score("flac", bitrate=1000, sample_rate=44100)
    mp3_320 = compute_quality_score("mp3", bitrate=320, sample_rate=44100)
    mp3_128 = compute_quality_score("mp3", bitrate=128, sample_rate=44100)

    assert flac_hires > flac_cd
    assert flac_cd > mp3_320
    assert mp3_320 > mp3_128


def test_sources_crud(db: DatabaseManager):
    """Vérifie la création, récupération et mise à jour des sources."""
    src1 = db.add_source(SourceType.LOCAL, "Musique Locale", "D:/Music")
    assert src1.id is not None
    assert src1.name == "Musique Locale"
    assert src1.source_type == SourceType.LOCAL

    # Conflit sur path_or_uri -> mise à jour du nom
    src1_updated = db.add_source(SourceType.LOCAL, "Musique Principale", "D:/Music")
    assert src1_updated.id == src1.id
    assert src1_updated.name == "Musique Principale"

    # Liste des sources
    db.add_source(SourceType.SPOTIFY, "Mon Spotify", "spotify:user:12345")
    sources = db.get_sources()
    assert len(sources) == 2

    # Horodatage du scan
    db.update_source_scanned(src1.id)
    refetched = db.get_source(src1.id)
    assert refetched is not None
    assert refetched.last_scanned_at is not None

    # Suppression
    deleted = db.delete_source(src1.id)
    assert deleted is True
    assert db.get_source(src1.id) is None


def test_tracks_upsert_and_batch(db: DatabaseManager):
    """Vérifie l'insertion unitaire et par lots de pistes audio."""
    src = db.add_source(SourceType.LOCAL, "Dossier Test", "D:/Audio")

    t1 = TrackRecord(
        source_ref="D:/Audio/track1.mp3",
        source_type=SourceType.LOCAL,
        source_id=src.id,
        title="Bohemian Rhapsody",
        artist="Queen",
        album="A Night at the Opera",
        format="mp3",
        bitrate=320,
        sample_rate=44100,
        duration_seconds=354.0,
        file_hash="hash_queen_1",
    )
    t2 = TrackRecord(
        source_ref="D:/Audio/track2.flac",
        source_type=SourceType.LOCAL,
        source_id=src.id,
        title="Stairway to Heaven",
        artist="Led Zeppelin",
        album="Led Zeppelin IV",
        format="flac",
        bitrate=950,
        sample_rate=44100,
        duration_seconds=482.0,
        file_hash="hash_led_1",
    )

    ids = db.upsert_tracks_batch([t1, t2])
    assert len(ids) == 2

    fetched = db.get_track(ids[0])
    assert fetched is not None
    assert fetched.title == "Bohemian Rhapsody"
    assert fetched.artist == "Queen"
    assert fetched.quality_score > 0

    # Test mise à jour via upsert (même source_ref)
    t1_modified = TrackRecord(
        source_ref="D:/Audio/track1.mp3",
        source_type=SourceType.LOCAL,
        source_id=src.id,
        title="Bohemian Rhapsody (2011 Remaster)",
        artist="Queen",
        album="A Night at the Opera",
        format="mp3",
        bitrate=320,
    )
    id_updated = db.upsert_track(t1_modified)
    assert id_updated == ids[0]

    refetched = db.get_track_by_ref("D:/Audio/track1.mp3")
    assert refetched is not None
    assert refetched.title == "Bohemian Rhapsody (2011 Remaster)"


def test_tracks_pagination_and_sorting(db: DatabaseManager):
    """Vérifie la pagination et le tri pour le modèle Qt."""
    src = db.add_source(SourceType.LOCAL, "Dossier", "D:/Audio")

    tracks = [
        TrackRecord(source_ref=f"ref_{i}", source_id=src.id, title=f"Track {i:02d}", artist="Artist") for i in range(25)
    ]
    db.upsert_tracks_batch(tracks)

    # Page 1 (10 éléments)
    page1, total = db.get_tracks(limit=10, offset=0, sort_by="title", sort_order="ASC")
    assert total == 25
    assert len(page1) == 10
    assert page1[0].title == "Track 00"

    # Page 2 (10 éléments)
    page2, _ = db.get_tracks(limit=10, offset=10, sort_by="title", sort_order="ASC")
    assert len(page2) == 10
    assert page2[0].title == "Track 10"

    # Tri décroissant
    desc_page, _ = db.get_tracks(limit=5, offset=0, sort_by="title", sort_order="DESC")
    assert desc_page[0].title == "Track 24"


def test_fts5_search(db: DatabaseManager):
    """Vérifie la recherche plein texte instantanée FTS5."""
    src = db.add_source(SourceType.LOCAL, "Dossier", "D:/Audio")

    db.upsert_tracks_batch(
        [
            TrackRecord(
                source_ref="1", source_id=src.id, title="Get Lucky", artist="Daft Punk", album="Random Access Memories"
            ),
            TrackRecord(
                source_ref="2",
                source_id=src.id,
                title="Instant Crush",
                artist="Daft Punk feat. Julian Casablancas",
                album="Random Access Memories",
            ),
            TrackRecord(
                source_ref="3", source_id=src.id, title="Around the World", artist="Daft Punk", album="Homework"
            ),
            TrackRecord(
                source_ref="4", source_id=src.id, title="Billie Jean", artist="Michael Jackson", album="Thriller"
            ),
        ]
    )

    # Recherche par artiste
    results, count = db.search_tracks("Daft")
    assert count == 3
    assert len(results) == 3

    # Recherche par album
    results, count = db.search_tracks("Random Access")
    assert count == 2

    # Recherche combinée titre + feat
    results, count = db.search_tracks("Julian Instant")
    assert count == 1
    assert results[0].title == "Instant Crush"

    # Recherche inexistante
    results, count = db.search_tracks("Metallica")
    assert count == 0
    assert len(results) == 0


def test_duplicate_detection(db: DatabaseManager):
    """Vérifie la détection de doublons par hash et métadonnées."""
    src = db.add_source(SourceType.LOCAL, "Audio", "D:/Audio")

    # Deux pistes avec le même hash mais des chemins différents
    db.upsert_tracks_batch(
        [
            TrackRecord(
                source_ref="path1.mp3",
                source_id=src.id,
                title="Song A",
                artist="Band",
                file_hash="hash_dup_123",
                format="mp3",
                bitrate=128,
            ),
            TrackRecord(
                source_ref="path2.flac",
                source_id=src.id,
                title="Song A (Lossless)",
                artist="Band",
                file_hash="hash_dup_123",
                format="flac",
                bitrate=1000,
            ),
            TrackRecord(
                source_ref="path3.mp3",
                source_id=src.id,
                title="Unique Song",
                artist="Band",
                file_hash="hash_unique",
                format="mp3",
                bitrate=320,
            ),
        ]
    )

    dup_groups = db.find_duplicates_by_hash()
    assert len(dup_groups) == 1
    assert len(dup_groups[0]) == 2
    # Le fichier FLAC (score plus élevé) doit être en premier
    assert dup_groups[0][0].format == "flac"
    assert dup_groups[0][1].format == "mp3"

    # Test doublons par métadonnées (titre & artiste identiques)
    meta_groups = db.find_duplicates_by_metadata()
    assert len(meta_groups) == 0
    # song A et song A (lossless) ont des titres légèrement différents, mais ajoutons des titres strictement identiques
    db.upsert_track(
        TrackRecord(source_ref="path4.mp3", source_id=src.id, title="Song A", artist="Band", format="mp3", bitrate=256)
    )
    meta_groups2 = db.find_duplicates_by_metadata()
    assert len(meta_groups2) >= 1


def test_prune_missing_tracks(db: DatabaseManager):
    """Vérifie le nettoyage des morceaux supprimés lors d'un scan."""
    src = db.add_source(SourceType.LOCAL, "Audio", "D:/Audio")

    db.upsert_tracks_batch(
        [
            TrackRecord(source_ref="f1.mp3", source_id=src.id, title="T1"),
            TrackRecord(source_ref="f2.mp3", source_id=src.id, title="T2"),
            TrackRecord(source_ref="f3.mp3", source_id=src.id, title="T3"),
        ]
    )

    # Le scan actuel ne trouve que f1 et f3 (f2 a été supprimé du disque)
    deleted = db.prune_missing_tracks(src.id, {"f1.mp3", "f3.mp3"})
    assert deleted == 1

    remaining, total = db.get_tracks()
    assert total == 2
    refs = {r.source_ref for r in remaining}
    assert refs == {"f1.mp3", "f3.mp3"}


def test_library_stats(db: DatabaseManager):
    """Vérifie le calcul des statistiques de la bibliothèque."""
    src_local = db.add_source(SourceType.LOCAL, "Disque", "D:/Audio")
    src_spotify = db.add_source(SourceType.SPOTIFY, "Spotify", "spotify:user")

    db.upsert_tracks_batch(
        [
            TrackRecord(
                source_ref="l1.flac",
                source_type=SourceType.LOCAL,
                source_id=src_local.id,
                format="flac",
                duration_seconds=200.0,
                file_size=30_000_000,
            ),
            TrackRecord(
                source_ref="l2.mp3",
                source_type=SourceType.LOCAL,
                source_id=src_local.id,
                format="mp3",
                duration_seconds=180.0,
                file_size=8_000_000,
            ),
            TrackRecord(
                source_ref="s1",
                source_type=SourceType.SPOTIFY,
                source_id=src_spotify.id,
                format="streaming",
                duration_seconds=210.0,
                file_size=0,
            ),
        ]
    )

    stats = db.get_library_stats()
    assert stats["total_tracks"] == 3
    assert stats["total_sources"] == 2
    assert stats["total_duration_seconds"] == 590.0
    assert stats["total_size_bytes"] == 38_000_000
    assert stats["by_source_type"]["local"] == 2
    assert stats["by_source_type"]["spotify"] == 1
    assert stats["by_format"]["flac"] == 1
    assert stats["by_format"]["mp3"] == 1


def test_batch_performance_and_clusters(db: DatabaseManager):
    """Vérifie que l'insertion par lot de 2 000 titres est ultra-rapide."""
    import time

    src = db.add_source(SourceType.LOCAL, "Gros Dossier", "D:/LargeMusic")

    large_batch = [
        TrackRecord(
            source_ref=f"D:/LargeMusic/track_{i}.mp3",
            source_id=src.id,
            title=f"Track {i}",
            artist=f"Artist {i % 50}",
            album=f"Album {i % 100}",
            format="mp3",
            bitrate=320,
            duration_seconds=210.0,
            file_hash=f"hash_{i % 200}",
        )
        for i in range(2000)
    ]

    t0 = time.perf_counter()
    ids = db.upsert_tracks_batch(large_batch)
    t1 = time.perf_counter()

    elapsed = t1 - t0
    assert len(ids) == 2000
    # L'insertion par lots doit être très rapide (< 1.5s pour 2 000 morceaux)
    assert elapsed < 1.5

    # Test d'assignation de cluster de doublons
    db.assign_duplicate_cluster([ids[0], ids[1]], cluster_id=42)
    t_clustered = db.get_track(ids[0])
    assert t_clustered is not None
    assert t_clustered.duplicate_cluster_id == 42


def test_track_record_folder_paths(db: DatabaseManager):
    """Vérifie le calcul et la persistance de file_name, folder_path et folder_name."""
    src = db.add_source(SourceType.LOCAL, "Source Test", "X:/Music/_Temp")

    t1 = TrackRecord(
        source_ref="X:/Music/_Temp/Rock/Queen/Bohemian.mp3",
        source_id=src.id,
        source_path="X:/Music/_Temp/Rock/Queen/Bohemian.mp3",
        title="Bohemian Rhapsody",
        artist="Queen",
    )
    # Vérification de l'auto-dérivation dans __post_init__
    assert t1.file_name == "Bohemian.mp3"
    assert t1.folder_path == "X:/Music/_Temp/Rock/Queen"
    assert t1.folder_name == "Queen"

    tid = db.upsert_track(t1)
    retrieved = db.get_track(tid)
    assert retrieved is not None
    assert retrieved.file_name == "Bohemian.mp3"
    assert retrieved.folder_path == "X:/Music/_Temp/Rock/Queen"
    assert retrieved.folder_name == "Queen"


def test_folders_summary_and_tracks_by_folder(db: DatabaseManager):
    """Vérifie l'exploration par dossiers, le résumé arborescent et le mode récursif."""
    src = db.add_source(SourceType.LOCAL, "Dossier Source", "D:/Music")

    db.upsert_tracks_batch(
        [
            TrackRecord(
                source_ref="D:/Music/root1.mp3", source_path="D:/Music/root1.mp3", source_id=src.id, title="Root 1"
            ),
            TrackRecord(
                source_ref="D:/Music/root2.mp3", source_path="D:/Music/root2.mp3", source_id=src.id, title="Root 2"
            ),
            TrackRecord(
                source_ref="D:/Music/Rock/track1.flac",
                source_path="D:/Music/Rock/track1.flac",
                source_id=src.id,
                title="Rock 1",
            ),
            TrackRecord(
                source_ref="D:/Music/Rock/Queen/song1.mp3",
                source_path="D:/Music/Rock/Queen/song1.mp3",
                source_id=src.id,
                title="Queen 1",
            ),
            TrackRecord(
                source_ref="D:/Music/Rock/Queen/song2.mp3",
                source_path="D:/Music/Rock/Queen/song2.mp3",
                source_id=src.id,
                title="Queen 2",
            ),
            TrackRecord(
                source_ref="D:/Music/Jazz/Miles/blue.flac",
                source_path="D:/Music/Jazz/Miles/blue.flac",
                source_id=src.id,
                title="Kind of Blue",
            ),
        ]
    )

    # Résumé des dossiers
    summary = db.get_folders_summary(source_id=src.id)
    folders_map = {s["folder_path"]: s["track_count"] for s in summary}
    assert folders_map["D:/Music"] == 2
    assert folders_map["D:/Music/Rock"] == 1
    assert folders_map["D:/Music/Rock/Queen"] == 2
    assert folders_map["D:/Music/Jazz/Miles"] == 1

    # Navigation non récursive dans Rock
    rock_direct = db.get_tracks_by_folder("D:/Music/Rock", source_id=src.id, recursive=False)
    assert len(rock_direct) == 1
    assert rock_direct[0].title == "Rock 1"
    assert db.count_tracks_by_folder("D:/Music/Rock", source_id=src.id, recursive=False) == 1

    # Navigation récursive dans Rock (inclut Rock et Rock/Queen)
    rock_recursive = db.get_tracks_by_folder("D:/Music/Rock", source_id=src.id, recursive=True)
    assert len(rock_recursive) == 3
    titles = {t.title for t in rock_recursive}
    assert titles == {"Rock 1", "Queen 1", "Queen 2"}
    assert db.count_tracks_by_folder("D:/Music/Rock", source_id=src.id, recursive=True) == 3

    # Navigation récursive depuis la racine D:/Music
    all_recursive = db.get_tracks_by_folder("D:/Music", source_id=src.id, recursive=True)
    assert len(all_recursive) == 6


def test_file_db_wal_mode_and_concurrency(tmp_path):
    """Vérifie le mode WAL persistant, les pragmas et la concurrence multi-threads sur fichier réel."""
    import concurrent.futures
    import sqlite3

    db_file = tmp_path / "test_concurrency.db"
    db_manager = DatabaseManager(db_path=db_file)

    try:
        # 1. Vérification du journal_mode persistant
        with sqlite3.connect(str(db_file)) as raw_conn:
            mode = raw_conn.execute("PRAGMA journal_mode;").fetchone()[0]
            assert mode.lower() == "wal"

        # 2. Test de lectures et écritures concurrentes
        db_manager.add_source(SourceType.LOCAL, "Concurrent Source", "D:/Concur")

        def worker_write(idx: int):
            db_manager.add_activity_log(
                action=f"Action {idx}",
                level="INFO",
                category="SYNC",
                source_name="Concurrent Source",
            )
            return True

        def worker_read():
            logs = db_manager.get_activity_logs(limit=50)
            return len(logs)

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            write_futures = [executor.submit(worker_write, i) for i in range(30)]
            read_futures = [executor.submit(worker_read) for _ in range(30)]

            for f in concurrent.futures.as_completed(write_futures + read_futures):
                res = f.result()
                assert res is not None

        # 3. Checkpoint et fermeture propre
        db_manager.checkpoint()
        assert db_manager.count_activity_logs() == 30
    finally:
        db_manager.close()


def test_ignored_tracks(db: DatabaseManager):
    """Vérifie l'ajout, la lecture et le retrait de morceaux ignorés."""
    # Au départ, aucun morceau ignoré
    assert len(db.get_ignored_tracks_refs()) == 0

    # Ignorer deux morceaux
    db.ignore_track("track_ref_1", "D:/Music/song1.flac")
    db.ignore_track("track_ref_2", "D:/Music/song2.mp3")

    refs = db.get_ignored_tracks_refs()
    assert len(refs) == 2
    assert "track_ref_1" in refs
    assert "track_ref_2" in refs

    # Ignorer à nouveau le même ref ne doit pas lever d'erreur (INSERT OR IGNORE)
    db.ignore_track("track_ref_1", "D:/Music/song1.flac")
    assert len(db.get_ignored_tracks_refs()) == 2

    # Désignorer
    assert db.unignore_track("track_ref_1") is True
    assert "track_ref_1" not in db.get_ignored_tracks_refs()
    assert len(db.get_ignored_tracks_refs()) == 1

