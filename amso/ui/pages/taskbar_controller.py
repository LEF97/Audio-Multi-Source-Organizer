"""Contrôleur barre des tâches Windows (ITaskbarList3) et zone de notification (QSystemTrayIcon)."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QPointF, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QIcon, QImage, QKeySequence, QPainter, QPixmap, QPolygonF, QShortcut
from PySide6.QtWidgets import QMainWindow, QMenu, QSystemTrayIcon

from amso import __version__
from amso.core.i18n import tr
from amso.core.startup_timing import get_startup_clock
from amso.services.windows_taskbar import (
    TaskbarProgressState,
    ThumbButtonSpec,
    WindowsTaskbarController,
    create_hicon_from_bgra,
    destroy_hicon,
)
from amso.ui.resources import get_app_icon

if TYPE_CHECKING:
    from amso.core.database import TrackRecord

logger = logging.getLogger(__name__)

_BTN_PREV_ID = 1001
_BTN_PLAY_PAUSE_ID = 1002
_BTN_NEXT_ID = 1003
_PROGRESS_THROTTLE_S = 0.5

if TYPE_CHECKING:
    _MixinBase = QMainWindow
else:
    _MixinBase = object


def _render_media_image(kind: str, size: int = 32) -> QImage:
    """Dessine une icône média vectorielle nette sur fond transparent."""
    img = QImage(size, size, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)

    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(241, 245, 249))

    s = float(size)
    if kind == "play":
        poly = QPolygonF([QPointF(s * 0.28, s * 0.20), QPointF(s * 0.80, s * 0.50), QPointF(s * 0.28, s * 0.80)])
        painter.drawPolygon(poly)
    elif kind == "pause":
        bar_w = s * 0.18
        bar_h = s * 0.56
        y = s * 0.22
        painter.drawRoundedRect(int(s * 0.26), int(y), int(bar_w), int(bar_h), 2, 2)
        painter.drawRoundedRect(int(s * 0.56), int(y), int(bar_w), int(bar_h), 2, 2)
    elif kind == "previous":
        painter.drawRoundedRect(int(s * 0.20), int(s * 0.22), int(s * 0.12), int(s * 0.56), 1, 1)
        poly = QPolygonF([QPointF(s * 0.78, s * 0.22), QPointF(s * 0.36, s * 0.50), QPointF(s * 0.78, s * 0.78)])
        painter.drawPolygon(poly)
    elif kind == "next":
        poly = QPolygonF([QPointF(s * 0.22, s * 0.22), QPointF(s * 0.64, s * 0.50), QPointF(s * 0.22, s * 0.78)])
        painter.drawPolygon(poly)
        painter.drawRoundedRect(int(s * 0.68), int(s * 0.22), int(s * 0.12), int(s * 0.56), 1, 1)

    painter.end()
    return img


def _format_track_label(track: TrackRecord | None, max_len: int = 56) -> str:
    """Formate 'Artiste — Titre' (ou nom de fichier) avec troncature propre."""
    if track is None:
        return ""
    title = (track.title or "").strip()
    artist = (track.artist or "").strip()
    if artist and title:
        label = f"{artist} — {title}"
    else:
        label = title or (track.file_name or "")
    if len(label) > max_len:
        return f"{label[: max_len - 1].rstrip()}…"
    return label


class TaskbarAndTrayMixin(_MixinBase):
    """Contrôleur du mini-lecteur barre des tâches Windows et de l'icône de notification."""

    if TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any: ...

    def _setup_taskbar_and_tray(self) -> None:
        """Initialise les contrôleurs Taskbar Windows et QSystemTrayIcon et connecte PlayerService."""
        self._taskbar = WindowsTaskbarController()
        self._taskbar_hicons: dict[str, int] = {}
        self._media_qicons: dict[str, QIcon] = {}
        self._last_taskbar_progress_ts: float = 0.0

        for kind in ("previous", "play", "pause", "next"):
            img = _render_media_image(kind, size=32)
            self._media_qicons[kind] = QIcon(QPixmap.fromImage(img))
            raw_bytes = bytes(img.constBits())
            hicon = create_hicon_from_bgra(img.width(), img.height(), raw_bytes)
            if hicon:
                self._taskbar_hicons[kind] = hicon

        self._tray_icon: QSystemTrayIcon | None = None
        self._tray_menu: QMenu | None = None
        self._tray_track_action: QAction | None = None
        self._tray_prev_action: QAction | None = None
        self._tray_play_pause_action: QAction | None = None
        self._tray_next_action: QAction | None = None
        self._tray_toggle_window_action: QAction | None = None
        self._tray_quit_action: QAction | None = None

        self._init_system_tray()
        self._init_media_shortcuts()

        self.player_service.state_changed.connect(self._on_taskbar_state_changed)
        self.player_service.track_changed.connect(self._on_taskbar_track_changed)
        self.player_service.position_changed.connect(self._on_taskbar_position_changed)
        self.player_service.playlist_updated.connect(self._sync_taskbar_and_tray)

        self._sync_taskbar_and_tray()
        # Repli si TaskbarButtonCreated a déjà été émis avant le câblage ou filtré
        QTimer.singleShot(800, self._ensure_taskbar_attached)

    def _ensure_taskbar_attached(self) -> None:
        """Attache ITaskbarList3 et enregistre les touches média globales si pas encore fait."""
        if not hasattr(self, "_taskbar") or not self.isVisible():
            return
        hwnd = int(self.winId())
        self._taskbar.register_media_hotkeys(hwnd)
        if self._taskbar.buttons_added:
            return
        attached = self._taskbar.attach(hwnd)
        get_startup_clock().note("taskbar: fallback attach=%s", attached)
        if attached:
            self._sync_taskbar_buttons()
            self._sync_taskbar_progress_state()
            get_startup_clock().note("taskbar: fallback buttons_added=%s", self._taskbar.buttons_added)

    def _init_media_shortcuts(self) -> None:
        """Installe les raccourcis clavier média Qt (actifs lorsque la fenêtre a le focus)."""
        self._media_shortcuts: list[QShortcut] = []
        bindings: list[tuple[Qt.Key, Any]] = [
            (Qt.Key.Key_MediaPrevious, self._on_external_previous),
            (Qt.Key.Key_MediaPlay, self._on_external_play_pause),
            (Qt.Key.Key_MediaPause, self._on_external_play_pause),
            (Qt.Key.Key_MediaTogglePlayPause, self._on_external_play_pause),
            (Qt.Key.Key_MediaNext, self._on_external_next),
            (Qt.Key.Key_MediaStop, self._on_external_stop),
        ]
        for key, callback in bindings:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
            shortcut.activated.connect(callback)
            self._media_shortcuts.append(shortcut)

    def _init_system_tray(self) -> None:
        """Crée l'icône et le menu contextuel dans la zone de notification si disponible."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        tray = QSystemTrayIcon(get_app_icon(), self)
        menu = QMenu(self)

        track_action = QAction(tr("tray.no_track"), menu)
        track_action.setEnabled(False)
        menu.addAction(track_action)
        menu.addSeparator()

        prev_action = QAction(self._media_qicons["previous"], tr("player.btn_previous"), menu)
        prev_action.triggered.connect(self._on_external_previous)
        menu.addAction(prev_action)

        play_pause_action = QAction(self._media_qicons["play"], tr("player.btn_play"), menu)
        play_pause_action.triggered.connect(self._on_external_play_pause)
        menu.addAction(play_pause_action)

        next_action = QAction(self._media_qicons["next"], tr("player.btn_next"), menu)
        next_action.triggered.connect(self._on_external_next)
        menu.addAction(next_action)

        menu.addSeparator()
        toggle_win_action = QAction(tr("tray.hide_window"), menu)
        toggle_win_action.triggered.connect(self._toggle_window_visibility)
        menu.addAction(toggle_win_action)

        quit_action = QAction(tr("tray.quit"), menu)
        quit_action.triggered.connect(self.close)
        menu.addAction(quit_action)

        menu.aboutToShow.connect(self._refresh_tray_window_action)
        tray.setContextMenu(menu)
        tray.activated.connect(self._on_tray_activated)
        tray.show()

        self._tray_icon = tray
        self._tray_menu = menu
        self._tray_track_action = track_action
        self._tray_prev_action = prev_action
        self._tray_play_pause_action = play_pause_action
        self._tray_next_action = next_action
        self._tray_toggle_window_action = toggle_win_action
        self._tray_quit_action = quit_action

    def _is_exclusive_mode_active(self) -> bool:
        """Retourne True quand le Blind Test (mode exclusif) est actif."""
        return getattr(self, "_current_active_page", None) == "blind_test"

    def _on_external_previous(self) -> None:
        if not self._is_exclusive_mode_active():
            self.player_service.previous()

    def _on_external_play_pause(self) -> None:
        if not self._is_exclusive_mode_active():
            self.player_service.toggle_play_pause()

    def _on_external_next(self) -> None:
        if not self._is_exclusive_mode_active():
            self.player_service.next()

    def _on_external_stop(self) -> None:
        if not self._is_exclusive_mode_active():
            self.player_service.stop()

    def _on_external_play(self) -> None:
        if not self._is_exclusive_mode_active() and not self.player_service.is_playing:
            self.player_service.play()

    def _on_external_pause(self) -> None:
        if not self._is_exclusive_mode_active() and self.player_service.is_playing:
            self.player_service.pause()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self._restore_and_focus_window()

    def _restore_and_focus_window(self) -> None:
        if self.isMinimized():
            self.showNormal()
        else:
            self.show()
        self.raise_()
        self.activateWindow()
        self._refresh_tray_window_action()

    def _toggle_window_visibility(self) -> None:
        if self.isVisible() and not self.isMinimized():
            self.hide()
        else:
            self._restore_and_focus_window()
        self._refresh_tray_window_action()

    def _refresh_tray_window_action(self) -> None:
        if self._tray_toggle_window_action is None:
            return
        if self.isVisible() and not self.isMinimized():
            self._tray_toggle_window_action.setText(tr("tray.hide_window"))
        else:
            self._tray_toggle_window_action.setText(tr("tray.show_window"))

    def _handle_taskbar_native_event(self, event_type: Any, message: Any) -> bool:
        """Traite TaskbarButtonCreated et THBN_CLICKED depuis MainWindow.nativeEvent."""
        if not hasattr(self, "_taskbar"):
            return False

        raw_type = bytes(event_type) if not isinstance(event_type, bytes) else event_type
        created, clicked_id = self._taskbar.parse_native_message(raw_type, message)
        if created:
            hwnd = int(self.winId())
            self._taskbar.register_media_hotkeys(hwnd)
            attached = self._taskbar.attach(hwnd)
            get_startup_clock().note("taskbar: TaskbarButtonCreated attach=%s", attached)
            if attached:
                self._sync_taskbar_buttons()
                self._sync_taskbar_progress_state()
                get_startup_clock().note("taskbar: buttons_added=%s", self._taskbar.buttons_added)
            return False

        if clicked_id == _BTN_PREV_ID:
            self._on_external_previous()
        elif clicked_id == _BTN_PLAY_PAUSE_ID:
            self._on_external_play_pause()
        elif clicked_id == _BTN_NEXT_ID:
            self._on_external_next()
        else:
            media_action = self._taskbar.parse_media_command(raw_type, message)
            if media_action is not None:
                self._dispatch_media_action(media_action)
                return True
        return False

    def _dispatch_media_action(self, action: str) -> None:
        dispatch = {
            "previous": self._on_external_previous,
            "play_pause": self._on_external_play_pause,
            "play": self._on_external_play,
            "pause": self._on_external_pause,
            "next": self._on_external_next,
            "stop": self._on_external_stop,
        }
        handler = dispatch.get(action)
        if handler is not None:
            handler()

    def _on_taskbar_state_changed(self, state: str) -> None:
        self._player_state = state
        self._sync_taskbar_and_tray()

    def _on_taskbar_track_changed(self, _track: TrackRecord | None) -> None:
        self._sync_taskbar_and_tray()

    def _on_taskbar_position_changed(self, current_ms: int, total_ms: int, _ratio: float) -> None:
        if not hasattr(self, "_taskbar") or self._is_exclusive_mode_active():
            return
        now = time.monotonic()
        if now - self._last_taskbar_progress_ts < _PROGRESS_THROTTLE_S:
            return
        self._last_taskbar_progress_ts = now
        if total_ms > 0:
            self._taskbar.set_progress_value(current_ms, total_ms)

    def _sync_taskbar_and_tray(self) -> None:
        """Synchronise la miniature Windows, la barre de progression, le tray et le titre."""
        if not hasattr(self, "_taskbar"):
            return
        self._sync_window_title_for_track()
        self._sync_taskbar_buttons()
        self._sync_taskbar_progress_state()
        self._sync_tray_menu()

    def _sync_window_title_for_track(self) -> None:
        base_title = f"{tr('app.window_title')} v{__version__}"
        track = self.player_service.current_track
        state = getattr(self, "_player_state", "stopped")
        label = _format_track_label(track)
        if label and state in ("playing", "paused"):
            self.setWindowTitle(f"{label} — {base_title}")
        else:
            self.setWindowTitle(base_title)

    def _sync_taskbar_buttons(self) -> None:
        exclusive = self._is_exclusive_mode_active()
        has_playlist = bool(self.player_service.playlist)
        controls_enabled = has_playlist and not exclusive
        # Utiliser _player_state plutôt que player_service.is_playing car LibVLC peut être en Opening/Buffering
        is_playing = getattr(self, "_player_state", "stopped") == "playing"

        play_key = "pause" if is_playing else "play"
        play_tip = tr("player.btn_pause") if is_playing else tr("player.btn_play")

        specs = [
            ThumbButtonSpec(
                button_id=_BTN_PREV_ID,
                hicon=self._taskbar_hicons.get("previous", 0),
                tooltip=tr("player.btn_previous"),
                enabled=controls_enabled,
            ),
            ThumbButtonSpec(
                button_id=_BTN_PLAY_PAUSE_ID,
                hicon=self._taskbar_hicons.get(play_key, 0),
                tooltip=play_tip,
                enabled=controls_enabled,
            ),
            ThumbButtonSpec(
                button_id=_BTN_NEXT_ID,
                hicon=self._taskbar_hicons.get("next", 0),
                tooltip=tr("player.btn_next"),
                enabled=controls_enabled,
            ),
        ]
        self._taskbar.set_thumb_buttons(specs)

    def _sync_taskbar_progress_state(self) -> None:
        if self._is_exclusive_mode_active():
            self._taskbar.set_progress_state(TaskbarProgressState.NO_PROGRESS)
            return

        state = getattr(self, "_player_state", "stopped")
        if state == "playing":
            self._taskbar.set_progress_state(TaskbarProgressState.NORMAL)
            total = self.player_service.total_time_ms
            if total > 0:
                self._taskbar.set_progress_value(self.player_service.current_time_ms, total)
        elif state == "paused":
            self._taskbar.set_progress_state(TaskbarProgressState.PAUSED)
            total = self.player_service.total_time_ms
            if total > 0:
                self._taskbar.set_progress_value(self.player_service.current_time_ms, total)
        else:
            self._taskbar.set_progress_state(TaskbarProgressState.NO_PROGRESS)

    def _sync_tray_menu(self) -> None:
        if self._tray_icon is None:
            return

        exclusive = self._is_exclusive_mode_active()
        has_playlist = bool(self.player_service.playlist)
        controls_enabled = has_playlist and not exclusive
        is_playing = getattr(self, "_player_state", "stopped") == "playing"

        track_label = _format_track_label(self.player_service.current_track, max_len=48)
        display_track = track_label if track_label else tr("tray.no_track")

        if self._tray_track_action is not None:
            self._tray_track_action.setText(display_track)
        if self._tray_prev_action is not None:
            self._tray_prev_action.setText(tr("player.btn_previous"))
            self._tray_prev_action.setEnabled(controls_enabled)
        if self._tray_play_pause_action is not None:
            self._tray_play_pause_action.setText(tr("player.btn_pause") if is_playing else tr("player.btn_play"))
            self._tray_play_pause_action.setIcon(self._media_qicons["pause" if is_playing else "play"])
            self._tray_play_pause_action.setEnabled(controls_enabled)
        if self._tray_next_action is not None:
            self._tray_next_action.setText(tr("player.btn_next"))
            self._tray_next_action.setEnabled(controls_enabled)
        if self._tray_quit_action is not None:
            self._tray_quit_action.setText(tr("tray.quit"))
        self._refresh_tray_window_action()

        tooltip = f"{tr('app.window_title')} — {track_label}" if track_label else tr("app.window_title")
        self._tray_icon.setToolTip(tooltip)

    def _cleanup_taskbar_and_tray(self) -> None:
        """Libère le tray, le contrôleur COM Taskbar et les HICON Win32."""
        tray_icon = getattr(self, "_tray_icon", None)
        if tray_icon is not None:
            tray_icon.hide()
        if hasattr(self, "_taskbar"):
            self._taskbar.dispose()
        for hicon in getattr(self, "_taskbar_hicons", {}).values():
            destroy_hicon(hicon)
        if hasattr(self, "_taskbar_hicons"):
            self._taskbar_hicons.clear()
