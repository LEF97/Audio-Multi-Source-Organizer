"""Tests unitaires pour les composants PySide6 (modèles virtualisés et interface)."""

import os

import pytest

# Exécution en mode headless pour assurer la compatibilité CI (Linux/macOS/Windows)
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from amso import __version__
from amso.core.database import DatabaseManager, SourceType, TrackRecord
from amso.core.i18n import get_i18n
from amso.ui.models import (
    FolderTrackTableModel,
    TrackTableModel,
    format_duration,
    format_quality,
)
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
    """Vérifie le fonctionnement du modèle virtualisé QAbstractTableModel harmonisé."""
    i18n = get_i18n()
    i18n.set_language("fr")

    model = TrackTableModel(db=db)
    model.reload_data()

    assert model.rowCount() == 2
    assert model.columnCount() == 29

    # Vérification des en-têtes en français
    assert model.headerData(0, Qt.Orientation.Horizontal) == "Nom de fichier"
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Titre"
    assert model.headerData(2, Qt.Orientation.Horizontal) == "Artiste"
    assert model.headerData(9, Qt.Orientation.Horizontal) == "Durée"

    # Vérification de la dynamique de changement de langue
    i18n.set_language("en")
    model.notify_language_changed()
    assert model.headerData(0, Qt.Orientation.Horizontal) == "Filename"
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Title"
    assert model.headerData(2, Qt.Orientation.Horizontal) == "Artist"
    assert model.headerData(9, Qt.Orientation.Horizontal) == "Duration"

    # Retour au français
    i18n.set_language("fr")
    model.notify_language_changed()

    # Vérification des cellules (ligne 0 : Queen)
    idx_title = model.index(0, 1)
    assert model.data(idx_title, Qt.ItemDataRole.DisplayRole) == "Bohemian Rhapsody"

    idx_artist = model.index(0, 2)
    assert model.data(idx_artist, Qt.ItemDataRole.DisplayRole) == "Queen"

    idx_duration = model.index(0, 9)
    assert model.data(idx_duration, Qt.ItemDataRole.DisplayRole) == "5:54"

    # Tri par titre décroissant (colonne 1 = titre)
    model.sort(1, Qt.SortOrder.DescendingOrder)
    assert model.data(model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "Stairway to Heaven"

    # Filtre recherche FTS
    model.set_filter(search_query="Queen")
    assert model.rowCount() == 1
    assert model.data(model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "Bohemian Rhapsody"


def test_main_window_instantiation(qapp: QApplication, db: DatabaseManager):
    """Vérifie la création correcte de la fenêtre principale et du sélecteur de langue."""
    i18n = get_i18n()
    i18n.set_language("fr")

    window = MainWindow(db=db)
    assert "AMSO" in window.windowTitle()
    assert __version__ in window.windowTitle()
    assert window.table_model.rowCount() == 2
    assert window.btn_player.isChecked() is True
    window.btn_all_tracks.click()
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
    assert "Duplicates" in window.btn_duplicates.text()

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

    # Test clic sur Paramètres > Sources (page dédiée avec sources)
    window.btn_settings_sources.click()
    assert window.btn_settings_sources.isChecked() is True
    assert window.stacked_widget.currentIndex() == 4

    # Test retour sur Tous les morceaux
    window.btn_all_tracks.click()
    assert window.btn_all_tracks.isChecked() is True
    assert window.stacked_widget.currentIndex() == 0

    # Test état des tiroirs par défaut : seul Lecteur est ouvert, tous les autres sont fermés
    assert window.drawer_player._is_expanded is True
    assert window.drawer_games._is_expanded is False
    assert window.drawer_library._is_expanded is False
    assert window.drawer_tools._is_expanded is False
    assert window.drawer_stats._is_expanded is False
    assert window.drawer_sources._is_expanded is False
    assert window.drawer_settings._is_expanded is False
    assert window.drawer_library.content_widget.isHidden() is True
    window.drawer_library.toggle()
    assert window.drawer_library._is_expanded is True
    assert window.drawer_library.content_widget.isHidden() is False
    window.drawer_library.toggle()
    assert window.drawer_library._is_expanded is False

    window.close()


def test_folder_track_table_model(qapp: QApplication, db: DatabaseManager):
    """Vérifie le modèle virtualisé spécifique à la vue par dossiers."""
    i18n = get_i18n()
    i18n.set_language("fr")

    # Ajouter des morceaux dans des dossiers distincts
    src = db.get_sources()[0]
    db.upsert_tracks_batch(
        [
            TrackRecord(
                source_ref="D:/Music/Rock/Queen/Bohemian.mp3",
                source_path="D:/Music/Rock/Queen/Bohemian.mp3",
                source_id=src.id,
                title="Bohemian Rhapsody",
                artist="Queen",
                album="A Night at the Opera",
                duration_seconds=354.0,
                format="mp3",
                file_size=12_500_000,
            ),
            TrackRecord(
                source_ref="D:/Music/Rock/Queen/RadioGaGa.mp3",
                source_path="D:/Music/Rock/Queen/RadioGaGa.mp3",
                source_id=src.id,
                title="Radio Ga Ga",
                artist="Queen",
                album="The Works",
                duration_seconds=345.0,
                format="mp3",
                file_size=11_200_000,
            ),
        ]
    )

    model = FolderTrackTableModel(db=db)
    model.set_folder("D:/Music/Rock/Queen", source_id=src.id, recursive=False)

    # Vérification de l'harmonisation stricte des colonnes entre les deux modèles
    assert FolderTrackTableModel.COLUMNS == TrackTableModel.COLUMNS

    assert model.rowCount() == 2
    assert model.columnCount() == 29

    # Colonnes harmonisées : Nom de fichier, Titre, Artiste, Album, Taille (colonne 15)...
    assert model.headerData(0, Qt.Orientation.Horizontal) == "Nom de fichier"
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Titre"
    assert model.headerData(15, Qt.Orientation.Horizontal) == "Taille"

    # Vérification des cellules
    assert model.data(model.index(0, 0), Qt.ItemDataRole.DisplayRole) == "Bohemian.mp3"
    assert "Mo" in str(model.data(model.index(0, 15), Qt.ItemDataRole.DisplayRole))

    # Test recherche dans le dossier
    model.set_search_query("Radio")
    assert model.rowCount() == 1
    assert model.data(model.index(0, 0), Qt.ItemDataRole.DisplayRole) == "RadioGaGa.mp3"

    model.set_search_query("")
    assert model.rowCount() == 2


def test_main_window_folder_navigation(qapp: QApplication, db: DatabaseManager):
    """Vérifie la navigation par dossiers dans la fenêtre principale."""
    i18n = get_i18n()
    i18n.set_language("fr")

    src = db.get_sources()[0]
    db.upsert_tracks_batch(
        [
            TrackRecord(
                source_ref="D:/Music/Pop/Abba/Waterloo.mp3",
                source_path="D:/Music/Pop/Abba/Waterloo.mp3",
                source_id=src.id,
                title="Waterloo",
                artist="Abba",
                format="mp3",
                duration_seconds=165.0,
                file_size=5_000_000,
            ),
        ]
    )

    window = MainWindow(db=db)

    # 1. Clic sur le bouton "Par dossiers" dans Bibliothèque
    assert window.btn_by_folder is not None
    assert "Par dossiers" in window.btn_by_folder.text()

    window.btn_by_folder.click()
    assert window.btn_by_folder.isChecked() is True
    assert window.stacked_widget.currentIndex() == 3

    # 2. Vérification de l'arborescence
    assert window.folder_tree.topLevelItemCount() >= 1
    root_item = window.folder_tree.topLevelItem(0)
    assert "Dossier Test" in root_item.text(0)

    # 3. Vérification de la présence de sous-dossiers dans l'arborescence (Pop -> Abba)
    child_count = root_item.childCount()
    assert child_count >= 1
    pop_node = root_item.child(0)
    assert "Pop" in pop_node.text(0)
    abba_node = pop_node.child(0)
    assert "Abba" in abba_node.text(0)

    # Sélectionner le dossier Abba (qui contient le fichier direct)
    window.folder_tree.setCurrentItem(abba_node)
    assert window.right_stack.currentIndex() == 1
    assert "Abba" in window.lbl_folder_breadcrumb.text()
    assert window.folder_table_model.rowCount() == 1

    # 4. Sélectionner le dossier parent Pop (0 direct, 1 récursif)
    window.folder_tree.setCurrentItem(pop_node)
    assert window.folder_table_model.rowCount() == 0
    window.cb_recursive.setChecked(True)
    assert window.folder_table_model.rowCount() == 1

    # 5. Test changement de langue dynamique sur la page Par dossiers
    window.combo_language.setCurrentIndex(window.combo_language.findData("en"))
    assert "By Folders" in window.btn_by_folder.text()
    assert "Folder Explorer" in window.lbl_folders_page_title.text()
    assert "Include subfolders" in window.cb_recursive.text()
    window.combo_language.setCurrentIndex(window.combo_language.findData("fr"))
    assert "Par dossiers" in window.btn_by_folder.text()

    # 6. Vérification de la hauteur fixe du panneau haut et du redimensionnement interactif des colonnes
    from PySide6.QtWidgets import QHeaderView

    folders_page = window.stacked_widget.widget(3)
    assert folders_page is not None
    # Vérifier que les colonnes de l'arborescence et du tableau sont interactives (permettent la réduction)
    assert window.folder_tree.header().stretchLastSection() is False
    assert window.folder_tree.header().sectionResizeMode(0) == QHeaderView.ResizeMode.Interactive
    assert window.folder_tree.header().sectionResizeMode(1) == QHeaderView.ResizeMode.Interactive

    # 7. Vérification que les colonnes sont déplaçables et masquables
    assert window.table_view.horizontalHeader().sectionsMovable() is True
    assert window.folder_table_view.horizontalHeader().sectionsMovable() is True

    # Test masquage / réaffichage d'une colonne
    window._toggle_table_column(window.table_view, 1, False, "all_tracks")
    assert window.table_view.isColumnHidden(1) is True
    window._toggle_table_column(window.table_view, 1, True, "all_tracks")
    assert window.table_view.isColumnHidden(1) is False

    # Test afficher toutes les colonnes
    window._show_all_columns(window.table_view, "all_tracks")
    for c in range(29):
        assert window.table_view.isColumnHidden(c) is False

    # Test réinitialisation colonnes par défaut
    window._reset_default_columns(window.table_view, "all_tracks")
    assert window.table_view.isColumnHidden(0) is False  # file_name visible
    assert window.table_view.isColumnHidden(1) is False  # title visible
    assert window.table_view.isColumnHidden(4) is True  # album_artist masqué par défaut
    assert window.table_view.isColumnHidden(28) is True  # id masqué par défaut

    # 8. Vérification du fil d'Ariane cliquable
    assert hasattr(window.lbl_folder_breadcrumb, "clicked")
    from unittest.mock import patch

    with patch.object(window, "_on_open_current_folder_explorer") as mock_open:
        window.lbl_folder_breadcrumb.clicked.emit()
        assert mock_open.called

    # 9. Vérification du menu contextuel de la source (Synchroniser)
    sources = window.db.get_sources()
    assert len(sources) >= 1
    src_menu = window._create_source_context_menu(sources[0])
    action_texts = [a.text() for a in src_menu.actions()]
    assert any("Synchroniser" in t for t in action_texts)
    assert any("Explorateur" in t for t in action_texts)

    window.close()


def test_splash_screen(qapp: QApplication):
    """Vérifie le cycle de vie de l'écran de chargement SplashScreen."""
    from PySide6.QtWidgets import QWidget

    from amso.ui.views.splash_screen import SplashScreen

    splash = SplashScreen()
    assert splash.progress_bar.value() == 0
    assert "0%" in splash.lbl_percent.text()

    splash.set_progress(45, "Chargement en cours...")
    assert splash.progress_bar.value() == 45
    assert "45%" in splash.lbl_percent.text()
    assert splash.lbl_status.text() == "Chargement en cours..."

    dummy_win = QWidget()
    splash.finish(dummy_win)
    assert not splash.isVisible()


def test_delete_track_dialog(qapp: QApplication, tmp_path) -> None:
    """Vérifie le dialogue de suppression de piste et l'envoi à la corbeille."""
    from amso.ui.dialogs.delete_track_dialog import DeleteTrackDialog, send_file_to_trash

    track = TrackRecord(
        id=123,
        source_ref="D:/Music/test.flac",
        source_path="D:/Music/test.flac",
        title="Test Song",
        artist="Test Artist",
    )

    # 1. Choix 'ignore'
    dlg_ignore = DeleteTrackDialog(track)
    assert dlg_ignore.action is None
    dlg_ignore._on_choose_ignore()
    assert dlg_ignore.action == "ignore"
    dlg_ignore.close()

    # 2. Choix 'trash'
    dlg_trash = DeleteTrackDialog(track)
    dlg_trash._on_choose_trash()
    assert dlg_trash.action == "trash"
    dlg_trash.close()

    # 3. Fonction send_file_to_trash
    test_file = tmp_path / "sample.mp3"
    test_file.write_text("audio content")
    assert test_file.exists()
    res = send_file_to_trash(str(test_file))
    assert res is True
    assert not test_file.exists()


def test_folder_tree_collapsed_by_default(qapp: QApplication, db: DatabaseManager) -> None:
    """Vérifie que l'arborescence des sources dans la vue dossiers est repliée par défaut."""
    window = MainWindow(db=db)
    # Vérifie les éléments racines de l'arborescence
    root_count = window.folder_tree.topLevelItemCount()
    assert root_count >= 1
    for i in range(root_count):
        item = window.folder_tree.topLevelItem(i)
        assert item is not None
        assert not item.isExpanded()
        # L'icône doit être 💾, ☁️ ou 🗑️ (Corbeille)
        assert "💾" in item.text(0) or "☁️" in item.text(0) or "🗑️" in item.text(0)
    window.close()


def test_trash_view_and_restore(qapp: QApplication, db: DatabaseManager) -> None:
    """Vérifie l'affichage de la Corbeille sous les sources et la restauration de morceaux."""
    db.ignore_track("D:/Music/song_a.mp3", "D:/Music/song_a.mp3")
    db.ignore_track("D:/Music/song_b.mp3", "D:/Music/song_b.mp3")

    window = MainWindow(db=db)
    root_count = window.folder_tree.topLevelItemCount()
    assert root_count >= 2

    # Le dernier élément racine est la Corbeille
    trash_item = window.folder_tree.topLevelItem(root_count - 1)
    assert trash_item is not None
    assert "🗑️" in trash_item.text(0)
    assert trash_item.text(1) == "2"

    # Sélection de la Corbeille
    window.folder_tree.setCurrentItem(trash_item)
    assert window.right_stack.currentIndex() == 2
    assert window.trash_table.rowCount() == 2

    # Restauration d'un morceau
    item_data = window.trash_table.item(0, 0).data(Qt.ItemDataRole.UserRole)
    assert item_data is not None
    window._restore_ignored_items([item_data])

    assert db.count_ignored_tracks() == 1
    assert window.trash_table.rowCount() == 1

    window.close()


def test_effects_combo_and_styles(qapp: QApplication) -> None:
    """Vérifie le bon fonctionnement du sélecteur d'effets visuels et des styles de sliders."""
    from PySide6.QtWidgets import QComboBox

    from amso.ui.styles import seek_slider_qss, volume_label_qss, volume_slider_qss
    from amso.ui.widgets.effects_combo import get_available_effects, populate_effects_combo

    # Effets disponibles
    effects = get_available_effects()
    assert len(effects) == 9
    assert effects[0][0] == "particles"

    # Peuplement de la combo
    combo = QComboBox()
    populate_effects_combo(combo, current_effect="warp")
    assert combo.count() == 9
    assert combo.currentData() == "warp"

    # QSS sliders et labels
    vol_qss = volume_slider_qss(groove_height=5, handle_size=12)
    assert "QSlider::groove:horizontal" in vol_qss
    assert "height: 5px;" in vol_qss
    assert "width: 12px;" in vol_qss

    seek_qss = seek_slider_qss(groove_height=6, handle_size=14)
    assert "QSlider::groove:horizontal" in seek_qss
    assert "height: 6px;" in seek_qss

    lbl_qss = volume_label_qss(min_width=38)
    assert "min-width: 38px;" in lbl_qss
