"""Fenêtre principale de l'application AMSO en PySide6."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from typing import Optional

from PySide6.QtCore import QPoint, QSize, Qt, QTimer
from PySide6.QtGui import QAction, QCursor, QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from amso.core.database import DatabaseManager, SourceRecord, SourceType, TrackRecord
from amso.core.i18n import SUPPORTED_LANGUAGES, get_i18n, tr
from amso.core.scanner import ScanSummary
from amso.ui.models import TrackTableModel
from amso.ui.theme import DARK_THEME_QSS
from amso.ui.workers import ScanWorker


class MainWindow(QMainWindow):
    """Fenêtre principale de l'organisateur audio multi-source."""

    def __init__(self, db: DatabaseManager) -> None:
        super().__init__()
        self.db = db
        self.scan_worker: Optional[ScanWorker] = None
        self.i18n = get_i18n()

        self.resize(1200, 780)
        self.setMinimumSize(900, 600)

        # Application du style sombre
        self.setStyleSheet(DARK_THEME_QSS)

        # Initialisation du modèle de données virtualisé
        self.table_model = TrackTableModel(db=self.db, parent=self)

        # Construction de l'interface
        self._setup_ui()
        self._setup_status_bar()

        # Enregistrement du callback de changement de langue dynamique
        self.i18n.add_listener(self._on_language_changed)

        # Appliquer les libellés traduits
        self.retranslate_ui()

        # Timer pour recherche incrémentale fluide (debounce de 250ms)
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(250)
        self._search_timer.timeout.connect(self._perform_search)

        # Chargement initial
        self.refresh_sources_list()
        self.table_model.reload_data()
        self._update_track_count()

    def closeEvent(self, event) -> None:
        self.i18n.remove_listener(self._on_language_changed)
        super().closeEvent(event)

    # -------------------------------------------------------------------------
    # Construction de l'interface graphique
    # -------------------------------------------------------------------------

    def _setup_ui(self) -> None:
        central_widget = QWidget(self)
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal, central_widget)
        main_layout.addWidget(splitter)

        # 1. Barre latérale (Sidebar)
        sidebar = self._create_sidebar()
        splitter.addWidget(sidebar)

        # 2. Zone principale droite
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)

        # Ratios de largeur du splitter (240px / reste)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

    def _create_sidebar(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("sidebarFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(6)

        # Logo / Titre de l'application
        logo = QLabel("🎵  AMSO")
        logo.setObjectName("appLogoLabel")
        layout.addWidget(logo)

        self.lbl_subtitle = QLabel(tr("sidebar.subtitle"))
        self.lbl_subtitle.setStyleSheet("color: #64748B; font-size: 11px; margin-left: 16px; margin-bottom: 12px;")
        layout.addWidget(self.lbl_subtitle)

        # Groupe de boutons de navigation
        self.nav_button_group = QButtonGroup(self)
        self.nav_button_group.setExclusive(True)

        # Section Bibliothèque
        self.sec_lib_label = QLabel(tr("sidebar.section_library"))
        self.sec_lib_label.setStyleSheet("color: #64748B; font-size: 10px; font-weight: 700; padding: 6px 12px;")
        layout.addWidget(self.sec_lib_label)

        self.btn_all_tracks = QPushButton(tr("sidebar.nav_all_tracks"))
        self.btn_all_tracks.setProperty("class", "nav-btn")
        self.btn_all_tracks.setCheckable(True)
        self.btn_all_tracks.setChecked(True)
        self.btn_all_tracks.clicked.connect(self._on_all_tracks_clicked)
        self.nav_button_group.addButton(self.btn_all_tracks)
        layout.addWidget(self.btn_all_tracks)

        self.btn_duplicates = QPushButton(tr("sidebar.nav_duplicates"))
        self.btn_duplicates.setProperty("class", "nav-btn")
        self.btn_duplicates.setCheckable(True)
        self.btn_duplicates.clicked.connect(self._on_duplicates_clicked)
        self.nav_button_group.addButton(self.btn_duplicates)
        layout.addWidget(self.btn_duplicates)

        self.btn_stats = QPushButton(tr("sidebar.nav_stats"))
        self.btn_stats.setProperty("class", "nav-btn")
        self.btn_stats.setCheckable(True)
        self.btn_stats.clicked.connect(self._on_stats_clicked)
        self.nav_button_group.addButton(self.btn_stats)
        layout.addWidget(self.btn_stats)

        # Séparateur
        layout.addSpacing(12)
        self.sec_sources_label = QLabel(tr("sidebar.section_sources"))
        self.sec_sources_label.setStyleSheet("color: #64748B; font-size: 10px; font-weight: 700; padding: 6px 12px;")
        layout.addWidget(self.sec_sources_label)

        # Zone déroulante pour la liste des sources
        self.sources_scroll = QScrollArea()
        self.sources_scroll.setWidgetResizable(True)
        self.sources_scroll.setStyleSheet("background: transparent; border: none;")
        self.sources_container = QWidget()
        self.sources_layout = QVBoxLayout(self.sources_container)
        self.sources_layout.setContentsMargins(0, 0, 0, 0)
        self.sources_layout.setSpacing(2)
        self.sources_scroll.setWidget(self.sources_container)
        layout.addWidget(self.sources_scroll)

        # Bouton d'ajout de source locale
        layout.addSpacing(8)
        self.btn_add_source = QPushButton(tr("sidebar.btn_add_source"))
        self.btn_add_source.setProperty("class", "secondary-btn")
        self.btn_add_source.clicked.connect(self._on_add_local_folder)
        layout.addWidget(self.btn_add_source)

        # Sélecteur de langue en bas de la barre latérale
        layout.addSpacing(14)
        lang_box = QWidget()
        lang_layout = QVBoxLayout(lang_box)
        lang_layout.setContentsMargins(4, 4, 4, 4)
        lang_layout.setSpacing(4)

        self.lbl_language = QLabel(tr("sidebar.language_label"))
        self.lbl_language.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 600;")
        lang_layout.addWidget(self.lbl_language)

        self.combo_language = QComboBox()
        self.combo_language.setObjectName("langComboBox")

        lang_display = {
            "fr": "🇫🇷  Français",
            "en": "🇬🇧  English",
            "es": "🇪🇸  Español",
            "it": "🇮🇹  Italiano",
            "de": "🇩🇪  Deutsch",
        }
        for code, name in SUPPORTED_LANGUAGES.items():
            disp = lang_display.get(code, f"{code.upper()} - {name}")
            self.combo_language.addItem(disp, userData=code)

        cur_idx = self.combo_language.findData(self.i18n.current_language)
        if cur_idx >= 0:
            self.combo_language.setCurrentIndex(cur_idx)

        self.combo_language.currentIndexChanged.connect(self._on_language_combo_changed)
        lang_layout.addWidget(self.combo_language)
        layout.addWidget(lang_box)

        return frame

    def _create_right_panel(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Barre supérieure (Recherche & Actions)
        top_bar = QFrame()
        top_bar.setObjectName("topBarFrame")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(16, 10, 16, 10)
        top_layout.setSpacing(12)

        # Barre de recherche FTS5
        self.search_edit = QLineEdit()
        self.search_edit.setObjectName("searchEdit")
        self.search_edit.setPlaceholderText(tr("topbar.search_placeholder"))
        self.search_edit.textChanged.connect(self._on_search_changed)
        top_layout.addWidget(self.search_edit)

        top_layout.addStretch()

        # Compteur de morceaux
        self.track_count_label = QLabel(tr("topbar.track_count", count="0"))
        self.track_count_label.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 500;")
        top_layout.addWidget(self.track_count_label)

        # Bouton Scanner / Actualiser
        self.btn_scan_all = QPushButton(tr("topbar.btn_scan_all"))
        self.btn_scan_all.setProperty("class", "primary-btn")
        self.btn_scan_all.clicked.connect(self._on_scan_current_source)
        top_layout.addWidget(self.btn_scan_all)

        layout.addWidget(top_bar)

        # 2. Table View virtualisée
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setShowGrid(False)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.verticalHeader().setDefaultSectionSize(32)

        # Ajustement des largeurs de colonnes
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)        # Titre
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)    # Artiste
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)    # Album
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)          # Durée
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)          # Qualité
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)          # Format
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)          # Source
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)          # Année
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)          # Piste

        header.resizeSection(1, 180)  # Artiste
        header.resizeSection(2, 180)  # Album
        header.resizeSection(3, 75)   # Durée
        header.resizeSection(4, 110)  # Qualité
        header.resizeSection(5, 70)   # Format
        header.resizeSection(6, 85)   # Source
        header.resizeSection(7, 65)   # Année
        header.resizeSection(8, 55)   # Piste

        # Menu contextuel clic droit
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self._on_table_context_menu)

        layout.addWidget(self.table_view)
        return container

    def _setup_status_bar(self) -> None:
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_label = QLabel(tr("status.ready"))
        self.status_bar.addWidget(self.status_label, 1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.btn_cancel_scan = QPushButton(tr("status.cancel"))
        self.btn_cancel_scan.setStyleSheet("font-size: 11px; padding: 2px 8px;")
        self.btn_cancel_scan.setVisible(False)
        self.btn_cancel_scan.clicked.connect(self._cancel_current_scan)
        self.status_bar.addPermanentWidget(self.btn_cancel_scan)

    # -------------------------------------------------------------------------
    # Internationalisation & Changement de langue dynamique
    # -------------------------------------------------------------------------

    def retranslate_ui(self) -> None:
        """Applique les traductions de la langue active à l'ensemble de l'interface."""
        self.setWindowTitle(tr("app.window_title"))
        self.lbl_subtitle.setText(tr("sidebar.subtitle"))
        self.sec_lib_label.setText(tr("sidebar.section_library"))
        self.btn_all_tracks.setText(tr("sidebar.nav_all_tracks"))
        self.btn_duplicates.setText(tr("sidebar.nav_duplicates"))
        self.btn_stats.setText(tr("sidebar.nav_stats"))
        self.sec_sources_label.setText(tr("sidebar.section_sources"))
        self.btn_add_source.setText(tr("sidebar.btn_add_source"))
        self.lbl_language.setText(tr("sidebar.language_label"))

        self.search_edit.setPlaceholderText(tr("topbar.search_placeholder"))
        self.btn_scan_all.setText(tr("topbar.btn_scan_all"))
        self.btn_cancel_scan.setText(tr("status.cancel"))

        if not (self.scan_worker and self.scan_worker.isRunning()):
            self.status_label.setText(tr("status.ready"))

        self._update_track_count()
        self.table_model.notify_language_changed()

    def _on_language_combo_changed(self, index: int) -> None:
        lang_code = self.combo_language.itemData(index)
        if lang_code and lang_code != self.i18n.current_language:
            self.i18n.set_language(lang_code, save_to_config=True)

    def _on_language_changed(self, lang_code: str) -> None:
        self.combo_language.blockSignals(True)
        idx = self.combo_language.findData(lang_code)
        if idx >= 0:
            self.combo_language.setCurrentIndex(idx)
        self.combo_language.blockSignals(False)

        self.retranslate_ui()

    # -------------------------------------------------------------------------
    # Actions & Événements
    # -------------------------------------------------------------------------

    def refresh_sources_list(self) -> None:
        """Met à jour les boutons de sources dans la barre latérale."""
        while self.sources_layout.count():
            item = self.sources_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        sources = self.db.get_sources()
        for src in sources:
            icon_str = "📁" if src.source_type == SourceType.LOCAL else "☁️"
            btn = QPushButton(f"{icon_str}  {src.name}")
            btn.setProperty("class", "nav-btn")
            btn.setCheckable(True)
            btn.setToolTip(src.path_or_uri)
            btn.clicked.connect(lambda checked=False, s=src: self._on_source_selected(s))
            self.nav_button_group.addButton(btn)
            self.sources_layout.addWidget(btn)

        self.sources_layout.addStretch()

    def _on_all_tracks_clicked(self) -> None:
        self.table_model.set_filter(source_id=None, source_type=None, search_query=self.search_edit.text())
        self._update_track_count()

    def _on_source_selected(self, source: SourceRecord) -> None:
        self.table_model.set_filter(source_id=source.id, search_query=self.search_edit.text())
        self._update_track_count()

    def _on_duplicates_clicked(self) -> None:
        """Affiche les morceaux identifiés comme doublons stricts ou similaires."""
        dup_hash = self.db.find_duplicates_by_hash()
        dup_meta = self.db.find_duplicates_by_metadata()

        all_dup_tracks: list[TrackRecord] = []
        seen_ids: set[int] = set()

        for group in dup_hash + dup_meta:
            for t in group:
                if t.id is not None and t.id not in seen_ids:
                    seen_ids.add(t.id)
                    all_dup_tracks.append(t)

        self.table_model.set_tracks(all_dup_tracks)
        self._update_track_count()
        self.status_label.setText(
            tr(
                "status.duplicates_summary",
                hash_count=len(dup_hash),
                meta_count=len(dup_meta),
            )
        )

    def _on_stats_clicked(self) -> None:
        """Affiche un dialogue modal récapitulant les statistiques de la bibliothèque."""
        stats = self.db.get_library_stats()
        size_gb = round(stats["total_size_bytes"] / (1024**3), 2)
        duration_hrs = round(stats["total_duration_seconds"] / 3600, 1)

        none_str = tr("dialog.stats_none")
        fmt_details = ", ".join(f"{k.upper()}: {v}" for k, v in stats["by_format"].items()) or none_str
        src_details = ", ".join(f"{k}: {v}" for k, v in stats["by_source_type"].items()) or none_str

        total_tracks_fmt = f"{stats['total_tracks']:,}"
        msg = (
            f"{tr('dialog.stats_header')}"
            f"{tr('dialog.stats_total_tracks', total=total_tracks_fmt)}"
            f"{tr('dialog.stats_total_size', size=size_gb)}"
            f"{tr('dialog.stats_total_duration', duration=duration_hrs)}"
            f"{tr('dialog.stats_total_sources', total=stats['total_sources'])}"
            f"{tr('dialog.stats_by_source', details=src_details)}"
            f"{tr('dialog.stats_by_format', details=fmt_details)}"
        )
        QMessageBox.information(self, tr("dialog.stats_title"), msg)

    def _on_search_changed(self, text: str) -> None:
        """Déclenche la recherche avec debounce."""
        self._search_timer.start()

    def _perform_search(self) -> None:
        query = self.search_edit.text().strip()
        self.table_model.set_filter(search_query=query)
        self._update_track_count()

    def _update_track_count(self) -> None:
        count = self.table_model.rowCount()
        if count <= 1:
            self.track_count_label.setText(tr("topbar.track_count_singular", count=f"{count:,}"))
        else:
            self.track_count_label.setText(tr("topbar.track_count", count=f"{count:,}"))

    def _on_add_local_folder(self) -> None:
        """Permet à l'utilisateur de sélectionner un dossier audio local à ajouter."""
        folder = QFileDialog.getExistingDirectory(
            self,
            tr("dialog.select_folder_title"),
            str(Path.home()),
        )
        if not folder:
            return

        folder_path = Path(folder).resolve()
        source = self.db.add_source(
            source_type=SourceType.LOCAL,
            name=folder_path.name or str(folder_path),
            path_or_uri=folder_path.as_posix(),
        )
        self.refresh_sources_list()

        # Proposer un scan immédiat
        reply = QMessageBox.question(
            self,
            tr("dialog.scan_prompt_title"),
            tr("dialog.scan_prompt_message", name=folder_path.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._start_scan(source)

    def _on_scan_current_source(self) -> None:
        """Lance le scan sur toutes les sources locales."""
        sources = self.db.get_sources()
        if not sources:
            QMessageBox.information(
                self,
                tr("dialog.no_source_title"),
                tr("dialog.no_source_message"),
            )
            return

        for src in sources:
            if src.source_type == SourceType.LOCAL:
                self._start_scan(src)
                break

    def _start_scan(self, source: SourceRecord) -> None:
        """Démarre le worker asynchrone de scan."""
        if self.scan_worker and self.scan_worker.isRunning():
            QMessageBox.warning(self, tr("dialog.scan_running_title"), tr("dialog.scan_running_message"))
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.btn_cancel_scan.setVisible(True)
        self.status_label.setText(tr("status.scanning", source=source.name))

        self.scan_worker = ScanWorker(db=self.db, source=source, compute_hash=True, parent=self)
        self.scan_worker.progress.connect(self._on_scan_progress)
        self.scan_worker.status_message.connect(self.status_label.setText)
        self.scan_worker.scan_finished.connect(self._on_scan_finished)
        self.scan_worker.scan_error.connect(self._on_scan_error)
        self.scan_worker.start()

    def _cancel_current_scan(self) -> None:
        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.cancel()
            self.status_label.setText(tr("status.cancelling"))

    def _on_scan_progress(self, current: int, total: int, current_file: str) -> None:
        if total > 0:
            pct = int((current / total) * 100)
            self.progress_bar.setValue(pct)
            fn = Path(current_file).name
            self.status_label.setText(tr("status.indexing", current=current, total=total, file=fn))

    def _on_scan_finished(self, summary: ScanSummary) -> None:
        self.progress_bar.setVisible(False)
        self.btn_cancel_scan.setVisible(False)
        self.refresh_sources_list()
        self.table_model.reload_data()
        self._update_track_count()

        if summary.cancelled:
            self.status_label.setText(tr("status.cancelled"))
        elif summary.errors and summary.added == 0 and summary.updated == 0 and summary.unchanged == 0:
            err_msg = tr("status.scan_errors", count=len(summary.errors))
            self.status_label.setText(err_msg)
            QMessageBox.warning(
                self,
                tr("dialog.scan_errors_title"),
                tr("dialog.scan_errors_message", count=len(summary.errors), error=summary.errors[0]),
            )
        else:
            self.status_label.setText(
                tr(
                    "status.scan_finished",
                    elapsed=summary.elapsed_seconds,
                    added=summary.added,
                    updated=summary.updated,
                    unchanged=summary.unchanged,
                )
            )

    def _on_scan_error(self, err_msg: str) -> None:
        self.progress_bar.setVisible(False)
        self.btn_cancel_scan.setVisible(False)
        self.status_label.setText(tr("status.scan_error", error=err_msg))
        QMessageBox.critical(
            self,
            tr("dialog.scan_error_title"),
            tr("dialog.scan_error_message", error=err_msg),
        )

    # -------------------------------------------------------------------------
    # Menu contextuel du tableau
    # -------------------------------------------------------------------------

    def _on_table_context_menu(self, pos: QPoint) -> None:
        index = self.table_view.indexAt(pos)
        if not index.isValid():
            return

        track: Optional[TrackRecord] = self.table_model.get_track_at(index.row())
        if not track:
            return

        menu = QMenu(self)

        action_open_dir = QAction(tr("context_menu.open_file_location"), self)
        action_open_dir.triggered.connect(lambda: self._open_file_location(track.source_path))
        menu.addAction(action_open_dir)

        menu.addSeparator()

        action_del = QAction(tr("context_menu.delete_track"), self)
        action_del.triggered.connect(lambda: self._delete_track_from_lib(track))
        menu.addAction(action_del)

        menu.exec(QCursor.pos())

    def _open_file_location(self, file_path: Optional[str]) -> None:
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
        reply = QMessageBox.question(
            self,
            tr("dialog.delete_confirm_title"),
            tr("dialog.delete_confirm_message", title=track.title or tr("track.untitled")),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_track(track.id)
            self.table_model.reload_data()
            self._update_track_count()
