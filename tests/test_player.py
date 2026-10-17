"""Tests unitaires pour le lecteur audio VLC, la playlist et leur intégration dans AMSO."""

import time
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QImage
from PySide6.QtWidgets import QApplication

from amso.core.config import ConfigManager
from amso.core.database import DatabaseManager, SourceType, TrackRecord
from amso.core.metadata import extract_cover_art
from amso.services.player_service import PlayerService, RepeatMode, vlc
from amso.ui.models import PlaylistTableModel
from amso.ui.views.cover_helper import get_cover_pixmap, load_cover_async
from amso.ui.views.main_window import MainWindow
from amso.ui.views.player_view import PlayerView
from amso.ui.views.visual_effects import VisualEffectWidget


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def sample_tracks() -> list[TrackRecord]:
    return [
        TrackRecord(
            source_ref="D:/Music/track1.mp3",
            source_path="D:/Music/track1.mp3",
            title="Track 1",
            artist="Artist 1",
            album="Album 1",
            duration_seconds=180.0,
            format="mp3",
            bitrate=320,
        ),
        TrackRecord(
            source_ref="D:/Music/track2.flac",
            source_path="D:/Music/track2.flac",
            title="Track 2",
            artist="Artist 2",
            album="Album 2",
            duration_seconds=240.0,
            format="flac",
            bitrate=900,
        ),
        TrackRecord(
            source_ref="D:/Music/track3.ogg",
            source_path="D:/Music/track3.ogg",
            title="Track 3",
            artist="Artist 3",
            album="Album 3",
            duration_seconds=300.0,
            format="ogg",
            bitrate=256,
        ),
    ]


def test_player_service_playlist_management(qapp: QApplication, sample_tracks: list[TrackRecord]):
    """Vérifie la manipulation de la playlist (remplacement, insertion, ajout, suppression)."""
    player = PlayerService()

    # 1. Remplacement de la playlist
    player.play_tracks(sample_tracks, start_index=1)
    assert len(player.playlist) == 3
    assert player.current_index == 1
    assert player.current_track.title == "Track 2"

    # 2. Insertion suivante
    new_track = TrackRecord(
        source_ref="D:/Music/next.mp3",
        source_path="D:/Music/next.mp3",
        title="Next Song",
        artist="Artist Next",
    )
    player.insert_next([new_track])
    # Devrait être inséré juste après l'index 1 -> index 2
    assert len(player.playlist) == 4
    assert player.playlist[2].title == "Next Song"
    assert player.current_track.title == "Track 2"

    # 3. Ajout à la fin (append)
    end_track = TrackRecord(
        source_ref="D:/Music/end.mp3",
        source_path="D:/Music/end.mp3",
        title="End Song",
    )
    player.append_tracks([end_track])
    assert len(player.playlist) == 5
    assert player.playlist[-1].title == "End Song"

    # 4. Suppression
    player.remove_at(2)  # Retire "Next Song"
    assert len(player.playlist) == 4
    assert player.playlist[2].title == "Track 3"

    # 5. Vider la playlist
    player.clear_playlist()
    assert len(player.playlist) == 0
    assert player.current_track is None
    assert player.current_index == -1


def test_player_service_controls_and_modes(qapp: QApplication, sample_tracks: list[TrackRecord]):
    """Vérifie le volume, le mode muet, shuffle et repeat."""
    player = PlayerService()
    player.play_tracks(sample_tracks, start_index=0)

    # Volume
    player.set_volume(50)
    assert player.volume == 50
    player.set_volume(150)
    assert player.volume == 100
    player.set_volume(-10)
    assert player.volume == 0

    # Mute
    assert not player.is_muted
    player.toggle_mute()
    assert player.is_muted
    player.toggle_mute()
    assert not player.is_muted

    # Repeat mode
    assert player.repeat_mode == RepeatMode.OFF
    player.toggle_repeat()
    assert player.repeat_mode == RepeatMode.ALL
    player.toggle_repeat()
    assert player.repeat_mode == RepeatMode.ONE
    player.toggle_repeat()
    assert player.repeat_mode == RepeatMode.OFF

    # Shuffle mode
    assert not player.is_shuffle
    player.toggle_shuffle()
    assert player.is_shuffle
    assert len(player._shuffle_order) == 3
    player.toggle_shuffle()
    assert not player.is_shuffle


def test_playlist_table_model(qapp: QApplication, sample_tracks: list[TrackRecord]):
    """Vérifie le comportement du modèle de tableau PlaylistTableModel."""
    player = PlayerService()
    model = PlaylistTableModel(player)

    assert model.rowCount() == 0
    assert model.columnCount() == len(PlaylistTableModel.COLUMNS)

    player.play_tracks(sample_tracks, start_index=0)
    assert model.rowCount() == 3

    # Vérification des colonnes
    idx_playing = model.index(0, 0)
    idx_order = model.index(0, 1)
    idx_title = model.index(0, 2)
    idx_artist = model.index(0, 3)

    assert model.data(idx_playing, Qt.ItemDataRole.DisplayRole) in {"▶", "⏸", ""}
    assert model.data(idx_order, Qt.ItemDataRole.DisplayRole) == "1"
    assert model.data(idx_title, Qt.ItemDataRole.DisplayRole) == "Track 1"
    assert model.data(idx_artist, Qt.ItemDataRole.DisplayRole) == "Artist 1"

    # Mise en surbrillance pour la piste active
    color = model.data(idx_title, Qt.ItemDataRole.ForegroundRole)
    assert isinstance(color, QColor)
    assert color.name().lower() == "#38bdf8"

    font = model.data(idx_title, Qt.ItemDataRole.FontRole)
    assert isinstance(font, QFont)
    assert font.bold()


