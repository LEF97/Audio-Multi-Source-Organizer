"""Le thread audio tire le PCM via `read_pcm` : silence sans avancer la position, thread arrêtable."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication

from amso.services.audio_engine import BYTES_PER_FRAME, ContinuousAudioEngine


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        app = QApplication([])
    return app


@pytest.fixture
def engine(qapp: QApplication) -> Iterator[ContinuousAudioEngine]:
    eng = ContinuousAudioEngine()
    if not eng.is_available:
        pytest.skip("aucune sortie audio disponible")
    yield eng
    eng.shutdown()


def _load(engine: ContinuousAudioEngine, frames: int) -> None:
    engine._current_pcm = bytearray(b"\x01" * frames * BYTES_PER_FRAME)
    engine._play_offset = 0


def test_read_pcm_donnees_suffisantes_avance_la_position_sans_silence(engine: ContinuousAudioEngine) -> None:
    _load(engine, 100)

    data, padded = engine.read_pcm(40 * BYTES_PER_FRAME)

    assert len(data) == 40 * BYTES_PER_FRAME
    assert padded == 0
    assert engine._play_offset == 40 * BYTES_PER_FRAME


def test_read_pcm_tampon_insuffisant_complete_par_du_silence_sans_avancer_au_dela(
    engine: ContinuousAudioEngine,
) -> None:
    _load(engine, 10)

    data, padded = engine.read_pcm(30 * BYTES_PER_FRAME)

    assert len(data) == 30 * BYTES_PER_FRAME
    assert padded == 20 * BYTES_PER_FRAME
    assert data[10 * BYTES_PER_FRAME :] == bytes(20 * BYTES_PER_FRAME)
    assert engine._play_offset == 10 * BYTES_PER_FRAME


def test_read_pcm_silence_avant_toute_donnee_nest_pas_compte_comme_manque(engine: ContinuousAudioEngine) -> None:
    engine.read_pcm(1000)

    assert engine.starved_ms == 0


def test_read_pcm_silence_apres_des_donnees_est_compte_comme_manque(engine: ContinuousAudioEngine) -> None:
    _load(engine, 10)
    engine.read_pcm(10 * BYTES_PER_FRAME)

    engine.read_pcm(441 * BYTES_PER_FRAME)

    assert engine.starved_ms == pytest.approx(10.0, abs=0.1)


def test_read_pcm_taille_non_alignee_reste_alignee_sur_la_trame(engine: ContinuousAudioEngine) -> None:
    _load(engine, 10)

    data, _padded = engine.read_pcm(3 * BYTES_PER_FRAME + 1)

    assert len(data) == 3 * BYTES_PER_FRAME


def test_shutdown_arrete_le_thread_audio_et_est_idempotent(qapp: QApplication) -> None:
    eng = ContinuousAudioEngine()
    if not eng.is_available:
        pytest.skip("aucune sortie audio disponible")

    eng.shutdown()
    eng.shutdown()

    assert eng._output is not None
    assert not eng._output._thread.isRunning()
