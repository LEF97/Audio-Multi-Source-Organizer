"""Configuration des tableaux de pistes et gestion des colonnes (mixin de MainWindow)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, cast

from PySide6.QtCore import QAbstractTableModel, QPoint, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMainWindow,
    QMenu,
    QPushButton,
    QTableView,
)

from amso.ui.table_settings import (
    apply_default_columns,
    build_columns_menu,
    reset_default_columns,
    restore_table_header_state,
    save_table_header_state,
    show_all_columns,
    toggle_table_column,
)

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
        # setSortingEnabled(True) trie selon l'indicateur courant de l'en-tête, décroissant par défaut : sans état
        # sauvegardé, la table s'ouvrirait à l'envers du tri initial du modèle (lu avant que ce tri ne l'écrase)
        sortable = cast(Any, model)
        if hasattr(sortable, "_current_sort_col") and hasattr(sortable, "_current_sort_order"):
            table_view.horizontalHeader().setSortIndicator(sortable._current_sort_col, sortable._current_sort_order)
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
        header.setMinimumSectionSize(28)
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(
            lambda pos, tv=table_view, m=model, key=storage_key: self._on_table_header_context_menu(pos, tv, m, key)
        )

        for col_idx in range(model.columnCount()):
            header.setSectionResizeMode(col_idx, QHeaderView.ResizeMode.Interactive)

        # Restauration de l'état (largeurs, ordre, masquage) ou application des valeurs par défaut
        if not self._restore_table_header_state(table_view, storage_key):
            apply_default_columns(table_view, model)

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
        return build_columns_menu(self, table_view, model, storage_key)

    def _toggle_table_column(self, table_view: QTableView, col_idx: int, visible: bool, storage_key: str) -> None:
        toggle_table_column(table_view, col_idx, visible, storage_key)

    def _show_all_columns(self, table_view: QTableView, storage_key: str) -> None:
        show_all_columns(table_view, storage_key)

    def _reset_default_columns(self, table_view: QTableView, storage_key: str) -> None:
        reset_default_columns(table_view, storage_key)

    def _save_table_header_state(self, table_view: QTableView, storage_key: str) -> None:
        save_table_header_state(table_view, storage_key)

    def _restore_table_header_state(self, table_view: QTableView, storage_key: str) -> bool:
        return restore_table_header_state(table_view, storage_key)

    # -------------------------------------------------------------------------
    # Pages du QStackedWidget
    # -------------------------------------------------------------------------