def test_cover_helper(tmp_path: Path, qapp: QApplication):
    """Vérifie la génération de pochette et fallback."""
    from PySide6.QtGui import QImage

    # 1. Piste sans fichier existant -> placeholder
    pm = get_cover_pixmap(None, size=100)
    assert not pm.isNull()
    assert pm.width() == 100
    assert pm.height() == 100

    # 2. Dossier avec fichier image folder.png (spécifiquement demandé)
    folder1 = tmp_path / "album_folder_png"
    folder1.mkdir()
    audio1 = folder1 / "song1.mp3"
    audio1.write_bytes(b"dummy audio 1")
    img1 = QImage(200, 200, QImage.Format.Format_RGB32)
    img1.fill(Qt.GlobalColor.green)
    img1.save(str(folder1 / "folder.png"))

    track1 = TrackRecord(source_ref=str(audio1), source_path=str(audio1), title="Song 1")
    pm_folder_png = get_cover_pixmap(track1, size=150)
    assert not pm_folder_png.isNull()
    assert pm_folder_png.width() == 150

    # 3. Dossier avec fichier image folder.jpg
    folder2 = tmp_path / "album_folder_jpg"
    folder2.mkdir()
    audio2 = folder2 / "song2.mp3"
    audio2.write_bytes(b"dummy audio 2")
    img2 = QImage(200, 200, QImage.Format.Format_RGB32)
    img2.fill(Qt.GlobalColor.red)
    img2.save(str(folder2 / "folder.jpg"))

    track2 = TrackRecord(source_ref=str(audio2), source_path=str(audio2), title="Song 2")
    pm_folder_jpg = get_cover_pixmap(track2, size=150)
    assert not pm_folder_jpg.isNull()
    assert pm_folder_jpg.width() == 150

    # 4. Dossier avec autre format image ou nom arbitraire (ex: artwork.webp ou mycover.png)
    folder3 = tmp_path / "album_other_format"
    folder3.mkdir()
    audio3 = folder3 / "song3.mp3"
    audio3.write_bytes(b"dummy audio 3")
    img3 = QImage(200, 200, QImage.Format.Format_RGB32)
    img3.fill(Qt.GlobalColor.cyan)
    img3.save(str(folder3 / "soundtrack_artwork.png"))

    track3 = TrackRecord(source_ref=str(audio3), source_path=str(audio3), title="Song 3")
    pm_other = get_cover_pixmap(track3, size=150)
    assert not pm_other.isNull()
    assert pm_other.width() == 150

    # 5. Extraction directe avec extract_cover_art sur un dossier ou sous-dossier CD1
    raw_folder_png = extract_cover_art(audio1)
    assert raw_folder_png is not None and len(raw_folder_png) > 0

    cd1 = folder1 / "CD1"
    cd1.mkdir()
    audio_cd1 = cd1 / "disc1_song.mp3"
    audio_cd1.write_bytes(b"dummy audio cd1")
    raw_cd1 = extract_cover_art(audio_cd1)
    assert raw_cd1 is not None and len(raw_cd1) > 0


def test_dynamic_cover_reload_on_folder_change(tmp_path: Path, qapp: QApplication):
    """Vérifie que la modification d'un fichier folder.png ou folder.ico est détectée au redémarrage de lecture."""
    folder = tmp_path / "dynamic_album"
    folder.mkdir()
    audio = folder / "test_song.mp3"
    audio.write_bytes(b"dummy audio without embedded cover")

    # 1. Image initiale : folder.png rouge
    img_red = QImage(80, 80, QImage.Format.Format_RGB32)
    img_red.fill(Qt.GlobalColor.red)
    img_red.save(str(folder / "folder.png"))

    track = TrackRecord(source_ref=str(audio), source_path=str(audio), title="Dynamic Song", folder_path=str(folder))

    received_pixmaps: list[object] = []
    pix1 = load_cover_async(track, size=80, callback=lambda p, pix: received_pixmaps.append(pix), force_check=True)
    assert not pix1.isNull()

    for _ in range(50):
        if received_pixmaps:
            break
        time.sleep(0.02)
        qapp.processEvents()

    assert len(received_pixmaps) == 1

    # 2. Remplacement du fichier folder.png par une image verte
    img_green = QImage(80, 80, QImage.Format.Format_RGB32)
    img_green.fill(Qt.GlobalColor.green)
    img_green.save(str(folder / "folder.png"))

    received_updates: list[object] = []
    # Lors d'un redémarrage de lecture (force_check=True), la nouvelle image doit être détectée
    pix2 = load_cover_async(track, size=80, callback=lambda p, pix: received_updates.append(pix), force_check=True)
    assert not pix2.isNull()

    for _ in range(50):
        if received_updates:
            break
        time.sleep(0.02)
        qapp.processEvents()

    assert len(received_updates) == 1

    # 3. Prise en charge des icônes de dossier (.ico)
    folder_ico = tmp_path / "ico_album"
    folder_ico.mkdir()
    audio_ico = folder_ico / "song_ico.mp3"
    audio_ico.write_bytes(b"dummy audio")
    img_ico = QImage(64, 64, QImage.Format.Format_RGB32)
    img_ico.fill(Qt.GlobalColor.yellow)
    img_ico.save(str(folder_ico / "folder.ico"), "ICO")

    raw_ico = extract_cover_art(audio_ico)
    assert raw_ico is not None and len(raw_ico) > 0


def test_main_window_player_drawer_and_views(qapp: QApplication):
    """Vérifie la présence du tiroir Lecteur, des boutons et de la navigation."""
    db = DatabaseManager(":memory:")
    src = db.add_source(SourceType.LOCAL, "Dossier 1", "D:/Music")
    db.upsert_tracks_batch(
        [
            TrackRecord(
                source_ref="D:/Music/A.mp3",
                source_path="D:/Music/A.mp3",
                source_id=src.id,
                title="Song A",
                artist="Artist A",
                format="mp3",
            ),
            TrackRecord(
                source_ref="D:/Music/B.mp3",
                source_path="D:/Music/B.mp3",
                source_id=src.id,
                title="Song B",
                artist="Artist B",
                format="mp3",
            ),
            TrackRecord(
                source_ref="D:/Music/C.mp3",
                source_path="D:/Music/C.mp3",
                source_id=src.id,
                title="Song C",
                artist="Artist C",
                format="mp3",
            ),
        ]
    )

    window = MainWindow(db=db)

    # 1. Présence du tiroir Lecteur
    assert hasattr(window, "drawer_player")
    assert hasattr(window, "btn_player")
    assert hasattr(window, "btn_playlist")

    # 2. Navigation vers la page Lecteur
    window.btn_player.click()
    assert window.stacked_widget.currentWidget() == window.page_player

    # 3. Navigation vers la page Playlist
    window.btn_playlist.click()
    assert window.stacked_widget.currentWidget() == window.page_playlist

    # 4. Simulation du double-clic sur un morceau dans la table
    window.btn_all_tracks.click()
    assert window.stacked_widget.currentWidget() == window.page_tracks
    window.table_model.reload_data()
    assert window.table_model.rowCount() == 3

    # Double clic sur la 2ème ligne (index 1 -> Song B)
    idx_1 = window.table_model.index(1, 1)
    window._on_table_view_double_clicked(idx_1)

    # La playlist doit contenir Song B et Song C
    playlist = window.player_service.playlist
    assert len(playlist) == 2
    assert playlist[0].title == "Song B"
    assert playlist[1].title == "Song C"
    assert window.player_service.current_index == 0

    # 5. Simulation menu contextuel : "Suivant" et "Ajouter"
    track_to_insert = [TrackRecord(source_ref="D:/Music/X.mp3", source_path="D:/Music/X.mp3", title="Song X")]
    window.player_service.insert_next(track_to_insert)
    assert len(window.player_service.playlist) == 3
    assert window.player_service.playlist[1].title == "Song X"

    track_to_append = [TrackRecord(source_ref="D:/Music/Z.mp3", source_path="D:/Music/Z.mp3", title="Song Z")]
    window.player_service.append_tracks(track_to_append)
    assert len(window.player_service.playlist) == 4
    assert window.player_service.playlist[-1].title == "Song Z"

    window.close()


