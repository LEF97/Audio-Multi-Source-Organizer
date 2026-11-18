"""Page Gestion de la bibliothèque > Sources (mixin de MainWindow)."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)

from amso.core.database import (
    PlaylistSummaryRecord,
    SourceLibrarySummary,
    SourceRecord,
    SourceType,
)
from amso.core.i18n import tr
from amso.ui.dialogs import PlaylistEditorDialog, send_file_to_trash
from amso.ui.pages.library_sources_tree import LibrarySourcesTreeMixin, _format_count
from amso.ui.styles import (
    COLOR_BG_CARD,
    COLOR_BG_HOVER,
    COLOR_BORDER,
    COLOR_DANGER_SOFT,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_TEXT_BRIGHT,
    COLOR_TEXT_MUTED,
    make_tree_action_button,
)
from amso.ui.widgets.page_header import build_page_top_bar

logger = logging.getLogger(__name__)


def _tab_segment_qss() -> str:
    """QSS des boutons d'onglet segmentés (Par source / Bibliothèque)."""
    return (
        f"QPushButton {{ background-color: {COLOR_BG_CARD}; color: {COLOR_TEXT_MUTED}; "
        f"border: 1px solid {COLOR_BORDER}; border-radius: 5px; padding: 4px 12px; "
        f"font-size: 12px; font-weight: 600; }} "
        f"QPushButton:hover {{ background-color: {COLOR_BG_HOVER}; color: {COLOR_TEXT_BRIGHT}; "
        f"border-color: {COLOR_PRIMARY_HOVER}; }} "
        f"QPushButton:checked {{ background-color: {COLOR_PRIMARY}; color: #FFFFFF; "
        f"border-color: {COLOR_PRIMARY_HOVER}; }}"
    )


