"""Tests pour le bouton d'aide et la popup HelpGuidePopup dans PlayerView."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication

from amso.core.i18n import get_i18n, tr
from amso.services.player_service import PlayerService
from amso.ui.views.player_view import PlayerView
from amso.ui.widgets.help_guide_popup import HelpButton, HelpGuidePopup, create_help_button


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def fr_lang() -> Iterator[str]:
    i18n = get_i18n()
    prev = i18n.current_language
    i18n.set_language("fr")
    yield "fr"
    i18n.set_language(prev)


def test_help_button_creation_uses_lightbulb_and_tooltip(qapp: QApplication, fr_lang: str) -> None:
    btn = create_help_button("player.btn_help")
    assert btn.text() == "💡"
    assert btn.toolTip() == tr("player.btn_help")


def test_help_guide_popup_displays_translated_content_and_closes(qapp: QApplication, fr_lang: str) -> None:
    popup = HelpGuidePopup("player.help_title", "player.help_body")
    assert "Bienvenue dans le Lecteur Audio" in popup.lbl_title.text()
    assert "Démarrer votre écoute" in popup.lbl_body.text()
    assert popup.btn_close.text() == tr("common.close")

    popup.show()
    assert popup.isVisible()
    popup.btn_close.click()
    assert not popup.isVisible()


def test_player_view_help_button_toggles_popup(qapp: QApplication, fr_lang: str) -> None:
    view = PlayerView(PlayerService())
    assert view.btn_help.parent() is view.top_bar

    view.btn_help.click()
    assert view._help_popup is not None
    assert view._help_popup.isVisible()

    view.btn_help.click()
    assert not view._help_popup.isVisible()
    view.close()


@pytest.mark.parametrize(
    ("title_key", "body_key"),
    [
        ("player.help_title", "player.help_body"),
        ("blind_test.help_title", "blind_test.help_body"),
        ("playlist.help_title", "playlist.help_body"),
        ("tracks.help_title", "tracks.help_body"),
        ("duplicates.help_title", "duplicates.help_body"),
        ("folders.help_title", "folders.help_body"),
        ("library_sources.help_title", "library_sources.help_body"),
        ("settings.general_help_title", "settings.general_help_body"),
        ("settings.sound_help_title", "settings.sound_help_body"),
        ("settings.player_help_title", "settings.player_help_body"),
        ("settings.effects_help_title", "settings.effects_help_body"),
        ("logs.help_title", "logs.help_body"),
        ("settings.about_help_title", "settings.about_help_body"),
    ],
)
def test_help_button_opens_and_translates_all_pages(
    qapp: QApplication,
    fr_lang: str,
    title_key: str,
    body_key: str,
) -> None:
    btn = HelpButton(title_key, body_key)
    assert btn.text() == "💡"
    assert btn.toolTip() == tr("common.help_tooltip")

    btn.click()
    assert btn._popup is not None
    assert btn._popup.isVisible()
    assert title_key not in btn._popup.lbl_title.text()
    assert body_key not in btn._popup.lbl_body.text()
    btn.retranslate_ui()
    btn._popup.close()


def test_help_button_set_keys_updates_open_popup(qapp: QApplication, fr_lang: str) -> None:
    btn = HelpButton("tracks.help_title", "tracks.help_body")
    btn.click()
    assert btn._popup is not None
    assert "Morceaux" in btn._popup.lbl_title.text()

    btn.set_keys("duplicates.help_title", "duplicates.help_body")
    assert "Doublons" in btn._popup.lbl_title.text()
    assert "liste de lecture active" in btn._popup.lbl_body.text()
    btn._popup.close()
