"""Thème et styles QSS modernes pour l'interface PySide6 d'AMSO.

Ce module réexporte la feuille de styles DARK_THEME_QSS ainsi que les fonctions
d'accès aux ressources graphiques pour assurer la compatibilité ascendante.
"""

from __future__ import annotations

from amso.ui.qss_base import BASE_DARK_QSS
from amso.ui.qss_components import COMPONENTS_DARK_QSS
from amso.ui.resources import get_app_icon, get_app_logo_pixmap, get_resource_path

DARK_THEME_QSS = f"{BASE_DARK_QSS}\n{COMPONENTS_DARK_QSS}"

__all__ = [
    "DARK_THEME_QSS",
    "get_app_icon",
    "get_app_logo_pixmap",
    "get_resource_path",
]
