"""Construction de l'arborescence et des nœuds pour Gestion de la bibliothèque > Sources."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QAction, QColor, QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QMainWindow,
    QMenu,
    QPushButton,
    QTreeWidgetItem,
    QWidget,
)

from amso.core.config import get_config_manager
from amso.core.database import (
    FormatBreakdown,
    PlaylistSummaryRecord,
    SourceLibrarySummary,
    SourceRecord,
    SourceType,
)
from amso.core.i18n import tr
from amso.core.network_paths import is_network_path
from amso.ui.models_base import format_duration
from amso.ui.pages.sources_list import format_sync_mode_label

logger = logging.getLogger(__name__)

_NODE_KEY_ROLE = Qt.ItemDataRole.UserRole + 1
_NODE_KIND_ROLE = Qt.ItemDataRole.UserRole + 2
_NODE_OBJ_ROLE = Qt.ItemDataRole.UserRole + 3
_NODE_HAS_ERROR_ROLE = Qt.ItemDataRole.UserRole + 4
_NODE_SOURCE_ROLE = Qt.ItemDataRole.UserRole + 5
_NODE_FORMAT_ROLE = Qt.ItemDataRole.UserRole + 6

_COL_NAME = 0
_COL_PATH = 1
_COL_FILES = 2
_COL_DURATION = 3
_COL_SIZE = 4
_COL_SYNC = 5
_COL_STATUS = 6
_COL_ACTIONS = 7
_COL_COUNT = 8


def _format_count(value: int) -> str:
    """Formate un entier avec espace comme séparateur de milliers."""
    return f"{value:,}".replace(",", " ")


def _format_duration_hms(seconds: float) -> str:
    """Formate une durée en secondes au format H:MM:SS ou Jj HH:MM:SS."""
    return format_duration(seconds, always_hours=True)


def _format_size_bytes(size_bytes: int) -> str:
    """Formate une taille disque en unité lisible (Ko, Mo, Go, To)."""
    if size_bytes <= 0:
        return "-"
    units = ("o", "Ko", "Mo", "Go", "To")
    val = float(size_bytes)
    idx = 0
    while val >= 1024.0 and idx < len(units) - 1:
        val /= 1024.0
        idx += 1
    if idx == 0:
        return f"{int(val)} o"
    return f"{val:.2f} {units[idx]}" if idx >= 3 else f"{val:.1f} {units[idx]}"


def _format_sync_datetime(raw: str | None) -> str:
    """Formate un horodatage ISO en YYYY-MM-DD HH:MM ou retourne le libellé Jamais."""
    if not raw:
        return tr("settings.last_scan_never")
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return raw[:16].replace("T", " ")


def _sync_mode_icon(sync_mode: str | None) -> str:
    """Retourne l'icône associée au mode de synchronisation d'une source."""
    mode = (sync_mode or "").lower()
    if mode == "realtime":
        return "⚡"
    if mode == "startup":
        return "🚀"
    if mode == "interval":
        return "⏱️"
    if mode == "scheduled":
        return "🕒"
    return "✋"


def _source_type_label(source_type: str) -> str:
    """Retourne le libellé localisé d'un type de source."""
    if source_type == SourceType.LOCAL:
        return tr("stats.source_type_local")
    return tr("library_sources.source_type_cloud")


if TYPE_CHECKING:
    _TreeMixinBase = QMainWindow
else:
    _TreeMixinBase = object