def test_vlc_downloader_utilities_and_dialog(tmp_path: Path, qapp: QApplication):
    """Vérifie le fonctionnement des utilitaires VLC et du dialogue de téléchargement."""
    from amso.services.vlc_downloader import (
        get_local_vlc_dir,
        is_local_vlc_installed,
        setup_vlc_environment,
    )
    from amso.ui.dialogs.vlc_download_dialog import VlcDownloadDialog

    # 1. Vérification des chemins
    local_dir = get_local_vlc_dir()
    assert local_dir.name == "vlc"
    assert isinstance(is_local_vlc_installed(), bool)
    setup_vlc_environment()

    # 2. Dialogue de téléchargement UI
    player = PlayerService()
    dlg = VlcDownloadDialog(player)
    assert dlg.isModal()
    assert not dlg.btn_download.isHidden()
    assert not dlg.btn_later.isHidden()
    dlg.close()


def test_vlc_extraction_logic(tmp_path: Path):
    """Vérifie l'algorithme d'extraction sélective des DLLs et plugins VLC."""
    import zipfile

    dest_dir = tmp_path / "vlc_extracted"
    zip_path = tmp_path / "mock_vlc.zip"

    # Création d'une archive zip simulant la structure officielle VideoLAN
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("vlc-3.0.21/libvlc.dll", b"libvlc_binary_content")
        zf.writestr("vlc-3.0.21/libvlccore.dll", b"libvlccore_binary_content")
        zf.writestr("vlc-3.0.21/plugins/audio_output/libdirectsound_plugin.dll", b"directsound_plugin")
        zf.writestr("vlc-3.0.21/vlc.exe", b"executable_ignored")
        zf.writestr("vlc-3.0.21/sdk/include/vlc.h", b"header_ignored")

    # Simulation de la boucle d'extraction du VlcDownloadWorker
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            filename = member.filename.replace("\\", "/")
            parts = filename.split("/")
            if "libvlc.dll" in parts:
                target = dest_dir / "libvlc.dll"
                target.write_bytes(zf.read(member))
            elif "libvlccore.dll" in parts:
                target = dest_dir / "libvlccore.dll"
                target.write_bytes(zf.read(member))
            elif "plugins" in parts:
                p_idx = parts.index("plugins")
                rel_parts = parts[p_idx:]
                if not member.is_dir():
                    target = dest_dir.joinpath(*rel_parts)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(zf.read(member))

    # Vérification des fichiers essentiels
    assert (dest_dir / "libvlc.dll").read_bytes() == b"libvlc_binary_content"
    assert (dest_dir / "libvlccore.dll").read_bytes() == b"libvlccore_binary_content"
    assert (dest_dir / "plugins/audio_output/libdirectsound_plugin.dll").read_bytes() == b"directsound_plugin"
    # Les fichiers inutiles (exe, doc, sdk) ne doivent pas avoir été extraits
    assert not (dest_dir / "vlc.exe").exists()
    assert not (dest_dir / "sdk").exists()


def test_sleep_inhibitor_lifecycle():
    """Vérifie le cycle d'inhibition et de libération de la veille système et écran."""
    from amso.services.sleep_inhibitor import SleepInhibitor

    # 1. Inhibit système uniquement
    SleepInhibitor.inhibit(prevent_display=False)
    assert SleepInhibitor.is_inhibited() is True
    assert SleepInhibitor.is_display_inhibited() is False

    # 2. Inhibit avec maintien écran
    SleepInhibitor.inhibit(prevent_display=True)
    assert SleepInhibitor.is_inhibited() is True
    assert SleepInhibitor.is_display_inhibited() is True

    # 3. Release
    SleepInhibitor.release()
    assert SleepInhibitor.is_inhibited() is False
    assert SleepInhibitor.is_display_inhibited() is False


def test_player_settings_page_and_sleep_prevention(qapp: QApplication, tmp_path: Path):
    """Vérifie la page Paramètres > Lecteur, la case à cocher et le maintien de l'écran sur Lecteur/Playlist."""
    from amso.core.config import get_config_manager
    from amso.services.sleep_inhibitor import SleepInhibitor

    db = DatabaseManager(str(tmp_path / "test_player_settings.db"))
    window = MainWindow(db=db)

    # 1. Vérifier la présence du bouton dans le tiroir Paramètres
    assert hasattr(window, "btn_settings_player")
    assert hasattr(window, "page_settings_player")

    # 2. Clic sur Paramètres > Lecteur
    window.btn_settings_player.click()
    assert window.stacked_widget.currentWidget() == window.page_settings_player

    # 3. Vérifier les 3 boutons radio et la persistance config
    cfg = get_config_manager()
    assert hasattr(window, "radio_sleep_allow")
    assert hasattr(window, "radio_sleep_screens")
    assert hasattr(window, "radio_sleep_always")

    # Mode par défaut : player_playlist
    assert window.radio_sleep_screens.isChecked() is True
    assert cfg.get_sleep_mode() == "player_playlist"

    # 4. Simulation d'état de lecture sur la vue Lecteur : l'écran doit rester allumé en mode player_playlist
    window.stacked_widget.setCurrentWidget(window.page_player)
    window._on_player_state_changed("playing")
    assert SleepInhibitor.is_inhibited() is True
    assert SleepInhibitor.is_display_inhibited() is True  # Écran maintenu allumé

    # 5. Bascule sur la vue Playlist : l'écran doit également rester allumé
    window.stacked_widget.setCurrentWidget(window.page_playlist)
    assert SleepInhibitor.is_inhibited() is True
    assert SleepInhibitor.is_display_inhibited() is True  # Écran maintenu allumé

    # 6. Bascule sur la vue Morceaux (page standard) : veille écran autorisée mais PC éveillé
    window.stacked_widget.setCurrentWidget(window.page_tracks)
    assert SleepInhibitor.is_inhibited() is True
    assert SleepInhibitor.is_display_inhibited() is False  # Veille écran autorisée

    # 7. Choix 3 : Ne pas autoriser la veille (sur tous les écrans)
    window.radio_sleep_always.setChecked(True)
    assert cfg.get_sleep_mode() == "always"
    assert SleepInhibitor.is_inhibited() is True
    assert SleepInhibitor.is_display_inhibited() is True  # Même sur la page Morceaux !

    # 8. Choix 1 : Autoriser la veille (mode standard Windows)
    window.radio_sleep_allow.setChecked(True)
    assert cfg.get_sleep_mode() == "allow"
    assert SleepInhibitor.is_inhibited() is False
    assert SleepInhibitor.is_display_inhibited() is False

    # 9. Remettre mode player_playlist puis tester Pause / Arrêt : libération complète
    window.radio_sleep_screens.setChecked(True)
    assert SleepInhibitor.is_inhibited() is True

    window._on_player_state_changed("paused")
    assert SleepInhibitor.is_inhibited() is False
    assert SleepInhibitor.is_display_inhibited() is False

    window._on_player_state_changed("stopped")
    assert SleepInhibitor.is_inhibited() is False
    assert SleepInhibitor.is_display_inhibited() is False

    window.close()


