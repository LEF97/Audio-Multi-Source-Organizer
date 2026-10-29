"""Le moteur `buffer` doit rester utilisable après un changement de mode de transition (reset_playback)."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from amso.core.config import get_config_manager
from amso.core.database import SourceType, TrackRecord
from amso.services.player_service import PlayerService


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        app = QApplication([])
    return app


def test_reset_playback_moteur_buffer_garde_la_sortie_disponible(qapp: QApplication) -> None:
    get_config_manager().set_audio_engine("buffer")
    player = PlayerService()
    if not player._engine.is_available:
        pytest.skip("aucune sortie audio disponible")

    player.reset_playback()

    # Sans sortie, le lecteur bascule sur le chemin VLC : seek puis play ne lisent plus rien en mode buffer.
    assert player._engine.is_available
    assert player._engine.is_playing is False


def test_reset_output_recree_une_session_neuve(qapp: QApplication) -> None:
    player = PlayerService()
    if not player._engine.is_available:
        pytest.skip("aucune sortie audio disponible")
    old_output = player._engine._output

    assert player._engine.reset_output() is True

    assert player._engine._output is not None
    assert player._engine._output is not old_output


def _track() -> TrackRecord:
    return TrackRecord(
        source_type=SourceType.LOCAL,
        source_ref="C:/absent/a.flac",
        source_path="C:/absent/a.flac",
        file_name="a.flac",
        title="A",
        artist="B",
        duration_seconds=240.0,
    )


@pytest.mark.parametrize("via_toggle", [True, False])
def test_reprise_apres_reset_relance_le_timer_de_transfert(qapp: QApplication, via_toggle: bool) -> None:
    cfg = get_config_manager()
    cfg.set_audio_engine("buffer")
    player = PlayerService()
    if not player._engine.is_available or not player.is_vlc_available:
        pytest.skip("sortie audio ou VLC indisponible")
    player.load_playlist([_track()], 0)
    player.reset_playback()
    # Le décodeur signale « prêt » : le moteur est chargé en pause, timer arrêté par stop().
    player._engine.play_track("C:/absent/a.flac", b"\0" * 4096, 240_000, start_offset_ms=90_000, start_paused=True)
    assert not player._timer.isActive()

    if via_toggle:
        player.toggle_play_pause()
    else:
        player._resume_from_paused()

    # Sans tick, poll_progress n'est plus appelé : la lecture reprend muette.
    assert player._timer.isActive()
    assert player._engine.is_playing


def test_reset_playback_par_defaut_revient_a_zero(qapp: QApplication) -> None:
    player = PlayerService()
    player.load_playlist([_track()], 0, initial_position_ms=60_000)

    player.reset_playback()

    assert player._pending_seek_ms == 0
    assert player._current_time_ms == 0


@pytest.mark.parametrize(("natural_end", "expected_gapless"), [(False, False), (True, True)])
def test_next_buffer_raccord_gapless_seulement_en_fin_naturelle(
    qapp: QApplication, monkeypatch: pytest.MonkeyPatch, natural_end: bool, expected_gapless: bool
) -> None:
    cfg = get_config_manager()
    cfg.set_audio_engine("buffer")
    cfg.set_transition_mode("gapless")
    player = PlayerService()
    if not player._engine.is_available:
        pytest.skip("aucune sortie audio disponible")
    player.load_playlist([_track(), _track()], 0)
    monkeypatch.setattr(player, "_standby_decoder", object())
    player._standby_player = None  # sans lecteur VLC de secours, seul le chemin du tampon est en jeu
    player._preloaded_index = 1
    player._advancing_after_track_end = natural_end
    transitions: list[int] = []
    played: list[int] = []
    monkeypatch.setattr(player, "_complete_buffer_transition", transitions.append)
    monkeypatch.setattr(player, "play_index", played.append)

    player.next()

    # Un « Suivant » manuel garde sinon la position de la piste précédente (suivante accolée dans le tampon).
    assert bool(transitions) is expected_gapless
    assert bool(played) is not expected_gapless