class _PathProbeWorker(QThread):
    """Vérifie l'accessibilité des chemins sources et playlists hors du thread UI."""

    probe_finished = Signal(int, dict)

    def __init__(self, generation: int, paths: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._generation = generation
        self._paths = paths

    def run(self) -> None:
        results: dict[str, bool] = {}
        for path in self._paths:
            if not path:
                continue
            try:
                results[path] = os.path.exists(path)
            except OSError:
                results[path] = False
        self.probe_finished.emit(self._generation, results)


if TYPE_CHECKING:
    from PySide6.QtWidgets import QMainWindow

    _MixinBase = QMainWindow
else:
    _MixinBase = object


class LibrarySourcesPageMixin(LibrarySourcesTreeMixin, _MixinBase):
    """Page Gestion de la bibliothèque > Sources (arborescence sources/formats/playlists)."""

    if TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any: ...

    def _create_library_sources_page(self) -> QWidget:
        """Construit la page Gestion de la bibliothèque > Sources."""
        self._lib_sources_probe_generation = 0
        self._lib_sources_probe_worker: _PathProbeWorker | None = None
        self._lib_sources_path_status: dict[str, bool] = {}
        self._lib_sources_filter_anomalies = False
        self._lib_sources_view_mode = "sources"

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        top_bar, self.lbl_library_sources_page_title, self.btn_sources_help = build_page_top_bar(
            tr("settings.page_sources_title"),
            "library_sources.help_title",
            "library_sources.help_body",
        )
        main_layout.addWidget(top_bar, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Bandeau d'état / anomalies global en haut de page
        self.card_lib_sources_health = QFrame()
        self.card_lib_sources_health.setObjectName("libSourcesHealthCard")
        self.card_lib_sources_health.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        l_health = QHBoxLayout(self.card_lib_sources_health)
        l_health.setContentsMargins(16, 12, 16, 12)
        l_health.setSpacing(12)

        l_health_text = QVBoxLayout()
        l_health_text.setContentsMargins(0, 0, 0, 0)
        l_health_text.setSpacing(4)

        self.lbl_lib_health_title = QLabel()
        self.lbl_lib_health_title.setStyleSheet("font-size: 13.5px; font-weight: 700;")
        l_health_text.addWidget(self.lbl_lib_health_title)

        self.lbl_lib_health_details = QLabel()
        self.lbl_lib_health_details.setWordWrap(True)
        self.lbl_lib_health_details.setStyleSheet("font-size: 12.5px;")
        l_health_text.addWidget(self.lbl_lib_health_details)

        l_health.addLayout(l_health_text, 1)

        self.btn_lib_show_anomalies = QPushButton(tr("library_sources.btn_show_anomalies"))
        self.btn_lib_show_anomalies.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lib_show_anomalies.setStyleSheet(
            "QPushButton { background-color: #7F1D1D; color: #FEE2E2; border: 1px solid #B91C1C; "
            "border-radius: 6px; padding: 6px 14px; font-size: 12.5px; font-weight: 600; } "
            "QPushButton:hover { background-color: #991B1B; border-color: #DC2626; } "
            "QPushButton:pressed { background-color: #B91C1C; }"
        )
        self.btn_lib_show_anomalies.clicked.connect(self._on_toggle_library_anomalies_filter)
        self.btn_lib_show_anomalies.setVisible(False)
        l_health.addWidget(self.btn_lib_show_anomalies, 0, Qt.AlignmentFlag.AlignVCenter)

        content_layout.addWidget(self.card_lib_sources_health, 0)

        card_sources = QFrame()
        card_sources.setProperty("class", "dashboard-card")
        card_sources.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        l_sources = QVBoxLayout(card_sources)
        l_sources.setContentsMargins(18, 16, 18, 16)
        l_sources.setSpacing(10)

        sources_header_row = QHBoxLayout()
        sources_header_row.setContentsMargins(0, 0, 0, 0)
        sources_header_row.setSpacing(6)

        self.lbl_lib_sources_card_title = QLabel(tr("settings.section_sources_title"))
        self.lbl_lib_sources_card_title.setStyleSheet(f"color: {COLOR_TEXT_BRIGHT}; font-size: 14px; font-weight: 700;")
        self.lbl_lib_sources_card_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sources_header_row.addWidget(self.lbl_lib_sources_card_title)
        sources_header_row.addStretch()

        self.lib_sources_tab_group = QButtonGroup(self)
        self.lib_sources_tab_group.setExclusive(True)
        tab_qss = _tab_segment_qss()

        self.btn_lib_tab_sources = QPushButton(tr("library_sources.tab_by_source"))
        self.btn_lib_tab_sources.setCheckable(True)
        self.btn_lib_tab_sources.setChecked(True)
        self.btn_lib_tab_sources.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lib_tab_sources.setStyleSheet(tab_qss)
        self.btn_lib_tab_sources.clicked.connect(lambda: self._set_library_sources_view_mode("sources"))
        self.lib_sources_tab_group.addButton(self.btn_lib_tab_sources)
        sources_header_row.addWidget(self.btn_lib_tab_sources)

        self.btn_lib_tab_library = QPushButton(tr("library_sources.tab_library"))
        self.btn_lib_tab_library.setCheckable(True)
        self.btn_lib_tab_library.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lib_tab_library.setStyleSheet(tab_qss)
        self.btn_lib_tab_library.clicked.connect(lambda: self._set_library_sources_view_mode("library"))
        self.lib_sources_tab_group.addButton(self.btn_lib_tab_library)
        sources_header_row.addWidget(self.btn_lib_tab_library)

        self.btn_expand_lib_sources = make_tree_action_button("⊞", tr("folders.btn_expand_all"))
        self.btn_expand_lib_sources.clicked.connect(lambda: self._set_library_sources_all_expanded(True))
        sources_header_row.addWidget(self.btn_expand_lib_sources)

        self.btn_collapse_lib_sources = make_tree_action_button("⊟", tr("folders.btn_collapse_all"))
        self.btn_collapse_lib_sources.clicked.connect(lambda: self._set_library_sources_all_expanded(False))
        sources_header_row.addWidget(self.btn_collapse_lib_sources)

        l_sources.addLayout(sources_header_row)

        self.lbl_lib_sources_card_desc = QLabel(tr("settings.section_sources_desc"))
        self.lbl_lib_sources_card_desc.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        self.lbl_lib_sources_card_desc.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        l_sources.addWidget(self.lbl_lib_sources_card_desc)

        self.tree_library_sources = QTreeWidget()
        self.tree_library_sources.setColumnCount(8)
        self.tree_library_sources.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tree_library_sources.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree_library_sources.setUniformRowHeights(True)
        self.tree_library_sources.setIndentation(18)
        self.tree_library_sources.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.tree_library_sources.setMinimumHeight(260)
        self.tree_library_sources.setStyleSheet(
            "QTreeWidget { background-color: #0F172A; border: 1px solid #334155; border-radius: 6px; "
            "color: #E2E8F0; outline: none; } "
            "QTreeWidget::item { height: 34px; border-bottom: 1px solid #1E293B; padding: 2px 4px; } "
            "QTreeWidget::item:hover { background-color: #1E293B; } "
            "QHeaderView::section { background-color: #1E293B; color: #94A3B8; font-weight: 600; "
            "padding: 8px 6px; border: none; }"
        )
        self.tree_library_sources.setExpandsOnDoubleClick(False)
        self.tree_library_sources.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_library_sources.itemExpanded.connect(self._on_lib_sources_expansion_changed)
        self.tree_library_sources.itemCollapsed.connect(self._on_lib_sources_expansion_changed)
        self.tree_library_sources.itemDoubleClicked.connect(self._on_lib_sources_item_double_clicked)
        self.tree_library_sources.customContextMenuRequested.connect(self._on_lib_sources_context_menu)
        l_sources.addWidget(self.tree_library_sources, 1)

        btn_add_box = QHBoxLayout()
        self.btn_add_source_library = QPushButton(tr("sidebar.btn_add_source"))
        self.btn_add_source_library.setProperty("class", "secondary-btn")
        self.btn_add_source_library.clicked.connect(self._on_add_local_folder)
        btn_add_box.addWidget(self.btn_add_source_library)
        btn_add_box.addStretch()
        l_sources.addLayout(btn_add_box)

        content_layout.addWidget(card_sources, 1)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

        self._init_library_sources_columns()
        self._refresh_library_sources_tree()
        return container

    def _set_library_sources_view_mode(self, mode: str) -> None:
        """Bascule entre la vue Par source et la vue agrégée Bibliothèque."""
        if mode not in ("sources", "library") or mode == getattr(self, "_lib_sources_view_mode", "sources"):
            return
        self._lib_sources_view_mode = mode
        if hasattr(self, "btn_lib_tab_sources") and hasattr(self, "btn_lib_tab_library"):
            self.btn_lib_tab_sources.setChecked(mode == "sources")
            self.btn_lib_tab_library.setChecked(mode == "library")
        self._refresh_library_sources_tree()

    def _compute_source_errors(self, summary: SourceLibrarySummary) -> list[str]:
        """Retourne la liste des anomalies connues pour une source."""
        errors: list[str] = []
        src = summary.source
        if src.source_type == SourceType.LOCAL and src.path_or_uri:
            exists = self._lib_sources_path_status.get(src.path_or_uri)
            if exists is False:
                errors.append(tr("library_sources.status_source_offline"))
        if summary.last_scan_errors > 0:
            errors.append(tr("library_sources.status_scan_errors", count=summary.last_scan_errors))
        return errors

    def _compute_playlist_errors(self, pl: PlaylistSummaryRecord) -> list[str]:
        """Retourne la liste des anomalies connues pour une playlist."""
        errors: list[str] = []
        if pl.file_path:
            exists = self._lib_sources_path_status.get(pl.file_path)
            if exists is False:
                errors.append(tr("library_sources.status_playlist_file_missing"))
        if pl.missing_count > 0:
            errors.append(tr("library_sources.status_playlist_entries_missing", count=pl.missing_count))
        return errors

    def _start_lib_sources_path_probe(self, paths: list[str]) -> None:
        """Lance un thread de vérification pour les chemins réseau sans bloquer l'UI."""
        unique_paths = list(dict.fromkeys(p for p in paths if p))
        if not unique_paths:
            return
        self._lib_sources_probe_generation += 1
        gen = self._lib_sources_probe_generation
        worker = _PathProbeWorker(gen, unique_paths, parent=self)
        worker.probe_finished.connect(self._on_lib_sources_probe_finished)
        worker.finished.connect(worker.deleteLater)
        self._lib_sources_probe_worker = worker
        worker.start()

    def _on_lib_sources_probe_finished(self, generation: int, results: dict[str, bool]) -> None:
        """Met à jour les pastilles de statut lorsque le sondage asynchrone se termine."""
        if generation != getattr(self, "_lib_sources_probe_generation", -1):
            return
        self._lib_sources_path_status.update(results)
        self._refresh_status_indicators_only()

    def _build_playlists_anomaly_lines(self, playlists: list[PlaylistSummaryRecord]) -> list[str]:
        """Construit un résumé chiffré + aperçu plafonné (max 5) des playlists en anomalie."""
        bad_items: list[tuple[PlaylistSummaryRecord, list[str], bool]] = []
        total_missing_entries = 0
        total_missing_files = 0
        for pl in playlists:
            errs = self._compute_playlist_errors(pl)
            if not errs:
                continue
            file_missing = bool(pl.file_path and self._lib_sources_path_status.get(pl.file_path) is False)
            if file_missing:
                total_missing_files += 1
            total_missing_entries += pl.missing_count
            bad_items.append((pl, errs, file_missing))

        if not bad_items:
            return []

        parts: list[str] = []
        if total_missing_entries > 0:
            parts.append(tr("library_sources.status_playlists_missing_entries_part", count=total_missing_entries))
        if total_missing_files > 0:
            parts.append(tr("library_sources.status_playlists_missing_files_part", count=total_missing_files))
        details = ", ".join(parts)

        lines = [tr("library_sources.status_playlists_summary", pl_count=len(bad_items), details=details)]
        max_preview = 5
        for pl, _errs, file_missing in bad_items[:max_preview]:
            pl_parts: list[str] = []
            if file_missing:
                pl_parts.append(tr("library_sources.status_playlists_missing_files_part", count=1))
            if pl.missing_count > 0:
                pl_parts.append(tr("library_sources.status_playlists_missing_entries_part", count=pl.missing_count))
            lines.append(f"• {pl.name} : {', '.join(pl_parts)}")

        remaining = len(bad_items) - max_preview
        if remaining > 0:
            lines.append(tr("library_sources.status_playlists_more", count=remaining))
        return lines

    def _build_source_combined_errors(self, summary: SourceLibrarySummary, playlists_lines: list[str]) -> list[str]:
        """Compile les anomalies propres de la source et le résumé de ses playlists."""
        lines = self._compute_source_errors(summary)
        if playlists_lines:
            lines.append(tr("library_sources.status_source_playlists_summary", summary=playlists_lines[0]))
            lines.extend(playlists_lines[1:])
        return lines

    def _update_health_banner(self, summaries: list[SourceLibrarySummary]) -> None:
        """Met à jour le bloc récapitulatif d'anomalies / état sain en haut de la page."""
        if not hasattr(self, "card_lib_sources_health"):
            return

        anomaly_count = 0
        total_items = 0
        for summary in summaries:
            total_items += summary.track_count + sum(pl.track_count for pl in summary.playlists)
            anomaly_count += len(self._compute_source_errors(summary))
            for pl in summary.playlists:
                anomaly_count += len(self._compute_playlist_errors(pl))

        if anomaly_count == 0:
            self._lib_sources_filter_anomalies = False
            self.card_lib_sources_health.setStyleSheet(
                "QFrame#libSourcesHealthCard { background-color: #052E16; border: 1px solid #166534; "
                "border-radius: 8px; }"
            )
            self.lbl_lib_health_title.setStyleSheet("color: #86EFAC; font-size: 13.5px; font-weight: 700;")
            self.lbl_lib_health_details.setStyleSheet("color: #BBF7D0; font-size: 12.5px;")
            self.lbl_lib_health_title.setText(f"✅  {tr('library_sources.health_ok_title')}")
            self.lbl_lib_health_details.setText(
                tr(
                    "library_sources.health_ok_desc",
                    sources=len(summaries),
                    items=_format_count(total_items),
                )
            )
            self.lbl_lib_health_details.setVisible(True)
            self.btn_lib_show_anomalies.setVisible(False)
            self._apply_anomalies_filter()
            return

        self.card_lib_sources_health.setStyleSheet(
            "QFrame#libSourcesHealthCard { background-color: #450A0A; border: 1px solid #991B1B; border-radius: 8px; }"
        )
        self.lbl_lib_health_title.setStyleSheet(f"color: {COLOR_DANGER_SOFT}; font-size: 13.5px; font-weight: 700;")
        self.lbl_lib_health_title.setText(f"⚠️  {tr('library_sources.health_err_title', count=anomaly_count)}")
        self.lbl_lib_health_details.clear()
        self.lbl_lib_health_details.setVisible(False)
        self._sync_anomalies_filter_button()
        self.btn_lib_show_anomalies.setVisible(True)
        self._apply_anomalies_filter()

    def _sync_anomalies_filter_button(self) -> None:
        """Affiche sur le bouton unique l'action réalisable."""
        if self._lib_sources_filter_anomalies:
            self.btn_lib_show_anomalies.setText(tr("playlist_editor.filter_all"))
        else:
            self.btn_lib_show_anomalies.setText(tr("library_sources.btn_show_anomalies"))

    def _on_toggle_library_anomalies_filter(self) -> None:
        """Bascule entre l'affichage des anomalies uniquement et l'affichage par défaut."""
        self._lib_sources_filter_anomalies = not self._lib_sources_filter_anomalies
        self._sync_anomalies_filter_button()
        self._apply_anomalies_filter()

    def _on_edit_library_playlist(self, playlist: PlaylistSummaryRecord) -> None:
        """Ouvre le dialogue de gestion et de réparation de la playlist."""
        dlg = PlaylistEditorDialog(db=self.db, playlist=playlist, parent=self)
        dlg.exec()
        if dlg.was_modified:
            self._refresh_library_sources_tree()
            if hasattr(self, "_refresh_folders_tree"):
                self._refresh_folders_tree()

    def _on_delete_library_playlist(self, playlist: PlaylistSummaryRecord) -> None:
        """Confirme la mise à la corbeille d'une playlist et la retire de la base."""
        reply = QMessageBox.question(
            self,
            tr("library_sources.delete_playlist_title"),
            tr("library_sources.delete_playlist_msg", name=playlist.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        if playlist.file_path and os.path.exists(playlist.file_path):
            trashed = send_file_to_trash(playlist.file_path)
            if not trashed:
                force = QMessageBox.question(
                    self,
                    tr("library_sources.delete_playlist_title"),
                    tr("library_sources.delete_playlist_trash_error"),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if force != QMessageBox.StandardButton.Yes:
                    return

        self.db.delete_playlist(playlist.id)
        self._refresh_library_sources_tree()
        if hasattr(self, "_refresh_folders_tree"):
            self._refresh_folders_tree()

    def _open_source_in_library(self, source: SourceRecord) -> None:
        """Bascule vers Lecteur > Bibliothèque et sélectionne la source demandée."""
        if source.id is None or not hasattr(self, "_on_by_folder_clicked"):
            return
        if hasattr(self, "btn_by_folder"):
            self.btn_by_folder.setChecked(True)
        self._on_by_folder_clicked()
        if not hasattr(self, "folder_tree"):
            return
        for i in range(self.folder_tree.topLevelItemCount()):
            item = self.folder_tree.topLevelItem(i)
            if item is None:
                continue
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(data, dict) and data.get("source_id") == source.id:
                self.folder_tree.setCurrentItem(item)
                self._select_folder_item(item)
                self.folder_tree.scrollToItem(item, QAbstractItemView.ScrollHint.PositionAtCenter)
                break

    def _open_format_in_library(self, fmt: str, source: SourceRecord | None = None) -> None:
        """Bascule vers Lecteur > Bibliothèque et filtre sur le format audio demandé."""
        if not hasattr(self, "_on_by_folder_clicked"):
            return
        if source is not None and source.id is not None:
            self._open_source_in_library(source)
        else:
            if hasattr(self, "btn_by_folder"):
                self.btn_by_folder.setChecked(True)
            self._on_by_folder_clicked()
            if hasattr(self, "folder_tree") and self.folder_tree.topLevelItemCount() > 0:
                first_item = self.folder_tree.topLevelItem(0)
                if first_item is not None:
                    self.folder_tree.setCurrentItem(first_item)
                    self._select_folder_item(first_item)
        if hasattr(self, "cb_recursive") and not self.cb_recursive.isChecked():
            self.cb_recursive.setChecked(True)
        if hasattr(self, "folder_search_edit") and fmt:
            self.folder_search_edit.setText(f".{fmt.lower()}")
            if hasattr(self, "_perform_folder_search"):
                self._perform_folder_search()
