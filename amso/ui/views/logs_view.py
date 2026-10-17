"""Vue dédiée à la consultation et gestion des journaux d'activité (Logs).

Accessible depuis le tiroir Paramètres > Logs. Permet de filtrer par niveau,
rechercher par mot-clé, inspecter les détails complets, vider et exporter en CSV.
"""

from __future__ import annotations

import csv
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from amso.core.database import ActivityLogRecord, DatabaseManager
from amso.core.i18n import tr


class LogDetailDialog(QDialog):
    """Boîte de dialogue affichant l'intégralité des détails d'un enregistrement de log."""

    def __init__(self, record: ActivityLogRecord, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("logs.detail_dialog_title"))
        self.setMinimumSize(560, 420)
        self.setStyleSheet(
            """
            QDialog {
                background-color: #121418;
                color: #E2E8F0;
            }
            QLabel {
                color: #CBD5E1;
                font-size: 13px;
            }
            QTextEdit {
                background-color: #1A1D24;
                border: 1px solid #333846;
                border-radius: 6px;
                color: #F8FAFC;
                font-family: "Consolas", monospace;
                font-size: 12px;
                padding: 8px;
            }
            QPushButton {
                background-color: #0284C7;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0369A1;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # En-tête
        header = QLabel(f"<b>{record.action}</b>")
        header.setStyleSheet("font-size: 16px; color: #38BDF8;")
        layout.addWidget(header)

        # Métadonnées
        meta_grid = QVBoxLayout()
        meta_grid.setSpacing(6)

        lvl_color = (
            "#4ADE80"
            if record.level == "SUCCESS"
            else ("#FBBF24" if record.level == "WARNING" else ("#F87171" if record.level == "ERROR" else "#38BDF8"))
        )
        lbl_lvl = QLabel(
            f"<b>{tr('logs.col_level')} :</b> <span style='color: {lvl_color}; font-weight: bold;'>{record.level}</span>"
        )
        lbl_time = QLabel(f"<b>{tr('logs.col_time')} :</b> {record.timestamp or '-'}")
        lbl_src = QLabel(f"<b>{tr('logs.col_source')} :</b> {record.source_name or '-'}")

        stats_str = f"+{record.items_added} ajouts, ~{record.items_updated} modifiés, -{record.items_deleted} supprimés, !{record.items_errors} erreurs"
        lbl_stats = QLabel(f"<b>Statistiques :</b> {stats_str}")

        meta_grid.addWidget(lbl_lvl)
        meta_grid.addWidget(lbl_time)
        meta_grid.addWidget(lbl_src)
        meta_grid.addWidget(lbl_stats)
        layout.addLayout(meta_grid)

        # Zone de texte pour les détails complets
        layout.addWidget(QLabel(f"<b>{tr('logs.col_details')} :</b>"))
        self.txt_details = QTextEdit()
        self.txt_details.setReadOnly(True)
        self.txt_details.setPlainText(record.details or "(Aucun détail supplémentaire)")
        layout.addWidget(self.txt_details, 1)

        # Bouton fermer
        btn_close = QPushButton(tr("dialog.btn_cancel"))
        btn_close.clicked.connect(self.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)


class LogsView(QWidget):
    """Écran complet de consultation des logs et historiques d'événements."""

    def __init__(self, db: DatabaseManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.db = db
        self._current_records: list[ActivityLogRecord] = []
        self._dirty = True

        # Styles et ressources pré-instanciés pour éviter les allocations répétées dans la boucle
        self._font_action = QFont("Segoe UI", 9, QFont.Weight.DemiBold)
        self._color_success = QColor("#4ADE80")
        self._color_warning = QColor("#FBBF24")
        self._color_error = QColor("#F87171")
        self._color_info = QColor("#38BDF8")

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # --- En-tête ---
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)

        self.lbl_title = QLabel(tr("logs.page_title"))
        self.lbl_title.setStyleSheet("font-size: 20px; font-weight: 700; color: #F8FAFC;")
        header_layout.addWidget(self.lbl_title)

        self.lbl_desc = QLabel(tr("logs.page_desc"))
        self.lbl_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        header_layout.addWidget(self.lbl_desc)

        layout.addLayout(header_layout)

        # --- Barre d'outils et filtres ---
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        # Filtre de niveau
        lbl_lvl = QLabel(tr("logs.filter_level"))
        lbl_lvl.setStyleSheet("color: #94A3B8; font-size: 13px;")
        toolbar.addWidget(lbl_lvl)

        self.combo_level = QComboBox()
        self.combo_level.addItem(tr("logs.filter_all"), "ALL")
        self.combo_level.addItem(tr("logs.filter_success"), "SUCCESS")
        self.combo_level.addItem(tr("logs.filter_info"), "INFO")
        self.combo_level.addItem(tr("logs.filter_warning"), "WARNING")
        self.combo_level.addItem(tr("logs.filter_error"), "ERROR")
        self.combo_level.setStyleSheet(
            """
            QComboBox {
                background-color: #20242D;
                color: #F8FAFC;
                border: 1px solid #333846;
                border-radius: 6px;
                padding: 5px 12px;
                min-width: 130px;
            }
            """
        )
        self.combo_level.currentIndexChanged.connect(self._on_filter_changed)
        toolbar.addWidget(self.combo_level)

        # Recherche textuelle
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(tr("logs.search_placeholder"))
        self.search_edit.setStyleSheet(
            """
            QLineEdit {
                background-color: #20242D;
                color: #F8FAFC;
                border: 1px solid #333846;
                border-radius: 6px;
                padding: 5px 12px;
                min-width: 250px;
            }
            QLineEdit:focus {
                border: 1px solid #38BDF8;
            }
            """
        )
        self.search_edit.textChanged.connect(self._on_search_changed)
        toolbar.addWidget(self.search_edit)

        toolbar.addStretch()

        # Bouton Rafraîchir
        self.btn_refresh = QPushButton(tr("logs.btn_refresh"))
        self.btn_refresh.setStyleSheet("padding: 6px 12px;")
        self.btn_refresh.clicked.connect(self.refresh_logs)
        toolbar.addWidget(self.btn_refresh)

        # Bouton Exporter
        self.btn_export = QPushButton(tr("logs.btn_export"))
        self.btn_export.setStyleSheet("padding: 6px 12px;")
        self.btn_export.clicked.connect(self._export_logs_csv)
        toolbar.addWidget(self.btn_export)

        # Bouton Vider
        self.btn_clear = QPushButton(tr("logs.btn_clear"))
        self.btn_clear.setStyleSheet(
            "background-color: #7F1D1D; color: #FCA5A5; border: 1px solid #991B1B; border-radius: 6px; padding: 6px 12px;"
        )
        self.btn_clear.clicked.connect(self._on_clear_logs)
        toolbar.addWidget(self.btn_clear)

        layout.addLayout(toolbar)

        # --- Tableau des logs ---
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(
            [
                tr("logs.col_time"),
                tr("logs.col_level"),
                tr("logs.col_source"),
                tr("logs.col_action"),
                tr("logs.col_added"),
                tr("logs.col_updated"),
                tr("logs.col_deleted"),
                tr("logs.col_errors"),
                tr("logs.col_details"),
            ]
        )
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(
            """
            QTableWidget {
                background-color: #16181F;
                alternate-background-color: #1B1E26;
                color: #CBD5E1;
                border: 1px solid #282C37;
                border-radius: 8px;
                gridline-color: transparent;
            }
            QTableWidget::item {
                padding: 6px 10px;
                border-bottom: 1px solid #232731;
            }
            QTableWidget::item:selected {
                background-color: #0284C7;
                color: white;
            }
            QHeaderView::section {
                background-color: #1A1D24;
                color: #94A3B8;
                font-weight: 600;
                font-size: 12px;
                border: none;
                border-bottom: 1px solid #282C37;
                padding: 8px 10px;
            }
            """
        )

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)

        # Largeurs initiales prédéfinies : évite les calculs ResizeToContents extrêmement lourds
        self.table.setColumnWidth(0, 145)  # Date / Heure
        self.table.setColumnWidth(1, 85)  # Niveau
        self.table.setColumnWidth(2, 110)  # Source
        self.table.setColumnWidth(3, 230)  # Action
        self.table.setColumnWidth(4, 55)  # Ajouts
        self.table.setColumnWidth(5, 55)  # Modifiés
        self.table.setColumnWidth(6, 55)  # Supprimés
        self.table.setColumnWidth(7, 55)  # Erreurs

        self.table.doubleClicked.connect(self._on_table_double_clicked)
        layout.addWidget(self.table, 1)

        # --- Pied de page ---
        footer_layout = QHBoxLayout()
        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet("color: #64748B; font-size: 12px;")
        footer_layout.addWidget(self.lbl_count)
        footer_layout.addStretch()
        layout.addLayout(footer_layout)

    def mark_dirty(self) -> None:
        """Marque les logs comme périmés et actualise la table."""
        self._dirty = True
        self.refresh_logs()

    def refresh_if_dirty(self) -> None:
        """Rafraîchit les logs uniquement si les données sont périmées."""
        if getattr(self, "_dirty", True):
            self.refresh_logs()

    def _on_filter_changed(self) -> None:
        self.refresh_logs()

    def _on_search_changed(self) -> None:
        self.refresh_logs()

    def refresh_logs(self) -> None:
        """Charge les logs depuis la base de données selon les filtres courants."""
        level = self.combo_level.currentData()
        search = self.search_edit.text().strip() or None

        self._current_records = self.db.get_activity_logs(
            limit=500,
            level=level,
            search=search,
        )

        align_center = Qt.AlignmentFlag.AlignCenter
        self.table.setUpdatesEnabled(False)
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(len(self._current_records))
            for row, rec in enumerate(self._current_records):
                # 0. Horodatage
                item_ts = QTableWidgetItem(rec.timestamp or "")
                self.table.setItem(row, 0, item_ts)

                # 1. Niveau avec couleur et badge
                item_lvl = QTableWidgetItem(rec.level)
                item_lvl.setTextAlignment(align_center)
                if rec.level == "SUCCESS":
                    item_lvl.setForeground(self._color_success)
                elif rec.level == "WARNING":
                    item_lvl.setForeground(self._color_warning)
                elif rec.level == "ERROR":
                    item_lvl.setForeground(self._color_error)
                else:
                    item_lvl.setForeground(self._color_info)
                self.table.setItem(row, 1, item_lvl)

                # 2. Source
                item_src = QTableWidgetItem(rec.source_name or "-")
                self.table.setItem(row, 2, item_src)

                # 3. Action
                item_act = QTableWidgetItem(rec.action)
                item_act.setFont(self._font_action)
                self.table.setItem(row, 3, item_act)

                # 4. Ajouts
                item_add = QTableWidgetItem(f"+{rec.items_added}" if rec.items_added > 0 else "-")
                item_add.setTextAlignment(align_center)
                if rec.items_added > 0:
                    item_add.setForeground(self._color_success)
                self.table.setItem(row, 4, item_add)

                # 5. Modifiés
                item_upd = QTableWidgetItem(f"~{rec.items_updated}" if rec.items_updated > 0 else "-")
                item_upd.setTextAlignment(align_center)
                if rec.items_updated > 0:
                    item_upd.setForeground(self._color_info)
                self.table.setItem(row, 5, item_upd)

                # 6. Supprimés
                item_del = QTableWidgetItem(f"-{rec.items_deleted}" if rec.items_deleted > 0 else "-")
                item_del.setTextAlignment(align_center)
                if rec.items_deleted > 0:
                    item_del.setForeground(self._color_error)
                self.table.setItem(row, 6, item_del)

                # 7. Erreurs
                item_err = QTableWidgetItem(f"!{rec.items_errors}" if rec.items_errors > 0 else "-")
                item_err.setTextAlignment(align_center)
                if rec.items_errors > 0:
                    item_err.setForeground(self._color_error)
                self.table.setItem(row, 7, item_err)

                # 8. Détails
                item_det = QTableWidgetItem(rec.details or "")
                self.table.setItem(row, 8, item_det)
        finally:
            self.table.blockSignals(False)
            self.table.setUpdatesEnabled(True)

        self._dirty = False
        self.lbl_count.setText(tr("logs.count_entries", count=len(self._current_records)))

    def _on_table_double_clicked(self) -> None:
        row = self.table.currentRow()
        if 0 <= row < len(self._current_records):
            record = self._current_records[row]
            dialog = LogDetailDialog(record, parent=self)
            dialog.exec()

    def _on_clear_logs(self) -> None:
        ans = QMessageBox.question(
            self,
            tr("logs.clear_confirm_title"),
            tr("logs.clear_confirm_message"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if ans == QMessageBox.StandardButton.Yes:
            self.db.clear_activity_logs()
            self.refresh_logs()

    def _export_logs_csv(self) -> None:
        """Exporte la liste actuelle des logs dans un fichier CSV."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr("logs.btn_export"),
            f"amso_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)",
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(
                    [
                        "ID",
                        "Timestamp",
                        "Level",
                        "Category",
                        "Source",
                        "Action",
                        "Added",
                        "Updated",
                        "Deleted",
                        "Errors",
                        "Details",
                    ]
                )
                for r in self._current_records:
                    writer.writerow(
                        [
                            r.id,
                            r.timestamp,
                            r.level,
                            r.category,
                            r.source_name,
                            r.action,
                            r.items_added,
                            r.items_updated,
                            r.items_deleted,
                            r.items_errors,
                            r.details,
                        ]
                    )
            QMessageBox.information(self, "Export", "Logs exportés avec succès !")
        except Exception as e:
            QMessageBox.critical(self, "Erreur d'exportation", f"Impossible d'exporter les logs :\n{e}")
