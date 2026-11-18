"""Navigation entre pages (identifiant de page active, sortie du Blind Test) et tables de retraduction."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication

from amso.core.database import DatabaseManager
from amso.ui.pages import navigation, retranslate
from amso.ui.views.main_window import MainWindow

_FR_JSON = Path(__file__).resolve().parent.parent / "amso" / "locales" / "fr.json"

# Widgets créés seulement sous certaines conditions (menu Aide macOS, bouton de don optionnel...)
_OPTIONAL_ATTRS = {"btn_about_donate", "menu_help", "action_about", "action_check_updates"}


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    return app if isinstance(app, QApplication) else QApplication([])


@pytest.fixture
def window(qapp: QApplication):
    win = MainWindow(db=DatabaseManager(":memory:"))
    yield win
    win.close()


def test_retranslate_tables_widgets_existants_sur_main_window(window: MainWindow) -> None:
    attrs = [a for a, _, _ in retranslate._TEXTS]
    attrs += [a for a, _ in retranslate._TITLES + retranslate._TOOLTIPS + retranslate._PLACEHOLDERS]
    attrs += list(retranslate._SUB_VIEWS)
    missing = [a for a in attrs if a not in _OPTIONAL_ATTRS and getattr(window, a, None) is None]
    assert missing == []


def test_retranslate_tables_cles_presentes_dans_fr_json() -> None:
    fr = json.loads(_FR_JSON.read_text(encoding="utf-8"))
    keys = [k for _, k, _ in retranslate._TEXTS]
    keys += [k for _, k in retranslate._TITLES + retranslate._TOOLTIPS + retranslate._PLACEHOLDERS]
    assert [k for k in keys if k not in fr] == []


def test_navigation_table_pages_existantes_sur_main_window(window: MainWindow) -> None:
    assert [a for a, _ in navigation._PAGE_IDS if getattr(window, a, None) is None] == []


@pytest.mark.parametrize(("attr", "page_id"), navigation._PAGE_IDS)
def test_page_changee_met_a_jour_la_page_active(window: MainWindow, attr: str, page_id: str) -> None:
    window.stacked_widget.setCurrentWidget(getattr(window, attr))
    assert window._current_active_page == page_id


def test_quitter_blind_test_coupe_la_lecture_et_le_standby(window: MainWindow, monkeypatch: pytest.MonkeyPatch) -> None:
    window._switch_to_page("blind_test", window.page_blind_test)
    pause, reset = MagicMock(), MagicMock()
    monkeypatch.setattr(window.player_service, "pause", pause)
    monkeypatch.setattr(window.player_service, "_reset_standby_player", reset)

    window._switch_to_page("player", window.page_player)

    pause.assert_called()
    reset.assert_called()
    assert window._current_active_page == "player"


def test_page_morceaux_conserve_le_mode_doublons(window: MainWindow) -> None:
    window._current_active_page = "duplicates"
    window.stacked_widget.setCurrentWidget(window.page_player)
    window._current_active_page = "duplicates"
    window.stacked_widget.setCurrentWidget(window.page_tracks)
    assert window._current_active_page == "duplicates"
