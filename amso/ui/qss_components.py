"""Styles QSS des composants (arborescences, tables, cartes, popovers, curseurs)."""

from __future__ import annotations

COMPONENTS_DARK_QSS = """
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

QSpinBox, QDoubleSpinBox {
    background-color: #20242D;
    color: #F8FAFC;
    border: 1px solid #333846;
    border-radius: 6px;
    padding: 5px 8px;
    font-size: 13px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #38BDF8;
    background-color: #262B36;
}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background-color: #282C37;
    border: none;
    width: 18px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
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
