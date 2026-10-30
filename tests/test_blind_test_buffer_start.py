"""Blind Test en moteur `buffer` : le bouton Lecture doit réellement démarrer le moteur (et non le laisser en pause)."""

from __future__ import annotations

import time
from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from amso.core.config import get_config_manager
from amso.services.player_service import PlayerService
from amso.ui.views.blind_test_view import BlindTestView
from tests.tnr.scenario import make_track

TRACKS = [Path("_work/tnr/01 - Sirius.flac"), Path("_work/tnr/02 - Eye In The Sky.flac")]


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        app = QApplication([])
    return app


def _pump_until(predicate: object, timeout_s: float = 6.0) -> bool:
    end = time.monotonic() + timeout_s
    while time.monotonic() < end:
        QCoreApplication.processEvents()
        if callable(predicate) and predicate():
            return True
        time.sleep(0.01)
    return False


@pytest.mark.parametrize("mode", ["gapless", "standard", "crossfade"])
def test_clic_lecture_moteur_buffer_demarre_le_moteur(qapp: QApplication, mode: str) -> None:
    if not all(p.exists() for p in TRACKS):
        pytest.skip("pistes de référence absentes (_work/tnr)")
    cfg = get_config_manager()
    cfg.set_audio_engine("buffer")
    cfg.set_transition_mode(mode)
    player = PlayerService()
    if not player._engine.is_available or not player.is_vlc_available:
        pytest.skip("sortie audio ou VLC indisponible")
    player.load_playlist([make_track(p) for p in TRACKS], 0)
    view = BlindTestView(player)
    view.show()
    _pump_until(lambda: False, 0.8)  # laisse le décodeur livrer la piste chargée en pause

    view._on_play_pause_clicked()

    assert _pump_until(lambda: player._engine.is_playing)
    assert not player._is_paused_requested
    view.hide()


def _blind_test_playing(mode: str) -> tuple[PlayerService, BlindTestView]:
    cfg = get_config_manager()
    cfg.set_audio_engine("buffer")
    cfg.set_transition_mode(mode)
    player = PlayerService()
    if not player._engine.is_available or not player.is_vlc_available:
        pytest.skip("sortie audio ou VLC indisponible")
    player.load_playlist([make_track(p) for p in TRACKS], 0)
    view = BlindTestView(player)
    view.show()
    _pump_until(lambda: False, 0.8)
    view._on_play_pause_clicked()
    assert _pump_until(lambda: player._engine.is_playing)
    return player, view


@pytest.mark.parametrize("mode", ["gapless", "crossfade"])
def test_suivant_puis_precedent_moteur_buffer_enchainent_sans_appuyer_sur_lecture(
    qapp: QApplication, mode: str
) -> None:
    if not all(p.exists() for p in TRACKS):
        pytest.skip("pistes de référence absentes (_work/tnr)")
    player, view = _blind_test_playing(mode)

    view._on_next_track_clicked()
    assert _pump_until(lambda: player.current_index == 1 and player._engine.is_playing)
    assert not player._is_paused_requested

    view._on_prev_track_clicked()
    assert _pump_until(lambda: player.current_index == 0 and player._engine.is_playing)
    assert not player._is_paused_requested
    view.hide()
