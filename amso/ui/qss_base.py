"""Styles QSS de base (palette sombre globale, fenêtres, boutons, contrôles)."""

from __future__ import annotations

BASE_DARK_QSS = """
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
}

QProgressBar::chunk {
    background-color: #0284C7;
    border-radius: 3px;
}

QStatusBar QProgressBar {
    max-width: 220px;
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
"""
