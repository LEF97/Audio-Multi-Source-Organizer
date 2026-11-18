"""Largeur du menu de gauche : restaurée à l'ouverture, modifiée uniquement par l'utilisateur."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication

from amso.core.config import get_config_manager
from amso.core.database import DatabaseManager


def test_sidebar_width_restored_and_stable_after_navigation(tmp_path, monkeypatch, isolate_config) -> None:
    from amso.ui.views.main_window import MainWindow

    monkeypatch.setenv("AMSO_QSETTINGS_PATH", str(tmp_path / "qt.ini"))
    app = QApplication.instance() or QApplication([])
    get_config_manager().set_sidebar_width(260)
    win = MainWindow(db=DatabaseManager(str(tmp_path / "t.db")))
    try:
        win.show()
        app.processEvents()
        app.processEvents()
        app.processEvents()
        app.processEvents()
        splitter = win._sidebar_splitter
        assert splitter.sizes()[0] == 260
        win.btn_playlist.click()
        app.processEvents()
        app.processEvents()
        assert splitter.sizes()[0] == 260

        splitter.setSizes([230, splitter.sizes()[1] + 30])
        splitter.splitterMoved.emit(230, 1)
        assert get_config_manager().get_sidebar_width() == 230
    finally:
        win.close()
