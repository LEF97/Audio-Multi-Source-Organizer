"""Panneau flottant de guide utilisateur ancré à un bouton d'aide."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from amso.core.i18n import tr
from amso.ui.styles import (
    COLOR_BG_CARD,
    COLOR_BG_HOVER,
    COLOR_BORDER,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_TEXT,
    COLOR_TEXT_BRIGHT,
    icon_button_qss,
)
from amso.ui.widgets.common import AnchoredPopup

_POPUP_WIDTH = 420
_HELP_POPUP_QSS = f"""
    QFrame#HelpGuidePopup {{
        background-color: {COLOR_BG_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: 10px;
    }}
    QLabel#helpTitle {{
        color: {COLOR_TEXT_BRIGHT};
        font-size: 14px;
        font-weight: 700;
    }}
    QLabel#helpBody {{
        color: {COLOR_TEXT};
        font-size: 12.5px;
        line-height: 1.45;
    }}
    QPushButton#helpCloseBtn {{
        background-color: {COLOR_BG_HOVER};
        color: {COLOR_TEXT_BRIGHT};
        border: 1px solid {COLOR_BORDER};
        border-radius: 6px;
        padding: 5px 14px;
        font-size: 12px;
        font-weight: 600;
    }}
    QPushButton#helpCloseBtn:hover {{
        border-color: {COLOR_PRIMARY_HOVER};
        background-color: {COLOR_PRIMARY};
    }}
"""


def create_help_button(tooltip_key: str, parent: QWidget | None = None) -> QPushButton:
    """Crée un bouton d'aide circulaire standardisé pour les barres d'en-tête."""
    btn = QPushButton("💡", parent)
    btn.setFixedSize(30, 30)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setToolTip(tr(tooltip_key))
    btn.setStyleSheet(icon_button_qss(radius=15, font_size=14))
    return btn


class HelpButton(QPushButton):
    """Bouton d'aide circulaire gérant sa propre popup de guide et sa retraduction."""

    def __init__(
        self,
        title_key: str,
        body_key: str,
        tooltip_key: str = "common.help_tooltip",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("💡", parent)
        self._title_key = title_key
        self._body_key = body_key
        self._tooltip_key = tooltip_key
        self._popup: HelpGuidePopup | None = None

        self.setFixedSize(30, 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(tr(tooltip_key))
        self.setStyleSheet(icon_button_qss(radius=15, font_size=14))
        self.clicked.connect(self._on_clicked)

    def _on_clicked(self) -> None:
        if self._popup is None:
            self._popup = HelpGuidePopup(self._title_key, self._body_key, self)
        self._popup.toggle_anchored(self)

    def set_keys(self, title_key: str, body_key: str) -> None:
        """Change dynamiquement le guide affiché (ex. vue partagée Morceaux / Doublons)."""
        self._title_key = title_key
        self._body_key = body_key
        if self._popup is not None:
            self._popup.set_keys(title_key, body_key)

    def retranslate_ui(self) -> None:
        """Met à jour l'infobulle et la popup de guide si elle existe."""
        self.setToolTip(tr(self._tooltip_key))
        if self._popup is not None:
            self._popup.retranslate_ui()


class HelpGuidePopup(AnchoredPopup):
    """Panneau flottant présentant le guide de prise en main d'une vue."""

    def __init__(self, title_key: str, body_key: str, parent: QWidget | None = None) -> None:
        super().__init__(parent, prefer_below=True)
        self.setObjectName("HelpGuidePopup")
        self.setFixedWidth(_POPUP_WIDTH)
        self.setStyleSheet(_HELP_POPUP_QSS)
        self._title_key = title_key
        self._body_key = body_key

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        self.lbl_title = QLabel(self)
        self.lbl_title.setObjectName("helpTitle")
        self.lbl_title.setWordWrap(True)
        root.addWidget(self.lbl_title)

        self.lbl_body = QLabel(self)
        self.lbl_body.setObjectName("helpBody")
        self.lbl_body.setTextFormat(Qt.TextFormat.RichText)
        self.lbl_body.setWordWrap(True)
        root.addWidget(self.lbl_body)

        footer = QHBoxLayout()
        footer.addStretch()
        self.btn_close = QPushButton(self)
        self.btn_close.setObjectName("helpCloseBtn")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.close)
        footer.addWidget(self.btn_close)
        root.addLayout(footer)

        self.retranslate_ui()

    def set_keys(self, title_key: str, body_key: str) -> None:
        """Met à jour les clés de traduction affichées dans la popup."""
        self._title_key = title_key
        self._body_key = body_key
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        """Met à jour les textes du guide selon la langue active."""
        self.lbl_title.setText(f"💡  {tr(self._title_key)}")
        self.lbl_body.setText(tr(self._body_key))
        self.btn_close.setText(tr("common.close"))
