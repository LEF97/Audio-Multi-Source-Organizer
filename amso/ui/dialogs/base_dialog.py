"""Base des dialogues modaux AMSO : titre, largeur minimale, poignée de redimensionnement, thème sombre."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QWidget

from amso.ui.theme import DARK_THEME_QSS


class AmsoDialog(QDialog):
    def __init__(self, title: str, min_width: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(min_width)
        self.setSizeGripEnabled(True)
        self.setModal(True)
        self.setStyleSheet(DARK_THEME_QSS)
