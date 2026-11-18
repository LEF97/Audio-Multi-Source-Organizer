"""Barre de titre standard des pages (titre à gauche, bouton d'aide à droite)."""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy

from amso.ui.styles import COLOR_TEXT_BRIGHT
from amso.ui.widgets.help_guide_popup import HelpButton


def page_title_qss(font_size: int = 16) -> str:
    return f"color: {COLOR_TEXT_BRIGHT}; font-size: {font_size}px; font-weight: 700;"


def build_page_top_bar(
    title: str,
    help_title_key: str,
    help_body_key: str,
) -> tuple[QFrame, QLabel, HelpButton]:
    """Construit la barre `topBarFrame` ; l'appelant conserve le label et le bouton pour `retranslate_ui`."""
    top_bar = QFrame()
    top_bar.setObjectName("topBarFrame")
    top_bar.setFixedHeight(50)
    top_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    layout = QHBoxLayout(top_bar)
    layout.setContentsMargins(20, 12, 20, 12)

    label = QLabel(title)
    label.setStyleSheet(page_title_qss())
    layout.addWidget(label)
    layout.addStretch()
    help_button = HelpButton(help_title_key, help_body_key, parent=top_bar)
    layout.addWidget(help_button)
    return top_bar, label, help_button
