"""Accès unique aux réglages Qt de l'interface (colonnes et tri des tables)."""

from __future__ import annotations

import logging
import os
from collections.abc import Iterable
from typing import Any, cast

from PySide6.QtCore import QAbstractItemModel, QSettings, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QTableView, QWidget

from amso.core.i18n import tr

logger = logging.getLogger(__name__)

ORGANIZATION = "AMSO"
APPLICATION = "AudioMultiSourceOrganizer"


def app_settings() -> QSettings:
    """Réglages de l'interface ; `AMSO_QSETTINGS_PATH` les redirige vers un fichier ini (tests : pas de registre ni de plist partagés)."""
    override = os.environ.get("AMSO_QSETTINGS_PATH")
    if override:
        return QSettings(override, QSettings.Format.IniFormat)
    return QSettings(ORGANIZATION, APPLICATION)


def apply_default_columns(table_view: QTableView, model: QAbstractItemModel | None = None) -> None:
    """Applique la visibilité et les largeurs par défaut définies dans `model.COLUMNS`."""
    target_model = model or table_view.model()
    if target_model is None:
        return
    header = table_view.horizontalHeader()
    columns = getattr(target_model, "COLUMNS", [])
    for col_idx, col_def in enumerate(columns):
        header.resizeSection(col_idx, col_def[2])
        table_view.setColumnHidden(col_idx, not col_def[3])


def save_table_header_state(table_view: QTableView, storage_key: str) -> None:
    """Sauvegarde indépendante des largeurs, de l'ordre, de la visibilité et du tri d'un tableau."""
    settings = app_settings()
    settings.setValue(f"header_state_{storage_key}", table_view.horizontalHeader().saveState())
    model = cast(Any, table_view.model())
    if model is not None and hasattr(model, "_current_sort_col"):
        settings.setValue(f"sort_col_{storage_key}", model._current_sort_col)
        order_val = (
            model._current_sort_order.value
            if hasattr(model._current_sort_order, "value")
            else int(model._current_sort_order)
        )
        settings.setValue(f"sort_order_{storage_key}", order_val)
    settings.sync()


def restore_table_header_state(table_view: QTableView, storage_key: str) -> bool:
    """Restaure l'état des colonnes et du tri d'un tableau depuis `QSettings`."""
    settings = app_settings()
    state = settings.value(f"header_state_{storage_key}")
    restored = False
    if state is not None:
        restored = bool(table_view.horizontalHeader().restoreState(state))

    model = cast(Any, table_view.model())
    if model is not None and hasattr(model, "_current_sort_col"):
        saved_sort_col = settings.value(f"sort_col_{storage_key}")
        saved_sort_order = settings.value(f"sort_order_{storage_key}")
        if saved_sort_col is not None and saved_sort_order is not None:
            try:
                col = int(saved_sort_col)
                order = Qt.SortOrder(int(saved_sort_order))
                columns = getattr(model, "COLUMNS", [])
                is_playing_col = 0 <= col < len(columns) and columns[col][1] == "is_playing"
                if 0 <= col < model.columnCount() and not is_playing_col:
                    model._current_sort_col = col
                    model._current_sort_order = order
                    table_view.horizontalHeader().setSortIndicator(col, order)
            except (ValueError, TypeError):
                # QSettings d'une ancienne version (valeur non entière) : tri par défaut.
                logger.debug("Tri enregistré illisible", exc_info=True)
    return restored


def toggle_table_column(table_view: QTableView, col_idx: int, visible: bool, storage_key: str) -> None:
    table_view.setColumnHidden(col_idx, not visible)
    save_table_header_state(table_view, storage_key)


def show_all_columns(table_view: QTableView, storage_key: str) -> None:
    model = table_view.model()
    if model is None:
        return
    for c in range(model.columnCount()):
        table_view.setColumnHidden(c, False)
    save_table_header_state(table_view, storage_key)


def reset_default_columns(table_view: QTableView, storage_key: str) -> None:
    model = table_view.model()
    if model is None:
        return
    header = table_view.horizontalHeader()
    apply_default_columns(table_view, model)
    for c in range(model.columnCount()):
        visual_idx = header.visualIndex(c)
        if visual_idx != c:
            header.moveSection(visual_idx, c)
    save_table_header_state(table_view, storage_key)


def build_columns_menu(
    parent: QWidget,
    table_view: QTableView,
    model: QAbstractItemModel,
    storage_key: str,
    *,
    skip_headers: Iterable[str] = ("",),
) -> QMenu:
    """Construit le menu contextuel de sélection des colonnes visibles."""
    menu = QMenu(parent)
    menu.setStyleSheet(
        "QMenu { background-color: #1A1D24; color: #E2E8F0; border: 1px solid #282C37; padding: 4px; }"
        "QMenu::item:selected { background-color: #0284C7; }"
    )

    act_show_all = QAction(tr("table.menu_show_all"), menu)
    act_show_all.triggered.connect(lambda: show_all_columns(table_view, storage_key))
    menu.addAction(act_show_all)

    act_reset = QAction(tr("table.menu_reset_columns"), menu)
    act_reset.triggered.connect(lambda: reset_default_columns(table_view, storage_key))
    menu.addAction(act_reset)

    menu.addSeparator()

    title_act = QAction(f"— {tr('table.menu_columns')} —", menu)
    title_act.setEnabled(False)
    menu.addAction(title_act)

    excluded = set(skip_headers)
    for col_idx in range(model.columnCount()):
        col_name = model.headerData(col_idx, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
        label = str(col_name).strip() if col_name is not None else ""
        if not label or label in excluded:
            continue
        act = QAction(str(col_name), menu)
        act.setCheckable(True)
        act.setChecked(not table_view.isColumnHidden(col_idx))
        act.toggled.connect(
            lambda checked, c=col_idx, tv=table_view, sk=storage_key: toggle_table_column(tv, c, checked, sk)
        )
        menu.addAction(act)

    return menu
