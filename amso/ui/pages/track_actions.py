"""Recherche, menu contextuel des pistes et lecture depuis les tableaux (mixin de MainWindow)."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QAction, QCursor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QTableView,
)

from amso.core.activity_messages import LogMessage, raw_line
from amso.core.database import (
    TrackRecord,
)
from amso.core.i18n import tr
from amso.ui.dialogs.delete_track_dialog import DeleteTrackDialog, send_file_to_trash
from amso.ui.dialogs.large_selection_dialog import LargeSelectionDialog

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    _MixinBase = QMainWindow
else:
    _MixinBase = object


class TrackActionsMixin(_MixinBase):
    """Recherche, menu contextuel des pistes et lecture depuis les tableaux (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de MainWindow sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    def _on_search_changed(self, text: str) -> None:
        self._search_timer.start()

    def _perform_search(self) -> None:
        query = self.search_edit.text().strip()
        self.table_model.set_filter(search_query=query)
        self._update_track_count()

    def _update_track_count(self) -> None:
        count = self.table_model.display_count()
        if count <= 1:
            self.track_count_label.setText(tr("topbar.track_count_singular", count=f"{count:,}"))
        else:
            self.track_count_label.setText(tr("topbar.track_count", count=f"{count:,}"))

    def _on_table_context_menu(self, pos: QPoint) -> None:
        index = self.table_view.indexAt(pos)
        menu = QMenu(self)

        if index.isValid():
            selected_tracks = self._get_selected_tracks(self.table_view, self.table_model, index.row())
            if selected_tracks:
                act_next = QAction(tr("context_menu.play_next"), self)
                act_next.triggered.connect(lambda: self._insert_next_with_vlc_check(selected_tracks))
                menu.addAction(act_next)

                act_add = QAction(tr("context_menu.add_to_playlist"), self)
                act_add.triggered.connect(lambda: self._append_tracks_with_vlc_check(selected_tracks))
                menu.addAction(act_add)

                menu.addSeparator()

            track: TrackRecord | None = self.table_model.get_track_at(index.row())
            if track:
                action_open_dir = QAction(tr("context_menu.open_file_location"), self)
                action_open_dir.triggered.connect(lambda: self._open_file_location(track.source_path))
                menu.addAction(action_open_dir)

                menu.addSeparator()

                action_del = QAction(tr("context_menu.delete_track"), self)
                action_del.triggered.connect(lambda: self._delete_track_from_lib(track))
                menu.addAction(action_del)

                menu.addSeparator()

        # Personnalisation des colonnes accessible directement depuis le tableau
        cols_submenu = self._build_columns_menu(self.table_view, self.table_model, "all_tracks")
        cols_submenu.setTitle("⚙️  " + tr("table.menu_columns"))
        menu.addMenu(cols_submenu)

        menu.exec(QCursor.pos())

    def _open_file_location(self, file_path: str | None) -> None:
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(
                self,
                tr("dialog.file_not_found_title"),
                tr("dialog.file_not_found_message"),
            )
            return

        norm_path = os.path.normpath(file_path)
        if sys.platform == "win32":
            subprocess.run(f'explorer /select,"{norm_path}"')
        elif sys.platform == "darwin":
            subprocess.run(["open", "-R", norm_path])
        else:
            subprocess.run(["xdg-open", os.path.dirname(norm_path)])

    def _delete_track_from_lib(self, track: TrackRecord) -> None:
        if track.id is None:
            return
        dlg = DeleteTrackDialog(track, self)
        if dlg.exec() != QDialog.DialogCode.Accepted or not dlg.action:
            return

        if dlg.action == "trash" and track.source_path:
            send_file_to_trash(track.source_path)

        # Dans les deux cas (retirer de la bibliothèque ou corbeille), on ignore pour les futurs scans
        self.db.ignore_track(track.source_ref, track.source_path)
        self.db.delete_track(track.id)

        # Retirer de la playlist du lecteur s'il y est présent
        self._remove_track_from_player(track)

        self.table_model.reload_data()
        self.folder_table_model.reload_data()
        self._update_track_count()
        self._refresh_stats_view()
        self._refresh_folders_tree()

    def _remove_track_from_player(self, track: TrackRecord) -> None:
        """Retire le morceau de la file d'attente du lecteur audio s'il y figure."""
        if not hasattr(self, "player_service") or not self.player_service:
            return
        pl = self.player_service.playlist
        for i in range(len(pl) - 1, -1, -1):
            t = pl[i]
            if (track.id is not None and t.id == track.id) or (
                track.source_path and t.source_path == track.source_path
            ):
                self.player_service.remove_at(i)

    # -------------------------------------------------------------------------
    # Interactions du Lecteur Audio (Double-clic, Playlist, Multi-sélection)
    # -------------------------------------------------------------------------

    def _on_player_error(self, message: str) -> None:
        """Affiche les avertissements ou erreurs du lecteur dans la barre d'état et les consigne dans les logs."""
        self._status_is_alert = True
        self.status_label.setText(f"⚠️ {message}")
        self.status_label.setToolTip(f"{message}\n({tr('status.click_to_view_logs')})")
        self.status_label.setCursor(Qt.CursorShape.PointingHandCursor)

        source_name = tr("sidebar.nav_player").replace("🎵", "").strip()
        self.db.add_activity_log(
            action=LogMessage("logs.action_player_error"),
            level="WARNING",
            category="PLAYER",
            source_name=source_name,
            details=[raw_line(message)],
            items_errors=1,
        )

        if hasattr(self, "page_logs") and self.page_logs:
            self.page_logs.mark_dirty()

    def _on_table_view_double_clicked(self, index) -> None:
        """Double-clic sur un morceau dans la table principale."""
        if not index.isValid():
            return
        self.table_view.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtCenter)
        self._play_from_table(self.table_model, index.row())

    def _on_folder_table_view_double_clicked(self, index) -> None:
        """Double-clic sur un morceau dans la table par dossier."""
        if not index.isValid():
            return
        self.folder_table_view.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtCenter)
        self._play_from_table(self.folder_table_model, index.row())

    def _play_from_table(self, model: Any, start_row: int) -> None:
        """Lance la lecture du morceau cliqué et charge la sélection dans la playlist (avec confirmation si > 1 000 morceaux)."""
        if not self.player_service.is_vlc_available:
            if not self._ensure_vlc_available():
                return

        clicked_track = model.get_track_at(start_row)
        if clicked_track is None:
            return

        total_rows = model.rowCount()

        # Si la sélection dépasse 1 000 titres, afficher le dialogue de décision
        if total_rows > 1000:
            folder_count = 0
            if clicked_track.folder_path:
                try:
                    folder_count = self.db.count_tracks_by_folder(
                        clicked_track.folder_path,
                        source_id=clicked_track.source_id,
                        recursive=False,
                    )
                except Exception:
                    folder_count = 0

            dialog = LargeSelectionDialog(
                track=clicked_track,
                total_count=total_rows,
                folder_track_count=folder_count,
                parent=self,
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return

            choice = dialog.get_choice()
            if choice == "folder":
                tracks_to_play = self.db.get_tracks_by_folder(
                    folder_path=clicked_track.folder_path,
                    source_id=clicked_track.source_id,
                    recursive=False,
                )
                if not tracks_to_play:
                    tracks_to_play = [clicked_track]
                target_idx = 0
                for idx, t in enumerate(tracks_to_play):
                    if (t.id is not None and t.id == clicked_track.id) or (
                        t.source_path and t.source_path == clicked_track.source_path
                    ):
                        target_idx = idx
                        break
                self.player_service.play_tracks(tracks_to_play, start_index=target_idx)
                return

            elif choice == "limit_1000":
                limit_tracks: list[TrackRecord] = []
                end_row = min(total_rows, start_row + 1000)
                for r in range(start_row, end_row):
                    t = model.get_track_at(r)
                    if t is not None:
                        limit_tracks.append(t)
                if limit_tracks:
                    self.player_service.play_tracks(limit_tracks, start_index=0)
                return

            elif choice == "play_all":
                # Poursuit vers le chargement complet ci-dessous
                pass
            else:
                return

        # Cas <= 1 000 ou choix "play_all" : tous les titres du modèle sont ajoutés, lecture démarrant au titre cliqué
        all_tracks: list[TrackRecord] = []
        target_index = 0
        for r in range(total_rows):
            t = model.get_track_at(r)
            if t is not None:
                if r == start_row:
                    target_index = len(all_tracks)
                all_tracks.append(t)

        if all_tracks:
            self.player_service.play_tracks(all_tracks, start_index=target_index)

    def _insert_next_with_vlc_check(self, tracks: list[TrackRecord]) -> None:
        if not self.player_service.is_vlc_available:
            if not self._ensure_vlc_available():
                return
        self.player_service.insert_next(tracks)

    def _append_tracks_with_vlc_check(self, tracks: list[TrackRecord]) -> None:
        if not self.player_service.is_vlc_available:
            if not self._ensure_vlc_available():
                return
        self.player_service.append_tracks(tracks)

    def _get_selected_tracks(self, table_view: QTableView, model: Any, clicked_row: int) -> list[TrackRecord]:
        """Récupère la liste ordonnée des pistes sélectionnées (avec prise en charge de la multi-sélection)."""
        selection_model = table_view.selectionModel()
        selected_rows: set[int] = set()
        if selection_model:
            selected_rows = {idx.row() for idx in selection_model.selectedRows()}
        if not selected_rows:
            selected_rows = {clicked_row}
        ordered_rows = sorted(selected_rows)
        tracks: list[TrackRecord] = []
        for r in ordered_rows:
            t = model.get_track_at(r)
            if t is not None:
                tracks.append(t)
        return tracks
