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
    old_sink = player._engine._sink

    assert player._engine.reset_output() is True

    assert player._engine._sink is not None
    assert player._engine._sink is not old_sink


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


@pytest.mark.parametrize("old_engine", ["buffer", "vlc_direct"])
@pytest.mark.parametrize("new_engine", ["buffer", "vlc_direct"])
def test_changement_de_moteur_conserve_la_position(qapp: QApplication, old_engine: str, new_engine: str) -> None:
    cfg = get_config_manager()
    cfg.set_audio_engine(old_engine)
    player = PlayerService()
    if not player._engine.is_available:
        pytest.skip("aucune sortie audio disponible")
    player.load_playlist([_track()], 0)
    if old_engine == "buffer":
        # Lecture en cours : seule la position du moteur à tampon la connaît (rien dans _pending_seek_ms).
        player._engine._is_playing = True
        player._engine._base_offset_ms = 90_000
    else:
        player._current_time_ms = 90_000
    states: list[str] = []
    player.state_changed.connect(states.append)

    resume_ms = player.capture_position_ms()
    cfg.set_audio_engine(new_engine)
    player.reset_playback(resume_ms)

    assert resume_ms == 90_000
    assert player._pending_seek_ms == 90_000
    assert player._current_time_ms == 90_000
    assert states[-1] == "paused"


def test_capture_position_hors_duree_revient_a_zero(qapp: QApplication) -> None:
    player = PlayerService()
    player.load_playlist([_track()], 0)
    player._current_time_ms = 240_000

    assert player.capture_position_ms() == 0


def test_reset_playback_par_defaut_revient_a_zero(qapp: QApplication) -> None:
    player = PlayerService()
    player.load_playlist([_track()], 0, initial_position_ms=60_000)

    player.reset_playback()

    assert player._pending_seek_ms == 0
    assert player._current_time_ms == 0
