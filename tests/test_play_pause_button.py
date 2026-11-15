"""Bouton Play/Pause : bascule d'état via setText, zone cliquable circulaire, couleur issue de la pochette."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication

from amso.ui.widgets.play_pause_button import PlayPauseButton


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    """Instance QApplication unique (les pixmaps et widgets en ont besoin)."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def button(qapp: QApplication) -> PlayPauseButton:
    return PlayPauseButton()


def test_set_text_pause_glyph_marks_button_as_playing(button: PlayPauseButton) -> None:
    button.setText("⏸")
    assert button._playing is True
    button.setText("▶")
    assert button._playing is False


def test_hit_button_corner_outside_disc_is_ignored(button: PlayPauseButton) -> None:
    assert button.hitButton(QPoint(32, 32)) is True
    assert button.hitButton(QPoint(2, 2)) is False
