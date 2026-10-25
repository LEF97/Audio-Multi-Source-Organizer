"""Cartes de configuration des Transitions et Effets visuels pour Paramètres > Lecteur."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from amso.core.config import get_config_manager
from amso.core.i18n import tr
from amso.ui.styles import settings_radio_qss

if TYPE_CHECKING:
    _MixinBase = QWidget
else:
    _MixinBase = object


class SettingsPlayerEffectsMixin(_MixinBase):
    """Génération des cartes de réglage des transitions sonores et des effets visuels."""

    if TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any: ...

    def _build_card_transitions(self) -> QFrame:
        """Carte de configuration des transitions sonores et du fondu enchaîné (Crossfade)."""
        cfg = get_config_manager()
        radio_qss = settings_radio_qss()
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

        radio_qss = settings_radio_qss()

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

        return card_transitions

    def _build_card_audio_engine(self) -> QFrame:
        """Carte de sélection de l'architecture du moteur de lecture audio."""
        cfg = get_config_manager()
        radio_qss = settings_radio_qss()
        card_engine = QFrame()
        card_engine.setProperty("class", "dashboard-card")
        l_eng = QVBoxLayout(card_engine)
        l_eng.setContentsMargins(18, 16, 18, 16)
        l_eng.setSpacing(12)

        self.lbl_card_engine_title = QLabel(tr("settings.player_engine_choice_title"))
        self.lbl_card_engine_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        l_eng.addWidget(self.lbl_card_engine_title)

        self.lbl_card_engine_desc = QLabel(tr("settings.player_engine_choice_desc"))
        self.lbl_card_engine_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        l_eng.addWidget(self.lbl_card_engine_desc)

        self.engine_group = QButtonGroup(cast("QObject", self))

        # Choix 1 (recommandé) : Tampon continu en mémoire (QAudioSink / WASAPI)
        box_buffer = QVBoxLayout()
        box_buffer.setSpacing(3)
        self.radio_engine_buffer = QRadioButton(tr("settings.player_engine_buffer_label"))
        self.radio_engine_buffer.setStyleSheet(radio_qss)
        self.engine_group.addButton(self.radio_engine_buffer)
        box_buffer.addWidget(self.radio_engine_buffer)

        self.lbl_engine_buffer_hint = QLabel(tr("settings.player_engine_buffer_hint"))
        self.lbl_engine_buffer_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_engine_buffer_hint.setWordWrap(True)
        box_buffer.addWidget(self.lbl_engine_buffer_hint)
        l_eng.addLayout(box_buffer)

        # Choix 2 : Sortie directe LibVLC (double lecteur)
        box_vlc = QVBoxLayout()
        box_vlc.setSpacing(3)
        self.radio_engine_vlc = QRadioButton(tr("settings.player_engine_vlc_label"))
        self.radio_engine_vlc.setStyleSheet(radio_qss)
        self.engine_group.addButton(self.radio_engine_vlc)
        box_vlc.addWidget(self.radio_engine_vlc)

        self.lbl_engine_vlc_hint = QLabel(tr("settings.player_engine_vlc_hint"))
        self.lbl_engine_vlc_hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
        self.lbl_engine_vlc_hint.setWordWrap(True)
        box_vlc.addWidget(self.lbl_engine_vlc_hint)
        box_vlc.addWidget(self._build_vlc_latency_control())
        l_eng.addLayout(box_vlc)

        # Statut LibVLC
        is_avail = getattr(self, "player_service", None) and self.player_service.is_vlc_available
        status_txt = tr("settings.player_engine_active") if is_avail else tr("settings.player_engine_inactive")
        status_color = "#34D399" if is_avail else "#EF4444"
        self.lbl_vlc_status_val = QLabel(
            f"• <b>{tr('settings.player_engine_status')}</b> <span style='color: {status_color}; font-weight: 600;'>{status_txt}</span>"
        )
        self.lbl_vlc_status_val.setStyleSheet("font-size: 12.5px; color: #CBD5E1; margin-top: 4px;")
        l_eng.addWidget(self.lbl_vlc_status_val)

        # État initial
        cur_eng = cfg.get_audio_engine()
        is_vlc = cur_eng == "vlc_direct"
        if is_vlc:
            self.radio_engine_vlc.setChecked(True)
        else:
            self.radio_engine_buffer.setChecked(True)
        self.vlc_latency_container.setVisible(is_vlc)

        self.radio_engine_buffer.toggled.connect(self._on_audio_engine_changed)
        self.radio_engine_vlc.toggled.connect(self._on_audio_engine_changed)

        return card_engine

    def _build_vlc_latency_control(self) -> QWidget:
        """Contrôle de réglage de la latence DirectSound pour LibVLC."""
        cfg = get_config_manager()
        self.vlc_latency_container = QWidget()
        vlc_lat_layout = QVBoxLayout(self.vlc_latency_container)
        vlc_lat_layout.setContentsMargins(26, 4, 0, 0)
        vlc_lat_layout.setSpacing(4)

        h_lat = QHBoxLayout()
        self.lbl_vlc_latency = QLabel(tr("settings.player_engine_vlc_latency_label"))
        self.lbl_vlc_latency.setStyleSheet("color: #CBD5E1; font-size: 12.5px; font-weight: 500;")
        h_lat.addWidget(self.lbl_vlc_latency)

        self.slider_vlc_latency = QSlider(Qt.Orientation.Horizontal)
        self.slider_vlc_latency.setRange(0, 1000)
        self.slider_vlc_latency.setSingleStep(10)
        self.slider_vlc_latency.setPageStep(50)
        self.slider_vlc_latency.setFixedWidth(180)
        self.slider_vlc_latency.setStyleSheet("""
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
        h_lat.addWidget(self.slider_vlc_latency)

        cur_lat = cfg.get_vlc_gapless_latency()
        self.slider_vlc_latency.setValue(cur_lat)

        self.lbl_vlc_latency_val = QLabel(tr("settings.player_engine_vlc_latency_val", ms=str(cur_lat)))
        self.lbl_vlc_latency_val.setStyleSheet("color: #38BDF8; font-size: 12.5px; font-weight: 600; min-width: 60px;")
        h_lat.addWidget(self.lbl_vlc_latency_val)
        h_lat.addStretch()
        vlc_lat_layout.addLayout(h_lat)

        self.lbl_vlc_latency_hint = QLabel(tr("settings.player_engine_vlc_latency_hint"))
        self.lbl_vlc_latency_hint.setStyleSheet("color: #64748B; font-size: 11.5px;")
        self.lbl_vlc_latency_hint.setWordWrap(True)
        vlc_lat_layout.addWidget(self.lbl_vlc_latency_hint)

        self.slider_vlc_latency.valueChanged.connect(self._on_vlc_latency_slider_changed)
        return self.vlc_latency_container

    def _build_card_effects(self) -> QFrame:
        """Carte de configuration des effets visuels d'ambiance."""
        cfg = get_config_manager()
        radio_qss = settings_radio_qss()
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

        return card_effects
