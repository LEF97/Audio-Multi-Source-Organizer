"""Tests unitaires pour les composants PySide6 (modèles virtualisés et interface)."""

import os
from pathlib import Path

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
    get_i18n().set_language("fr")
    assert format_duration(65) == "1:05"
    assert format_duration(3665) == "1:01:05"
    assert format_duration(86400 + 3665) == "1j 01:01:05"
    assert format_duration(3966 * 3600 + 15 * 60 + 59) == "165j 06:15:59"
    assert format_duration(2074, always_hours=True) == "0:34:34"
    assert format_duration(0, always_hours=True) == "0:00:00"
    assert format_duration(None) == "--:--"
    assert format_duration(0) == "--:--"

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
    assert model.columnCount() == 30

    # Vérification des en-têtes en français
    assert model.headerData(0, Qt.Orientation.Horizontal) == " "
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Nom de fichier"
    assert model.headerData(2, Qt.Orientation.Horizontal) == "Titre"
    assert model.headerData(3, Qt.Orientation.Horizontal) == "Artiste"
    assert model.headerData(10, Qt.Orientation.Horizontal) == "Durée"

    # Vérification de la dynamique de changement de langue
    i18n.set_language("en")
    model.notify_language_changed()
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Filename"
    assert model.headerData(2, Qt.Orientation.Horizontal) == "Title"
    assert model.headerData(3, Qt.Orientation.Horizontal) == "Artist"
    assert model.headerData(10, Qt.Orientation.Horizontal) == "Duration"

    # Retour au français
    i18n.set_language("fr")
    model.notify_language_changed()

    # Vérification des cellules (ligne 0 : Queen)
    idx_title = model.index(0, 2)
    assert model.data(idx_title, Qt.ItemDataRole.DisplayRole) == "Bohemian Rhapsody"

    idx_artist = model.index(0, 3)
    assert model.data(idx_artist, Qt.ItemDataRole.DisplayRole) == "Queen"

    idx_duration = model.index(0, 10)
    assert model.data(idx_duration, Qt.ItemDataRole.DisplayRole) == "5:54"

    # Tri par titre décroissant (colonne 2 = titre)
    model.sort(2, Qt.SortOrder.DescendingOrder)
    assert model.data(model.index(0, 2), Qt.ItemDataRole.DisplayRole) == "Stairway to Heaven"

    # Filtre recherche FTS
    model.set_filter(search_query="Queen")
    assert model.rowCount() == 1
    assert model.data(model.index(0, 2), Qt.ItemDataRole.DisplayRole) == "Bohemian Rhapsody"


