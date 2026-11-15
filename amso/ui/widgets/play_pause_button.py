"""Bouton Play/Pause rond : anneau réactif au spectre audio et transformation ▶ ↔ ⏸."""

from __future__ import annotations

import math
import time

from PySide6.QtCore import QEasingCurve, QEvent, QPoint, QPointF, QRectF, Qt, QTimer, QVariantAnimation
from PySide6.QtGui import (
    QColor,
    QEnterEvent,
    QHideEvent,
    QLinearGradient,
    QPainter,
    QPaintEvent,
    QPen,
    QPolygonF,
    QRadialGradient,
    QShowEvent,
)
from PySide6.QtWidgets import QPushButton, QWidget

from amso.ui.styles import COLOR_PLAY_ACCENT, COLOR_PRIMARY

_REFERENCE_DIAMETER = 50  # toutes les cotes de dessin sont exprimées pour ce diamètre puis mises à l'échelle
_HALO_MARGIN = 7  # marge autour du disque pour le halo
_FRAME_MS = 33
_BASS_BANDS = 5
_SPECTRUM_BANDS = 12
_ATTACK = 0.5
_RELEASE = 0.12
_IDLE_LEVEL = 0.01

# Chaque icône est un couple de quadrilatères (même ordre de points : haut-gauche, haut-droit,
# bas-droit, bas-gauche) pour pouvoir interpoler point à point entre play et pause.
_PLAY_QUADS = (
    ((-7.0, -10.0), (1.0, -5.0), (1.0, 5.0), (-7.0, 10.0)),
    ((1.0, -5.0), (9.0, 0.0), (9.0, 0.0), (1.0, 5.0)),
)
_PAUSE_QUADS = (
    ((-7.0, -10.0), (-2.0, -10.0), (-2.0, 10.0), (-7.0, 10.0)),
    ((2.0, -10.0), (7.0, -10.0), (7.0, 10.0), (2.0, 10.0)),
)
# Le centre de gravité d'un triangle est décalé : on recentre optiquement le play.
_PLAY_OPTICAL_SHIFT = 1.0


