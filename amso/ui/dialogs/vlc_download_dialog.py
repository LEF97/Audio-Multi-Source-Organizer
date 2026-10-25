"""Boîte de dialogue de téléchargement et d'installation automatique de VLC pour AMSO."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from amso.core.i18n import tr
from amso.services.player_service import PlayerService
from amso.services.vlc_downloader import VlcDownloadWorker
from amso.ui.theme import DARK_THEME_QSS


class VlcDownloadDialog(QDialog):
    """Dialogue guidant le téléchargement automatique et transparent des composants VLC."""

    def __init__(self, player_service: PlayerService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.player_service = player_service
        self.worker: VlcDownloadWorker | None = None

        self.setWindowTitle(tr("dialog.vlc_title"))
        self.setMinimumWidth(520)
        self.setModal(True)
        self.setStyleSheet(DARK_THEME_QSS)

        self._setup_ui()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)

        # En-tête avec icône et texte
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        icon_lbl = QLabel("🎵")
        icon_lbl.setStyleSheet("""
            font-size: 38px;
            padding: 10px;
            background-color: #1A1D24;
            border: 1px solid #282C37;
            border-radius: 12px;
        """)
        header_layout.addWidget(icon_lbl)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(6)

        title_lbl = QLabel(tr("dialog.vlc_title"))
        title_lbl.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        text_layout.addWidget(title_lbl)

        self.lbl_desc = QLabel(tr("dialog.vlc_desc"))
        self.lbl_desc.setStyleSheet("color: #94A3B8; font-size: 13px; line-height: 1.4;")
        self.lbl_desc.setWordWrap(True)
        text_layout.addWidget(self.lbl_desc)

        header_layout.addLayout(text_layout, 1)
        main_layout.addLayout(header_layout)

        # Zone de progression (masquée au début)
        self.progress_frame = QFrame()
        self.progress_frame.setStyleSheet("""
            background-color: #1A1D24;
            border: 1px solid #282C37;
            border-radius: 8px;
            padding: 14px;
        """)
        self.progress_frame.setVisible(False)
        prog_layout = QVBoxLayout(self.progress_frame)
        prog_layout.setSpacing(10)

        self.lbl_status = QLabel(tr("dialog.vlc_downloading"))
        self.lbl_status.setStyleSheet("color: #E2E8F0; font-size: 12px; font-weight: 500;")
        prog_layout.addWidget(self.lbl_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(12)
        prog_layout.addWidget(self.progress_bar)

        main_layout.addWidget(self.progress_frame)

        # Barre de boutons
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setSpacing(10)
        self.buttons_layout.addStretch()

        self.btn_later = QPushButton(tr("common.later"))
        self.btn_later.setProperty("class", "secondary-btn")
        self.btn_later.clicked.connect(self.reject)
        self.buttons_layout.addWidget(self.btn_later)

        self.btn_download = QPushButton(tr("dialog.vlc_btn_download"))
        self.btn_download.setProperty("class", "primary-btn")
        self.btn_download.setStyleSheet("""
            QPushButton.primary-btn {
                background-color: #0284C7;
                color: #FFFFFF;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 6px;
                border: none;
            }
            QPushButton.primary-btn:hover {
                background-color: #0369A1;
            }
        """)
        self.btn_download.clicked.connect(self._start_download)
        self.buttons_layout.addWidget(self.btn_download)

        main_layout.addLayout(self.buttons_layout)

    def _start_download(self) -> None:
        """Démarre le téléchargement en arrière-plan."""
        self.btn_download.setVisible(False)
        self.btn_later.setText(tr("common.cancel"))
        self.btn_later.clicked.disconnect()
        self.btn_later.clicked.connect(self._cancel_download)

        self.progress_frame.setVisible(True)
        self.progress_bar.setValue(0)
        self.lbl_status.setText(tr("dialog.vlc_downloading"))

        self.worker = VlcDownloadWorker(parent=self)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, percent: int, message: str) -> None:
        self.progress_bar.setValue(percent)
        self.lbl_status.setText(message)

    def _on_finished(self, success: bool, message: str) -> None:
        if success:
            self.lbl_status.setText(f"✅  {tr('dialog.vlc_success')}")
            self.progress_bar.setValue(100)
            self.btn_later.setVisible(False)

            # Recharger le moteur VLC à chaud
            if self.player_service:
                self.player_service.reload_vlc()

            # Fermeture automatique fluide après 1 seconde
            QTimer.singleShot(1200, self.accept)
        else:
            self.lbl_status.setText(f"❌  {message}")
            self.btn_later.setText("Fermer")
            self.btn_later.clicked.disconnect()
            self.btn_later.clicked.connect(self.reject)

    def _cancel_download(self) -> None:
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait(1500)
        self.reject()

    def closeEvent(self, event) -> None:
        self._cancel_download()
        super().closeEvent(event)