def test_main_window_instantiation(qapp: QApplication, db: DatabaseManager):
    """Vérifie la création correcte de la fenêtre principale et du sélecteur de langue."""
    i18n = get_i18n()
    i18n.set_language("fr")

    window = MainWindow(db=db)
    assert "AMSO" in window.windowTitle()
    assert __version__ in window.windowTitle()
    # Chargement différé : la table n'est remplie qu'à l'affichage de la page, mais le compteur est exact.
    assert window.table_model.rowCount() == 0
    assert window.table_model.display_count() == 2
    assert not hasattr(window, "btn_all_tracks")
    assert not hasattr(window, "drawer_library")
    assert window.btn_by_folder.parentWidget() == window.drawer_player.content_widget
    assert window.btn_player.isChecked() is True
    window.btn_by_folder.click()
    assert window.btn_by_folder.isChecked() is True
    assert "Bibliothèque" in window.btn_by_folder.text()

    # Vérification du sélecteur de langue
    assert window.combo_language is not None
    assert window.combo_language.count() >= 4

    # Changement dynamique de langue vers l'anglais
    en_idx = window.combo_language.findData("en")
    assert en_idx >= 0
    window.combo_language.setCurrentIndex(en_idx)
    assert "By Folders" in window.btn_by_folder.text()
    assert "Duplicates" in window.btn_duplicates.text()

    # Retour au français
    fr_idx = window.combo_language.findData("fr")
    window.combo_language.setCurrentIndex(fr_idx)
    assert "Bibliothèque" in window.btn_by_folder.text()

    # Test clic sur Doublons
    window.btn_duplicates.click()
    assert window.btn_duplicates.isChecked() is True
    assert window.stacked_widget.currentIndex() == 0

    # Test clic sur Paramètres > Général (page dédiée avec langue)
    window.btn_settings_general.click()
    assert window.btn_settings_general.isChecked() is True
    assert window.stacked_widget.currentIndex() == 1

    # Test retour sur Par dossiers
    window.btn_by_folder.click()
    assert window.btn_by_folder.isChecked() is True
    assert window.stacked_widget.currentIndex() == 2

    # Test état des tiroirs par défaut : seul Lecteur est ouvert, tous les autres sont fermés
    assert window.drawer_player._is_expanded is True
    assert window.drawer_games._is_expanded is False
    assert window.drawer_tools._is_expanded is False
    assert not hasattr(window, "drawer_stats")
    assert not hasattr(window, "drawer_sources")
    assert window.drawer_library_mgmt._is_expanded is False
    assert window.drawer_settings._is_expanded is False
    assert window.drawer_tools.content_widget.isHidden() is True
    window.drawer_tools.toggle()
    assert window.drawer_tools._is_expanded is True
    assert window.drawer_tools.content_widget.isHidden() is False
    window.drawer_tools.toggle()
    assert window.drawer_tools._is_expanded is False

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
    assert model.total_duration_seconds() == 699.0
    assert model.columnCount() == 30

    # Colonnes harmonisées : Indicateur lecture, Nom de fichier, Titre, Artiste, Album, Taille (colonne 16)...
    assert model.headerData(0, Qt.Orientation.Horizontal) == " "
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Nom de fichier"
    assert model.headerData(2, Qt.Orientation.Horizontal) == "Titre"
    assert model.headerData(16, Qt.Orientation.Horizontal) == "Taille"

    # Vérification des cellules
    assert model.data(model.index(0, 0), Qt.ItemDataRole.DisplayRole) == ""
    assert model.data(model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "Bohemian.mp3"
    assert "Mo" in str(model.data(model.index(0, 16), Qt.ItemDataRole.DisplayRole))

    # Test recherche dans le dossier
    model.set_search_query("Radio")
    assert model.rowCount() == 1
    assert model.total_duration_seconds() == 345.0
    assert model.data(model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "RadioGaGa.mp3"

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

    # 1. Clic sur le bouton "Bibliothèque" dans le tiroir Lecteur
    assert window.btn_by_folder is not None
    assert "Bibliothèque" in window.btn_by_folder.text()

    window.btn_by_folder.click()
    assert window.btn_by_folder.isChecked() is True
    assert window.stacked_widget.currentIndex() == 2

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

    # 5. Test changement de langue dynamique sur la page Bibliothèque
    window.combo_language.setCurrentIndex(window.combo_language.findData("en"))
    assert "By Folders" in window.btn_by_folder.text()
    assert "Folder Explorer" in window.lbl_folders_page_title.text()
    assert "Include subfolders" in window.cb_recursive.text()
    window.combo_language.setCurrentIndex(window.combo_language.findData("fr"))
    assert "Bibliothèque" in window.btn_by_folder.text()

    # 6. Vérification de la hauteur fixe du panneau haut et du redimensionnement interactif des colonnes
    from PySide6.QtWidgets import QHeaderView

    folders_page = window.stacked_widget.widget(3)
    assert folders_page is not None
    # Vérifier que les colonnes de l'arborescence et du tableau sont interactives (permettent la réduction)
    assert window.folder_tree.header().stretchLastSection() is False
    assert window.folder_tree.header().sectionResizeMode(0) == QHeaderView.ResizeMode.Stretch
    assert window.folder_tree.header().sectionResizeMode(1) == QHeaderView.ResizeMode.Fixed

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
    for c in range(30):
        assert window.table_view.isColumnHidden(c) is False

    # Test réinitialisation colonnes par défaut
    window._reset_default_columns(window.table_view, "all_tracks")
    assert window.table_view.isColumnHidden(0) is False  # is_playing visible
    assert window.table_view.isColumnHidden(1) is False  # file_name visible
    assert window.table_view.isColumnHidden(2) is False  # title visible
    assert window.table_view.isColumnHidden(5) is True  # album_artist masqué par défaut
    assert window.table_view.isColumnHidden(29) is True  # id masqué par défaut

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
    assert len(effects) == 10
    assert effects[0][0] == "none"
    assert effects[-1][0] == "random"

    # Peuplement de la combo
    combo = QComboBox()
    populate_effects_combo(combo, current_effect="warp")
    assert combo.count() == 10
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


def test_track_model_chargement_differe_ne_lit_pas_la_base_avant_set_filter(qapp: QApplication, db: DatabaseManager):
    """Tri et reload_data ne chargent rien tant que la page n'est pas affichée ; le compteur reste exact."""
    model = TrackTableModel(db=db, defer_loading=True)

    model.sort(2, Qt.SortOrder.DescendingOrder)
    model.reload_data()
    assert model.rowCount() == 0
    assert model.display_count() == 2

    model.set_filter()
    assert model.rowCount() == 2
    assert model.display_count() == 2
    # Le tri demandé pendant le différé est appliqué au premier chargement
    assert model.data(model.index(0, 2), Qt.ItemDataRole.DisplayRole) == "Stairway to Heaven"


def test_folders_page_player_header_and_session_folder_restore(
    qapp: QApplication, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Vérifie le lecteur intégré en haut de Par dossiers et la réouverture du dossier de lecture au démarrage."""
    playlist_path = tmp_path / "saved_playlist.json"
    monkeypatch.setattr("amso.ui.pages.session_state.get_saved_playlist_path", lambda: playlist_path)

    db_file = str(tmp_path / "test_restore_folder.db")
    db1 = DatabaseManager(db_file)
    src = db1.add_source(SourceType.LOCAL, "Dossier Test", "D:/Music")
    db1.upsert_tracks_batch(
        [
            TrackRecord(
                source_ref="D:/Music/Rock/PinkFloyd/1973_DSOTM/Time.mp3",
                source_path="D:/Music/Rock/PinkFloyd/1973_DSOTM/Time.mp3",
                source_id=src.id,
                title="Time",
                artist="Pink Floyd",
                album="The Dark Side of the Moon",
                duration_seconds=413.0,
                format="mp3",
            ),
            TrackRecord(
                source_ref="D:/Music/Rock/PinkFloyd/1973_DSOTM/Money.mp3",
                source_path="D:/Music/Rock/PinkFloyd/1973_DSOTM/Money.mp3",
                source_id=src.id,
                title="Money",
                artist="Pink Floyd",
                album="The Dark Side of the Moon",
                duration_seconds=382.0,
                format="mp3",
            ),
        ]
    )
    folder_tracks = db1.get_tracks_by_folder("D:/Music/Rock/PinkFloyd/1973_DSOTM", source_id=src.id, recursive=False)
    assert len(folder_tracks) == 2

    expected_title = folder_tracks[1].title
    # Session 1 : lecture dans le sous-dossier 1973_DSOTM puis fermeture
    win1 = MainWindow(db=db1)
    assert hasattr(win1, "folders_player_header")
    win1.player_service.load_playlist(folder_tracks, current_index=1, initial_position_ms=15000)
    assert win1.folders_player_header.lbl_track_title.text() == expected_title
    assert "2" in win1.folders_player_header.lbl_playlist_stats.text()
    win1.close()

    # Session 2 : réouverture -> la playlist ET le dossier 1973_DSOTM sont restaurés et dépliés dans l'arbre
    db2 = DatabaseManager(db_file)
    win2 = MainWindow(db=db2)
    assert len(win2.player_service.playlist) == 2
    assert win2.player_service.current_track is not None
    assert win2.player_service.current_track.title == expected_title
    assert win2.folders_player_header.lbl_track_title.text() == expected_title

    selected_item = win2.folder_tree.currentItem()
    assert selected_item is not None
    item_data = selected_item.data(0, Qt.ItemDataRole.UserRole)
    assert isinstance(item_data, dict)
    assert item_data.get("folder_path") == "D:/Music/Rock/PinkFloyd/1973_DSOTM"

    # Toute la hiérarchie parente doit être dépliée pour rendre le dossier visible
    parent = selected_item.parent()
    assert parent is not None
    while parent is not None:
        assert parent.isExpanded() is True
        parent = parent.parent()

    # Le tableau de droite de la page Par dossiers affiche directement les pistes de ce dossier
    assert win2.folder_table_model.rowCount() == 2
    assert "1973_DSOTM" in win2.lbl_folder_breadcrumb.text()
    win2.close()


def test_session_restore_positions_on_cue_and_m3u_playlist_in_tree(
    qapp: QApplication, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Vérifie qu'au redémarrage, une lecture issue d'un CUE ou d'une playlist M3U sélectionne le noeud CUE/playlist."""
    from types import SimpleNamespace

    playlist_path = tmp_path / "saved_playlist_cue.json"
    monkeypatch.setattr("amso.ui.pages.session_state.get_saved_playlist_path", lambda: playlist_path)

    db_file = str(tmp_path / "test_restore_cue_m3u.db")
    db1 = DatabaseManager(db_file)
    src = db1.add_source(SourceType.LOCAL, "Dossier Test", "D:/Music")
    assert src.id is not None
    db1.upsert_tracks_batch(
        [
            TrackRecord(
                source_ref="D:/Music/Radiohead/Tribute/album_full.mp3",
                source_path="D:/Music/Radiohead/Tribute/album_full.mp3",
                source_id=src.id,
                title="RADIOHEAD tribute",
                artist="Radiohead",
                duration_seconds=1200.0,
                format="mp3",
            ),
            TrackRecord(
                source_ref="D:/Music/Mix/Song1.mp3",
                source_path="D:/Music/Mix/Song1.mp3",
                source_id=src.id,
                title="Song 1",
                artist="Artist 1",
                duration_seconds=200.0,
                format="mp3",
            ),
            TrackRecord(
                source_ref="D:/Music/Mix/Song2.mp3",
                source_path="D:/Music/Mix/Song2.mp3",
                source_id=src.id,
                title="Song 2",
                artist="Artist 2",
                duration_seconds=210.0,
                format="mp3",
            ),
        ]
    )

    cue_id = db1.upsert_playlist(
        source_id=src.id,
        file_path="D:/Music/Radiohead/Tribute/tribute.cue",
        file_name="tribute.cue",
        folder_path="D:/Music/Radiohead/Tribute",
        format_str="cue",
        file_mtime=1.0,
        file_size=500,
        entries=[
            SimpleNamespace(
                position=1,
                raw_path="album_full.mp3",
                resolved_path="D:/Music/Radiohead/Tribute/album_full.mp3",
                title="Intro",
                artist="Radiohead",
                duration_seconds=139.0,
                is_missing=False,
                start_ms=0,
                end_ms=139000,
            ),
            SimpleNamespace(
                position=2,
                raw_path="album_full.mp3",
                resolved_path="D:/Music/Radiohead/Tribute/album_full.mp3",
                title="There There",
                artist="Radiohead",
                duration_seconds=390.0,
                is_missing=False,
                start_ms=139000,
                end_ms=529000,
            ),
        ],
    )
    m3u_id = db1.upsert_playlist(
        source_id=src.id,
        file_path="D:/Music/Mix/best_of.m3u",
        file_name="best_of.m3u",
        folder_path="D:/Music/Mix",
        format_str="m3u",
        file_mtime=1.0,
        file_size=200,
        entries=[
            SimpleNamespace(
                position=1,
                raw_path="Song1.mp3",
                resolved_path="D:/Music/Mix/Song1.mp3",
                title="Song 1",
                artist="Artist 1",
                duration_seconds=200.0,
                is_missing=False,
                start_ms=None,
                end_ms=None,
            ),
            SimpleNamespace(
                position=2,
                raw_path="Song2.mp3",
                resolved_path="D:/Music/Mix/Song2.mp3",
                title="Song 2",
                artist="Artist 2",
                duration_seconds=210.0,
                is_missing=False,
                start_ms=None,
                end_ms=None,
            ),
        ],
    )

    # 1. Test restauration d'une feuille CUE (même sans playlist_id pré-enregistré)
    cue_tracks = db1.get_playlist_tracks(cue_id)
    win1 = MainWindow(db=db1)
    win1.player_service.load_playlist(cue_tracks, current_index=1, initial_position_ms=5000)
    win1.close()

    db2 = DatabaseManager(db_file)
    win2 = MainWindow(db=db2)
    cur_item = win2.folder_tree.currentItem()
    assert cur_item is not None
    cur_data = cur_item.data(0, Qt.ItemDataRole.UserRole)
    assert cur_data.get("is_playlist") is True
    assert cur_data.get("playlist_id") == cue_id
    assert "tribute.cue" in win2.lbl_folder_breadcrumb.text()
    assert win2.folder_table_model.rowCount() == 2
    assert win2.folder_table_model.current_track_row() == 1
    idx_active = win2.folder_table_model.index(1, 0)
    idx_inactive = win2.folder_table_model.index(0, 0)
    idx_active_fn = win2.folder_table_model.index(1, 1)
    assert win2.folder_table_model.data(idx_active, Qt.ItemDataRole.DisplayRole) in ("▶", "⏸", "⏹")
    assert win2.folder_table_model.data(idx_inactive, Qt.ItemDataRole.DisplayRole) == ""
    assert not str(win2.folder_table_model.data(idx_active_fn, Qt.ItemDataRole.DisplayRole)).startswith(("▶", "⏸", "⏹"))
    assert win2.folder_table_model.data(idx_active, Qt.ItemDataRole.ForegroundRole).name().upper() == "#38BDF8"
    assert win2.folder_table_model.data(idx_active, Qt.ItemDataRole.FontRole).bold() is True
    # La sélection de lignes dans la table ne doit pas impacter l'indicateur de lecture
    win2.folder_table_view.selectRow(0)
    assert win2.folder_table_model.current_track_row() == 1
    assert win2.folder_table_model.data(idx_active, Qt.ItemDataRole.ForegroundRole).name().upper() == "#38BDF8"

    # Le changement de piste via le lecteur actualise l'indicateur ▶/⏸ sans déplacer l'ascenseur
    scroll_calls: list[object] = []
    monkeypatch.setattr(win2.folder_table_view, "scrollTo", lambda idx, hint=None: scroll_calls.append(idx))
    win2.player_service.load_index(0)
    assert win2.folder_table_model.current_track_row() == 0
    assert win2.folder_table_model.data(idx_inactive, Qt.ItemDataRole.DisplayRole) in ("▶", "⏸", "⏹")
    assert scroll_calls == []

    # 2. Test restauration d'une playlist M3U
    m3u_tracks = db2.get_playlist_tracks(m3u_id)
    win2.player_service.load_playlist(m3u_tracks, current_index=0, initial_position_ms=1000)
    win2.close()

    db3 = DatabaseManager(db_file)
    win3 = MainWindow(db=db3)
    cur_item_m3u = win3.folder_tree.currentItem()
    assert cur_item_m3u is not None
    m3u_data = cur_item_m3u.data(0, Qt.ItemDataRole.UserRole)
    assert m3u_data.get("is_playlist") is True
    assert m3u_data.get("playlist_id") == m3u_id
    assert "best_of.m3u" in win3.lbl_folder_breadcrumb.text()
    assert win3.folder_table_model.rowCount() == 2
    assert win3.folder_table_model.current_track_row() == 0
    win3.close()


def test_playlist_table_model_refreshes_play_icon_on_state_changed(qapp: QApplication, db: DatabaseManager) -> None:
    """Vérifie le rafraîchissement immédiat de l'icône ▶/⏸ lors de state_changed et la largeur étroite (30 px)."""
    from PySide6.QtCore import QObject, Signal

    from amso.ui.models import PlaylistTableModel

    class _DummyPlayer(QObject):
        playlist_updated = Signal()
        track_changed = Signal(object)
        state_changed = Signal(str)

        def __init__(self) -> None:
            super().__init__()
            self.playlist = db.get_tracks()[0]
            self.current_index = 0
            self.is_playing = False

    player = _DummyPlayer()
    model = PlaylistTableModel(player)
    assert PlaylistTableModel.COLUMNS[0][2] == 30
    assert FolderTrackTableModel.COLUMNS[0][2] == 30

    changes: list[tuple[int, int]] = []
    model.dataChanged.connect(lambda tl, br, _roles=None: changes.append((tl.row(), br.row())))

    assert model.data(model.index(0, 0), Qt.ItemDataRole.DisplayRole) == "⏸"
    player.is_playing = True
    player.state_changed.emit("playing")
    assert len(changes) == 1
    assert model.data(model.index(0, 0), Qt.ItemDataRole.DisplayRole) == "▶"


def test_duplicates_page_uses_active_playlist_only_and_empty_message(qapp: QApplication, db: DatabaseManager) -> None:
    """Vérifie que Doublons détectés analyse uniquement la liste de lecture et affiche un message si elle est vide."""
    get_i18n().set_language("fr")
    src = db.get_sources()[0]

    # Doublons en base hors playlist (ne doivent pas apparaître)
    db.upsert_tracks_batch(
        [
            TrackRecord(
                source_ref="D:/Music/DbDup1.mp3",
                source_path="D:/Music/DbDup1.mp3",
                source_id=src.id,
                title="Only In DB",
                artist="Some Artist",
                file_hash="hash_db_only",
                duration_seconds=180.0,
            ),
            TrackRecord(
                source_ref="D:/Music/DbDup2.mp3",
                source_path="D:/Music/DbDup2.mp3",
                source_id=src.id,
                title="Only In DB",
                artist="Some Artist",
                file_hash="hash_db_only",
                duration_seconds=180.0,
            ),
        ]
    )

    window = MainWindow(db=db)
    window.player_service.clear_playlist()

    # 1. Liste de lecture vide -> message centré affiché et barre supérieure masquée
    window.btn_duplicates.click()
    assert window.tracks_stack.currentWidget() == window.tracks_empty_widget
    assert window.tracks_top_bar.isHidden() is True
    assert window.track_count_label.text() == ""
    assert "liste de lecture" in window.lbl_tracks_empty_message.text().lower()
    assert window.table_model.rowCount() == 0

    # 2. Liste de lecture avec un doublon + une piste unique -> seuls les 2 doublons de la playlist sont affichés
    pl_tracks = [
        TrackRecord(
            id=101,
            source_ref="D:/Music/A1.mp3",
            source_path="D:/Music/A1.mp3",
            title="Track A",
            artist="Artist X",
            file_hash="hash_pl_1",
            duration_seconds=200.0,
        ),
        TrackRecord(
            id=102,
            source_ref="D:/Music/B.mp3",
            source_path="D:/Music/B.mp3",
            title="Unique Track",
            artist="Artist Y",
            file_hash="hash_unique",
            duration_seconds=210.0,
        ),
        TrackRecord(
            id=103,
            source_ref="D:/Music/A2.mp3",
            source_path="D:/Music/A2.mp3",
            title="Track A",
            artist="Artist X",
            file_hash="hash_pl_1",
            duration_seconds=200.0,
        ),
    ]
    window.player_service.load_playlist(pl_tracks, current_index=0)
    assert window.tracks_top_bar.isHidden() is False
    assert window.track_count_label.text() == "2 doublons / 3 titres"
    assert window.tracks_stack.currentWidget() == window.table_view
    assert window.table_model.rowCount() == 2
    displayed_titles = {window.table_model.get_track_at(r).title for r in range(window.table_model.rowCount())}
    assert displayed_titles == {"Track A"}
    window.close()


def test_load_cover_async_notifies_all_concurrent_callbacks(
    qapp: QApplication, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Vérifie que deux vues demandant la même pochette (ex. Liste de lecture et Bibliothèque) sont toutes deux notifiées."""
    from PySide6.QtGui import QColor, QImage

    from amso.ui.views import cover_helper

    audio_file = tmp_path / "song.mp3"
    audio_file.write_bytes(b"dummy")

    img = QImage(16, 16, QImage.Format.Format_RGBA8888)
    img.fill(QColor("#38BDF8"))
    buf_path = tmp_path / "cover.png"
    img.save(str(buf_path))
    raw_png = buf_path.read_bytes()

    cover_helper.invalidate_cover_cache()
    monkeypatch.setattr(cover_helper, "extract_cover_art", lambda _p: raw_png)

    trk = TrackRecord(source_ref=str(audio_file), source_path=str(audio_file), title="Song")
    calls_a: list[str] = []
    calls_b: list[str] = []

    cover_helper.load_cover_async(trk, size=56, radius=8, callback=lambda p, _pm: calls_a.append(p))
    cover_helper.load_cover_async(trk, size=56, radius=8, callback=lambda p, _pm: calls_b.append(p))

    cover_helper.wait_for_cover_workers(timeout_ms=2000)
    qapp.processEvents()

    assert calls_a == [str(audio_file)]
    assert calls_b == [str(audio_file)]


def test_save_playlist_button_and_immediate_source_indexing(
    qapp: QApplication, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Vérifie l'activation du bouton Enregistrer et l'indexation immédiate si enregistré dans une source."""
    from PySide6.QtWidgets import QFileDialog

    from amso.core.database import SourceType

    music_dir = tmp_path / "MusicSrc"
    music_dir.mkdir()
    song = music_dir / "track.mp3"
    song.write_bytes(b"mp3")

    db_mgr = DatabaseManager(str(tmp_path / "save_pl.db"))
    src = db_mgr.add_source(SourceType.LOCAL, "MusicSrc", str(music_dir))
    trk = TrackRecord(
        source_ref=str(song),
        source_path=str(song),
        source_id=src.id,
        title="Track",
        artist="Artist",
        duration_seconds=120.0,
    )
    db_mgr.upsert_tracks_batch([trk])

    window = MainWindow(db=db_mgr)
    window.player_service.clear_playlist()
    assert window.page_playlist.btn_save_playlist.isEnabled() is False
    assert window.folders_player_header.btn_save_playlist.isEnabled() is False

    window.player_service.load_playlist([trk], current_index=0)
    assert window.page_playlist.btn_save_playlist.isEnabled() is True
    assert window.folders_player_header.btn_save_playlist.isEnabled() is True

    dest_file = music_dir / "ma_liste.m3u8"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(dest_file), "M3U8 UTF-8 (*.m3u8)"),
    )
    window.page_playlist.btn_save_playlist.click()

    assert dest_file.exists()
    indexed = db_mgr.get_playlists(source_id=src.id)
    assert len(indexed) == 1
    assert indexed[0].file_name == "ma_liste.m3u8"
    window.close()


def test_cover_transition_label_and_settings(qapp: QApplication, db: DatabaseManager) -> None:
    """Vérifie l'anti-clignotement (même hash = pas d'animation) et la config des transitions."""
    from PySide6.QtGui import QPixmap

    from amso.core.config import get_config_manager
    from amso.core.i18n import tr
    from amso.ui.widgets.cover_transition_label import CoverTransitionLabel

    lbl = CoverTransitionLabel()
    pix_a = QPixmap(64, 64)
    pix_b = QPixmap(64, 64)

    # Premier affichage : pas d'animation
    lbl.set_cover_pixmap(pix_a, cover_hash=111, transition="fade", animate=True)
    assert lbl._animating is False

    # Même hash : aucune transition déclenchée (zéro clignotement)
    lbl.set_cover_pixmap(pix_a, cover_hash=111, transition="fade", animate=True)
    assert lbl._animating is False

    # Hash différent avec transition : animation démarrée
    lbl.set_cover_pixmap(pix_b, cover_hash=222, transition="slide", animate=True)
    assert lbl._animating is True

    # Mode 'none' : pas d'animation même si hash différent
    lbl.set_cover_pixmap(pix_a, cover_hash=333, transition="none", animate=True)
    assert lbl._animating is False

    # Vérification de l'intégration dans Paramètres > Lecteur + titre Bibliothèque
    window = MainWindow(db=db)
    assert window.folders_player_header.lbl_page_title.text() == tr("sidebar.drawer_library")
    cfg = get_config_manager()
    window._cover_trans_radios["zoom"][0].setChecked(True)
    assert cfg.get_cover_transition() == "zoom"
    window._cover_trans_radios["fade"][0].setChecked(True)
    assert cfg.get_cover_transition() == "fade"
    window.close()


def test_load_folder_cover_async_loads_artist_folder_image(qapp: QApplication, tmp_path: Path) -> None:
    """Vérifie que load_folder_cover_async charge l'image d'un dossier (ex. folder.png d'un dossier artiste)."""
    from PySide6.QtGui import QColor, QImage

    from amso.ui.views import cover_helper

    artist_dir = tmp_path / "Oldfield, Mike"
    artist_dir.mkdir()

    img = QImage(24, 24, QImage.Format.Format_RGBA8888)
    img.fill(QColor("#F97316"))
    img.save(str(artist_dir / "folder.png"))

    cover_helper.invalidate_cover_cache()
    received: list[tuple[str, object]] = []

    immediate = cover_helper.load_folder_cover_async(
        str(artist_dir),
        size=136,
        radius=10,
        callback=lambda p, pix: received.append((p, pix)),
    )
    assert not immediate.isNull()

    cover_helper.wait_for_cover_workers(timeout_ms=2000)
    qapp.processEvents()

    assert len(received) == 1
    assert received[0][0] == str(artist_dir)
    default_pix = cover_helper.get_default_cover_pixmap(136, 10)
    assert received[0][1].toImage() != default_pix.toImage()


def test_folders_page_displays_artist_folder_cover_when_no_direct_tracks(qapp: QApplication, tmp_path: Path) -> None:
    """Vérifie qu'un dossier artiste sans piste directe affiche son image folder/cover dans la bibliothèque."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QImage
    from PySide6.QtWidgets import QTreeWidgetItem

    from amso.ui.views import cover_helper

    artist_dir = tmp_path / "Artist"
    album_dir = artist_dir / "Album"
    album_dir.mkdir(parents=True)

    img = QImage(24, 24, QImage.Format.Format_RGBA8888)
    img.fill(QColor("#10B981"))
    img.save(str(artist_dir / "folder.png"))

    song = album_dir / "01.mp3"
    song.write_bytes(b"mp3")

    db = DatabaseManager(tmp_path / "lib.db")
    src = db.add_source(SourceType.LOCAL, "Music", str(tmp_path))
    db.upsert_tracks_batch(
        [
            TrackRecord(
                source_id=src.id,
                source_type=SourceType.LOCAL,
                source_ref=str(song),
                source_path=str(song),
                folder_path=str(album_dir),
                file_name="01.mp3",
                title="Track 1",
            )
        ]
    )

    cover_helper.invalidate_cover_cache()
    window = MainWindow(db=db)
    window.cb_recursive.setChecked(False)

    item = QTreeWidgetItem(["Artist", "1"])
    item.setData(0, Qt.ItemDataRole.UserRole, {"source_id": src.id, "folder_path": str(artist_dir)})
    window._select_folder_item(item)

    cover_helper.wait_for_cover_workers(timeout_ms=2000)
    qapp.processEvents()

    default_pix = cover_helper.get_default_cover_pixmap(136, 10)
    assert window.lbl_folder_selected_cover.pixmap().toImage() != default_pix.toImage()
    window.close()


def test_folders_page_displays_subfolder_cover_when_artist_folder_has_no_image(
    qapp: QApplication, tmp_path: Path
) -> None:
    """Vérifie qu'un dossier artiste sans image propre affiche la première pochette trouvée dans ses sous-dossiers."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QImage
    from PySide6.QtWidgets import QTreeWidgetItem

    from amso.core.database import SourceType
    from amso.ui.views import cover_helper

    artist_dir = tmp_path / "ArtistNoImage"
    album_dir = artist_dir / "Album1"
    album_dir.mkdir(parents=True)

    img = QImage(24, 24, QImage.Format.Format_RGBA8888)
    img.fill(QColor("#8B5CF6"))
    img.save(str(album_dir / "cover.png"))

    db = DatabaseManager(tmp_path / "lib.db")
    src = db.add_source(SourceType.LOCAL, "Music", str(tmp_path))

    cover_helper.invalidate_cover_cache()
    window = MainWindow(db=db)
    window.cb_recursive.setChecked(False)

    item = QTreeWidgetItem(["ArtistNoImage", "0"])
    item.setData(0, Qt.ItemDataRole.UserRole, {"source_id": src.id, "folder_path": str(artist_dir)})
    window._select_folder_item(item)

    cover_helper.wait_for_cover_workers(timeout_ms=2000)
    qapp.processEvents()

    default_pix = cover_helper.get_default_cover_pixmap(136, 10)
    assert window.lbl_folder_selected_cover.pixmap().toImage() != default_pix.toImage()
    window.close()


def test_folders_page_falls_back_to_embedded_track_cover_for_artist_folder(
    qapp: QApplication, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Vérifie le repli sur la pochette intégrée d'un fichier audio si aucun fichier image n'existe dans l'arborescence."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QImage
    from PySide6.QtWidgets import QTreeWidgetItem

    from amso.core.database import SourceType
    from amso.ui.views import cover_helper

    artist_dir = tmp_path / "Novelists"
    album_dir = artist_dir / "2015 - Souvenirs"
    album_dir.mkdir(parents=True)

    song = album_dir / "01.mp3"
    song.write_bytes(b"mp3")

    img = QImage(24, 24, QImage.Format.Format_RGBA8888)
    img.fill(QColor("#EC4899"))
    buf_path = tmp_path / "embedded.png"
    img.save(str(buf_path))
    raw_png = buf_path.read_bytes()

    db = DatabaseManager(tmp_path / "lib.db")
    src = db.add_source(SourceType.LOCAL, "Music", str(tmp_path))
    db.upsert_tracks_batch(
        [
            TrackRecord(
                source_id=src.id,
                source_type=SourceType.LOCAL,
                source_ref=str(song),
                source_path=str(song),
                folder_path=str(album_dir),
                file_name="01.mp3",
                title="Souvenirs",
            )
        ]
    )

    cover_helper.invalidate_cover_cache()
    monkeypatch.setattr(
        cover_helper,
        "extract_cover_art",
        lambda p: raw_png if str(p) == str(song) else None,
    )

    window = MainWindow(db=db)
    window.cb_recursive.setChecked(False)

    item = QTreeWidgetItem(["Novelists", "1"])
    item.setData(0, Qt.ItemDataRole.UserRole, {"source_id": src.id, "folder_path": str(artist_dir)})
    window._select_folder_item(item)

    cover_helper.wait_for_cover_workers(timeout_ms=2000)
    qapp.processEvents()

    default_pix = cover_helper.get_default_cover_pixmap(136, 10)
    assert window.lbl_folder_selected_cover.pixmap().toImage() != default_pix.toImage()
    window.close()


def test_folders_page_displays_cover_for_playlist_only_folder(
    qapp: QApplication, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Vérifie qu'un dossier ne contenant que des playlists (ex. _Playlists) affiche la pochette d'une piste référencée."""
    from types import SimpleNamespace

    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QImage
    from PySide6.QtWidgets import QTreeWidgetItem

    from amso.core.database import SourceType
    from amso.ui.views import cover_helper

    pl_dir = tmp_path / "_Playlists"
    pl_dir.mkdir()
    audio_dir = tmp_path / "Par artiste" / "Air"
    audio_dir.mkdir(parents=True)
    song = audio_dir / "01.mp3"
    song.write_bytes(b"mp3")

    img = QImage(24, 24, QImage.Format.Format_RGBA8888)
    img.fill(QColor("#0EA5E9"))
    buf_path = tmp_path / "air_cover.png"
    img.save(str(buf_path))
    raw_png = buf_path.read_bytes()

    db = DatabaseManager(tmp_path / "lib.db")
    src = db.add_source(SourceType.LOCAL, "_Playlists", str(pl_dir))
    db.upsert_tracks_batch(
        [
            TrackRecord(
                source_id=src.id,
                source_type=SourceType.LOCAL,
                source_ref=str(song),
                source_path=str(song),
                folder_path=str(audio_dir),
                file_name="01.mp3",
                title="Playground Love",
            )
        ]
    )
    pl_file = pl_dir / "Amiga.xspf"
    pl_id = db.upsert_playlist(
        source_id=src.id,
        file_path=str(pl_file),
        file_name="Amiga.xspf",
        folder_path=str(pl_dir),
        format_str="xspf",
        file_mtime=1.0,
        file_size=100,
        entries=[
            SimpleNamespace(
                position=1,
                raw_path=str(song),
                resolved_path=str(song),
                title="Playground Love",
                artist="Air",
                duration_seconds=210.0,
                is_missing=False,
                start_ms=None,
                end_ms=None,
            )
        ],
    )
    db.link_playlist_entries_to_tracks(source_id=src.id)
    assert pl_id > 0

    cover_helper.invalidate_cover_cache()
    monkeypatch.setattr(
        cover_helper,
        "extract_cover_art",
        lambda p: raw_png if str(p) == str(song) else None,
    )

    window = MainWindow(db=db)
    item = QTreeWidgetItem(["_Playlists", ""])
    item.setData(
        0,
        Qt.ItemDataRole.UserRole,
        {"source_id": src.id, "folder_path": str(pl_dir), "is_source_root": True},
    )
    window._select_folder_item(item)

    cover_helper.wait_for_cover_workers(timeout_ms=2000)
    qapp.processEvents()

    default_pix = cover_helper.get_default_cover_pixmap(136, 10)
    assert window.lbl_folder_selected_cover.pixmap().toImage() != default_pix.toImage()
    window.close()


def test_playlist_table_model_exposes_all_unified_columns(qapp: QApplication, db: DatabaseManager) -> None:
    """Vérifie que PlaylistTableModel expose tous les champs de UNIFIED_TRACK_COLUMNS en plus de '#'."""
    from amso.services.player_service import PlayerService
    from amso.ui.models import UNIFIED_TRACK_COLUMNS, PlaylistTableModel

    player = PlayerService()
    tracks, _ = db.get_tracks()
    player.play_tracks(tracks, start_index=0)

    model = PlaylistTableModel(player, db=db)
    expected_fields = {col[1] for col in UNIFIED_TRACK_COLUMNS} | {"playlist_order"}
    actual_fields = {col[1] for col in model.COLUMNS}
    assert actual_fields == expected_fields

    # Colonnes visibles par défaut dans la playlist
    default_visible = {col[1] for col in model.COLUMNS if col[3]}
    assert default_visible == {"is_playing", "playlist_order", "title", "artist", "album", "duration_seconds", "format"}

    # Vérification du formatage d'une colonne étendue (ex: bitrate)
    bitrate_col = next(i for i, col in enumerate(model.COLUMNS) if col[1] == "bitrate")
    val = model.data(model.index(0, bitrate_col), Qt.ItemDataRole.DisplayRole)
    assert isinstance(val, str) and len(val) > 0


def test_playlist_columns_menu_and_independent_persistence_on_close(qapp: QApplication, db: DatabaseManager) -> None:
    """Vérifie le menu colonnes de la playlist et la persistance indépendante à la fermeture."""
    from amso.ui.table_settings import build_columns_menu

    win1 = MainWindow(db=db)
    pl_view = win1.page_playlist

    menu = build_columns_menu(
        pl_view,
        pl_view.table_view,
        pl_view.playlist_model,
        pl_view._TABLE_STORAGE_KEY,
        skip_headers=("", "#"),
    )
    action_texts = [a.text() for a in menu.actions() if a.isCheckable()]
    # Toutes les colonnes nommées de la bibliothèque (29 champs) doivent être présentes
    assert len(action_texts) == 29

    # Modifier des colonnes différentes sur chaque écran
    bitrate_col_pl = next(i for i, c in enumerate(pl_view.playlist_model.COLUMNS) if c[1] == "bitrate")
    genre_col_lib = next(i for i, c in enumerate(win1.table_model.COLUMNS) if c[1] == "genre")
    year_col_fld = next(i for i, c in enumerate(win1.folder_table_model.COLUMNS) if c[1] == "year")

    pl_view._toggle_column(bitrate_col_pl, True)
    win1._toggle_table_column(win1.table_view, genre_col_lib, False, "all_tracks")
    win1._toggle_table_column(win1.folder_table_view, year_col_fld, False, "folders")

    win1.close()

    # Réouverture : chaque écran retrouve ses propres colonnes actives indépendamment
    db2 = DatabaseManager(db_path=db.db_path)
    win2 = MainWindow(db=db2)
    assert not win2.page_playlist.table_view.isColumnHidden(bitrate_col_pl)
    assert win2.table_view.isColumnHidden(genre_col_lib)
    assert not win2.page_playlist.table_view.isColumnHidden(
        next(i for i, c in enumerate(win2.page_playlist.playlist_model.COLUMNS) if c[1] == "title")
    )
    assert win2.folder_table_view.isColumnHidden(year_col_fld)
    # 'bitrate' reste visible par défaut dans la bibliothèque même si modifié dans la playlist
    bitrate_col_lib = next(i for i, c in enumerate(win2.table_model.COLUMNS) if c[1] == "bitrate")
    assert not win2.table_view.isColumnHidden(bitrate_col_lib)
    win2.close()
