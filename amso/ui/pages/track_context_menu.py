"""Menu contextuel des tables de pistes (bibliothèque et vue Dossiers), identique hors suppression."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QPoint
from PySide6.QtGui import QAction, QCursor
from PySide6.QtWidgets import QAbstractItemView, QMenu

from amso.core.database import TrackRecord
from amso.core.i18n import tr


def show_track_context_menu(
    owner: Any,
    view: QAbstractItemView,
    model: Any,
    pos: QPoint,
    columns_key: str,
    on_delete: Callable[[TrackRecord], None],
) -> None:
    """`owner` est la fenêtre qui fournit les actions de lecture, la sélection et le menu des colonnes."""
    index = view.indexAt(pos)
    menu = QMenu(owner)

    if index.isValid():
        selected_tracks = owner._get_selected_tracks(view, model, index.row())
        if selected_tracks:
            act_next = QAction(tr("context_menu.play_next"), owner)
            act_next.triggered.connect(lambda: owner._insert_next_with_vlc_check(selected_tracks))
            menu.addAction(act_next)

            act_add = QAction(tr("context_menu.add_to_playlist"), owner)
            act_add.triggered.connect(lambda: owner._append_tracks_with_vlc_check(selected_tracks))
            menu.addAction(act_add)

            menu.addSeparator()

        track: TrackRecord | None = model.get_track_at(index.row())
        if track:
            action_open_dir = QAction(tr("context_menu.open_file_location"), owner)
            action_open_dir.triggered.connect(lambda: owner._open_file_location(track.source_path))
            menu.addAction(action_open_dir)

            menu.addSeparator()

            action_del = QAction(tr("context_menu.delete_track"), owner)
            action_del.triggered.connect(lambda: on_delete(track))
            menu.addAction(action_del)

            menu.addSeparator()

    # Personnalisation des colonnes accessible directement depuis le tableau
    cols_submenu = owner._build_columns_menu(view, model, columns_key)
    cols_submenu.setTitle("⚙️  " + tr("table.menu_columns"))
    menu.addMenu(cols_submenu)

    menu.exec(QCursor.pos())
