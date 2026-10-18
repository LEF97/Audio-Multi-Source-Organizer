"""Dialogue de confirmation lorsqu'une sélection dépasse 1 000 morceaux à charger dans la playlist."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from amso.core.database import TrackRecord
from amso.core.i18n import tr
from amso.ui.theme import DARK_THEME_QSS


class LargeSelectionDialog(QDialog):
    """Dialogue modal proposant les choix de chargement pour les très grandes listes (> 1000 morceaux)."""

    def __init__(
        self,
        track: TrackRecord,
        total_count: int,
        folder_track_count: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.track = track
        self.total_count = total_count
        self.folder_track_count = folder_track_count
        self._choice: str = "cancel"

        self.setWindowTitle(tr("dialog.large_selection_title"))
        self.setMinimumWidth(560)
        self.setModal(True)
        self.setStyleSheet(DARK_THEME_QSS)

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # En-tête avec badge icône et détails de la sélection
        header = QHBoxLayout()
        header.setSpacing(16)
        header.setAlignment(Qt.AlignmentFlag.AlignTop)

        icon_lbl = QLabel("⚡")
        icon_lbl.setStyleSheet("""
            font-size: 30px;
            padding: 10px;
            background-color: #1A1D24;
            border: 1px solid #282C37;
            border-radius: 12px;
        """)
        header.addWidget(icon_lbl)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        title_lbl = QLabel(tr("dialog.large_selection_title"))
        title_lbl.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        text_layout.addWidget(title_lbl)

        track_title = self.track.title or self.track.file_name or tr("track.untitled")
        artist = self.track.artist or tr("track.unknown_artist")
        track_info = QLabel(f"<b>{track_title}</b> — <span style='color: #94A3B8;'>{artist}</span>")
        track_info.setTextFormat(Qt.TextFormat.RichText)
        track_info.setStyleSheet("color: #38BDF8; font-size: 13px;")
        text_layout.addWidget(track_info)

        folder_name = self.track.folder_name or (Path(self.track.folder_path).name if self.track.folder_path else "")
        if folder_name:
            folder_lbl = QLabel(f"📁 {folder_name}")
            folder_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
            text_layout.addWidget(folder_lbl)

        header.addLayout(text_layout, 1)
        layout.addLayout(header)

        # Question / Explication
        prompt_lbl = QLabel(tr("dialog.large_selection_prompt", count=f"{self.total_count:,}"))
        prompt_lbl.setStyleSheet("color: #E2E8F0; font-size: 13px; font-weight: 600; margin-top: 4px;")
        prompt_lbl.setWordWrap(True)
        layout.addWidget(prompt_lbl)

        # Conteneur des boutons d'options
        options_frame = QFrame()
        options_frame.setStyleSheet("""
            QFrame {
                background-color: #161920;
                border: 1px solid #282C37;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        options_layout = QVBoxLayout(options_frame)
        options_layout.setSpacing(10)

        button_qss = """
            QPushButton {
                background-color: #1A1E26;
                color: #F8FAFC;
                border: 1px solid #2D3342;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1E293B;
                border-color: #38BDF8;
                color: #38BDF8;
            }
        """

        # Option 1 : Lire uniquement le dossier du morceau
        if self.folder_track_count > 0:
            count_str = f"{self.folder_track_count:,}"
            btn_folder_text = (
                f"{tr('dialog.large_selection_opt_folder', count=count_str)}\n"
                f"   {tr('dialog.large_selection_opt_folder_desc')}"
            )
            btn_folder = QPushButton(btn_folder_text)
            btn_folder.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_folder.setStyleSheet(button_qss)
            btn_folder.clicked.connect(lambda: self._choose("folder"))
            options_layout.addWidget(btn_folder)

        # Option 2 : Limiter aux 1 000 titres suivants
        btn_limit_text = (
            f"{tr('dialog.large_selection_opt_limit')}\n"
            f"   {tr('dialog.large_selection_opt_limit_desc')}"
        )
        btn_limit = QPushButton(btn_limit_text)
        btn_limit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_limit.setStyleSheet(button_qss)
        btn_limit.clicked.connect(lambda: self._choose("limit_1000"))
        options_layout.addWidget(btn_limit)

        # Option 3 : Tout charger
        btn_all_text = (
            f"{tr('dialog.large_selection_opt_all', count=f'{self.total_count:,}')}\n"
            f"   {tr('dialog.large_selection_opt_all_desc')}"
        )
        btn_all = QPushButton(btn_all_text)
        btn_all.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_all.setStyleSheet(button_qss)
        btn_all.clicked.connect(lambda: self._choose("play_all"))
        options_layout.addWidget(btn_all)

        layout.addWidget(options_frame)

        # Bouton Annuler
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        btn_cancel = QPushButton(tr("dialog.btn_cancel"))
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94A3B8;
                border: 1px solid #333846;
                border-radius: 6px;
                padding: 6px 18px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #20242D;
                color: #F8FAFC;
                border-color: #475569;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        bottom_layout.addWidget(btn_cancel)

        layout.addLayout(bottom_layout)

    def _choose(self, choice: str) -> None:
        self._choice = choice
        self.accept()

    def get_choice(self) -> str:
        return self._choice
