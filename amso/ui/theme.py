"""Thème et styles QSS modernes pour l'interface PySide6 d'AMSO."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon, QPixmap

DARK_THEME_QSS = """
/* =========================================================================
   AMSO - Modern Dark Palette
   ========================================================================= */

QMainWindow, QDialog, QWidget#centralWidget {
    background-color: #121418;
    color: #E2E8F0;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Roboto", sans-serif;
    font-size: 13px;
}

QDialog QLabel {
    color: #E2E8F0;
}

/* --- Barre latérale (Sidebar) --- */
QFrame#sidebarFrame {
    background-color: #1A1D24;
    border-right: 1px solid #282C37;
    min-width: 170px;
    max-width: 320px;
}

QLabel#appLogoLabel {
    color: #38BDF8;
    font-size: 16px;
    font-weight: 700;
    padding: 18px 16px;
    letter-spacing: 0.5px;
}

QLabel#sidebarLogo {
    background: transparent;
    padding: 2px;
    border-radius: 16px;
}

QLabel#sidebarLogo:hover {
    background-color: rgba(56, 189, 248, 0.08);
}

QPushButton.nav-btn {
    background-color: transparent;
    color: #94A3B8;
    text-align: left;
    padding: 10px 16px;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    margin: 2px 8px;
}

QPushButton.nav-btn:hover {
    background-color: #242833;
    color: #F8FAFC;
}

QPushButton.nav-btn:checked {
    background-color: #0284C7;
    color: #FFFFFF;
    font-weight: 600;
}

/* --- Barre supérieure d'outils --- */
QFrame#topBarFrame {
    background-color: #16181F;
    border-bottom: 1px solid #282C37;
    max-height: 52px;
}

QLineEdit#searchEdit, QLineEdit#folderSearchEdit {
    background-color: #20242D;
    color: #F8FAFC;
    border: 1px solid #333846;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
}

QLineEdit#searchEdit {
    min-width: 260px;
}

QLineEdit#folderSearchEdit {
    max-width: 220px;
}

QLineEdit#searchEdit:focus, QLineEdit#folderSearchEdit:focus {
    border: 1px solid #38BDF8;
    background-color: #262B36;
}

QLabel#folderBreadcrumbLabel {
    color: #38BDF8;
    font-size: 12px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 6px;
    background-color: rgba(56, 189, 248, 0.08);
    border: 1px solid rgba(56, 189, 248, 0.2);
}

QLabel#folderBreadcrumbLabel:hover {
    color: #7DD3FC;
    background-color: rgba(56, 189, 248, 0.18);
    border: 1px solid rgba(56, 189, 248, 0.45);
    text-decoration: underline;
}

QPushButton.primary-btn {
    background-color: #0284C7;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton.primary-btn:hover {
    background-color: #0369A1;
}

QPushButton.primary-btn:pressed {
    background-color: #075985;
}

QPushButton.secondary-btn {
    background-color: #242833;
    color: #E2E8F0;
    border: 1px solid #333846;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 500;
}

QPushButton.secondary-btn:hover {
    background-color: #2E3341;
    border-color: #475569;
}

/* --- Tableau des pistes (QTableView Virtualisé) --- */
QTableView {
    background-color: #121418;
    alternate-background-color: #161920;
    color: #E2E8F0;
    gridline-color: #1E222B;
    border: none;
    selection-background-color: #0C4A6E;
    selection-color: #F0F9FF;
    font-size: 12.5px;
}

QTableView::item {
    padding: 6px 10px;
    border: none;
}

QTableView::item:hover {
    background-color: #1E232E;
}

QTableView::item:selected {
    background-color: #0369A1;
    color: #FFFFFF;
}

QHeaderView::section {
    background-color: #1A1D24;
    color: #94A3B8;
    font-size: 11.5px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid #282C37;
    border-right: 1px solid #20242E;
}

QHeaderView::section:hover {
    background-color: #242833;
    color: #F8FAFC;
}

