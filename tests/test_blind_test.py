"""Tests unitaires pour le mode Blind Test d'AMSO."""

import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtGui import QHideEvent, QShowEvent
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
    # Le morceau doit être éteint à 0% sans rebond sonore, et passer au morceau suivant
    player_mock.audio_set_temporary_volume.assert_called_with(0)
    player_mock.next.assert_called_once()


def test_main_window_blind_test_integration(qapp: QApplication, tmp_path: Path):
    """Vérifie l'intégration complète de Blind Test dans MainWindow."""
    db_file = tmp_path / "test.db"
    db = DatabaseManager(db_file)

    window = MainWindow(db=db)

    # 1. Bouton dans le tiroir dédié Jeux
    assert hasattr(window, "btn_blind_test")
    assert hasattr(window, "drawer_games")
    assert window.btn_blind_test in window.drawer_games.findChildren(type(window.btn_blind_test))

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


def test_zoom_fade_label_dynamic_zoom(qapp: QApplication):
    """Vérifie l'animation combinée d'opacité et de zoom dynamique sur ZoomFadeLabel."""
    lbl = ZoomFadeLabel()
    assert hasattr(lbl, "_anim_scale")
    assert hasattr(lbl, "_anim_opacity")
    assert hasattr(lbl, "scale_factor")

    # Déclenchement de l'animation
    lbl.trigger_tick_animation()
    assert lbl._anim_scale.state() == lbl._anim_scale.State.Running
    assert lbl._anim_opacity.state() == lbl._anim_opacity.State.Running

    # Propriété scale_factor
    lbl.scale_factor = 1.25
    assert lbl.scale_factor == 1.25


def test_blind_test_top_bar_volume(qapp: QApplication):
    """Vérifie que la réglette de volume est positionnée dans la barre supérieure."""
    player_mock = MagicMock(spec=PlayerService)
    player_mock.current_track = None
    player_mock.state = "stopped"
    player_mock.is_vlc_available = True
    player_mock.is_playing = False
    player_mock.volume = 65
    player_mock.is_muted = False

    view = BlindTestView(player_mock)
    assert hasattr(view, "slider_volume")
    assert hasattr(view, "btn_mute")
    assert hasattr(view, "lbl_volume")
    assert view.slider_volume.value() == 65
    # Contrôle de volume dans la top_bar et non dans la carte
    assert view.slider_volume.parent() == view.top_bar
    assert view.btn_mute.parent() == view.top_bar


def test_blind_test_no_autoplay_on_entry_and_start_at_zero(qapp: QApplication, sample_track: TrackRecord):
    """Vérifie que la musique ne démarre pas automatiquement lors de l'accès à la page blindtest."""
    player_mock = MagicMock(spec=PlayerService)
    player_mock.current_track = sample_track
    player_mock.current_index = 0
    player_mock.playlist = [sample_track]
    player_mock.current_time_ms = 42000
    player_mock.is_playing = True
    player_mock.state = "playing"
    player_mock.is_vlc_available = True

    view = BlindTestView(player_mock)
    # L'utilisateur arrive sur la page
    view.showEvent(QShowEvent())

    # La lecture en cours a été mise en pause immédiatement
    player_mock.pause.assert_called()
    # Le chrono de manche n'a pas démarré tout seul
    assert not view._game_timer.isActive()
    assert view.btn_play_pause.text() == "▶"
    # La lecture a été calée à 0 seconde
    player_mock.seek_ratio.assert_called_with(0.0)

    # Lorsque l'utilisateur clique sur play : le morceau démarre bien à 0s
    player_mock.is_playing = False
    view._on_play_pause_clicked()
    player_mock.play.assert_called()
    assert view._game_timer.isActive()
    assert view.btn_play_pause.text() == "⏸"


