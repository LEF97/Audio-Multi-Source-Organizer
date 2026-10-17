"""Boîte de dialogue « À propos » d'AMSO (Audio Multi-Source Organizer)."""

from __future__ import annotations

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from amso import __version__
from amso.core.constants import (
    URL_GITHUB_REPO,
    URL_GITHUB_SPONSORS,
    URL_ITCH_IO,
    URL_KO_FI,
)
from amso.core.i18n import tr
from amso.ui.theme import DARK_THEME_QSS, get_app_logo_pixmap


class AboutDialog(QDialog):
    """Boîte de dialogue présentant le projet AMSO, sa version, ses crédits et ses liens de soutien."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle(tr("dialog.about_title"))
        self.setMinimumWidth(560)
        self.setModal(True)
        self.setStyleSheet(DARK_THEME_QSS)

        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 28, 28, 24)
        main_layout.setSpacing(20)

        # ---------------------------------------------------------------------
        # 1. En-tête : Icône officielle, Titre & Badge de version
        # ---------------------------------------------------------------------
        header_layout = QHBoxLayout()
        header_layout.setSpacing(18)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        icon_pm = get_app_logo_pixmap()
        icon_lbl = QLabel()
        if not icon_pm.isNull():
            icon_lbl.setPixmap(
                icon_pm.scaled(
                    64,
                    64,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            icon_lbl.setText("🎵")
            icon_lbl.setStyleSheet("font-size: 40px;")

        icon_lbl.setStyleSheet("""
            padding: 8px;
            background-color: #1A1D24;
            border: 1px solid #282C37;
            border-radius: 14px;
        """)
        header_layout.addWidget(icon_lbl)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)

        app_name_lbl = QLabel(tr("dialog.about_app_name"))
        app_name_lbl.setStyleSheet("color: #F8FAFC; font-size: 19px; font-weight: 800; letter-spacing: 0.5px;")
        title_layout.addWidget(app_name_lbl)

        sub_layout = QHBoxLayout()
        sub_layout.setSpacing(8)

        acronym_lbl = QLabel("AMSO")
        acronym_lbl.setStyleSheet("color: #38BDF8; font-size: 14px; font-weight: 700;")
        sub_layout.addWidget(acronym_lbl)

        ver_badge = QLabel(f"v{__version__}")
        ver_badge.setStyleSheet("""
            background-color: #0369A1;
            color: #FFFFFF;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 700;
        """)
        sub_layout.addWidget(ver_badge)
        sub_layout.addStretch()

        title_layout.addLayout(sub_layout)
        header_layout.addLayout(title_layout, 1)

        main_layout.addLayout(header_layout)

        # ---------------------------------------------------------------------
        # 2. Description concise du projet
        # ---------------------------------------------------------------------
        desc_lbl = QLabel(tr("dialog.about_description"))
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #CBD5E1; font-size: 13px; line-height: 1.4;")
        main_layout.addWidget(desc_lbl)

        # ---------------------------------------------------------------------
        # 3. Carte des Crédits & Technologies Open Source
        # ---------------------------------------------------------------------
        credits_card = QFrame()
        credits_card.setStyleSheet("""
            QFrame {
                background-color: #161922;
                border: 1px solid #282C37;
                border-radius: 12px;
                padding: 14px;
            }
        """)
        credits_layout = QVBoxLayout(credits_card)
        credits_layout.setContentsMargins(14, 12, 14, 12)
        credits_layout.setSpacing(8)

        credits_title = QLabel(tr("dialog.about_credits_title"))
        credits_title.setStyleSheet("color: #F1F5F9; font-size: 13px; font-weight: 700;")
        credits_layout.addWidget(credits_title)

        credits_desc = QLabel(tr("dialog.about_credits_tech"))
        credits_desc.setStyleSheet("color: #94A3B8; font-size: 12px; line-height: 1.4;")
        credits_layout.addWidget(credits_desc)

        license_lbl = QLabel(tr("dialog.about_license"))
        license_lbl.setStyleSheet("color: #64748B; font-size: 11px; font-style: italic; margin-top: 4px;")
        credits_layout.addWidget(license_lbl)

        main_layout.addWidget(credits_card)

        # ---------------------------------------------------------------------
        # 4. Liens externes & Boutons d'action (GitHub, Itch.io, Ko-fi)
        # ---------------------------------------------------------------------
        actions_card = QFrame()
        actions_card.setStyleSheet("""
            QFrame {
                background-color: #12141C;
                border: 1px solid #1E293B;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        actions_layout = QVBoxLayout(actions_card)
        actions_layout.setContentsMargins(12, 10, 12, 10)
        actions_layout.setSpacing(10)

        # Bouton principal Don / Soutien (Mise en valeur)
        self.btn_donate = QPushButton(tr("dialog.about_btn_donate"))
        self.btn_donate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_donate.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E11D48, stop:1 #BE123C);
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 700;
                padding: 10px 18px;
                border: 1px solid #F43F5E;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F43F5E, stop:1 #E11D48);
                border: 1px solid #FDA4AF;
            }
        """)
        self.btn_donate.clicked.connect(lambda: self._open_url(URL_KO_FI))
        actions_layout.addWidget(self.btn_donate)

        # Ligne de boutons secondaires : GitHub, Itch.io, GitHub Sponsors
        sub_links_layout = QHBoxLayout()
        sub_links_layout.setSpacing(10)

        self.btn_github = QPushButton(tr("dialog.about_btn_github"))
        self.btn_github.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_github.setProperty("class", "secondary-btn")
        self.btn_github.clicked.connect(lambda: self._open_url(URL_GITHUB_REPO))
        sub_links_layout.addWidget(self.btn_github)

        self.btn_itch = QPushButton(tr("dialog.about_btn_itch"))
        self.btn_itch.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_itch.setProperty("class", "secondary-btn")
        self.btn_itch.clicked.connect(lambda: self._open_url(URL_ITCH_IO))
        sub_links_layout.addWidget(self.btn_itch)

        self.btn_sponsors = QPushButton(tr("dialog.about_btn_sponsors"))
        self.btn_sponsors.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sponsors.setProperty("class", "secondary-btn")
        self.btn_sponsors.clicked.connect(lambda: self._open_url(URL_GITHUB_SPONSORS))
        sub_links_layout.addWidget(self.btn_sponsors)

        actions_layout.addLayout(sub_links_layout)
        main_layout.addWidget(actions_card)

        # ---------------------------------------------------------------------
        # 5. Pied de page : Bouton Fermer
        # ---------------------------------------------------------------------
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()

        self.btn_close = QPushButton(tr("dialog.about_btn_close"))
        self.btn_close.setProperty("class", "secondary-btn")
        self.btn_close.setMinimumWidth(100)
        self.btn_close.clicked.connect(self.accept)
        footer_layout.addWidget(self.btn_close)

        main_layout.addLayout(footer_layout)

    def _open_url(self, url: str) -> None:
        """Ouvre une URL externe dans le navigateur par défaut du système."""
        QDesktopServices.openUrl(QUrl(url))
