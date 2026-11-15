"""Enchaînement des pistes CUE d'un même fichier dans un seul flux décodé (frontières exactes au sample)."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from PySide6.QtWidgets import QApplication

from amso.core.database import TrackRecord
from amso.core.pcm_mixer import ms_to_bytes
from amso.services.audio_decoder import AsyncAudioDecoder
from amso.services.audio_engine import ContinuousAudioEngine
from amso.services.cue_continuation import CueContinuation, continuation_after, continues_stream
from amso.services.player_cue import (
    MAX_DECODE_LEAD_MS,
    RESUME_DECODE_LEAD_MS,
    limit_decode_lead,
    start_track_decode,
    start_track_run,
    stream_key,
)
from amso.services.player_service import PlayerService


def _seg(start: int, end: int | None, path: str = "/m/live.mp3") -> TrackRecord:
    duration = (end - start) / 1000.0 if end is not None else 60.0
    return TrackRecord(source_ref=path, source_path=path, duration_seconds=duration, cue_start_ms=start, cue_end_ms=end)


def _album() -> list[TrackRecord]:
    return [_seg(0, 139_000), _seg(139_000, 335_000), _seg(335_000, 725_000), _seg(725_000, None)]


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        app = QApplication([])
    return app


@pytest.fixture
def engine(qapp: QApplication) -> Iterator[ContinuousAudioEngine]:
    eng = ContinuousAudioEngine()
    yield eng
    eng.shutdown()


class _FakeDecoder:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def start_decode(self, file_path: str, **kwargs: Any) -> None:
        self.calls.append((file_path, kwargs))


# --- Détection des pistes contiguës -------------------------------------------------------------


def test_continues_stream_pistes_contigues_du_meme_fichier_vrai() -> None:
    first, second, *_ = _album()
    assert continues_stream(first, second)


def test_continues_stream_trou_entre_les_pistes_faux() -> None:
    assert not continues_stream(_seg(0, 100_000), _seg(101_000, 200_000))


def test_continues_stream_autre_fichier_faux() -> None:
    assert not continues_stream(_seg(0, 100_000, "/m/a.mp3"), _seg(100_000, 200_000, "/m/b.mp3"))


def test_continues_stream_derniere_piste_sans_fin_faux() -> None:
    assert not continues_stream(_seg(725_000, None), _seg(725_000, None))


def test_continues_stream_piste_non_cue_faux() -> None:
    plain = TrackRecord(source_ref="/m/live.mp3", source_path="/m/live.mp3", duration_seconds=10.0)
    assert not continues_stream(plain, _seg(0, 1000))
    assert not continues_stream(_seg(0, 1000), plain)


def test_continuation_after_suite_complete_jusqua_la_derniere_piste() -> None:
    album = _album()
    assert continuation_after(album, 0) == album[1:]
    assert continuation_after(album, 2) == album[3:]
    assert continuation_after(album, 3) == []


def test_continuation_after_sarrete_au_changement_de_fichier() -> None:
    playlist = [_seg(0, 100_000), _seg(100_000, 200_000), _seg(0, 50_000, "/m/autre.mp3")]
    assert continuation_after(playlist, 0) == [playlist[1]]


# --- Décodage unique pour toute la suite ---------------------------------------------------------


def test_start_track_decode_avec_suite_sarrete_a_la_fin_de_la_derniere_piste() -> None:
    album = _album()
    dec = _FakeDecoder()
    start_track_decode(dec, album[0], 0, album[1:3])  # type: ignore[arg-type]
    assert dec.calls[0][1]["stop_offset_ms"] == 725_000
    assert dec.calls[0][1]["key"] == stream_key(album[0])


def test_start_track_decode_suite_jusquau_bout_du_fichier_sans_arret() -> None:
    album = _album()
    dec = _FakeDecoder()
    start_track_decode(dec, album[2], 0, album[3:])  # type: ignore[arg-type]
    assert dec.calls[0][1]["stop_offset_ms"] == 0


def test_start_track_run_arme_le_moteur_avec_les_durees_des_pistes_suivantes(engine: ContinuousAudioEngine) -> None:
    album = _album()
    dec = _FakeDecoder()
    start_track_run(engine, dec, album, 0)  # type: ignore[arg-type]
    assert engine.cue_continues
    assert dec.calls[0][1]["stop_offset_ms"] == 0  # la dernière piste court jusqu'à la fin du fichier


def test_start_track_run_repetition_dune_piste_nenchaine_rien(engine: ContinuousAudioEngine) -> None:
    dec = _FakeDecoder()
    start_track_run(engine, dec, _album(), 0, chain_next=False)  # type: ignore[arg-type]
    assert not engine.cue_continues
    assert dec.calls[0][1]["stop_offset_ms"] == 139_000


# --- Frontières dans le tampon ----------------------------------------------------------------


def test_crossing_avant_la_frontiere_ne_change_rien() -> None:
    cont = CueContinuation()
    cont.arm([2000])
    assert cont.crossing(ms_to_bytes(1000) - 4, 1000, 0) is None
    assert cont.active


def test_crossing_a_la_frontiere_retourne_les_octets_exacts_et_la_duree_suivante() -> None:
    cont = CueContinuation()
    cont.arm([2000, 3000])
    assert cont.crossing(ms_to_bytes(1000), 1000, 0) == (ms_to_bytes(1000), 2000)
    assert cont.active


def test_crossing_apres_un_seek_la_frontiere_tient_compte_du_decalage_du_tampon() -> None:
    cont = CueContinuation()
    cont.arm([2000])
    assert cont.crossing(ms_to_bytes(500), 1000, 500) == (ms_to_bytes(500), 2000)
    assert not cont.active


def test_crossing_sans_suite_armee_retourne_none() -> None:
    assert CueContinuation().crossing(10**9, 1000, 0) is None


def test_engine_franchit_la_frontiere_sans_perdre_ni_repeter_un_octet(engine: ContinuousAudioEngine) -> None:
    first, second = ms_to_bytes(1000), ms_to_bytes(2000)
    engine._current_pcm = bytearray(b"\x01" * first + b"\x02" * second)
    engine._total_duration_ms = 1000
    engine.arm_cue_continuation([2000])
    engine._play_offset = first + 400  # 100 frames déjà lues au-delà de la frontière

    assert engine._advance_cue_boundaries() == 1

    assert bytes(engine._current_pcm) == b"\x02" * second
    assert engine._play_offset == 400
    assert engine.total_duration_ms == 2000
    assert engine.current_time_ms == int(100 / 44.1)
    assert not engine.cue_continues


def test_engine_poll_progress_emet_les_pistes_franchies_une_seule_fois(engine: ContinuousAudioEngine) -> None:
    engine._current_pcm = bytearray(bytes(ms_to_bytes(3000)))
    engine._total_duration_ms = 1000
    engine.arm_cue_continuation([1000, 1000])
    engine._is_playing = True
    engine._output_started = True
    engine._play_offset = ms_to_bytes(2000) + 8  # deux frontières franchies entre deux ticks
    steps: list[int] = []
    engine.cue_track_advanced.connect(steps.append)

    engine.poll_progress()
    engine.poll_progress()

    assert steps == [2]
    assert not engine.cue_continues


def test_engine_stop_et_seek_hors_tampon_effacent_les_frontieres(engine: ContinuousAudioEngine) -> None:
    engine.arm_cue_continuation([1000])
    engine.reset_buffer_for_seek(5000)
    assert not engine.cue_continues

    engine.arm_cue_continuation([1000])
    engine.stop()
    assert not engine.cue_continues


def test_engine_pause_conserve_les_frontieres(engine: ContinuousAudioEngine) -> None:
    engine.arm_cue_continuation([1000])
    engine._is_playing = True
    engine.pause()
    assert engine.cue_continues


# --- Lecteur --------------------------------------------------------------------------------


def test_player_suit_la_frontiere_cue_sans_relancer_le_decodage(
    qapp: QApplication, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(PlayerService, "is_vlc_available", property(lambda self: True))
    audio = tmp_path / "live.mp3"
    audio.write_text("x")
    album = [_seg(0, 1000, str(audio)), _seg(1000, 3000, str(audio))]
    player = PlayerService()
    player.load_playlist(album)
    player._current_index = 0
    changed: list[TrackRecord] = []
    player.track_changed.connect(changed.append)

    player._on_cue_track_advanced(1)

    assert player._current_index == 1
    assert changed == [album[1]]
    assert player._total_time_ms == 2000


# --- Mémoire bornée : avance du décodage et copie interne du décodeur -----------------------------


class _FakeVlcPlayer:
    def __init__(self) -> None:
        self.pauses: list[int] = []

    def set_pause(self, value: int) -> None:
        self.pauses.append(value)


class _FakeThrottle:
    def __init__(self) -> None:
        self.calls: list[bool] = []

    def set_throttled(self, throttled: bool) -> None:
        self.calls.append(throttled)


def _engine_with_lead(engine: ContinuousAudioEngine, lead_ms: int, chained: bool = True) -> ContinuousAudioEngine:
    engine._current_pcm = bytearray(ms_to_bytes(lead_ms))
    engine._play_offset = 0
    engine.arm_cue_continuation([1000] if chained else [])
    return engine


def test_limit_decode_lead_avance_excessive_suspend_le_decodage(engine: ContinuousAudioEngine) -> None:
    dec = _FakeThrottle()
    limit_decode_lead(_engine_with_lead(engine, MAX_DECODE_LEAD_MS + 1000), dec)  # type: ignore[arg-type]
    assert dec.calls == [True]


def test_limit_decode_lead_zone_dhysteresis_ne_change_rien(engine: ContinuousAudioEngine) -> None:
    dec = _FakeThrottle()
    limit_decode_lead(_engine_with_lead(engine, RESUME_DECODE_LEAD_MS + 1000), dec)  # type: ignore[arg-type]
    assert dec.calls == []


def test_limit_decode_lead_avance_retombee_reprend_le_decodage(engine: ContinuousAudioEngine) -> None:
    dec = _FakeThrottle()
    limit_decode_lead(_engine_with_lead(engine, RESUME_DECODE_LEAD_MS - 1000), dec)  # type: ignore[arg-type]
    assert dec.calls == [False]


def test_limit_decode_lead_sans_suite_cue_ne_suspend_jamais(engine: ContinuousAudioEngine) -> None:
    dec = _FakeThrottle()
    limit_decode_lead(_engine_with_lead(engine, MAX_DECODE_LEAD_MS * 3, chained=False), dec)  # type: ignore[arg-type]
    assert dec.calls == [False]


def test_decoder_set_throttled_met_en_pause_une_seule_fois_et_reste_actif(qapp: QApplication) -> None:
    decoder = AsyncAudioDecoder()
    fake = _FakeVlcPlayer()
    decoder._player = fake

    decoder.set_throttled(True)
    decoder.set_throttled(True)
    assert fake.pauses == [1]
    assert decoder.is_decoding  # sinon le tick du lecteur s'arrête et ne reprend jamais le décodage

    decoder.set_throttled(False)
    assert fake.pauses == [1, 0]


def test_decoder_ne_conserve_pas_le_pcm_deja_livre(qapp: QApplication) -> None:
    decoder = AsyncAudioDecoder()
    decoder._current_path = "/m/a.mp3"
    chunks: list[bytes] = []
    decoder._ready_relay.disconnect()
    decoder._chunk_relay.disconnect()
    decoder._ready_relay.connect(lambda path, pcm, dur, gen: chunks.append(pcm))
    decoder._chunk_relay.connect(lambda path, pcm, gen: chunks.append(pcm))

    block = b"\x01" * decoder._min_initial_bytes
    decoder._handle_pcm_samples(block)
    for _ in range(5):
        decoder._handle_pcm_samples(b"\x02" * 4000)

    assert len(chunks) == 6
    assert len(decoder._accumulated_pcm) == 0
