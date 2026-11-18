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
from amso.ui.pages.vlc_status import build_vlc_status
from amso.ui.styles import (
    COLOR_BG_DEEP,
    COLOR_BG_SLATE,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_TEXT,
    COLOR_TEXT_BRIGHT,
    COLOR_TEXT_DIM,
    COLOR_TEXT_MUTED,
    crossfade_slider_qss,
    settings_radio_qss,
)

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
        self.lbl_card_transitions_title.setStyleSheet(f"color: {COLOR_TEXT_BRIGHT}; font-size: 14px; font-weight: 700;")
        l_trans.addWidget(self.lbl_card_transitions_title)

        self.lbl_card_transitions_desc = QLabel(tr("settings.player_transitions_desc"))
        self.lbl_card_transitions_desc.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
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
        self.lbl_trans_standard_hint.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 12px; margin-left: 26px;")
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
        self.lbl_trans_gapless_hint.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 12px; margin-left: 26px;")
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
        self.lbl_trans_crossfade_hint.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 12px; margin-left: 26px;")
        self.lbl_trans_crossfade_hint.setWordWrap(True)
        box_crossfade.addWidget(self.lbl_trans_crossfade_hint)

        # Conteneur curseur de durée de fondu (indenté)
        self.crossfade_container = QWidget()
        h_cf = QHBoxLayout(self.crossfade_container)
        h_cf.setContentsMargins(26, 6, 12, 4)
        h_cf.setSpacing(12)

        self.lbl_crossfade_duration = QLabel(tr("settings.crossfade_duration"))
        self.lbl_crossfade_duration.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 12.5px; font-weight: 500;")
        h_cf.addWidget(self.lbl_crossfade_duration)

        self.slider_crossfade = QSlider(Qt.Orientation.Horizontal)
        self.slider_crossfade.setRange(1, 20)
        self.slider_crossfade.setSingleStep(1)
        self.slider_crossfade.setPageStep(2)
        self.slider_crossfade.setFixedWidth(200)
        self.slider_crossfade.setStyleSheet(crossfade_slider_qss())
        h_cf.addWidget(self.slider_crossfade)

        self.lbl_crossfade_value = QLabel()
        self.lbl_crossfade_value.setStyleSheet(
            f"color: {COLOR_PRIMARY_HOVER}; font-size: 12.5px; font-weight: 600; min-width: 90px;"
        )
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
        self.lbl_card_engine_title.setStyleSheet(f"color: {COLOR_TEXT_BRIGHT}; font-size: 14px; font-weight: 700;")
        l_eng.addWidget(self.lbl_card_engine_title)

        self.lbl_card_engine_desc = QLabel(tr("settings.player_engine_choice_desc"))
        self.lbl_card_engine_desc.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
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
        self.lbl_engine_buffer_hint.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 12px; margin-left: 26px;")
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
        self.lbl_engine_vlc_hint.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 12px; margin-left: 26px;")
        self.lbl_engine_vlc_hint.setWordWrap(True)
        box_vlc.addWidget(self.lbl_engine_vlc_hint)
        box_vlc.addWidget(self._build_vlc_latency_control())
        l_eng.addLayout(box_vlc)

        # Statut LibVLC
        status_html, status_tip = build_vlc_status(getattr(self, "player_service", None))
        self.lbl_vlc_status_val = QLabel(status_html)
        self.lbl_vlc_status_val.setToolTip(status_tip)
        self.lbl_vlc_status_val.setStyleSheet(f"font-size: 12.5px; color: {COLOR_TEXT}; margin-top: 4px;")
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
        self.lbl_vlc_latency.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 12.5px; font-weight: 500;")
        h_lat.addWidget(self.lbl_vlc_latency)

        self.slider_vlc_latency = QSlider(Qt.Orientation.Horizontal)
        self.slider_vlc_latency.setRange(0, 1000)
        self.slider_vlc_latency.setSingleStep(10)
        self.slider_vlc_latency.setPageStep(50)
        self.slider_vlc_latency.setFixedWidth(180)
        self.slider_vlc_latency.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 6px;
                background: {COLOR_BG_SLATE};
                border-radius: 3px;
            }}
            QSlider::sub-page:horizontal {{
                background: {COLOR_PRIMARY};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {COLOR_PRIMARY_HOVER};
                border: 2px solid {COLOR_BG_DEEP};
                width: 16px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 8px;
            }}
            QSlider::handle:horizontal:hover {{
                background: #7DD3FC;
            }}
        """)
        h_lat.addWidget(self.slider_vlc_latency)

        cur_lat = cfg.get_vlc_gapless_latency()
        self.slider_vlc_latency.setValue(cur_lat)

        self.lbl_vlc_latency_val = QLabel(tr("settings.player_engine_vlc_latency_val", ms=str(cur_lat)))
        self.lbl_vlc_latency_val.setStyleSheet(
            f"color: {COLOR_PRIMARY_HOVER}; font-size: 12.5px; font-weight: 600; min-width: 60px;"
        )
        h_lat.addWidget(self.lbl_vlc_latency_val)
        h_lat.addStretch()
        vlc_lat_layout.addLayout(h_lat)

        self.lbl_vlc_latency_hint = QLabel(tr("settings.player_engine_vlc_latency_hint"))
        self.lbl_vlc_latency_hint.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 11.5px;")
        self.lbl_vlc_latency_hint.setWordWrap(True)
        vlc_lat_layout.addWidget(self.lbl_vlc_latency_hint)

        self.slider_vlc_latency.valueChanged.connect(self._on_vlc_latency_slider_changed)
        return self.vlc_latency_container
