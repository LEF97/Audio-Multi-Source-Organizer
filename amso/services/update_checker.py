"""Service de vérification non-bloquante des mises à jour d'AMSO via l'API GitHub Releases."""

from __future__ import annotations

import json
import logging
import re
import urllib.request
from typing import Any

from PySide6.QtCore import QThread, Signal

from amso import __version__
from amso.core.constants import URL_GITHUB_API_LATEST_RELEASE, URL_GITHUB_RELEASES

logger = logging.getLogger(__name__)


def parse_version(version_str: str) -> tuple[int, ...]:
    """Extrait un tuple d'entiers représentant la version sémantique (ex. 'v1.2.3' -> (1, 2, 3))."""
    if not version_str:
        return (0,)
    # Supprime 'v' ou 'V' initial et les espaces
    cleaned = version_str.strip().lstrip("vV")
    # Trouve toutes les séquences numériques consécutives
    numbers = re.findall(r"\d+", cleaned)
    if not numbers:
        return (0,)
    return tuple(int(num) for num in numbers)


def is_newer_version(latest_str: str, current_str: str) -> bool:
    """Compare deux numéros de versions et renvoie True si latest est plus récent que current."""
    v_latest = parse_version(latest_str)
    v_current = parse_version(current_str)
    return v_latest > v_current


class UpdateCheckerWorker(QThread):
    """Worker en arrière-plan vérifiant silencieusement l'existence d'une nouvelle version."""

    update_available = Signal(str, str)  # (version_tag, release_url)
    check_finished = Signal(bool, str)  # (is_newer_available, latest_version_or_err)

    def __init__(
        self,
        current_version: str = __version__,
        api_url: str = URL_GITHUB_API_LATEST_RELEASE,
        parent: Any = None,
    ) -> None:
        super().__init__(parent)
        self.current_version = current_version
        self.api_url = api_url
        self._is_cancelled = False
        self.latest_tag = ""
        self.release_url = URL_GITHUB_RELEASES
        self.published_date = ""

    def cancel(self) -> None:
        """Indique au worker d'annuler la vérification."""
        self._is_cancelled = True

    def run(self) -> None:
        """Interroge l'API GitHub de manière légère et non-bloquante avec timeout court."""
        if self._is_cancelled:
            return

        req = urllib.request.Request(
            self.api_url,
            headers={
                "User-Agent": f"AMSO-UpdateChecker/{self.current_version}",
                "Accept": "application/vnd.github.v3+json",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=4.0) as response:
                if self._is_cancelled:
                    return
                if response.status != 200:
                    logger.debug("Réponse GitHub inattendue: status %s", response.status)
                    self.check_finished.emit(False, f"Status {response.status}")
                    return

                raw_data = response.read().decode("utf-8")
                data = json.loads(raw_data)

            if self._is_cancelled:
                return

            tag_name = data.get("tag_name", "").strip()
            release_url = data.get("html_url", URL_GITHUB_RELEASES)
            published_at = str(data.get("published_at", "")).strip()

            self.latest_tag = tag_name
            self.release_url = release_url
            self.published_date = published_at[:10] if published_at else ""

            if tag_name and is_newer_version(tag_name, self.current_version):
                logger.info("Nouvelle version d'AMSO détectée : %s (actuelle: %s)", tag_name, self.current_version)
                self.update_available.emit(tag_name, release_url)
                self.check_finished.emit(True, tag_name)
            else:
                logger.debug("AMSO est à jour (%s vs %s)", self.current_version, tag_name)
                self.check_finished.emit(False, tag_name)

        except Exception as exc:
            # En cas de coupure réseau, d'absence de connexion ou de rate limit :
            # Échec 100% silencieux sans impacter ni bloquer l'expérience utilisateur
            logger.debug("Vérification de mise à jour échouée (silencieuse) : %s", exc)
            self.check_finished.emit(False, str(exc))
