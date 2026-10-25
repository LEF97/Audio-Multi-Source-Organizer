"""Widgets communs (bouton à badge, label cliquable, tiroir repliable)."""

from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent, QResizeEvent
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class HoverBadgeButton(QPushButton):
    """Bouton interactif de barre d'état émettant des signaux au survol pour les popovers."""

    hover_entered = Signal()
    hover_left = Signal()

    def enterEvent(self, event: Any) -> None:
        self.hover_entered.emit()
        super().enterEvent(event)

    def leaveEvent(self, event: Any) -> None:
        self.hover_left.emit()
        super().leaveEvent(event)


class ClickableLabel(QLabel):
    """QLabel cliquable émettant un signal clicked lors d'un clic gauche."""

    clicked = Signal()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class CollapsibleDrawer(QWidget):
    """Tiroir pliable/dépliable regroupant des boutons de navigation."""

    def __init__(
        self,
        title: str,
        parent: QWidget | None = None,
        initially_expanded: bool = True,
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._is_expanded = initially_expanded

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # En-tête cliquable avec chevron
        self.header_btn = QPushButton()
        self.header_btn.setProperty("class", "drawer-header")
        self.header_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header_btn.clicked.connect(self.toggle)
        layout.addWidget(self.header_btn)

        # Conteneur des éléments enfants du tiroir
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(2)
        layout.addWidget(self.content_widget)

        self._update_header()
        self.content_widget.setVisible(self._is_expanded)

    def title(self) -> str:
        return self._title

    def set_title(self, title: str) -> None:
        self._title = title
        self._update_header()

    def _update_header(self) -> None:
        arrow = "▼" if self._is_expanded else "▶"
        self.header_btn.setText(f"{arrow}  {self._title.upper()}")

    @property
    def is_expanded(self) -> bool:
        return self._is_expanded

    def toggle(self) -> None:
        self.set_expanded(not self._is_expanded)

    def set_expanded(self, expanded: bool) -> None:
        self._is_expanded = expanded
        self.content_widget.setVisible(self._is_expanded)
        self._update_header()

    def add_widget(self, widget: QWidget) -> None:
        self.content_layout.addWidget(widget)


class ClickableSlider(QSlider):
    """QSlider permettant de cliquer directement à n'importe quel endroit de la barre."""

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            val = self.minimum() + ((self.maximum() - self.minimum()) * event.position().x()) / max(1, self.width())
            self.setValue(int(round(val)))
            self.sliderMoved.emit(self.value())
        super().mousePressEvent(event)


class EffectContainer(QWidget):
    """Conteneur qui maintient le widget d'effet visuel redimensionné en arrière-plan."""

    def __init__(self, effect_canvas: QWidget | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.effect_canvas = effect_canvas
        if self.effect_canvas:
            self.effect_canvas.setParent(self)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if self.effect_canvas:
            self.effect_canvas.setGeometry(0, 0, self.width(), self.height())
            self.effect_canvas.lower()
