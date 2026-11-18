"""Tests pour le sélecteur de moteur audio dans AudioToolsPopup."""

from __future__ import annotations

from unittest.mock import MagicMock

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QWidget

from amso.core.config import get_config_manager
from amso.ui.widgets.audio_tools_popup import AudioToolsPopup


class _DummyPlayer(QWidget):
    audio_outputs_changed = Signal()
    sleep_timer_changed = Signal(str, int)

    def __init__(self) -> None:
        super().__init__()
        self.reset_playback = MagicMock()

    def current_audio_output_device(self) -> str:
        return "auto"

    def audio_output_devices(self) -> list[tuple[str, str]]:
        return []

    def playback_rate(self) -> float:
        return 1.0

    def sleep_timer_state(self) -> tuple[str, int]:
        return ("off", 0)

    def is_eq_enabled(self) -> bool:
        return False

    def eq_preset(self) -> str:
        return "flat"

    def eq_gains(self) -> list[float]:
        return [0.0] * 10


def test_audio_tools_popup_engine_selector_syncs_and_switches() -> None:
    _app = QApplication.instance() or QApplication([])
    cfg = get_config_manager()
    cfg.set_audio_engine("buffer")

    player = _DummyPlayer()
    popup = AudioToolsPopup(player)  # type: ignore[arg-type]
    popup.sync_from_state()

    # Le sélecteur de moteur doit être en première position dans l'onglet Lecture
    playback_layout = popup._tab_playback.layout()
    assert playback_layout is not None
    assert playback_layout.itemAt(0).widget() is popup.lbl_audio_engine
    assert playback_layout.itemAt(1).widget() is popup.combo_engine

    assert popup.combo_engine.currentData() == "buffer"
    assert popup.combo_output_device.isEnabled()

    # Bascule vers vlc_direct
    vlc_idx = popup.combo_engine.findData("vlc_direct")
    assert vlc_idx >= 0
    popup.combo_engine.setCurrentIndex(vlc_idx)

    assert cfg.get_audio_engine() == "vlc_direct"
    player.reset_playback.assert_called_once()
    assert not popup.combo_output_device.isEnabled()
    assert not popup.chk_replaygain.isEnabled()
    assert not popup.slider_speed.isEnabled()

    popup.close()
    player.close()
