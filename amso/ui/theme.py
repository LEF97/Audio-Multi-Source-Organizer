"""Thème et styles QSS modernes pour l'interface PySide6 d'AMSO."""

DARK_THEME_QSS = """
/* =========================================================================
   AMSO - Modern Dark Palette
   ========================================================================= */

QMainWindow, QWidget#centralWidget {
    background-color: #121418;
    color: #E2E8F0;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Roboto", sans-serif;
    font-size: 13px;
}

/* --- Barre latérale (Sidebar) --- */
QFrame#sidebarFrame {
    background-color: #1A1D24;
    border-right: 1px solid #282C37;
    min-width: 230px;
    max-width: 260px;
}

QLabel#appLogoLabel {
    color: #38BDF8;
    font-size: 16px;
    font-weight: 700;
    padding: 18px 16px;
    letter-spacing: 0.5px;
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
    padding: 8px 16px;
}

QLineEdit#searchEdit {
    background-color: #20242D;
    color: #F8FAFC;
    border: 1px solid #333846;
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 13px;
    min-width: 320px;
}

QLineEdit#searchEdit:focus {
    border: 1px solid #38BDF8;
    background-color: #262B36;
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
"""
