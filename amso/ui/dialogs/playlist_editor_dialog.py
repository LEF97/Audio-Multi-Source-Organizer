"""Dialogue de gestion, réparation et réorganisation d'une playlist."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from PySide6.QtCore import QEventLoop, Qt, QThread
from PySide6.QtGui import QCloseEvent, QColor, QKeyEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from amso.core.database import DatabaseManager, PlaylistEntryRecord, PlaylistSummaryRecord
from amso.core.i18n import tr
from amso.core.playlist_parser import parse_playlist_file
from amso.ui.dialogs.playlist_repair_panel import PlaylistRepairPanel, PlaylistSaveWorker
from amso.ui.styles import COLOR_DANGER_SOFT, COLOR_TEXT, COLOR_TEXT_BRIGHT, COLOR_TEXT_MUTED
from amso.ui.theme import DARK_THEME_QSS

logger = logging.getLogger(__name__)


def _format_duration_short(seconds: float | None) -> str:
    """Formate une durée en secondes en M:SS ou H:MM:SS."""
    if seconds is None or seconds < 0:
        return "-"
    total = int(round(seconds))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


class PlaylistEditorDialog(QDialog):
    """Dialogue permettant d'inspecter, réordonner, nettoyer et relocaliser une playlist."""

    def __init__(
        self,
        db: DatabaseManager,
        playlist: PlaylistSummaryRecord,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.db = db
        self.playlist = playlist
        self._entries: list[PlaylistEntryRecord] = db.get_playlist_entries(playlist.id)
        self._is_cue = (playlist.format or "").lower() == "cue" or playlist.file_path.lower().endswith(".cue")
        self._file_exists = bool(playlist.file_path and os.path.exists(playlist.file_path))
        self._show_errors_only = False
        self._modified = False
        self._reloaded_from_disk = False
        self._pending_cue_replacements: dict[str, Path] = {}
        self._prefer_relative = self._detect_relative_preference()

        self.setWindowTitle(tr("playlist_editor.window_title", name=playlist.name))
        self.setMinimumSize(920, 580)
        self.resize(980, 640)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(DARK_THEME_QSS)

        self._setup_ui()
        self._populate_table()

    def _detect_relative_preference(self) -> bool:
        """Détermine si la playlist utilisait majoritairement des chemins relatifs."""
        if not self._entries:
            return True
        rel_count = sum(1 for e in self._entries if e.raw_path and not os.path.isabs(e.raw_path))
        return rel_count >= (len(self._entries) / 2)

    @property
    def was_modified(self) -> bool:
        """Indique si la playlist a été modifiée (fichier et base mis à jour)."""
        return self._modified or self._reloaded_from_disk

    def _setup_ui(self) -> None:
        """Construit les widgets du dialogue."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        # En-tête : titre à gauche, onglets Contenu / Propositions en haut à droite
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        lbl_name = QLabel(f"📃  {self.playlist.name}")
        lbl_name.setStyleSheet(f"color: {COLOR_TEXT_BRIGHT}; font-size: 16px; font-weight: 700;")
        header_row.addWidget(lbl_name)
        header_row.addStretch()

        self.stacked_views = QStackedWidget()
        tab_qss = (
            "QPushButton { background-color: #1E293B; color: #94A3B8; border: 1px solid #334155; "
            "border-bottom: 2px solid #334155; border-top-left-radius: 6px; border-top-right-radius: 6px; "
            "border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; "
            "padding: 6px 14px; font-size: 12.5px; font-weight: 600; } "
            "QPushButton:hover:enabled { color: #E2E8F0; background-color: #263549; } "
            "QPushButton:checked { background-color: #0F172A; color: #38BDF8; "
            "border-color: #334155; border-bottom: 2px solid #38BDF8; } "
            "QPushButton:disabled { color: #475569; background-color: #162032; }"
        )
        tab_container = QHBoxLayout()
        tab_container.setSpacing(2)

        self.btn_tab_content = QPushButton(tr("playlist_editor.tab_content", count=len(self._entries)))
        self.btn_tab_content.setCheckable(True)
        self.btn_tab_content.setChecked(True)
        self.btn_tab_content.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tab_content.setStyleSheet(tab_qss)
        self.btn_tab_content.clicked.connect(lambda: self._switch_tab(0))
        tab_container.addWidget(self.btn_tab_content)

        self.btn_tab_proposals = QPushButton(tr("playlist_editor.tab_proposals", count=0))
        self.btn_tab_proposals.setCheckable(True)
        self.btn_tab_proposals.setEnabled(False)
        self.btn_tab_proposals.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tab_proposals.setStyleSheet(tab_qss)
        self.btn_tab_proposals.clicked.connect(lambda: self._switch_tab(1))
        tab_container.addWidget(self.btn_tab_proposals)
        header_row.addLayout(tab_container)

        layout.addLayout(header_row)

        lbl_path = QLabel(self.playlist.file_path)
        lbl_path.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px;")
        lbl_path.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(lbl_path)

        self.lbl_summary = QLabel()
        self.lbl_summary.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 12.5px; font-weight: 600;")
        layout.addWidget(self.lbl_summary)

        if not self._file_exists:
            warn_box = QWidget()
            warn_box.setStyleSheet("background-color: #450A0A; border: 1px solid #991B1B; border-radius: 6px;")
            warn_layout = QHBoxLayout(warn_box)
            warn_layout.setContentsMargins(10, 6, 10, 6)
            warn_layout.setSpacing(10)

            lbl_warn = QLabel(f"⚠️  {tr('playlist_editor.file_missing_notice')}")
            lbl_warn.setWordWrap(True)
            lbl_warn.setStyleSheet(f"color: {COLOR_DANGER_SOFT}; border: none; font-size: 12px;")
            warn_layout.addWidget(lbl_warn, stretch=1)

            self.btn_remove_from_library = QPushButton(tr("playlist_editor.btn_remove_from_library"))
            self.btn_remove_from_library.setProperty("class", "danger-btn")
            self.btn_remove_from_library.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_remove_from_library.clicked.connect(self._on_remove_from_library)
            warn_layout.addWidget(self.btn_remove_from_library)

            layout.addWidget(warn_box)

        if self._is_cue:
            lbl_cue = QLabel(f"ℹ️  {tr('playlist_editor.cue_notice')}")
            lbl_cue.setWordWrap(True)
            lbl_cue.setStyleSheet(
                "background-color: #0F2744; color: #93C5FD; border: 1px solid #1E40AF; "
                "border-radius: 6px; padding: 8px 10px; font-size: 12px;"
            )
            layout.addWidget(lbl_cue)

        content_page = QWidget()
        content_layout = QVBoxLayout(content_page)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        # Barre d'outils : filtres + actions de masse
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.btn_filter_all = QPushButton(tr("playlist_editor.filter_all"))
        self.btn_filter_all.setCheckable(True)
        self.btn_filter_all.setChecked(True)
        self.btn_filter_all.setProperty("class", "secondary-btn")
        self.btn_filter_all.clicked.connect(lambda: self._set_filter(False))
        toolbar.addWidget(self.btn_filter_all)

        self.btn_filter_errors = QPushButton()
        self.btn_filter_errors.setCheckable(True)
        self.btn_filter_errors.setProperty("class", "secondary-btn")
        self.btn_filter_errors.clicked.connect(lambda: self._set_filter(True))
        toolbar.addWidget(self.btn_filter_errors)

        toolbar.addStretch()

        self.btn_reload_disk = QPushButton(tr("playlist_editor.btn_reload_disk"))
        self.btn_reload_disk.setToolTip(tr("playlist_editor.tooltip_reload_disk"))
        self.btn_reload_disk.setProperty("class", "secondary-btn")
        self.btn_reload_disk.setEnabled(self._file_exists)
        self.btn_reload_disk.clicked.connect(self._on_reload_from_disk)
        toolbar.addWidget(self.btn_reload_disk)

        self.btn_auto_search = QPushButton(tr("playlist_editor.btn_auto_search"))
        self.btn_auto_search.setProperty("class", "secondary-btn")
        self.btn_auto_search.clicked.connect(self._on_auto_search)
        toolbar.addWidget(self.btn_auto_search)

        if not self._is_cue:
            self.btn_move_up = QPushButton(tr("playlist_editor.btn_move_up"))
            self.btn_move_up.setProperty("class", "secondary-btn")
            self.btn_move_up.clicked.connect(lambda: self._move_selected(-1))
            toolbar.addWidget(self.btn_move_up)

            self.btn_move_down = QPushButton(tr("playlist_editor.btn_move_down"))
            self.btn_move_down.setProperty("class", "secondary-btn")
            self.btn_move_down.clicked.connect(lambda: self._move_selected(1))
            toolbar.addWidget(self.btn_move_down)

            self.btn_clean_missing = QPushButton()
            self.btn_clean_missing.setProperty("class", "secondary-btn")
            self.btn_clean_missing.clicked.connect(self._on_clean_missing)
            toolbar.addWidget(self.btn_clean_missing)

        content_layout.addLayout(toolbar)

        # Tableau des entrées
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            [
                tr("playlist_editor.col_pos"),
                tr("library_sources.col_status"),
                tr("playlist_editor.col_title"),
                tr("playlist_editor.col_artist"),
                tr("settings.col_source_path"),
                tr("library_sources.col_duration"),
                tr("settings.col_source_actions"),
            ]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(34)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.table.setStyleSheet(
            "QTableWidget { background-color: #0F172A; border: 1px solid #334155; border-radius: 6px; "
            "color: #E2E8F0; } "
            "QTableWidget::item:selected { background-color: #1E3A5F; color: #F8FAFC; } "
            "QHeaderView::section { background-color: #1E293B; color: #94A3B8; font-weight: 600; "
            "padding: 7px 6px; border: none; }"
        )
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        for col in range(7):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(0, 44)
        self.table.setColumnWidth(1, 60)
        self.table.setColumnWidth(2, 220)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 260)
        self.table.setColumnWidth(5, 72)
        self.table.setColumnWidth(6, 84)
        self.table.itemSelectionChanged.connect(self._update_move_buttons_state)
        content_layout.addWidget(self.table, 1)

        self.stacked_views.addWidget(content_page)
        self.repair_panel = PlaylistRepairPanel(self.db, self.playlist.file_path, self)
        self.repair_panel.search_finished.connect(self._on_repair_search_finished)
        self.repair_panel.apply_requested.connect(self._on_apply_repair_proposals)
        self.repair_panel.manual_relocate_requested.connect(self._relocate_entry_at)
        self.stacked_views.addWidget(self.repair_panel)
        layout.addWidget(self.stacked_views, 1)

        # Pied de dialogue
        footer = QHBoxLayout()
        footer.addStretch()
        self.btn_cancel = QPushButton(tr("common.close"))
        self.btn_cancel.setProperty("class", "secondary-btn")
        self.btn_cancel.clicked.connect(self.reject)
        footer.addWidget(self.btn_cancel)

        self.btn_save = QPushButton(tr("common.save"))
        self.btn_save.setProperty("class", "primary-btn")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self._on_save)
        footer.addWidget(self.btn_save)
        layout.addLayout(footer)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Permet de retirer l'entrée sélectionnée avec la touche Suppr."""
        if not self._is_cue and self.stacked_views.currentIndex() == 0 and event.key() == Qt.Key.Key_Delete:
            row = self.table.currentRow()
            if row >= 0:
                idx = self._entry_index_for_row(row)
                if idx is not None:
                    self._remove_entry_at(idx)
                    return
        super().keyPressEvent(event)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Arrête proprement le worker de recherche à la fermeture."""
        self.repair_panel.stop_worker()
        super().closeEvent(event)

    def reject(self) -> None:
        """Arrête proprement le worker de recherche avant d'annuler."""
        self.repair_panel.stop_worker()
        super().reject()

    def _switch_tab(self, index: int) -> None:
        """Bascule entre l'onglet Contenu (0) et l'onglet Propositions (1)."""
        self.stacked_views.setCurrentIndex(index)
        self.btn_tab_content.setChecked(index == 0)
        self.btn_tab_proposals.setChecked(index == 1)

    def _on_remove_from_library(self) -> None:
        """Retire de la base une playlist dont le fichier n'existe plus sur le disque."""
        reply = QMessageBox.question(
            self,
            tr("playlist_editor.remove_library_confirm_title"),
            tr("playlist_editor.remove_library_confirm_msg", name=self.playlist.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.db.delete_playlist(self.playlist.id)
        self._reloaded_from_disk = True
        self.accept()

    def _on_reload_from_disk(self) -> None:
        """Relit et réindexe uniquement ce fichier playlist/CUE depuis le disque."""
        if self._modified:
            reply = QMessageBox.question(
                self,
                tr("playlist_editor.reload_confirm_title"),
                tr("playlist_editor.reload_confirm_msg"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        pl_path = Path(self.playlist.file_path)
        if not pl_path.exists():
            self._file_exists = False
            self.btn_reload_disk.setEnabled(False)
            QMessageBox.warning(
                self,
                tr("playlist_editor.reload_confirm_title"),
                tr("playlist_editor.file_missing_notice"),
            )
            return

        try:
            parsed_entries = parse_playlist_file(pl_path)
            st = pl_path.stat()
            fmt = pl_path.suffix.lstrip(".").lower() or (self.playlist.format or "")
            playlist_id = self.db.upsert_playlist(
                source_id=self.playlist.source_id,
                file_path=str(pl_path),
                file_name=pl_path.name,
                folder_path=str(pl_path.parent),
                format_str=fmt,
                file_mtime=st.st_mtime,
                file_size=st.st_size,
                entries=parsed_entries,
            )
            self.db.link_playlist_entries_to_tracks(self.playlist.source_id)
            self._entries = self.db.get_playlist_entries(playlist_id or self.playlist.id)
        except Exception as exc:
            logger.exception("Erreur lors de la relecture de la playlist %s", pl_path)
            QMessageBox.critical(
                self,
                tr("playlist_editor.reload_confirm_title"),
                tr("playlist_editor.reload_error_msg", error=exc),
            )
            return

        self._pending_cue_replacements.clear()
        self._modified = False
        self._reloaded_from_disk = True
        self.btn_tab_proposals.setEnabled(False)
        self.btn_tab_proposals.setText(tr("playlist_editor.tab_proposals", count=0))
        if self.stacked_views.currentIndex() != 0:
            self._switch_tab(0)
        self._populate_table()

    def _on_auto_search(self) -> None:
        """Lance la recherche automatique de fichiers et bascule sur l'onglet Propositions."""
        self.btn_tab_proposals.setEnabled(True)
        self._switch_tab(1)
        self.repair_panel.start_search(self._entries)

    def _on_repair_search_finished(self, matched_count: int) -> None:
        """Met à jour le compteur de l'onglet Propositions à la fin du scan."""
        self.btn_tab_proposals.setText(tr("playlist_editor.tab_proposals", count=matched_count))

    def _on_apply_repair_proposals(self, mapping: dict[int, str]) -> None:
        """Applique les propositions cochées en mémoire puis revient sur l'onglet Contenu."""
        for entry_idx, resolved_path in mapping.items():
            if 0 <= entry_idx < len(self._entries):
                new_path = Path(resolved_path)
                if self._is_cue and self._entries[entry_idx].raw_path:
                    self._pending_cue_replacements[self._entries[entry_idx].raw_path] = new_path
                self._apply_relocated_path(entry_idx, new_path)
        self._modified = True
        if self._show_errors_only and not any(e.is_missing for e in self._entries):
            self._set_filter(False)
        else:
            self._populate_table()
        self._switch_tab(0)

    def _set_filter(self, errors_only: bool) -> None:
        """Bascule entre toutes les pistes et les anomalies uniquement."""
        self._show_errors_only = errors_only
        self.btn_filter_all.setChecked(not errors_only)
        self.btn_filter_errors.setChecked(errors_only)
        self._populate_table()

    def _update_summary_and_buttons(self) -> None:
        """Met à jour les compteurs d'en-tête et l'état des boutons."""
        total = len(self._entries)
        err_count = sum(1 for e in self._entries if e.is_missing)
        total_dur = sum(e.duration_seconds or 0.0 for e in self._entries)

        self.lbl_summary.setText(
            tr(
                "playlist_editor.summary",
                total=total,
                errors=err_count,
                duration=_format_duration_short(total_dur),
            )
        )
        self.btn_filter_errors.setText(tr("playlist_editor.filter_errors", count=err_count))
        self.btn_tab_content.setText(tr("playlist_editor.tab_content", count=total))
        self.btn_auto_search.setEnabled(err_count > 0)
        if not self._is_cue:
            self.btn_clean_missing.setText(tr("playlist_editor.btn_clean_missing", count=err_count))
            self.btn_clean_missing.setEnabled(err_count > 0)
        self.btn_save.setEnabled(self._modified)
        self.btn_cancel.setText(tr("common.cancel") if self._modified else tr("common.close"))
        self._update_move_buttons_state()

    def _update_move_buttons_state(self) -> None:
        """Active ou désactive Monter / Descendre selon la sélection et le filtre."""
        if self._is_cue:
            return
        can_reorder = not self._show_errors_only and self.table.currentRow() >= 0
        row = self.table.currentRow()
        self.btn_move_up.setEnabled(can_reorder and row > 0)
        self.btn_move_down.setEnabled(can_reorder and row < self.table.rowCount() - 1)

    def _populate_table(self) -> None:
        """Remplit le tableau selon self._entries et le filtre actif."""
        self._update_summary_and_buttons()

        visible_pairs: list[tuple[int, PlaylistEntryRecord]] = [
            (idx, entry) for idx, entry in enumerate(self._entries) if not self._show_errors_only or entry.is_missing
        ]
        self.table.setRowCount(len(visible_pairs))

        for row, (entry_idx, entry) in enumerate(visible_pairs):
            pos_item = QTableWidgetItem(str(entry_idx + 1))
            pos_item.setData(Qt.ItemDataRole.UserRole, entry_idx)
            pos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, pos_item)

            status_item = QTableWidgetItem("🔴" if entry.is_missing else "🟢")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setToolTip(
                tr("playlist_editor.status_missing", path=entry.resolved_path or entry.raw_path)
                if entry.is_missing
                else tr("playlist_editor.status_ok")
            )
            self.table.setItem(row, 1, status_item)

            fallback_name = (
                Path(entry.raw_path or entry.resolved_path).stem if (entry.raw_path or entry.resolved_path) else "-"
            )
            title_item = QTableWidgetItem(entry.title or fallback_name)
            artist_item = QTableWidgetItem(entry.artist or "-")
            path_text = entry.raw_path or entry.resolved_path or "-"
            path_item = QTableWidgetItem(path_text)
            path_item.setToolTip(entry.resolved_path or entry.raw_path or "")

            dur_item = QTableWidgetItem(_format_duration_short(entry.duration_seconds))
            dur_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            if entry.is_missing:
                err_fg = QColor(COLOR_DANGER_SOFT)
                for cell_item in (title_item, artist_item, path_item):
                    cell_item.setForeground(err_fg)

            self.table.setItem(row, 2, title_item)
            self.table.setItem(row, 3, artist_item)
            self.table.setItem(row, 4, path_item)
            self.table.setItem(row, 5, dur_item)

            self._attach_entry_actions(row, entry_idx, entry)

        self._update_move_buttons_state()

    def _attach_entry_actions(self, row: int, entry_idx: int, entry: PlaylistEntryRecord) -> None:
        """Ajoute les boutons Relocaliser / Retirer dans la colonne Actions."""
        cell = QWidget()
        layout = QHBoxLayout(cell)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if entry.is_missing or self._is_cue:
            btn_relocate = QPushButton("🔍")
            btn_relocate.setToolTip(tr("playlist_editor.tooltip_relocate"))
            btn_relocate.setFixedSize(28, 24)
            btn_relocate.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_relocate.setStyleSheet("QPushButton { background: transparent; border: none; font-size: 13px; }")
            btn_relocate.clicked.connect(lambda _c=False, idx=entry_idx: self._relocate_entry_at(idx))
            layout.addWidget(btn_relocate)

        if not self._is_cue:
            btn_remove = QPushButton("🗑️")
            btn_remove.setToolTip(tr("playlist_editor.tooltip_remove"))
            btn_remove.setFixedSize(28, 24)
            btn_remove.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_remove.setStyleSheet("QPushButton { background: transparent; border: none; font-size: 13px; }")
            btn_remove.clicked.connect(lambda _c=False, idx=entry_idx: self._remove_entry_at(idx))
            layout.addWidget(btn_remove)

        self.table.setCellWidget(row, 6, cell)

    def _entry_index_for_row(self, row: int) -> int | None:
        """Retourne l'index dans self._entries correspondant à une ligne du tableau."""
        item = self.table.item(row, 0)
        if item is None:
            return None
        val = item.data(Qt.ItemDataRole.UserRole)
        return int(val) if isinstance(val, int) else None

    def _move_selected(self, delta: int) -> None:
        """Déplace la piste sélectionnée vers le haut (-1) ou vers le bas (+1)."""
        if self._is_cue or self._show_errors_only:
            return
        row = self.table.currentRow()
        new_row = row + delta
        if row < 0 or new_row < 0 or new_row >= len(self._entries):
            return
        self._entries[row], self._entries[new_row] = self._entries[new_row], self._entries[row]
        self._modified = True
        self._populate_table()
        self.table.selectRow(new_row)

    def _remove_entry_at(self, entry_idx: int) -> None:
        """Retire une entrée de la liste en mémoire."""
        if self._is_cue or not (0 <= entry_idx < len(self._entries)):
            return
        self._entries.pop(entry_idx)
        self._modified = True
        self._populate_table()

    def _on_clean_missing(self) -> None:
        """Retire toutes les entrées marquées introuvables."""
        if self._is_cue:
            return
        before = len(self._entries)
        self._entries = [e for e in self._entries if not e.is_missing]
        if len(self._entries) != before:
            self._modified = True
            self._populate_table()

    def _relocate_entry_at(self, entry_idx: int) -> None:
        """Permet à l'utilisateur de sélectionner le fichier audio manquant."""
        if not (0 <= entry_idx < len(self._entries)):
            return
        entry = self._entries[entry_idx]
        start_dir = str(Path(self.playlist.file_path).parent) if self.playlist.file_path else ""
        chosen, _ = QFileDialog.getOpenFileName(
            self,
            tr("playlist_editor.relocate_dialog_title"),
            start_dir,
            tr("playlist_editor.relocate_filter"),
        )
        if not chosen:
            return

        new_path = Path(chosen)
        if self._is_cue and entry.raw_path:
            self._pending_cue_replacements[entry.raw_path] = new_path

        # Met à jour l'entrée (et toute autre entrée pointant vers le même raw_path manquant)
        self._apply_relocated_path(entry_idx, new_path)
        self._modified = True
        self._populate_table()

    def _apply_relocated_path(self, entry_idx: int, new_path: Path) -> None:
        """Met à jour une entrée manquante (et ses doublons) avec le nouveau chemin."""
        entry = self._entries[entry_idx]
        old_raw = entry.raw_path
        pl_dir = Path(self.playlist.file_path).parent if self.playlist.file_path else None
        try:
            rel_raw = (
                os.path.relpath(str(new_path), str(pl_dir)) if (pl_dir and self._prefer_relative) else str(new_path)
            )
        except ValueError:
            rel_raw = str(new_path)

        for item in self._entries:
            if item is entry or (item.is_missing and old_raw and item.raw_path == old_raw):
                item.raw_path = rel_raw.replace("\\", "/")
                item.resolved_path = str(new_path)
                item.is_missing = False
                if not item.title:
                    item.title = new_path.stem

    def _on_save(self) -> None:
        """Écrit la playlist modifiée sur disque et met à jour la base hors thread UI."""
        self.repair_panel.stop_worker()
        if self._is_cue and not self._pending_cue_replacements:
            self.accept()
            return
        if not self._entries:
            QMessageBox.warning(
                self,
                tr("playlist_editor.empty_save_title"),
                tr("playlist_editor.empty_save_msg"),
            )
            return

        dest = Path(self.playlist.file_path)
        self.btn_save.setEnabled(False)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        save_error: list[str] = []
        loop = QEventLoop(self)
        thread = QThread(self)
        worker = PlaylistSaveWorker(
            self.db,
            dest,
            list(self._entries),
            relative_paths=self._prefer_relative,
            cue_replacements=dict(self._pending_cue_replacements) if self._is_cue else None,
        )
        worker.moveToThread(thread)

        def _on_error(msg: str) -> None:
            save_error.append(msg)
            loop.quit()

        thread.started.connect(worker.run)
        worker.finished.connect(loop.quit)
        worker.error.connect(_on_error)
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        thread.start()
        loop.exec()
        thread.wait(2000)

        QApplication.restoreOverrideCursor()
        self.btn_save.setEnabled(True)

        if save_error:
            QMessageBox.critical(
                self,
                tr("playlist_editor.save_error_title"),
                tr("playlist_editor.save_error_msg", error=save_error[0]),
            )
            return

        self._modified = True
        self.accept()
