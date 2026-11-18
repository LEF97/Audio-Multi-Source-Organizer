"""Page Paramètres > Lecteur (mixin de MainWindow)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from amso.core.config import get_config_manager
from amso.core.i18n import tr
from amso.ui.pages.settings_player_cover import SettingsPlayerCoverMixin
from amso.ui.pages.settings_player_effects import SettingsPlayerEffectsMixin
from amso.ui.widgets.page_header import build_page_top_bar

if TYPE_CHECKING:
    from amso.services.player_service import PlayerService

logger = logging.getLogger(__name__)


class SettingsPlayerPageMixin(SettingsPlayerEffectsMixin, SettingsPlayerCoverMixin):
    """Page Paramètres > Lecteur (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Attributs / méthodes fournis par MainWindow (typage uniquement)
        player_service: PlayerService

        def _on_crossfade_slider_changed(self, value: int) -> None: ...
        def _on_audio_engine_changed(self) -> None: ...
        def _on_vlc_latency_slider_changed(self, value: int) -> None: ...
        def _update_vlc_latency_controls_state(self) -> None: ...
        def _on_sleep_mode_changed(self) -> None: ...
        def _on_transition_mode_changed(self) -> None: ...
        def _update_crossfade_controls_state(self) -> None: ...

    def _create_settings_player_page(self) -> QWidget:
        """Page Paramètres > Lecteur (Options de veille et moteur de lecture)."""
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. En-tête
        top_bar, self.lbl_settings_player_page_title, self.btn_settings_player_help = build_page_top_bar(
            tr("settings.page_player_title"),
            "settings.player_help_title",
            "settings.player_help_body",
        )
        main_layout.addWidget(top_bar, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        cfg = get_config_manager()

        # Carte 5 : Transitions des pochettes
        content_layout.addWidget(self._build_card_cover_transitions())

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
        self.spin_bt_countdown.setSuffix(f" {tr('unit.seconds_short')}")
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
        self.spin_bt_reveal.setSuffix(f" {tr('unit.seconds_short')}")
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
        self.spin_bt_fade.setSuffix(f" {tr('unit.seconds_short')}")
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
