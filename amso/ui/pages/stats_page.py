"""Page Statistiques (mixin de MainWindow)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from amso.core.db.models import SourceType
from amso.core.i18n import tr

logger = logging.getLogger(__name__)


def _source_type_label(source_type: str) -> str:
    if source_type == SourceType.LOCAL:
        return tr("stats.source_type_local")
    return source_type.capitalize()


class StatsPageMixin:
    """Page Statistiques (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de MainWindow sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    def _create_stats_page(self) -> QWidget:
        """Page dédiée aux statistiques de la bibliothèque."""
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # En-tête de page
        top_bar = QFrame()
        top_bar.setObjectName("topBarFrame")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 12, 20, 12)

        self.lbl_stats_page_title = QLabel(tr("stats.page_title"))
        self.lbl_stats_page_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        top_layout.addWidget(self.lbl_stats_page_title)

        top_layout.addStretch()

        self.btn_refresh_stats = QPushButton(tr("common.refresh"))
        self.btn_refresh_stats.setProperty("class", "secondary-btn")
        self.btn_refresh_stats.clicked.connect(self._refresh_stats_view)
        top_layout.addWidget(self.btn_refresh_stats)

        main_layout.addWidget(top_bar)

        # Zone de contenu défilante
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)

        # Rangée des 4 cartes KPI
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(12)

        # 1. Total Morceaux
        self.card_tracks = QFrame()
        self.card_tracks.setProperty("class", "dashboard-card")
        l1 = QVBoxLayout(self.card_tracks)
        l1.setContentsMargins(16, 14, 16, 14)
        self.lbl_kpi_tracks_title = QLabel(tr("stats.card_tracks"))
        self.lbl_kpi_tracks_title.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 600;")
        self.kpi_tracks_val = QLabel("0")
        self.kpi_tracks_val.setStyleSheet("color: #38BDF8; font-size: 26px; font-weight: 700;")
        l1.addWidget(self.lbl_kpi_tracks_title)
        l1.addWidget(self.kpi_tracks_val)
        kpi_layout.addWidget(self.card_tracks)

        # 2. Volume Total
        self.card_size = QFrame()
        self.card_size.setProperty("class", "dashboard-card")
        l2 = QVBoxLayout(self.card_size)
        l2.setContentsMargins(16, 14, 16, 14)
        self.lbl_kpi_size_title = QLabel(tr("stats.card_size"))
        self.lbl_kpi_size_title.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 600;")
        self.kpi_size_val = QLabel(tr("stats.size_value", size=0))
        self.kpi_size_val.setStyleSheet("color: #10B981; font-size: 26px; font-weight: 700;")
        l2.addWidget(self.lbl_kpi_size_title)
        l2.addWidget(self.kpi_size_val)
        kpi_layout.addWidget(self.card_size)

        # 3. Durée d'écoute
        self.card_duration = QFrame()
        self.card_duration.setProperty("class", "dashboard-card")
        l3 = QVBoxLayout(self.card_duration)
        l3.setContentsMargins(16, 14, 16, 14)
        self.lbl_kpi_duration_title = QLabel(tr("stats.card_duration"))
        self.lbl_kpi_duration_title.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 600;")
        self.kpi_duration_val = QLabel("0 h")
        self.kpi_duration_val.setStyleSheet("color: #A855F7; font-size: 26px; font-weight: 700;")
        l3.addWidget(self.lbl_kpi_duration_title)
        l3.addWidget(self.kpi_duration_val)
        kpi_layout.addWidget(self.card_duration)

        # 4. Sources connectées
        self.card_sources = QFrame()
        self.card_sources.setProperty("class", "dashboard-card")
        l4 = QVBoxLayout(self.card_sources)
        l4.setContentsMargins(16, 14, 16, 14)
        self.lbl_kpi_sources_title = QLabel(tr("stats.card_sources"))
        self.lbl_kpi_sources_title.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 600;")
        self.kpi_sources_val = QLabel("0")
        self.kpi_sources_val.setStyleSheet("color: #F59E0B; font-size: 26px; font-weight: 700;")
        l4.addWidget(self.lbl_kpi_sources_title)
        l4.addWidget(self.kpi_sources_val)
        kpi_layout.addWidget(self.card_sources)

        content_layout.addLayout(kpi_layout)

        # Cartes de détail (Formats & Sources)
        details_layout = QHBoxLayout()
        details_layout.setSpacing(14)

        # Détail Formats
        card_formats = QFrame()
        card_formats.setProperty("class", "dashboard-card")
        lf = QVBoxLayout(card_formats)
        lf.setContentsMargins(18, 16, 18, 16)
        self.lbl_section_formats = QLabel(tr("stats.section_formats"))
        self.lbl_section_formats.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700; margin-bottom: 8px;")
        lf.addWidget(self.lbl_section_formats)
        self.lbl_formats_breakdown = QLabel()
        self.lbl_formats_breakdown.setStyleSheet("color: #94A3B8; font-size: 13px; line-height: 1.6;")
        lf.addWidget(self.lbl_formats_breakdown)
        lf.addStretch()
        details_layout.addWidget(card_formats, 1)

        # Détail Types de source
        card_src = QFrame()
        card_src.setProperty("class", "dashboard-card")
        ls = QVBoxLayout(card_src)
        ls.setContentsMargins(18, 16, 18, 16)
        self.lbl_section_sources = QLabel(tr("stats.section_sources"))
        self.lbl_section_sources.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700; margin-bottom: 8px;")
        ls.addWidget(self.lbl_section_sources)
        self.lbl_sources_breakdown = QLabel()
        self.lbl_sources_breakdown.setStyleSheet("color: #94A3B8; font-size: 13px; line-height: 1.6;")
        ls.addWidget(self.lbl_sources_breakdown)
        ls.addStretch()
        details_layout.addWidget(card_src, 1)

        content_layout.addLayout(details_layout)
        content_layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        return container

    def _refresh_stats_view(self) -> None:
        """Met à jour les cartes et métriques de la page Statistiques."""
        stats = self.db.get_library_stats()
        size_gb = round(stats["total_size_bytes"] / (1024**3), 2)
        duration_hrs = round(stats["total_duration_seconds"] / 3600, 1)

        self.kpi_tracks_val.setText(f"{stats['total_tracks']:,}")
        self.kpi_size_val.setText(tr("stats.size_value", size=size_gb))
        self.kpi_duration_val.setText(tr("stats.duration_value", hours=duration_hrs))
        self.kpi_sources_val.setText(str(stats["total_sources"]))

        # Détail Formats
        if stats["by_format"]:
            fmts_lines = [
                f"• <b>{k.upper()}</b> : {tr('folders.track_count', count=f'{v:,}')}"
                for k, v in stats["by_format"].items()
            ]
            self.lbl_formats_breakdown.setText("<br>".join(fmts_lines))
        else:
            self.lbl_formats_breakdown.setText(f"<i>{tr('dialog.stats_none')}</i>")

        # Détail Sources
        if stats["by_source_type"]:
            srcs_lines = [
                f"• <b>{_source_type_label(k)}</b> : {tr('folders.track_count', count=f'{v:,}')}"
                for k, v in stats["by_source_type"].items()
            ]
            self.lbl_sources_breakdown.setText("<br>".join(srcs_lines))
        else:
            self.lbl_sources_breakdown.setText(f"<i>{tr('dialog.stats_none')}</i>")
