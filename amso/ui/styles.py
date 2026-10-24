"""QSS partagés des boutons de transport (lecteur, playlist, blind test)."""

from __future__ import annotations

from PySide6.QtWidgets import QPushButton

# Couleurs partagées du thème sombre
COLOR_PRIMARY = "#0284C7"
COLOR_PRIMARY_HOVER = "#38BDF8"
COLOR_BG_CARD = "#20242D"
COLOR_BG_HOVER = "#2B303C"
COLOR_BORDER = "#282C37"
COLOR_TEXT = "#CBD5E1"
COLOR_TEXT_BRIGHT = "#F8FAFC"
COLOR_TEXT_MUTED = "#94A3B8"


def icon_button_qss(radius: int = 6, font_size: int = 14) -> str:
    """QSS d'un petit bouton-icône (état normal, survol, appui)."""
    return f"""
        QPushButton {{
            background-color: {COLOR_BG_CARD};
            color: {COLOR_TEXT};
            border: 1px solid {COLOR_BORDER};
            border-radius: {radius}px;
            font-size: {font_size}px;
        }}
        QPushButton:hover {{
            background-color: {COLOR_BG_HOVER};
            color: {COLOR_TEXT_BRIGHT};
            border-color: {COLOR_PRIMARY_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {COLOR_PRIMARY};
            color: #FFFFFF;
        }}
    """


def active_button_qss(radius: int = 6, font_size: int = 14) -> str:
    """QSS d'un bouton-icône à l'état actif (aléatoire, répétition)."""
    return f"""
        background-color: {COLOR_PRIMARY};
        color: #FFFFFF;
        border: 1px solid {COLOR_PRIMARY_HOVER};
        border-radius: {radius}px;
        font-size: {font_size}px;
    """


def style_icon_button(btn: QPushButton, radius: int = 6, font_size: int = 14) -> None:
    """Applique le style bouton-icône standard."""
    btn.setStyleSheet(icon_button_qss(radius, font_size))


def volume_slider_qss(groove_height: int = 5, handle_size: int = 12) -> str:
    """QSS du curseur de volume."""
    radius = groove_height // 2
    handle_radius = handle_size // 2
    margin_top = -(handle_size - groove_height) // 2
    return f"""
        QSlider::groove:horizontal {{
            height: {groove_height}px;
            background-color: {COLOR_BORDER};
            border-radius: {radius}px;
        }}
        QSlider::sub-page:horizontal {{
            background-color: {COLOR_PRIMARY_HOVER};
            border-radius: {radius}px;
        }}
        QSlider::handle:horizontal {{
            background-color: #E2E8F0;
            width: {handle_size}px;
            height: {handle_size}px;
            margin: {margin_top}px 0;
            border-radius: {handle_radius}px;
        }}
        QSlider::handle:horizontal:hover {{
            background-color: {COLOR_PRIMARY_HOVER};
        }}
    """


def seek_slider_qss(groove_height: int = 6, handle_size: int = 14) -> str:
    """QSS du curseur de position (seekbar)."""
    radius = groove_height // 2
    handle_radius = handle_size // 2
    margin_top = -(handle_size - groove_height) // 2
    return f"""
        QSlider::groove:horizontal {{
            height: {groove_height}px;
            background-color: {COLOR_BORDER};
            border-radius: {radius}px;
        }}
        QSlider::sub-page:horizontal {{
            background-color: {COLOR_PRIMARY};
            border-radius: {radius}px;
        }}
        QSlider::handle:horizontal {{
            background-color: #FFFFFF;
            width: {handle_size}px;
            height: {handle_size}px;
            margin: {margin_top}px 0;
            border-radius: {handle_radius}px;
        }}
        QSlider::handle:horizontal:hover {{
            background-color: {COLOR_PRIMARY_HOVER};
        }}
    """


def volume_label_qss(min_width: int = 38) -> str:
    """QSS du label de volume en pourcentage."""
    return f"color: {COLOR_TEXT_MUTED}; font-size: 12px; min-width: {min_width}px;"


def effects_combo_qss() -> str:
    """QSS pour le sélecteur déroulant des effets visuels."""
    return f"""
        QComboBox {{
            background-color: {COLOR_BG_CARD};
            color: {COLOR_TEXT_BRIGHT};
            border: 1px solid {COLOR_PRIMARY_HOVER};
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: 500;
        }}
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        QComboBox QAbstractItemView {{
            background-color: #1A1D24;
            color: {COLOR_TEXT_BRIGHT};
            selection-background-color: {COLOR_PRIMARY};
            selection-color: #FFFFFF;
            border: 1px solid {COLOR_BORDER};
            border-radius: 6px;
            outline: none;
        }}
    """


def settings_radio_qss() -> str:
    """Feuille de style QSS pour les boutons radio des pages de paramètres."""
    return f"""
        QRadioButton {{
            color: {COLOR_TEXT_BRIGHT};
            font-size: 13.5px;
            font-weight: 600;
            spacing: 8px;
        }}
        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 1px solid #333846;
            background-color: #121418;
        }}
        QRadioButton::indicator:hover {{
            border-color: {COLOR_PRIMARY_HOVER};
        }}
        QRadioButton::indicator:checked {{
            background-color: {COLOR_PRIMARY};
            border-color: {COLOR_PRIMARY_HOVER};
        }}
    """
