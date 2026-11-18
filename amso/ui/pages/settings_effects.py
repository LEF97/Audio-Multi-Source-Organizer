"""Page Paramètres > Effets (mixin de MainWindow)."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from amso.core.config import VISUAL_EFFECT_IDS, get_config_manager
from amso.core.i18n import tr
from amso.ui.styles import (
    COLOR_BG_CARD,
    COLOR_TEXT,
    COLOR_TEXT_BRIGHT,
    COLOR_TEXT_DIM,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_SOFT,
    effects_combo_qss,
    tree_action_button_qss,
)
from amso.ui.widgets.effects_combo import EFFECT_CATALOG
from amso.ui.widgets.page_header import build_page_top_bar

if TYPE_CHECKING:
    _MixinBase = QWidget
else:
    _MixinBase = object

_RANDOM_INTERVAL_ITEMS: tuple[tuple[str, str], ...] = (
    ("track", "settings.effects_random_track"),
    ("15", "settings.effects_random_15s"),
    ("30", "settings.effects_random_30s"),
    ("60", "settings.effects_random_1m"),
    ("120", "settings.effects_random_2m"),
    ("300", "settings.effects_random_5m"),
)


class SettingsEffectsPageMixin(_MixinBase):
    """Page de configuration des effets visuels disponibles et du mode aléatoire."""

    if TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any: ...

    def _create_settings_effects_page(self) -> QWidget:
        """Construit la page Paramètres > Effets."""
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # En-tête
        top_bar, self.lbl_settings_effects_page_title, self.btn_settings_effects_help = build_page_top_bar(
            tr("settings.page_effects_title"),
            "settings.effects_help_title",
            "settings.effects_help_body",
        )
        main_layout.addWidget(top_bar, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        content_layout.addWidget(self._build_card_effects_table())
        content_layout.addWidget(self._build_card_effects_random())
        content_layout.addStretch(1)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)
        return container

    def _build_card_effects_table(self) -> QFrame:
        """Carte contenant le tableau 3 colonnes des effets (Description / Lecteur / Blind test)."""
        cfg = get_config_manager()
        enabled_player = set(cfg.get_enabled_effects("player"))
        enabled_bt = set(cfg.get_enabled_effects("blind_test"))

        card = QFrame()
        card.setProperty("class", "dashboard-card")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        header_row = QHBoxLayout()
        header_row.setSpacing(12)
        self.lbl_card_effects_table_title = QLabel(tr("settings.effects_table_title"))
        self.lbl_card_effects_table_title.setStyleSheet(
            f"color: {COLOR_TEXT_BRIGHT}; font-size: 14px; font-weight: 700;"
        )
        self.lbl_card_effects_table_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        header_row.addWidget(self.lbl_card_effects_table_title)
        header_row.addStretch()

        self.btn_effects_check_all = QPushButton(tr("settings.effects_btn_check_all"))
        self.btn_effects_check_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_effects_check_all.setStyleSheet(tree_action_button_qss())
        self.btn_effects_check_all.clicked.connect(self._on_effects_check_all_clicked)
        header_row.addWidget(self.btn_effects_check_all)
        layout.addLayout(header_row)

        self.lbl_card_effects_table_desc = QLabel(tr("settings.effects_table_desc"))
        self.lbl_card_effects_table_desc.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        self.lbl_card_effects_table_desc.setWordWrap(True)
        self.lbl_card_effects_table_desc.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.lbl_card_effects_table_desc)

        table = QTableWidget(len(EFFECT_CATALOG), 3)
        self.table_effects_settings = table
        table.setHorizontalHeaderLabels(
            [
                tr("settings.effects_col_effect"),
                tr("settings.effects_col_player"),
                tr("settings.effects_col_blind_test"),
            ]
        )
        table.verticalHeader().setVisible(False)
        table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: #161922;
                alternate-background-color: #1B1F2A;
                border: 1px solid #2A303E;
                border-radius: 8px;
                color: {COLOR_TEXT_SOFT};
            }}
            QHeaderView::section {{
                background-color: {COLOR_BG_CARD};
                color: {COLOR_TEXT};
                font-size: 12.5px;
                font-weight: 700;
                padding: 8px 12px;
                border: none;
                border-bottom: 1px solid #2A303E;
            }}
            QTableWidget::item {{
                border-bottom: 1px solid #222734;
            }}
        """)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(1, 110)
        table.setColumnWidth(2, 120)

        self._effect_row_labels: dict[str, tuple[QLabel, QLabel]] = {}
        self._effect_checks_player: dict[str, QCheckBox] = {}
        self._effect_checks_blind_test: dict[str, QCheckBox] = {}

        row_height = 58
        for row, (eff_id, emoji, title_key, hint_key) in enumerate(EFFECT_CATALOG):
            table.setRowHeight(row, row_height)

            desc_widget = QWidget()
            desc_widget.setStyleSheet("background: transparent;")
            desc_layout = QVBoxLayout(desc_widget)
            desc_layout.setContentsMargins(12, 6, 12, 6)
            desc_layout.setSpacing(2)

            lbl_title = QLabel(f"{emoji}  {tr(title_key)}")
            lbl_title.setStyleSheet(
                f"color: {COLOR_TEXT_BRIGHT}; font-size: 13px; font-weight: 600; background: transparent;"
            )
            lbl_hint = QLabel(tr(hint_key))
            lbl_hint.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 11.5px; background: transparent;")
            lbl_hint.setWordWrap(True)
            desc_layout.addWidget(lbl_title)
            desc_layout.addWidget(lbl_hint)
            table.setCellWidget(row, 0, desc_widget)
            self._effect_row_labels[eff_id] = (lbl_title, lbl_hint)

            chk_player = self._make_centered_effect_checkbox(eff_id in enabled_player)
            chk_player.toggled.connect(partial(self._on_effect_availability_toggled, eff_id, "player"))
            table.setCellWidget(row, 1, self._wrap_centered_widget(chk_player))
            self._effect_checks_player[eff_id] = chk_player

            chk_bt = self._make_centered_effect_checkbox(eff_id in enabled_bt)
            chk_bt.toggled.connect(partial(self._on_effect_availability_toggled, eff_id, "blind_test"))
            table.setCellWidget(row, 2, self._wrap_centered_widget(chk_bt))
            self._effect_checks_blind_test[eff_id] = chk_bt

        header_h = table.horizontalHeader().sizeHint().height() or 36
        table.setFixedHeight(header_h + row_height * len(EFFECT_CATALOG) + 4)
        layout.addWidget(table)
        return card

    @staticmethod
    def _make_centered_effect_checkbox(checked: bool) -> QCheckBox:
        chk = QCheckBox()
        chk.setChecked(checked)
        chk.setCursor(Qt.CursorShape.PointingHandCursor)
        chk.setStyleSheet("background: transparent;")
        return chk

    @staticmethod
    def _wrap_centered_widget(widget: QWidget) -> QWidget:
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        box = QHBoxLayout(wrapper)
        box.setContentsMargins(0, 0, 0, 0)
        box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.addWidget(widget)
        return wrapper

    def _build_card_effects_random(self) -> QFrame:
        """Carte de configuration de la fréquence du mode aléatoire."""
        cfg = get_config_manager()
        card = QFrame()
        card.setProperty("class", "dashboard-card")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        self.lbl_card_effects_random_title = QLabel(f"🎲  {tr('settings.effects_random_title')}")
        self.lbl_card_effects_random_title.setStyleSheet(
            f"color: {COLOR_TEXT_BRIGHT}; font-size: 14px; font-weight: 700;"
        )
        layout.addWidget(self.lbl_card_effects_random_title)

        self.lbl_card_effects_random_desc = QLabel(tr("settings.effects_random_desc"))
        self.lbl_card_effects_random_desc.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        self.lbl_card_effects_random_desc.setWordWrap(True)
        layout.addWidget(self.lbl_card_effects_random_desc)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(10)

        self.lbl_effects_random_player = QLabel(tr("settings.effects_random_player_label"))
        self.lbl_effects_random_player.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 13px; font-weight: 500;")
        grid.addWidget(self.lbl_effects_random_player, 0, 0)

        self.combo_effects_random_player = self._make_random_interval_combo(
            cfg.get_visual_effect_random_interval("player"),
            "player",
        )
        grid.addWidget(self.combo_effects_random_player, 0, 1)

        self.lbl_effects_random_blind_test = QLabel(tr("settings.effects_random_blind_test_label"))
        self.lbl_effects_random_blind_test.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 13px; font-weight: 500;")
        grid.addWidget(self.lbl_effects_random_blind_test, 1, 0)

        self.combo_effects_random_blind_test = self._make_random_interval_combo(
            cfg.get_visual_effect_random_interval("blind_test"),
            "blind_test",
        )
        grid.addWidget(self.combo_effects_random_blind_test, 1, 1)

        grid.setColumnStretch(2, 1)
        layout.addLayout(grid)
        return card

    def _make_random_interval_combo(self, current_val: str, context: str) -> QComboBox:
        combo = QComboBox()
        combo.setCursor(Qt.CursorShape.PointingHandCursor)
        combo.setFixedWidth(240)
        combo.setStyleSheet(effects_combo_qss())
        self._populate_random_interval_combo(combo, current_val)
        combo.currentIndexChanged.connect(partial(self._on_random_interval_changed, context))
        return combo

    @staticmethod
    def _populate_random_interval_combo(combo: QComboBox, current_val: str) -> None:
        combo.blockSignals(True)
        combo.clear()
        target_idx = 0
        for idx, (val, key) in enumerate(_RANDOM_INTERVAL_ITEMS):
            combo.addItem(tr(key), val)
            if val == current_val:
                target_idx = idx
        combo.setCurrentIndex(target_idx)
        combo.blockSignals(False)

    def _on_effect_availability_toggled(self, _effect_id: str, context: str, _checked: bool) -> None:
        """Persiste les effets activés pour le Lecteur ou le Blind Test et rafraîchit la vue."""
        checks = self._effect_checks_blind_test if context == "blind_test" else self._effect_checks_player
        selected = [eff_id for eff_id, chk in checks.items() if chk.isChecked()]
        if not selected:
            # Si tout est décoché, on recoche automatiquement "Désactivé"
            chk_none = checks["none"]
            chk_none.blockSignals(True)
            chk_none.setChecked(True)
            chk_none.blockSignals(False)
            selected = ["none"]

        get_config_manager().set_enabled_effects(context, selected)
        target_page = getattr(self, "page_blind_test" if context == "blind_test" else "page_player", None)
        if target_page and hasattr(target_page, "refresh_available_effects"):
            target_page.refresh_available_effects()

    def _on_effects_check_all_clicked(self) -> None:
        """Coche tous les effets pour le Lecteur et le Blind Test."""
        all_ids = list(VISUAL_EFFECT_IDS)
        cfg = get_config_manager()
        for context, checks, page_attr in (
            ("player", self._effect_checks_player, "page_player"),
            ("blind_test", self._effect_checks_blind_test, "page_blind_test"),
        ):
            for chk in checks.values():
                chk.blockSignals(True)
                chk.setChecked(True)
                chk.blockSignals(False)
            cfg.set_enabled_effects(context, all_ids)
            target_page = getattr(self, page_attr, None)
            if target_page and hasattr(target_page, "refresh_available_effects"):
                target_page.refresh_available_effects()

    def _on_random_interval_changed(self, context: str, _index: int = 0) -> None:
        """Sauvegarde la fréquence du mode Random pour un contexte et resynchronise son timer."""
        combo = self.combo_effects_random_blind_test if context == "blind_test" else self.combo_effects_random_player
        val = combo.currentData()
        if not val:
            return
        get_config_manager().set_visual_effect_random_interval(str(val), context=context)
        page = getattr(self, "page_blind_test" if context == "blind_test" else "page_player", None)
        if page and hasattr(page, "_sync_random_timer"):
            page._sync_random_timer()

    def _retranslate_settings_effects_page(self) -> None:
        """Met à jour les traductions de la page Paramètres > Effets."""
        if not hasattr(self, "lbl_settings_effects_page_title"):
            return
        self.lbl_settings_effects_page_title.setText(tr("settings.page_effects_title"))
        self.lbl_card_effects_table_title.setText(tr("settings.effects_table_title"))
        self.btn_effects_check_all.setText(tr("settings.effects_btn_check_all"))
        self.lbl_card_effects_table_desc.setText(tr("settings.effects_table_desc"))
        self.table_effects_settings.setHorizontalHeaderLabels(
            [
                tr("settings.effects_col_effect"),
                tr("settings.effects_col_player"),
                tr("settings.effects_col_blind_test"),
            ]
        )
        for eff_id, emoji, title_key, hint_key in EFFECT_CATALOG:
            labels = self._effect_row_labels.get(eff_id)
            if labels:
                lbl_title, lbl_hint = labels
                lbl_title.setText(f"{emoji}  {tr(title_key)}")
                lbl_hint.setText(tr(hint_key))

        self.lbl_card_effects_random_title.setText(f"🎲  {tr('settings.effects_random_title')}")
        self.lbl_card_effects_random_desc.setText(tr("settings.effects_random_desc"))
        self.lbl_effects_random_player.setText(tr("settings.effects_random_player_label"))
        self.lbl_effects_random_blind_test.setText(tr("settings.effects_random_blind_test_label"))
        cfg = get_config_manager()
        for combo, ctx in (
            (self.combo_effects_random_player, "player"),
            (self.combo_effects_random_blind_test, "blind_test"),
        ):
            current_val = combo.currentData() or cfg.get_visual_effect_random_interval(ctx)
            self._populate_random_interval_combo(combo, str(current_val))
