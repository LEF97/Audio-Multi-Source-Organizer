"""Carte de configuration des transitions de pochettes pour Paramètres > Lecteur."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QButtonGroup, QFrame, QLabel, QRadioButton, QVBoxLayout, QWidget

from amso.core.config import COVER_TRANSITION_MODES, get_config_manager
from amso.core.i18n import tr
from amso.ui.styles import settings_radio_qss

if TYPE_CHECKING:
    _MixinBase = QWidget
else:
    _MixinBase = object


class SettingsPlayerCoverMixin(_MixinBase):
    """Construction et gestion de la carte 'Transitions des pochettes'."""

    if TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any: ...

    def _build_card_cover_transitions(self) -> QFrame:
        """Construit la carte de sélection de l'animation lors d'un changement de pochette."""
        cfg = get_config_manager()
        radio_qss = settings_radio_qss()

        card = QFrame()
        card.setProperty("class", "dashboard-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        self.lbl_card_cover_trans_title = QLabel(tr("settings.cover_transition_title"))
        self.lbl_card_cover_trans_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        layout.addWidget(self.lbl_card_cover_trans_title)

        self.lbl_card_cover_trans_desc = QLabel(tr("settings.cover_transition_desc"))
        self.lbl_card_cover_trans_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        self.lbl_card_cover_trans_desc.setWordWrap(True)
        layout.addWidget(self.lbl_card_cover_trans_desc)

        self.cover_transition_group = QButtonGroup(cast("QObject", self))
        self._cover_trans_radios: dict[str, tuple[QRadioButton, QLabel]] = {}

        cur_mode = cfg.get_cover_transition()
        for mode in COVER_TRANSITION_MODES:
            box = QVBoxLayout()
            box.setSpacing(3)

            radio = QRadioButton(tr(f"settings.cover_transition_{mode}"))
            radio.setStyleSheet(radio_qss)
            self.cover_transition_group.addButton(radio)
            box.addWidget(radio)

            hint = QLabel(tr(f"settings.cover_transition_{mode}_hint"))
            hint.setStyleSheet("color: #64748B; font-size: 12px; margin-left: 26px;")
            hint.setWordWrap(True)
            box.addWidget(hint)

            layout.addLayout(box)
            self._cover_trans_radios[mode] = (radio, hint)

            if mode == cur_mode:
                radio.setChecked(True)
            radio.toggled.connect(self._on_cover_transition_changed)

        return card

    def _on_cover_transition_changed(self) -> None:
        """Enregistre immédiatement le mode de transition choisi."""
        cfg = get_config_manager()
        for mode, (radio, _hint) in self._cover_trans_radios.items():
            if radio.isChecked():
                cfg.set_cover_transition(mode)
                return

    def _retranslate_cover_transition_card(self) -> None:
        """Met à jour les libellés de la carte lors d'un changement de langue."""
        if not hasattr(self, "lbl_card_cover_trans_title"):
            return
        self.lbl_card_cover_trans_title.setText(tr("settings.cover_transition_title"))
        self.lbl_card_cover_trans_desc.setText(tr("settings.cover_transition_desc"))
        for mode, (radio, hint) in self._cover_trans_radios.items():
            radio.setText(tr(f"settings.cover_transition_{mode}"))
            hint.setText(tr(f"settings.cover_transition_{mode}_hint"))