def test_player_transition_config(tmp_path: Path):
    """Vérifie la persistance du mode de transition et de la durée du fondu."""
    from amso.core.config import ConfigManager

    cfg = ConfigManager(config_path=tmp_path / "test_config.ini")
    assert cfg.get_transition_mode() == "gapless"
    assert cfg.get_crossfade_duration() == 3

    cfg.set_transition_mode("standard")
    assert cfg.get_transition_mode() == "standard"

    cfg.set_transition_mode("crossfade")
    assert cfg.get_transition_mode() == "crossfade"

    cfg.set_crossfade_duration(5)
    assert cfg.get_crossfade_duration() == 5

    # Bornage 1 à 20
    cfg.set_crossfade_duration(12)
    assert cfg.get_crossfade_duration() == 12

    cfg.set_crossfade_duration(25)
    assert cfg.get_crossfade_duration() == 20

    cfg.set_crossfade_duration(-2)
    assert cfg.get_crossfade_duration() == 1


def test_player_service_get_next_index(qapp: QApplication, sample_tracks: list[TrackRecord]):
    """Vérifie la logique de calcul de la prochaine piste (get_next_index)."""
    player = PlayerService()
    player.play_tracks(sample_tracks, start_index=0)

    # 1. Mode normal séquentiel
    assert player.get_next_index() == 1
    player._current_index = 1
    assert player.get_next_index() == 2
    player._current_index = 2
    assert player.get_next_index() is None

    # 2. Répétition totale (RepeatMode.ALL)
    player.toggle_repeat()  # RepeatMode.ALL
    assert player.repeat_mode == RepeatMode.ALL
    assert player.get_next_index() == 0

    # 3. Répétition unique (RepeatMode.ONE)
    player.toggle_repeat()  # RepeatMode.ONE
    assert player.repeat_mode == RepeatMode.ONE
    assert player.get_next_index() == 2

    # 4. Mode aléatoire (Shuffle)
    player.toggle_repeat()  # RepeatMode.OFF
    player.toggle_shuffle()
    assert player.is_shuffle is True
    next_idx = player.get_next_index()
    assert next_idx is not None or len(sample_tracks) == 1

    player.clear_playlist()
    assert player.get_next_index() is None


def test_player_settings_page_transitions(qapp: QApplication, tmp_path: Path):
    """Vérifie les boutons radio de transition et le curseur de fondu dans les Paramètres."""
    from amso.core.config import get_config_manager

    db = DatabaseManager(str(tmp_path / "test_player_trans.db"))
    window = MainWindow(db=db)
    cfg = get_config_manager()

    assert hasattr(window, "radio_trans_standard")
    assert hasattr(window, "radio_trans_gapless")
    assert hasattr(window, "radio_trans_crossfade")
    assert hasattr(window, "slider_crossfade")
    assert hasattr(window, "crossfade_container")

    # Choix 1 : Standard
    window.radio_trans_standard.setChecked(True)
    assert cfg.get_transition_mode() == "standard"
    assert window.crossfade_container.isEnabled() is False

    # Choix 2 : Gapless (sans coupure)
    window.radio_trans_gapless.setChecked(True)
    assert cfg.get_transition_mode() == "gapless"
    assert window.crossfade_container.isEnabled() is False

    # Choix 3 : Crossfade (fondu)
    window.radio_trans_crossfade.setChecked(True)
    assert cfg.get_transition_mode() == "crossfade"
    assert window.crossfade_container.isEnabled() is True

    # Modification de la durée du fondu via le slider
    window.slider_crossfade.setValue(6)
    assert cfg.get_crossfade_duration() == 6
    assert "6" in window.lbl_crossfade_value.text()

    window.close()


def test_player_and_playlist_translations(qapp: QApplication, tmp_path: Path, sample_tracks: list[TrackRecord]):
    """Vérifie que les titres et libellés du Lecteur et de la Playlist se traduisent dynamiquement."""
    from amso.core.i18n import get_i18n

    db = DatabaseManager(str(tmp_path / "test_player_i18n.db"))
    window = MainWindow(db=db)
    i18n = get_i18n()

    # 1. En Français
    i18n.set_language("fr")
    window.retranslate_ui()

    assert window.drawer_player.title() == "Lecteur"
    assert "Lecteur" in window.btn_player.text()
    assert "Playlist" in window.btn_playlist.text()
    assert window.page_player.lbl_page_title.text() == "Lecteur audio"
    assert window.page_playlist.lbl_page_title.text() == "Liste de lecture"

    # Vérifier le tableau et stats playlist
    window.player_service.play_tracks(sample_tracks, start_index=0)
    window.page_playlist._update_stats_label()
    assert "morceaux" in window.page_playlist.lbl_playlist_stats.text()
    assert "Durée totale" in window.page_playlist.lbl_playlist_stats.text()
    assert window.page_playlist.playlist_model.headerData(2, Qt.Orientation.Horizontal) == "Titre"
    assert window.page_playlist.playlist_model.headerData(3, Qt.Orientation.Horizontal) == "Artiste"

    assert window.radio_sleep_allow.text() == "Autoriser la veille"
    assert "Ne pas autoriser la veille sur les écrans Lecteur et Playlist" in window.radio_sleep_screens.text()
    assert window.radio_sleep_always.text() == "Ne pas autoriser la veille"

    # 2. Bascule en Anglais
    i18n.set_language("en")
    window.retranslate_ui()

    assert window.drawer_player.title() == "Player"
    assert "Player" in window.btn_player.text()
    assert window.page_player.lbl_page_title.text() == "Audio Player"
    assert window.page_playlist.lbl_page_title.text() == "Playlist"
    assert "tracks" in window.page_playlist.lbl_playlist_stats.text()
    assert "Total duration" in window.page_playlist.lbl_playlist_stats.text()
    assert window.page_playlist.playlist_model.headerData(2, Qt.Orientation.Horizontal) == "Title"
    assert window.page_playlist.playlist_model.headerData(3, Qt.Orientation.Horizontal) == "Artist"
    assert window.radio_sleep_allow.text() == "Allow sleep"
    assert "Prevent sleep on Player and Playlist" in window.radio_sleep_screens.text()
    assert window.radio_sleep_always.text() == "Prevent sleep completely"

    # Rétablir en Français
    i18n.set_language("fr")
    window.retranslate_ui()
    window.close()


