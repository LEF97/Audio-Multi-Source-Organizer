"""Widget QLabel avec transitions animées et anti-clignotement pour les pochettes d'albums."""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPointF, QRectF, QVariantAnimation
from PySide6.QtGui import QPainter, QPaintEvent, QPixmap
from PySide6.QtWidgets import QLabel, QWidget


class CoverTransitionLabel(QLabel):
    """Affiche une pochette avec transition fluide uniquement lorsque l'image change réellement."""

    _ANIMATION_DURATION_MS = 600

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._current_pixmap: QPixmap | None = None
        self._previous_pixmap: QPixmap | None = None
        self._current_hash: int | None = None
        self._transition_mode: str = "fade"
        self._progress: float = 1.0
        self._animating: bool = False

        self._anim = QVariantAnimation(self)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setDuration(self._ANIMATION_DURATION_MS)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._anim.valueChanged.connect(self._on_anim_value_changed)
        self._anim.finished.connect(self._on_anim_finished)

    def _on_anim_value_changed(self, value: object) -> None:
        if isinstance(value, (int, float)):
            self._progress = float(value)
            self.update()

    def _on_anim_finished(self) -> None:
        self._animating = False
        self._previous_pixmap = None
        self._progress = 1.0
        self.update()

    def set_cover_pixmap(
        self,
        pixmap: QPixmap,
        *,
        cover_hash: int | None = None,
        transition: str = "fade",
        animate: bool = True,
    ) -> None:
        """Met à jour la pochette ; ignore si le hash est identique (hors redimensionnement)."""
        if (
            cover_hash is not None
            and self._current_hash is not None
            and cover_hash == self._current_hash
            and self._current_pixmap is not None
        ):
            if self._current_pixmap.size() != pixmap.size():
                self._current_pixmap = pixmap
                super().setPixmap(pixmap)
                self.update()
            return

        old_pix = self._current_pixmap
        self._current_pixmap = pixmap
        self._current_hash = cover_hash
        super().setPixmap(pixmap)

        if not animate or transition == "none" or old_pix is None or old_pix.isNull():
            self._anim.stop()
            self._animating = False
            self._previous_pixmap = None
            self._progress = 1.0
            self.update()
            return

        self._anim.stop()
        self._previous_pixmap = old_pix
        self._transition_mode = transition
        self._progress = 0.0
        self._animating = True
        self._anim.start()

    def _draw_centered_pixmap(self, painter: QPainter, pixmap: QPixmap, rect: QRectF) -> None:
        if pixmap.isNull():
            return
        pw = pixmap.width() / max(1.0, pixmap.devicePixelRatio())
        ph = pixmap.height() / max(1.0, pixmap.devicePixelRatio())
        x = rect.x() + (rect.width() - pw) / 2.0
        y = rect.y() + (rect.height() - ph) / 2.0
        painter.drawPixmap(QPointF(x, y), pixmap)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Dessine la transition animée entre l'ancienne et la nouvelle pochette."""
        if not self._animating or self._current_pixmap is None or self._previous_pixmap is None:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        rect = QRectF(self.rect())
        p = max(0.0, min(1.0, self._progress))
        mode = self._transition_mode

        if mode == "slide":
            offset_old = -rect.width() * p
            offset_new = rect.width() * (1.0 - p)
            painter.save()
            painter.setOpacity(1.0 - p * 0.4)
            painter.translate(offset_old, 0.0)
            self._draw_centered_pixmap(painter, self._previous_pixmap, rect)
            painter.restore()

            painter.save()
            painter.setOpacity(0.4 + 0.6 * p)
            painter.translate(offset_new, 0.0)
            self._draw_centered_pixmap(painter, self._current_pixmap, rect)
            painter.restore()
        elif mode == "zoom":
            painter.save()
            painter.setOpacity(1.0 - p)
            self._draw_centered_pixmap(painter, self._previous_pixmap, rect)
            painter.restore()

            scale = 0.86 + 0.14 * p
            painter.save()
            painter.setOpacity(p)
            center = rect.center()
            painter.translate(center)
            painter.scale(scale, scale)
            painter.translate(-center)
            self._draw_centered_pixmap(painter, self._current_pixmap, rect)
            painter.restore()
        elif mode == "flip":
            center = rect.center()
            if p < 0.5:
                sx = max(0.01, 1.0 - (p * 2.0))
                painter.save()
                painter.translate(center)
                painter.scale(sx, 1.0)
                painter.translate(-center)
                self._draw_centered_pixmap(painter, self._previous_pixmap, rect)
                painter.restore()
            else:
                sx = max(0.01, (p - 0.5) * 2.0)
                painter.save()
                painter.translate(center)
                painter.scale(sx, 1.0)
                painter.translate(-center)
                self._draw_centered_pixmap(painter, self._current_pixmap, rect)
                painter.restore()
        else:
            # Mode 'fade' (fondu enchaîné) par défaut
            painter.save()
            painter.setOpacity(1.0 - p)
            self._draw_centered_pixmap(painter, self._previous_pixmap, rect)
            painter.restore()

            painter.save()
            painter.setOpacity(p)
            self._draw_centered_pixmap(painter, self._current_pixmap, rect)
            painter.restore()

        painter.end()
