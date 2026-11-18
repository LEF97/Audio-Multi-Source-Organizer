"""Popup à onglets d'outils audio rapides (sortie son, égaliseur, transitions, minuterie)."""

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
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from amso.core.config import get_config_manager
from amso.core.i18n import tr
from amso.services.audio_output import AUTO_DEVICE_ID
from amso.ui.styles import (
    COLOR_BG_CARD,
    COLOR_BG_HOVER,
    COLOR_BORDER,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_TEXT,
    COLOR_TEXT_BRIGHT,
    COLOR_TEXT_DISABLED,
    COLOR_TEXT_MUTED,
    crossfade_slider_qss,
)
from amso.ui.widgets.audio_tools_eq_tab import EqualizerTab
from amso.ui.widgets.common import AnchoredPopup

if TYPE_CHECKING:
    from amso.services.player_service import PlayerService

_POPUP_WIDTH = 370
_POPUP_QSS = f"""
    QFrame#AudioToolsPopup {{
        background-color: {COLOR_BG_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: 10px;
    }}
    QTabWidget::pane {{
        border: 1px solid {COLOR_BORDER};
        border-radius: 6px;
        background-color: {COLOR_BG_CARD};
        padding: 8px;
    }}
    QTabBar::tab {{
        background-color: transparent;
        color: {COLOR_TEXT_MUTED};
        padding: 6px 12px;
        border-bottom: 2px solid transparent;
        font-weight: 600;
        font-size: 12px;
    }}
    QTabBar::tab:selected {{
        color: {COLOR_TEXT_BRIGHT};
        border-bottom: 2px solid {COLOR_PRIMARY};
    }}
    QTabBar::tab:hover:!selected {{
        color: {COLOR_TEXT};
        background-color: {COLOR_BG_HOVER};
    }}
    QLabel {{
        color: {COLOR_TEXT};
        font-size: 12px;
    }}
    QLabel:disabled {{
        color: {COLOR_TEXT_DISABLED};
    }}
    QComboBox {{
        background-color: {COLOR_BG_HOVER};
        color: {COLOR_TEXT_BRIGHT};
        border: 1px solid {COLOR_BORDER};
        border-radius: 5px;
        padding: 4px 8px;
        font-size: 12px;
    }}
    QComboBox:hover {{
        border-color: {COLOR_PRIMARY_HOVER};
    }}
    QComboBox:disabled {{
        color: {COLOR_TEXT_MUTED};
    }}
"""


