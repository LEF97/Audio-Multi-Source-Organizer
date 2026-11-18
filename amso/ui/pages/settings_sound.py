"""Page Paramètres > Son (mixin de MainWindow)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from amso.core.config import get_config_manager
from amso.core.i18n import tr
from amso.ui.styles import COLOR_PRIMARY_HOVER, COLOR_TEXT, COLOR_TEXT_BRIGHT, COLOR_TEXT_MUTED
from amso.ui.widgets.page_header import build_page_top_bar

if TYPE_CHECKING:
    from amso.services.player_service import PlayerService


class SettingsSoundPageMixin:
    """Page Paramètres > Son (moteur audio, transitions, normalisation, vitesse)."""

    if TYPE_CHECKING:
        player_service: PlayerService

        def _build_card_audio_engine(self) -> QFrame: ...
        def _build_card_transitions(self) -> QFrame: ...
        def __getattr__(self, name: str) -> Any: ...

    def _create_settings_sound_page(self) -> QWidget:
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        top_bar, self.lbl_settings_sound_page_title, self.btn_settings_sound_help = build_page_top_bar(
            tr("settings.page_sound_title"),
            "settings.sound_help_title",
            "settings.sound_help_body",
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

        content_layout.addWidget(self._build_card_audio_engine())
        content_layout.addWidget(self._build_card_transitions())
        content_layout.addWidget(self._build_card_sound_processing())
        content_layout.addStretch(1)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)
        return container

    def _build_card_sound_processing(self) -> QFrame:
        card = QFrame()
        card.setProperty("class", "dashboard-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        self.lbl_card_sound_proc_title = QLabel(tr("settings.sound_processing_title"))
        self.lbl_card_sound_proc_title.setStyleSheet(f"color: {COLOR_TEXT_BRIGHT}; font-size: 14px; font-weight: 700;")
        layout.addWidget(self.lbl_card_sound_proc_title)

        self.lbl_card_sound_proc_desc = QLabel(tr("settings.sound_processing_desc"))
        self.lbl_card_sound_proc_desc.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        self.lbl_card_sound_proc_desc.setWordWrap(True)
        layout.addWidget(self.lbl_card_sound_proc_desc)

        self.chk_settings_replaygain = QCheckBox(tr("audio_tools.replaygain_enable"))
        self.chk_settings_replaygain.toggled.connect(self._on_settings_replaygain_toggled)
        layout.addWidget(self.chk_settings_replaygain)

        speed_row = QHBoxLayout()
        speed_row.setSpacing(12)
        self.lbl_settings_speed = QLabel(tr("audio_tools.playback_speed"))
        self.lbl_settings_speed.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 12.5px; font-weight: 500;")
        speed_row.addWidget(self.lbl_settings_speed)

        self.slider_settings_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_settings_speed.setRange(5, 20)
        self.slider_settings_speed.setMaximumWidth(240)
        self.slider_settings_speed.valueChanged.connect(self._on_settings_speed_changed)
        speed_row.addWidget(self.slider_settings_speed, 1)

        self.lbl_settings_speed_val = QLabel("1.0×")
        self.lbl_settings_speed_val.setMinimumWidth(40)
        self.lbl_settings_speed_val.setStyleSheet(f"color: {COLOR_PRIMARY_HOVER}; font-size: 12.5px; font-weight: 600;")
        speed_row.addWidget(self.lbl_settings_speed_val)

        self.btn_settings_speed_reset = QPushButton(tr("audio_tools.speed_reset"))
        self.btn_settings_speed_reset.setProperty("class", "secondary-btn")
        self.btn_settings_speed_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings_speed_reset.clicked.connect(lambda: self.slider_settings_speed.setValue(10))
        speed_row.addWidget(self.btn_settings_speed_reset)
        speed_row.addStretch()
        layout.addLayout(speed_row)

        self._sync_sound_processing_controls()
        return card

    def _sync_sound_processing_controls(self) -> None:
        if not hasattr(self, "chk_settings_replaygain"):
            return
        cfg = get_config_manager()
        is_buffer = cfg.get_audio_engine() == "buffer"
        self.chk_settings_replaygain.blockSignals(True)
        self.chk_settings_replaygain.setChecked(cfg.get_replaygain_enabled())
        self.chk_settings_replaygain.setEnabled(is_buffer)
        self.chk_settings_replaygain.blockSignals(False)

        rate = self.player_service.playback_rate() if getattr(self, "player_service", None) else 1.0
        self.slider_settings_speed.blockSignals(True)
        self.slider_settings_speed.setValue(int(round(rate * 10.0)))
        self.slider_settings_speed.setEnabled(is_buffer)
        self.slider_settings_speed.blockSignals(False)
        self.lbl_settings_speed_val.setText(f"{rate:.1f}×")
        self.btn_settings_speed_reset.setEnabled(is_buffer)

    def _on_settings_replaygain_toggled(self, checked: bool) -> None:
        if getattr(self, "player_service", None):
            self.player_service.set_replaygain_enabled(checked)

    def _on_settings_speed_changed(self, value: int) -> None:
        rate = value / 10.0
        self.lbl_settings_speed_val.setText(f"{rate:.1f}×")
        if getattr(self, "player_service", None):
            self.player_service.set_playback_rate(rate)
