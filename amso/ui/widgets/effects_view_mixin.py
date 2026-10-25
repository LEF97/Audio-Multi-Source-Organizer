"""Mixin partagé pour la gestion des effets visuels (PlayerView et BlindTestView)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLabel, QWidget

from amso.core.config import get_config_manager
from amso.core.i18n import tr
from amso.ui.styles import effects_combo_qss
from amso.ui.views.visual_effects import VisualEffectWidget
from amso.ui.widgets.common import EffectContainer
from amso.ui.widgets.effects_combo import populate_effects_combo

if TYPE_CHECKING:
    _MixinBase = QWidget
else:
    _MixinBase = object


class EffectsViewMixin(_MixinBase):
    """Logique partagée de sélection, stockage et contrôle de l'effet visuel actif."""

    if TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any: ...

    def _create_effects_combo(self) -> tuple[QLabel, QComboBox]:
        """Crée le label badge et le menu déroulant stylisé pour les effets visuels."""
        lbl_badge = QLabel(tr("player.visual_effect"))
        lbl_badge.setStyleSheet("color: #94A3B8; font-size: 12.5px; font-weight: 500; margin-right: 4px;")

        combo = QComboBox()
        combo.setCursor(Qt.CursorShape.PointingHandCursor)
        combo.setFixedWidth(250)
        combo.view().setMinimumWidth(260)
        combo.setStyleSheet(effects_combo_qss())
        combo.currentIndexChanged.connect(self._on_effect_combo_changed)
        return lbl_badge, combo

    def _create_effect_container(self) -> tuple[VisualEffectWidget, EffectContainer]:
        """Instancie le canevas d'effet et son conteneur arrière-plan redimensionnable."""
        effect_canvas = VisualEffectWidget(effect_type=self.current_effect)
        container = EffectContainer(effect_canvas)
        return effect_canvas, container

    def _populate_effects_combo(self) -> None:
        """Remplit le menu déroulant avec les effets disponibles."""
        populate_effects_combo(self.combo_effect, self.current_effect)

    def _on_effect_combo_changed(self) -> None:
        """Réagit à la sélection d'un nouvel effet par l'utilisateur."""
        eff = self.combo_effect.currentData()
        if eff and eff != self.current_effect:
            self.set_effect_type(eff)

    def set_effect_type(self, effect_name: str) -> None:
        """Change le type d'effet visuel actif, persiste le choix et émet le signal."""
        self.current_effect = effect_name
        canvas = getattr(self, "effect_widget", None) or getattr(self, "effect_canvas", None)
        if canvas:
            canvas.set_effect_type(effect_name)
        get_config_manager().set_visual_effect(effect_name)
        self._populate_effects_combo()
        if hasattr(self, "effect_changed"):
            self.effect_changed.emit(effect_name)

    @property
    def current_effect(self) -> str:
        """Type d'effet visuel courant, lu en cache d'instance ou depuis la configuration."""
        cached = getattr(self, "_current_effect", None)
        if cached:
            return cached
        return get_config_manager().get_visual_effect()

    @current_effect.setter
    def current_effect(self, value: str) -> None:
        self._current_effect = value

    @property
    def effect_type(self) -> str:
        return self.current_effect
