"""Popover d'affichage détaillé du fil des actions en cours et prévues (AMSO).

S'affiche au survol de la zone d'état en bas à droite pour offrir une vue
synthétique sur l'action active, la file d'attente, les synchronisations
planifiées et les dernières opérations terminées avec lien vers les logs.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QPoint, Qt, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from amso.core.activity_messages import display_action
from amso.core.database import DatabaseManager, SourceRecord
from amso.core.i18n import tr
from amso.core.scheduler import SyncScheduler


class ActivityFeedPopover(QFrame):
    """Popover flottant affichant l'état des opérations en cours et à venir."""

    open_logs_requested = Signal()

    def __init__(
        self,
        db: DatabaseManager,
        scheduler: SyncScheduler | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.db = db
        self.scheduler = scheduler

        # Configuration de la fenêtre flottante sans cadre avec ombre
        self.setWindowFlags(
            Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.setInterval(350)
        self._hide_timer.timeout.connect(self.hide)

        # Timer d'actualisation en temps réel du popover s'il est visible
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(1000)
        self._refresh_timer.timeout.connect(self._on_tick_refresh)

        # Données dynamiques de progression
        self._current_progress_text: str = ""
        self._current_progress_pct: int | None = None

        self._init_ui()

    def _init_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(10, 10, 10, 10)

        # Conteneur principal avec style sombre et bordure lumineuse
        self.card = QFrame(self)
        self.card.setObjectName("activityCard")
        self.card.setStyleSheet(
            """
            QFrame#activityCard {
                background-color: #0F172A;
                border: 1px solid #334155;
                border-radius: 12px;
            }
            QLabel {
                color: #E2E8F0;
                font-family: "Segoe UI", -apple-system, sans-serif;
            }
            """
        )

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 6)
        self.card.setGraphicsEffect(shadow)

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(16, 14, 16, 14)
        self.card_layout.setSpacing(12)

        # --- 1. En-tête ---
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        self.lbl_title = QLabel(tr("feed.title"))
        self.lbl_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #38BDF8;")
        header_layout.addWidget(self.lbl_title)

        header_layout.addStretch()

        self.lbl_badge_status = QLabel("")
        self.lbl_badge_status.setStyleSheet("font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px;")
        header_layout.addWidget(self.lbl_badge_status)
        self.card_layout.addLayout(header_layout)

        # Ligne de séparation
        self.card_layout.addWidget(self._create_separator())

        # --- 2. Action en cours ---
        self.sec_current = QWidget()
        sec_current_layout = QVBoxLayout(self.sec_current)
        sec_current_layout.setContentsMargins(0, 0, 0, 0)
        sec_current_layout.setSpacing(4)

        self.lbl_cur_title = QLabel(f"<b>{tr('feed.current_action')}</b>")
        self.lbl_cur_title.setStyleSheet(
            "font-size: 12px; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;"
        )
        sec_current_layout.addWidget(self.lbl_cur_title)

        self.cur_box = QFrame()
        self.cur_box.setStyleSheet("background-color: #1E293B; border: 1px solid #334155; border-radius: 8px;")
        cur_box_layout = QVBoxLayout(self.cur_box)
        cur_box_layout.setContentsMargins(10, 8, 10, 8)
        cur_box_layout.setSpacing(4)

        self.lbl_cur_source = QLabel("")
        self.lbl_cur_source.setStyleSheet("font-size: 13px; font-weight: 600; color: #F8FAFC;")
        cur_box_layout.addWidget(self.lbl_cur_source)

        self.lbl_cur_detail = QLabel("")
        self.lbl_cur_detail.setStyleSheet("font-size: 11px; color: #94A3B8;")
        self.lbl_cur_detail.setWordWrap(True)
        cur_box_layout.addWidget(self.lbl_cur_detail)

        self.cur_progress = QProgressBar()
        self.cur_progress.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #334155;
                border-radius: 4px;
                background-color: #0F172A;
                text-align: center;
                height: 10px;
                font-size: 9px;
                color: #CBD5E1;
            }
            QProgressBar::chunk {
                background-color: #0284C7;
                border-radius: 3px;
            }
            """
        )
        self.cur_progress.setFixedHeight(10)
        cur_box_layout.addWidget(self.cur_progress)

        sec_current_layout.addWidget(self.cur_box)
        self.card_layout.addWidget(self.sec_current)

        # --- 3. File d'attente (Queue) ---
        self.sec_queue = QWidget()
        sec_queue_layout = QVBoxLayout(self.sec_queue)
        sec_queue_layout.setContentsMargins(0, 0, 0, 0)
        sec_queue_layout.setSpacing(4)

        self.lbl_queue_title = QLabel(f"<b>{tr('feed.queue')}</b>")
        self.lbl_queue_title.setStyleSheet(
            "font-size: 12px; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;"
        )
        sec_queue_layout.addWidget(self.lbl_queue_title)

        self.lbl_queue_content = QLabel("")
        self.lbl_queue_content.setStyleSheet("font-size: 12px; color: #CBD5E1; padding-left: 4px;")
        self.lbl_queue_content.setWordWrap(True)
        sec_queue_layout.addWidget(self.lbl_queue_content)
        self.card_layout.addWidget(self.sec_queue)

        # --- 4. Synchronisations planifiées ---
        self.sec_upcoming = QWidget()
        sec_upcoming_layout = QVBoxLayout(self.sec_upcoming)
        sec_upcoming_layout.setContentsMargins(0, 0, 0, 0)
        sec_upcoming_layout.setSpacing(4)

        self.lbl_up_title = QLabel(f"<b>{tr('feed.upcoming')}</b>")
        self.lbl_up_title.setStyleSheet(
            "font-size: 12px; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;"
        )
        sec_upcoming_layout.addWidget(self.lbl_up_title)

        self.lbl_upcoming_content = QLabel("")
        self.lbl_upcoming_content.setStyleSheet("font-size: 12px; color: #CBD5E1; padding-left: 4px;")
        self.lbl_upcoming_content.setWordWrap(True)
        sec_upcoming_layout.addWidget(self.lbl_upcoming_content)
        self.card_layout.addWidget(self.sec_upcoming)

        # --- 5. Activité récente (Derniers logs) ---
        self.sec_recent = QWidget()
        sec_recent_layout = QVBoxLayout(self.sec_recent)
        sec_recent_layout.setContentsMargins(0, 0, 0, 0)
        sec_recent_layout.setSpacing(4)

        self.lbl_rec_title = QLabel(f"<b>{tr('feed.recent_activity')}</b>")
        self.lbl_rec_title.setStyleSheet(
            "font-size: 12px; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;"
        )
        sec_recent_layout.addWidget(self.lbl_rec_title)

        self.lbl_recent_content = QLabel("")
        self.lbl_recent_content.setStyleSheet("font-size: 11px; color: #94A3B8; padding-left: 4px;")
        self.lbl_recent_content.setWordWrap(True)
        sec_recent_layout.addWidget(self.lbl_recent_content)
        self.card_layout.addWidget(self.sec_recent)

        # Ligne de séparation
        self.card_layout.addWidget(self._create_separator())

        # --- 6. Bouton d'accès aux logs complets ---
        self.btn_view_logs = QPushButton(tr("feed.btn_view_logs"))
        self.btn_view_logs.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_view_logs.setStyleSheet(
            """
            QPushButton {
                background-color: #1E293B;
                color: #38BDF8;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 600;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #0284C7;
                color: #FFFFFF;
                border: 1px solid #38BDF8;
            }
            """
        )
        self.btn_view_logs.clicked.connect(self._on_open_logs)
        self.card_layout.addWidget(self.btn_view_logs)

        outer_layout.addWidget(self.card)
        self.setFixedWidth(380)

    def _create_separator(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        sep.setStyleSheet("background-color: #1E293B; max-height: 1px; border: none;")
        return sep

    def update_progress(self, message: str, pct: int | None = None) -> None:
        """Met à jour le texte et le pourcentage de l'action en cours de façon ultra-légère."""
        self._current_progress_text = message
        self._current_progress_pct = pct
        if self.isVisible():
            if hasattr(self, "lbl_cur_detail"):
                self.lbl_cur_detail.setText(message)
            if hasattr(self, "cur_progress") and pct is not None and pct >= 0:
                self.cur_progress.setVisible(True)
                self.cur_progress.setValue(pct)

    def refresh_content(self) -> None:
        """Réactualise toutes les sections du fil d'actions."""
        # 1. État du scheduler
        status = self.scheduler.get_schedule_status() if self.scheduler else {}
        current_source: SourceRecord | None = status.get("current_source")
        queue_sources: list[SourceRecord] = status.get("queue_sources", [])
        upcoming: list[dict[str, Any]] = status.get("upcoming", [])

        # 2. Section Action en cours
        if current_source:
            self.lbl_badge_status.setText("● SYNCHRO ACTIVE")
            self.lbl_badge_status.setStyleSheet(
                "background-color: rgba(56, 189, 248, 0.2); color: #38BDF8; "
                "border: 1px solid rgba(56, 189, 248, 0.5); font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 8px;"
            )
            self.lbl_cur_source.setText(f"🔄  {current_source.name}")
            detail_text = self._current_progress_text or tr("status.scanning", source=current_source.name)
            self.lbl_cur_detail.setText(detail_text)

            if self._current_progress_pct is not None and self._current_progress_pct >= 0:
                self.cur_progress.setVisible(True)
                self.cur_progress.setValue(self._current_progress_pct)
            else:
                self.cur_progress.setVisible(False)
        else:
            self.lbl_badge_status.setText(tr("status.system_ready"))
            self.lbl_badge_status.setStyleSheet(
                "background-color: rgba(34, 197, 94, 0.2); color: #4ADE80; "
                "border: 1px solid rgba(34, 197, 94, 0.5); font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 8px;"
            )
            self.lbl_cur_source.setText(tr("feed.no_current_action"))
            self.lbl_cur_detail.setText(self._current_progress_text or "")
            self.cur_progress.setVisible(False)

        # 3. Section File d'attente
        if queue_sources:
            lines = []
            for i, s in enumerate(queue_sources, 1):
                lines.append(f"<b>#{i}</b> {s.name}")
            self.lbl_queue_content.setText("<br>".join(lines))
        else:
            self.lbl_queue_content.setText(f"<span style='color: #64748B;'>{tr('feed.queue_empty')}</span>")

        # 4. Section Prochaines synchronisations
        if upcoming:
            lines = []
            for item in upcoming[:4]:  # Top 4 pour ne pas déborder
                src: SourceRecord = item["source"]
                mode = item["mode"]
                if mode == "realtime":
                    badge = f"<span style='color: #4ADE80;'>⚡ {tr('feed.mode_realtime')}</span>"
                else:
                    sec = item.get("remaining_seconds", 0)
                    if sec < 60:
                        t_str = f"{sec}s"
                    else:
                        t_str = f"{sec // 60} min"
                    rem = tr("feed.remaining_time", time=t_str)
                    badge = f"<span style='color: #FBBF24;'>⏱️ {rem}</span>"
                lines.append(f"• <b>{src.name}</b> : {badge}")
            self.lbl_upcoming_content.setText("<br>".join(lines))
        else:
            self.lbl_upcoming_content.setText(f"<span style='color: #64748B;'>{tr('feed.no_upcoming')}</span>")

        # 5. Section Dernières activités (3 derniers logs de la BDD)
        try:
            recent_logs = self.db.get_activity_logs(limit=3)
            if recent_logs:
                lines = []
                for log in recent_logs:
                    ts = (log.timestamp or "").split()[-1] if log.timestamp else ""
                    if log.level == "SUCCESS":
                        icon = "<span style='color: #4ADE80;'>✓</span>"
                    elif log.level == "WARNING":
                        icon = "<span style='color: #FBBF24;'>⚠</span>"
                    elif log.level == "ERROR":
                        icon = "<span style='color: #F87171;'>✕</span>"
                    else:
                        icon = "<span style='color: #38BDF8;'>ℹ</span>"

                    summary = display_action(log)
                    if log.items_added or log.items_updated or log.items_deleted:
                        summary += f" (+{log.items_added}/~{log.items_updated}/-{log.items_deleted})"

                    lines.append(
                        f"{icon} <span style='color: #94A3B8;'>{ts}</span> <b>{log.source_name or ''}</b> {summary}"
                    )
                self.lbl_recent_content.setText("<br>".join(lines))
            else:
                self.lbl_recent_content.setText(f"<span style='color: #64748B;'>{tr('feed.no_recent_activity')}</span>")
        except Exception:
            self.lbl_recent_content.setText(f"<span style='color: #64748B;'>{tr('feed.no_recent_activity')}</span>")

        self.adjustSize()

    def show_above_widget(self, target_widget: QWidget) -> None:
        """Positionne et affiche le popover au-dessus du widget cible."""
        self._hide_timer.stop()
        self.refresh_content()
        self.show()

        target_rect = target_widget.rect()
        global_target = target_widget.mapToGlobal(QPoint(0, 0))

        # Aligner à droite du widget cible, légèrement au-dessus
        popover_w = self.width()
        popover_h = self.height()

        x = global_target.x() + target_rect.width() - popover_w
        y = global_target.y() - popover_h - 4

        self.move(x, y)
        self.raise_()
        self._refresh_timer.start()

    def schedule_hide(self) -> None:
        """Déclenche le masquage différé pour laisser le temps à la souris d'entrer."""
        self._hide_timer.start()

    def cancel_hide(self) -> None:
        """Annule le masquage."""
        self._hide_timer.stop()

    def enterEvent(self, event: Any) -> None:
        self.cancel_hide()
        super().enterEvent(event)

    def leaveEvent(self, event: Any) -> None:
        self.schedule_hide()
        super().leaveEvent(event)

    def _on_tick_refresh(self) -> None:
        if self.isVisible():
            self.refresh_content()
        else:
            self._refresh_timer.stop()

    def _on_open_logs(self) -> None:
        self.hide()
        self.open_logs_requested.emit()

    def retranslate_ui(self) -> None:
        """Met à jour les libellés traduits du popover."""
        self.lbl_title.setText(tr("feed.title"))
        self.lbl_cur_title.setText(f"<b>{tr('feed.current_action')}</b>")
        self.lbl_queue_title.setText(f"<b>{tr('feed.queue')}</b>")
        self.lbl_up_title.setText(f"<b>{tr('feed.upcoming')}</b>")
        self.lbl_rec_title.setText(f"<b>{tr('feed.recent_activity')}</b>")
        self.btn_view_logs.setText(tr("feed.btn_view_logs"))
        self.refresh_content()
