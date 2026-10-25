"""Sélecteur et helpers pour le menu déroulant des effets visuels (lecteur, blind test)."""

from __future__ import annotations

from PySide6.QtWidgets import QComboBox

from amso.core.i18n import tr


def get_available_effects() -> list[tuple[str, str]]:
    """Retourne la liste ordonnée des couples (id_effet, label_avec_emoji)."""
    return [
        ("particles", f"✨ {tr('effects.particles')}"),
        ("waves", f"🌊 {tr('effects.waves')}"),
        ("stars", f"☄️ {tr('effects.stars')}"),
        ("warp", f"🚀 {tr('effects.warp')}"),
        ("warp_dynamic", f"🛸 {tr('effects.warp_dynamic')}"),
        ("aurora", f"🌌 {tr('effects.aurora')}"),
        ("bars", f"📊 {tr('effects.bars')}"),
        ("bars_full", f"📶 {tr('effects.bars_full')}"),
        ("none", f"🚫 {tr('effects.none')}"),
    ]


def populate_effects_combo(combo: QComboBox, current_effect: str | None = None) -> None:
    """Remplit le QComboBox avec les effets visuels disponibles et sélectionne l'effet courant."""
    effects = get_available_effects()
    target_idx = 0
    combo.blockSignals(True)
    combo.clear()
    for i, (key, label) in enumerate(effects):
        combo.addItem(label, key)
        if current_effect and key == current_effect:
            target_idx = i
    combo.setCurrentIndex(target_idx)
    combo.blockSignals(False)
