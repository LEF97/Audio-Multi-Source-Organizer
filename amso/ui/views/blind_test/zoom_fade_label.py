"""Label de compte à rebours animé (zoom + fondu) du Blind Test."""

from __future__ import annotations

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPropertyAnimation,
    Qt,
)
from PySide6.QtGui import QColor, QPainter, QResizeEvent
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QLabel,
    QWidget,
)


class ZoomFadeLabel(QLabel):
    """QLabel animé effectuant un zoom dynamique et un fondu à chaque changement de valeur."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scale: float = 1.0

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)

        # Animation d'opacité (fondu doux)
        self._anim_opacity = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._anim_opacity.setDuration(750)
        self._anim_opacity.setStartValue(1.0)
        self._anim_opacity.setEndValue(0.4)
        self._anim_opacity.setEasingCurve(QEasingCurve.Type.OutQuad)

        # Animation d'échelle (Zoom dynamique plus marqué de 2.2 vers 1.0)
        self._anim_scale = QPropertyAnimation(self, b"scale_factor", self)
        self._anim_scale.setDuration(750)
        self._anim_scale.setStartValue(2.2)
        self._anim_scale.setEndValue(1.0)
        self._anim_scale.setEasingCurve(QEasingCurve.Type.OutCubic)

    def get_scale_factor(self) -> float:
        return self._scale

    def set_scale_factor(self, s: float) -> None:
        self._scale = s
        self.update()

    scale_factor = Property(float, get_scale_factor, set_scale_factor)

    def trigger_tick_animation(self) -> None:
        """Déclenche l'animation de pulse (zoom dynamique) et fondu à chaque seconde."""
        self._anim_opacity.stop()
        self._anim_scale.stop()
        self._opacity_effect.setOpacity(1.0)
        self._scale = 2.2
        self._anim_opacity.start()
        self._anim_scale.start()

    def show_number(self, val: int) -> None:
        """Affiche le nombre et déclenche l'animation de zoom et fondu."""
        self.setText(str(val))
        self.trigger_tick_animation()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = float(self.width())
        h = float(self.height())
        painter.translate(w / 2.0, h / 2.0)
        painter.scale(self._scale, self._scale)
        painter.translate(-w / 2.0, -h / 2.0)

        painter.setFont(self.font())
        painter.setPen(QColor("#38BDF8"))
        painter.drawText(self.rect(), int(self.alignment()), self.text())
        painter.end()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if hasattr(self, "_opacity_effect") and self._opacity_effect:
            self._opacity_effect.updateBoundingRect()
            self._opacity_effect.update()
