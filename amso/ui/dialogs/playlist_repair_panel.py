"""Panneau et worker de recherche automatique pour la réparation de playlist."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtGui import QColor, QPaintEvent, QWheelEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QStyle,
    QStyleOptionComboBox,
    QStylePainter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from amso.core.database import DatabaseManager, PlaylistEntryRecord
from amso.core.i18n import tr
from amso.core.playlist_exporter import (
    entries_to_track_records,
    export_playlist,
    index_exported_playlist_in_db,
    replace_cue_file_target,
)
from amso.core.playlist_parser import ParsedPlaylistEntry
from amso.core.playlist_repair import (
    AUTO_CHECK_SCORE,
    EntryRepairProposal,
    RepairCandidate,
    enrich_proposals_with_db,
    find_local_repair_proposals,
    find_most_effective_folder,
)

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


class _NoWheelComboBox(QComboBox):
    """QComboBox ignorant la molette et masquant le % quand la liste est fermée."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._compact_texts: list[str] = []

    def add_candidate_item(self, compact_text: str, popup_text: str, user_data: object) -> None:
        """Ajoute un candidat avec libellé compact (fermé) et libellé avec score (menu déroulé)."""
        self._compact_texts.append(compact_text)
        self.addItem(popup_text, user_data)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QStylePainter(self)
        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        idx = self.currentIndex()
        if 0 <= idx < len(self._compact_texts):
            opt.currentText = self._compact_texts[idx]
        painter.drawComplexControl(QStyle.ComplexControl.CC_ComboBox, opt)
        painter.drawControl(QStyle.ControlElement.CE_ComboBoxLabel, opt)

    def wheelEvent(self, event: QWheelEvent) -> None:
        event.ignore()


class PlaylistRepairWorker(QObject):
    """Worker exécuté en arrière-plan pour rechercher les fichiers manquants."""

    progress = Signal(int, int)
    local_complete = Signal(list)
    finished = Signal(list)
    error = Signal(str)

    def __init__(
        self,
        db: DatabaseManager,
        playlist_file_path: str,
        entries: list[PlaylistEntryRecord],
        *,
        db_only_proposals: list[EntryRepairProposal] | None = None,
    ) -> None:
        super().__init__()
        self._db = db
        self._playlist_file_path = playlist_file_path
        self._entries = entries
        self._db_only_proposals = db_only_proposals
        self._cancelled = False

    def cancel(self) -> None:
        """Demande l'arrêt propre de la recherche."""
        self._cancelled = True

    def run(self) -> None:
        """Exécute la passe locale puis, si nécessaire, la passe base de données."""
        try:
            worker_db = self._db if self._db.db_path == ":memory:" else DatabaseManager(self._db.db_path)

            if self._db_only_proposals is not None:
                enriched = enrich_proposals_with_db(
                    worker_db,
                    self._playlist_file_path,
                    self._db_only_proposals,
                    cancel_check=lambda: self._cancelled,
                    progress_cb=lambda done, total: self.progress.emit(done, total),
                )
                self.finished.emit(enriched)
                return

            local_proposals = find_local_repair_proposals(
                self._playlist_file_path,
                self._entries,
                cancel_check=lambda: self._cancelled,
                progress_cb=lambda done, total: self.progress.emit(done, total),
            )
            if self._cancelled:
                self.finished.emit(local_proposals)
                return

            all_resolved_locally = bool(local_proposals) and all(
                p.best is not None and p.best.score >= AUTO_CHECK_SCORE for p in local_proposals
            )
            if all_resolved_locally:
                self.local_complete.emit(local_proposals)
                return

            enriched = enrich_proposals_with_db(
                worker_db,
                self._playlist_file_path,
                local_proposals,
                cancel_check=lambda: self._cancelled,
                progress_cb=lambda done, total: self.progress.emit(done, total),
            )
            self.finished.emit(enriched)
        except Exception as exc:
            logger.exception("Erreur dans PlaylistRepairWorker")
            self.error.emit(str(exc))


