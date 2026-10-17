"""Tests unitaires pour le mode Blind Test d'AMSO."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtGui import QHideEvent
from PySide6.QtWidgets import QApplication

from amso.core.config import ConfigManager
from amso.core.database import DatabaseManager, TrackRecord
from amso.services.player_service import PlayerService
from amso.ui.views.blind_test_view import BlindTestView, ZoomFadeLabel
from amso.ui.views.main_window import MainWindow
from amso.ui.views.player_view import PlayerView


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def sample_track() -> TrackRecord:
    return TrackRecord(
        source_ref="D:/Music/test_track.mp3",
        source_path="D:/Music/test_track.mp3",
        title="Bohemian Rhapsody",
        artist="Queen",
        album="A Night at the Opera",
        duration_seconds=354.0,
        format="mp3",
        bitrate=320,
    )


def test_blind_test_config(tmp_path: Path):
    """Vérifie les réglages de configuration du blind test et leur clamping."""
    cfg_file = tmp_path / "test_config.ini"
    cfg = ConfigManager(config_path=cfg_file)

    # Valeurs par défaut
    assert cfg.get_blind_test_countdown() == 20
    assert cfg.get_blind_test_reveal() == 10
    assert cfg.get_blind_test_fade() == 2

    # Modification avec des valeurs valides
    cfg.set_blind_test_countdown(35)
    cfg.set_blind_test_reveal(15)
    cfg.set_blind_test_fade(4)
    assert cfg.get_blind_test_countdown() == 35
    assert cfg.get_blind_test_reveal() == 15
    assert cfg.get_blind_test_fade() == 4

    # Clamping décompte (5 à 120 secondes)
    cfg.set_blind_test_countdown(2)
    assert cfg.get_blind_test_countdown() == 5
    cfg.set_blind_test_countdown(200)
    assert cfg.get_blind_test_countdown() == 120

    # Clamping découverte (3 à 60 secondes)
    cfg.set_blind_test_reveal(1)
    assert cfg.get_blind_test_reveal() == 3
    cfg.set_blind_test_reveal(90)
    assert cfg.get_blind_test_reveal() == 60

    # Clamping fondu (0 à 10 secondes)
    cfg.set_blind_test_fade(-1)
    assert cfg.get_blind_test_fade() == 0
    cfg.set_blind_test_fade(25)
    assert cfg.get_blind_test_fade() == 10


def test_zoom_fade_label(qapp: QApplication):
    """Vérifie le composant ZoomFadeLabel."""
    lbl = ZoomFadeLabel()
    lbl.show_number(10)
    assert lbl.text() == "10"
    assert lbl._anim_opacity is not None


def test_blind_test_view_init(qapp: QApplication):
    """Vérifie l'instanciation de BlindTestView et la présence de ses widgets clés."""
    player_mock = MagicMock(spec=PlayerService)
    player_mock.current_track = None
    player_mock.state = "stopped"
    player_mock.is_vlc_available = True
    player_mock.is_playing = False

    view = BlindTestView(player_mock)
    assert view.countdown_label is not None
    assert view.btn_reveal is not None
    assert view.btn_play_pause is not None
    assert view.btn_next is not None
    assert view.cover_label is not None
    assert view.lbl_title is not None
    assert view.lbl_artist_album is not None

    # Retraduction UI
    view.retranslate_ui()
    assert "Blind Test" in view.lbl_header_title.text() or "🎭" in view.lbl_header_title.text()


def test_blind_test_countdown_and_tick(qapp: QApplication, sample_track: TrackRecord):
    """Vérifie le déroulement du décompte et le passage au mode révélé."""
    player_mock = MagicMock(spec=PlayerService)
    player_mock.current_track = sample_track
    player_mock.state = "playing"
    player_mock.is_vlc_available = True
    player_mock.is_playing = True

    view = BlindTestView(player_mock)
    view._is_active_page = True
    view.set_durations(countdown_seconds=15, reveal_seconds=8)
    assert view._countdown_duration == 15
    assert view._reveal_duration == 8

    # Démarre la piste
    view._on_track_loaded(sample_track)
    assert not view._is_revealed
    assert view._remaining_seconds == 15
    assert view.cover_opacity_effect.opacity() == 0.0

    # Un tick de seconde
    view._tick()
    assert view._remaining_seconds == 14

    # On force à 1 pour vérifier l'arrivée à 0
    view._remaining_seconds = 1
    view._tick()
    # Arrivée à 0 : doit basculer en mode révélé
    assert view._is_revealed
    assert view._remaining_seconds == 8  # Durée de découverte
    assert view.lbl_title.text() == "Bohemian Rhapsody"
    assert "Queen" in view.lbl_artist_album.text()


