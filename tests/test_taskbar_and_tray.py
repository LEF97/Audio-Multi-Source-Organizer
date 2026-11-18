"""Tests unitaires du mini-lecteur barre des tâches Windows et de l'icône de notification."""

from __future__ import annotations

import ctypes
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

from amso.core.database import TrackRecord
from amso.services import windows_taskbar as wt
from amso.services.windows_taskbar import (
    _HOTKEY_NEXT_ID,
    _HOTKEY_PLAY_PAUSE_ID,
    THBN_CLICKED,
    WM_APPCOMMAND,
    WM_COMMAND,
    WM_HOTKEY,
    TaskbarProgressState,
    WindowsTaskbarController,
)
from amso.ui.pages.taskbar_controller import (
    _BTN_NEXT_ID,
    _BTN_PLAY_PAUSE_ID,
    _BTN_PREV_ID,
    TaskbarAndTrayMixin,
    _format_track_label,
    _render_media_image,
)


def _ensure_qapp() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def _make_track(title: str = "Lotus Flower", artist: str = "Radiohead") -> TrackRecord:
    return TrackRecord(
        source_ref="C:/Music/lotus.flac",
        id=1,
        source_id=1,
        file_name="lotus.flac",
        title=title,
        artist=artist,
        album="The King of Limbs",
    )


class _DummySignal:
    def __init__(self) -> None:
        self._callbacks: list[object] = []

    def connect(self, cb: object) -> None:
        self._callbacks.append(cb)


class _DummyPlayerService:
    def __init__(self) -> None:
        self.state_changed = _DummySignal()
        self.track_changed = _DummySignal()
        self.position_changed = _DummySignal()
        self.playlist_updated = _DummySignal()
        self._playlist: list[TrackRecord] = [_make_track()]
        self._track: TrackRecord | None = self._playlist[0]
        self._playing = False
        self._current_ms = 12000
        self._total_ms = 300000
        self.previous = MagicMock()
        self.toggle_play_pause = MagicMock()
        self.next = MagicMock()

    @property
    def playlist(self) -> list[TrackRecord]:
        return self._playlist

    @property
    def current_track(self) -> TrackRecord | None:
        return self._track

    @property
    def is_playing(self) -> bool:
        return self._playing

    @property
    def current_time_ms(self) -> int:
        return self._current_ms

    @property
    def total_time_ms(self) -> int:
        return self._total_ms


class _DummyHost(TaskbarAndTrayMixin):
    def __init__(self, qapp: object) -> None:
        self._qapp = qapp
        self.player_service = _DummyPlayerService()
        self._player_state = "stopped"
        self._current_active_page = "player"
        self.window_title = ""
        self._visible = True
        self._minimized = False

    def setWindowTitle(self, title: str) -> None:
        self.window_title = title

    def isVisible(self) -> bool:
        return self._visible

    def isMinimized(self) -> bool:
        return self._minimized

    def show(self) -> None:
        self._visible = True

    def hide(self) -> None:
        self._visible = False

    def showNormal(self) -> None:
        self._minimized = False
        self._visible = True

    def raise_(self) -> None:
        pass

    def activateWindow(self) -> None:
        pass

    def close(self) -> None:
        pass

    def winId(self) -> int:
        return 12345


def test_format_track_label_formats_and_truncates() -> None:
    assert _format_track_label(None) == ""
    assert _format_track_label(_make_track("Lotus", "Radiohead")) == "Radiohead — Lotus"
    assert _format_track_label(_make_track("Solo", "")) == "Solo"
    long_track = _make_track("A" * 60, "Artist")
    formatted = _format_track_label(long_track, max_len=20)
    assert len(formatted) == 20
    assert formatted.endswith("…")


def test_render_media_image_creates_non_empty_images() -> None:
    _ensure_qapp()
    for kind in ("previous", "play", "pause", "next"):
        img = _render_media_image(kind, size=32)
        assert img.width() == 32
        assert img.height() == 32
        assert any(bytes(img.constBits()))


def test_windows_taskbar_noop_off_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(wt.sys, "platform", "linux")
    ctrl = WindowsTaskbarController()
    assert ctrl.taskbar_created_msg == 0
    assert ctrl.attach(1234) is False
    assert ctrl.set_progress_state(TaskbarProgressState.NORMAL) is False
    assert ctrl.set_progress_value(10, 100) is False
    assert ctrl.set_thumb_buttons([]) is False
    assert ctrl.parse_native_message(b"windows_generic_MSG", 1) == (False, None)
    assert wt.create_hicon_from_bgra(32, 32, b"\x00" * 4096) == 0


