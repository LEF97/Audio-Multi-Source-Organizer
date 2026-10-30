"""Configuration des tableaux de pistes et gestion des colonnes (mixin de MainWindow)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, cast

from PySide6.QtCore import QAbstractTableModel, QPoint, QSettings, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMainWindow,
    QMenu,
    QPushButton,
    QTableView,
)

from amso.core.i18n import tr

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    _MixinBase = QMainWindow
else:
    _MixinBase = object


class TableColumnsMixin(_MixinBase):
    """Configuration des tableaux de pistes et gestion des colonnes (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de MainWindow sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    def _setup_track_table_view(self, table_view: QTableView, model: QAbstractTableModel, storage_key: str) -> None:
        """Harmonise et configure un QTableView de pistes :
        - Modèle virtualisé avec l'ensemble des 29 champs de la BDD.
        - Tri activé par clic d'en-tête.
        - Colonnes redimensionnables (Interactive).
        - Colonnes déplaçables par glisser-déposer (setSectionsMovable(True)).
        - Menu contextuel d'en-tête pour masquer / afficher des colonnes.
        - Sauvegarde et restauration persistante dans QSettings.
        """
        table_view.setModel(model)
        table_view.setSortingEnabled(True)
        table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        table_view.setAlternatingRowColors(True)
        table_view.setShowGrid(False)
        table_view.verticalHeader().setVisible(False)
        table_view.verticalHeader().setDefaultSectionSize(32)

        header = table_view.horizontalHeader()
        header.setSectionsMovable(True)
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(35)
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(
            lambda pos, tv=table_view, m=model, key=storage_key: self._on_table_header_context_menu(pos, tv, m, key)
        )

        for col_idx in range(model.columnCount()):
            header.setSectionResizeMode(col_idx, QHeaderView.ResizeMode.Interactive)

        # setSortingEnabled(True) applique l'indicateur par défaut de l'en-tête, décroissant sur certaines versions de Qt :
        # sans état sauvegardé, la table s'ouvrirait triée à l'envers par rapport au modèle
        sortable = cast(Any, model)
        if hasattr(sortable, "_current_sort_col") and hasattr(sortable, "_current_sort_order"):
            header.setSortIndicator(sortable._current_sort_col, sortable._current_sort_order)

        # Restauration de l'état (largeurs, ordre, masquage) ou application des valeurs par défaut
        if not self._restore_table_header_state(table_view, storage_key):
            columns = getattr(model, "COLUMNS", [])
            for col_idx, col_def in enumerate(columns):
                header.resizeSection(col_idx, col_def[2])
                table_view.setColumnHidden(col_idx, not col_def[3])

        header.sectionResized.connect(lambda *_: self._save_table_header_state(table_view, storage_key))
        header.sectionMoved.connect(lambda *_: self._save_table_header_state(table_view, storage_key))
        header.sortIndicatorChanged.connect(lambda *_: self._save_table_header_state(table_view, storage_key))

    def _on_table_header_context_menu(
        self,
        pos: QPoint,
        table_view: QTableView,
        model: QAbstractTableModel,
        storage_key: str,
    ) -> None:
        header = table_view.horizontalHeader()
        menu = self._build_columns_menu(table_view, model, storage_key)
        menu.exec(header.mapToGlobal(pos))

    def _open_columns_menu(
        self,
        button: QPushButton,
        table_view: QTableView,
        model: QAbstractTableModel,
        storage_key: str,
    ) -> None:
        menu = self._build_columns_menu(table_view, model, storage_key)
        pos = QPoint(0, button.height())
        menu.exec(button.mapToGlobal(pos))

    def _build_columns_menu(
        self,
        table_view: QTableView,
        model: QAbstractTableModel,
        storage_key: str,
    ) -> QMenu:
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background-color: #1A1D24; color: #E2E8F0; border: 1px solid #282C37; padding: 4px; }"
            "QMenu::item:selected { background-color: #0284C7; }"
        )

        act_show_all = QAction(tr("table.menu_show_all"), menu)
        act_show_all.triggered.connect(lambda: self._show_all_columns(table_view, storage_key))
        menu.addAction(act_show_all)

        act_reset = QAction(tr("table.menu_reset_columns"), menu)
        act_reset.triggered.connect(lambda: self._reset_default_columns(table_view, storage_key))
        menu.addAction(act_reset)

        menu.addSeparator()

        title_act = QAction(f"— {tr('table.menu_columns')} —", menu)
        title_act.setEnabled(False)
        menu.addAction(title_act)

        for col_idx in range(model.columnCount()):
            col_name = model.headerData(col_idx, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            if not col_name:
                continue
            act = QAction(col_name, menu)
            act.setCheckable(True)
            act.setChecked(not table_view.isColumnHidden(col_idx))
            act.toggled.connect(
                lambda checked, c=col_idx, tv=table_view, sk=storage_key: self._toggle_table_column(tv, c, checked, sk)
            )
            menu.addAction(act)

        return menu

    def _toggle_table_column(self, table_view: QTableView, col_idx: int, visible: bool, storage_key: str) -> None:
        table_view.setColumnHidden(col_idx, not visible)
        self._save_table_header_state(table_view, storage_key)

    def _show_all_columns(self, table_view: QTableView, storage_key: str) -> None:
        for c in range(table_view.model().columnCount()):
            table_view.setColumnHidden(c, False)
        self._save_table_header_state(table_view, storage_key)

    def _reset_default_columns(self, table_view: QTableView, storage_key: str) -> None:
        model = cast(Any, table_view.model())
        header = table_view.horizontalHeader()
        columns = getattr(model, "COLUMNS", [])
        for c in range(model.columnCount()):
            if c < len(columns):
                col_def = columns[c]
                table_view.setColumnHidden(c, not col_def[3])
                header.resizeSection(c, col_def[2])
            visual_idx = header.visualIndex(c)
            if visual_idx != c:
                header.moveSection(visual_idx, c)
        self._save_table_header_state(table_view, storage_key)

    def _save_table_header_state(self, table_view: QTableView, storage_key: str) -> None:
        settings = QSettings("AMSO", "AudioMultiSourceOrganizer")
        settings.setValue(f"header_state_{storage_key}", table_view.horizontalHeader().saveState())
        model = cast(Any, table_view.model())
        if hasattr(model, "_current_sort_col"):
            settings.setValue(f"sort_col_{storage_key}", model._current_sort_col)
            order_val = (
                model._current_sort_order.value
                if hasattr(model._current_sort_order, "value")
                else int(model._current_sort_order)
            )
            settings.setValue(f"sort_order_{storage_key}", order_val)

    def _restore_table_header_state(self, table_view: QTableView, storage_key: str) -> bool:
        settings = QSettings("AMSO", "AudioMultiSourceOrganizer")
        state = settings.value(f"header_state_{storage_key}")
        restored = False
        if state is not None:
            restored = bool(table_view.horizontalHeader().restoreState(state))

        model = cast(Any, table_view.model())
        if hasattr(model, "_current_sort_col"):
            saved_sort_col = settings.value(f"sort_col_{storage_key}")
            saved_sort_order = settings.value(f"sort_order_{storage_key}")
            if saved_sort_col is not None and saved_sort_order is not None:
                try:
                    col = int(saved_sort_col)
                    order = Qt.SortOrder(int(saved_sort_order))
                    if 0 <= col < model.columnCount():
                        model._current_sort_col = col
                        model._current_sort_order = order
                        table_view.horizontalHeader().setSortIndicator(col, order)
                except Exception:
                    pass
        return restored

    # -------------------------------------------------------------------------
    # Pages du QStackedWidget
    # -------------------------------------------------------------------------