def test_blind_test_discovery_tick_to_next(qapp: QApplication, sample_track: TrackRecord):
    """Vérifie qu'à la fin de la durée de découverte, player.next() est invoqué."""
    player_mock = MagicMock(spec=PlayerService)
    player_mock.current_track = sample_track
    player_mock.state = "playing"
    player_mock.is_vlc_available = True
    player_mock.is_playing = True

    view = BlindTestView(player_mock)
    view._is_active_page = True
    view.set_durations(countdown_seconds=10, reveal_seconds=3)
    view._on_track_loaded(sample_track)

    # Déclenche manuellement la révélation
    view._trigger_reveal()
    assert view._is_revealed
    assert view._remaining_seconds == 3

    # Décompte découverte : 3 -> 2 -> 1 -> 0 -> next
    view._tick()
    assert view._remaining_seconds == 2
    view._tick()
    assert view._remaining_seconds == 1
    view._tick()
    # Fin de découverte : appel de next()
    player_mock.next.assert_called_once()


def test_blind_test_manual_reveal(qapp: QApplication, sample_track: TrackRecord):
    """Vérifie que le clic sur 'Révéler' abrège le décompte immédiatement."""
    player_mock = MagicMock(spec=PlayerService)
    player_mock.current_track = sample_track
    player_mock.state = "playing"
    player_mock.is_vlc_available = True
    player_mock.is_playing = True

    view = BlindTestView(player_mock)
    view._is_active_page = True
    view.set_durations(countdown_seconds=20, reveal_seconds=10)
    view._on_track_loaded(sample_track)

    assert not view._is_revealed
    assert view._remaining_seconds == 20

    # Clic sur le bouton Révéler
    view._on_reveal_clicked()
    assert view._is_revealed
    assert view.lbl_title.text() == "Bohemian Rhapsody"
    assert view._remaining_seconds == 10


def test_blind_test_play_pause_and_visibility(qapp: QApplication, sample_track: TrackRecord):
    """Vérifie le bouton play/pause et la mise en pause du timer lors du masquage de la page."""
    player_mock = MagicMock(spec=PlayerService)
    player_mock.current_track = sample_track
    player_mock.state = "playing"
    player_mock.is_vlc_available = True
    player_mock.is_playing = True

    view = BlindTestView(player_mock)
    view._is_active_page = True
    view._on_track_loaded(sample_track)
    assert view._game_timer.isActive()

    # Clic Pause
    view._on_play_pause_clicked()
    player_mock.pause.assert_called_once()

    # État changé vers paused
    view._on_state_changed("paused")
    assert not view._game_timer.isActive()

    # État changé vers playing
    view._on_state_changed("playing")
    assert view._game_timer.isActive()

    # Masquage de la page : le timer doit s'arrêter
    view.hideEvent(QHideEvent())
    assert not view._game_timer.isActive()


def test_player_view_volume_in_top_bar_and_no_blind_test(qapp: QApplication):
    """Vérifie que le volume est dans la barre supérieure de PlayerView et que le bloc blind test a disparu."""
    player_mock = MagicMock(spec=PlayerService)
    player_mock.current_track = None
    player_mock.state = "stopped"
    player_mock.is_vlc_available = True
    player_mock.is_playing = False
    player_mock.volume = 75
    player_mock.is_muted = False

    pview = PlayerView(player_mock)

    # 1. Présence du contrôle de volume dans la barre supérieure
    assert hasattr(pview, "slider_volume")
    assert hasattr(pview, "btn_mute")
    assert hasattr(pview, "lbl_volume")
    assert pview.slider_volume.value() == 75

    # Le volume doit être enfant de top_bar
    assert pview.slider_volume.parent() == pview.top_bar
    assert pview.btn_mute.parent() == pview.top_bar

    # 2. Le bloc paramètres du blind test ne doit plus être présent sur PlayerView
    assert not hasattr(pview, "card_blind_test")
    assert not hasattr(pview, "spin_bt_countdown")
    assert not hasattr(pview, "spin_bt_reveal")


