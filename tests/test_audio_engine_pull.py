"""Le thread audio tire le PCM via `read_pcm` : silence sans avancer la position, thread arrêtable."""

from __future__ import annotations

from collections.abc import Iterator

import numpy as np
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


class _CountingOutput:
    available = True

    def __init__(self) -> None:
        self.starts = 0

    def start(self, paused: bool = False) -> None:
        self.starts += 1

    def suspend(self) -> None:
        return None

    def resume(self) -> None:
        return None

    def stop(self) -> None:
        return None

    def shutdown(self) -> None:
        return None


def test_prepare_output_avant_play_track_ouvre_la_sortie_une_seule_fois(engine: ContinuousAudioEngine) -> None:
    engine._output.shutdown()
    output = _CountingOutput()
    engine._output = output  # type: ignore[assignment]  # double de test de SinkOutput
    engine._output_started = False

    engine.prepare_output()
    engine.prepare_output()
    engine.play_track("a.flac", b"\x01" * 400, 1000)

    assert output.starts == 1


def _cut_engine(engine: ContinuousAudioEngine) -> None:
    engine._output.shutdown()
    engine._output = _CountingOutput()  # type: ignore[assignment]  # double de test de SinkOutput
    engine._output_started = True


def _constant_pcm(frames: int, value: int) -> bytes:
    return int(value).to_bytes(2, "little", signed=True) * 2 * frames


def test_stop_fade_out_fin_fondue_vers_zero_puis_silence_sans_fermer_la_sortie(engine: ContinuousAudioEngine) -> None:
    _cut_engine(engine)
    engine._current_pcm = bytearray(_constant_pcm(4410, 10000))
    engine._play_offset = 400 * BYTES_PER_FRAME

    engine.stop(keep_output=True, fade_out=True)
    data, padded = engine.read_pcm(600 * BYTES_PER_FRAME)

    samples = np.frombuffer(data, dtype="<i2").reshape(-1, 2)[:, 0]
    fade_frames = 441
    assert samples[0] > 9900
    assert abs(int(samples[fade_frames - 1])) < 50
    assert np.all(np.diff(samples[:fade_frames].astype(np.int32)) <= 0)
    assert not samples[fade_frames:].any()
    assert padded == (600 - fade_frames) * BYTES_PER_FRAME
    assert engine._output_started is True


def test_play_track_apres_stop_fade_out_demarre_par_un_fondu_entrant_puis_plein_niveau(
    engine: ContinuousAudioEngine,
) -> None:
    _cut_engine(engine)
    engine._current_pcm = bytearray(_constant_pcm(2000, 10000))
    engine.stop(keep_output=True, fade_out=True)

    engine.play_track("b.flac", _constant_pcm(2000, 8000), 1000)
    engine.read_pcm(441 * BYTES_PER_FRAME)  # purge de la fin fondue de l'ancien titre
    data, _ = engine.read_pcm(1000 * BYTES_PER_FRAME)

    samples = np.frombuffer(data, dtype="<i2").reshape(-1, 2)[:, 0]
    assert abs(int(samples[0])) < 50
    assert np.all(np.diff(samples[:441].astype(np.int32)) >= 0)
    assert samples[600] == 8000


def test_stop_sans_fondu_ne_fond_pas_le_titre_suivant(engine: ContinuousAudioEngine) -> None:
    _cut_engine(engine)
    engine.stop(keep_output=True)

    engine.play_track("b.flac", _constant_pcm(2000, 8000), 1000)
    data, _ = engine.read_pcm(10 * BYTES_PER_FRAME)

    assert np.all(np.frombuffer(data, dtype="<i2") == 8000)
