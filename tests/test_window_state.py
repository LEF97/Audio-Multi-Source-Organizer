"""Tests de mémorisation et restauration de la taille et de l'état agrandi de la fenêtre principale."""

from __future__ import annotations

import ctypes
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QEvent, QPoint, QRect, QSize, Qt
from PySide6.QtGui import QGuiApplication, QMoveEvent, QResizeEvent
from PySide6.QtWidgets import QApplication

from amso.core.config import (
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    ConfigManager,
    get_config_manager,
)
from amso.core.database import DatabaseManager
from amso.ui.views.main_window import MainWindow


def test_config_window_state_defaults(tmp_path: Path) -> None:
    cfg = ConfigManager(tmp_path / "config.ini")
    assert cfg.get_window_size() == (DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
    assert cfg.get_window_position() is None
    assert cfg.get_window_maximized() is False


def test_config_window_state_persists_and_clamps_minimum(tmp_path: Path) -> None:
    path = tmp_path / "config.ini"
    cfg = ConfigManager(path)
    cfg.set_window_state(1440, 900, True, x=-1200, y=120)

    reloaded = ConfigManager(path)
    assert reloaded.get_window_size() == (1440, 900)
    assert reloaded.get_window_position() == (-1200, 120)
    assert reloaded.get_window_maximized() is True

    reloaded.set_window_state(400, 300, False, x=100, y=50)
    assert ConfigManager(path).get_window_size() == (MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
    assert ConfigManager(path).get_window_position() == (100, 50)
    assert ConfigManager(path).get_window_maximized() is False


def test_config_window_size_invalid_values_fallback_to_default(tmp_path: Path) -> None:
    path = tmp_path / "config.ini"
    path.write_text("[UI]\nwindow_width = abc\nwindow_height = xyz\nwindow_x = bad\nwindow_y = 10\n", encoding="utf-8")
    cfg = ConfigManager(path)
    assert cfg.get_window_size() == (DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
    assert cfg.get_window_position() is None


def test_main_window_restores_windowed_size_and_maximized_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = QApplication.instance() or QApplication([])
    assert app is not None
    cfg_path = tmp_path / "config.ini"
    monkeypatch.setenv("AMSO_CONFIG_PATH", str(cfg_path))
    cfg = get_config_manager()
    cfg.set_window_state(1100, 700, True)

    db = DatabaseManager(db_path=":memory:")
    window = MainWindow(db=db)

    assert window._windowed_size == (1100, 700)
    assert window._start_maximized is True
    assert (window.width(), window.height()) == (1100, 700)

    mock_show_max = MagicMock()
    mock_show = MagicMock()
    monkeypatch.setattr(window, "showMaximized", mock_show_max)
    monkeypatch.setattr(window, "show", mock_show)
    window.show_restored()
    mock_show_max.assert_called_once()
    mock_show.assert_not_called()

    window.close()


def test_main_window_preserves_windowed_size_when_closed_maximized(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = QApplication.instance() or QApplication([])
    assert app is not None
    cfg_path = tmp_path / "config.ini"
    monkeypatch.setenv("AMSO_CONFIG_PATH", str(cfg_path))

    db = DatabaseManager(db_path=":memory:")
    window = MainWindow(db=db)

    window.resize(1080, 720)
    window.resizeEvent(QResizeEvent(QSize(1080, 720), QSize(1200, 780)))
    window.move(120, 80)
    window.moveEvent(QMoveEvent(QPoint(120, 80), QPoint(0, 0)))
    assert window._windowed_size == (1080, 720)
    assert window._windowed_pos == (120, 80)

    # Simuler un passage en mode agrandi (taille plus grande mais état WindowMaximized actif)
    monkeypatch.setattr(window, "isMaximized", lambda: True)
    monkeypatch.setattr(window, "windowState", lambda: Qt.WindowState.WindowMaximized)
    window.resize(1920, 1040)
    window.resizeEvent(QResizeEvent(QSize(1920, 1040), QSize(1080, 720)))
    window.move(0, 0)
    window.moveEvent(QMoveEvent(QPoint(0, 0), QPoint(120, 80)))

    # La taille et la position fenêtrées mémorisées ne doivent pas être écrasées
    assert window._windowed_size == (1080, 720)
    assert window._windowed_pos == (120, 80)

    window.close()

    reloaded = ConfigManager(cfg_path)
    assert reloaded.get_window_size() == (1080, 720)
    assert reloaded.get_window_position() == (120, 80)
    assert reloaded.get_window_maximized() is True


def test_main_window_restores_on_valid_screen_and_falls_back_when_offscreen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = QApplication.instance() or QApplication([])
    assert app is not None

    primary_screen = MagicMock()
    primary_screen.availableGeometry.return_value = QRect(0, 0, 1920, 1040)
    secondary_screen = MagicMock()
    secondary_screen.availableGeometry.return_value = QRect(1920, 0, 1920, 1080)

    monkeypatch.setattr(QGuiApplication, "primaryScreen", lambda: primary_screen)
    monkeypatch.setattr(QGuiApplication, "screens", lambda: [primary_screen, secondary_screen])

    cfg_path = tmp_path / "config.ini"
    monkeypatch.setenv("AMSO_CONFIG_PATH", str(cfg_path))
    get_config_manager().set_window_state(1200, 780, False, x=2100, y=100)

    db = DatabaseManager(db_path=":memory:")
    window_on_secondary = MainWindow(db=db)
    assert window_on_secondary._windowed_pos == (2100, 100)
    assert (window_on_secondary.x(), window_on_secondary.y()) == (2100, 100)
    window_on_secondary.close()

    # Simuler le débranchement de l'écran secondaire : seul primary_screen reste connecté
    monkeypatch.setattr(QGuiApplication, "screens", lambda: [primary_screen])
    db2 = DatabaseManager(db_path=":memory:")
    window_fallback = MainWindow(db=db2)
    expected_cx = (1920 - 1200) // 2
    expected_cy = (1040 - 780) // 2
    assert window_fallback._windowed_pos == (expected_cx, expected_cy)
    assert (window_fallback.x(), window_fallback.y()) == (expected_cx, expected_cy)
    window_fallback.close()


def test_config_batch_writes_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = ConfigManager(tmp_path / "config.ini")
    save_calls = 0
    orig_save = cfg.save

    def counted_save() -> None:
        nonlocal save_calls
        save_calls += 1
        orig_save()

    monkeypatch.setattr(cfg, "save", counted_save)
    with cfg.batch():
        cfg.set_window_state(1200, 780, False, x=10, y=20)
        cfg.set_player_volume(75)
        cfg.set_player_muted(True)
        assert save_calls == 0

    assert save_calls == 1


def test_main_window_preserves_windowed_geometry_when_win32_zoomed_before_state_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = QApplication.instance() or QApplication([])
    assert app is not None
    cfg_path = tmp_path / "config.ini"
    monkeypatch.setenv("AMSO_CONFIG_PATH", str(cfg_path))

    window = MainWindow(db=DatabaseManager(db_path=":memory:"))
    window.resize(1040, 680)
    window.resizeEvent(QResizeEvent(QSize(1040, 680), QSize(1200, 780)))
    window.move(140, 90)
    window.moveEvent(QMoveEvent(QPoint(140, 90), QPoint(0, 0)))
    assert window._windowed_size == (1040, 680)
    assert window._windowed_pos == (140, 90)

    # Simuler la séquence Win32 SC_MAXIMIZE : WM_SIZE/WM_MOVE arrivent avant WindowStateChange
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(window, "internalWinId", lambda: 12345)
    monkeypatch.setattr(ctypes.windll.user32, "IsZoomed", lambda _hwnd: 1)
    monkeypatch.setattr(ctypes.windll.user32, "IsIconic", lambda _hwnd: 0)

    window.resize(2560, 1369)
    window.resizeEvent(QResizeEvent(QSize(2560, 1369), QSize(1040, 680)))
    window.move(0, -8)
    window.moveEvent(QMoveEvent(QPoint(0, -8), QPoint(140, 90)))

    assert window._windowed_size == (1040, 680)
    assert window._windowed_pos == (140, 90)

    # Retour à l'état normal via WindowStateChange
    monkeypatch.setattr(ctypes.windll.user32, "IsZoomed", lambda _hwnd: 0)
    window.resize(1040, 680)
    window.move(140, 90)
    window.changeEvent(QEvent(QEvent.Type.WindowStateChange))
    assert window._windowed_size == (1040, 680)
    assert window._windowed_pos == (140, 90)

    window.close()