/* --- Barre de défilement (QScrollBar) --- */
QScrollBar:vertical {
    background-color: #121418;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #2E3341;
    min-height: 24px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* --- Barre de progression & Barre d'état --- */
QStatusBar {
    background-color: #16181F;
    color: #94A3B8;
    border-top: 1px solid #282C37;
    font-size: 12px;
    padding: 4px 12px;
}

QProgressBar {
    border: 1px solid #333846;
    border-radius: 4px;
    background-color: #1A1D24;
    text-align: center;
    color: #F8FAFC;
    font-size: 11px;
    height: 14px;
    max-width: 220px;
}

QProgressBar::chunk {
    background-color: #0284C7;
    border-radius: 3px;
}

/* --- Sélecteur de langue (QComboBox) --- */
QComboBox#langComboBox {
    background-color: #20242D;
    color: #F8FAFC;
    border: 1px solid #333846;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
    min-height: 20px;
}

QComboBox#langComboBox:hover {
    border-color: #38BDF8;
    background-color: #242833;
}

QComboBox#langComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox#langComboBox QAbstractItemView {
    background-color: #1A1D24;
    color: #F8FAFC;
    selection-background-color: #0284C7;
    selection-color: #FFFFFF;
    border: 1px solid #333846;
    border-radius: 4px;
    padding: 4px;
    outline: none;
}

/* --- En-têtes de tiroirs pliables (Drawer Header) --- */
QPushButton.drawer-header {
    background-color: transparent;
    color: #64748B;
    text-align: left;
    padding: 6px 8px;
    border: none;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-top: 4px;
}

QPushButton.drawer-header:hover {
    background-color: #20242E;
    color: #94A3B8;
}

/* --- Cartes de tableau de bord (Dashboard / Statistiques / Paramètres) --- */
QFrame.dashboard-card {
    background-color: #1A1D24;
    border: 1px solid #282C37;
    border-radius: 8px;
}

QFrame.dashboard-card:hover {
    border-color: #38BDF8;
}

/* --- Arborescence de dossiers (QTreeWidget / QTreeView) --- */
QTreeWidget, QTreeView {
    background-color: #16181F;
    color: #E2E8F0;
    border: 1px solid #282C37;
    border-radius: 6px;
    outline: none;
    font-size: 12.5px;
}

QTreeWidget::item, QTreeView::item {
    padding: 5px 8px;
    border-radius: 4px;
    margin: 1px 4px;
}

QTreeWidget::item:hover, QTreeView::item:hover {
    background-color: #242833;
    color: #F8FAFC;
}

QTreeWidget::item:selected, QTreeView::item:selected {
    background-color: #0284C7;
    color: #FFFFFF;
}

/* --- Cases à cocher modernes (QCheckBox) --- */
QCheckBox {
    color: #E2E8F0;
    font-size: 12.5px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #475569;
    border-radius: 3px;
    background-color: #20242D;
}

QCheckBox::indicator:hover {
    border-color: #38BDF8;
}

QCheckBox::indicator:checked {
    background-color: #0284C7;
    border-color: #38BDF8;
}

/* --- Formulaires génériques & Boîtes de dialogue (QLineEdit, QComboBox, QSpinBox) --- */
QLineEdit {
    background-color: #20242D;
    color: #F8FAFC;
    border: 1px solid #333846;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
}

QLineEdit:focus {
    border: 1px solid #38BDF8;
    background-color: #262B36;
}

QLineEdit:read-only {
    background-color: #16181F;
    color: #94A3B8;
    border-color: #282C37;
}

QComboBox {
    background-color: #20242D;
    color: #F8FAFC;
    border: 1px solid #333846;
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 12.5px;
    min-height: 22px;
}

QComboBox:hover {
    border-color: #38BDF8;
    background-color: #242833;
}

QComboBox:focus {
    border-color: #38BDF8;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #282C37;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #94A3B8;
    width: 0;
    height: 0;
}

QComboBox::down-arrow:hover {
    border-top-color: #38BDF8;
}

QComboBox QAbstractItemView {
    background-color: #1E293B;
    color: #F8FAFC;
    selection-background-color: #0284C7;
    selection-color: #FFFFFF;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 4px;
    outline: none;
}

