"""Boîte de dialogue affichant les détails complets d'un enregistrement de log."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from amso.core.database import ActivityLogRecord
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
        lbl_src = QLabel(f"<b>{tr('table.col_source')} :</b> {record.source_name or '-'}")

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
        btn_close = QPushButton(tr("common.cancel"))
        btn_close.clicked.connect(self.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