class LibrarySourcesTreeMixin(_TreeMixinBase):
    """Mixin gérant l'arborescence sources/formats/playlists et la vue Bibliothèque."""

    if TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any: ...

    def _init_library_sources_columns(self) -> None:
        """Configure les colonnes redimensionnables et leurs largeurs initiales."""
        header = self.tree_library_sources.header()
        header.setStretchLastSection(False)
        for col in range(_COL_COUNT):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
        self.tree_library_sources.setColumnWidth(_COL_NAME, 240)
        self.tree_library_sources.setColumnWidth(_COL_PATH, 220)
        self.tree_library_sources.setColumnWidth(_COL_FILES, 85)
        self.tree_library_sources.setColumnWidth(_COL_DURATION, 90)
        self.tree_library_sources.setColumnWidth(_COL_SIZE, 90)
        self.tree_library_sources.setColumnWidth(_COL_SYNC, 150)
        self.tree_library_sources.setColumnWidth(_COL_STATUS, 65)
        self.tree_library_sources.setColumnWidth(_COL_ACTIONS, 136)

    def _apply_library_sources_headers(self) -> None:
        """Applique les en-têtes traduits sans écraser les largeurs choisies."""
        self.tree_library_sources.setHeaderLabels(
            [
                tr("settings.col_source_name").upper(),
                tr("settings.col_source_path").upper(),
                tr("library_sources.col_files").upper(),
                tr("library_sources.col_duration").upper(),
                tr("library_sources.col_size").upper(),
                tr("library_sources.col_sync").upper(),
                tr("library_sources.col_status").upper(),
                tr("settings.col_source_actions").upper(),
            ]
        )

    def _refresh_library_sources_tree(self) -> None:
        """Reconstruit l'arborescence selon l'onglet actif (Par source ou Bibliothèque)."""
        if not hasattr(self, "tree_library_sources"):
            return

        self._apply_library_sources_headers()
        summaries: list[SourceLibrarySummary] = self.db.get_sources_library_summary()
        expanded_keys = set(get_config_manager().get_library_sources_expanded_nodes())

        self.tree_library_sources.blockSignals(True)
        self.tree_library_sources.clear()

        probe_paths: list[str] = []
        for summary in summaries:
            src = summary.source
            if src.source_type == SourceType.LOCAL and src.path_or_uri:
                if is_network_path(src.path_or_uri):
                    probe_paths.append(src.path_or_uri)
                else:
                    self._lib_sources_path_status[src.path_or_uri] = os.path.exists(src.path_or_uri)
            for pl in summary.playlists:
                if pl.file_path:
                    if is_network_path(pl.file_path):
                        probe_paths.append(pl.file_path)
                    else:
                        self._lib_sources_path_status[pl.file_path] = os.path.exists(pl.file_path)

        view_mode = getattr(self, "_lib_sources_view_mode", "sources")
        if view_mode == "library":
            self._build_library_overview_tree(summaries, expanded_keys)
        else:
            for summary in summaries:
                self._build_source_tree_item(summary, expanded_keys)

        self.tree_library_sources.blockSignals(False)
        self._update_health_banner(summaries)
        self._start_lib_sources_path_probe(probe_paths)

    def _build_source_tree_item(self, summary: SourceLibrarySummary, expanded_keys: set[str]) -> None:
        """Construit un nœud Source et ses sous-nœuds Fichiers (par format) / Playlists."""
        src = summary.source
        sid = src.id or 0
        pl_total_count = sum(pl.track_count for pl in summary.playlists)
        pl_total_dur = sum(pl.total_duration_seconds for pl in summary.playlists)
        total_count = summary.track_count + pl_total_count
        total_dur = summary.track_duration_seconds + pl_total_dur

        src_icon = "📁" if src.source_type == SourceType.LOCAL else "☁️"
        sync_icon = _sync_mode_icon(src.sync_mode)
        last_sync = _format_sync_datetime(src.last_scanned_at)

        src_item = QTreeWidgetItem(self.tree_library_sources)
        src_item.setData(0, _NODE_KEY_ROLE, f"source:{sid}")
        src_item.setData(0, _NODE_KIND_ROLE, "source")
        src_item.setData(0, _NODE_OBJ_ROLE, src)

        src_item.setText(_COL_NAME, f"{src_icon}  {src.name}")
        src_item.setToolTip(_COL_NAME, src.name)
        src_item.setText(_COL_PATH, src.path_or_uri)
        src_item.setToolTip(_COL_PATH, src.path_or_uri)
        src_item.setText(_COL_FILES, _format_count(total_count))
        src_item.setText(_COL_DURATION, _format_duration_hms(total_dur))
        src_item.setText(_COL_SIZE, _format_size_bytes(summary.track_size_bytes))
        src_item.setText(_COL_SYNC, f"{sync_icon}  {last_sync}")
        src_item.setToolTip(_COL_SYNC, format_sync_mode_label(src))
        for col in (_COL_FILES, _COL_DURATION, _COL_SIZE):
            src_item.setTextAlignment(col, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        src_item.setTextAlignment(_COL_SYNC, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        src_item.setTextAlignment(_COL_STATUS, Qt.AlignmentFlag.AlignCenter)

        bold_font = QFont()
        bold_font.setBold(True)
        for col in range(_COL_STATUS):
            src_item.setFont(col, bold_font)
            src_item.setBackground(col, QColor("#090E1A"))

        self._attach_row_actions(
            src_item,
            edit_tooltip=tr("library_sources.tooltip_edit_source"),
            delete_tooltip=tr("library_sources.tooltip_delete_source"),
            on_sync=lambda s=src: self._start_scan(s, user_initiated=True),
            sync_tooltip=tr("sources.menu_sync"),
            on_edit=lambda s=src: self._on_edit_source_properties(s),
            on_delete=lambda s=src: self._on_delete_source(s),
            on_open_folder=(
                (lambda p=src.path_or_uri: self._open_source_in_explorer(p))
                if src.source_type == SourceType.LOCAL and src.path_or_uri
                else None
            ),
        )

        if summary.track_count > 0:
            self._build_files_group_node(src_item, summary, last_sync, expanded_keys)

        playlists_errors: list[str] = []
        if summary.playlists:
            playlists_errors = self._build_playlists_group_node(
                src_item, src, summary.playlists, pl_total_count, pl_total_dur, last_sync, expanded_keys
            )

        src_errors = self._build_source_combined_errors(summary, playlists_errors)
        self._apply_status_cell(src_item, src_errors)
        src_item.setExpanded(f"source:{sid}" in expanded_keys)

    def _build_files_group_node(
        self,
        src_item: QTreeWidgetItem,
        summary: SourceLibrarySummary,
        last_sync: str,
        expanded_keys: set[str],
    ) -> None:
        """Construit le sous-nœud Fichiers et ses nœuds enfants par format audio."""
        src = summary.source
        sid = src.id or 0
        files_item = QTreeWidgetItem(src_item)
        files_item.setData(0, _NODE_KEY_ROLE, f"files:{sid}")
        files_item.setData(0, _NODE_KIND_ROLE, "files")
        files_item.setData(0, _NODE_OBJ_ROLE, src)
        files_item.setText(_COL_NAME, f"📄  {tr('library_sources.group_files')}")
        files_item.setText(_COL_PATH, "-")
        files_item.setText(_COL_FILES, _format_count(summary.track_count))
        files_item.setText(_COL_DURATION, _format_duration_hms(summary.track_duration_seconds))
        files_item.setText(_COL_SIZE, _format_size_bytes(summary.track_size_bytes))
        files_item.setText(_COL_SYNC, last_sync)
        for col in (_COL_FILES, _COL_DURATION, _COL_SIZE):
            files_item.setTextAlignment(col, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        files_item.setTextAlignment(_COL_STATUS, Qt.AlignmentFlag.AlignCenter)
        self._attach_row_actions(
            files_item,
            edit_tooltip="",
            on_sync=lambda s=src: self._start_scan(s, user_initiated=True),
            sync_tooltip=tr("sources.menu_sync"),
            on_open_folder=(
                (lambda p=src.path_or_uri: self._open_source_in_explorer(p))
                if src.source_type == SourceType.LOCAL and src.path_or_uri
                else None
            ),
        )
        for col in range(_COL_COUNT):
            files_item.setBackground(col, QColor("#0F2744"))

        self._apply_status_cell(files_item, self._compute_source_errors(summary))

        for fmt_item in summary.formats:
            self._add_format_child_node(
                parent=files_item,
                node_key=f"format:{sid}:{fmt_item.format}",
                fmt=fmt_item,
                total_tracks=summary.track_count,
                source=src,
            )
        files_item.setExpanded(f"files:{sid}" in expanded_keys)

    def _add_format_child_node(
        self,
        parent: QTreeWidgetItem,
        node_key: str,
        fmt: FormatBreakdown,
        total_tracks: int,
        source: SourceRecord | None,
    ) -> QTreeWidgetItem:
        """Ajoute un nœud feuille représentant un format audio."""
        pct = (fmt.track_count / total_tracks * 100.0) if total_tracks > 0 else 0.0
        node = QTreeWidgetItem(parent)
        node.setData(0, _NODE_KEY_ROLE, node_key)
        node.setData(0, _NODE_KIND_ROLE, "format")
        node.setData(0, _NODE_OBJ_ROLE, source)
        node.setData(0, _NODE_FORMAT_ROLE, fmt.format)
        node.setText(_COL_NAME, f"🎶  {fmt.format.upper()}")
        node.setText(_COL_PATH, f"{pct:.1f} %")
        node.setText(_COL_FILES, _format_count(fmt.track_count))
        node.setText(_COL_DURATION, _format_duration_hms(fmt.duration_seconds))
        node.setText(_COL_SIZE, _format_size_bytes(fmt.size_bytes))
        node.setText(_COL_SYNC, "-")
        for col in (_COL_FILES, _COL_DURATION, _COL_SIZE):
            node.setTextAlignment(col, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        node.setTextAlignment(_COL_STATUS, Qt.AlignmentFlag.AlignCenter)
        return node

    def _build_playlists_group_node(
        self,
        src_item: QTreeWidgetItem,
        src: SourceRecord,
        playlists: list[PlaylistSummaryRecord],
        pl_total_count: int,
        pl_total_dur: float,
        last_sync: str,
        expanded_keys: set[str],
    ) -> list[str]:
        """Construit le sous-nœud Playlists et ses feuilles."""
        sid = src.id or 0
        pl_group_item = QTreeWidgetItem(src_item)
        pl_group_item.setData(0, _NODE_KEY_ROLE, f"playlists:{sid}")
        pl_group_item.setData(0, _NODE_KIND_ROLE, "playlists_group")
        pl_group_item.setData(0, _NODE_OBJ_ROLE, src)
        pl_group_item.setText(_COL_NAME, f"🎵  {tr('library_sources.group_playlists')}")
        pl_group_item.setText(_COL_PATH, "-")
        pl_group_item.setText(_COL_FILES, _format_count(pl_total_count))
        pl_group_item.setText(_COL_DURATION, _format_duration_hms(pl_total_dur))
        pl_group_item.setText(_COL_SIZE, "-")
        pl_group_item.setText(_COL_SYNC, last_sync)
        for col in (_COL_FILES, _COL_DURATION, _COL_SIZE):
            pl_group_item.setTextAlignment(col, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        if hasattr(self, "_start_playlist_rescan"):
            self._attach_row_actions(
                pl_group_item,
                edit_tooltip="",
                on_sync=lambda s=src: self._start_playlist_rescan(s),
                sync_tooltip=tr("library_sources.tooltip_rescan_playlists"),
            )
        pl_group_item.setTextAlignment(_COL_STATUS, Qt.AlignmentFlag.AlignCenter)
        for col in range(_COL_COUNT):
            pl_group_item.setBackground(col, QColor("#0F2744"))

        for pl in playlists:
            pl_item = QTreeWidgetItem(pl_group_item)
            pl_item.setData(0, _NODE_KEY_ROLE, f"playlist:{pl.id}")
            pl_item.setData(0, _NODE_KIND_ROLE, "playlist")
            pl_item.setData(0, _NODE_OBJ_ROLE, pl)
            pl_item.setData(0, _NODE_SOURCE_ROLE, src)

            pl_item.setText(_COL_NAME, f"📃  {pl.name}")
            pl_item.setToolTip(_COL_NAME, pl.name)
            pl_item.setText(_COL_PATH, pl.file_path)
            pl_item.setToolTip(_COL_PATH, pl.file_path)
            pl_item.setText(_COL_FILES, _format_count(pl.track_count))
            pl_item.setText(_COL_DURATION, _format_duration_hms(pl.total_duration_seconds))
            pl_item.setText(_COL_SIZE, "-")
            pl_item.setText(_COL_SYNC, _format_sync_datetime(pl.updated_at or src.last_scanned_at))
            for col in (_COL_FILES, _COL_DURATION, _COL_SIZE):
                pl_item.setTextAlignment(col, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            pl_item.setTextAlignment(_COL_STATUS, Qt.AlignmentFlag.AlignCenter)

            self._attach_row_actions(
                pl_item,
                edit_tooltip=tr("library_sources.tooltip_edit_playlist"),
                on_sync=(lambda s=src: self._start_playlist_rescan(s))
                if hasattr(self, "_start_playlist_rescan")
                else None,
                sync_tooltip=tr("library_sources.tooltip_rescan_playlists"),
                on_edit=lambda p=pl: self._on_edit_library_playlist(p),
                edit_icon="🛠️",
                on_open_folder=(
                    (lambda p=pl.file_path: self._open_source_in_explorer(str(Path(p).parent)))
                    if pl.file_path
                    else None
                ),
            )
            self._apply_status_cell(pl_item, self._compute_playlist_errors(pl))

        playlists_errors = self._build_playlists_anomaly_lines(playlists)
        self._apply_status_cell(pl_group_item, playlists_errors)
        pl_group_item.setExpanded(f"playlists:{sid}" in expanded_keys)
        return playlists_errors

    def _build_library_overview_tree(self, summaries: list[SourceLibrarySummary], expanded_keys: set[str]) -> None:
        """Construit l'arborescence agrégée de l'onglet Bibliothèque (fichiers, formats, playlists, types)."""
        bold_font = QFont()
        bold_font.setBold(True)

        total_tracks = sum(s.track_count for s in summaries)
        total_dur = sum(s.track_duration_seconds for s in summaries)
        total_size = sum(s.track_size_bytes for s in summaries)

        # 1. Tous les fichiers -> formats audio
        files_root = QTreeWidgetItem(self.tree_library_sources)
        files_root.setData(0, _NODE_KEY_ROLE, "overview:files")
        files_root.setData(0, _NODE_KIND_ROLE, "overview_files")
        files_root.setText(_COL_NAME, f"📄  {tr('library_sources.overview_all_files')}")
        files_root.setText(_COL_PATH, f"{len(summaries)} source(s)")
        files_root.setText(_COL_FILES, _format_count(total_tracks))
        files_root.setText(_COL_DURATION, _format_duration_hms(total_dur))
        files_root.setText(_COL_SIZE, _format_size_bytes(total_size))
        files_root.setText(_COL_SYNC, "-")
        for col in (_COL_FILES, _COL_DURATION, _COL_SIZE):
            files_root.setTextAlignment(col, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        files_root.setTextAlignment(_COL_STATUS, Qt.AlignmentFlag.AlignCenter)
        for col in range(_COL_STATUS):
            files_root.setFont(col, bold_font)
            files_root.setBackground(col, QColor("#090E1A"))

        agg_formats: dict[str, FormatBreakdown] = {}
        for s in summaries:
            for fmt in s.formats:
                cur = agg_formats.get(fmt.format)
                if cur is None:
                    agg_formats[fmt.format] = FormatBreakdown(
                        format=fmt.format,
                        track_count=fmt.track_count,
                        duration_seconds=fmt.duration_seconds,
                        size_bytes=fmt.size_bytes,
                    )
                else:
                    cur.track_count += fmt.track_count
                    cur.duration_seconds += fmt.duration_seconds
                    cur.size_bytes += fmt.size_bytes

        for fmt in sorted(agg_formats.values(), key=lambda f: (-f.track_count, f.format)):
            self._add_format_child_node(
                parent=files_root,
                node_key=f"overview_format:{fmt.format}",
                fmt=fmt,
                total_tracks=total_tracks,
                source=None,
            )
        files_root.setExpanded("overview:files" in expanded_keys or not expanded_keys)

        # 2. Toutes les playlists -> formats de playlists
        all_playlists = [pl for s in summaries for pl in s.playlists]
        pl_entries_total = sum(pl.track_count for pl in all_playlists)
        pl_dur_total = sum(pl.total_duration_seconds for pl in all_playlists)

        pl_root = QTreeWidgetItem(self.tree_library_sources)
        pl_root.setData(0, _NODE_KEY_ROLE, "overview:playlists")
        pl_root.setData(0, _NODE_KIND_ROLE, "overview_playlists")
        pl_root.setText(_COL_NAME, f"🎵  {tr('library_sources.overview_all_playlists')}")
        pl_root.setText(_COL_PATH, f"{len(all_playlists)} playlist(s)")
        pl_root.setText(_COL_FILES, _format_count(pl_entries_total))
        pl_root.setText(_COL_DURATION, _format_duration_hms(pl_dur_total))
        pl_root.setText(_COL_SIZE, "-")
        pl_root.setText(_COL_SYNC, "-")
        for col in (_COL_FILES, _COL_DURATION, _COL_SIZE):
            pl_root.setTextAlignment(col, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        pl_root.setTextAlignment(_COL_STATUS, Qt.AlignmentFlag.AlignCenter)
        for col in range(_COL_STATUS):
            pl_root.setFont(col, bold_font)
            pl_root.setBackground(col, QColor("#090E1A"))

        pl_by_fmt: dict[str, tuple[int, int, float]] = {}
        for pl in all_playlists:
            pfmt = (pl.format or "unknown").lower()
            n_pl, n_tr, dur = pl_by_fmt.get(pfmt, (0, 0, 0.0))
            pl_by_fmt[pfmt] = (n_pl + 1, n_tr + pl.track_count, dur + pl.total_duration_seconds)

        for pfmt, (n_pl, n_tr, dur) in sorted(pl_by_fmt.items(), key=lambda kv: (-kv[1][1], kv[0])):
            node = QTreeWidgetItem(pl_root)
            node.setData(0, _NODE_KEY_ROLE, f"overview_pl_format:{pfmt}")
            node.setData(0, _NODE_KIND_ROLE, "overview_pl_format")
            node.setText(_COL_NAME, f"📃  {pfmt.upper()}")
            node.setText(_COL_PATH, f"{n_pl} playlist(s)")
            node.setText(_COL_FILES, _format_count(n_tr))
            node.setText(_COL_DURATION, _format_duration_hms(dur))
            node.setText(_COL_SIZE, "-")
            node.setText(_COL_SYNC, "-")
            for col in (_COL_FILES, _COL_DURATION, _COL_SIZE):
                node.setTextAlignment(col, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            node.setTextAlignment(_COL_STATUS, Qt.AlignmentFlag.AlignCenter)
        pl_root.setExpanded("overview:playlists" in expanded_keys)

        # 3. Par type de source
        type_root = QTreeWidgetItem(self.tree_library_sources)
        type_root.setData(0, _NODE_KEY_ROLE, "overview:source_types")
        type_root.setData(0, _NODE_KIND_ROLE, "overview_source_types")
        type_root.setText(_COL_NAME, f"🌐  {tr('library_sources.overview_source_types')}")
        type_root.setText(_COL_PATH, "-")
        type_root.setText(_COL_FILES, _format_count(total_tracks))
        type_root.setText(_COL_DURATION, _format_duration_hms(total_dur))
        type_root.setText(_COL_SIZE, _format_size_bytes(total_size))
        type_root.setText(_COL_SYNC, "-")
        for col in (_COL_FILES, _COL_DURATION, _COL_SIZE):
            type_root.setTextAlignment(col, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        type_root.setTextAlignment(_COL_STATUS, Qt.AlignmentFlag.AlignCenter)
        for col in range(_COL_STATUS):
            type_root.setFont(col, bold_font)
            type_root.setBackground(col, QColor("#090E1A"))

        by_type: dict[str, tuple[int, int, float, int]] = {}
        for s in summaries:
            stype = str(s.source.source_type)
            n_src, n_tr, dur, sz = by_type.get(stype, (0, 0, 0.0, 0))
            by_type[stype] = (n_src + 1, n_tr + s.track_count, dur + s.track_duration_seconds, sz + s.track_size_bytes)

        for stype, (n_src, n_tr, dur, sz) in sorted(by_type.items(), key=lambda kv: (-kv[1][1], kv[0])):
            node = QTreeWidgetItem(type_root)
            node.setData(0, _NODE_KEY_ROLE, f"overview_type:{stype}")
            node.setData(0, _NODE_KIND_ROLE, "overview_type")
            node.setData(0, _NODE_OBJ_ROLE, stype)
            icon = "📁" if stype == SourceType.LOCAL else "☁️"
            node.setText(_COL_NAME, f"{icon}  {_source_type_label(stype)}")
            node.setText(_COL_PATH, f"{n_src} source(s)")
            node.setText(_COL_FILES, _format_count(n_tr))
            node.setText(_COL_DURATION, _format_duration_hms(dur))
            node.setText(_COL_SIZE, _format_size_bytes(sz))
            node.setText(_COL_SYNC, "-")
            for col in (_COL_FILES, _COL_DURATION, _COL_SIZE):
                node.setTextAlignment(col, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            node.setTextAlignment(_COL_STATUS, Qt.AlignmentFlag.AlignCenter)
        type_root.setExpanded("overview:source_types" in expanded_keys)
        self._apply_library_overview_statuses(summaries)

    def _apply_library_overview_statuses(self, summaries: list[SourceLibrarySummary]) -> None:
        """Calcule et applique les pastilles de statut sur l'arborescence de l'onglet Bibliothèque."""
        if not hasattr(self, "tree_library_sources"):
            return
        source_errors: list[str] = []
        for s in summaries:
            for err in self._compute_source_errors(s):
                source_errors.append(f"{s.source.name} : {err}")

        all_playlists = [pl for s in summaries for pl in s.playlists]
        all_pl_errors = self._build_playlists_anomaly_lines(all_playlists)
        all_errors = source_errors + all_pl_errors

        root = self.tree_library_sources.invisibleRootItem()
        for i in range(root.childCount()):
            top = root.child(i)
            if top is None:
                continue
            kind = top.data(0, _NODE_KIND_ROLE)
            if kind == "overview_files":
                self._apply_status_cell(top, source_errors)
            elif kind == "overview_playlists":
                self._apply_status_cell(top, all_pl_errors)
                for j in range(top.childCount()):
                    child = top.child(j)
                    if child is None:
                        continue
                    key = str(child.data(0, _NODE_KEY_ROLE) or "")
                    pfmt = key.removeprefix("overview_pl_format:")
                    fmt_pls = [pl for pl in all_playlists if (pl.format or "unknown").lower() == pfmt]
                    self._apply_status_cell(child, self._build_playlists_anomaly_lines(fmt_pls))
            elif kind == "overview_source_types":
                self._apply_status_cell(top, all_errors)
                for j in range(top.childCount()):
                    child = top.child(j)
                    if child is None:
                        continue
                    stype = str(child.data(0, _NODE_OBJ_ROLE) or "")
                    typed_summaries = [s for s in summaries if str(s.source.source_type) == stype]
                    typed_errs: list[str] = []
                    for s in typed_summaries:
                        for err in self._compute_source_errors(s):
                            typed_errs.append(f"{s.source.name} : {err}")
                    typed_pls = [pl for s in typed_summaries for pl in s.playlists]
                    typed_errs.extend(self._build_playlists_anomaly_lines(typed_pls))
                    self._apply_status_cell(child, typed_errs)

    def _attach_row_actions(
        self,
        item: QTreeWidgetItem,
        edit_tooltip: str,
        delete_tooltip: str = "",
        on_edit: Any = None,
        on_delete: Any = None,
        on_open_folder: Any = None,
        edit_icon: str = "✏️",
        on_sync: Any = None,
        sync_tooltip: str = "",
    ) -> None:
        """Ajoute les boutons d'action dans la colonne Actions."""
        cell = QWidget()
        layout = QHBoxLayout(cell)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def add_btn(icon: str, tooltip: str, callback: Any) -> None:
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.setFixedSize(28, 24)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("QPushButton { background: transparent; border: none; font-size: 13px; }")
            btn.clicked.connect(lambda _checked=False: callback())
            layout.addWidget(btn)

        if on_sync is not None:
            add_btn("🔄", sync_tooltip, on_sync)
        if on_open_folder is not None:
            add_btn("📂", tr("common.open_explorer"), on_open_folder)
        if on_edit is not None:
            add_btn(edit_icon, edit_tooltip, on_edit)
        if on_delete is not None:
            add_btn("🗑️", delete_tooltip, on_delete)

        self.tree_library_sources.setItemWidget(item, _COL_ACTIONS, cell)

    def _apply_status_cell(self, item: QTreeWidgetItem, errors: list[str]) -> None:
        """Met à jour la pastille et l'infobulle de statut d'une ligne."""
        has_errors = bool(errors)
        item.setData(0, _NODE_HAS_ERROR_ROLE, has_errors)
        if has_errors:
            item.setText(_COL_STATUS, "🔴")
            item.setToolTip(_COL_STATUS, "\n".join(errors))
        else:
            item.setText(_COL_STATUS, "🟢")
            item.setToolTip(_COL_STATUS, tr("library_sources.status_ok"))

    def _refresh_status_indicators_only(self) -> None:
        """Recalcule uniquement les pastilles de statut de l'arborescence existante."""
        if not hasattr(self, "tree_library_sources"):
            return
        summaries = self.db.get_sources_library_summary()
        if getattr(self, "_lib_sources_view_mode", "sources") == "library":
            self._apply_library_overview_statuses(summaries)
            self._update_health_banner(summaries)
            return

        summaries_by_id = {s.source.id: s for s in summaries}
        root = self.tree_library_sources.invisibleRootItem()
        for i in range(root.childCount()):
            src_item = root.child(i)
            if src_item is None:
                continue
            src_obj = src_item.data(0, _NODE_OBJ_ROLE)
            if not isinstance(src_obj, SourceRecord) or src_obj.id not in summaries_by_id:
                continue
            summary = summaries_by_id[src_obj.id]
            playlists_lines: list[str] = []

            for j in range(src_item.childCount()):
                child = src_item.child(j)
                if child is None:
                    continue
                kind = child.data(0, _NODE_KIND_ROLE)
                if kind == "files":
                    self._apply_status_cell(child, self._compute_source_errors(summary))
                elif kind == "playlists_group":
                    for k in range(child.childCount()):
                        pl_item = child.child(k)
                        if pl_item is None:
                            continue
                        pl_obj = pl_item.data(0, _NODE_OBJ_ROLE)
                        if isinstance(pl_obj, PlaylistSummaryRecord):
                            self._apply_status_cell(pl_item, self._compute_playlist_errors(pl_obj))
                    playlists_lines = self._build_playlists_anomaly_lines(summary.playlists)
                    self._apply_status_cell(child, playlists_lines)

            src_errs = self._build_source_combined_errors(summary, playlists_lines)
            self._apply_status_cell(src_item, src_errs)

        self._update_health_banner(summaries)

    def _apply_anomalies_filter(self) -> None:
        """Filtre l'arborescence pour n'afficher que les nœuds en anomalie ou tout réafficher."""
        if not hasattr(self, "tree_library_sources"):
            return
        if getattr(self, "_lib_sources_view_mode", "sources") == "library":
            return
        only_errors = self._lib_sources_filter_anomalies
        expanded_keys = set(get_config_manager().get_library_sources_expanded_nodes())

        self.tree_library_sources.blockSignals(True)
        root = self.tree_library_sources.invisibleRootItem()
        for i in range(root.childCount()):
            src_item = root.child(i)
            if src_item is None:
                continue
            src_has_err = bool(src_item.data(0, _NODE_HAS_ERROR_ROLE))
            src_item.setHidden(only_errors and not src_has_err)
            if only_errors:
                src_item.setExpanded(src_has_err)
            else:
                src_item.setExpanded(str(src_item.data(0, _NODE_KEY_ROLE) or "") in expanded_keys)

            for j in range(src_item.childCount()):
                child = src_item.child(j)
                if child is None:
                    continue
                child_has_err = bool(child.data(0, _NODE_HAS_ERROR_ROLE))
                child.setHidden(only_errors and not child_has_err)
                if child.data(0, _NODE_KIND_ROLE) == "playlists_group":
                    if only_errors:
                        child.setExpanded(child_has_err)
                    else:
                        child.setExpanded(str(child.data(0, _NODE_KEY_ROLE) or "") in expanded_keys)
                    for k in range(child.childCount()):
                        pl_item = child.child(k)
                        if pl_item is None:
                            continue
                        pl_has_err = bool(pl_item.data(0, _NODE_HAS_ERROR_ROLE))
                        pl_item.setHidden(only_errors and not pl_has_err)
        self.tree_library_sources.blockSignals(False)

    def _set_library_sources_all_expanded(self, expanded: bool) -> None:
        """Déplie ou replie tous les nœuds de l'arborescence et sauvegarde l'état."""
        if not hasattr(self, "tree_library_sources"):
            return
        self.tree_library_sources.blockSignals(True)
        if expanded:
            self.tree_library_sources.expandAll()
        else:
            self.tree_library_sources.collapseAll()
        self.tree_library_sources.blockSignals(False)
        self._on_lib_sources_expansion_changed(None)

    def _on_lib_sources_expansion_changed(self, _item: QTreeWidgetItem | None) -> None:
        """Sauvegarde récursivement l'état déplié de chaque nœud dans la configuration."""
        if not hasattr(self, "tree_library_sources"):
            return
        expanded: list[str] = []

        def _collect(node: QTreeWidgetItem) -> None:
            for idx in range(node.childCount()):
                child = node.child(idx)
                if child is None:
                    continue
                if child.isExpanded():
                    key = child.data(0, _NODE_KEY_ROLE)
                    if key:
                        expanded.append(str(key))
                _collect(child)

        _collect(self.tree_library_sources.invisibleRootItem())
        get_config_manager().set_library_sources_expanded_nodes(expanded)

    def _on_lib_sources_item_double_clicked(self, item: QTreeWidgetItem, _column: int) -> None:
        """Ouvre la source/format dans Bibliothèque ou la playlist dans l'éditeur au double-clic."""
        kind = item.data(0, _NODE_KIND_ROLE)
        obj = item.data(0, _NODE_OBJ_ROLE)
        if kind in ("source", "files") and isinstance(obj, SourceRecord):
            self._open_source_in_library(obj)
        elif kind == "format":
            fmt = str(item.data(0, _NODE_FORMAT_ROLE) or "")
            src = obj if isinstance(obj, SourceRecord) else None
            self._open_format_in_library(fmt, source=src)
        elif kind == "playlist" and isinstance(obj, PlaylistSummaryRecord):
            self._on_edit_library_playlist(obj)

    def _on_lib_sources_context_menu(self, pos: QPoint) -> None:
        """Affiche le menu contextuel adapté au nœud cliqué (source, fichiers, format, playlists, playlist)."""
        item = self.tree_library_sources.itemAt(pos)
        if item is None:
            return
        kind = item.data(0, _NODE_KIND_ROLE)
        obj = item.data(0, _NODE_OBJ_ROLE)
        menu = QMenu(self)

        def add_action(label: str, callback: Any) -> None:
            act = QAction(label, self)
            act.triggered.connect(lambda _checked=False: callback())
            menu.addAction(act)

        if kind == "source" and isinstance(obj, SourceRecord):
            menu = self._create_source_context_menu(obj)
        elif kind == "files" and isinstance(obj, SourceRecord):
            add_action(
                "📁  " + tr("library_sources.menu_open_in_library"), lambda s=obj: self._open_source_in_library(s)
            )
            add_action("🔄  " + tr("sources.menu_sync"), lambda s=obj: self._start_scan(s, user_initiated=True))
            if obj.source_type == SourceType.LOCAL and obj.path_or_uri:
                add_action(
                    "📂  " + tr("common.open_explorer"), lambda p=obj.path_or_uri: self._open_source_in_explorer(p)
                )
        elif kind == "format":
            fmt = str(item.data(0, _NODE_FORMAT_ROLE) or "")
            src = obj if isinstance(obj, SourceRecord) else None
            add_action(
                "📁  " + tr("library_sources.menu_open_in_library"),
                lambda f=fmt, s=src: self._open_format_in_library(f, source=s),
            )
        elif kind == "playlists_group" and isinstance(obj, SourceRecord):
            if hasattr(self, "_start_playlist_rescan"):
                add_action(
                    "🔄  " + tr("library_sources.tooltip_rescan_playlists"),
                    lambda s=obj: self._start_playlist_rescan(s),
                )
        elif kind == "playlist" and isinstance(obj, PlaylistSummaryRecord):
            src = item.data(0, _NODE_SOURCE_ROLE)
            add_action(
                "🛠️  " + tr("library_sources.tooltip_edit_playlist"), lambda p=obj: self._on_edit_library_playlist(p)
            )
            if isinstance(src, SourceRecord) and hasattr(self, "_start_playlist_rescan"):
                add_action(
                    "🔄  " + tr("library_sources.tooltip_rescan_playlists"),
                    lambda s=src: self._start_playlist_rescan(s),
                )
            if obj.file_path:
                add_action(
                    "📂  " + tr("common.open_explorer"),
                    lambda p=obj.file_path: self._open_source_in_explorer(str(Path(p).parent)),
                )

        if not menu.isEmpty():
            menu.exec(self.tree_library_sources.viewport().mapToGlobal(pos))
