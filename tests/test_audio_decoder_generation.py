"""Les blocs d'un décodage remplacé ne doivent pas atteindre le lecteur (position et son faussés sinon)."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from amso.services.audio_decoder import AsyncAudioDecoder


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        app = QApplication([])
    return app


def test_deliver_ready_generation_perimee_est_ignoree(qapp: QApplication) -> None:
    decoder = AsyncAudioDecoder()
    received: list[str] = []
    decoder.ready_to_play.connect(lambda path, _pcm, _dur: received.append(path))
    stale_generation = decoder._generation

    decoder.stop()  # un nouveau décodage remplace le précédent
    decoder._deliver_ready("a.flac", b"\0", 1000, stale_generation)
    decoder._deliver_ready("a.flac", b"\0", 1000, decoder._generation)

    assert received == ["a.flac"]


def test_deliver_chunk_generation_perimee_est_ignoree(qapp: QApplication) -> None:
    decoder = AsyncAudioDecoder()
    received: list[bytes] = []
    decoder.chunk_decoded.connect(lambda _path, chunk: received.append(chunk))
    stale_generation = decoder._generation

    decoder.stop()
    decoder._deliver_chunk("a.flac", b"old", stale_generation)
    decoder._deliver_chunk("a.flac", b"new", decoder._generation)

    assert received == [b"new"]
