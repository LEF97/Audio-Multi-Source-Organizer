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

from amso.core.activity_messages import display_action, display_details, display_level
from amso.core.database import ActivityLogRecord
from amso.core.i18n import tr
from amso.ui.styles import (
    COLOR_BG_DARK,
    COLOR_BORDER_LIGHT,
    COLOR_PRIMARY,
    COLOR_PRIMARY_DARK,
    COLOR_PRIMARY_HOVER,
    COLOR_SUCCESS,
    COLOR_TEXT,
    COLOR_TEXT_BRIGHT,
    COLOR_TEXT_SOFT,
)


class LogDetailDialog(QDialog):
    """Boîte de dialogue affichant l'intégralité des détails d'un enregistrement de log."""

    def __init__(self, record: ActivityLogRecord, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("logs.detail_dialog_title"))
        self.setMinimumSize(560, 420)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: #121418;
                color: {COLOR_TEXT_SOFT};
            }}
            QLabel {{
                color: {COLOR_TEXT};
                font-size: 13px;
            }}
            QTextEdit {{
                background-color: {COLOR_BG_DARK};
                border: 1px solid {COLOR_BORDER_LIGHT};
                border-radius: 6px;
                color: {COLOR_TEXT_BRIGHT};
                font-family: "Consolas", monospace;
                font-size: 12px;
                padding: 8px;
            }}
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_DARK};
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # En-tête
        header = QLabel(f"<b>{display_action(record)}</b>")
        header.setStyleSheet(f"font-size: 16px; color: {COLOR_PRIMARY_HOVER};")
        layout.addWidget(header)

        # Métadonnées
        meta_grid = QVBoxLayout()
        meta_grid.setSpacing(6)

        lvl_color = (
            COLOR_SUCCESS
            if record.level == "SUCCESS"
            else (
                "#FBBF24"
                if record.level == "WARNING"
                else ("#F87171" if record.level == "ERROR" else COLOR_PRIMARY_HOVER)
            )
        )
        lbl_lvl = QLabel(
            f"<b>{tr('logs.col_level')} :</b> <span style='color: {lvl_color}; font-weight: bold;'>{display_level(record.level)}</span>"
        )
        lbl_time = QLabel(f"<b>{tr('logs.col_time')} :</b> {record.timestamp or '-'}")
        lbl_src = QLabel(f"<b>{tr('table.col_source')} :</b> {record.source_name or '-'}")

        stats_str = tr(
            "logs.detail_stats_values",
            added=record.items_added,
            updated=record.items_updated,
            deleted=record.items_deleted,
            errors=record.items_errors,
        )
        lbl_stats = QLabel(f"<b>{tr('logs.detail_stats')}</b> {stats_str}")

        meta_grid.addWidget(lbl_lvl)
        meta_grid.addWidget(lbl_time)
        meta_grid.addWidget(lbl_src)
        meta_grid.addWidget(lbl_stats)
        layout.addLayout(meta_grid)

        # Zone de texte pour les détails complets
        layout.addWidget(QLabel(f"<b>{tr('logs.col_details')} :</b>"))
        self.txt_details = QTextEdit()
        self.txt_details.setReadOnly(True)
        self.txt_details.setPlainText(display_details(record) or tr("logs.detail_none"))
        layout.addWidget(self.txt_details, 1)

        # Bouton fermer
        btn_close = QPushButton(tr("common.cancel"))
        btn_close.clicked.connect(self.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