class PlaylistSaveWorker(QObject):
    """Worker exécuté en arrière-plan pour écrire la playlist et la réindexer sans figer l'UI."""

    finished = Signal()
    error = Signal(str)

    def __init__(
        self,
        db: DatabaseManager,
        dest: Path,
        entries: list[PlaylistEntryRecord],
        *,
        relative_paths: bool,
        cue_replacements: dict[str, Path] | None = None,
    ) -> None:
        super().__init__()
        self._db = db
        self._dest = dest
        self._entries = entries
        self._relative_paths = relative_paths
        self._cue_replacements = cue_replacements

    def run(self) -> None:
        """Exporte le fichier playlist (ou met à jour les FILE d'un CUE) et réindexe hors thread UI."""
        try:
            if self._cue_replacements is not None:
                for old_raw, new_path in self._cue_replacements.items():
                    if not replace_cue_file_target(self._dest, old_raw, new_path):
                        raise RuntimeError(tr("playlist_editor.cue_relocate_error"))
            else:
                tracks = entries_to_track_records(self._entries)
                export_playlist(tracks, self._dest, relative_paths=self._relative_paths)

            precomputed = [
                ParsedPlaylistEntry(
                    position=idx,
                    raw_path=entry.raw_path,
                    resolved_path=entry.resolved_path,
                    title=entry.title,
                    artist=entry.artist,
                    duration_seconds=entry.duration_seconds,
                    is_missing=entry.is_missing,
                    start_ms=entry.start_ms,
                    end_ms=entry.end_ms,
                )
                for idx, entry in enumerate(self._entries, start=1)
            ]
            worker_db = self._db if self._db.db_path == ":memory:" else DatabaseManager(self._db.db_path)
            index_exported_playlist_in_db(worker_db, self._dest, precomputed_entries=precomputed)
            self.finished.emit()
        except Exception as exc:
            logger.exception("Erreur lors de l'enregistrement asynchrone de %s", self._dest)
            self.error.emit(str(exc))


