"""Page Paramètres > Général (mixin de MainWindow)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from amso.core.config import get_config_path
from amso.core.i18n import SUPPORTED_LANGUAGES, tr

logger = logging.getLogger(__name__)


class SettingsGeneralPageMixin:
    """Page Paramètres > Général (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de MainWindow sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    def _create_settings_page(self) -> QWidget:
        """Page des Paramètres Généraux (contenant le choix de langue)."""
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

        self.lbl_settings_title = QLabel(tr("settings.page_title"))
        self.lbl_settings_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        top_layout.addWidget(self.lbl_settings_title)
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

        # 1. Carte Langue
        card_lang = QFrame()
        card_lang.setProperty("class", "dashboard-card")
        l_lang = QVBoxLayout(card_lang)
        l_lang.setContentsMargins(18, 16, 18, 16)
        l_lang.setSpacing(8)

        self.lbl_card_lang_title = QLabel(tr("settings.section_language"))
        self.lbl_card_lang_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        l_lang.addWidget(self.lbl_card_lang_title)

        self.lbl_card_lang_desc = QLabel(tr("settings.language_desc"))
        self.lbl_card_lang_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        l_lang.addWidget(self.lbl_card_lang_desc)

        self.combo_language = QComboBox()
        self.combo_language.setObjectName("langComboBox")
        self.combo_language.setMaximumWidth(280)

        lang_display = {
            "fr": "🇫🇷  Français",
            "en": "🇬🇧  English",
            "es": "🇪🇸  Español",
            "it": "🇮🇹  Italiano",
            "de": "🇩🇪  Deutsch",
        }
        for code, name in SUPPORTED_LANGUAGES.items():
            disp = lang_display.get(code, f"{code.upper()} - {name}")
            self.combo_language.addItem(disp, userData=code)

        cur_idx = self.combo_language.findData(self.i18n.current_language)
        if cur_idx >= 0:
            self.combo_language.setCurrentIndex(cur_idx)

        self.combo_language.currentIndexChanged.connect(self._on_language_combo_changed)
        l_lang.addWidget(self.combo_language)
        content_layout.addWidget(card_lang)

        # 2. Carte Emplacement des données
        card_storage = QFrame()
        card_storage.setProperty("class", "dashboard-card")
        l_storage = QVBoxLayout(card_storage)
        l_storage.setContentsMargins(18, 16, 18, 16)
        l_storage.setSpacing(8)

        self.lbl_card_storage_title = QLabel(tr("settings.section_storage"))
        self.lbl_card_storage_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        l_storage.addWidget(self.lbl_card_storage_title)

        cfg_p = str(get_config_path())
        db_p = str(self.db.db_path)

        self.lbl_config_path_val = QLabel(f"• <b>{tr('settings.config_file')}</b> <code>{cfg_p}</code>")
        self.lbl_config_path_val.setStyleSheet("color: #94A3B8; font-size: 12px;")
        l_storage.addWidget(self.lbl_config_path_val)

        self.lbl_db_path_val = QLabel(f"• <b>{tr('settings.db_file')}</b> <code>{db_p}</code>")
        self.lbl_db_path_val.setStyleSheet("color: #94A3B8; font-size: 12px;")
        l_storage.addWidget(self.lbl_db_path_val)

        self.btn_open_data_folder = QPushButton(tr("settings.btn_open_folder"))
        self.btn_open_data_folder.setProperty("class", "secondary-btn")
        self.btn_open_data_folder.setMaximumWidth(220)
        self.btn_open_data_folder.clicked.connect(self._on_open_data_folder)
        l_storage.addWidget(self.btn_open_data_folder)

        content_layout.addWidget(card_storage)
        content_layout.addStretch(1)

        # Alias de compatibilité pour tests existants
        self.btn_open_about_dialog = getattr(self, "btn_settings_about", None)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

        return container
