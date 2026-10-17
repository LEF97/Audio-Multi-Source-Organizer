"""Bannière discrète et non-bloquante de notification de mise à jour et soutien."""

from __future__ import annotations

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from amso.core.constants import URL_ITCH_IO, URL_KO_FI
from amso.core.i18n import tr


class UpdateBannerWidget(QFrame):
    """Bannière d'information non-bloquante affichée en bas de fenêtre lors d'une nouvelle version."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("updateBannerWidget")
        self.latest_version: str = ""
        self.release_url: str = ""

        # Cachée par défaut tant qu'aucune nouvelle version n'est trouvée
        self.setVisible(False)

        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setStyleSheet("""
            QFrame#updateBannerWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0B1E38, stop:0.5 #0F2D54, stop:1 #0B1E38);
                border-top: 1px solid #0284C7;
                border-bottom: 1px solid #1E293B;
                padding: 4px 12px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 6, 16, 6)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Icône animée/lumineuse
        self.icon_label = QLabel("✨")
        self.icon_label.setStyleSheet("font-size: 20px; background: transparent;")
        layout.addWidget(self.icon_label)

        # Message informatif
        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("""
            color: #F1F5F9;
            font-size: 12px;
            background: transparent;
        """)
        layout.addWidget(self.text_label, 1)

        # Groupe de boutons d'action
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        # Bouton Télécharger
        self.btn_download = QPushButton()
        self.btn_download.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_download.setStyleSheet("""
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                font-size: 11px;
                font-weight: 700;
                padding: 5px 12px;
                border: 1px solid #38BDF8;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #0369A1;
                border: 1px solid #7DD3FC;
            }
        """)
        self.btn_download.clicked.connect(self._on_download_clicked)
        buttons_layout.addWidget(self.btn_download)

        # Bouton Soutenir / Don
        self.btn_support = QPushButton()
        self.btn_support.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_support.setStyleSheet("""
            QPushButton {
                background-color: #9F1239;
                color: #FFFFFF;
                font-size: 11px;
                font-weight: 700;
                padding: 5px 12px;
                border: 1px solid #F43F5E;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #BE123C;
                border: 1px solid #FDA4AF;
            }
        """)
        self.btn_support.clicked.connect(self._on_support_clicked)
        buttons_layout.addWidget(self.btn_support)

        # Bouton Fermer (Discret)
        self.btn_dismiss = QPushButton("✕")
        self.btn_dismiss.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_dismiss.setToolTip(tr("update.btn_dismiss"))
        self.btn_dismiss.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #94A3B8;
                font-size: 13px;
                font-weight: 700;
                padding: 4px 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                color: #FFFFFF;
                background-color: #334155;
            }
        """)
        self.btn_dismiss.clicked.connect(self.hide)
        buttons_layout.addWidget(self.btn_dismiss)

        layout.addLayout(buttons_layout)

    def show_update(self, latest_version: str, release_url: str) -> None:
        """Affiche la bannière avec les informations de la dernière version."""
        self.latest_version = latest_version
        self.release_url = release_url
        self.retranslate_ui()
        self.setVisible(True)

    def retranslate_ui(self) -> None:
        """Met à jour les libellés de la bannière selon la langue active."""
        if self.latest_version:
            self.text_label.setText(tr("update.banner_text").format(version=self.latest_version))
        self.btn_download.setText(tr("update.btn_download"))
        self.btn_support.setText(tr("update.btn_support"))
        self.btn_dismiss.setToolTip(tr("update.btn_dismiss"))

    def _on_download_clicked(self) -> None:
        url = self.release_url if self.release_url else URL_ITCH_IO
        QDesktopServices.openUrl(QUrl(url))

    def _on_support_clicked(self) -> None:
        QDesktopServices.openUrl(QUrl(URL_KO_FI))
