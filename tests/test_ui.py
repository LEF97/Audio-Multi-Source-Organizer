"""Tests unitaires pour les composants PySide6 (modèles virtualisés et interface)."""

import os
from pathlib import Path
import pytest

# Exécution en mode headless pour assurer la compatibilité CI (Linux/macOS/Windows)
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from amso.core.database import DatabaseManager, SourceType, TrackRecord
from amso.core.i18n import get_i18n, tr
from amso.ui.models import TrackTableModel, format_duration, format_quality
from amso.ui.views.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Fixture créant ou réutilisant l'instance QApplication unique."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def db() -> DatabaseManager:
    """Fixture fournissant une base SQLite en mémoire avec quelques morceaux."""
    db_manager = DatabaseManager(":memory:")
    src = db_manager.add_source(SourceType.LOCAL, "Dossier Test", "D:/Music")

    tracks = [
        TrackRecord(
            source_ref="D:/Music/track1.mp3",
            source_id=src.id,
            title="Bohemian Rhapsody",
            artist="Queen",
            album="A Night at the Opera",
            duration_seconds=354.0,
            format="mp3",
            bitrate=320,
            quality_score=650,
            year=1975,
            track_number=11,
        ),
        TrackRecord(
            source_ref="D:/Music/track2.flac",
            source_id=src.id,
            title="Stairway to Heaven",
            artist="Led Zeppelin",
            album="Led Zeppelin IV",
            duration_seconds=482.0,
            format="flac",
            bitrate=1000,
            quality_score=850,
            year=1971,
            track_number=4,
        ),
    ]
    db_manager.upsert_tracks_batch(tracks)
    return db_manager


def test_format_helpers():
    """Vérifie le formatage des durées et libellés de qualité."""
    assert format_duration(65) == "1:05"
    assert format_duration(3665) == "1:01:05"
    assert format_duration(None) == "--:--"
    assert format_duration(0) == "--:--"

    get_i18n().set_language("fr")
    assert "Lossless" in format_quality(850, "flac", 1000)
    assert "Hi-Res" in format_quality(950, "flac", 2500)
    assert "320k" in format_quality(650, "mp3", 320)


def test_track_table_model(qapp: QApplication, db: DatabaseManager):
    """Vérifie le fonctionnement du modèle virtualisé QAbstractTableModel."""
    i18n = get_i18n()
    i18n.set_language("fr")

    model = TrackTableModel(db=db)
    model.reload_data()

    assert model.rowCount() == 2
    assert model.columnCount() == 9

    # Vérification des en-têtes en français
    assert model.headerData(0, Qt.Orientation.Horizontal) == "Titre"
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Artiste"
    assert model.headerData(3, Qt.Orientation.Horizontal) == "Durée"

    # Vérification de la dynamique de changement de langue
    i18n.set_language("en")
    model.notify_language_changed()
    assert model.headerData(0, Qt.Orientation.Horizontal) == "Title"
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Artist"
    assert model.headerData(3, Qt.Orientation.Horizontal) == "Duration"

    # Retour au français
    i18n.set_language("fr")
    model.notify_language_changed()

    # Vérification des cellules (ligne 0 : Queen)
    idx_title = model.index(0, 0)
    assert model.data(idx_title, Qt.ItemDataRole.DisplayRole) == "Bohemian Rhapsody"

    idx_artist = model.index(0, 1)
    assert model.data(idx_artist, Qt.ItemDataRole.DisplayRole) == "Queen"

    idx_duration = model.index(0, 3)
    assert model.data(idx_duration, Qt.ItemDataRole.DisplayRole) == "5:54"

    # Tri par titre décroissant
    model.sort(0, Qt.SortOrder.DescendingOrder)
    assert model.data(model.index(0, 0), Qt.ItemDataRole.DisplayRole) == "Stairway to Heaven"

    # Filtre recherche FTS
    model.set_filter(search_query="Queen")
    assert model.rowCount() == 1
    assert model.data(model.index(0, 0), Qt.ItemDataRole.DisplayRole) == "Bohemian Rhapsody"


def test_main_window_instantiation(qapp: QApplication, db: DatabaseManager):
    """Vérifie la création correcte de la fenêtre principale et du sélecteur de langue."""
    i18n = get_i18n()
    i18n.set_language("fr")

    window = MainWindow(db=db)
    assert "AMSO" in window.windowTitle()
    assert window.table_model.rowCount() == 2
    assert window.search_edit is not None
    assert window.btn_all_tracks.isChecked() is True
    assert "Tous les morceaux" in window.btn_all_tracks.text()

    # Vérification du sélecteur de langue
    assert window.combo_language is not None
    assert window.combo_language.count() >= 4

    # Changement dynamique de langue vers l'anglais
    en_idx = window.combo_language.findData("en")
    assert en_idx >= 0
    window.combo_language.setCurrentIndex(en_idx)
    assert "All Tracks" in window.btn_all_tracks.text()
    assert "Scan Sources" in window.btn_scan_all.text()

    # Retour au français
    fr_idx = window.combo_language.findData("fr")
    window.combo_language.setCurrentIndex(fr_idx)
    assert "Tous les morceaux" in window.btn_all_tracks.text()

    # Test clic sur Doublons
    window.btn_duplicates.click()
    assert window.btn_duplicates.isChecked() is True
    assert window.stacked_widget.currentIndex() == 0

    # Test clic sur Statistiques (nouvelle page dédiée)
    window.btn_stats_page.click()
    assert window.btn_stats_page.isChecked() is True
    assert window.stacked_widget.currentIndex() == 1
    assert "2" in window.kpi_tracks_val.text()

    # Test clic sur Paramètres > Général (page dédiée avec langue)
    window.btn_settings_general.click()
    assert window.btn_settings_general.isChecked() is True
    assert window.stacked_widget.currentIndex() == 2

    # Test retour sur Tous les morceaux
    window.btn_all_tracks.click()
    assert window.btn_all_tracks.isChecked() is True
    assert window.stacked_widget.currentIndex() == 0

    # Test repliement / dépliement d'un tiroir
    assert window.drawer_library._is_expanded is True
    window.drawer_library.toggle()
    assert window.drawer_library._is_expanded is False
    assert window.drawer_library.content_widget.isVisible() is False
    window.drawer_library.toggle()
    assert window.drawer_library._is_expanded is True

    window.close()
