"""Sélecteur et helpers pour le menu déroulant des effets visuels (lecteur, blind test)."""

from __future__ import annotations

from PySide6.QtWidgets import QComboBox

from amso.core.config import get_config_manager
from amso.core.i18n import tr

EFFECT_CATALOG: tuple[tuple[str, str, str, str], ...] = (
    ("none", "🚫", "effects.none", "effects.none_hint"),
    ("particles", "✨", "effects.particles", "effects.particles_hint"),
    ("waves", "🌊", "effects.waves", "effects.waves_hint"),
    ("stars", "☄️", "effects.stars", "effects.stars_hint"),
    ("warp", "🚀", "effects.warp", "effects.warp_hint"),
    ("warp_dynamic", "🛸", "effects.warp_dynamic", "effects.warp_dynamic_hint"),
    ("aurora", "🌌", "effects.aurora", "effects.aurora_hint"),
    ("bars", "📊", "effects.bars", "effects.bars_hint"),
    ("bars_full", "📶", "effects.bars_full", "effects.bars_full_hint"),
)


def get_available_effects(context: str | None = None) -> list[tuple[str, str]]:
    """Retourne la liste ordonnée des couples (id_effet, label_avec_emoji) pour un contexte donné."""
    enabled_set: set[str] | None = None
    if context in ("player", "blind_test"):
        enabled_set = set(get_config_manager().get_enabled_effects(context))

    items: list[tuple[str, str]] = []
    visual_count = 0
    for key, emoji, title_key, _hint_key in EFFECT_CATALOG:
        if enabled_set is not None and key not in enabled_set:
            continue
        items.append((key, f"{emoji} {tr(title_key)}"))
        if key != "none":
            visual_count += 1

    if visual_count >= 2:
        items.append(("random", f"🎲 {tr('effects.random')}"))
    return items


def populate_effects_combo(
    combo: QComboBox,
    current_effect: str | None = None,
    context: str | None = None,
) -> None:
    """Remplit le QComboBox avec les effets visuels disponibles et sélectionne l'effet courant."""
    effects = get_available_effects(context=context)
    target_idx = 0
    combo.blockSignals(True)
    combo.clear()
    for i, (key, label) in enumerate(effects):
        combo.addItem(label, key)
        if current_effect and key == current_effect:
            target_idx = i
    combo.setCurrentIndex(target_idx)
    combo.blockSignals(False)