class PlayPauseButton(QPushButton):
    """Disque d'accent avec halo pulsant selon les basses et icône qui se transforme.

    Reste compatible avec le code existant : `setText("⏸")` / `setText("▶")` bascule l'état visuel.
    """

    def __init__(self, diameter: int = _REFERENCE_DIAMETER, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._k = diameter / _REFERENCE_DIAMETER
        self._radius = diameter / 2
        self._size = diameter + 2 * round(_HALO_MARGIN * self._k)
        self.setFixedSize(self._size, self._size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)

        self._idle_color = QColor(COLOR_PRIMARY)
        self._playing_color = QColor(COLOR_PLAY_ACCENT)
        self._playing = False
        self._hovered = False
        self._morph = 0.0  # 0 = play, 1 = pause
        self._level = 0.0
        self._phase_start = time.monotonic()

        self._morph_anim = QVariantAnimation(self)
        self._morph_anim.setDuration(260)
        self._morph_anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self._morph_anim.valueChanged.connect(self._on_morph_value)

        self._timer = QTimer(self)
        self._timer.setInterval(_FRAME_MS)
        self._timer.timeout.connect(self._tick)

    # --- API publique ---

    def setText(self, text: str) -> None:
        """Interprète ⏸ comme « lecture en cours » ; tout autre texte comme « à l'arrêt »."""
        self.set_playing("⏸" in text)

    def text(self) -> str:
        """Glyphe de l'état courant, pour les appelants qui lisent encore le texte du bouton."""
        return "⏸" if self._playing else "▶"

    def set_playing(self, playing: bool) -> None:
        if playing == self._playing:
            return
        self._playing = playing
        self._morph_anim.stop()
        self._morph_anim.setStartValue(self._morph)
        self._morph_anim.setEndValue(1.0 if playing else 0.0)
        self._morph_anim.start()
        self._update_timer_state()

    @property
    def _accent(self) -> QColor:
        """Bleu à l'arrêt, ambre en lecture ; fondu suivant la transformation de l'icône."""
        t = min(1.0, max(0.0, self._morph))  # OutBack dépasse 1 : on borne pour ne pas sortir du dégradé
        idle, active = self._idle_color, self._playing_color
        return QColor.fromRgbF(
            idle.redF() + (active.redF() - idle.redF()) * t,
            idle.greenF() + (active.greenF() - idle.greenF()) * t,
            idle.blueF() + (active.blueF() - idle.blueF()) * t,
        )

    # --- Animation ---

    def _on_morph_value(self, value: object) -> None:
        self._morph = float(value) if isinstance(value, int | float) else 0.0
        self.update()

    def _update_timer_state(self) -> None:
        needs_frames = self._playing or self._level > _IDLE_LEVEL
        if needs_frames and self.isVisible():
            if not self._timer.isActive():
                self._timer.start()
        elif self._timer.isActive():
            self._timer.stop()

    def _target_level(self) -> float:
        """Énergie des basses (spectre réel) ; repli sur une respiration lente sans capture audio."""
        if not self._playing:
            return 0.0
        from amso.services.audio_spectrum import get_audio_spectrum_service

        levels = get_audio_spectrum_service().get_spectrum(_SPECTRUM_BANDS)
        if levels is None:
            t = time.monotonic() - self._phase_start
            return 0.3 + 0.15 * math.sin(t * 3.0)
        bass = sum(levels[:_BASS_BANDS]) / _BASS_BANDS
        overall = sum(levels) / len(levels)
        return min(1.0, bass * 0.7 + overall * 0.5)

    def _tick(self) -> None:
        target = self._target_level()
        rate = _ATTACK if target > self._level else _RELEASE
        self._level += (target - self._level) * rate
        if not self._playing and self._level <= _IDLE_LEVEL:
            self._level = 0.0
            self._update_timer_state()
        self.update()

    # --- Interaction ---

    def hitButton(self, pos: QPoint) -> bool:
        """Zone cliquable limitée au disque (le halo ne déclenche pas de clic)."""
        centre = self._size / 2
        return math.hypot(pos.x() - centre, pos.y() - centre) <= self._radius

    def enterEvent(self, event: QEnterEvent) -> None:
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self._update_timer_state()

    def hideEvent(self, event: QHideEvent) -> None:
        super().hideEvent(event)
        self._timer.stop()

    # --- Rendu ---

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        centre = QPointF(self._size / 2, self._size / 2)
        radius = self._radius
        if self._level > _IDLE_LEVEL:
            self._paint_halo(painter, centre, radius)
        scale = 0.94 if self.isDown() else 1.0
        self._paint_disc(painter, centre, radius * scale)
        self._paint_icon(painter, centre, scale)

    def _paint_halo(self, painter: QPainter, centre: QPointF, radius: float) -> None:
        level = self._level
        k = self._k
        glow_radius = radius + (6.0 + level) * k
        gradient = QRadialGradient(centre, glow_radius)
        inner = QColor(self._accent)
        inner.setAlphaF(0.55 * level)
        outer = QColor(self._accent)
        outer.setAlpha(0)
        gradient.setColorAt(max(0.0, (radius - 2 * k) / glow_radius), inner)
        gradient.setColorAt(1.0, outer)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawEllipse(centre, glow_radius, glow_radius)

        ring = QColor(self._accent.lighter(130))
        ring.setAlphaF(0.35 + 0.5 * level)
        painter.setPen(QPen(ring, (1.5 + level * 1.5) * k))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        ring_radius = radius + (2.5 + level * 4.5) * k
        painter.drawEllipse(centre, ring_radius, ring_radius)

    def _paint_disc(self, painter: QPainter, centre: QPointF, radius: float) -> None:
        top = QColor(self._accent.lighter(125 if self._hovered else 112))
        bottom = QColor(self._accent.darker(125 if self.isDown() else 108))
        gradient = QLinearGradient(centre.x(), centre.y() - radius, centre.x(), centre.y() + radius)
        gradient.setColorAt(0.0, top)
        gradient.setColorAt(1.0, bottom)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawEllipse(QRectF(centre.x() - radius, centre.y() - radius, radius * 2, radius * 2))

    def _paint_icon(self, painter: QPainter, centre: QPointF, scale: float) -> None:
        m = self._morph
        shift = _PLAY_OPTICAL_SHIFT * (1.0 - m)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#FFFFFF"))
        for play_quad, pause_quad in zip(_PLAY_QUADS, _PAUSE_QUADS, strict=True):
            polygon = QPolygonF()
            for (px, py), (qx, qy) in zip(play_quad, pause_quad, strict=True):
                x = px + (qx - px) * m + shift
                y = py + (qy - py) * m
                polygon.append(QPointF(centre.x() + x * scale * self._k, centre.y() + y * scale * self._k))
            painter.drawPolygon(polygon)
