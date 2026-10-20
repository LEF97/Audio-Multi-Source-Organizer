"""Peinture des effets (particules, ondes, étoiles, aurore, warp)."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget

from amso.ui.views.effects.effect_types import AuroraBlob, WaveLayer

if TYPE_CHECKING:
    _MixinBase = QWidget
else:
    _MixinBase = object


class EffectPaintersMixin(_MixinBase):
    """Peinture des effets (particules, ondes, étoiles, aurore, warp)."""

    if TYPE_CHECKING:
        # Attributs de VisualEffectWidget résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    def _paint_particles(self, painter: QPainter, w: float, h: float) -> None:
        """Dessine les particules lumineuses flottantes."""
        painter.setPen(Qt.PenStyle.NoPen)
        for p in self._particles:
            pulse = 0.7 + 0.3 * math.sin(self._time * 3.0 + p.phase)
            alpha = max(0.05, min(1.0, p.base_alpha * pulse))

            # Halo externe doux
            glow_radius = p.radius * 2.5
            rad_grad = QRadialGradient(p.x, p.y, glow_radius)
            c_glow = QColor(p.color)
            c_glow.setAlphaF(alpha * 0.35)
            rad_grad.setColorAt(0.0, c_glow)
            c_transparent = QColor(p.color)
            c_transparent.setAlphaF(0.0)
            rad_grad.setColorAt(1.0, c_transparent)

            painter.setBrush(QBrush(rad_grad))
            painter.drawEllipse(QPointF(p.x, p.y), glow_radius, glow_radius)

            # Cœur brillant de la particule
            c_core = QColor(p.color)
            c_core.setAlphaF(alpha)
            painter.setBrush(QBrush(c_core))
            painter.drawEllipse(QPointF(p.x, p.y), p.radius, p.radius)

    def _paint_waves(self, painter: QPainter, w: float, h: float) -> None:
        """Dessine des courbes sinusoïdales d'ondes spectrales fluides."""
        baseline = h * 0.75
        wave_layers: list[WaveLayer] = [
            {"amp": 28.0, "freq": 0.007, "speed": 1.4, "color": QColor(2, 132, 199), "alpha": 0.22, "offset": 0.0},
            {"amp": 20.0, "freq": 0.011, "speed": -1.8, "color": QColor(168, 85, 247), "alpha": 0.18, "offset": 1.2},
            {"amp": 36.0, "freq": 0.005, "speed": 0.9, "color": QColor(56, 189, 248), "alpha": 0.26, "offset": 2.5},
        ]

        amp_factor = 1.0 if self._playback_state == "playing" else 0.4

        for layer in wave_layers:
            amp = layer["amp"] * amp_factor
            freq = layer["freq"]
            speed = layer["speed"]
            color = layer["color"]
            alpha = layer["alpha"]
            offset = layer["offset"]

            path = QPainterPath()
            path.moveTo(0, h)
            path.lineTo(0, baseline)

            step = 16
            x = 0
            while x <= w + step:
                # Harmonique composée
                y = baseline + amp * math.sin(x * freq + self._time * speed + offset)
                y += (amp * 0.35) * math.cos(x * freq * 1.8 - self._time * speed * 0.7)
                path.lineTo(x, y)
                x += step

            path.lineTo(w, h)
            path.closeSubpath()

            grad = QLinearGradient(0, baseline - amp, 0, h)
            c_top = QColor(color)
            c_top.setAlphaF(alpha)
            c_bottom = QColor(color)
            c_bottom.setAlphaF(0.02)
            grad.setColorAt(0.0, c_top)
            grad.setColorAt(1.0, c_bottom)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(grad))
            painter.drawPath(path)

            # Ligne de crête lumineuse
            pen_color = QColor(color)
            pen_color.setAlphaF(alpha * 1.6)
            pen = QPen(pen_color, 1.8)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            crest_path = QPainterPath()
            crest_path.moveTo(0, baseline + amp * math.sin(self._time * speed + offset))
            x = 0
            while x <= w + step:
                y = baseline + amp * math.sin(x * freq + self._time * speed + offset)
                y += (amp * 0.35) * math.cos(x * freq * 1.8 - self._time * speed * 0.7)
                crest_path.lineTo(x, y)
                x += step
            painter.drawPath(crest_path)

    def _paint_stars(self, painter: QPainter, w: float, h: float) -> None:
        """Dessine des traînées de comètes filantes."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        for c in self._comets:
            tail_x = c.x - c.length * 0.35
            tail_y = c.y - c.length

            grad = QLinearGradient(tail_x, tail_y, c.x, c.y)
            c_tail = QColor(c.color)
            c_tail.setAlphaF(0.0)
            c_head = QColor(c.color)
            c_head.setAlphaF(c.alpha)
            grad.setColorAt(0.0, c_tail)
            grad.setColorAt(1.0, c_head)

            pen = QPen(QBrush(grad), 1.8)
            painter.setPen(pen)
            painter.drawLine(QPointF(tail_x, tail_y), QPointF(c.x, c.y))

            # Point lumineux en tête
            c_dot = QColor(255, 255, 255)
            c_dot.setAlphaF(c.alpha)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(c_dot))
            painter.drawEllipse(QPointF(c.x, c.y), 1.5, 1.5)

    def _paint_aurora(self, painter: QPainter, w: float, h: float) -> None:
        """Dessine des nébuleuses aurores lumineuses oscillantes."""
        blobs: list[AuroraBlob] = [
            {"cx": 0.28, "cy": 0.35, "rad": 320.0, "color": QColor(56, 189, 248), "alpha": 0.16, "speed": 0.7},
            {"cx": 0.72, "cy": 0.42, "rad": 360.0, "color": QColor(168, 85, 247), "alpha": 0.14, "speed": -0.5},
            {"cx": 0.50, "cy": 0.65, "rad": 300.0, "color": QColor(45, 212, 191), "alpha": 0.12, "speed": 0.9},
        ]

        painter.setPen(Qt.PenStyle.NoPen)
        for b in blobs:
            s = b["speed"]
            cx = w * (b["cx"] + 0.12 * math.sin(self._time * s))
            cy = h * (b["cy"] + 0.10 * math.cos(self._time * s * 1.2))
            rad = b["rad"] * (0.85 + 0.15 * math.sin(self._time * s * 1.5))

            grad = QRadialGradient(cx, cy, rad)
            c_center = QColor(b["color"])
            c_center.setAlphaF(b["alpha"])
            c_outer = QColor(b["color"])
            c_outer.setAlphaF(0.0)
            grad.setColorAt(0.0, c_center)
            grad.setColorAt(1.0, c_outer)

            painter.setBrush(QBrush(grad))
            painter.drawEllipse(QPointF(cx, cy), rad, rad)

    def _paint_warp(self, painter: QPainter, w: float, h: float) -> None:
        """Dessine l'effet d'hyperespace / champ stellaire 3D (voyage spatial vers le fond de l'écran)."""
        cx = w * 0.5
        cy = h * 0.5
        fov = max(w, h) * 0.55
        max_depth = 1000.0

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        for s in self._warp_stars:
            if s.z <= 1.0 or s.pz <= 1.0:
                continue

            # Position courante projetée
            k = fov / s.z
            sx = cx + s.x * k
            sy = cy + s.y * k

            # Position précédente projetée (pour la traînée de vitesse)
            pk = fov / s.pz
            px = cx + s.x * pk
            py = cy + s.y * pk

            # Profondeur relative (0.0 au fond, 1.0 très proche de l'écran)
            depth_ratio = max(0.0, min(1.0, 1.0 - (s.z / max_depth)))
            alpha = max(0.1, min(1.0, s.base_alpha * (depth_ratio**1.2)))
            radius = s.radius * (0.6 + 1.8 * depth_ratio)

            # 1. Traînée lumineuse vers l'extérieur (Warp speed streak)
            dist_sq = (sx - px) ** 2 + (sy - py) ** 2
            if dist_sq > 0.5:
                grad = QLinearGradient(px, py, sx, sy)
                c_tail = QColor(s.color)
                c_tail.setAlphaF(0.0)
                c_head = QColor(s.color)
                c_head.setAlphaF(alpha * 0.85)
                grad.setColorAt(0.0, c_tail)
                grad.setColorAt(1.0, c_head)

                pen = QPen(QBrush(grad), max(1.0, radius * 0.75))
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                painter.setPen(pen)
                painter.drawLine(QPointF(px, py), QPointF(sx, sy))

            # 2. Halo lumineux doux pour les étoiles proches
            if radius > 2.0 and depth_ratio > 0.4:
                glow_rad = radius * 2.4
                rad_grad = QRadialGradient(sx, sy, glow_rad)
                c_glow = QColor(s.color)
                c_glow.setAlphaF(alpha * 0.28)
                rad_grad.setColorAt(0.0, c_glow)
                c_out = QColor(s.color)
                c_out.setAlphaF(0.0)
                rad_grad.setColorAt(1.0, c_out)

                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(rad_grad))
                painter.drawEllipse(QPointF(sx, sy), glow_rad, glow_rad)

            # 3. Cœur brillant de l'étoile
            painter.setPen(Qt.PenStyle.NoPen)
            c_star = QColor(255, 255, 255) if depth_ratio > 0.5 else QColor(s.color)
            c_star.setAlphaF(alpha)
            painter.setBrush(QBrush(c_star))
            painter.drawEllipse(QPointF(sx, sy), radius * 0.55, radius * 0.55)

    def _paint_warp_dynamic(self, painter: QPainter, w: float, h: float) -> None:
        """Dessine l'hyperespace dynamique avec virages aléatoires 3D et roulis."""
        cx = w * 0.5
        cy = h * 0.5
        fov = max(w, h) * 0.55
        max_depth = 1000.0

        # Point de fuite incurvé et rotation de roulis
        vanish_x = cx + self._warp_dyn_vx * 4.0
        vanish_y = cy + self._warp_dyn_vy * 4.0
        cos_r = math.cos(self._warp_dyn_roll)
        sin_r = math.sin(self._warp_dyn_roll)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        for s in self._warp_stars:
            if s.z <= 1.0 or s.pz <= 1.0:
                continue

            # Position courante projetée
            k = fov / s.z
            raw_sx = vanish_x + s.x * k
            raw_sy = vanish_y + s.y * k
            dx = raw_sx - cx
            dy = raw_sy - cy
            sx = cx + dx * cos_r - dy * sin_r
            sy = cy + dx * sin_r + dy * cos_r

            # Position précédente projetée pour la traînée incurvée
            pk = fov / s.pz
            drift_x = self._warp_dyn_vx * self._speed_multiplier * 0.8
            drift_y = self._warp_dyn_vy * self._speed_multiplier * 0.8
            raw_px = vanish_x + (s.x + drift_x) * pk
            raw_py = vanish_y + (s.y + drift_y) * pk
            pdx = raw_px - cx
            pdy = raw_py - cy
            px = cx + pdx * cos_r - pdy * sin_r
            py = cy + pdx * sin_r + pdy * cos_r

            # Profondeur relative
            depth_ratio = max(0.0, min(1.0, 1.0 - (s.z / max_depth)))
            alpha = max(0.1, min(1.0, s.base_alpha * (depth_ratio**1.2)))
            radius = s.radius * (0.6 + 1.8 * depth_ratio)

            # 1. Traînée lumineuse incurvée vers l'extérieur
            dist_sq = (sx - px) ** 2 + (sy - py) ** 2
            if dist_sq > 0.5:
                grad = QLinearGradient(px, py, sx, sy)
                c_tail = QColor(s.color)
                c_tail.setAlphaF(0.0)
                c_head = QColor(s.color)
                c_head.setAlphaF(alpha * 0.88)
                grad.setColorAt(0.0, c_tail)
                grad.setColorAt(1.0, c_head)

                pen = QPen(QBrush(grad), max(1.0, radius * 0.78))
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                painter.setPen(pen)
                painter.drawLine(QPointF(px, py), QPointF(sx, sy))

            # 2. Halo lumineux doux pour les étoiles proches
            if radius > 2.0 and depth_ratio > 0.4:
                glow_rad = radius * 2.4
                rad_grad = QRadialGradient(sx, sy, glow_rad)
                c_glow = QColor(s.color)
                c_glow.setAlphaF(alpha * 0.28)
                rad_grad.setColorAt(0.0, c_glow)
                c_out = QColor(s.color)
                c_out.setAlphaF(0.0)
                rad_grad.setColorAt(1.0, c_out)

                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(rad_grad))
                painter.drawEllipse(QPointF(sx, sy), glow_rad, glow_rad)

            # 3. Cœur brillant de l'étoile
            painter.setPen(Qt.PenStyle.NoPen)
            c_star = QColor(255, 255, 255) if depth_ratio > 0.5 else QColor(s.color)
            c_star.setAlphaF(alpha)
            painter.setBrush(QBrush(c_star))
            painter.drawEllipse(QPointF(sx, sy), radius * 0.55, radius * 0.55)
