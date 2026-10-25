"""Page Paramètres > Sources (mixin de MainWindow)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from amso.core.database import (
    SourceType,
)
from amso.core.i18n import tr

logger = logging.getLogger(__name__)


class SettingsSourcesPageMixin:
    """Page Paramètres > Sources (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de MainWindow sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    def _create_settings_sources_page(self) -> QWidget:
        """Page dédiée Paramètres > Sources (Configuration des sources et synchronisation)."""
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        top_bar = QFrame()
        top_bar.setObjectName("topBarFrame")
        top_bar.setFixedHeight(50)
        top_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 12, 20, 12)

        self.lbl_settings_sources_page_title = QLabel(tr("settings.page_sources_title"))
        self.lbl_settings_sources_page_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        top_layout.addWidget(self.lbl_settings_sources_page_title)
        top_layout.addStretch()
        main_layout.addWidget(top_bar, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Carte Sources configurées et synchronisation
        card_sources = QFrame()
        card_sources.setProperty("class", "dashboard-card")
        card_sources.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        l_sources = QVBoxLayout(card_sources)
        l_sources.setContentsMargins(18, 16, 18, 16)
        l_sources.setSpacing(10)
        l_sources.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.lbl_card_sources_title = QLabel(tr("settings.section_sources_title"))
        self.lbl_card_sources_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        self.lbl_card_sources_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        l_sources.addWidget(self.lbl_card_sources_title)

        self.lbl_card_sources_desc = QLabel(tr("settings.section_sources_desc"))
        self.lbl_card_sources_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        self.lbl_card_sources_desc.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        l_sources.addWidget(self.lbl_card_sources_desc)

        self.table_settings_sources = QTableWidget()
        self.table_settings_sources.setColumnCount(5)
        self.table_settings_sources.verticalHeader().setVisible(False)
        self.table_settings_sources.verticalHeader().setDefaultSectionSize(40)
        self.table_settings_sources.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table_settings_sources.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_settings_sources.setShowGrid(False)
        self.table_settings_sources.setAlternatingRowColors(True)
        self.table_settings_sources.setMinimumHeight(140)
        self.table_settings_sources.setStyleSheet(
            "QTableWidget { background-color: #0F172A; border: 1px solid #334155; border-radius: 6px; } "
            "QHeaderView::section { background-color: #1E293B; color: #94A3B8; font-weight: 600; padding: 8px 6px; border: none; }"
        )
        self.table_settings_sources.cellDoubleClicked.connect(self._on_settings_source_double_clicked)
        l_sources.addWidget(self.table_settings_sources)

        btn_add_box = QHBoxLayout()
        self.btn_add_source_settings = QPushButton(tr("sidebar.btn_add_source"))
        self.btn_add_source_settings.setProperty("class", "secondary-btn")
        self.btn_add_source_settings.clicked.connect(self._on_add_local_folder)
        btn_add_box.addWidget(self.btn_add_source_settings)
        btn_add_box.addStretch()
        l_sources.addLayout(btn_add_box)

        content_layout.addWidget(card_sources)
        content_layout.addStretch(1)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

        self._refresh_settings_sources_table()
        return container

    def _refresh_settings_sources_table(self) -> None:
        """Remplit le tableau des sources dans la page Paramètres > Sources."""
        if not hasattr(self, "table_settings_sources"):
            return

        self.table_settings_sources.setHorizontalHeaderLabels(
            [
                tr("settings.col_source_name"),
                tr("settings.col_source_path"),
                tr("settings.col_source_mode"),
                tr("settings.col_source_last_scan"),
                tr("settings.col_source_actions"),
            ]
        )
        header = self.table_settings_sources.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table_settings_sources.setColumnWidth(4, 135)

        sources = self.db.get_sources()
        self.table_settings_sources.setRowCount(len(sources))

        mode_labels = {
            "manual": tr("sync_mode.manual"),
            "startup": tr("sync_mode.startup"),
            "interval": tr("sync_mode.interval"),
            "realtime": tr("sync_mode.realtime"),
        }

        for row, src in enumerate(sources):
            # Nom
            icon_str = "📁" if src.source_type == SourceType.LOCAL else "☁️"
            name_item = QTableWidgetItem(f"{icon_str}  {src.name}")
            name_item.setToolTip(src.name)
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table_settings_sources.setItem(row, 0, name_item)

            # Chemin
            path_item = QTableWidgetItem(src.path_or_uri)
            path_item.setToolTip(src.path_or_uri)
            path_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            path_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table_settings_sources.setItem(row, 1, path_item)

            raw_mode = getattr(src, "sync_mode", "manual") or "manual"
            interval_m = getattr(src, "sync_interval_minutes", 60) or 60
            interval_s = getattr(src, "sync_interval_seconds", 60) or 60
            if raw_mode == "interval":
                mode_text = f"⏱️  {interval_m} min"
            elif raw_mode == "realtime":
                mode_text = f"⚡  {mode_labels.get('realtime', 'En continu')} ({interval_s}s)"
            elif raw_mode == "startup":
                mode_text = "🚀  " + mode_labels.get("startup", "Au démarrage")
            else:
                mode_text = "✋  " + mode_labels.get("manual", "Manuel")

            mode_item = QTableWidgetItem(mode_text)
            mode_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            mode_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table_settings_sources.setItem(row, 2, mode_item)

            # Dernière synchro
            if src.last_scanned_at:
                date_str = src.last_scanned_at[:16].replace("T", " ")
            else:
                date_str = tr("settings.last_scan_never")
            last_item = QTableWidgetItem(date_str)
            last_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            last_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
            self.table_settings_sources.setItem(row, 3, last_item)

            # Action : Bouton Modifier (largeur garantie 135px, aucune troncature)
            btn_edit = QPushButton(tr("settings.btn_edit_source"))
            btn_edit.setProperty("class", "secondary-btn")
            btn_edit.setStyleSheet("padding: 4px 12px; font-size: 11.5px; margin: 2px;")
            btn_edit.clicked.connect(lambda checked=False, s=src: self._on_edit_source_properties(s))
            self.table_settings_sources.setCellWidget(row, 4, btn_edit)

        total_h = 42 + len(sources) * 40
        self.table_settings_sources.setFixedHeight(max(140, min(total_h, 400)))
