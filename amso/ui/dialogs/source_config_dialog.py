"""Boîte de dialogue moderne de configuration et modification d'une source audio."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from amso.core.database import SourceRecord
from amso.core.i18n import tr
from amso.ui.theme import DARK_THEME_QSS


class SourceConfigData(TypedDict):
    name: str
    path_or_uri: str
    sync_mode: str
    sync_interval_minutes: int
    sync_interval_seconds: int


class SourceConfigDialog(QDialog):
    """Dialogue de paramétrage du nom, de l'emplacement et de la stratégie de synchronisation d'une source."""

    def __init__(
        self,
        source: SourceRecord | None = None,
        initial_path: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.source = source
        self.is_edit_mode = source is not None

        title_key = "dialog.source_config_edit_title" if self.is_edit_mode else "dialog.source_config_add_title"
        self.setWindowTitle(tr(title_key))
        self.setMinimumWidth(500)
        self.setModal(True)
        self.setStyleSheet(DARK_THEME_QSS)

        self._init_ui(initial_path)

    def _init_ui(self, initial_path: str | None) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # En-tête du dialogue
        header_lbl = QLabel(
            tr("dialog.source_config_edit_desc") if self.is_edit_mode else tr("dialog.source_config_add_desc")
        )
        header_lbl.setStyleSheet("color: #94A3B8; font-size: 13px; margin-bottom: 2px;")
        header_lbl.setWordWrap(True)
        main_layout.addWidget(header_lbl)

        # Formulaire
        form_frame = QFrame()
        form_frame.setObjectName("sourceConfigFormFrame")
        form_frame.setStyleSheet(
            "QFrame#sourceConfigFormFrame { background-color: #1A1D24; border: 1px solid #282C37; border-radius: 8px; }"
        )
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(18, 18, 18, 18)
        form_layout.setSpacing(14)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # 1. Nom de la source
        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText(tr("dialog.source_name_placeholder"))
        self.edit_name.setFixedHeight(34)
        default_name = ""
        if self.source:
            default_name = self.source.name
        elif initial_path:
            default_name = Path(initial_path).name or initial_path
        self.edit_name.setText(default_name)

        self.edit_name.returnPressed.connect(self._on_save)

        lbl_name = QLabel(tr("dialog.source_name"))
        lbl_name.setStyleSheet("color: #F8FAFC; font-weight: 600; font-size: 13px;")
        form_layout.addRow(lbl_name, self.edit_name)

        # 2. Emplacement du dossier
        path_layout = QHBoxLayout()
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(8)

        self.edit_path = QLineEdit()
        self.edit_path.setFixedHeight(34)
        self.edit_path.returnPressed.connect(self._on_save)
        if self.source:
            self.edit_path.setText(self.source.path_or_uri)
            self.edit_path.setReadOnly(True)
            self.edit_path.setStyleSheet("color: #94A3B8; background-color: #121418; border: 1px solid #282C37;")
        elif initial_path:
            self.edit_path.setText(initial_path)

        path_layout.addWidget(self.edit_path)

        if not self.is_edit_mode:
            self.btn_browse = QPushButton(tr("dialog.btn_browse"))
            self.btn_browse.setProperty("class", "secondary-btn")
            self.btn_browse.setFixedHeight(34)
            self.btn_browse.setAutoDefault(False)
            self.btn_browse.clicked.connect(self._on_browse_folder)
            path_layout.addWidget(self.btn_browse)

        lbl_path = QLabel(tr("dialog.source_path"))
        lbl_path.setStyleSheet("color: #F8FAFC; font-weight: 600; font-size: 13px;")
        form_layout.addRow(lbl_path, path_layout)

        # 3. Stratégie de synchronisation
        self.combo_sync_mode = QComboBox()
        self.combo_sync_mode.setFixedHeight(34)
        self.combo_sync_mode.addItem("✋  " + tr("sync_mode.manual"), userData="manual")
        self.combo_sync_mode.addItem("🚀  " + tr("sync_mode.startup"), userData="startup")
        self.combo_sync_mode.addItem("⏱️  " + tr("sync_mode.interval"), userData="interval")
        self.combo_sync_mode.addItem("⚡  " + tr("sync_mode.realtime"), userData="realtime")

        current_mode = self.source.sync_mode if self.source else "startup"
        idx = self.combo_sync_mode.findData(current_mode)
        if idx >= 0:
            self.combo_sync_mode.setCurrentIndex(idx)

        lbl_mode = QLabel(tr("dialog.sync_mode"))
        lbl_mode.setStyleSheet("color: #F8FAFC; font-weight: 600; font-size: 13px;")
        form_layout.addRow(lbl_mode, self.combo_sync_mode)

        # Info-bulle / conseil sous le mode
        self.lbl_mode_hint = QLabel()
        self.lbl_mode_hint.setStyleSheet(
            "color: #38BDF8; font-size: 12px; margin-top: -2px; padding: 6px 10px; "
            "background-color: rgba(56, 189, 248, 0.08); border-radius: 4px; border: 1px solid rgba(56, 189, 248, 0.2);"
        )
        self.lbl_mode_hint.setWordWrap(True)
        form_layout.addRow("", self.lbl_mode_hint)

        # 4. Intervalle périodique (affiché si 'interval')
        self.interval_container = QWidget()
        interval_layout = QHBoxLayout(self.interval_container)
        interval_layout.setContentsMargins(0, 0, 0, 0)
        interval_layout.setSpacing(8)

        self.spin_interval = QSpinBox()
        self.spin_interval.setFixedHeight(34)
        self.spin_interval.setRange(5, 10080)  # De 5 min à 7 jours
        self.spin_interval.setSingleStep(15)
        default_interval = self.source.sync_interval_minutes if self.source else 60
        self.spin_interval.setValue(default_interval)
        interval_layout.addWidget(self.spin_interval)

        lbl_min = QLabel(tr("dialog.sync_interval_unit"))
        lbl_min.setStyleSheet("color: #94A3B8; font-size: 12.5px;")
        interval_layout.addWidget(lbl_min)
        interval_layout.addStretch()

        self.lbl_interval_form = QLabel(tr("dialog.sync_interval"))
        self.lbl_interval_form.setStyleSheet("color: #F8FAFC; font-weight: 600; font-size: 13px;")
        form_layout.addRow(self.lbl_interval_form, self.interval_container)

        # 5. Fréquence d'actualisation en continu (affiché si 'realtime')
        self.realtime_container = QWidget()
        realtime_layout = QHBoxLayout(self.realtime_container)
        realtime_layout.setContentsMargins(0, 0, 0, 0)
        realtime_layout.setSpacing(8)

        self.spin_realtime = QSpinBox()
        self.spin_realtime.setFixedHeight(34)
        self.spin_realtime.setRange(5, 3600)  # De 5 sec à 1 heure
        self.spin_realtime.setSingleStep(10)
        default_realtime = getattr(self.source, "sync_interval_seconds", 60) if self.source else 60
        self.spin_realtime.setValue(default_realtime or 60)
        realtime_layout.addWidget(self.spin_realtime)

        lbl_sec = QLabel(tr("dialog.sync_realtime_unit"))
        lbl_sec.setStyleSheet("color: #94A3B8; font-size: 12.5px;")
        realtime_layout.addWidget(lbl_sec)
        realtime_layout.addStretch()

        self.lbl_realtime_form = QLabel(tr("dialog.sync_realtime_label"))
        self.lbl_realtime_form.setStyleSheet("color: #F8FAFC; font-weight: 600; font-size: 13px;")
        form_layout.addRow(self.lbl_realtime_form, self.realtime_container)

        main_layout.addWidget(form_frame)

        # Boutons d'action
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 8, 0, 0)
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.btn_cancel = QPushButton(tr("common.cancel"))
        self.btn_cancel.setProperty("class", "secondary-btn")
        self.btn_cancel.setFixedHeight(34)
        self.btn_cancel.setAutoDefault(False)
        self.btn_cancel.setDefault(False)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        save_txt = tr("dialog.btn_save") if self.is_edit_mode else tr("dialog.btn_add_confirm")
        self.btn_save = QPushButton(save_txt)
        self.btn_save.setProperty("class", "primary-btn")
        self.btn_save.setFixedHeight(34)
        self.btn_save.setDefault(True)
        self.btn_save.setAutoDefault(True)
        self.btn_save.clicked.connect(self._on_save)
        btn_layout.addWidget(self.btn_save)

        main_layout.addLayout(btn_layout)

        # Connexions
        self.combo_sync_mode.currentIndexChanged.connect(self._update_mode_visibility)
        self._update_mode_visibility()

    def keyPressEvent(self, event) -> None:
        """Permet de valider et enregistrer le formulaire avec la touche Entrée / Return."""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._on_save()
            event.accept()
            return
        super().keyPressEvent(event)

    def _update_mode_visibility(self) -> None:
        mode = self.combo_sync_mode.currentData()
        is_interval = mode == "interval"
        is_realtime = mode == "realtime"

        self.interval_container.setVisible(is_interval)
        self.lbl_interval_form.setVisible(is_interval)

        self.realtime_container.setVisible(is_realtime)
        self.lbl_realtime_form.setVisible(is_realtime)

        hints = {
            "manual": tr("sync_mode.manual_hint"),
            "startup": tr("sync_mode.startup_hint"),
            "interval": tr("sync_mode.interval_hint"),
            "realtime": tr("sync_mode.realtime_hint"),
        }
        self.lbl_mode_hint.setText(hints.get(mode, ""))

    def _on_browse_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self,
            tr("dialog.select_folder_title"),
            self.edit_path.text() or "",
        )
        if folder:
            self.edit_path.setText(folder)
            if not self.edit_name.text().strip():
                self.edit_name.setText(Path(folder).name or folder)

    def _on_save(self) -> None:
        name = self.edit_name.text().strip()
        path = self.edit_path.text().strip()
        if not path:
            QMessageBox.warning(self, tr("dialog.source_config_add_title"), tr("dialog.source_path"))
            return
        if not name:
            self.edit_name.setText(Path(path).name or path)
        self.accept()

    _on_accept = _on_save

    def get_config_data(self) -> SourceConfigData:
        """Retourne les valeurs validées du formulaire."""
        return {
            "name": self.edit_name.text().strip() or Path(self.edit_path.text().strip()).name,
            "path_or_uri": self.edit_path.text().strip(),
            "sync_mode": str(self.combo_sync_mode.currentData() or "manual"),
            "sync_interval_minutes": int(self.spin_interval.value()),
            "sync_interval_seconds": int(self.spin_realtime.value()),
        }

    get_data = get_config_data
