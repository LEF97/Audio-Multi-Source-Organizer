"""Vérification et affichage des mises à jour (mixin de MainWindow)."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QMainWindow,
)

from amso import __version__
from amso.core.constants import (
    URL_GITHUB_RELEASES,
)
from amso.core.i18n import get_i18n, tr
from amso.services.update_checker import UpdateCheckerWorker

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    _MixinBase = QMainWindow
else:
    _MixinBase = object


class UpdateControllerMixin(_MixinBase):
    """Vérification et affichage des mises à jour (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de MainWindow sont résolus dynamiquement (typage uniquement)
        update_worker: UpdateCheckerWorker | None
        _last_update_check: dict[str, Any]

        def __getattr__(self, name: str) -> Any: ...

    def _check_for_updates(self, manual: bool = False) -> None:
        """Lance une vérification non bloquante de mise à jour sur GitHub Releases."""
        if hasattr(self, "update_worker") and self.update_worker and self.update_worker.isRunning():
            return

        if manual:
            self._last_update_check["status"] = "checking"
            self._refresh_update_ui()
            self.status_label.setText(tr("settings.update_checking"))

        self.update_worker = UpdateCheckerWorker(parent=self)
        self.update_worker.update_available.connect(self._on_update_available)
        self.update_worker.check_finished.connect(
            lambda has_update, detail: self._on_update_check_finished(has_update, detail, manual=manual)
        )
        self.update_worker.start()

    def _on_update_available(self, latest_version: str, release_url: str) -> None:
        """Affiche la bannière discrète de mise à jour au bas de la fenêtre."""
        if hasattr(self, "update_banner") and self.update_banner:
            self.update_banner.show_update(latest_version, release_url)

    def _on_update_check_finished(self, has_update: bool, detail: str, manual: bool = False) -> None:
        """Met à jour l'état de l'application après toute vérification (automatique ou manuelle)."""
        worker = getattr(self, "update_worker", None)
        latest_tag = getattr(worker, "latest_tag", "") or detail
        release_url = getattr(worker, "release_url", "") or URL_GITHUB_RELEASES
        published_date = getattr(worker, "published_date", "")

        if has_update:
            self._last_update_check = {
                "status": "available",
                "version": latest_tag,
                "date": published_date,
                "url": release_url,
                "checked_at": time.time(),
            }
        elif (
            detail
            and not detail.lower().startswith("status")
            and "error" not in detail.lower()
            and "exception" not in detail.lower()
        ):
            # Vérification réussie sans mise à jour plus récente
            self._last_update_check = {
                "status": "latest",
                "version": __version__,
                "date": published_date,
                "url": release_url,
                "checked_at": time.time(),
            }
        else:
            # Erreur de connexion ou API indisponible
            self._last_update_check = {
                "status": "error",
                "version": "",
                "date": "",
                "url": "",
                "error": detail,
                "checked_at": time.time(),
            }

        self._refresh_update_ui()

        if manual:
            self._on_manual_update_check_finished(has_update, detail)

    def _refresh_update_ui(self) -> None:
        """Met à jour les éléments de la page À propos et les boutons selon l'état actuel de mise à jour."""
        if not hasattr(self, "lbl_update_status_about"):
            return

        status = self._last_update_check.get("status", "pending")
        if status == "checking":
            self.lbl_update_status_about.setText(f"⏳ {tr('settings.update_checking')}")
            self.lbl_update_status_about.setStyleSheet("color: #38BDF8; font-size: 12px; font-weight: 500;")
            if hasattr(self, "btn_update_download"):
                self.btn_update_download.setVisible(False)
        elif status == "latest":
            msg = tr("settings.update_latest").format(version=__version__)
            self.lbl_update_status_about.setText(msg)
            self.lbl_update_status_about.setStyleSheet("color: #4ADE80; font-size: 12px; font-weight: 600;")
            if hasattr(self, "btn_update_download"):
                self.btn_update_download.setVisible(False)
        elif status == "available":
            ver = self._last_update_check.get("version", "")
            date_str = self._last_update_check.get("date", "")
            current_lang = get_i18n().current_language
            if date_str:
                date_formatted = f" du {date_str}" if current_lang == "fr" else f" ({date_str})"
            else:
                date_formatted = ""
            msg = tr("settings.update_available").format(version=ver, date=date_formatted)
            self.lbl_update_status_about.setText(msg)
            self.lbl_update_status_about.setStyleSheet("color: #FBBF24; font-size: 12px; font-weight: 700;")
            if hasattr(self, "btn_update_download"):
                self.btn_update_download.setVisible(True)
                self.btn_update_download.setText(tr("settings.btn_download_update"))
        elif status == "error":
            self.lbl_update_status_about.setText(tr("settings.update_error"))
            self.lbl_update_status_about.setStyleSheet("color: #94A3B8; font-size: 12px;")
            if hasattr(self, "btn_update_download"):
                self.btn_update_download.setVisible(False)
        else:
            # "pending"
            self.lbl_update_status_about.setText("")
            if hasattr(self, "btn_update_download"):
                self.btn_update_download.setVisible(False)

    def _open_latest_release_url(self) -> None:
        """Ouvre la page GitHub Releases de la dernière version dans le navigateur."""
        url = self._last_update_check.get("url") or URL_GITHUB_RELEASES
        QDesktopServices.openUrl(QUrl(url))

    def _on_manual_update_check_finished(self, has_update: bool, detail: str) -> None:
        """Affiche le retour d'une vérification manuelle initiée par l'utilisateur."""
        if not has_update:
            status = self._last_update_check.get("status")
            if status == "error":
                self.status_label.setText(tr("settings.update_error"))
            else:
                msg = tr("update.already_latest").format(version=__version__)
                self.status_label.setText(f"✓ {msg}")
            QTimer.singleShot(4000, lambda: self.status_label.setText(tr("status.ready")))
