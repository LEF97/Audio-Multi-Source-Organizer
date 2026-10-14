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

        self.setWindowTitle("Audio Multi-Source Organizer (AMSO)")
        self.resize(1200, 780)
        self.setMinimumSize(900, 600)

        # Application du style sombre
        self.setStyleSheet(DARK_THEME_QSS)

        # Initialisation du modèle de données virtualisé
        self.table_model = TrackTableModel(db=self.db, parent=self)

        # Construction de l'interface
        self._setup_ui()
        self._setup_status_bar()

        # Timer pour recherche incrémentale fluide (debounce de 250ms)
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(250)
        self._search_timer.timeout.connect(self._perform_search)

        # Chargement initial
        self.refresh_sources_list()
        self.table_model.reload_data()
        self._update_track_count()

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

        subtitle = QLabel("Audio Multi-Source")
        subtitle.setStyleSheet("color: #64748B; font-size: 11px; margin-left: 16px; margin-bottom: 12px;")
        layout.addWidget(subtitle)

        # Groupe de boutons de navigation
        self.nav_button_group = QButtonGroup(self)
        self.nav_button_group.setExclusive(True)

        # Section Bibliothèque
        sec_lib = QLabel("BIBLIOTHÈQUE")
        sec_lib.setStyleSheet("color: #64748B; font-size: 10px; font-weight: 700; padding: 6px 12px;")
        layout.addWidget(sec_lib)

        self.btn_all_tracks = QPushButton("🎵  Tous les morceaux")
        self.btn_all_tracks.setProperty("class", "nav-btn")
        self.btn_all_tracks.setCheckable(True)
        self.btn_all_tracks.setChecked(True)
        self.btn_all_tracks.clicked.connect(self._on_all_tracks_clicked)
        self.nav_button_group.addButton(self.btn_all_tracks)
        layout.addWidget(self.btn_all_tracks)

        self.btn_duplicates = QPushButton("👥  Doublons détectés")
        self.btn_duplicates.setProperty("class", "nav-btn")
        self.btn_duplicates.setCheckable(True)
        self.btn_duplicates.clicked.connect(self._on_duplicates_clicked)
        self.nav_button_group.addButton(self.btn_duplicates)
        layout.addWidget(self.btn_duplicates)

        self.btn_stats = QPushButton("📊  Statistiques")
        self.btn_stats.setProperty("class", "nav-btn")
        self.btn_stats.setCheckable(True)
        self.btn_stats.clicked.connect(self._on_stats_clicked)
        self.nav_button_group.addButton(self.btn_stats)
        layout.addWidget(self.btn_stats)

        # Séparateur
        layout.addSpacing(12)
        sec_sources = QLabel("SOURCES CONNECTÉES")
        sec_sources.setStyleSheet("color: #64748B; font-size: 10px; font-weight: 700; padding: 6px 12px;")
        layout.addWidget(sec_sources)

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
        self.btn_add_source = QPushButton("➕  Ajouter un dossier...")
        self.btn_add_source.setProperty("class", "secondary-btn")
        self.btn_add_source.clicked.connect(self._on_add_local_folder)
        layout.addWidget(self.btn_add_source)

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
        self.search_edit.setPlaceholderText("🔍 Rechercher par titre, artiste, album, genre...")
        self.search_edit.textChanged.connect(self._on_search_changed)
        top_layout.addWidget(self.search_edit)

        top_layout.addStretch()

        # Compteur de morceaux
        self.track_count_label = QLabel("0 morceaux")
        self.track_count_label.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 500;")
        top_layout.addWidget(self.track_count_label)

        # Bouton Scanner / Actualiser
        self.btn_scan_all = QPushButton("🔄  Scanner les sources")
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

        self.status_label = QLabel("Prêt")
        self.status_bar.addWidget(self.status_label, 1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.btn_cancel_scan = QPushButton("Annuler")
        self.btn_cancel_scan.setStyleSheet("font-size: 11px; padding: 2px 8px;")
        self.btn_cancel_scan.setVisible(False)
        self.btn_cancel_scan.clicked.connect(self._cancel_current_scan)
        self.status_bar.addPermanentWidget(self.btn_cancel_scan)

    # -------------------------------------------------------------------------
    # Actions & Événements
    # -------------------------------------------------------------------------

    def refresh_sources_list(self) -> None:
        """Met à jour les boutons de sources dans la barre latérale."""
        # Nettoyage des boutons existants
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
            f"{len(dup_hash)} groupes de doublons par empreinte, "
            f"{len(dup_meta)} groupes par métadonnées détectés."
        )

    def _on_stats_clicked(self) -> None:
        """Affiche un dialogue modal récapitulant les statistiques de la bibliothèque."""
        stats = self.db.get_library_stats()
        size_gb = round(stats["total_size_bytes"] / (1024**3), 2)
        duration_hrs = round(stats["total_duration_seconds"] / 3600, 1)

        fmt_details = ", ".join(f"{k.upper()}: {v}" for k, v in stats["by_format"].items()) or "Aucun"
        src_details = ", ".join(f"{k}: {v}" for k, v in stats["by_source_type"].items()) or "Aucun"

        msg = (
            f"<b>📊 Statistiques de la Bibliothèque :</b><br><br>"
            f"• <b>Total des morceaux :</b> {stats['total_tracks']:,}<br>"
            f"• <b>Volume total :</b> {size_gb} Go<br>"
            f"• <b>Durée d'écoute cumulée :</b> {duration_hrs} heures<br>"
            f"• <b>Sources connectées :</b> {stats['total_sources']}<br><br>"
            f"• <b>Répartition par source :</b> {src_details}<br>"
            f"• <b>Formats audio :</b> {fmt_details}"
        )
        QMessageBox.information(self, "Statistiques AMSO", msg)

    def _on_search_changed(self, text: str) -> None:
        """Déclenche la recherche avec debounce."""
        self._search_timer.start()

    def _perform_search(self) -> None:
        query = self.search_edit.text().strip()
        self.table_model.set_filter(search_query=query)
        self._update_track_count()

    def _update_track_count(self) -> None:
        count = self.table_model.rowCount()
        self.track_count_label.setText(f"{count:,} morceaux")

    def _on_add_local_folder(self) -> None:
        """Permet à l'utilisateur de sélectionner un dossier audio local à ajouter."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Sélectionner un dossier audio à organiser",
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
            "Lancer le scan ?",
            f"Le dossier '{folder_path.name}' a été ajouté.<br>Voulez-vous lancer l'indexation immédiatement ?",
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
                "Aucune source",
                "Ajoutez d'abord un dossier local pour lancer un scan.",
            )
            return

        # Scanner la première source ou itérer
        for src in sources:
            if src.source_type == SourceType.LOCAL:
                self._start_scan(src)
                break

    def _start_scan(self, source: SourceRecord) -> None:
        """Démarre le worker asynchrone de scan."""
        if self.scan_worker and self.scan_worker.isRunning():
            QMessageBox.warning(self, "Scan en cours", "Un scan est déjà en cours d'exécution.")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.btn_cancel_scan.setVisible(True)
        self.status_label.setText(f"Scan en cours de {source.name}...")

        self.scan_worker = ScanWorker(db=self.db, source=source, compute_hash=True, parent=self)
        self.scan_worker.progress.connect(self._on_scan_progress)
        self.scan_worker.status_message.connect(self.status_label.setText)
        self.scan_worker.scan_finished.connect(self._on_scan_finished)
        self.scan_worker.scan_error.connect(self._on_scan_error)
        self.scan_worker.start()

    def _cancel_current_scan(self) -> None:
        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.cancel()
            self.status_label.setText("Annulation en cours...")

    def _on_scan_progress(self, current: int, total: int, current_file: str) -> None:
        if total > 0:
            pct = int((current / total) * 100)
            self.progress_bar.setValue(pct)
            fn = Path(current_file).name
            self.status_label.setText(f"Indexation ({current}/{total}) : {fn}")

    def _on_scan_finished(self, summary: ScanSummary) -> None:
        self.progress_bar.setVisible(False)
        self.btn_cancel_scan.setVisible(False)
        self.table_model.reload_data()
        self._update_track_count()

        if summary.cancelled:
            self.status_label.setText("Scan interrompu par l'utilisateur.")
        else:
            self.status_label.setText(
                f"Scan terminé en {summary.elapsed_seconds}s : "
                f"+{summary.added} ajouts, {summary.updated} mis à jour, {summary.unchanged} inchangés."
            )

    def _on_scan_error(self, err_msg: str) -> None:
        self.progress_bar.setVisible(False)
        self.btn_cancel_scan.setVisible(False)
        self.status_label.setText(f"Erreur : {err_msg}")
        QMessageBox.critical(self, "Erreur de scan", f"Une erreur est survenue pendant le scan :<br>{err_msg}")

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

        action_open_dir = QAction("📂 Ouvrir l'emplacement du fichier", self)
        action_open_dir.triggered.connect(lambda: self._open_file_location(track.source_path))
        menu.addAction(action_open_dir)

        menu.addSeparator()

        action_del = QAction("🗑️ Supprimer de la bibliothèque", self)
        action_del.triggered.connect(lambda: self._delete_track_from_lib(track))
        menu.addAction(action_del)

        menu.exec(QCursor.pos())

    def _open_file_location(self, file_path: Optional[str]) -> None:
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "Introuvable", "Le fichier local est introuvable sur le disque.")
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
            "Confirmation",
            f"Voulez-vous supprimer '{track.title}' de la bibliothèque ?<br>(Le fichier sur le disque ne sera pas supprimé)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_track(track.id)
            self.table_model.reload_data()
            self._update_track_count()