def test_settings_player_blind_test_spinboxes(qapp: QApplication, tmp_path: Path):
    """Vérifie les spinbox de réglage du Blind Test dans Paramètres > Lecteur."""
    from amso.core.config import get_config_manager

    cfg = get_config_manager()
    cfg.set_blind_test_countdown(25)
    cfg.set_blind_test_reveal(12)
    cfg.set_blind_test_fade(3)

    db_file = tmp_path / "test_settings_bt.db"
    db = DatabaseManager(db_file)
    window = MainWindow(db=db)

    # Vérification de la présence des 3 spinboxes sur la page Paramètres > Lecteur
    assert hasattr(window, "spin_bt_countdown")
    assert hasattr(window, "spin_bt_reveal")
    assert hasattr(window, "spin_bt_fade")
    assert window.spin_bt_countdown.value() == 25
    assert window.spin_bt_reveal.value() == 12
    assert window.spin_bt_fade.value() == 3

    # Modification des spinboxes
    window.spin_bt_countdown.setValue(30)
    window.spin_bt_reveal.setValue(15)
    window.spin_bt_fade.setValue(4)

    # Vérification de la persistance en configuration
    assert cfg.get_blind_test_countdown() == 30
    assert cfg.get_blind_test_reveal() == 15
    assert cfg.get_blind_test_fade() == 4

    # Vérification de la synchronisation avec page_blind_test
    assert window.page_blind_test._configured_countdown == 30
    assert window.page_blind_test._configured_reveal == 15
    assert window.page_blind_test._configured_fade == 4


def test_blind_test_audio_fade_logic(qapp: QApplication, sample_track: TrackRecord):
    """Vérifie que la découverte joue à 100% de volume puis effectue un fondu sur la durée configurée."""
    player_mock = MagicMock(spec=PlayerService)
    player_mock.current_track = sample_track
    player_mock.state = "playing"
    player_mock.is_vlc_available = True
    player_mock.is_playing = True
    player_mock.volume = 80
    player_mock.is_muted = False

    view = BlindTestView(player_mock)
    view._is_active_page = True
    # 5s de countdown, 10s de reveal, 2s de fade
    view.set_durations(countdown_seconds=5, reveal_seconds=10, fade_seconds=2)
    view._on_track_loaded(sample_track)

    # Déclenche la révélation (10s de découverte)
    view._trigger_reveal()
    assert view._is_revealed
    assert view._remaining_seconds == 10

    # Les 7 premières secondes (10s -> 3s restantes) : pas de fondu, volume à 100% (80)
    for _ in range(7):
        view._tick()
    assert view._remaining_seconds == 3
    assert not view._is_fading

    # Tick suivant : 2s restantes -> début du fondu sonore
    view._tick()
    assert view._remaining_seconds == 2
    assert view._is_fading
    # Le volume matériel temporaire doit avoir été abaissé
    player_mock.audio_set_temporary_volume.assert_called()

    # Tick suivant : 1s restante -> fondu continue
    view._tick()
    assert view._remaining_seconds == 1

    # Dernier tick : 0s restante -> fin de la découverte
    view._tick()
    # Le volume nominal doit être rétabli avant d'enchaîner sur la piste suivante
    player_mock.restore_volume.assert_called()
    player_mock.next.assert_called_once()


def test_main_window_blind_test_integration(qapp: QApplication, tmp_path: Path):
    """Vérifie l'intégration complète de Blind Test dans MainWindow."""
    db_file = tmp_path / "test.db"
    db = DatabaseManager(db_file)

    window = MainWindow(db=db)

    # 1. Bouton dans le tiroir Lecteur
    assert hasattr(window, "btn_blind_test")
    assert window.btn_blind_test in window.drawer_player.findChildren(type(window.btn_blind_test))

    # 2. Page Blind Test dans le stacked_widget
    assert hasattr(window, "page_blind_test")
    assert window.stacked_widget.indexOf(window.page_blind_test) >= 0

    # 3. Clic sur le bouton de navigation
    window.btn_blind_test.click()
    assert window.stacked_widget.currentWidget() == window.page_blind_test
    assert window._current_active_page == "blind_test"

    # 4. Synchronisation des effets visuels
    window.set_visual_effect("waves")
    assert window.page_blind_test.current_effect == "waves"
    assert window.page_player.current_effect == "waves"

    # 5. Retranscription de langue
    window.retranslate_ui()
    assert window.btn_blind_test.text() != ""