class AudioToolsPopup(AnchoredPopup):
    """Panneau flottant à onglets ancré au bouton d'outils audio du lecteur."""

    def __init__(self, player: PlayerService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("AudioToolsPopup")
        self.setFixedWidth(_POPUP_WIDTH)
        self.setStyleSheet(_POPUP_QSS)
        self._player = player
        self._syncing = False

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(6)

        self.tabs = QTabWidget(self)
        root.addWidget(self.tabs)

        self._tab_audio = QWidget()
        self._tab_eq = EqualizerTab(player, self)
        self._tab_playback = QWidget()

        self._build_audio_tab()
        self._build_playback_tab()

        self.tabs.addTab(self._tab_audio, tr("audio_tools.tab_audio"))
        self.tabs.addTab(self._tab_eq, tr("audio_tools.tab_eq"))
        self.tabs.addTab(self._tab_playback, tr("audio_tools.tab_playback"))

        self._player.audio_outputs_changed.connect(self._refresh_output_devices)
        self._player.sleep_timer_changed.connect(self._on_sleep_timer_tick)

    def _build_audio_tab(self) -> None:
        layout = QVBoxLayout(self._tab_audio)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(10)

        self.lbl_output_device = QLabel(tr("audio_tools.output_device"))
        layout.addWidget(self.lbl_output_device)

        row = QHBoxLayout()
        row.setSpacing(6)
        self.combo_output_device = QComboBox()
        self.combo_output_device.currentIndexChanged.connect(self._on_output_device_selected)
        row.addWidget(self.combo_output_device, 1)

        self.btn_refresh_devices = QPushButton("🔄")
        self.btn_refresh_devices.setFixedSize(28, 28)
        self.btn_refresh_devices.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh_devices.setToolTip(tr("common.refresh"))
        self.btn_refresh_devices.clicked.connect(self._refresh_output_devices)
        row.addWidget(self.btn_refresh_devices)
        layout.addLayout(row)

        self.chk_replaygain = QCheckBox(tr("audio_tools.replaygain_enable"))
        self.chk_replaygain.toggled.connect(self._on_replaygain_toggled)
        layout.addWidget(self.chk_replaygain)

        self.lbl_speed = QLabel(tr("audio_tools.playback_speed"))
        layout.addWidget(self.lbl_speed)

        speed_row = QHBoxLayout()
        speed_row.setSpacing(6)
        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setRange(5, 20)  # 0.5x à 2.0x par pas de 0.1x
        self.slider_speed.setValue(10)
        self.slider_speed.valueChanged.connect(self._on_speed_changed)
        speed_row.addWidget(self.slider_speed, 1)

        self.lbl_speed_val = QLabel("1.0×")
        self.lbl_speed_val.setMinimumWidth(36)
        self.lbl_speed_val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        speed_row.addWidget(self.lbl_speed_val)

        self.btn_speed_reset = QPushButton(tr("audio_tools.speed_reset"))
        self.btn_speed_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_speed_reset.clicked.connect(lambda: self.slider_speed.setValue(10))
        speed_row.addWidget(self.btn_speed_reset)
        layout.addLayout(speed_row)

        self.lbl_buffer_only_hint = QLabel(tr("audio_tools.buffer_only_hint"))
        self.lbl_buffer_only_hint.setWordWrap(True)
        self.lbl_buffer_only_hint.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px;")
        layout.addWidget(self.lbl_buffer_only_hint)
        layout.addStretch(1)

    def _build_playback_tab(self) -> None:
        layout = QVBoxLayout(self._tab_playback)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(10)

        self.lbl_audio_engine = QLabel(tr("audio_tools.audio_engine"))
        layout.addWidget(self.lbl_audio_engine)

        self.combo_engine = QComboBox()
        self.combo_engine.addItem(tr("audio_tools.engine_buffer"), "buffer")
        self.combo_engine.addItem(tr("audio_tools.engine_vlc_direct"), "vlc_direct")
        self.combo_engine.currentIndexChanged.connect(self._on_audio_engine_changed)
        layout.addWidget(self.combo_engine)

        self.lbl_transition_mode = QLabel(tr("audio_tools.transition_mode"))
        layout.addWidget(self.lbl_transition_mode)

        self.combo_transition = QComboBox()
        self.combo_transition.addItem(tr("audio_tools.transition_standard"), "standard")
        self.combo_transition.addItem(tr("audio_tools.transition_gapless"), "gapless")
        self.combo_transition.addItem(tr("audio_tools.transition_crossfade"), "crossfade")
        self.combo_transition.currentIndexChanged.connect(self._on_transition_changed)
        layout.addWidget(self.combo_transition)

        cf_row = QHBoxLayout()
        cf_row.setSpacing(8)
        self.lbl_crossfade_dur = QLabel(tr("settings.crossfade_duration"))
        cf_row.addWidget(self.lbl_crossfade_dur)

        self.slider_crossfade = QSlider(Qt.Orientation.Horizontal)
        self.slider_crossfade.setRange(1, 12)
        self.slider_crossfade.setStyleSheet(crossfade_slider_qss())
        self.slider_crossfade.valueChanged.connect(self._on_crossfade_duration_changed)
        cf_row.addWidget(self.slider_crossfade, 1)

        self.lbl_crossfade_val = QLabel("3 s")
        self.lbl_crossfade_val.setMinimumWidth(36)
        self.lbl_crossfade_val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        cf_row.addWidget(self.lbl_crossfade_val)
        layout.addLayout(cf_row)

        self.lbl_sleep_timer = QLabel(tr("audio_tools.sleep_timer"))
        layout.addWidget(self.lbl_sleep_timer)

        sleep_row = QHBoxLayout()
        sleep_row.setSpacing(8)
        self.combo_sleep_timer = QComboBox()
        for key in ("off", "15m", "30m", "45m", "60m", "end_of_track", "end_of_queue"):
            self.combo_sleep_timer.addItem(tr(f"audio_tools.sleep_{key}"), key)
        self.combo_sleep_timer.currentIndexChanged.connect(self._on_sleep_timer_selected)
        sleep_row.addWidget(self.combo_sleep_timer, 1)

        self.lbl_sleep_remaining = QLabel("")
        self.lbl_sleep_remaining.setMinimumWidth(46)
        self.lbl_sleep_remaining.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_sleep_remaining.setStyleSheet(f"color: {COLOR_PRIMARY_HOVER}; font-weight: 600;")
        sleep_row.addWidget(self.lbl_sleep_remaining)
        layout.addLayout(sleep_row)
        layout.addStretch(1)

    def _before_show(self) -> None:
        self.sync_from_state()

    def sync_from_state(self) -> None:
        """Recharge les valeurs depuis ConfigManager et PlayerService."""
        self._syncing = True
        try:
            cfg = get_config_manager()
            is_buffer = cfg.get_audio_engine() == "buffer"
            eng_idx = self.combo_engine.findData("buffer" if is_buffer else "vlc_direct")
            if eng_idx >= 0:
                self.combo_engine.setCurrentIndex(eng_idx)
            self._populate_output_devices()
            self.chk_replaygain.setChecked(cfg.get_replaygain_enabled())
            rate = self._player.playback_rate()
            self.slider_speed.setValue(int(round(rate * 10.0)))
            self.lbl_speed_val.setText(f"{rate:.1f}×")
            self._update_buffer_controls_state(is_buffer)

            mode = cfg.get_transition_mode()
            idx = self.combo_transition.findData(mode)
            if idx >= 0:
                self.combo_transition.setCurrentIndex(idx)
            cf_sec = cfg.get_crossfade_duration()
            self.slider_crossfade.setValue(cf_sec)
            self.lbl_crossfade_val.setText(f"{cf_sec} s")
            self._update_crossfade_enabled(mode == "crossfade")

            sleep_mode, sleep_rem = self._player.sleep_timer_state()
            s_idx = self.combo_sleep_timer.findData(sleep_mode)
            if s_idx >= 0:
                self.combo_sleep_timer.setCurrentIndex(s_idx)
            self._format_sleep_remaining(sleep_rem)
        finally:
            self._syncing = False

    def _populate_output_devices(self) -> None:
        current_id = self._player.current_audio_output_device()
        self.combo_output_device.clear()
        self.combo_output_device.addItem(tr("audio_tools.output_auto"), AUTO_DEVICE_ID)
        for dev_id, label in self._player.audio_output_devices():
            self.combo_output_device.addItem(label, dev_id)
        idx = self.combo_output_device.findData(current_id)
        self.combo_output_device.setCurrentIndex(idx if idx >= 0 else 0)

    def _refresh_output_devices(self) -> None:
        self._syncing = True
        try:
            self._populate_output_devices()
        finally:
            self._syncing = False

    def _on_output_device_selected(self, index: int) -> None:
        if self._syncing or index < 0:
            return
        dev_id = self.combo_output_device.itemData(index)
        if isinstance(dev_id, str):
            self._player.set_audio_output_device(dev_id)

    def _on_replaygain_toggled(self, checked: bool) -> None:
        if not self._syncing:
            self._player.set_replaygain_enabled(checked)

    def _on_speed_changed(self, value: int) -> None:
        rate = value / 10.0
        self.lbl_speed_val.setText(f"{rate:.1f}×")
        if not self._syncing:
            self._player.set_playback_rate(rate)

    def _on_sleep_timer_selected(self, index: int) -> None:
        if self._syncing or index < 0:
            return
        mode = self.combo_sleep_timer.itemData(index)
        if isinstance(mode, str):
            self._player.set_sleep_timer(mode)

    def _on_sleep_timer_tick(self, mode: str, remaining_s: int) -> None:
        self._format_sleep_remaining(remaining_s)
        if not self._syncing:
            self._syncing = True
            try:
                idx = self.combo_sleep_timer.findData(mode)
                if idx >= 0:
                    self.combo_sleep_timer.setCurrentIndex(idx)
            finally:
                self._syncing = False

    def _format_sleep_remaining(self, remaining_s: int) -> None:
        if remaining_s <= 0:
            self.lbl_sleep_remaining.setText("")
            return
        mins, secs = divmod(remaining_s, 60)
        self.lbl_sleep_remaining.setText(f"{mins:02d}:{secs:02d}")

    def _update_buffer_controls_state(self, is_buffer: bool) -> None:
        self.combo_output_device.setEnabled(is_buffer)
        self.btn_refresh_devices.setEnabled(is_buffer)
        self.chk_replaygain.setEnabled(is_buffer)
        self.slider_speed.setEnabled(is_buffer)
        self.btn_speed_reset.setEnabled(is_buffer)
        self.lbl_buffer_only_hint.setVisible(not is_buffer)
        self._tab_eq.sync_from_state(is_buffer)

    def _on_audio_engine_changed(self, index: int) -> None:
        if self._syncing or index < 0:
            return
        new_engine = self.combo_engine.itemData(index)
        if not isinstance(new_engine, str):
            return
        cfg = get_config_manager()
        old_engine = cfg.get_audio_engine()
        cfg.set_audio_engine(new_engine)
        self._update_buffer_controls_state(new_engine == "buffer")
        if new_engine != old_engine:
            self._player.reset_playback()

    def _on_transition_changed(self, index: int) -> None:
        if self._syncing or index < 0:
            return
        new_mode = self.combo_transition.itemData(index)
        if not isinstance(new_mode, str):
            return
        cfg = get_config_manager()
        old_mode = cfg.get_transition_mode()
        cfg.set_transition_mode(new_mode)
        self._update_crossfade_enabled(new_mode == "crossfade")
        if new_mode != old_mode:
            self._player.reset_playback()

    def _on_crossfade_duration_changed(self, value: int) -> None:
        self.lbl_crossfade_val.setText(f"{value} s")
        if not self._syncing:
            get_config_manager().set_crossfade_duration(value)

    def _update_crossfade_enabled(self, enabled: bool) -> None:
        self.lbl_crossfade_dur.setEnabled(enabled)
        self.slider_crossfade.setEnabled(enabled)
        self.lbl_crossfade_val.setEnabled(enabled)

    def retranslate_ui(self) -> None:
        """Met à jour les libellés de la popup selon la langue active."""
        self.tabs.setTabText(0, tr("audio_tools.tab_audio"))
        self.tabs.setTabText(1, tr("audio_tools.tab_eq"))
        self.tabs.setTabText(2, tr("audio_tools.tab_playback"))
        self.lbl_output_device.setText(tr("audio_tools.output_device"))
        self.btn_refresh_devices.setToolTip(tr("common.refresh"))
        self.chk_replaygain.setText(tr("audio_tools.replaygain_enable"))
        self.lbl_speed.setText(tr("audio_tools.playback_speed"))
        self.btn_speed_reset.setText(tr("audio_tools.speed_reset"))
        self.lbl_buffer_only_hint.setText(tr("audio_tools.buffer_only_hint"))
        self._tab_eq.retranslate_ui()
        self.lbl_audio_engine.setText(tr("audio_tools.audio_engine"))
        self.combo_engine.setItemText(0, tr("audio_tools.engine_buffer"))
        self.combo_engine.setItemText(1, tr("audio_tools.engine_vlc_direct"))
        self.lbl_transition_mode.setText(tr("audio_tools.transition_mode"))
        self.combo_transition.setItemText(0, tr("audio_tools.transition_standard"))
        self.combo_transition.setItemText(1, tr("audio_tools.transition_gapless"))
        self.combo_transition.setItemText(2, tr("audio_tools.transition_crossfade"))
        self.lbl_crossfade_dur.setText(tr("settings.crossfade_duration"))
        self.lbl_sleep_timer.setText(tr("audio_tools.sleep_timer"))
        for i in range(self.combo_sleep_timer.count()):
            key = self.combo_sleep_timer.itemData(i)
            if isinstance(key, str):
                self.combo_sleep_timer.setItemText(i, tr(f"audio_tools.sleep_{key}"))
        self._refresh_output_devices()
