"""Tests pour la page Paramètres > Effets, le filtrage par contexte et le mode Random."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication

from amso.core.config import VISUAL_EFFECT_IDS, get_config_manager
from amso.ui.views.main_window import MainWindow
from amso.ui.widgets.effects_combo import get_available_effects


def test_config_effects_defaults_all_enabled(isolate_config) -> None:
    """Par défaut, tous les effets sont activés, Random Lecteur = 30s et Blind Test = track."""
    cfg = get_config_manager()
    assert cfg.get_enabled_effects("player") == list(VISUAL_EFFECT_IDS)
    assert cfg.get_enabled_effects("blind_test") == list(VISUAL_EFFECT_IDS)
    assert cfg.get_visual_effect_random_interval("player") == "30"
    assert cfg.get_visual_effect_random_interval("blind_test") == "track"


def test_available_effects_filtered_per_context_and_random(isolate_config) -> None:
    """Les effets proposés sont filtrés indépendamment par contexte et incluent Random si >= 2 visuels."""
    cfg = get_config_manager()
    cfg.set_enabled_effects("player", ["particles", "waves", "none"])
    cfg.set_enabled_effects("blind_test", ["stars", "none"])

    player_keys = [k for k, _ in get_available_effects("player")]
    bt_keys = [k for k, _ in get_available_effects("blind_test")]

    assert player_keys == ["none", "particles", "waves", "random"]
    assert bt_keys == ["none", "stars"]


def test_settings_effects_page_guard_and_random_behavior(isolate_config, tmp_path) -> None:
    """Vérifie le garde-fou de la dernière case, le basculement si décoché et le mode Random."""
    from amso.core.database import DatabaseManager

    _app = QApplication.instance() or QApplication([])
    cfg = get_config_manager()
    db = DatabaseManager(tmp_path / "test_effects.db")

    win = MainWindow(db=db)
    try:
        # Navigation vers Paramètres > Effets
        win._on_settings_effects_clicked()
        assert win.stacked_widget.currentWidget() == win.page_settings_effects

        # Décocher tous les effets pour le lecteur : "Désactivé" (none) se recoche automatiquement
        for eff_id in VISUAL_EFFECT_IDS:
            win._effect_checks_player[eff_id].setChecked(False)
        assert win._effect_checks_player["none"].isChecked() is True
        assert win.page_player.current_effect == "none"

        # Réactiver 2 effets visuels puis passer en mode Random
        win._effect_checks_player["particles"].setChecked(True)
        win._effect_checks_player["waves"].setChecked(True)
        win.page_player.set_effect_type("random")
        assert win.page_player.current_effect == "random"
        assert win.page_player.effect_canvas.effect_type in ("particles", "waves")

        # Changer l'intervalle Lecteur vers "À chaque morceau" et Blind Test vers "15s" sans interférence
        idx_track = win.combo_effects_random_player.findData("track")
        win.combo_effects_random_player.setCurrentIndex(idx_track)
        idx_15 = win.combo_effects_random_blind_test.findData("15")
        win.combo_effects_random_blind_test.setCurrentIndex(idx_15)
        assert cfg.get_visual_effect_random_interval("player") == "track"
        assert cfg.get_visual_effect_random_interval("blind_test") == "15"

        # Le pas aléatoire évite de répéter l'effet courant si >= 2 effets sont disponibles
        first_rendered = win.page_player.effect_canvas.effect_type
        win.page_player.apply_random_effect_step()
        second_rendered = win.page_player.effect_canvas.effect_type
        assert second_rendered in ("particles", "waves")
        assert second_rendered != first_rendered

        # Le bouton "Tout cocher" réactive tous les effets pour les deux colonnes
        win.btn_effects_check_all.click()
        assert all(chk.isChecked() for chk in win._effect_checks_player.values())
        assert all(chk.isChecked() for chk in win._effect_checks_blind_test.values())
        assert win.page_player.combo_effect.count() == len(VISUAL_EFFECT_IDS) + 1
    finally:
        win.close()
        db.close()
