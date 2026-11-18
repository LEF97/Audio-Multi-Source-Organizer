"""Tests pour la sélection et la bascule automatique de sortie audio (moteur buffer)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from PySide6.QtMultimedia import QAudioFormat

from amso.core.config import ConfigManager
from amso.services import audio_output
from amso.services.audio_output import AUTO_DEVICE_ID, _SinkWorker


def _make_format() -> QAudioFormat:
    fmt = QAudioFormat()
    fmt.setSampleRate(44100)
    fmt.setChannelCount(2)
    fmt.setSampleFormat(QAudioFormat.SampleFormat.Int16)
    return fmt


def _fake_device(raw_id: bytes, description: str, is_null: bool = False) -> MagicMock:
    dev = MagicMock()
    dev.isNull.return_value = is_null
    qba = MagicMock()
    qba.data.return_value = raw_id
    dev.id.return_value = qba
    dev.description.return_value = description
    return dev


def test_config_audio_output_device_default_and_persistence(tmp_path: Path) -> None:
    cfg = ConfigManager(config_path=tmp_path / "config.ini")
    assert cfg.get_audio_output_device() == AUTO_DEVICE_ID

    cfg.set_audio_output_device("64657631")
    reloaded = ConfigManager(config_path=tmp_path / "config.ini")
    assert reloaded.get_audio_output_device() == "64657631"

    cfg.set_audio_output_device("   ")
    assert cfg.get_audio_output_device() == AUTO_DEVICE_ID


def test_resolve_audio_output_device_selects_matching_or_falls_back_to_default() -> None:
    dev1 = _fake_device(b"dev1", "Casque")
    dev2 = _fake_device(b"dev2", "HDMI")
    default_dev = dev1

    with (
        patch.object(audio_output.QMediaDevices, "audioOutputs", return_value=[dev1, dev2]),
        patch.object(audio_output.QMediaDevices, "defaultAudioOutput", return_value=default_dev),
    ):
        assert audio_output.resolve_audio_output_device("auto") is default_dev
        assert audio_output.resolve_audio_output_device(b"dev2".hex()) is dev2
        assert audio_output.resolve_audio_output_device("deadbeef") is default_dev


def test_sink_worker_switch_device_preserves_playing_state_and_skips_same_device() -> None:
    dev1 = _fake_device(b"dev1", "Haut-parleurs")
    dev2 = _fake_device(b"dev2", "Casque USB")
    sinks_created: list[MagicMock] = []

    def _make_sink(target: MagicMock, fmt: QAudioFormat) -> MagicMock:
        sink = MagicMock()
        sink._target = target
        sinks_created.append(sink)
        return sink

    worker = _SinkWorker(_make_format(), 32768, 0.75, lambda n: (b"\x00" * n, 0), device_id=AUTO_DEVICE_ID)
    with (
        patch.object(audio_output.QMediaDevices, "audioOutputs", return_value=[dev1, dev2]),
        patch.object(audio_output.QMediaDevices, "defaultAudioOutput", return_value=dev1),
        patch.object(audio_output, "QAudioSink", side_effect=_make_sink),
    ):
        worker.create()
        assert worker.created
        assert len(sinks_created) == 1

        worker.start(paused=False, drain_ms=0)
        # Bascule vers le même périphérique : aucune recréation
        worker.switch_device(b"dev1".hex())
        assert len(sinks_created) == 1

        # Bascule vers dev2 pendant la lecture : ancien sink arrêté, nouveau démarré sans suspend
        worker.switch_device(b"dev2".hex())
        assert len(sinks_created) == 2
        sinks_created[0].stop.assert_called_once()
        sinks_created[1].start.assert_called_once()
        sinks_created[1].suspend.assert_not_called()
        sinks_created[1].setVolume.assert_called_with(0.75)


def test_sink_worker_switch_device_preserves_paused_state() -> None:
    dev1 = _fake_device(b"dev1", "Haut-parleurs")
    dev2 = _fake_device(b"dev2", "Casque USB")
    sinks_created: list[MagicMock] = []

    def _make_sink(target: MagicMock, fmt: QAudioFormat) -> MagicMock:
        sink = MagicMock()
        sinks_created.append(sink)
        return sink

    worker = _SinkWorker(_make_format(), 32768, 0.5, lambda n: (b"\x00" * n, 0), device_id=AUTO_DEVICE_ID)
    with (
        patch.object(audio_output.QMediaDevices, "audioOutputs", return_value=[dev1, dev2]),
        patch.object(audio_output.QMediaDevices, "defaultAudioOutput", return_value=dev1),
        patch.object(audio_output, "QAudioSink", side_effect=_make_sink),
    ):
        worker.create()
        worker.start(paused=True, drain_ms=0)
        worker.switch_device(b"dev2".hex())

        assert len(sinks_created) == 2
        sinks_created[1].start.assert_called_once()
        sinks_created[1].suspend.assert_called_once()
