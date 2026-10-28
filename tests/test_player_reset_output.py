"""Le moteur `buffer` doit rester utilisable après un changement de mode de transition (reset_playback)."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from amso.core.config import get_config_manager
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
    old_sink = player._engine._sink

    assert player._engine.reset_output() is True

    assert player._engine._sink is not None
    assert player._engine._sink is not old_sink
