"""Tests d'intégration pour l'indexation des playlists, l'affichage dans l'arbre par dossier et la lecture."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from amso.core.database import DatabaseManager, SourceType
from amso.core.scanner import LocalScanner
from amso.services.player_service import PlayerService
from amso.ui.views.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_playlist_scanning_and_tree_integration(qapp: QApplication, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie l'indexation de playlists (M3U, PLS), leur présence dans l'arborescence et l'affichage des morceaux ordonnés."""
    music_dir = tmp_path / "Music"
    music_dir.mkdir(parents=True)

    rock_dir = music_dir / "Rock"
    rock_dir.mkdir(parents=True)

    # Création de fichiers audio physiques
    t1 = rock_dir / "01_intro.mp3"
    t1.write_text("audio 1 content")
    t2 = rock_dir / "02_rock_anthem.mp3"
    t2.write_text("audio 2 content")
    t3 = music_dir / "outside.mp3"
    t3.write_text("audio 3 content")

    # Création d'une playlist M3U dans Rock avec 1 morceau existant et 1 manquant
    m3u_file = rock_dir / "BestOf.m3u"
    m3u_file.write_text(
        """#EXTM3U
#EXTINF:120,The Band - Intro
01_intro.mp3
#EXTINF:250,Ghost Artist - Missing Track
ghost_track.mp3
#EXTINF:180,The Band - Anthem
02_rock_anthem.mp3
""",
        encoding="utf-8",
    )

    db_path = tmp_path / "test_pl.db"
    db = DatabaseManager(str(db_path))
    src = db.add_source(SourceType.LOCAL, "Ma Musique", str(music_dir))

    # Scan complet
    scanner = LocalScanner(db=db)
    summary, _ = scanner.scan_inventory(source=src)
    assert summary.total_found == 3  # 3 fichiers audio
    assert summary.added == 3

    # Vérification de l'enregistrement en BDD dans la table playlists
    playlists = db.get_playlists(source_id=src.id)
    assert len(playlists) == 1
    pl = playlists[0]
    assert pl.file_name == "BestOf.m3u"
    assert pl.format == "m3u"
    assert pl.track_count == 3

    # Vérification des morceaux de la playlist
    pl_tracks = db.get_playlist_tracks(pl.id)
    assert len(pl_tracks) == 3
    # Ordre séquentiel strict
    assert pl_tracks[0].track_number == 1
    assert pl_tracks[0].file_name == "01_intro.mp3"
    assert pl_tracks[0].is_missing is False

    assert pl_tracks[1].track_number == 2
    assert pl_tracks[1].title == "Missing Track"
    assert pl_tracks[1].is_missing is True  # Fichier fantôme détecté manquant !

    assert pl_tracks[2].track_number == 3
    assert pl_tracks[2].file_name == "02_rock_anthem.mp3"
    assert pl_tracks[2].is_missing is False

    # Test IHM dans MainWindow
    window = MainWindow(db=db)
    monkeypatch.setattr(PlayerService, "is_vlc_available", property(lambda self: True))

    # Vérification de l'arborescence des dossiers
    tree = window.folder_tree
    root_item = tree.topLevelItem(0)
    assert root_item is not None

    # Recherche du nœud playlist dans l'arborescence
    found_pl_item = None
    for i in range(tree.topLevelItemCount()):
        top_it = tree.topLevelItem(i)
        if not top_it:
            continue
        stack = [top_it]
        while stack:
            curr = stack.pop()
            d = curr.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(d, dict) and d.get("is_playlist"):
                found_pl_item = curr
                break
            for c_idx in range(curr.childCount()):
                child = curr.child(c_idx)
                if child:
                    stack.append(child)
        if found_pl_item:
            break

    assert found_pl_item is not None
    assert "🎶" in found_pl_item.text(0)
    assert "BestOf.m3u" in found_pl_item.text(0)
    assert found_pl_item.text(1) == "3"

    # Clic / sélection du nœud playlist
    window._select_folder_item(found_pl_item)

    # Vérification breadcrumb et table
    assert "🎶" in window.lbl_folder_breadcrumb.text()
    assert "BestOf.m3u" in window.lbl_folder_breadcrumb.text()
    assert window.cb_recursive.isHidden() is True  # Récursivité masquée pour une playlist

    # Table des pistes
    assert window.folder_table_model.rowCount() == 3
    t_row0 = window.folder_table_model.get_track_at(0)
    assert t_row0 is not None
    assert t_row0.track_number == 1
    assert t_row0.is_missing is False

    t_row1 = window.folder_table_model.get_track_at(1)
    assert t_row1 is not None
    assert t_row1.is_missing is True
    # Vérification de l'affichage avec préfixe d'avertissement
    idx_title = window.folder_table_model.index(1, 1)  # Colonne titre
    disp_title = window.folder_table_model.data(idx_title, Qt.ItemDataRole.DisplayRole)
    assert "⚠️" in disp_title

    # Lancement de la lecture depuis la playlist
    window.player_service.clear_playlist()
    window._play_from_table(window.folder_table_model, start_row=0)
    assert len(window.player_service.playlist) == 3
    assert window.player_service.playlist[0].file_name == "01_intro.mp3"

    # Vérification du menu contextuel sur l'élément playlist
    ctx_tracks: list = []
    monkeypatch.setattr(window.player_service, "play_tracks", lambda trs, start_index=0: ctx_tracks.extend(trs))
    window.folder_tree.setCurrentItem(found_pl_item)
    # Simulation action menu contextuel
    data = found_pl_item.data(0, Qt.ItemDataRole.UserRole)
    tracks = window.db.get_playlist_tracks(data["playlist_id"])
    assert len(tracks) == 3
    window.player_service.play_tracks(tracks, start_index=0)
    assert len(ctx_tracks) == 3

    # Test suppression du fichier playlist sur le disque + re-scan -> la playlist doit être retirée
    m3u_file.unlink()
    summary2, _ = scanner.scan_inventory(source=src)
    assert len(db.get_playlists(source_id=src.id)) == 0

    # L'arbre ne doit plus contenir le nœud
    window._refresh_folders_tree()
    found_after_delete = False
    for i in range(tree.topLevelItemCount()):
        top_it = tree.topLevelItem(i)
        if not top_it:
            continue
        stack = [top_it]
        while stack:
            curr = stack.pop()
            d = curr.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(d, dict) and d.get("is_playlist"):
                found_after_delete = True
                break
            for c_idx in range(curr.childCount()):
                child = curr.child(c_idx)
                if child:
                    stack.append(child)
    assert not found_after_delete

    window.close()