QSpinBox {
    background-color: #20242D;
    color: #F8FAFC;
    border: 1px solid #333846;
    border-radius: 6px;
    padding: 5px 8px;
    font-size: 13px;
}

QSpinBox:focus {
    border: 1px solid #38BDF8;
    background-color: #262B36;
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #282C37;
    border: none;
    width: 18px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #0284C7;
}

/* --- Tableaux QTableWidget --- */
QTableWidget {
    background-color: #16181F;
    alternate-background-color: #1A1D24;
    color: #E2E8F0;
    border: 1px solid #282C37;
    border-radius: 6px;
    gridline-color: transparent;
    outline: none;
    font-size: 12.5px;
}

QTableWidget::item {
    padding: 4px 8px;
    border-bottom: 1px solid #1E222B;
}

QTableWidget::item:selected {
    background-color: #0284C7;
    color: #FFFFFF;
}

/* --- Menus contextuels (QMenu) --- */
QMenu {
    background-color: #1A1D24;
    color: #F8FAFC;
    border: 1px solid #333846;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    background-color: transparent;
    padding: 6px 20px 6px 10px;
    border-radius: 4px;
    font-size: 13px;
    color: #E2E8F0;
}

QMenu::item:selected {
    background-color: #0284C7;
    color: #FFFFFF;
}

QMenu::item:disabled {
    color: #64748B;
}

QMenu::separator {
    height: 1px;
    background-color: #282C37;
    margin: 4px 6px;
}

/* --- Curseur de défilement (QSlider) pour Lecteur & Volume --- */
QSlider::groove:horizontal {
    height: 6px;
    background-color: #282C37;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background-color: #0284C7;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background-color: #F8FAFC;
    width: 14px;
    height: 14px;
    margin: -4px 0;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background-color: #38BDF8;
}
"""


def get_resource_path(relative_name: str) -> Path:
    """Retourne le chemin absolu d'une ressource embarquée (gère l'exécution dev et PyInstaller)."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_name

    root_dir = Path(__file__).resolve().parent.parent.parent  # racine du projet
    amso_dir = Path(__file__).resolve().parent.parent  # amso/

    # Si le fichier est présent à la fois à la racine et dans amso/resources, prendre le plus récent
    root_file = root_dir / relative_name
    res_file = amso_dir / "resources" / relative_name

    if root_file.exists() and res_file.exists():
        try:
            if root_file.stat().st_mtime >= res_file.stat().st_mtime:
                return root_file
            return res_file
        except OSError:
            pass

    candidates = [
        root_file,
        res_file,
        root_dir / "resources" / relative_name,
        amso_dir / relative_name,
    ]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def get_app_icon() -> QIcon:
    """Retourne l'icône officielle de l'application AMSO adaptée à l'OS (Windows .ico, macOS .icns, Linux .png)."""
    icon = QIcon()
    if sys.platform == "darwin":
        icns_path = get_resource_path("icon.icns")
        if icns_path.exists():
            icon.addFile(str(icns_path))
    elif sys.platform == "win32":
        ico_path = get_resource_path("icon.ico")
        if ico_path.exists():
            icon.addFile(str(ico_path))

    # PNG universel haute définition (indispensable pour Linux X11/Wayland et repli tous OS)
    for name in ["AMSO.png", "icon.png"]:
        png_path = get_resource_path(name)
        if png_path.exists():
            icon.addFile(str(png_path))
            break

    # Repli final
    if icon.isNull():
        ico_path = get_resource_path("icon.ico")
        if ico_path.exists():
            icon.addFile(str(ico_path))

    return icon


def get_app_logo_pixmap() -> QPixmap:
    """Retourne le logo / icône sous forme de QPixmap haute définition."""
    for name in ["AMSO.png", "icon.png", "logo.png"]:
        p = get_resource_path(name)
        if p.exists():
            pm = QPixmap(str(p))
            if not pm.isNull():
                return pm
    ico_path = get_resource_path("icon.ico")
    if ico_path.exists():
        return QIcon(str(ico_path)).pixmap(256, 256)
    return QPixmap()
