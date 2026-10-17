"""Composant d'effets visuels et animations d'ambiance pour la page Lecteur d'AMSO.

Propose plusieurs ambiances lumineuses et fluides dessinées via QPainter :
- Particules & Poussières d'étoiles (dérive douce et scintillement)
- Ondes spectrales fluides (courbes néon ondulantes)
- Pluie de comètes (traînées lumineuses)
- Hyperespace & Voyage spatial 3D (plongée dans le fond, étoiles filant vers les côtés)
- Aurore boréale (pulsation de nébuleuses colorées)
- Désactivé (arrière-plan sobre)

Optimisé pour de hautes performances (30 FPS, pause automatique hors écran).
"""

from __future__ import annotations

import math
import random
from typing import TypedDict

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
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


class VisualEffectWidget(QWidget):
    """Widget de fond d'ambiance avec rendu d'effets visuels paramétrables."""

    EFFECT_NONE = "none"
    EFFECT_PARTICLES = "particles"
    EFFECT_WAVES = "waves"
    EFFECT_STARS = "stars"
    EFFECT_AURORA = "aurora"
    EFFECT_WARP = "warp"
    EFFECT_WARP_DYNAMIC = "warp_dynamic"
    EFFECT_BARS = "bars"
    EFFECT_BARS_FULL = "bars_full"

    ALL_EFFECTS = (
        EFFECT_NONE,
        EFFECT_PARTICLES,
        EFFECT_WAVES,
        EFFECT_STARS,
        EFFECT_AURORA,
        EFFECT_WARP,
        EFFECT_WARP_DYNAMIC,
        EFFECT_BARS,
        EFFECT_BARS_FULL,
    )

    def __init__(self, effect_type: str = EFFECT_PARTICLES, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setStyleSheet("background: transparent;")

        self._effect_type: str = effect_type if effect_type in self.ALL_EFFECTS else self.EFFECT_PARTICLES
        self._playback_state: str = "stopped"
        self._speed_multiplier: float = 0.5
        self._time: float = 0.0

        # Particules, comètes & étoiles hyperespace
        self._particles: list[Particle] = []
        self._comets: list[Comet] = []
        self._warp_stars: list[WarpStar] = []

        # Navigation pour l'hyperespace dynamique (changement de trajectoire 3D)
        self._warp_dyn_timer: float = 0.0
        self._warp_dyn_interval: float = 4.0
        self._warp_dyn_vx: float = 0.0
        self._warp_dyn_vy: float = 0.0
        self._warp_dyn_target_vx: float = 0.0
        self._warp_dyn_target_vy: float = 0.0
        self._warp_dyn_roll: float = 0.0
        self._warp_dyn_target_roll: float = 0.0

        # Barres de son rétro (Égaliseur de spectre audio)
        self._bars_align_left: bool = False
        self._bar_count: int = 32
        self._bar_levels: list[float] = [0.0] * 48
        self._bar_targets: list[float] = [0.0] * 48
        self._bar_peaks: list[float] = [0.0] * 48
        self._bar_peak_holds: list[int] = [0] * 48
        self._bar_peak_speeds: list[float] = [0.0] * 48
        self._audio_volume: float = 1.0
        self._audio_time_ms: int = 0
        self._track_seed: int = 0

        # Timer d'animation fluide (~30 FPS, économe en CPU)
        self._timer = QTimer(self)
        self._timer.setInterval(33)
        self._timer.timeout.connect(self._on_tick)
        self._demo_mode: bool = False

        self._init_particles(50)
        self._init_comets(25)
        self._init_warp_stars(75)

    def _init_particles(self, count: int) -> None:
        w = float(self.width() or 800)
        h = float(self.height() or 600)
        self._particles = [Particle(w, h) for _ in range(count)]

    def _init_comets(self, count: int) -> None:
        w = float(self.width() or 800)
        h = float(self.height() or 600)
        self._comets = [Comet(w, h) for _ in range(count)]

    def _init_warp_stars(self, count: int) -> None:
        w = float(self.width() or 800)
        h = float(self.height() or 600)
        self._warp_stars = [WarpStar(w, h, max_depth=1000.0, random_z=True) for _ in range(count)]

    def reinitialize_effect(self, w: float | None = None, h: float | None = None) -> None:
        """Réinitialise l'effet actif pour couvrir l'intégralité de la surface de l'écran."""
        width = w if w is not None and w > 0 else float(self.width() or 800)
        height = h if h is not None and h > 0 else float(self.height() or 600)
        if width <= 50 or height <= 50:
            return

        p_count = int(max(45, min(95, (width * height) / 18000)))
        c_count = int(max(20, min(50, (width * height) / 36000)))
        w_count = int(max(55, min(130, (width * height) / 13000)))

        self._particles = [Particle(width, height) for _ in range(p_count)]
        self._comets = [Comet(width, height) for _ in range(c_count)]
        self._warp_stars = [WarpStar(width, height, max_depth=1000.0, random_z=True) for _ in range(w_count)]

        if self._effect_type in (self.EFFECT_BARS, self.EFFECT_BARS_FULL):
            if self._effect_type == self.EFFECT_BARS_FULL:
                self._bar_count = max(32, min(64, int(width / 18.0)))
            else:
                self._bar_count = max(24, min(48, int(width / 24.0)))
            self._bar_levels = [0.0] * self._bar_count
            self._bar_targets = [0.0] * self._bar_count
            self._bar_peaks = [0.0] * self._bar_count
            self._bar_peak_holds = [0] * self._bar_count
            self._bar_peak_speeds = [0.0] * self._bar_count

        self.update()

    # -------------------------------------------------------------------------
    # Configuration et Contrôle
    # -------------------------------------------------------------------------

    @property
    def effect_type(self) -> str:
        return self._effect_type

    def set_effect_type(self, effect: str) -> None:
        """Définit le type d'effet actif ('none', 'particles', 'waves', 'stars', 'warp', 'warp_dynamic', 'aurora', 'bars', 'bars_full')."""
        if effect not in self.ALL_EFFECTS:
            effect = self.EFFECT_NONE

        if self._effect_type != effect:
            self._effect_type = effect
            self.reinitialize_effect()
            self._update_timer_state()
            self._update_spectrum_service_state()
            self.update()

    def _update_spectrum_service_state(self) -> None:
        """Démarre ou arrête la capture audio selon l'effet actif et la visibilité."""
        try:
            from amso.services.audio_spectrum import get_audio_spectrum_service

            svc = get_audio_spectrum_service()
            if self._effect_type in (self.EFFECT_BARS, self.EFFECT_BARS_FULL) and self.isVisible():
                svc.start()
            else:
                svc.stop()
        except Exception:
            pass

    def set_playback_state(self, state: str) -> None:
        """Adapte la réactivité et la vitesse de l'animation à l'état de lecture."""
        self._playback_state = state
        if state == "playing":
            self._speed_multiplier = 1.0
        else:
            self._speed_multiplier = 0.4
        self.update()

    def set_bars_aligned_left(self, align_left: bool = True) -> None:
        """Définit si les barres démarrent à gauche et s'étendent jusqu'au bord droit."""
        self._bars_align_left = align_left
        self.update()

    def update_audio_time(self, current_ms: int, ratio: float) -> None:
        """Transmet la position temporelle de la musique pour synchroniser le rythme."""
        self._audio_time_ms = current_ms

    def update_audio_volume(self, volume: int, is_muted: bool) -> None:
        """Adapte l'amplitude du visualiseur au volume réel configuré."""
        if is_muted or volume <= 0:
            self._audio_volume = 0.0
        else:
            self._audio_volume = max(0.15, min(1.0, volume / 100.0))

    def set_track(self, track: object | None) -> None:
        """Injecte une empreinte de la piste pour moduler harmoniquement les fréquences."""
        title = getattr(track, "title", "") if track else ""
        if title:
            self._track_seed = sum(ord(c) for c in str(title))
        else:
            self._track_seed = 0

    def set_demo_mode(self, enabled: bool) -> None:
        """Active ou désactive le mode démo (animation continue et autonome, sans dépendre du lecteur audio)."""
        self._demo_mode = enabled
        if enabled:
            self._playback_state = "playing"
            self._audio_volume = 0.85
            self._speed_multiplier = 1.0
            self._update_timer_state()
        self.update()

    def _update_timer_state(self) -> None:
        if self._effect_type == self.EFFECT_NONE:
            if self._timer.isActive():
                self._timer.stop()
        elif getattr(self, "_demo_mode", False) or self.isVisible():
            if not self._timer.isActive():
                self._timer.start()
        else:
            if self._timer.isActive():
                self._timer.stop()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._update_timer_state()
        self._update_spectrum_service_state()
        if self.width() > 50 and self.height() > 50:
            self.reinitialize_effect()

    def hideEvent(self, event) -> None:
        super().hideEvent(event)
        if self._timer.isActive():
            self._timer.stop()
        self._update_spectrum_service_state()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        new_size = event.size()
        old_size = event.oldSize()
        if new_size.width() <= 50 or new_size.height() <= 50:
            return

        w_new = float(new_size.width())
        h_new = float(new_size.height())

        # Si premier affichage ou taille précédente non initialisée
        if old_size.width() <= 0 or old_size.height() <= 0:
            self.reinitialize_effect(w_new, h_new)
            return

        w_old = float(old_size.width())
        h_old = float(old_size.height())

        # Si changement de taille important (ex: maximisation / plein écran / redimensionnement fort),
        # réinitialiser immédiatement pour répartir les éléments sur 100% de la surface
        ratio_w = w_new / w_old
        ratio_h = h_new / h_old
        if ratio_w > 1.15 or ratio_w < 0.85 or ratio_h > 1.15 or ratio_h < 0.85:
            self.reinitialize_effect(w_new, h_new)
            return

        # Redimensionnement progressif au curseur :
        # Mise à l'échelle instantanée des positions actuelles sur le nouvel espace
        rx = w_new / max(1.0, w_old)
        ry = h_new / max(1.0, h_old)

        target_p_count = int(max(45, min(95, (w_new * h_new) / 18000)))
        target_c_count = int(max(20, min(50, (w_new * h_new) / 36000)))
        target_w_count = int(max(55, min(130, (w_new * h_new) / 13000)))

        for p in self._particles:
            p.x = max(0.0, min(w_new, p.x * rx))
            p.y = max(0.0, min(h_new, p.y * ry))

        while len(self._particles) < target_p_count:
            self._particles.append(Particle(w_new, h_new))
        while len(self._particles) > target_p_count:
            self._particles.pop()

        for c in self._comets:
            c.x = max(0.0, min(w_new, c.x * rx))
            c.y = max(-h_new, min(h_new, c.y * ry))

        while len(self._comets) < target_c_count:
            self._comets.append(Comet(w_new, h_new))
        while len(self._comets) > target_c_count:
            self._comets.pop()

        for s in self._warp_stars:
            s.x = s.x * rx
            s.y = s.y * ry

        while len(self._warp_stars) < target_w_count:
            self._warp_stars.append(WarpStar(w_new, h_new, max_depth=1000.0, random_z=True))
        while len(self._warp_stars) > target_w_count:
            self._warp_stars.pop()

        self.update()

    # -------------------------------------------------------------------------
    # Boucle d'animation
    # -------------------------------------------------------------------------

    def _on_tick(self) -> None:
        if self._effect_type == self.EFFECT_NONE:
            return

        dt = 0.033 * self._speed_multiplier
        self._time += dt
        w = float(self.width())
        h = float(self.height())

        if self._effect_type == self.EFFECT_PARTICLES:
            for p in self._particles:
                p.y += p.vy * self._speed_multiplier
                p.x += (p.vx + 0.3 * math.sin(self._time * 2.0 + p.phase)) * self._speed_multiplier
                if p.y < -20 or p.x < -20 or p.x > w + 20:
                    p.reset(w, h, random_y=False)

        elif self._effect_type == self.EFFECT_STARS:
            for c in self._comets:
                c.x += c.vx * self._speed_multiplier
                c.y += c.vy * self._speed_multiplier
                if c.y > h + 50 or c.x > w + 50:
                    c.reset(w, h, random_pos=False)

        elif self._effect_type == self.EFFECT_WARP:
            max_depth = 1000.0
            cx = w * 0.5
            cy = h * 0.5
            fov = max(w, h) * 0.55

            for s in self._warp_stars:
                s.pz = s.z
                s.z -= s.speed * self._speed_multiplier

                if s.z <= 12.0:
                    s.reset(w, h, max_depth=max_depth, random_z=False)
                    continue

                # Calcul rapide de projection écran
                k = fov / s.z
                sx = cx + s.x * k
                sy = cy + s.y * k

                # Si l'étoile est sortie de l'écran avec une marge
                if sx < -80 or sx > w + 80 or sy < -80 or sy > h + 80:
                    s.reset(w, h, max_depth=max_depth, random_z=False)

        elif self._effect_type == self.EFFECT_WARP_DYNAMIC:
            max_depth = 1000.0
            cx = w * 0.5
            cy = h * 0.5
            fov = max(w, h) * 0.55

            # Gestion aléatoire des changements de trajectoire (virages toutes les 3.5 à 7 secondes)
            self._warp_dyn_timer += dt
            if self._warp_dyn_timer >= self._warp_dyn_interval:
                self._warp_dyn_timer = 0.0
                self._warp_dyn_interval = random.uniform(3.5, 7.0)
                if random.random() < 0.22:
                    # Rétablissement d'une trajectoire droite
                    self._warp_dyn_target_vx = 0.0
                    self._warp_dyn_target_vy = 0.0
                    self._warp_dyn_target_roll = 0.0
                else:
                    # Choix d'un nouvel angle de virage dans l'espace 3D
                    ang = random.uniform(0.0, math.pi * 2.0)
                    speed_drift = random.uniform(22.0, 48.0)
                    self._warp_dyn_target_vx = math.cos(ang) * speed_drift
                    self._warp_dyn_target_vy = math.sin(ang) * speed_drift * 0.65
                    self._warp_dyn_target_roll = -math.cos(ang) * 0.32

            # Interpolation progressive (inertie et amorti de pilotage réaliste)
            self._warp_dyn_vx += (self._warp_dyn_target_vx - self._warp_dyn_vx) * 0.045
            self._warp_dyn_vy += (self._warp_dyn_target_vy - self._warp_dyn_vy) * 0.045
            self._warp_dyn_roll += (self._warp_dyn_target_roll - self._warp_dyn_roll) * 0.04

            # Le point de fuite de la caméra se décale dynamiquement dans le sens du virage
            vanish_x = cx + self._warp_dyn_vx * 4.0
            vanish_y = cy + self._warp_dyn_vy * 4.0

            for s in self._warp_stars:
                s.pz = s.z
                s.z -= s.speed * self._speed_multiplier

                # Dérive latérale en fonction du virage du vaisseau
                s.x -= self._warp_dyn_vx * self._speed_multiplier * 0.8
                s.y -= self._warp_dyn_vy * self._speed_multiplier * 0.8

                if s.z <= 12.0:
                    s.reset(w, h, max_depth=max_depth, random_z=False)
                    s.x += self._warp_dyn_vx * random.uniform(8.0, 20.0)
                    s.y += self._warp_dyn_vy * random.uniform(8.0, 20.0)
                    continue

                # Calcul rapide de projection écran
                k = fov / s.z
                sx = vanish_x + s.x * k
                sy = vanish_y + s.y * k

                # Si l'étoile est sortie de l'écran avec une marge
                if sx < -140 or sx > w + 140 or sy < -140 or sy > h + 140:
                    s.reset(w, h, max_depth=max_depth, random_z=False)
                    s.x += self._warp_dyn_vx * random.uniform(8.0, 20.0)
                    s.y += self._warp_dyn_vy * random.uniform(8.0, 20.0)

        elif self._effect_type in (self.EFFECT_BARS, self.EFFECT_BARS_FULL):
            self._update_bars_tick(dt, w, h)

        self.update()

    # -------------------------------------------------------------------------
    # Rendu graphique (QPainter)
    # -------------------------------------------------------------------------

    def paintEvent(self, event) -> None:
        if self._effect_type == self.EFFECT_NONE:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = float(self.width())
        h = float(self.height())
        if w <= 0 or h <= 0:
            return

        if self._effect_type == self.EFFECT_PARTICLES:
            self._paint_particles(painter, w, h)
        elif self._effect_type == self.EFFECT_WAVES:
            self._paint_waves(painter, w, h)
        elif self._effect_type == self.EFFECT_STARS:
            self._paint_stars(painter, w, h)
        elif self._effect_type == self.EFFECT_WARP:
            self._paint_warp(painter, w, h)
        elif self._effect_type == self.EFFECT_WARP_DYNAMIC:
            self._paint_warp_dynamic(painter, w, h)
        elif self._effect_type == self.EFFECT_AURORA:
            self._paint_aurora(painter, w, h)
        elif self._effect_type == self.EFFECT_BARS:
            self._paint_bars(painter, w, h)
        elif self._effect_type == self.EFFECT_BARS_FULL:
            self._paint_bars_full(painter, w, h)

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

    def _update_bars_tick(self, dt: float, w: float, h: float) -> None:
        """Anime les barres de spectre rétro et la dynamique des pics de crête."""
        if self._bars_align_left:
            target_count = max(20, min(56, int(w / 18.0))) if w > 50 else 24
        elif self._effect_type == self.EFFECT_BARS_FULL:
            target_count = max(32, min(64, int(w / 18.0))) if w > 100 else 40
        else:
            target_count = max(24, min(48, int(w / 24.0))) if w > 100 else 32
        if len(self._bar_levels) != target_count:
            self._bar_count = target_count
            self._bar_levels = [0.0] * target_count
            self._bar_targets = [0.0] * target_count
            self._bar_peaks = [0.0] * target_count
            self._bar_peak_holds = [0] * target_count
            self._bar_peak_speeds = [0.0] * target_count

        n = len(self._bar_levels)
        is_demo = getattr(self, "_demo_mode", False)
        is_playing = self._playback_state == "playing" or is_demo

        # 1. Tentative d'obtention du spectre audio réel en direct (WASAPI Loopback)
        real_levels = None
        if is_playing and self._audio_volume > 0.0 and not is_demo:
            try:
                from amso.services.audio_spectrum import get_audio_spectrum_service

                real_levels = get_audio_spectrum_service().get_spectrum(n)
            except Exception:
                real_levels = None

        if real_levels is not None:
            # Mode réel actif : les barres réagissent à 100% au son physique joué
            for i in range(n):
                self._bar_targets[i] = real_levels[i] * self._audio_volume
        else:
            # Mode repli procédural si capture système indisponible ou mode démo
            t = self._time
            t_sec = t if is_demo else ((self._audio_time_ms / 1000.0) if self._audio_time_ms > 0 else t)
            tempo = 2.4
            kick = max(0.0, math.sin(t_sec * tempo * math.pi * 2.0)) ** 4
            snare = max(0.0, math.sin((t_sec * tempo + 0.5) * math.pi * 2.0)) ** 6
            hihat = max(0.0, math.sin((t_sec * tempo * 2.0) * math.pi * 2.0)) ** 8
            macro = 0.72 + 0.28 * math.sin(t_sec * 0.35 + (self._track_seed % 100) * 0.1)
            vol = 0.85 if is_demo else self._audio_volume

            for i in range(n):
                if not is_playing or vol <= 0.0:
                    self._bar_targets[i] = 0.0
                else:
                    rel = i / max(1, n - 1)  # 0.0 = Bass, 1.0 = Treble
                    if rel < 0.28:
                        b_rel = rel / 0.28
                        wave = math.sin(t * 4.5 + i * 0.4) ** 2
                        amp = (kick * 0.72 + wave * 0.28) * (1.15 - b_rel * 0.4)
                        amp += 0.12 * math.sin(t * 8.0 + i)
                    elif rel < 0.70:
                        m_rel = (rel - 0.28) / 0.42
                        vocal = math.sin(t * 3.8 + i * 0.7 + self._track_seed * 0.05) ** 2
                        amp = snare * (0.52 - m_rel * 0.1) + vocal * 0.38 + 0.14 * math.sin(t * 9.5 + i)
                    else:
                        shimmer = (math.sin(t * 16.0 + i * 1.8) ** 4) * (0.6 + 0.4 * math.sin(t * 3.0))
                        amp = hihat * 0.58 + shimmer * 0.32 + 0.12 * math.sin(t * 24.0 + i * 2.0)

                    target = max(0.0, min(1.0, amp * macro * vol))
                    self._bar_targets[i] = target

        # Interpolation des niveaux : attaque très vive (0.65), relâchement analogique (0.20)
        for i in range(n):
            cur = self._bar_levels[i]
            tar = self._bar_targets[i]
            if tar > cur:
                self._bar_levels[i] = cur + (tar - cur) * 0.65
            else:
                self._bar_levels[i] = max(0.0, cur - (cur - tar) * 0.20)

            # Physique des crêtes (Peak hold & descente gravitationnelle)
            lvl = self._bar_levels[i]
            if lvl >= self._bar_peaks[i]:
                self._bar_peaks[i] = lvl
                self._bar_peak_holds[i] = 10
                self._bar_peak_speeds[i] = 0.0
            else:
                if self._bar_peak_holds[i] > 0:
                    self._bar_peak_holds[i] -= 1
                else:
                    self._bar_peak_speeds[i] += 0.0042
                    self._bar_peaks[i] = max(lvl, self._bar_peaks[i] - self._bar_peak_speeds[i])

    def _paint_bars(self, painter: QPainter, w: float, h: float) -> None:
        """Dessine un égaliseur de spectre rétro à barres LED segmentées avec maintien de crête."""
        n = len(self._bar_levels)
        if n == 0 or w <= 50 or h <= 50:
            return

        is_demo = getattr(self, "_demo_mode", False)
        if is_demo:
            painter.setOpacity(0.35)

        baseline_y = h - 12.0
        if self._bars_align_left:
            available_h = max(24.0, baseline_y - 2.0)
            max_bar_h = min(available_h, max(28.0, h * 0.72))
            seg_h = max(2.2, min(3.0, max_bar_h / 13.0))
            seg_gap = 1.0
            step_h = seg_h + seg_gap
            total_segs = max(8, int(max_bar_h / step_h))

            spacing = max(2.5, min(4.5, w / 200.0))
            total_spacing = (n - 1) * spacing
            total_span = max(10.0, w - 2.0)
            bar_w = max(4.0, (total_span - total_spacing) / n)
            actual_total_w = total_span
            start_x = 0.0
        else:
            max_bar_h = min(170.0, max(55.0, h * 0.42))
            seg_h = 3.2
            seg_gap = 1.2
            step_h = seg_h + seg_gap
            total_segs = max(10, int(max_bar_h / step_h))

            spacing = max(2.5, min(5.0, w / 260.0))
            total_spacing = (n - 1) * spacing
            total_span = min(w * 0.92, n * 24.0)
            bar_w = max(6.0, min(16.0, (total_span - total_spacing) / n))
            actual_total_w = n * bar_w + total_spacing
            start_x = (w - actual_total_w) / 2.0

        painter.setPen(Qt.PenStyle.NoPen)

        # 1. Dessin des barres segmentées (Matrice LED active + fond sombre inactif)
        for i in range(n):
            bx = start_x + i * (bar_w + spacing)
            lvl = max(0.0, min(1.0, self._bar_levels[i]))
            lit_segs = int(round(lvl * total_segs))
            peak_lvl = max(0.0, min(1.0, self._bar_peaks[i]))
            peak_seg = int(round(peak_lvl * total_segs))

            for s in range(total_segs):
                sy = baseline_y - (s + 1) * step_h
                ratio = s / float(total_segs)

                # Couleurs étagées style matériel Hi-Fi vintage :
                # - Vert fluo / Lime pour les niveaux usuels (0-60%)
                # - Ambre doré / Jaune pour les niveaux médians (60-82%)
                # - Rouge corail éclatant pour les crêtes (82-100%)
                if ratio < 0.60:
                    lit_color = QColor(34, 197, 94)  # #22C55E
                    dim_color = QColor(20, 50, 30, 40)
                elif ratio < 0.82:
                    lit_color = QColor(234, 179, 8)  # #EAB308
                    dim_color = QColor(50, 40, 12, 40)
                else:
                    lit_color = QColor(239, 68, 68)  # #EF4444
                    dim_color = QColor(55, 18, 18, 40)

                seg_rect = QRectF(bx, sy, bar_w, seg_h)
                if s < lit_segs:
                    painter.setBrush(QBrush(lit_color))
                    painter.drawRoundedRect(seg_rect, 1.0, 1.0)
                else:
                    painter.setBrush(QBrush(dim_color))
                    painter.drawRoundedRect(seg_rect, 1.0, 1.0)

            # Capuchon flottant de maintien de crête (Peak Cap)
            if peak_seg > 0 and peak_seg < total_segs:
                py = baseline_y - (peak_seg + 1) * step_h
                p_ratio = peak_seg / float(total_segs)
                if p_ratio < 0.60:
                    peak_color = QColor(134, 239, 172)
                elif p_ratio < 0.82:
                    peak_color = QColor(254, 240, 138)
                else:
                    peak_color = QColor(254, 202, 202)
                painter.setBrush(QBrush(peak_color))
                painter.drawRoundedRect(QRectF(bx, py, bar_w, seg_h), 1.0, 1.0)

            # 2. Reflet miroir en dessous du socle (verre acrylique fumé)
            if not self._bars_align_left:
                ref_segs = min(4, lit_segs)
                for r in range(ref_segs):
                    ry = baseline_y + (r + 1) * step_h - 2.0
                    alpha = 0.16 * (1.0 - r / 4.0)
                    ref_c = QColor(34, 197, 94) if r < 2 else QColor(56, 189, 248)
                    ref_c.setAlphaF(alpha)
                    painter.setBrush(QBrush(ref_c))
                    painter.drawRoundedRect(QRectF(bx, ry, bar_w, seg_h), 1.0, 1.0)

        # 3. Ligne de socle lumineuse et repères rétro
        line_y = baseline_y + 1.0
        x_left = start_x if self._bars_align_left else (start_x - 15.0)
        x_right = (start_x + actual_total_w) if self._bars_align_left else (start_x + actual_total_w + 15.0)
        grad = QLinearGradient(x_left, line_y, x_right, line_y)
        grad.setColorAt(0.0, QColor(56, 189, 248, 60 if self._bars_align_left else 0))
        grad.setColorAt(0.15, QColor(56, 189, 248, 120))
        grad.setColorAt(0.5, QColor(56, 189, 248, 140))
        grad.setColorAt(0.85, QColor(56, 189, 248, 120))
        grad.setColorAt(1.0, QColor(56, 189, 248, 60 if self._bars_align_left else 0))

        painter.setPen(QPen(QBrush(grad), 1.2))
        painter.drawLine(QPointF(x_left, line_y), QPointF(x_right, line_y))

        # Repères typographiques subtils (BASS / MID / TREBLE)
        painter.setPen(QColor(148, 163, 184, 120))
        font = painter.font()
        font.setPointSize(7 if self._bars_align_left else 8)
        font.setBold(True)
        painter.setFont(font)

        lbl_y = min(h - 2.0, baseline_y + 10.0)
        # Bass à 12%
        x_bass = start_x + (actual_total_w * 0.08 if self._bars_align_left else (actual_total_w * 0.12 - 12.0))
        painter.drawText(QPointF(x_bass, lbl_y), "BASS")
        # Mid à 50%
        x_mid = start_x + actual_total_w * 0.50 - 10.0
        painter.drawText(QPointF(x_mid, lbl_y), "MID")
        # Treble à 88%
        x_treb = start_x + (actual_total_w * 0.90 if self._bars_align_left else (actual_total_w * 0.88 - 18.0))
        painter.drawText(QPointF(x_treb, lbl_y), "TREBLE")

    def _paint_bars_full(self, painter: QPainter, w: float, h: float) -> None:
        """Dessine un égaliseur de spectre rétro géant couvrant toute la surface de l'écran avec matrice LED et repères studio."""
        n = len(self._bar_levels)
        if n == 0 or w <= 50 or h <= 50:
            return

        baseline_y = h - 26.0
        top_y = 20.0
        max_bar_h = max(80.0, baseline_y - top_y)

        # Hauteur des segments et espacement vertical
        step_h = max(4.6, min(7.5, max_bar_h / 52.0))
        seg_gap = 1.4
        seg_h = step_h - seg_gap
        total_segs = max(16, int(max_bar_h / step_h))

        # Disposition horizontale sur l'ensemble de la largeur disponible
        side_margin = max(16.0, min(36.0, w * 0.03))
        total_span = w - 2.0 * side_margin
        spacing = max(2.5, min(5.0, total_span / (n * 5.0)))
        bar_w = (total_span - (n - 1) * spacing) / n
        start_x = side_margin

        # 1. Grille d'alignement dB subtile façon rack de mastering vintage
        db_levels = [
            (0.88, "0 dB", QColor(239, 68, 68, 85)),  # Seuil rouge critique
            (0.72, "-6 dB", QColor(245, 158, 11, 45)),  # Seuil ambre
            (0.52, "-12 dB", QColor(6, 182, 212, 35)),  # Seuil cyan
            (0.24, "-24 dB", QColor(16, 185, 129, 25)),  # Seuil vert
        ]

        font_orig = painter.font()
        font_db = painter.font()
        font_db.setPointSize(7)
        font_db.setBold(True)
        painter.setFont(font_db)

        for ratio_lvl, db_txt, db_color in db_levels:
            ref_y = baseline_y - ratio_lvl * (total_segs * step_h)
            pen_db = QPen(db_color, 1.0, Qt.PenStyle.DotLine)
            painter.setPen(pen_db)
            painter.drawLine(QPointF(start_x, ref_y), QPointF(start_x + total_span, ref_y))
            # Repères texte sur les côtés
            painter.setPen(db_color)
            painter.drawText(QPointF(max(2.0, start_x - 30.0), ref_y + 3.0), db_txt)

        painter.setPen(Qt.PenStyle.NoPen)

        # 2. Dessin de chaque barre LED segmentée
        for i in range(n):
            bx = start_x + i * (bar_w + spacing)
            lvl = max(0.0, min(1.0, self._bar_levels[i]))
            lit_segs = int(round(lvl * total_segs))
            peak_lvl = max(0.0, min(1.0, self._bar_peaks[i]))
            peak_seg = int(round(peak_lvl * total_segs))

            for s in range(total_segs):
                sy = baseline_y - (s + 1) * step_h
                ratio = s / float(total_segs)

                # Échelonnage colorimétrique studio 4 zones :
                # - Vert émeraude électrique (0 - 52%)
                # - Cyan / Turquoise dynamique (52 - 72%)
                # - Ambre doré chaud (72 - 88%)
                # - Rouge corail éclatant (88 - 100%)
                if ratio < 0.52:
                    lit_color = QColor(16, 185, 129)  # #10B981
                    dim_color = QColor(16, 185, 129, 28)
                elif ratio < 0.72:
                    lit_color = QColor(6, 182, 212)  # #06B6D4
                    dim_color = QColor(6, 182, 212, 28)
                elif ratio < 0.88:
                    lit_color = QColor(245, 158, 11)  # #F59E0B
                    dim_color = QColor(245, 158, 11, 30)
                else:
                    lit_color = QColor(239, 68, 68)  # #EF4444
                    dim_color = QColor(239, 68, 68, 35)

                seg_rect = QRectF(bx, sy, bar_w, seg_h)
                if s < lit_segs:
                    painter.setBrush(QBrush(lit_color))
                    painter.drawRoundedRect(seg_rect, 1.2, 1.2)
                else:
                    painter.setBrush(QBrush(dim_color))
                    painter.drawRoundedRect(seg_rect, 1.2, 1.2)

            # Capuchon de maintien de pic flottant
            if peak_seg > 0 and peak_seg < total_segs:
                py = baseline_y - (peak_seg + 1) * step_h
                p_ratio = peak_seg / float(total_segs)
                if p_ratio < 0.52:
                    peak_color = QColor(167, 243, 208)
                elif p_ratio < 0.72:
                    peak_color = QColor(165, 243, 252)
                elif p_ratio < 0.88:
                    peak_color = QColor(254, 240, 138)
                else:
                    peak_color = QColor(254, 202, 202)

                painter.setBrush(QBrush(peak_color))
                painter.drawRoundedRect(QRectF(bx - 0.5, py, bar_w + 1.0, seg_h), 1.2, 1.2)

        # 3. Ligne de socle lumineuse et repères de fréquences ISO
        line_y = baseline_y + 1.0
        grad = QLinearGradient(start_x, line_y, start_x + total_span, line_y)
        grad.setColorAt(0.0, QColor(56, 189, 248, 20))
        grad.setColorAt(0.15, QColor(56, 189, 248, 90))
        grad.setColorAt(0.5, QColor(56, 189, 248, 160))
        grad.setColorAt(0.85, QColor(56, 189, 248, 90))
        grad.setColorAt(1.0, QColor(56, 189, 248, 20))

        painter.setPen(QPen(QBrush(grad), 1.4))
        painter.drawLine(QPointF(start_x, line_y), QPointF(start_x + total_span, line_y))

        # Repères de fréquences standards (style égaliseur 10 bandes Technics / Pioneer)
        painter.setPen(QColor(148, 163, 184, 130))
        font_freq = painter.font()
        font_freq.setPointSize(8)
        font_freq.setBold(True)
        painter.setFont(font_freq)

        freq_labels = ["31Hz", "63Hz", "125Hz", "250Hz", "500Hz", "1kHz", "2kHz", "4kHz", "8kHz", "16kHz"]
        lbl_y = baseline_y + 16.0
        k = len(freq_labels)
        for idx, lbl in enumerate(freq_labels):
            pos_x = start_x + (idx / float(k - 1)) * (total_span - 32.0)
            painter.drawText(QPointF(pos_x, lbl_y), lbl)

        painter.setFont(font_orig)
