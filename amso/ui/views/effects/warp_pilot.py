"""Pilotage de la caméra de l'hyperespace dynamique : lignes droites et manœuvres.

Logique pure (zéro Qt). Chaque manœuvre tourne la caméra d'un angle total donné,
avec une vitesse angulaire en cloche (départ et arrêt en douceur), puis la caméra
repart tout droit vers le fond.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import StrEnum


class Maneuver(StrEnum):
    TURN = "turn"
    BARREL_ROLL = "barrel_roll"
    SPIRAL = "spiral"


@dataclass(slots=True)
class PilotStep:
    """Rotation à appliquer à la caméra pour un tick (radians) et roulis courant."""

    yaw: float
    pitch: float
    roll: float


class WarpPilot:
    CRUISE_RANGE_S = (4.0, 8.0)
    TURN_RANGE_S = (2.0, 3.0)
    ROLL_RANGE_S = (3.0, 4.0)
    TURN_ANGLE_RANGE = (0.4, 0.8)
    BANK_RATIO = 0.35
    # Tirage des manœuvres : virage fréquent, tonneau et spirale plus rares.
    KINDS = (Maneuver.TURN, Maneuver.BARREL_ROLL, Maneuver.SPIRAL)
    WEIGHTS = (0.65, 0.2, 0.15)

    def __init__(self) -> None:
        self.maneuver: Maneuver | None = None
        self._clock = 0.0
        self._duration = random.uniform(*self.CRUISE_RANGE_S)
        self._yaw_total = 0.0
        self._pitch_total = 0.0
        self._roll_total = 0.0
        self._bank_peak = 0.0
        self._roll_base = 0.0

    def start(self, maneuver: Maneuver) -> None:
        """Lance une manœuvre précise (utilisé par le tirage aléatoire et les tests)."""
        self.maneuver = maneuver
        self._clock = 0.0
        self._yaw_total = self._pitch_total = self._roll_total = self._bank_peak = 0.0
        sign = random.choice((-1.0, 1.0))
        if maneuver is Maneuver.BARREL_ROLL:
            self._duration = random.uniform(*self.ROLL_RANGE_S)
            self._roll_total = sign * 2.0 * math.pi
            return
        self._duration = random.uniform(*self.TURN_RANGE_S)
        heading = random.randrange(8) * math.pi / 4.0
        magnitude = random.uniform(*self.TURN_ANGLE_RANGE)
        self._yaw_total = math.cos(heading) * magnitude
        self._pitch_total = math.sin(heading) * magnitude * 0.7
        # Une caméra qui vire à droite penche à droite (rotation anti-horaire de l'image).
        self._bank_peak = -math.cos(heading) * magnitude * self.BANK_RATIO
        if maneuver is Maneuver.SPIRAL:
            self._roll_total = sign * math.pi

    def _pick_maneuver(self) -> Maneuver:
        return random.choices(self.KINDS, weights=self.WEIGHTS)[0]

    def _end_maneuver(self) -> None:
        self._roll_base = (self._roll_base + self._roll_total) % (2.0 * math.pi)
        self.maneuver = None
        self._clock = 0.0
        self._duration = random.uniform(*self.CRUISE_RANGE_S)

    def _current_roll(self, progress: float) -> float:
        smooth = progress * progress * (3.0 - 2.0 * progress)
        return self._roll_base + self._bank_peak * math.sin(math.pi * progress) + self._roll_total * smooth

    def advance(self, dt: float) -> PilotStep:
        """Avance de `dt` secondes ; renvoie les rotations de ce tick."""
        if self.maneuver is None:
            self._clock += dt
            if self._clock >= self._duration:
                self.start(self._pick_maneuver())
            return PilotStep(0.0, 0.0, self._roll_base)

        previous = min(1.0, self._clock / self._duration)
        self._clock += dt
        progress = min(1.0, self._clock / self._duration)
        # Intégrale exacte de la cloche sin(pi t) entre deux instants : l'angle total est atteint à la fin.
        share = (math.cos(math.pi * previous) - math.cos(math.pi * progress)) / 2.0
        step = PilotStep(self._yaw_total * share, self._pitch_total * share, self._current_roll(progress))
        if progress >= 1.0:
            self._end_maneuver()
        return step