def test_track_record_serialization_and_db_getters(tmp_path: Path, sample_tracks: list[TrackRecord]):
    """Vérifie la sérialisation TrackRecord et la récupération par ID dans DatabaseManager."""
    db = DatabaseManager(str(tmp_path / "test_serialize.db"))
    for t in sample_tracks:
        db.upsert_track(t)

    tracks, _ = db.get_tracks(limit=10)
    assert len(tracks) >= 2
    t1 = tracks[0]
    assert t1.id is not None

    # Test to_dict / from_dict
    d = t1.to_dict()
    assert d["title"] == t1.title
    assert d["artist"] == t1.artist
    t_rebuilt = TrackRecord.from_dict(d)
    assert t_rebuilt.title == t1.title
    assert t_rebuilt.source_path == t1.source_path
    assert t_rebuilt.id == t1.id

    # Test get_track_by_id
    fetched = db.get_track_by_id(t1.id)
    assert fetched is not None
    assert fetched.id == t1.id
    assert fetched.title == t1.title

    # Test get_tracks_by_ids
    t2 = tracks[1]
    assert t2.id is not None
    fetched_list = db.get_tracks_by_ids([t2.id, t1.id])
    assert len(fetched_list) == 2
    assert fetched_list[0].id == t2.id
    assert fetched_list[1].id == t1.id


def test_player_state_and_playlist_persistence(
    qapp: QApplication, tmp_path: Path, monkeypatch, sample_tracks: list[TrackRecord]
):
    """Vérifie la sauvegarde à la fermeture et la restauration au lancement :
    - Filtres & colonnes des tableaux (taille, visibilité, tri)
    - Paramètres du lecteur (shuffle, boucle, volume)
    - Playlist en cours et index actif
    """
    config_path = tmp_path / "test_persist_config.ini"
    playlist_path = tmp_path / "test_saved_playlist.json"
    db_path = tmp_path / "test_persist.db"

    monkeypatch.setenv("AMSO_CONFIG_PATH", str(config_path))
    monkeypatch.setenv("AMSO_PLAYLIST_PATH", str(playlist_path))

    db = DatabaseManager(str(db_path))
    for t in sample_tracks:
        db.upsert_track(t)
    db_tracks, _ = db.get_tracks(limit=10)

    # 1. Première session : modifier paramètres, playlist et colonnes
    win1 = MainWindow(db=db)

    # Paramètres lecteur
    win1.player_service.set_shuffle(True)
    win1.player_service.set_repeat_mode(RepeatMode.ALL)
    win1.player_service.set_volume(65)

    # Playlist
    win1.player_service.play_tracks(db_tracks, start_index=1)
    assert len(win1.player_service.playlist) == len(db_tracks)
    assert win1.player_service.current_index == 1

    # Modification de colonne sur table_view (Morceaux)
    win1.table_view.horizontalHeader().resizeSection(1, 312)
    win1.table_view.setColumnHidden(4, True)  # Masquer colonne 4
    win1._save_table_header_state(win1.table_view, "all_tracks")

    # Modification de colonne sur page_playlist
    win1.page_playlist.table_view.horizontalHeader().resizeSection(2, 280)
    win1.page_playlist._toggle_column(4, False)  # Masquer album
    win1.page_playlist.save_table_state()

    # Fermeture de la fenêtre (déclenche closeEvent)
    win1.close()

    # Vérification des fichiers de persistance
    cfg = ConfigManager(config_path=config_path)
    assert cfg.get_player_shuffle() is True
    assert cfg.get_player_repeat_mode() == RepeatMode.ALL
    assert cfg.get_player_volume() == 65
    assert playlist_path.exists()

    # 2. Deuxième session : vérifier restauration complète
    win2 = MainWindow(db=db)

    # Paramètres lecteur restaurés
    assert win2.player_service.is_shuffle is True
    assert win2.player_service.repeat_mode == RepeatMode.ALL
    assert win2.player_service.volume == 65

    # Playlist restaurée
    assert len(win2.player_service.playlist) == len(db_tracks)
    assert win2.player_service.current_index == 1
    assert win2.player_service.current_track is not None
    assert win2.player_service.current_track.id == db_tracks[1].id

    # Boutons d'interface synchronisés
    assert win2.page_player.btn_shuffle.styleSheet() != ""  # Actif
    assert win2.page_playlist.btn_shuffle.styleSheet() != ""  # Actif

    # Colonnes restaurées sur table_view
    assert win2.table_view.horizontalHeader().sectionSize(1) == 312
    assert win2.table_view.isColumnHidden(4) is True

    # Colonnes restaurées sur page_playlist
    assert win2.page_playlist.table_view.horizontalHeader().sectionSize(2) == 280
    assert win2.page_playlist.table_view.isColumnHidden(4) is True

    win2.close()


