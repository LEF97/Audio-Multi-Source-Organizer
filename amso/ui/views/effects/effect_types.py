"""Types de données des effets visuels (couches, particules, comètes, étoiles)."""

from __future__ import annotations

import math
import random
from typing import TypedDict

from PySide6.QtGui import (
    QColor,
)


class WaveLayer(TypedDict):
    amp: float
    freq: float
    speed: float
    color: QColor
    alpha: float
    offset: float


class AuroraBlob(TypedDict):
    cx: float
    cy: float
    rad: float
    color: QColor
    alpha: float
    speed: float


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "radius", "color", "base_alpha", "phase")

    def __init__(self, w: float, h: float) -> None:
        self.reset(w, h, random_y=True)

    def reset(self, w: float, h: float, random_y: bool = False) -> None:
        self.x = random.uniform(0, max(100.0, w))
        self.y = random.uniform(0, max(100.0, h)) if random_y else h + random.uniform(5, 30)
        self.vx = random.uniform(-0.35, 0.35)
        self.vy = random.uniform(-0.6, -1.8)
        self.radius = random.uniform(1.8, 4.5)
        colors = [
            QColor(56, 189, 248),  # Cyan
            QColor(129, 140, 248),  # Indigo doux
            QColor(192, 132, 252),  # Violet
            QColor(45, 212, 191),  # Teal
            QColor(251, 191, 36),  # Ambre doré
        ]
        self.color = random.choice(colors)
        self.base_alpha = random.uniform(0.35, 0.85)
        self.phase = random.uniform(0, math.pi * 2)


class Comet:
    __slots__ = ("x", "y", "vx", "vy", "length", "color", "alpha")

    def __init__(self, w: float, h: float) -> None:
        self.reset(w, h, random_pos=True)

    def reset(self, w: float, h: float, random_pos: bool = False) -> None:
        self.x = random.uniform(0, max(100.0, w))
        self.y = random.uniform(-h, h) if random_pos else -random.uniform(10, 50)
        spd = random.uniform(2.5, 5.0)
        self.vx = spd * 0.35
        self.vy = spd
        self.length = random.uniform(25, 60)
        colors = [
            QColor(56, 189, 248),
            QColor(168, 85, 247),
            QColor(96, 165, 250),
        ]
        self.color = random.choice(colors)
        self.alpha = random.uniform(0.3, 0.75)


class WarpStar:
    """Étoile 3D pour l'effet d'hyperespace / voyage spatial en profondeur."""

    __slots__ = ("x", "y", "z", "pz", "speed", "color", "base_alpha", "radius")

    def __init__(self, w: float, h: float, max_depth: float = 1000.0, random_z: bool = True) -> None:
        self.reset(w, h, max_depth, random_z=random_z)

    def reset(self, w: float, h: float, max_depth: float = 1000.0, random_z: bool = False) -> None:
        spread_x = max(250.0, w) * 0.75
        spread_y = max(250.0, h) * 0.75
        self.x = random.uniform(-spread_x, spread_x)
        self.y = random.uniform(-spread_y, spread_y)
        if abs(self.x) < 20.0 and abs(self.y) < 20.0:
            self.x = 35.0 if self.x >= 0 else -35.0

        self.z = random.uniform(25.0, max_depth) if random_z else random.uniform(max_depth * 0.85, max_depth)
        self.pz = self.z
        self.speed = random.uniform(14.0, 24.0)
        self.radius = random.uniform(1.2, 3.2)
        self.base_alpha = random.uniform(0.65, 0.95)

        colors = [
            QColor(255, 255, 255),  # Blanc pur diamant
            QColor(56, 189, 248),  # Cyan électrique
            QColor(129, 140, 248),  # Indigo interstellaire
            QColor(192, 132, 252),  # Violet nébuleuse
            QColor(45, 212, 191),  # Turquoise cosmique
            QColor(254, 240, 138),  # Éclat jaune chaud
        ]
        self.color = random.choice(colors)
