"""Page Paramètres > À propos (mixin de MainWindow)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
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
from amso.ui.theme import get_app_logo_pixmap
from amso.ui.views.visual_effects import VisualEffectWidget

if TYPE_CHECKING:
    from amso.services.player_service import PlayerService

logger = logging.getLogger(__name__)


class SettingsAboutPageMixin:
    """Page Paramètres > À propos (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Attributs / méthodes fournis par MainWindow (typage uniquement)
        player_service: PlayerService

        def _check_for_updates(self, manual: bool = False) -> None: ...
        def _open_latest_release_url(self) -> None: ...
        def _refresh_update_ui(self) -> None: ...

    def _create_settings_about_page(self) -> QWidget:
        """Page dédiée Paramètres > À propos d'AMSO."""
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # En-tête de page standardisé
        top_bar = QFrame()
        top_bar.setObjectName("topBarFrame")
        top_bar.setFixedHeight(50)
        top_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 12, 20, 12)

        self.lbl_settings_about_page_title = QLabel(tr("settings.about_page_title"))
        self.lbl_settings_about_page_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        top_layout.addWidget(self.lbl_settings_about_page_title)
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

        # 1. En-tête Identité AMSO & Version unifié (Logo à gauche + Colonne droite : Titre + Description + Rétro-bars sous le texte)
        top_card = QFrame()
        top_card.setFixedHeight(172)
        top_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        top_card.setStyleSheet("""
            QFrame#aboutTopCard {
                background-color: #15181E;
                border: 1px solid #282C37;
                border-radius: 18px;
            }
        """)
        top_card.setObjectName("aboutTopCard")

        top_layout = QHBoxLayout(top_card)
        top_layout.setContentsMargins(20, 16, 16, 16)
        top_layout.setSpacing(22)
        top_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Logo officiel AMSO (aligné tout en haut)
        lbl_logo = QLabel()
        icon_pm = get_app_logo_pixmap()
        if not icon_pm.isNull():
            lbl_logo.setPixmap(
                icon_pm.scaled(
                    132,
                    132,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            lbl_logo.setText("🎵")
            lbl_logo.setStyleSheet("font-size: 64px;")
        lbl_logo.setFixedSize(132, 132)
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        lbl_logo.setStyleSheet("background: transparent; border: none; padding: 0px; margin: 0px;")
        top_layout.addWidget(lbl_logo, 0, Qt.AlignmentFlag.AlignTop)

        # Colonne droite : Titre aligné en haut avec l'icône, puis description, puis barres en dessous
        right_col = QVBoxLayout()
        right_col.setContentsMargins(0, 0, 0, 0)
        right_col.setSpacing(6)
        right_col.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Ligne 1 : Nom complet + AMSO + Badge Version (aligné tout en haut du cadre)
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(10)
        title_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.lbl_about_app_name = QLabel(tr("dialog.about_app_name"))
        self.lbl_about_app_name.setStyleSheet(
            "color: #F8FAFC; font-size: 20px; font-weight: 800; letter-spacing: 0.5px; padding: 0px; margin: 0px;"
        )
        title_row.addWidget(self.lbl_about_app_name)

        acronym_lbl = QLabel("AMSO")
        acronym_lbl.setStyleSheet("color: #38BDF8; font-size: 14px; font-weight: 700; padding: 0px; margin: 0px;")
        title_row.addWidget(acronym_lbl)

        ver_badge = QLabel(f"v{__version__}")
        ver_badge.setStyleSheet("""
            background-color: #0369A1;
            color: #FFFFFF;
            padding: 2px 10px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 700;
        """)
        title_row.addWidget(ver_badge)
        title_row.addStretch()
        right_col.addLayout(title_row)

        # Ligne 2 : Description
        self.lbl_about_desc = QLabel(tr("dialog.about_description"))
        self.lbl_about_desc.setWordWrap(True)
        self.lbl_about_desc.setStyleSheet(
            "color: #CBD5E1; font-size: 13px; line-height: 1.45; padding: 0px; margin: 0px;"
        )
        right_col.addWidget(self.lbl_about_desc)

        # Ligne 3 : Barres de spectre rétro sous le texte (alignées à gauche avec le texte, collant au cadre à droite)
        self.about_visual_effect = VisualEffectWidget(
            VisualEffectWidget.EFFECT_BARS,
            parent=top_card,
        )
        self.about_visual_effect.set_demo_mode(False)
        self.about_visual_effect.set_bars_aligned_left(True)
        self.about_visual_effect.setFixedHeight(62)
        self.about_visual_effect.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.about_visual_effect.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.about_visual_effect.setStyleSheet("background: transparent; border: none;")

        # Synchronisation immédiate avec l'état actuel de lecture
        if self.player_service.is_playing:
            self.about_visual_effect.set_playback_state("playing")
        else:
            self.about_visual_effect.set_playback_state("stopped")
        self.about_visual_effect.update_audio_volume(
            self.player_service.volume,
            getattr(self.player_service, "is_muted", False),
        )
        if self.player_service.current_track:
            self.about_visual_effect.set_track(self.player_service.current_track)

        # Écoute réactive des événements de lecture audio
        self.player_service.state_changed.connect(self.about_visual_effect.set_playback_state)
        self.player_service.position_changed.connect(self.about_visual_effect.update_audio_time)
        self.player_service.track_changed.connect(self.about_visual_effect.set_track)
        self.player_service.volume_changed.connect(self.about_visual_effect.update_audio_volume)

        right_col.addWidget(self.about_visual_effect, 0, Qt.AlignmentFlag.AlignBottom)
        top_layout.addLayout(right_col, 1)

        content_layout.addWidget(top_card)

        # 2. Carte de vérification des mises à jour & statut
        card_update = QFrame()
        card_update.setProperty("class", "dashboard-card")
        update_row = QHBoxLayout(card_update)
        update_row.setContentsMargins(20, 14, 20, 14)
        update_row.setSpacing(14)
        update_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.btn_check_updates_about = QPushButton(tr("settings.btn_check_updates"))
        self.btn_check_updates_about.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_check_updates_about.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #E2E8F0;
                font-size: 12px;
                font-weight: 600;
                padding: 7px 16px;
                border: 1px solid #334155;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #334155;
                border-color: #475569;
                color: #FFFFFF;
            }
        """)
        self.btn_check_updates_about.clicked.connect(lambda: self._check_for_updates(manual=True))
        update_row.addWidget(self.btn_check_updates_about)

        self.lbl_update_status_about = QLabel("")
        self.lbl_update_status_about.setStyleSheet("color: #94A3B8; font-size: 12.5px; font-weight: 500;")
        update_row.addWidget(self.lbl_update_status_about)

        self.btn_update_download = QPushButton(tr("settings.btn_download_update"))
        self.btn_update_download.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_update_download.setStyleSheet("""
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 700;
                padding: 7px 14px;
                border: 1px solid #38BDF8;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #0369A1;
                border-color: #7DD3FC;
            }
        """)
        self.btn_update_download.setVisible(False)
        self.btn_update_download.clicked.connect(self._open_latest_release_url)
        update_row.addWidget(self.btn_update_download)

        update_row.addStretch()
        content_layout.addWidget(card_update)

        # 3. Carte Soutenir le projet (Faire un don)
        card_support = QFrame()
        card_support.setProperty("class", "dashboard-card")
        l_support = QVBoxLayout(card_support)
        l_support.setContentsMargins(22, 18, 22, 18)
        l_support.setSpacing(14)

        # Sous-titre Soutien
        self.lbl_about_support_title = QLabel("💖  " + tr("dialog.about_support_title"))
        self.lbl_about_support_title.setStyleSheet("color: #F1F5F9; font-size: 14px; font-weight: 700;")
        l_support.addWidget(self.lbl_about_support_title)

        # Ligne de dons : Ko-fi et GitHub Sponsors
        donate_row = QHBoxLayout()
        donate_row.setSpacing(12)

        # Bouton Ko-fi
        self.btn_about_kofi = QPushButton(tr("dialog.about_btn_kofi"))
        self.btn_about_kofi.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_about_kofi.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF5E5B, stop:1 #D9413E);
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 700;
                padding: 10px 22px;
                border: 1px solid #FFA4A2;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF7673, stop:1 #FF5E5B);
                border-color: #FFFFFF;
            }
        """)
        self.btn_about_kofi.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(URL_KO_FI)))
        donate_row.addWidget(self.btn_about_kofi)

        # Bouton GitHub Sponsors
        self.btn_about_sponsors = QPushButton(tr("dialog.about_btn_sponsors"))
        self.btn_about_sponsors.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_about_sponsors.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #EA4AAA, stop:1 #C5288B);
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 700;
                padding: 10px 22px;
                border: 1px solid #F9A8D4;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F062BA, stop:1 #EA4AAA);
                border-color: #FFFFFF;
            }
        """)
        self.btn_about_sponsors.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(URL_GITHUB_SPONSORS)))
        donate_row.addWidget(self.btn_about_sponsors)

        donate_row.addStretch()
        l_support.addLayout(donate_row)

        # Alias de compatibilité
        self.btn_about_donate = self.btn_about_kofi
        content_layout.addWidget(card_support)

        # 4. Carte Pages officielles (séparée par l'espacement standard, sans ligne horizontale)
        card_official = QFrame()
        card_official.setProperty("class", "dashboard-card")
        l_official = QVBoxLayout(card_official)
        l_official.setContentsMargins(22, 18, 22, 18)
        l_official.setSpacing(14)

        # Sous-titre Pages officielles
        self.lbl_about_official_title = QLabel("🌐  " + tr("dialog.about_official_pages_title"))
        self.lbl_about_official_title.setStyleSheet("color: #F1F5F9; font-size: 14px; font-weight: 700;")
        l_official.addWidget(self.lbl_about_official_title)

        # Ligne de pages officielles : Dépôt GitHub et Page Itch.io
        official_row = QHBoxLayout()
        official_row.setSpacing(12)

        self.btn_about_github = QPushButton(tr("dialog.about_btn_github"))
        self.btn_about_github.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_about_github.setProperty("class", "secondary-btn")
        self.btn_about_github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(URL_GITHUB_REPO)))
        official_row.addWidget(self.btn_about_github)

        self.btn_about_itch = QPushButton(tr("dialog.about_btn_itch"))
        self.btn_about_itch.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_about_itch.setProperty("class", "secondary-btn")
        self.btn_about_itch.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(URL_ITCH_IO)))
        official_row.addWidget(self.btn_about_itch)

        official_row.addStretch()
        l_official.addLayout(official_row)
        content_layout.addWidget(card_official)

        # 5. Carte Crédits & Technologies Open Source (placée après Pages officielles)
        card_credits = QFrame()
        card_credits.setProperty("class", "dashboard-card")
        l_credits = QVBoxLayout(card_credits)
        l_credits.setContentsMargins(22, 18, 22, 18)
        l_credits.setSpacing(10)

        self.lbl_about_credits_title = QLabel("👍  " + tr("dialog.about_credits_title"))
        self.lbl_about_credits_title.setStyleSheet("color: #F1F5F9; font-size: 14px; font-weight: 700;")
        l_credits.addWidget(self.lbl_about_credits_title)

        self.lbl_about_credits_tech = QLabel(tr("dialog.about_credits_tech"))
        self.lbl_about_credits_tech.setWordWrap(True)
        self.lbl_about_credits_tech.setStyleSheet("color: #94A3B8; font-size: 13px; line-height: 1.4;")
        l_credits.addWidget(self.lbl_about_credits_tech)

        self.lbl_about_license = QLabel(tr("dialog.about_license"))
        self.lbl_about_license.setStyleSheet("color: #64748B; font-size: 11px; font-style: italic; margin-top: 4px;")
        l_credits.addWidget(self.lbl_about_license)

        content_layout.addWidget(card_credits)
        content_layout.addStretch(1)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

        self._refresh_update_ui()
        return container