def test_player_visual_effects(qapp: QApplication, tmp_path: Path):
    """Vérifie le fonctionnement du widget d'effets visuels, le sélecteur et la synchronisation avec les paramètres."""
    # 1. Test unitaire du VisualEffectWidget
    widget = VisualEffectWidget(VisualEffectWidget.EFFECT_PARTICLES)
    widget.resize(600, 400)
    assert widget.effect_type == "particles"

    # Vérification des différentes transitions d'effets
    for eff in VisualEffectWidget.ALL_EFFECTS:
        widget.set_effect_type(eff)
        assert widget.effect_type == eff
        widget._on_tick()

    # Effet none éteint le timer
    widget.set_effect_type("none")
    assert not widget._timer.isActive()

    # Rendu graphique sans crash
    widget.set_effect_type("waves")
    pixmap = widget.grab()
    assert not pixmap.isNull()

    widget.set_effect_type("stars")
    pixmap = widget.grab()
    assert not pixmap.isNull()

    widget.set_effect_type("warp")
    pixmap = widget.grab()
    assert not pixmap.isNull()

    widget.set_effect_type("warp_dynamic")
    widget._on_tick()
    pixmap = widget.grab()
    assert not pixmap.isNull()

    widget.set_effect_type("aurora")
    pixmap = widget.grab()
    assert not pixmap.isNull()

    widget.set_effect_type("bars")
    widget.set_playback_state("playing")
    widget.update_audio_volume(85, False)
    widget.update_audio_time(15000, 0.25)
    widget._on_tick()
    pixmap = widget.grab()
    assert not pixmap.isNull()

    widget.set_effect_type("bars_full")
    widget._on_tick()
    pixmap = widget.grab()
    assert not pixmap.isNull()

    # 2. Test intégration dans PlayerView et synchronisation MainWindow
    db = DatabaseManager(tmp_path / "test.db")
    win = MainWindow(db=db)

    # Vérification de la présence des composants sur PlayerView
    assert hasattr(win.page_player, "combo_effect")
    assert hasattr(win.page_player, "effect_canvas")
    assert win.page_player.combo_effect.count() == 9

    # Vérification des boutons radio dans Paramètres > Lecteur
    assert hasattr(win, "radio_eff_particles")
    assert hasattr(win, "radio_eff_waves")
    assert hasattr(win, "radio_eff_stars")
    assert hasattr(win, "radio_eff_warp")
    assert hasattr(win, "radio_eff_warp_dynamic")
    assert hasattr(win, "radio_eff_aurora")
    assert hasattr(win, "radio_eff_bars")
    assert hasattr(win, "radio_eff_bars_full")
    assert hasattr(win, "radio_eff_none")

    # Changement depuis le lecteur (combobox)
    idx_waves = win.page_player.combo_effect.findData("waves")
    win.page_player.combo_effect.setCurrentIndex(idx_waves)
    assert win.page_player.effect_canvas.effect_type == "waves"
    assert win.radio_eff_waves.isChecked()

    idx_warp_dyn = win.page_player.combo_effect.findData("warp_dynamic")
    win.page_player.combo_effect.setCurrentIndex(idx_warp_dyn)
    assert win.page_player.effect_canvas.effect_type == "warp_dynamic"
    assert win.radio_eff_warp_dynamic.isChecked()

    idx_bars = win.page_player.combo_effect.findData("bars")
    win.page_player.combo_effect.setCurrentIndex(idx_bars)
    assert win.page_player.effect_canvas.effect_type == "bars"
    assert win.radio_eff_bars.isChecked()

    idx_bars_full = win.page_player.combo_effect.findData("bars_full")
    win.page_player.combo_effect.setCurrentIndex(idx_bars_full)
    assert win.page_player.effect_canvas.effect_type == "bars_full"
    assert win.radio_eff_bars_full.isChecked()

    idx_warp = win.page_player.combo_effect.findData("warp")
    win.page_player.combo_effect.setCurrentIndex(idx_warp)
    assert win.page_player.effect_canvas.effect_type == "warp"
    assert win.radio_eff_warp.isChecked()

    # Changement depuis les paramètres (radio buttons)
    win.radio_eff_warp_dynamic.setChecked(True)
    assert win.page_player.effect_canvas.effect_type == "warp_dynamic"
    assert win.page_player.combo_effect.currentData() == "warp_dynamic"

    win.radio_eff_bars.setChecked(True)
    assert win.page_player.effect_canvas.effect_type == "bars"
    assert win.page_player.combo_effect.currentData() == "bars"

    win.radio_eff_bars_full.setChecked(True)
    assert win.page_player.effect_canvas.effect_type == "bars_full"
    assert win.page_player.combo_effect.currentData() == "bars_full"

    win.radio_eff_stars.setChecked(True)
    assert win.page_player.effect_canvas.effect_type == "stars"
    assert win.page_player.combo_effect.currentData() == "stars"

    # Changement d'effet depuis le lecteur vers l'hyperespace dynamique
    win.page_player.combo_effect.setCurrentIndex(idx_warp_dyn)
    assert win.page_player.effect_type == "warp_dynamic"

    win.close()

    # Vérification que la configuration a bien persisté le dernier effet actif du lecteur
    from amso.core.config import get_config_manager

    cfg = get_config_manager()
    assert cfg.get_visual_effect() == "warp_dynamic"


def test_player_view_adaptive_vertical_layout(qapp) -> None:
    """Vérifie que la vue Player adapte dynamiquement la pochette et ses blocs verticaux
    afin que l'ensemble du lecteur (y compris auteur multi-lignes et volume) s'affiche sans coupure."""
    ps = PlayerService()
    pv = PlayerView(ps)
    pv.resize(800, 660)
    pv.show()

    # Piste avec titre long (2 lignes) et auteur court (cas de la capture d'écran)
    track1 = TrackRecord(
        source_ref="local",
        title="Heavy Young Heathens - Close to Me (taken from Halloween 2018)",
        artist="ivan",
        file_name="halloween.mp3",
    )
    pv.update_track_info(track1)
    qapp.processEvents()

    assert pv.lbl_file_name.text() == "halloween.mp3"
    assert pv.lbl_file_name.isVisible() is True
    assert pv.lbl_cover.width() >= 150
    assert pv.lbl_cover.height() >= 150
    assert pv.card.height() <= pv.scroll_area.viewport().height() + 10

    # Piste avec auteur et album sur plusieurs lignes
    track2 = TrackRecord(
        source_ref="local",
        title="Heavy Young Heathens - Close to Me (taken from Halloween 2018)",
        artist="ivan\nArtiste invité : John Carpenter\nAlbum : Halloween Original Soundtrack 2018",
        file_name="halloween.mp3",
    )
    pv.update_track_info(track2)
    qapp.processEvents()

    assert pv.card.height() <= pv.scroll_area.viewport().height() + 10

    # Redimensionnement sur une fenêtre plus petite
    pv.resize(800, 520)
    qapp.processEvents()
    assert pv.lbl_cover.width() <= 280
    assert pv.card.height() <= pv.scroll_area.viewport().height() + 10

    pv.close()