def test_blind_test_previous_button_logic(qapp: QApplication, sample_track: TrackRecord):
    """Vérifie le fonctionnement du bouton Morceau précédent :
    - Si écoulé > 2s ou révélé : remet à zéro la manche courante à 0s.
    - Si écoulé <= 2s : passe réellement au morceau précédent dans la playlist.
    """
    player_mock = MagicMock(spec=PlayerService)
    player_mock.current_track = sample_track
    player_mock.playlist = [sample_track]
    player_mock.is_playing = True
    player_mock.state = "playing"
    player_mock.is_vlc_available = True

    view = BlindTestView(player_mock)
    view._is_active_page = True
    view._on_track_loaded(sample_track)
    assert view.btn_previous is not None
    assert view.btn_prev is not None

    # Cas 1 : La manche a déjà tourné plus de 2s (ex: 6s)
    view._current_round_elapsed = 6
    view._countdown_remain = 14
    view._on_prev_track_clicked()
    # Ne doit pas appeler previous() sur le player, mais réinitialiser la manche à 0
    player_mock.previous.assert_not_called()
    assert view._current_round_elapsed == 0
    assert view._countdown_remain == view._configured_countdown
    assert not view._is_revealed
    player_mock.seek_ratio.assert_called_with(0.0)

    # Cas 2 : La manche a été révélée
    view._trigger_reveal()
    assert view._is_revealed
    view._on_prev_track_clicked()
    player_mock.previous.assert_not_called()
    assert view._current_round_elapsed == 0
    assert not view._is_revealed
    assert view._countdown_remain == view._configured_countdown

    # Cas 3 : La manche est au tout début (<= 2s)
    view._current_round_elapsed = 1
    view._on_prev_track_clicked()
    player_mock.previous.assert_called_once()


def test_blind_test_reveal_guarantees_full_reveal_duration(qapp: QApplication, sample_track: TrackRecord):
    """Vérifie que le clic sur 'Révéler' garantit la durée complète de découverte (10s par défaut)."""
    player_mock = MagicMock(spec=PlayerService)
    player_mock.current_track = sample_track
    player_mock.is_playing = True
    player_mock.state = "playing"
    player_mock.is_vlc_available = True

    view = BlindTestView(player_mock)
    view._is_active_page = True
    view.set_durations(countdown_seconds=20, reveal_seconds=10)
    view._on_track_loaded(sample_track)

    # 7 secondes se sont écoulées
    for _ in range(7):
        view._tick()
    assert view._current_round_elapsed == 7
    assert view._countdown_remain == 13

    # L'utilisateur clique sur Révéler
    view._on_reveal_clicked()
    assert view._is_revealed
    # Le temps restant de découverte doit être exactement de 10 secondes (durée configurée)
    assert view._remaining_seconds == 10
    assert view._reveal_remain == 10
    # Le temps écoulé total est calé sur le seuil de début de découverte
    assert view._current_round_elapsed == 20


def test_blind_test_state_restoration_on_exit(qapp: QApplication, sample_track: TrackRecord):
    """Vérifie que quitter la page blindtest restaure fidèlement la piste et la position initiales du lecteur."""
    track1 = sample_track
    track2 = TrackRecord(
        source_ref="D:/Music/track2.mp3",
        source_path="D:/Music/track2.mp3",
        title="Another One Bites the Dust",
        artist="Queen",
        album="The Game",
        duration_seconds=215.0,
    )

    player_mock = MagicMock(spec=PlayerService)
    player_mock.playlist = [track1, track2]
    player_mock.current_track = track1
    player_mock.current_index = 0
    player_mock.current_time_ms = 73000
    player_mock.is_playing = True
    player_mock.state = "playing"
    player_mock.is_vlc_available = True

    view = BlindTestView(player_mock)

    # 1. Arrivée sur Blind Test
    view.showEvent(QShowEvent())
    assert view._saved_player_index == 0
    assert view._saved_player_position_ms == 73000
    assert view._saved_player_was_playing is True

    # 2. Simulation de passages de titres pendant le Blind Test
    player_mock.current_index = 1
    player_mock.current_track = track2
    player_mock.current_time_ms = 12000

    # 3. Quitter la page Blind Test
    view.hideEvent(QHideEvent())

    # Le player doit être revenu sur la piste 0 et avoir restauré les 73000 ms, et être mis en pause
    player_mock.play_index.assert_called_with(0, resume_pending=True)
    player_mock.pause.assert_called()