@pytest.mark.skipif(sys.platform != "win32", reason="Messages Win32 testés uniquement sous Windows")
def test_windows_taskbar_parse_native_message_win32() -> None:
    ctrl = WindowsTaskbarController()
    msg = wt._WinMsg()
    msg.message = WM_COMMAND
    msg.wParam = (THBN_CLICKED << 16) | _BTN_PLAY_PAUSE_ID
    created, btn_id = ctrl.parse_native_message(b"windows_generic_MSG", ctypes.addressof(msg))
    assert created is False
    assert btn_id == _BTN_PLAY_PAUSE_ID

    if ctrl.taskbar_created_msg:
        msg.message = ctrl.taskbar_created_msg
        msg.wParam = 0
        created, btn_id = ctrl.parse_native_message(b"windows_generic_MSG", ctypes.addressof(msg))
        assert created is True
        assert btn_id is None

    msg.message = WM_HOTKEY
    msg.wParam = _HOTKEY_PLAY_PAUSE_ID
    assert ctrl.parse_media_command(b"windows_generic_MSG", ctypes.addressof(msg)) == "play_pause"

    msg.message = WM_HOTKEY
    msg.wParam = _HOTKEY_NEXT_ID
    assert ctrl.parse_media_command(b"windows_generic_MSG", ctypes.addressof(msg)) == "next"

    msg.message = WM_APPCOMMAND
    msg.lParam = 14 << 16  # APPCOMMAND_MEDIA_PLAY_PAUSE
    assert ctrl.parse_media_command(b"windows_generic_MSG", ctypes.addressof(msg)) == "play_pause"


def test_taskbar_mixin_syncs_state_progress_and_blind_test_guard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    qapp = _ensure_qapp()
    fake_taskbar = SimpleNamespace(
        attach=MagicMock(return_value=True),
        set_thumb_buttons=MagicMock(return_value=True),
        set_progress_state=MagicMock(return_value=True),
        set_progress_value=MagicMock(return_value=True),
        parse_native_message=MagicMock(return_value=(False, None)),
        parse_media_command=MagicMock(return_value=None),
        register_media_hotkeys=MagicMock(return_value=[]),
        dispose=MagicMock(),
    )
    monkeypatch.setattr("amso.ui.pages.taskbar_controller.WindowsTaskbarController", lambda: fake_taskbar)
    monkeypatch.setattr("amso.ui.pages.taskbar_controller.QSystemTrayIcon.isSystemTrayAvailable", lambda: False)
    monkeypatch.setattr("amso.ui.pages.taskbar_controller.QShortcut", MagicMock())

    host = _DummyHost(qapp)
    host._setup_taskbar_and_tray()

    # État initial : arrêté
    fake_taskbar.set_progress_state.assert_called_with(TaskbarProgressState.NO_PROGRESS)
    assert "Radiohead — Lotus Flower" not in host.window_title

    # Passage en lecture (même si LibVLC est encore en Opening/Buffering et is_playing == False)
    host.player_service._playing = False
    host._on_taskbar_state_changed("playing")
    fake_taskbar.set_progress_state.assert_called_with(TaskbarProgressState.NORMAL)
    fake_taskbar.set_progress_value.assert_called_with(12000, 300000)
    assert "Radiohead — Lotus Flower" in host.window_title

    buttons = fake_taskbar.set_thumb_buttons.call_args[0][0]
    assert [b.button_id for b in buttons] == [_BTN_PREV_ID, _BTN_PLAY_PAUSE_ID, _BTN_NEXT_ID]
    assert all(b.enabled for b in buttons)
    assert buttons[1].hicon == host._taskbar_hicons.get("pause", 0)

    # Mode exclusif Blind Test : contrôles désactivés et commandes ignorées
    host._current_active_page = "blind_test"
    host._sync_taskbar_and_tray()
    fake_taskbar.set_progress_state.assert_called_with(TaskbarProgressState.NO_PROGRESS)
    buttons_bt = fake_taskbar.set_thumb_buttons.call_args[0][0]
    assert all(not b.enabled for b in buttons_bt)

    host._on_external_play_pause()
    host._on_external_next()
    host._on_external_previous()
    host.player_service.toggle_play_pause.assert_not_called()
    host.player_service.next.assert_not_called()
    host.player_service.previous.assert_not_called()

    # Retour sur la page lecteur : commandes de nouveau actives
    host._current_active_page = "player"
    host._on_external_play_pause()
    host.player_service.toggle_play_pause.assert_called_once()

    host._cleanup_taskbar_and_tray()
    fake_taskbar.dispose.assert_called_once()