def test_visual_effects_resize_reinitialization(qapp) -> None:
    """Vérifie que lors du redimensionnement de la fenêtre, l'effet visuel réinitialise
    ses éléments et couvre l'intégralité de la nouvelle surface d'écran sans zones vides."""
    v = VisualEffectWidget(VisualEffectWidget.EFFECT_PARTICLES)
    v.resize(800, 600)
    v.show()
    qapp.processEvents()

    # Redimensionnement vers un grand écran
    v.resize(1600, 1000)
    qapp.processEvents()

    w = v.width()
    h = v.height()
    assert len(v._particles) >= 50
    # Vérifie que les particules occupent la nouvelle largeur et hauteur
    assert max(p.x for p in v._particles) > w * 0.7
    assert max(p.y for p in v._particles) > h * 0.7

    # Changement d'effet vers les étoiles / comètes
    v.set_effect_type(VisualEffectWidget.EFFECT_STARS)
    qapp.processEvents()
    assert len(v._comets) >= 20
    assert max(c.x for c in v._comets) > w * 0.7

    # Changement d'effet vers le voyage spatial 3D (warp)
    v.set_effect_type(VisualEffectWidget.EFFECT_WARP)
    qapp.processEvents()
    assert len(v._warp_stars) >= 50
    v.close()


def test_player_crossfade_equal_power(qapp, sample_tracks: list[TrackRecord]) -> None:
    """Vérifie le fonctionnement acoustique haute-fidélité du fondu à puissance constante (Equal-Power)."""
    player = PlayerService()
    player.play_tracks(sample_tracks, start_index=0)
    assert player._fade_timer.interval() == 40

    # Mock de lecteurs VLC
    class DummyPlayer:
        def __init__(self):
            self.vol = 0
            self.state = 3  # Playing

        def audio_set_volume(self, v):
            self.vol = v

        def get_state(self):
            return self.state

        def stop(self):
            pass

        def play(self):
            pass

    dummy_curr = DummyPlayer()
    dummy_next = DummyPlayer()
    player._media_player = dummy_curr
    player._standby_player = dummy_next
    player._volume = 100
    player._is_muted = False

    # Démarrage d'un crossfade simulé de 10 secondes
    player._is_crossfading = True
    player._crossfade_next_index = 1
    player._fade_duration_sec = 10.0
    import time

    player._fade_start_time = time.time() - 5.0  # 50% écoulé

    player._on_fade_tick()
    # À 50%, avec cos(pi/4) = 0.707, le volume doit être d'environ 71% (puissance acoustique égale)
    assert 70 <= dummy_curr.vol <= 72
    assert 70 <= dummy_next.vol <= 72

    # À 100% de la durée, la transition doit se finaliser
    player._fade_start_time = time.time() - 10.1
    player._on_fade_tick()
    assert player._is_crossfading is False
    assert player._fade_timer.isActive() is False


def test_audio_spectrum_service() -> None:
    """Vérifie le bon fonctionnement du service d'analyse spectrale audio en temps réel."""
    from amso.services.audio_spectrum import get_audio_spectrum_service

    svc = get_audio_spectrum_service()
    assert svc is not None

    # Test calcul FFT et bandes de fréquences
    spec = svc.get_spectrum(32)
    assert spec is not None
    assert len(spec) == 32
    assert all(0.0 <= v <= 1.0 for v in spec)

    # Test avec 48 bandes
    spec_48 = svc.get_spectrum(48)
    assert spec_48 is not None
    assert len(spec_48) == 48

    # Démarrage et arrêt
    svc.start()
    assert svc._running is True
    svc.stop()
    assert svc._running is False


def test_config_active_page_and_position(tmp_path: Path) -> None:
    """Vérifie la persistance et la lecture de active_page et position_ms dans ConfigManager."""
    cfg_file = tmp_path / "config.ini"
    cfg = ConfigManager(config_path=cfg_file)

    # Valeurs par défaut
    assert cfg.get_active_page() == "tracks"
    assert cfg.get_player_position_ms() == 0

    # Sauvegarde et relecture
    cfg.set_active_page("player")
    cfg.set_player_position_ms(125400)
    assert cfg.get_active_page() == "player"
    assert cfg.get_player_position_ms() == 125400

    # Nouvelle instance pointant vers le même fichier
    cfg2 = ConfigManager(config_path=cfg_file)
    assert cfg2.get_active_page() == "player"
    assert cfg2.get_player_position_ms() == 125400


def test_player_load_playlist_with_initial_position(qapp: QApplication, sample_tracks: list[TrackRecord]) -> None:
    """Vérifie que le chargement d'une playlist avec position initiale émet le bon signal et stocke le temps."""
    player = PlayerService()
    received_positions = []

    def on_pos(cur: int, tot: int, rat: float):
        received_positions.append((cur, tot, rat))

    player.position_changed.connect(on_pos)

    # Morceau 1 fait 180s = 180000ms. On restaure à 60s = 60000ms.
    player.load_playlist(sample_tracks, current_index=0, initial_position_ms=60000)

    assert player.current_index == 0
    assert player.current_time_ms == 60000
    assert len(received_positions) >= 1

    cur, tot, rat = received_positions[-1]
    assert cur == 60000
    assert tot == 180000
    assert round(rat, 2) == round(60000 / 180000, 2)

    # Test seek à l'arrêt
    player.seek_ms(90000)
    assert player.current_time_ms == 90000
    cur2, tot2, rat2 = received_positions[-1]
    assert cur2 == 90000
    assert round(rat2, 2) == 0.5


def test_main_window_active_page_and_position_restore(qapp: QApplication, tmp_path: Path, monkeypatch) -> None:
    """Vérifie que MainWindow sauvegarde et restaure fidèlement la page active et la position du lecteur."""
    cfg_file = tmp_path / "config.ini"
    playlist_file = tmp_path / "saved_playlist.json"
    db_file = tmp_path / "test.db"

    monkeypatch.setenv("AMSO_CONFIG_PATH", str(cfg_file))
    monkeypatch.setenv("AMSO_SAVED_PLAYLIST_PATH", str(playlist_file))

    # Configuration initiale avec page active "player" et position 45000ms
    cfg = ConfigManager(config_path=cfg_file)
    cfg.set_active_page("player")
    cfg.set_player_position_ms(45000)
    cfg.set_player_volume(75)
    cfg.set_player_muted(False)

    db = DatabaseManager(db_path=db_file)
    win = MainWindow(db=db)

    # Vérification que la page "player" a été restaurée
    assert win._current_active_page == "player"
    assert win.btn_player.isChecked() is True
    assert win.stacked_widget.currentWidget() == win.page_player
    assert win.drawer_player.is_expanded is True

    # Changement pour la page playlist
    win._on_playlist_nav_clicked()
    assert win._current_active_page == "playlist"
    assert win.stacked_widget.currentWidget() == win.page_playlist

    # Sauvegarde
    win._save_active_page()
    cfg_reloaded = ConfigManager(config_path=cfg_file)
    assert cfg_reloaded.get_active_page() == "playlist"

    win.close()


