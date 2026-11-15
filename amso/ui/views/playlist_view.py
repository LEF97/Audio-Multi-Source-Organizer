"""Vue Liste de Lecture (Playlist) pour AMSO.

Comprend un mini-lecteur en haut avec contrôles complets et miniature de jaquette,
et un tableau détaillé de la file d'attente en dessous.
"""

from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QAction, QCursor, QShowEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QMenu,
    QWidget,
)

from amso.core.database import TrackRecord
from amso.core.i18n import tr
from amso.services.player_service import PlayerService
from amso.ui.models import PlaylistTableModel
from amso.ui.table_settings import app_settings
from amso.ui.views.playlist_ui_builder import PlaylistHeaderWidget, PlaylistUiMixin
from amso.ui.widgets.playlist_table_view import PlaylistTableView
from amso.ui.widgets.transport_mixin import TransportViewMixin

__all__ = ["PlaylistHeaderWidget", "PlaylistTableView", "PlaylistView"]


class PlaylistView(PlaylistUiMixin, TransportViewMixin, QWidget):
    """Page Playlist : Mini-lecteur en haut + Tableau de la file d'attente en dessous."""

    _transport_btn_radius = 4
    _transport_btn_font = 19
    _transport_cover_size = 56
    _transport_cover_radius = 8

    def __init__(self, player_service: PlayerService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.player = player_service
        self.playlist_model = PlaylistTableModel(self.player, parent=self)

        self._setup_ui()
        self._connect_signals()

        # État initial
        self.update_track_info(self.player.current_track)
        self.update_playback_state("playing" if self.player.is_playing else "stopped")
        self._update_stats_label()

    def _connect_signals(self) -> None:
        self._connect_playlist_header_signals()

        # Interactions sur le tableau de playlist
        self.table_view.doubleClicked.connect(self._on_table_double_clicked)
        self.table_view.customContextMenuRequested.connect(self._on_context_menu)

    def _on_header_context_menu(self, pos: QPoint) -> None:
        header = self.table_view.horizontalHeader()
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background-color: #1A1D24; color: #E2E8F0; border: 1px solid #282C37; padding: 4px; }"
            "QMenu::item:selected { background-color: #0284C7; }"
        )

        act_show_all = QAction(tr("table.menu_show_all"), menu)
        act_show_all.triggered.connect(self._show_all_columns)
        menu.addAction(act_show_all)

        act_reset = QAction(tr("table.menu_reset_columns"), menu)
        act_reset.triggered.connect(self._reset_default_columns)
        menu.addAction(act_reset)

        menu.addSeparator()

        title_act = QAction(f"— {tr('table.menu_columns')} —", menu)
        title_act.setEnabled(False)
        menu.addAction(title_act)

        for col_idx in range(self.playlist_model.columnCount()):
            col_name = self.playlist_model.headerData(col_idx, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            if not col_name or col_name.strip() in ("", "#"):
                continue
            act = QAction(col_name, menu)
            act.setCheckable(True)
            act.setChecked(not self.table_view.isColumnHidden(col_idx))
            act.toggled.connect(lambda checked, c=col_idx: self._toggle_column(c, checked))
            menu.addAction(act)

        menu.exec(header.mapToGlobal(pos))

    def _toggle_column(self, col_idx: int, visible: bool) -> None:
        self.table_view.setColumnHidden(col_idx, not visible)
        self.save_table_state()

    def _show_all_columns(self) -> None:
        for c in range(self.playlist_model.columnCount()):
            self.table_view.setColumnHidden(c, False)
        self.save_table_state()

    def _reset_default_columns(self) -> None:
        header = self.table_view.horizontalHeader()
        for idx, col_def in enumerate(self.playlist_model.COLUMNS):
            self.table_view.setColumnHidden(idx, False)
            header.resizeSection(idx, col_def[1])
            visual_idx = header.visualIndex(idx)
            if visual_idx != idx:
                header.moveSection(visual_idx, idx)
        self.save_table_state()

    def save_table_state(self) -> None:
        """Sauvegarde la configuration des colonnes du tableau de playlist (largeurs, ordre, masquage)."""
        settings = app_settings()
        settings.setValue("header_state_playlist", self.table_view.horizontalHeader().saveState())

    def restore_table_state(self) -> bool:
        """Restaure la configuration des colonnes du tableau de playlist."""
        settings = app_settings()
        state = settings.value("header_state_playlist")
        if state is not None:
            return bool(self.table_view.horizontalHeader().restoreState(state))
        return False

    def _on_table_double_clicked(self, index) -> None:
        if index.isValid():
            self.player.play_index(index.row())

    def _on_context_menu(self, pos: QPoint) -> None:
        index = self.table_view.indexAt(pos)
        menu = QMenu(self)

        if index.isValid():
            row = index.row()
            act_play = QAction(tr("playlist.menu_play"), self)
            act_play.triggered.connect(lambda: self.player.play_index(row))
            menu.addAction(act_play)

            act_remove = QAction(tr("playlist.menu_remove"), self)
            act_remove.triggered.connect(lambda: self.player.remove_at(row))
            menu.addAction(act_remove)

            menu.addSeparator()

        act_save = QAction(tr("playlist.menu_save"), self)
        act_save.setEnabled(len(self.player.playlist) > 0)
        act_save.triggered.connect(self._on_save_playlist_clicked)
        menu.addAction(act_save)

        act_shuffle = QAction(tr("playlist.btn_shuffle_tracks"), self)
        act_shuffle.setEnabled(bool(self.player.is_shuffle) and len(self.player.playlist) > 1)
        act_shuffle.triggered.connect(self._on_shuffle_tracks_clicked)
        menu.addAction(act_shuffle)
        menu.addSeparator()

        act_clear = QAction(tr("playlist.menu_clear"), self)
        act_clear.triggered.connect(self.player.clear_playlist)
        menu.addAction(act_clear)

        menu.exec(QCursor.pos())

    def _on_playlist_updated(self) -> None:
        """Appelé lorsque la composition de la playlist change."""
        super()._on_playlist_updated()
        QTimer.singleShot(60, self.scroll_to_current_track)

    def scroll_to_current_track(self) -> None:
        """Positionne le défilement de manière à centrer le morceau actif au milieu de l'écran."""
        try:
            curr_idx = self.player.current_index
            if 0 <= curr_idx < self.playlist_model.rowCount():
                model_idx = self.playlist_model.index(curr_idx, 0)
                self.table_view.scrollTo(model_idx, QAbstractItemView.ScrollHint.PositionAtCenter)
        except Exception:
            pass

    def showEvent(self, event: QShowEvent) -> None:
        """Centre automatiquement la vue sur le titre en cours de lecture lorsqu'on accède à la page."""
        super().showEvent(event)
        QTimer.singleShot(60, self.scroll_to_current_track)

    def update_track_info(self, track: TrackRecord | None) -> None:
        """Met à jour l'affichage avec la piste en cours de lecture et centre la ligne active."""
        super().update_track_info(track)
        if track:
            self.scroll_to_current_track()

    def retranslate_ui(self) -> None:
        """Met à jour l'ensemble des textes, infobulles et en-têtes selon la langue active."""
        self.retranslate_header_ui()
        if hasattr(self, "playlist_model"):
            self.playlist_model.notify_language_changed()
