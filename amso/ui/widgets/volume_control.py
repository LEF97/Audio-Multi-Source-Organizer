"""Contrôle de volume (bouton muet, curseur, pourcentage) partagé par le lecteur et le Blind Test."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from amso.ui.styles import style_icon_button, volume_label_qss, volume_slider_qss
from amso.ui.widgets.common import ClickableSlider


class VolumeControl(QWidget):
    """Les trois widgets restent accessibles pour que les vues branchent leurs propres signaux."""

    def __init__(self, volume: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.btn_mute = QPushButton("🔊")
        self.btn_mute.setFixedSize(30, 30)
        self.btn_mute.setCursor(Qt.CursorShape.PointingHandCursor)
        style_icon_button(self.btn_mute, radius=6, font_size=13)
        layout.addWidget(self.btn_mute)

        self.slider = ClickableSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(volume)
        self.slider.setFixedWidth(120)
        self.slider.setFixedHeight(22)
        self.slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider.setStyleSheet(volume_slider_qss(groove_height=5, handle_size=12))
        layout.addWidget(self.slider)

        self.lbl_percent = QLabel(f"{volume}%")
        self.lbl_percent.setStyleSheet(volume_label_qss(min_width=38))
        layout.addWidget(self.lbl_percent)
