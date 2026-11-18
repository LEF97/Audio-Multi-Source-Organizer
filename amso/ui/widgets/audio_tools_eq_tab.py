"""Onglet Égaliseur 10 bandes de la popup d'outils audio."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from amso.core.config import get_config_manager
from amso.core.dsp_equalizer import EQ_FREQUENCIES, EQ_PRESETS
from amso.core.i18n import tr
from amso.ui.styles import COLOR_TEXT_MUTED

if TYPE_CHECKING:
    from amso.services.player_service import PlayerService

_FREQ_LABELS = ("32", "64", "125", "250", "500", "1k", "2k", "4k", "8k", "16k")


class EqualizerTab(QWidget):
    """Panneau égaliseur 10 bandes avec présets et activation en temps réel."""

    def __init__(self, player: PlayerService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._player = player
        self._syncing = False
        self._sliders: list[QSlider] = []
        self._val_labels: list[QLabel] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(8)

        top = QHBoxLayout()
        top.setSpacing(6)
        self.chk_enabled = QCheckBox(tr("audio_tools.eq_enable"))
        self.chk_enabled.toggled.connect(self._on_controls_changed)
        top.addWidget(self.chk_enabled)
        top.addStretch(1)

        self.combo_preset = QComboBox()
        for key in EQ_PRESETS:
            self.combo_preset.addItem(tr(f"audio_tools.eq_preset_{key}"), key)
        self.combo_preset.addItem(tr("audio_tools.eq_preset_custom"), "custom")
        self.combo_preset.currentIndexChanged.connect(self._on_preset_selected)
        top.addWidget(self.combo_preset)

        self.btn_reset = QPushButton(tr("audio_tools.eq_reset"))
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self._on_reset_clicked)
        top.addWidget(self.btn_reset)
        root.addLayout(top)

        bands_row = QHBoxLayout()
        bands_row.setSpacing(4)
        for idx, freq_label in enumerate(_FREQ_LABELS):
            col = QVBoxLayout()
            col.setSpacing(2)
            col.setAlignment(Qt.AlignmentFlag.AlignCenter)

            lbl_val = QLabel("0")
            lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_val.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 10px;")
            col.addWidget(lbl_val)

            slider = QSlider(Qt.Orientation.Vertical)
            slider.setRange(-24, 24)  # pas de 0.5 dB (-12 à +12 dB)
            slider.setValue(0)
            slider.setMinimumHeight(110)
            slider.setToolTip(f"{EQ_FREQUENCIES[idx]} Hz")
            slider.valueChanged.connect(self._on_band_changed)
            col.addWidget(slider, 1, Qt.AlignmentFlag.AlignHCenter)

            lbl_freq = QLabel(freq_label)
            lbl_freq.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_freq.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 10px;")
            col.addWidget(lbl_freq)

            self._sliders.append(slider)
            self._val_labels.append(lbl_val)
            bands_row.addLayout(col)

        root.addLayout(bands_row)

    def sync_from_state(self, is_buffer: bool) -> None:
        self._syncing = True
        try:
            cfg = get_config_manager()
            self.setEnabled(is_buffer)
            self.chk_enabled.setChecked(cfg.get_eq_enabled())
            preset = cfg.get_eq_preset()
            idx = self.combo_preset.findData(preset)
            self.combo_preset.setCurrentIndex(idx if idx >= 0 else self.combo_preset.count() - 1)
            bands = cfg.get_eq_bands()
            for i, gain in enumerate(bands):
                self._sliders[i].setValue(int(round(gain * 2.0)))
                self._val_labels[i].setText(f"{gain:+.0f}" if abs(gain) >= 0.5 else "0")
            self._update_sliders_enabled()
        finally:
            self._syncing = False

    def _update_sliders_enabled(self) -> None:
        enabled = self.chk_enabled.isChecked()
        self.combo_preset.setEnabled(enabled)
        self.btn_reset.setEnabled(enabled)
        for slider in self._sliders:
            slider.setEnabled(enabled)

    def _current_bands(self) -> list[float]:
        return [s.value() / 2.0 for s in self._sliders]

    def _apply_to_player(self) -> None:
        preset = self.combo_preset.currentData()
        preset_str = preset if isinstance(preset, str) else "custom"
        self._player.set_equalizer(self.chk_enabled.isChecked(), preset_str, self._current_bands())

    def _on_controls_changed(self) -> None:
        self._update_sliders_enabled()
        if not self._syncing:
            self._apply_to_player()

    def _on_preset_selected(self, index: int) -> None:
        if self._syncing or index < 0:
            return
        key = self.combo_preset.itemData(index)
        if isinstance(key, str) and key in EQ_PRESETS:
            self._syncing = True
            try:
                for i, gain in enumerate(EQ_PRESETS[key]):
                    self._sliders[i].setValue(int(round(gain * 2.0)))
                    self._val_labels[i].setText(f"{gain:+.0f}" if abs(gain) >= 0.5 else "0")
            finally:
                self._syncing = False
            self._apply_to_player()

    def _on_band_changed(self) -> None:
        for slider, lbl in zip(self._sliders, self._val_labels, strict=True):
            gain = slider.value() / 2.0
            lbl.setText(f"{gain:+.0f}" if abs(gain) >= 0.5 else "0")
        if self._syncing:
            return
        self._syncing = True
        try:
            custom_idx = self.combo_preset.findData("custom")
            if custom_idx >= 0:
                self.combo_preset.setCurrentIndex(custom_idx)
        finally:
            self._syncing = False
        self._apply_to_player()

    def _on_reset_clicked(self) -> None:
        flat_idx = self.combo_preset.findData("flat")
        if flat_idx >= 0:
            self.combo_preset.setCurrentIndex(flat_idx)
        else:
            self._syncing = True
            try:
                for slider, lbl in zip(self._sliders, self._val_labels, strict=True):
                    slider.setValue(0)
                    lbl.setText("0")
            finally:
                self._syncing = False
            self._apply_to_player()

    def retranslate_ui(self) -> None:
        self.chk_enabled.setText(tr("audio_tools.eq_enable"))
        self.btn_reset.setText(tr("audio_tools.eq_reset"))
        for i in range(self.combo_preset.count()):
            key = self.combo_preset.itemData(i)
            if isinstance(key, str):
                self.combo_preset.setItemText(i, tr(f"audio_tools.eq_preset_{key}"))