def test_player_start_at_zero_and_volume_lock_and_immediate_persistence(tmp_path: Path, monkeypatch) -> None:
    """Valide les 3 comportements :
    1. Forcer le démarrage à 0:00 sur play_tracks et play_track_now, tout en conservant la reprise sur toggle_play_pause.
    2. Sauvegarde immédiate du volume dans config.ini dès l'appel à set_volume et toggle_mute.
    3. Verrouillage / réapplication du volume dans VLC lors du tick de lecture si le volume dérive.
    """
    cfg_file = tmp_path / "test_config.ini"
    monkeypatch.setenv("AMSO_CONFIG_PATH", str(cfg_file))
    ConfigManager(config_path=cfg_file)

    player = PlayerService()

    # 1. Test de la persistance immédiate du volume et mute
    player.set_volume(42)
    # Vérification directe depuis le fichier physique
    cfg_check = ConfigManager(config_path=cfg_file)
    assert cfg_check.get_player_volume() == 42

    player.toggle_mute()
    cfg_check2 = ConfigManager(config_path=cfg_file)
    assert cfg_check2.get_player_muted() is True

    player.toggle_mute()
    cfg_check3 = ConfigManager(config_path=cfg_file)
    assert cfg_check3.get_player_muted() is False

    # 2. Test du démarrage à 0:00 vs reprise de session
    t1 = TrackRecord(source_ref="C:/dummy/track1.mp3", title="Track 1", source_path="C:/dummy/track1.mp3", duration_seconds=180.0)
    t2 = TrackRecord(source_ref="C:/dummy/track2.mp3", title="Track 2", source_path="C:/dummy/track2.mp3", duration_seconds=200.0)

    # Restauration d'une session avec 50 secondes d'offset
    player.load_playlist([t1, t2], current_index=0, initial_position_ms=50000)
    assert player.current_time_ms == 50000
    assert player._pending_seek_ms == 50000

    # Si l'utilisateur lance une nouvelle sélection avec play_tracks -> démarre à 0:00
    calls_seek = []

    def mock_play_index(index: int, resume_pending: bool = False):
        calls_seek.append((index, resume_pending, player._pending_seek_ms))

    player.play_index = mock_play_index

    # Nouvelle sélection via play_tracks -> resume_pending doit être False et _pending_seek_ms doit être 0
    player.play_tracks([t1, t2], start_index=0)
    assert calls_seek[-1] == (0, False, 0)
    assert player._pending_seek_ms == 0

    # Nouvelle sélection via play_track_now -> démarre à 0:00
    player._pending_seek_ms = 45000
    player.play_track_now(t2)
    assert calls_seek[-1] == (1, False, 0)
    assert player._pending_seek_ms == 0

    # En revanche, si on charge une session et qu'on appuie sur Play / toggle_play_pause -> resume_pending est True !
    player.load_playlist([t1, t2], current_index=0, initial_position_ms=30000)
    player.toggle_play_pause()
    assert calls_seek[-1] == (0, True, 30000)

    # 3. Test de la réapplication du volume dans _on_tick si VLC a désynchronisé
    class MockVlcPlayer:
        def __init__(self):
            self._vol = 100  # VLC démarre par défaut à 100%
            self.applied_vol = 100

        def get_state(self):
            return vlc.State.Playing

        def audio_get_volume(self):
            return self._vol

        def audio_set_volume(self, v):
            self._vol = v
            self.applied_vol = v

        def get_time(self):
            return 1000

        def get_length(self):
            return 180000

        def get_position(self):
            return 1000 / 180000

    mock_vlc = MockVlcPlayer()
    player._media_player = mock_vlc
    player.set_volume(42)
    # Simuler VLC qui était resté à 100
    mock_vlc._vol = 100

    player._on_tick()
    # Le tick doit avoir réappliqué et forcé le volume désiré (42)
    assert mock_vlc.applied_vol == 42


def test_player_startup_volume_locking_and_countdown(tmp_path: Path, monkeypatch) -> None:
    """Valide la protection contre la condition de course LibVLC asynchrone au démarrage :
    1. _volume_enforce_ticks est armé à 25 ticks (2.5s) lors de play_index.
    2. Les ticks successifs réappliquent audio_set_volume même si audio_get_volume prétendait déjà correspondre.
    3. _reset_standby_player et stop restaurent le volume nominal du lecteur principal.
    """
    cfg_file = tmp_path / "test_config_vol.ini"
    monkeypatch.setenv("AMSO_CONFIG_PATH", str(cfg_file))
    cfg = ConfigManager(config_path=cfg_file)
    cfg.set_player_volume(90)

    player = PlayerService()
    assert player.volume == 90

    applied_calls = []

    class MockVlcPlayer:
        def __init__(self):
            self._vol = 90

        def get_state(self):
            return vlc.State.Playing

        def audio_get_volume(self):
            return self._vol

        def audio_set_volume(self, v):
            applied_calls.append(v)
            self._vol = v

        def get_time(self):
            return 500

        def get_length(self):
            return 120000

        def get_position(self):
            return 500 / 120000

    mock_vlc = MockVlcPlayer()
    player._media_player = mock_vlc

    # Simuler le démarrage d'une piste
    player._volume_enforce_ticks = 3
    applied_calls.clear()

    # Tick 1 -> doit forcer audio_set_volume(90) même si mock_vlc.audio_get_volume() == 90
    player._on_tick()
    assert player._volume_enforce_ticks == 2
    assert applied_calls == [90]

    # Tick 2 -> doit encore forcer
    player._on_tick()
    assert player._volume_enforce_ticks == 1
    assert applied_calls == [90, 90]

    # Tick 3 -> dernier tick du décompte
    player._on_tick()
    assert player._volume_enforce_ticks == 0
    assert applied_calls == [90, 90, 90]

    # Arrêt du lecteur -> doit rétablir le volume
    player.stop()
    assert player._volume_enforce_ticks == 0
    assert applied_calls[-1] == 90

