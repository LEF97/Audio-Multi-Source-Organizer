"""Page Paramètres > Lecteur (mixin de MainWindow)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from amso.core.config import get_config_manager
from amso.core.i18n import tr

if TYPE_CHECKING:
    from amso.services.player_service import PlayerService

logger = logging.getLogger(__name__)


class SettingsPlayerPageMixin:
    """Page Paramètres > Lecteur (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Attributs / méthodes fournis par MainWindow (typage uniquement)
        player_service: PlayerService

        def _on_crossfade_slider_changed(self, value: int) -> None: ...
        def _on_sleep_mode_changed(self) -> None: ...
        def _on_transition_mode_changed(self) -> None: ...
        def _on_visual_effect_changed(self) -> None: ...
        def _update_crossfade_controls_state(self) -> None: ...

    def _create_settings_player_page(self) -> QWidget:
        """Page Paramètres > Lecteur (Options de veille et moteur de lecture)."""
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. En-tête
        top_bar = QFrame()
        top_bar.setObjectName("topBarFrame")
        top_bar.setFixedHeight(50)
        top_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 12, 20, 12)

        self.lbl_settings_player_page_title = QLabel(tr("settings.page_player_title"))
        self.lbl_settings_player_page_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        top_layout.addWidget(self.lbl_settings_player_page_title)
        top_layout.addStretch()
        main_layout.addWidget(top_bar, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Carte 1 : Alimentation et Veille
        card_sleep = QFrame()
        card_sleep.setProperty("class", "dashboard-card")
        l_sleep = QVBoxLayout(card_sleep)
        l_sleep.setContentsMargins(18, 16, 18, 16)
        l_sleep.setSpacing(10)

        self.lbl_card_player_title = QLabel(tr("settings.player_playback_title"))
        self.lbl_card_player_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        l_sleep.addWidget(self.lbl_card_player_title)

        self.lbl_card_player_desc = QLabel(tr("settings.player_playback_desc"))
        self.lbl_card_player_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        l_sleep.addWidget(self.lbl_card_player_desc)

        cfg = get_config_manager()

        radio_qss = """
            QRadioButton {
                color: #F8FAFC;
                font-size: 13.5px;
                font-weight: 600;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 1px solid #333846;
                background-color: #121418;
            }
            QRadioButton::indicator:hover {
                border-color: #38BDF8;
            }
            QRadioButton::indicator:checked {
                background-color: #0284C7;
                border-color: #38BDF8;
            }
        """

        self.sleep_group = QButtonGroup(cast("QObject", self))

        # Choix 1 : Autoriser la veille
        box_allow = QVBoxLayout()
        box_allow.setSpacing(3)
        self.radio_sleep_allow = QRadioButton(tr("settings.sleep_mode_allow"))
        self.radio_sleep_allow.setStyleSheet(radio_qss)
        self.sleep_group.addButton(self.radio_sleep_allow)
        box_allow.addWidget(self.radio_sleep_allow)

        self.lbl_sleep_allow_hint = QLabel(tr("settings.sleep_mode_allow_hint"))
        self.lbl_sleep_allow_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_sleep_allow_hint.setWordWrap(True)
        box_allow.addWidget(self.lbl_sleep_allow_hint)
        l_sleep.addLayout(box_allow)

        # Choix 2 (par défaut) : Ne pas autoriser la veille sur les écrans Lecteur et Playlist
        box_screens = QVBoxLayout()
        box_screens.setSpacing(3)
        self.radio_sleep_screens = QRadioButton(tr("settings.sleep_mode_player_playlist"))
        self.radio_sleep_screens.setStyleSheet(radio_qss)
        self.sleep_group.addButton(self.radio_sleep_screens)
        box_screens.addWidget(self.radio_sleep_screens)

        self.lbl_sleep_screens_hint = QLabel(tr("settings.sleep_mode_player_playlist_hint"))
        self.lbl_sleep_screens_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_sleep_screens_hint.setWordWrap(True)
        box_screens.addWidget(self.lbl_sleep_screens_hint)
        l_sleep.addLayout(box_screens)

        # Choix 3 : Ne pas autoriser la veille
        box_always = QVBoxLayout()
        box_always.setSpacing(3)
        self.radio_sleep_always = QRadioButton(tr("settings.sleep_mode_always"))
        self.radio_sleep_always.setStyleSheet(radio_qss)
        self.sleep_group.addButton(self.radio_sleep_always)
        box_always.addWidget(self.radio_sleep_always)

        self.lbl_sleep_always_hint = QLabel(tr("settings.sleep_mode_always_hint"))
        self.lbl_sleep_always_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_sleep_always_hint.setWordWrap(True)
        box_always.addWidget(self.lbl_sleep_always_hint)
        l_sleep.addLayout(box_always)

        sleep_mode = cfg.get_sleep_mode()
        if sleep_mode == "allow":
            self.radio_sleep_allow.setChecked(True)
        elif sleep_mode == "always":
            self.radio_sleep_always.setChecked(True)
        else:
            self.radio_sleep_screens.setChecked(True)

        self.radio_sleep_allow.toggled.connect(self._on_sleep_mode_changed)
        self.radio_sleep_screens.toggled.connect(self._on_sleep_mode_changed)
        self.radio_sleep_always.toggled.connect(self._on_sleep_mode_changed)

        content_layout.addWidget(card_sleep)

        # Carte 2 : Transitions et enchaînement des pistes
        card_transitions = QFrame()
        card_transitions.setProperty("class", "dashboard-card")
        l_trans = QVBoxLayout(card_transitions)
        l_trans.setContentsMargins(18, 16, 18, 16)
        l_trans.setSpacing(12)

        self.lbl_card_transitions_title = QLabel(tr("settings.player_transitions_title"))
        self.lbl_card_transitions_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        l_trans.addWidget(self.lbl_card_transitions_title)

        self.lbl_card_transitions_desc = QLabel(tr("settings.player_transitions_desc"))
        self.lbl_card_transitions_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        l_trans.addWidget(self.lbl_card_transitions_desc)

        radio_qss = """
            QRadioButton {
                color: #F8FAFC;
                font-size: 13.5px;
                font-weight: 600;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 1px solid #333846;
                background-color: #121418;
            }
            QRadioButton::indicator:hover {
                border-color: #38BDF8;
            }
            QRadioButton::indicator:checked {
                background-color: #0284C7;
                border-color: #38BDF8;
            }
        """

        self.transition_group = QButtonGroup(cast("QObject", self))

        # Choix 1 : Pas de fondu enchaîné (standard)
        box_standard = QVBoxLayout()
        box_standard.setSpacing(3)
        self.radio_trans_standard = QRadioButton(tr("settings.transition_standard"))
        self.radio_trans_standard.setStyleSheet(radio_qss)
        self.transition_group.addButton(self.radio_trans_standard)
        box_standard.addWidget(self.radio_trans_standard)

        self.lbl_trans_standard_hint = QLabel(tr("settings.transition_standard_hint"))
        self.lbl_trans_standard_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_trans_standard_hint.setWordWrap(True)
        box_standard.addWidget(self.lbl_trans_standard_hint)
        l_trans.addLayout(box_standard)

        # Choix 2 (par défaut) : Enchaînement instantané (gapless)
        box_gapless = QVBoxLayout()
        box_gapless.setSpacing(3)
        self.radio_trans_gapless = QRadioButton(tr("settings.transition_gapless"))
        self.radio_trans_gapless.setStyleSheet(radio_qss)
        self.transition_group.addButton(self.radio_trans_gapless)
        box_gapless.addWidget(self.radio_trans_gapless)

        self.lbl_trans_gapless_hint = QLabel(tr("settings.transition_gapless_hint"))
        self.lbl_trans_gapless_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_trans_gapless_hint.setWordWrap(True)
        box_gapless.addWidget(self.lbl_trans_gapless_hint)
        l_trans.addLayout(box_gapless)

        # Choix 3 : Fondu enchaîné (crossfade avec curseur)
        box_crossfade = QVBoxLayout()
        box_crossfade.setSpacing(3)
        self.radio_trans_crossfade = QRadioButton(tr("settings.transition_crossfade"))
        self.radio_trans_crossfade.setStyleSheet(radio_qss)
        self.transition_group.addButton(self.radio_trans_crossfade)
        box_crossfade.addWidget(self.radio_trans_crossfade)

        self.lbl_trans_crossfade_hint = QLabel(tr("settings.transition_crossfade_hint"))
        self.lbl_trans_crossfade_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_trans_crossfade_hint.setWordWrap(True)
        box_crossfade.addWidget(self.lbl_trans_crossfade_hint)

        # Conteneur curseur de durée de fondu (indenté)
        self.crossfade_container = QWidget()
        h_cf = QHBoxLayout(self.crossfade_container)
        h_cf.setContentsMargins(26, 6, 12, 4)
        h_cf.setSpacing(12)

        self.lbl_crossfade_duration = QLabel(tr("settings.crossfade_duration"))
        self.lbl_crossfade_duration.setStyleSheet("color: #CBD5E1; font-size: 12.5px; font-weight: 500;")
        h_cf.addWidget(self.lbl_crossfade_duration)

        self.slider_crossfade = QSlider(Qt.Orientation.Horizontal)
        self.slider_crossfade.setRange(1, 20)
        self.slider_crossfade.setSingleStep(1)
        self.slider_crossfade.setPageStep(2)
        self.slider_crossfade.setFixedWidth(200)
        self.slider_crossfade.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #1E293B;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #0284C7;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #38BDF8;
                border: 2px solid #0F172A;
                width: 16px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #7DD3FC;
            }
        """)
        h_cf.addWidget(self.slider_crossfade)

        self.lbl_crossfade_value = QLabel()
        self.lbl_crossfade_value.setStyleSheet("color: #38BDF8; font-size: 12.5px; font-weight: 600; min-width: 90px;")
        h_cf.addWidget(self.lbl_crossfade_value)
        h_cf.addStretch()

        box_crossfade.addWidget(self.crossfade_container)
        l_trans.addLayout(box_crossfade)

        # État initial selon la configuration
        trans_mode = cfg.get_transition_mode()
        if trans_mode == "standard":
            self.radio_trans_standard.setChecked(True)
        elif trans_mode == "crossfade":
            self.radio_trans_crossfade.setChecked(True)
        else:
            self.radio_trans_gapless.setChecked(True)

        cf_dur = cfg.get_crossfade_duration()
        self.slider_crossfade.setValue(cf_dur)
        self.lbl_crossfade_value.setText(tr("settings.crossfade_duration_val", seconds=str(cf_dur)))
        self._update_crossfade_controls_state()

        # Connexions des signaux
        self.radio_trans_standard.toggled.connect(self._on_transition_mode_changed)
        self.radio_trans_gapless.toggled.connect(self._on_transition_mode_changed)
        self.radio_trans_crossfade.toggled.connect(self._on_transition_mode_changed)
        self.slider_crossfade.valueChanged.connect(self._on_crossfade_slider_changed)

        content_layout.addWidget(card_transitions)

        # Carte 3 : Effets visuels d'ambiance
        card_effects = QFrame()
        card_effects.setProperty("class", "dashboard-card")
        l_eff = QVBoxLayout(card_effects)
        l_eff.setContentsMargins(18, 16, 18, 16)
        l_eff.setSpacing(12)

        self.lbl_card_effects_title = QLabel(tr("settings.player_effects_title"))
        self.lbl_card_effects_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        l_eff.addWidget(self.lbl_card_effects_title)

        self.lbl_card_effects_desc = QLabel(tr("settings.player_effects_desc"))
        self.lbl_card_effects_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        l_eff.addWidget(self.lbl_card_effects_desc)

        self.effect_group = QButtonGroup(cast("QObject", self))

        # Effet 1 : Poussière d'étoiles & particules
        box_eff_part = QVBoxLayout()
        box_eff_part.setSpacing(3)
        self.radio_eff_particles = QRadioButton(f"✨ {tr('effects.particles')}")
        self.radio_eff_particles.setStyleSheet(radio_qss)
        self.effect_group.addButton(self.radio_eff_particles)
        box_eff_part.addWidget(self.radio_eff_particles)

        self.lbl_eff_particles_hint = QLabel(tr("effects.particles_hint"))
        self.lbl_eff_particles_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_eff_particles_hint.setWordWrap(True)
        box_eff_part.addWidget(self.lbl_eff_particles_hint)
        l_eff.addLayout(box_eff_part)

        # Effet 2 : Ondes néon spectrales
        box_eff_waves = QVBoxLayout()
        box_eff_waves.setSpacing(3)
        self.radio_eff_waves = QRadioButton(f"🌊 {tr('effects.waves')}")
        self.radio_eff_waves.setStyleSheet(radio_qss)
        self.effect_group.addButton(self.radio_eff_waves)
        box_eff_waves.addWidget(self.radio_eff_waves)

        self.lbl_eff_waves_hint = QLabel(tr("effects.waves_hint"))
        self.lbl_eff_waves_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_eff_waves_hint.setWordWrap(True)
        box_eff_waves.addWidget(self.lbl_eff_waves_hint)
        l_eff.addLayout(box_eff_waves)

        # Effet 3 : Pluie de comètes filantes
        box_eff_stars = QVBoxLayout()
        box_eff_stars.setSpacing(3)
        self.radio_eff_stars = QRadioButton(f"☄️ {tr('effects.stars')}")
        self.radio_eff_stars.setStyleSheet(radio_qss)
        self.effect_group.addButton(self.radio_eff_stars)
        box_eff_stars.addWidget(self.radio_eff_stars)

        self.lbl_eff_stars_hint = QLabel(tr("effects.stars_hint"))
        self.lbl_eff_stars_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_eff_stars_hint.setWordWrap(True)
        box_eff_stars.addWidget(self.lbl_eff_stars_hint)
        l_eff.addLayout(box_eff_stars)

        # Effet 4 : Hyperespace (Voyage spatial 3D)
        box_eff_warp = QVBoxLayout()
        box_eff_warp.setSpacing(3)
        self.radio_eff_warp = QRadioButton(f"🚀 {tr('effects.warp')}")
        self.radio_eff_warp.setStyleSheet(radio_qss)
        self.effect_group.addButton(self.radio_eff_warp)
        box_eff_warp.addWidget(self.radio_eff_warp)

        self.lbl_eff_warp_hint = QLabel(tr("effects.warp_hint"))
        self.lbl_eff_warp_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_eff_warp_hint.setWordWrap(True)
        box_eff_warp.addWidget(self.lbl_eff_warp_hint)
        l_eff.addLayout(box_eff_warp)

        # Effet 4b : Hyperespace dynamique (Navigation 3D avec changements de trajectoire)
        box_eff_warp_dyn = QVBoxLayout()
        box_eff_warp_dyn.setSpacing(3)
        self.radio_eff_warp_dynamic = QRadioButton(f"🛸 {tr('effects.warp_dynamic')}")
        self.radio_eff_warp_dynamic.setStyleSheet(radio_qss)
        self.effect_group.addButton(self.radio_eff_warp_dynamic)
        box_eff_warp_dyn.addWidget(self.radio_eff_warp_dynamic)

        self.lbl_eff_warp_dynamic_hint = QLabel(tr("effects.warp_dynamic_hint"))
        self.lbl_eff_warp_dynamic_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_eff_warp_dynamic_hint.setWordWrap(True)
        box_eff_warp_dyn.addWidget(self.lbl_eff_warp_dynamic_hint)
        l_eff.addLayout(box_eff_warp_dyn)

        # Effet 5 : Aurore boréale
        box_eff_aurora = QVBoxLayout()
        box_eff_aurora.setSpacing(3)
        self.radio_eff_aurora = QRadioButton(f"🌌 {tr('effects.aurora')}")
        self.radio_eff_aurora.setStyleSheet(radio_qss)
        self.effect_group.addButton(self.radio_eff_aurora)
        box_eff_aurora.addWidget(self.radio_eff_aurora)

        self.lbl_eff_aurora_hint = QLabel(tr("effects.aurora_hint"))
        self.lbl_eff_aurora_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_eff_aurora_hint.setWordWrap(True)
        box_eff_aurora.addWidget(self.lbl_eff_aurora_hint)
        l_eff.addLayout(box_eff_aurora)

        # Effet 6 : Barres rétro (Égaliseur de spectre)
        box_eff_bars = QVBoxLayout()
        box_eff_bars.setSpacing(3)
        self.radio_eff_bars = QRadioButton(f"📊 {tr('effects.bars')}")
        self.radio_eff_bars.setStyleSheet(radio_qss)
        self.effect_group.addButton(self.radio_eff_bars)
        box_eff_bars.addWidget(self.radio_eff_bars)

        self.lbl_eff_bars_hint = QLabel(tr("effects.bars_hint"))
        self.lbl_eff_bars_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_eff_bars_hint.setWordWrap(True)
        box_eff_bars.addWidget(self.lbl_eff_bars_hint)
        l_eff.addLayout(box_eff_bars)

        # Effet 7 : Barres rétro plein écran
        box_eff_bars_full = QVBoxLayout()
        box_eff_bars_full.setSpacing(3)
        self.radio_eff_bars_full = QRadioButton(f"📶 {tr('effects.bars_full')}")
        self.radio_eff_bars_full.setStyleSheet(radio_qss)
        self.effect_group.addButton(self.radio_eff_bars_full)
        box_eff_bars_full.addWidget(self.radio_eff_bars_full)

        self.lbl_eff_bars_full_hint = QLabel(tr("effects.bars_full_hint"))
        self.lbl_eff_bars_full_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_eff_bars_full_hint.setWordWrap(True)
        box_eff_bars_full.addWidget(self.lbl_eff_bars_full_hint)
        l_eff.addLayout(box_eff_bars_full)

        # Effet 8 : Aucun effet (désactivé)
        box_eff_none = QVBoxLayout()
        box_eff_none.setSpacing(3)
        self.radio_eff_none = QRadioButton(f"🚫 {tr('effects.none')}")
        self.radio_eff_none.setStyleSheet(radio_qss)
        self.effect_group.addButton(self.radio_eff_none)
        box_eff_none.addWidget(self.radio_eff_none)

        self.lbl_eff_none_hint = QLabel(tr("effects.none_hint"))
        self.lbl_eff_none_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_eff_none_hint.setWordWrap(True)
        box_eff_none.addWidget(self.lbl_eff_none_hint)
        l_eff.addLayout(box_eff_none)

        # État initial selon la configuration
        cur_eff = cfg.get_visual_effect()
        if cur_eff == "waves":
            self.radio_eff_waves.setChecked(True)
        elif cur_eff == "stars":
            self.radio_eff_stars.setChecked(True)
        elif cur_eff == "warp":
            self.radio_eff_warp.setChecked(True)
        elif cur_eff == "warp_dynamic":
            self.radio_eff_warp_dynamic.setChecked(True)
        elif cur_eff == "aurora":
            self.radio_eff_aurora.setChecked(True)
        elif cur_eff == "bars":
            self.radio_eff_bars.setChecked(True)
        elif cur_eff == "bars_full":
            self.radio_eff_bars_full.setChecked(True)
        elif cur_eff == "none":
            self.radio_eff_none.setChecked(True)
        else:
            self.radio_eff_particles.setChecked(True)

        self.radio_eff_particles.toggled.connect(self._on_visual_effect_changed)
        self.radio_eff_waves.toggled.connect(self._on_visual_effect_changed)
        self.radio_eff_stars.toggled.connect(self._on_visual_effect_changed)
        self.radio_eff_warp.toggled.connect(self._on_visual_effect_changed)
        self.radio_eff_warp_dynamic.toggled.connect(self._on_visual_effect_changed)
        self.radio_eff_aurora.toggled.connect(self._on_visual_effect_changed)
        self.radio_eff_bars.toggled.connect(self._on_visual_effect_changed)
        self.radio_eff_bars_full.toggled.connect(self._on_visual_effect_changed)
        self.radio_eff_none.toggled.connect(self._on_visual_effect_changed)

        content_layout.addWidget(card_effects)

        # Carte 3 : Moteur de lecture (VLC)
        card_vlc = QFrame()
        card_vlc.setProperty("class", "dashboard-card")
        l_vlc = QVBoxLayout(card_vlc)
        l_vlc.setContentsMargins(18, 16, 18, 16)
        l_vlc.setSpacing(10)

        self.lbl_card_vlc_title = QLabel(tr("settings.player_engine_title"))
        self.lbl_card_vlc_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        l_vlc.addWidget(self.lbl_card_vlc_title)

        self.lbl_card_vlc_desc = QLabel(tr("settings.player_engine_desc"))
        self.lbl_card_vlc_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        l_vlc.addWidget(self.lbl_card_vlc_desc)

        is_avail = self.player_service.is_vlc_available
        status_txt = tr("settings.player_engine_active") if is_avail else tr("settings.player_engine_inactive")
        status_color = "#34D399" if is_avail else "#EF4444"
        self.lbl_vlc_status_val = QLabel(
            f"• <b>{tr('settings.player_engine_status')}</b> <span style='color: {status_color}; font-weight: 600;'>{status_txt}</span>"
        )
        self.lbl_vlc_status_val.setStyleSheet("font-size: 12.5px; color: #CBD5E1;")
        l_vlc.addWidget(self.lbl_vlc_status_val)

        content_layout.addWidget(card_vlc)

        # Carte 4 : Paramètres du Blind Test
        card_bt = QFrame()
        card_bt.setProperty("class", "dashboard-card")
        self.card_settings_blind_test = card_bt
        l_bt = QVBoxLayout(card_bt)
        l_bt.setContentsMargins(18, 16, 18, 16)
        l_bt.setSpacing(12)

        self.lbl_card_bt_title = QLabel("🎭  " + tr("blind_test.settings_title"))
        self.lbl_card_bt_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        l_bt.addWidget(self.lbl_card_bt_title)

        self.lbl_card_bt_desc = QLabel(tr("settings.blind_test_desc"))
        self.lbl_card_bt_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        l_bt.addWidget(self.lbl_card_bt_desc)

        spin_qss = """
            QSpinBox {
                background-color: #20242D;
                color: #F8FAFC;
                border: 1px solid #333846;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 12.5px;
                font-weight: 600;
            }
            QSpinBox:focus {
                border-color: #38BDF8;
            }
        """

        inputs_layout = QHBoxLayout()
        inputs_layout.setSpacing(20)

        # 1. Durée du décompte
        cd_box = QHBoxLayout()
        cd_box.setSpacing(8)
        self.lbl_bt_countdown = QLabel(tr("blind_test.countdown_label"))
        self.lbl_bt_countdown.setStyleSheet("color: #CBD5E1; font-size: 12.5px; font-weight: 500;")
        cd_box.addWidget(self.lbl_bt_countdown)

        self.spin_bt_countdown = QSpinBox()
        self.spin_bt_countdown.setRange(5, 120)
        self.spin_bt_countdown.setSingleStep(5)
        self.spin_bt_countdown.setSuffix(" s")
        self.spin_bt_countdown.setValue(cfg.get_blind_test_countdown())
        self.spin_bt_countdown.setFixedWidth(80)
        self.spin_bt_countdown.setStyleSheet(spin_qss)
        self.spin_bt_countdown.valueChanged.connect(self._on_blind_test_settings_changed)
        cd_box.addWidget(self.spin_bt_countdown)
        inputs_layout.addLayout(cd_box)

        # 2. Durée de la découverte
        rev_box = QHBoxLayout()
        rev_box.setSpacing(8)
        self.lbl_bt_reveal = QLabel(tr("blind_test.reveal_label"))
        self.lbl_bt_reveal.setStyleSheet("color: #CBD5E1; font-size: 12.5px; font-weight: 500;")
        rev_box.addWidget(self.lbl_bt_reveal)

        self.spin_bt_reveal = QSpinBox()
        self.spin_bt_reveal.setRange(3, 60)
        self.spin_bt_reveal.setSingleStep(1)
        self.spin_bt_reveal.setSuffix(" s")
        self.spin_bt_reveal.setValue(cfg.get_blind_test_reveal())
        self.spin_bt_reveal.setFixedWidth(80)
        self.spin_bt_reveal.setStyleSheet(spin_qss)
        self.spin_bt_reveal.valueChanged.connect(self._on_blind_test_settings_changed)
        rev_box.addWidget(self.spin_bt_reveal)
        inputs_layout.addLayout(rev_box)

        # 3. Durée du fondu sonore de transition
        fade_box = QHBoxLayout()
        fade_box.setSpacing(8)
        self.lbl_bt_fade = QLabel(tr("blind_test.fade_label"))
        self.lbl_bt_fade.setStyleSheet("color: #CBD5E1; font-size: 12.5px; font-weight: 500;")
        fade_box.addWidget(self.lbl_bt_fade)

        self.spin_bt_fade = QSpinBox()
        self.spin_bt_fade.setRange(0, 10)
        self.spin_bt_fade.setSingleStep(1)
        self.spin_bt_fade.setSuffix(" s")
        self.spin_bt_fade.setValue(cfg.get_blind_test_fade())
        self.spin_bt_fade.setFixedWidth(80)
        self.spin_bt_fade.setStyleSheet(spin_qss)
        self.spin_bt_fade.valueChanged.connect(self._on_blind_test_settings_changed)
        fade_box.addWidget(self.spin_bt_fade)
        inputs_layout.addLayout(fade_box)

        inputs_layout.addStretch()
        l_bt.addLayout(inputs_layout)

        # Label d'information résumé de la manche
        self.lbl_bt_total = QLabel()
        self.lbl_bt_total.setStyleSheet("color: #38BDF8; font-size: 12px; font-weight: 500; margin-top: 4px;")
        self._update_blind_test_summary_label()
        l_bt.addWidget(self.lbl_bt_total)

        content_layout.addWidget(card_bt)
        content_layout.addStretch(1)

        # Rendre accessibles les contrôles sur le widget de page
        setattr(container, "spin_bt_countdown", self.spin_bt_countdown)  # noqa: B010
        setattr(container, "spin_bt_reveal", self.spin_bt_reveal)  # noqa: B010
        setattr(container, "spin_bt_fade", self.spin_bt_fade)  # noqa: B010
        setattr(container, "lbl_bt_total", self.lbl_bt_total)  # noqa: B010

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

        return container

    def _update_blind_test_summary_label(self) -> None:
        if not hasattr(self, "spin_bt_countdown") or not hasattr(self, "lbl_bt_total"):
            return
        cd = self.spin_bt_countdown.value()
        rev = self.spin_bt_reveal.value()
        fade = self.spin_bt_fade.value()
        tot = cd + rev
        self.lbl_bt_total.setText(tr("blind_test.total_duration", total=tot, countdown=cd, reveal=rev, fade=fade))

    def _on_blind_test_settings_changed(self) -> None:
        if not hasattr(self, "spin_bt_countdown"):
            return
        cd = self.spin_bt_countdown.value()
        rev = self.spin_bt_reveal.value()
        fade = self.spin_bt_fade.value()

        # Le fondu ne peut excéder la durée de la découverte
        if fade > rev:
            fade = rev
            self.spin_bt_fade.blockSignals(True)
            self.spin_bt_fade.setValue(fade)
            self.spin_bt_fade.blockSignals(False)

        cfg = get_config_manager()
        cfg.set_blind_test_countdown(cd)
        cfg.set_blind_test_reveal(rev)
        cfg.set_blind_test_fade(fade)

        self._update_blind_test_summary_label()

        if hasattr(self, "page_blind_test") and self.page_blind_test:
            self.page_blind_test.set_durations(cd, rev, fade)
