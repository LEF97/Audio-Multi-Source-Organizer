"""Mixin partagé pour la gestion des effets visuels (PlayerView et BlindTestView)."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any, cast

from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtWidgets import QComboBox, QLabel, QWidget

from amso.core.config import get_config_manager
from amso.core.i18n import tr
from amso.ui.styles import COLOR_TEXT_MUTED, effects_combo_qss
from amso.ui.views.visual_effects import VisualEffectWidget
from amso.ui.widgets.common import EffectContainer
from amso.ui.widgets.effects_combo import get_available_effects, populate_effects_combo

if TYPE_CHECKING:
    _MixinBase = QWidget
else:
    _MixinBase = object


class EffectsViewMixin(_MixinBase):
    """Logique partagée de sélection, stockage et contrôle de l'effet visuel actif."""

    effect_context: str = "player"

    if TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any: ...

    def _create_effects_combo(self) -> tuple[QLabel, QComboBox]:
        """Crée le label badge et le menu déroulant stylisé pour les effets visuels."""
        lbl_badge = QLabel(tr("player.visual_effect"))
        lbl_badge.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12.5px; font-weight: 500; margin-right: 4px;")

        combo = QComboBox()
        combo.setCursor(Qt.CursorShape.PointingHandCursor)
        combo.setFixedWidth(250)
        combo.view().setMinimumWidth(260)
        combo.setStyleSheet(effects_combo_qss())
        combo.currentIndexChanged.connect(self._on_effect_combo_changed)
        return lbl_badge, combo

    def _create_effect_container(self) -> tuple[VisualEffectWidget, EffectContainer]:
        """Instancie le canevas d'effet et son conteneur arrière-plan redimensionnable."""
        initial = self.current_effect
        if initial == "random":
            initial = self._pick_random_effect()
        effect_canvas = VisualEffectWidget(effect_type=initial)
        container = EffectContainer(effect_canvas)
        return effect_canvas, container

    def _get_configured_effect(self) -> str:
        """Lit l'effet actif configuré pour le contexte courant."""
        cfg = get_config_manager()
        if self.effect_context == "blind_test":
            return cfg.get_blind_test_visual_effect()
        return cfg.get_visual_effect()

    def _save_configured_effect(self, effect_name: str) -> None:
        """Persiste l'effet actif pour le contexte courant."""
        cfg = get_config_manager()
        if self.effect_context == "blind_test":
            cfg.set_blind_test_visual_effect(effect_name)
        else:
            cfg.set_visual_effect(effect_name)

    def _get_effect_canvas(self) -> VisualEffectWidget | None:
        return getattr(self, "effect_widget", None) or getattr(self, "effect_canvas", None)

    def _pick_random_effect(self) -> str:
        """Tire aléatoirement un effet visuel activé pour ce contexte, sans répétition immédiate."""
        enabled = [eff for eff in get_config_manager().get_enabled_effects(self.effect_context) if eff != "none"]
        if not enabled:
            return "none"
        canvas = self._get_effect_canvas()
        current_rendered = canvas.effect_type if canvas else None
        candidates = [eff for eff in enabled if eff != current_rendered] if len(enabled) >= 2 else enabled
        return random.choice(candidates)

    def apply_random_effect_step(self) -> None:
        """Applique un nouvel effet aléatoire au canevas si le mode Random est actif."""
        if self.current_effect != "random":
            return
        canvas = self._get_effect_canvas()
        if canvas:
            canvas.set_effect_type(self._pick_random_effect())

    def _ensure_random_timer(self) -> QTimer:
        timer = getattr(self, "_random_effect_timer", None)
        if timer is None:
            timer = QTimer(cast("QObject", self))
            timer.timeout.connect(self.apply_random_effect_step)
            self._random_effect_timer = timer
        return timer

    def _sync_random_timer(self) -> None:
        """Démarre ou arrête le timer de rotation aléatoire selon la visibilité et l'intervalle."""
        timer = getattr(self, "_random_effect_timer", None)
        if self.current_effect != "random" or not self.isVisible():
            if timer is not None:
                timer.stop()
            return

        interval = get_config_manager().get_visual_effect_random_interval(self.effect_context)
        if interval == "track":
            if timer is not None:
                timer.stop()
            return

        timer = self._ensure_random_timer()
        interval_ms = int(interval) * 1000
        if timer.interval() != interval_ms or not timer.isActive():
            timer.start(interval_ms)

    def _stop_random_timer(self) -> None:
        timer = getattr(self, "_random_effect_timer", None)
        if timer is not None:
            timer.stop()

    def _populate_effects_combo(self) -> None:
        """Remplit le menu déroulant avec les effets disponibles pour ce contexte."""
        populate_effects_combo(self.combo_effect, self.current_effect, context=self.effect_context)

    def refresh_available_effects(self) -> None:
        """Met à jour la liste déroulante après modification des préférences et garantit un effet valide."""
        available = [key for key, _label in get_available_effects(context=self.effect_context)]
        target = self.current_effect
        if target not in available:
            target = available[0] if available else "none"
            self.set_effect_type(target)
        else:
            self._populate_effects_combo()
            self._sync_random_timer()

    def _on_effect_combo_changed(self) -> None:
        """Réagit à la sélection d'un nouvel effet par l'utilisateur."""
        eff = self.combo_effect.currentData()
        if eff and eff != self.current_effect:
            self.set_effect_type(eff)

    def set_effect_type(self, effect_name: str) -> None:
        """Change le type d'effet visuel actif, persiste le choix et émet le signal."""
        available = [key for key, _label in get_available_effects(context=self.effect_context)]
        if available and effect_name not in available:
            effect_name = available[0]

        self.current_effect = effect_name
        canvas = self._get_effect_canvas()
        if canvas:
            rendered = self._pick_random_effect() if effect_name == "random" else effect_name
            canvas.set_effect_type(rendered)
        self._save_configured_effect(effect_name)
        self._populate_effects_combo()
        self._sync_random_timer()
        if hasattr(self, "effect_changed"):
            self.effect_changed.emit(effect_name)

    @property
    def current_effect(self) -> str:
        """Type d'effet visuel courant, lu en cache d'instance ou depuis la configuration."""
        cached = getattr(self, "_current_effect", None)
        if cached:
            return cached
        return self._get_configured_effect()

    @current_effect.setter
    def current_effect(self, value: str) -> None:
        self._current_effect = value

    @property
    def effect_type(self) -> str:
        return self.current_effect