class PlaylistRepairPanel(QWidget):
    """Onglet affichant les propositions de réparation avec validation par cases à cocher."""

    apply_requested = Signal(object)  # {entry_index: resolved_path}
    manual_relocate_requested = Signal(int)  # entry_index
    search_finished = Signal(int)  # matched_count

    def __init__(
        self,
        db: DatabaseManager,
        playlist_file_path: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._db = db
        self._playlist_file_path = playlist_file_path
        self._playlist_dir = Path(playlist_file_path).parent if playlist_file_path else None
        self._playlist_dir_norm = os.path.normcase(str(self._playlist_dir)) if self._playlist_dir else ""
        self._proposals: list[EntryRepairProposal] = []
        self._best_folder_path: str = ""
        self._best_folder_count: int = 0
        self._row_checkboxes: list[QCheckBox | None] = []
        self._row_combos: list[QComboBox | None] = []
        self._thread: QThread | None = None
        self._worker: PlaylistRepairWorker | None = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Construit les contrôles de l'onglet Propositions."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Barre d'état + boutons de sélection
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        self.lbl_status = QLabel()
        self.lbl_status.setStyleSheet("color: #CBD5E1; font-size: 12.5px; font-weight: 600;")
        top_bar.addWidget(self.lbl_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(180)
        self.progress_bar.setFixedHeight(14)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        top_bar.addWidget(self.progress_bar)

        top_bar.addStretch()

        self.btn_check_all = QPushButton(tr("playlist_editor.repair_btn_check_all"))
        self.btn_check_all.setProperty("class", "secondary-btn")
        self.btn_check_all.clicked.connect(lambda: self._set_all_checked(True))
        top_bar.addWidget(self.btn_check_all)

        self.btn_uncheck_all = QPushButton(tr("playlist_editor.repair_btn_uncheck_all"))
        self.btn_uncheck_all.setProperty("class", "secondary-btn")
        self.btn_uncheck_all.clicked.connect(lambda: self._set_all_checked(False))
        top_bar.addWidget(self.btn_uncheck_all)

        self.btn_check_sure = QPushButton(tr("playlist_editor.repair_btn_check_sure"))
        self.btn_check_sure.setProperty("class", "secondary-btn")
        self.btn_check_sure.clicked.connect(self._check_sure_only)
        top_bar.addWidget(self.btn_check_sure)

        self.btn_apply = QPushButton(tr("playlist_editor.repair_btn_apply", count=0))
        self.btn_apply.setProperty("class", "primary-btn")
        self.btn_apply.clicked.connect(self._on_apply_clicked)
        top_bar.addWidget(self.btn_apply)

        layout.addLayout(top_bar)

        # Tableau des propositions (colonnes 2 et 3 extensibles sur toute la largeur)
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            [
                tr("playlist_editor.repair_col_apply"),
                tr("playlist_editor.col_pos"),
                tr("playlist_editor.repair_col_missing"),
                tr("playlist_editor.repair_col_proposal"),
                tr("playlist_editor.repair_col_confidence"),
                tr("settings.col_source_actions"),
            ]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(38)
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
        for col, width in ((0, 62), (1, 44), (4, 92), (5, 64)):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(col, width)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table, 1)

        # Barre inférieure de sélection de masse par stratégie (boutons radio)
        radio_bar = QHBoxLayout()
        radio_bar.setSpacing(16)

        self._mode_group = QButtonGroup(self)
        self.radio_playlist_dir = QRadioButton(tr("playlist_editor.repair_mode_playlist_dir", matched=0, total=0))
        self.radio_playlist_dir.setChecked(True)
        self.radio_best_dir = QRadioButton(tr("playlist_editor.repair_mode_best_dir_none"))
        self.radio_best_dir.setEnabled(False)
        self.radio_exact_100 = QRadioButton(tr("playlist_editor.repair_mode_exact_100", matched=0, total=0))
        self.radio_exact_100.setEnabled(False)

        radio_qss = "QRadioButton { color: #CBD5E1; font-size: 12px; } QRadioButton:disabled { color: #64748B; }"
        for idx, rb in enumerate((self.radio_playlist_dir, self.radio_best_dir, self.radio_exact_100)):
            rb.setStyleSheet(radio_qss)
            self._mode_group.addButton(rb, idx)
            radio_bar.addWidget(rb)
        radio_bar.addStretch()
        self._mode_group.idClicked.connect(self._on_strategy_changed)
        layout.addLayout(radio_bar)

        self._update_controls_state()

    def start_search(self, entries: list[PlaylistEntryRecord]) -> None:
        """Lance la recherche de propositions dans un QThread dédié."""
        self._launch_worker(entries=list(entries), db_only_proposals=None)

    def _launch_worker(
        self,
        *,
        entries: list[PlaylistEntryRecord],
        db_only_proposals: list[EntryRepairProposal] | None,
    ) -> None:
        self.stop_worker()
        missing_count = (
            len(db_only_proposals) if db_only_proposals is not None else sum(1 for e in entries if e.is_missing)
        )
        if db_only_proposals is None:
            self._proposals = []
            self._populate_table()

        self.progress_bar.setRange(0, max(1, missing_count))
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.lbl_status.setText(tr("playlist_editor.repair_searching", done=0, total=missing_count))
        self._update_controls_state()

        thread = QThread(self)
        worker = PlaylistRepairWorker(
            self._db,
            self._playlist_file_path,
            entries,
            db_only_proposals=db_only_proposals,
        )
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.progress.connect(self._on_worker_progress)
        worker.local_complete.connect(self._on_local_complete)
        worker.finished.connect(self._on_worker_finished)
        worker.error.connect(self._on_worker_error)
        worker.local_complete.connect(thread.quit)
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_worker_refs)

        self._thread = thread
        self._worker = worker
        thread.start()

    def stop_worker(self) -> None:
        """Interrompt proprement la recherche en cours (ex. fermeture du dialogue)."""
        if self._worker is not None:
            self._worker.cancel()
        if self._thread is not None and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait(2000)

    def _clear_worker_refs(self) -> None:
        self._worker = None
        self._thread = None

    def _on_worker_progress(self, done: int, total: int) -> None:
        self.progress_bar.setValue(done)
        self.lbl_status.setText(tr("playlist_editor.repair_searching", done=done, total=total))

    def _on_local_complete(self, proposals: list[EntryRepairProposal]) -> None:
        """Affiche les résultats locaux et propose de s'arrêter là si 100 % sont trouvés."""
        self._on_worker_finished(proposals)

        total = len(proposals)
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Question)
        box.setWindowTitle(tr("playlist_editor.repair_local_complete_title"))
        box.setText(tr("playlist_editor.repair_local_complete_msg", count=total, total=total))
        btn_stop = box.addButton(tr("playlist_editor.repair_btn_stop_here"), QMessageBox.ButtonRole.AcceptRole)
        btn_continue = box.addButton(tr("playlist_editor.repair_btn_continue_db"), QMessageBox.ButtonRole.ActionRole)
        box.setDefaultButton(btn_stop)
        box.exec()

        if box.clickedButton() == btn_continue:
            self._launch_worker(entries=[], db_only_proposals=proposals)

    def _on_worker_finished(self, proposals: list[EntryRepairProposal]) -> None:
        self.progress_bar.hide()
        self._proposals = proposals
        self._best_folder_path, self._best_folder_count = find_most_effective_folder(proposals, self._playlist_dir)
        self._update_strategy_radios_and_select_default()
        self._populate_table()
        self._apply_strategy(self._mode_group.checkedId())
        matched = sum(1 for p in proposals if p.best is not None)
        self.lbl_status.setText(tr("playlist_editor.repair_summary", matched=matched, total=len(proposals)))
        self.search_finished.emit(matched)

    def _on_worker_error(self, message: str) -> None:
        self.progress_bar.hide()
        self.lbl_status.setText(tr("playlist_editor.repair_error", error=message))
        self._update_controls_state()

    def _update_strategy_radios_and_select_default(self) -> None:
        total = len(self._proposals)
        playlist_dir_count = (
            sum(
                1
                for prop in self._proposals
                if any(os.path.normcase(str(Path(c.path).parent)) == self._playlist_dir_norm for c in prop.candidates)
            )
            if self._playlist_dir_norm
            else 0
        )
        exact_100_count = sum(1 for prop in self._proposals if any(c.score == 100 for c in prop.candidates))

        self.radio_playlist_dir.setText(
            tr("playlist_editor.repair_mode_playlist_dir", matched=playlist_dir_count, total=total)
        )
        self.radio_playlist_dir.setEnabled(playlist_dir_count > 0)

        self.radio_exact_100.setText(tr("playlist_editor.repair_mode_exact_100", matched=exact_100_count, total=total))
        self.radio_exact_100.setEnabled(exact_100_count > 0)

        if self._best_folder_path and self._best_folder_count > 0:
            folder_name = Path(self._best_folder_path).name or self._best_folder_path
            self.radio_best_dir.setText(
                tr(
                    "playlist_editor.repair_mode_best_dir",
                    folder=folder_name,
                    matched=self._best_folder_count,
                    total=total,
                )
            )
            self.radio_best_dir.setToolTip(self._best_folder_path)
            self.radio_best_dir.setEnabled(True)
        else:
            self.radio_best_dir.setText(tr("playlist_editor.repair_mode_best_dir_none"))
            self.radio_best_dir.setToolTip("")
            self.radio_best_dir.setEnabled(False)

        # Sélection par défaut : dossier de la playlist si efficace, sinon dossier le plus efficace
        if playlist_dir_count > 0 and playlist_dir_count >= self._best_folder_count:
            self.radio_playlist_dir.setChecked(True)
        elif self._best_folder_count > 0 and (
            (total > 0 and self._best_folder_count * 2 >= total)
            or (playlist_dir_count == 0 and self._best_folder_count >= 2)
        ):
            self.radio_best_dir.setChecked(True)
        elif exact_100_count > 0:
            self.radio_exact_100.setChecked(True)
        elif playlist_dir_count > 0:
            self.radio_playlist_dir.setChecked(True)
        elif self._best_folder_count > 0:
            self.radio_best_dir.setChecked(True)

    def _format_candidate_label(self, cand: RepairCandidate) -> str:
        """Formate le libellé d'un candidat (chemin relatif si possible + durée)."""
        display_path = cand.path
        if self._playlist_dir is not None:
            try:
                rel = os.path.relpath(cand.path, str(self._playlist_dir))
                if not rel.startswith(".."):
                    display_path = rel.replace("\\", "/")
            except ValueError:
                pass
        dur = _format_duration_short(cand.duration_seconds)
        return f"{display_path}  ({dur})" if dur != "-" else display_path

    @staticmethod
    def _candidate_tooltip(cand: RepairCandidate) -> str:
        """Retourne l'infobulle avec le chemin complet et la source du candidat."""
        source_lbl = (
            tr("playlist_editor.repair_source_local")
            if cand.source_kind == "local_dir"
            else tr("playlist_editor.repair_source_db")
        )
        return f"{cand.path}\n({source_lbl})"

    def _populate_table(self) -> None:
        """Remplit le tableau avec les propositions calculées."""
        self._row_checkboxes.clear()
        self._row_combos.clear()
        self.table.setRowCount(len(self._proposals))

        for row, prop in enumerate(self._proposals):
            entry = prop.entry
            best = prop.best

            cb: QCheckBox | None = None
            if best is not None:
                cb_wrap = QWidget()
                cb_layout = QHBoxLayout(cb_wrap)
                cb_layout.setContentsMargins(0, 0, 0, 0)
                cb_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cb = QCheckBox()
                cb.stateChanged.connect(lambda _s: self._update_controls_state())
                cb_layout.addWidget(cb)
                self.table.setCellWidget(row, 0, cb_wrap)
            self._row_checkboxes.append(cb)

            pos_item = QTableWidgetItem(str(prop.entry_index + 1))
            pos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, pos_item)

            orig_label = entry.raw_path or entry.resolved_path or "-"
            dur_str = _format_duration_short(entry.duration_seconds)
            missing_text = f"{orig_label}  ({dur_str})" if dur_str != "-" else orig_label
            missing_item = QTableWidgetItem(missing_text)
            missing_item.setForeground(QColor("#FCA5A5"))
            full_missing = entry.resolved_path or orig_label
            missing_item.setToolTip(f"{entry.title or '-'} — {entry.artist or '-'}\n{full_missing}")
            self.table.setItem(row, 2, missing_item)

            combo: QComboBox | None = None
            if not prop.candidates:
                none_item = QTableWidgetItem(tr("playlist_editor.repair_no_match"))
                none_item.setForeground(QColor("#64748B"))
                self.table.setItem(row, 3, none_item)
            elif len(prop.candidates) == 1:
                cand = prop.candidates[0]
                prop_item = QTableWidgetItem(self._format_candidate_label(cand))
                prop_item.setToolTip(self._candidate_tooltip(cand))
                self.table.setItem(row, 3, prop_item)
            else:
                combo = _NoWheelComboBox()
                for cand_idx, cand in enumerate(prop.candidates):
                    label = self._format_candidate_label(cand)
                    combo.add_candidate_item(label, f"[{cand.score} %] {label}", cand.path)
                    combo.setItemData(cand_idx, self._candidate_tooltip(cand), Qt.ItemDataRole.ToolTipRole)
                combo.setToolTip(self._candidate_tooltip(prop.candidates[0]))
                combo.currentIndexChanged.connect(lambda idx, r=row, p=prop: self._on_combo_changed(r, p, idx))
                self.table.setCellWidget(row, 3, combo)
            self._row_combos.append(combo)

            self._set_confidence_cell(row, best)

            act_wrap = QWidget()
            act_layout = QHBoxLayout(act_wrap)
            act_layout.setContentsMargins(4, 2, 4, 2)
            act_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_relocate = QPushButton("🔍")
            btn_relocate.setToolTip(tr("playlist_editor.tooltip_relocate"))
            btn_relocate.setFixedSize(28, 24)
            btn_relocate.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_relocate.setStyleSheet("QPushButton { background: transparent; border: none; font-size: 13px; }")
            btn_relocate.clicked.connect(
                lambda _c=False, idx=prop.entry_index: self.manual_relocate_requested.emit(idx)
            )
            act_layout.addWidget(btn_relocate)
            self.table.setCellWidget(row, 5, act_wrap)

        self._update_controls_state()

    def _on_strategy_changed(self, mode_id: int) -> None:
        self._apply_strategy(mode_id)

    def _apply_strategy(self, mode_id: int) -> None:
        """Sélectionne les candidats dans les menus et pré-coche selon le mode radio actif."""
        if not self._proposals:
            return

        target_dir_norm = ""
        if mode_id == 0:
            target_dir_norm = self._playlist_dir_norm
        elif mode_id == 1 and self._best_folder_path:
            target_dir_norm = os.path.normcase(self._best_folder_path)

        # Choisit le meilleur index de candidat par ligne selon la stratégie
        chosen_candidates: list[tuple[int, RepairCandidate | None]] = []
        for row, prop in enumerate(self._proposals):
            if not prop.candidates:
                chosen_candidates.append((row, None))
                continue
            cand_idx = 0
            if target_dir_norm:
                for idx, cand in enumerate(prop.candidates):
                    if os.path.normcase(str(Path(cand.path).parent)) == target_dir_norm:
                        cand_idx = idx
                        break
            combo = self._row_combos[row]
            if combo is not None and combo.currentIndex() != cand_idx:
                combo.setCurrentIndex(cand_idx)
            chosen_candidates.append((row, prop.candidates[cand_idx]))

        # Pré-coche sans collision de chemin cible
        claimed_paths: set[str] = set()
        ranked = sorted(
            ((row, cand) for row, cand in chosen_candidates if cand is not None),
            key=lambda item: item[1].score,
            reverse=True,
        )
        checked_rows: set[int] = set()
        duplicate_rows: set[int] = set()
        for row, cand in ranked:
            norm_path = os.path.normcase(os.path.abspath(cand.path))
            if norm_path in claimed_paths:
                duplicate_rows.add(row)
                continue
            in_target = bool(target_dir_norm) and os.path.normcase(str(Path(cand.path).parent)) == target_dir_norm
            should_check = False
            if mode_id == 2:
                should_check = cand.score == 100
            else:
                should_check = in_target and cand.score >= AUTO_CHECK_SCORE

            if should_check:
                checked_rows.add(row)
                claimed_paths.add(norm_path)

        for row, cb in enumerate(self._row_checkboxes):
            if cb is None:
                continue
            cb.blockSignals(True)
            cb.setChecked(row in checked_rows)
            cb.setToolTip(tr("playlist_editor.repair_duplicate_tooltip") if row in duplicate_rows else "")
            cb.blockSignals(False)
        self._update_controls_state()

    def _set_confidence_cell(self, row: int, cand: RepairCandidate | None) -> None:
        if cand is None:
            item = QTableWidgetItem("-")
            item.setForeground(QColor("#64748B"))
        else:
            item = QTableWidgetItem(f"{cand.score} %")
            item.setForeground(QColor("#4ADE80") if cand.score >= AUTO_CHECK_SCORE else QColor("#FBBF24"))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 4, item)

    def _on_combo_changed(self, row: int, prop: EntryRepairProposal, combo_idx: int) -> None:
        if 0 <= combo_idx < len(prop.candidates):
            cand = prop.candidates[combo_idx]
            self._set_confidence_cell(row, cand)
            combo = self._row_combos[row]
            if combo is not None:
                combo.setToolTip(self._candidate_tooltip(cand))

    def _set_all_checked(self, checked: bool) -> None:
        for cb in self._row_checkboxes:
            if cb is not None:
                cb.setChecked(checked)

    def _check_sure_only(self) -> None:
        for row, prop in enumerate(self._proposals):
            cb = self._row_checkboxes[row]
            if cb is None:
                continue
            cand = self._selected_candidate_for_row(row, prop)
            cb.setChecked(cand is not None and cand.score >= AUTO_CHECK_SCORE)

    def _selected_candidate_for_row(self, row: int, prop: EntryRepairProposal) -> RepairCandidate | None:
        if not prop.candidates:
            return None
        combo = self._row_combos[row]
        if combo is not None:
            idx = combo.currentIndex()
            if 0 <= idx < len(prop.candidates):
                return prop.candidates[idx]
        return prop.best

    def _selected_count(self) -> int:
        return sum(1 for cb in self._row_checkboxes if cb is not None and cb.isChecked())

    def _update_controls_state(self) -> None:
        has_any = any(cb is not None for cb in self._row_checkboxes)
        selected = self._selected_count()
        self.btn_check_all.setEnabled(has_any)
        self.btn_uncheck_all.setEnabled(has_any)
        self.btn_check_sure.setEnabled(has_any)
        self.btn_apply.setText(tr("playlist_editor.repair_btn_apply", count=selected))
        self.btn_apply.setEnabled(selected > 0)

    def _on_apply_clicked(self) -> None:
        mapping: dict[int, str] = {}
        for row, prop in enumerate(self._proposals):
            cb = self._row_checkboxes[row]
            if cb is None or not cb.isChecked():
                continue
            cand = self._selected_candidate_for_row(row, prop)
            if cand is not None:
                mapping[prop.entry_index] = cand.path
        if mapping:
            self.apply_requested.emit(mapping)