def test_blind_test_file_name_display(qapp: QApplication, sample_track: TrackRecord):
    """Vérifie l'affichage du nom de fichier sous l'artiste (masqué puis révélé)."""
    player_mock = MagicMock(spec=PlayerService)
    sample_track.file_name = "Queen_Bohemian_Rhapsody.mp3"
    player_mock.current_track = sample_track
    player_mock.playlist = [sample_track]
    player_mock.current_index = 0
    player_mock.is_playing = False
    player_mock.state = "paused"
    player_mock.is_vlc_available = True

    view = BlindTestView(player_mock)
    view._is_active_page = True
    view._on_track_loaded(sample_track)

    # 1. En phase de recherche (countdown) : doit afficher le texte mystère
    assert "Fichier mystère" in view.lbl_file_name.text() or "Mystery file" in view.lbl_file_name.text()
    assert not view.lbl_file_name.isHidden()

    # 2. En phase de révélation : doit afficher le vrai nom de fichier
    view._trigger_reveal()
    assert view.lbl_file_name.text() == "Queen_Bohemian_Rhapsody.mp3"
    assert not view.lbl_file_name.isHidden()


def test_blind_test_session_progress_label(qapp: QApplication, sample_track: TrackRecord):
    """Vérifie le calcul et l'affichage de 'Extrait x / y — reste z minutes'."""
    player_mock = MagicMock(spec=PlayerService)
    # Playlist de 10 morceaux
    tracks = [sample_track] * 10
    player_mock.playlist = tracks
    player_mock.current_track = sample_track
    player_mock.current_index = 2  # Morceau 3 sur 10
    player_mock.is_playing = True
    player_mock.state = "playing"
    player_mock.is_vlc_available = True

    view = BlindTestView(player_mock)
    view._is_active_page = True
    # 20s + 10s = 30s par manche
    view.set_durations(countdown_seconds=20, reveal_seconds=10, fade_seconds=2)
    view._on_track_loaded(sample_track)

    progress_text = view.lbl_session_progress.text()
    # Morceau courant = index 2 + 1 = 3 sur 10
    assert "3 / 10" in progress_text
    assert "reste" in progress_text or "left" in progress_text
    assert "minutes" in progress_text or "minute" in progress_text


def test_blind_test_fade_in_and_preloading(qapp: QApplication, sample_track: TrackRecord):
    """Vérifie le préchargement anticipé et le fondu d'entrée (Fade-In) de 0% à 100% en 2 secondes."""
    player_mock = MagicMock(spec=PlayerService)
    player_mock.playlist = [sample_track, sample_track]
    player_mock.current_track = sample_track
    player_mock.current_index = 0
    player_mock.get_next_index.return_value = 1
    player_mock.volume = 100
    player_mock.is_playing = True
    player_mock.state = "playing"
    player_mock.is_vlc_available = True

    view = BlindTestView(player_mock)
    view._is_active_page = True

    # Démarre une manche avec auto_play=True
    view._start_round_for_track(sample_track, auto_play=True)

    # 1. Vérifier que la piste suivante a été préchargée en avance
    player_mock.preload_track.assert_called_with(1)

    # 2. Vérifier que le volume a débuté à 0% pour le fondu entrant
    player_mock.audio_set_temporary_volume.assert_called_with(0)
    assert view._is_fading_in is True

    # 3. Simuler le passage du temps (2.0s écoulées)
    view._fade_in_start_time = time.time() - 2.1
    view._on_fade_in_tick()

    # Le fondu entrant est terminé, le volume nominal est restauré
    assert view._is_fading_in is False
    player_mock.restore_volume.assert_called()

