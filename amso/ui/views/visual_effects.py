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

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import (
    QPainter,
)
from PySide6.QtWidgets import QWidget

from amso.ui.views.effects.bars import SpectrumBarsMixin
from amso.ui.views.effects.effect_types import Comet, Particle, WarpStar
from amso.ui.views.effects.painters import EffectPaintersMixin


class VisualEffectWidget(EffectPaintersMixin, SpectrumBarsMixin, QWidget):
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
