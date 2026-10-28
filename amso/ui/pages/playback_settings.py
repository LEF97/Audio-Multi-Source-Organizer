"""Veille, transitions, crossfade et effets visuels (mixin de MainWindow)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
)

from amso.core.config import get_config_manager
from amso.core.i18n import tr
from amso.services.sleep_inhibitor import SleepInhibitor

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    _MixinBase = QMainWindow
else:
    _MixinBase = object


class PlaybackSettingsMixin(_MixinBase):
    """Veille, transitions, crossfade et effets visuels (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de MainWindow sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    def _update_sleep_inhibition(self) -> None:
        """Met à jour l'inhibition de veille du système et de l'écran selon le mode choisi, l'état et la page active."""
        cfg = get_config_manager()
        is_playing = (getattr(self, "_player_state", "stopped") == "playing") or self.player_service.is_playing
        mode = cfg.get_sleep_mode()

        if not is_playing or mode == "allow":
            SleepInhibitor.release()
            return

        if mode == "always":
            SleepInhibitor.inhibit(prevent_display=True)
            return

        # mode == "player_playlist" (par défaut)
        curr_widget = self.stacked_widget.currentWidget() if hasattr(self, "stacked_widget") else None
        is_player_or_playlist = curr_widget in (
            getattr(self, "page_player", None),
            getattr(self, "page_blind_test", None),
            getattr(self, "page_playlist", None),
        )
        SleepInhibitor.inhibit(prevent_display=is_player_or_playlist)

    def _on_sleep_mode_changed(self) -> None:
        """Enregistre le choix du mode de veille et applique immédiatement l'effet."""
        cfg = get_config_manager()
        if hasattr(self, "radio_sleep_allow") and self.radio_sleep_allow.isChecked():
            cfg.set_sleep_mode("allow")
        elif hasattr(self, "radio_sleep_always") and self.radio_sleep_always.isChecked():
            cfg.set_sleep_mode("always")
        elif hasattr(self, "radio_sleep_screens") and self.radio_sleep_screens.isChecked():
            cfg.set_sleep_mode("player_playlist")
        self._update_sleep_inhibition()

    def _on_prevent_sleep_toggled(self, checked: bool) -> None:
        """Rétrocompatibilité."""
        cfg = get_config_manager()
        cfg.set_prevent_sleep(checked)
        self._update_sleep_inhibition()

    def _on_transition_mode_changed(self) -> None:
        cfg = get_config_manager()
        new_mode = None
        if hasattr(self, "radio_trans_standard") and self.radio_trans_standard.isChecked():
            new_mode = "standard"
        elif hasattr(self, "radio_trans_gapless") and self.radio_trans_gapless.isChecked():
            new_mode = "gapless"
        elif hasattr(self, "radio_trans_crossfade") and self.radio_trans_crossfade.isChecked():
            new_mode = "crossfade"

        if not new_mode:
            return

        old_mode = cfg.get_transition_mode()
        cfg.set_transition_mode(new_mode)
        self._update_crossfade_controls_state()

        # Couper la lecture et réinitialiser complètement le lecteur si le mode change
        if new_mode != old_mode and hasattr(self, "player_service") and self.player_service:
            self.player_service.reset_playback(keep_position=True)

    def _on_crossfade_slider_changed(self, value: int) -> None:
        cfg = get_config_manager()
        cfg.set_crossfade_duration(value)
        if hasattr(self, "lbl_crossfade_value"):
            self.lbl_crossfade_value.setText(tr("settings.crossfade_duration_val", seconds=str(value)))

    def _update_crossfade_controls_state(self) -> None:
        if not hasattr(self, "crossfade_container") or not hasattr(self, "radio_trans_crossfade"):
            return
        is_cf = self.radio_trans_crossfade.isChecked()
        self.crossfade_container.setEnabled(is_cf)
        if hasattr(self, "lbl_crossfade_duration"):
            self.lbl_crossfade_duration.setStyleSheet(
                "color: #CBD5E1; font-size: 12.5px; font-weight: 500;"
                if is_cf
                else "color: #475569; font-size: 12.5px; font-weight: 500;"
            )
        if hasattr(self, "lbl_crossfade_value"):
            self.lbl_crossfade_value.setStyleSheet(
                "color: #38BDF8; font-size: 12.5px; font-weight: 600; min-width: 90px;"
                if is_cf
                else "color: #475569; font-size: 12.5px; font-weight: 600; min-width: 90px;"
            )

    def _on_visual_effect_changed(self) -> None:
        """Appelé lors d'un changement de sélection dans les boutons radio d'effets visuels."""
        if not hasattr(self, "effect_group"):
            return
        if hasattr(self, "radio_eff_particles") and self.radio_eff_particles.isChecked():
            eff = "particles"
        elif hasattr(self, "radio_eff_waves") and self.radio_eff_waves.isChecked():
            eff = "waves"
        elif hasattr(self, "radio_eff_stars") and self.radio_eff_stars.isChecked():
            eff = "stars"
        elif hasattr(self, "radio_eff_warp") and self.radio_eff_warp.isChecked():
            eff = "warp"
        elif hasattr(self, "radio_eff_warp_dynamic") and self.radio_eff_warp_dynamic.isChecked():
            eff = "warp_dynamic"
        elif hasattr(self, "radio_eff_aurora") and self.radio_eff_aurora.isChecked():
            eff = "aurora"
        elif hasattr(self, "radio_eff_bars") and self.radio_eff_bars.isChecked():
            eff = "bars"
        elif hasattr(self, "radio_eff_bars_full") and self.radio_eff_bars_full.isChecked():
            eff = "bars_full"
        elif hasattr(self, "radio_eff_none") and self.radio_eff_none.isChecked():
            eff = "none"
        else:
            eff = "particles"

        cfg = get_config_manager()
        cfg.set_visual_effect(eff)
        if hasattr(self, "page_player") and self.page_player:
            self.page_player.set_effect_type(eff)
        if hasattr(self, "page_blind_test") and self.page_blind_test:
            self.page_blind_test.set_effect_type(eff)

    def set_visual_effect(self, eff: str) -> None:
        """Applique l'effet visuel à l'ensemble de l'application (Lecteur, Blind Test et réglages)."""
        cfg = get_config_manager()
        cfg.set_visual_effect(eff)
        self._sync_visual_effect_radio(eff)

    def _sync_visual_effect_radio(self, eff: str) -> None:
        """Synchronise l'état des boutons radio Paramètres > Lecteur avec le lecteur sans boucle."""
        if hasattr(self, "page_blind_test") and self.page_blind_test:
            if getattr(self.page_blind_test, "current_effect", None) != eff:
                self.page_blind_test.set_effect_type(eff)
        if hasattr(self, "page_player") and self.page_player:
            if getattr(self.page_player, "current_effect", None) != eff:
                self.page_player.blockSignals(True)
                self.page_player.set_effect_type(eff)
                self.page_player.blockSignals(False)
        if not hasattr(self, "effect_group"):
            return
        radio_map = {
            "particles": getattr(self, "radio_eff_particles", None),
            "waves": getattr(self, "radio_eff_waves", None),
            "stars": getattr(self, "radio_eff_stars", None),
            "warp": getattr(self, "radio_eff_warp", None),
            "warp_dynamic": getattr(self, "radio_eff_warp_dynamic", None),
            "aurora": getattr(self, "radio_eff_aurora", None),
            "bars": getattr(self, "radio_eff_bars", None),
            "bars_full": getattr(self, "radio_eff_bars_full", None),
            "none": getattr(self, "radio_eff_none", None),
        }
        target = radio_map.get(eff)
        if target and not target.isChecked():
            self.effect_group.blockSignals(True)
            target.setChecked(True)
            self.effect_group.blockSignals(False)

    def _on_player_state_changed(self, state: str) -> None:
        self._player_state = state
        self._update_sleep_inhibition()
        if state == "playing" and getattr(self, "_status_is_alert", False):
            self._status_is_alert = False
            self.status_label.setText(tr("status.ready"))
            self.status_label.setToolTip("")
            self.status_label.setCursor(Qt.CursorShape.ArrowCursor)

    def _on_audio_engine_changed(self) -> None:
        """Sauvegarde le choix d'architecture du moteur audio et réinitialise le lecteur."""
        cfg = get_config_manager()
        new_engine = None
        if hasattr(self, "radio_engine_vlc") and self.radio_engine_vlc.isChecked():
            new_engine = "vlc_direct"
        elif hasattr(self, "radio_engine_buffer") and self.radio_engine_buffer.isChecked():
            new_engine = "buffer"

        if not new_engine:
            return

        old_engine = cfg.get_audio_engine()
        cfg.set_audio_engine(new_engine)
        self._update_vlc_latency_controls_state()

        # Si le moteur a changé, couper la lecture et réinitialiser complètement le lecteur
        if new_engine != old_engine and hasattr(self, "player_service") and self.player_service:
            self.player_service.reset_playback(keep_position=True)

    def _on_vlc_latency_slider_changed(self, value: int) -> None:
        """Met à jour la latence DirectSound pour LibVLC."""
        cfg = get_config_manager()
        cfg.set_vlc_gapless_latency(value)
        if hasattr(self, "player_service") and self.player_service:
            self.player_service.gapless_directsound_latency_ms = value
        if hasattr(self, "lbl_vlc_latency_val"):
            self.lbl_vlc_latency_val.setText(tr("settings.player_engine_vlc_latency_val", ms=str(value)))

    def _update_vlc_latency_controls_state(self) -> None:
        """Affiche ou masque les réglages spécifiques à LibVLC."""
        if not hasattr(self, "vlc_latency_container") or not hasattr(self, "radio_engine_vlc"):
            return
        is_vlc = self.radio_engine_vlc.isChecked()
        self.vlc_latency_container.setVisible(is_vlc)
