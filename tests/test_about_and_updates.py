"""Tests unitaires pour le modèle économique, le dialogue À propos et la notification de mise à jour."""

from __future__ import annotations

import json
import urllib.error
from pathlib import Path

import pytest
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QApplication

from amso import __version__
from amso.core.constants import (
    URL_GITHUB_API_LATEST_RELEASE,
    URL_GITHUB_REPO,
    URL_GITHUB_SPONSORS,
    URL_ITCH_IO,
    URL_KO_FI,
)
from amso.core.database import DatabaseManager, SourceType
from amso.core.i18n import get_i18n, tr
from amso.services.update_checker import (
    UpdateCheckerWorker,
    is_newer_version,
    parse_version,
)
from amso.ui.dialogs.about_dialog import AboutDialog
from amso.ui.views.main_window import MainWindow
from amso.ui.views.update_banner import UpdateBannerWidget


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Fixture réutilisant ou créant l'instance QApplication unique."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def db() -> DatabaseManager:
    """Base de données en mémoire pour initialiser MainWindow."""
    db_manager = DatabaseManager(":memory:")
    db_manager.add_source(SourceType.LOCAL, "Dossier Test", "D:/Music")
    return db_manager


def test_funding_yaml_exists_and_valid():
    """Vérifie que .github/FUNDING.yml est bien présent et contient les bons canaux de financement."""
    funding_path = Path(__file__).parents[1] / ".github" / "FUNDING.yml"
    assert funding_path.is_file(), "Le fichier .github/FUNDING.yml doit exister"

    content = funding_path.read_text(encoding="utf-8")
    assert "github: [LEF97]" in content or "github: LEF97" in content
    assert "ko_fi: arnaudlef97" in content or "ko_fi: lef97" in content
    assert "https://arnaudlef97.itch.io/amso" in content or "https://lef97.itch.io/audio-multi-source-organizer" in content


def test_constants_and_version():
    """Vérifie la définition cohérente des versions et des URLs de distribution/don."""
    assert __version__ == "0.2.0"
    assert "github.com/LEF97" in URL_GITHUB_REPO
    assert "itch.io" in URL_ITCH_IO
    assert "ko-fi.com" in URL_KO_FI
    assert URL_GITHUB_SPONSORS == "https://github.com/sponsors/lef97"
    assert "api.github.com" in URL_GITHUB_API_LATEST_RELEASE


def test_version_parsing_and_comparison():
    """Vérifie le parsing et la comparaison sémantique robuste des versions."""
    assert parse_version("v0.1.0") == (0, 1, 0)
    assert parse_version("1.2.3") == (1, 2, 3)
    assert parse_version("v2.0.0-rc1") == (2, 0, 0, 1)
    assert parse_version("") == (0,)
    assert parse_version("abc") == (0,)

    assert is_newer_version("v0.2.0", "v0.1.0") is True
    assert is_newer_version("v1.0.0", "v0.9.9") is True
    assert is_newer_version("0.1.1", "0.1.0") is True

    assert is_newer_version("v0.1.0", "v0.1.0") is False
    assert is_newer_version("v0.0.9", "v0.1.0") is False
    assert is_newer_version("0.1.0", "0.2.0") is False


def test_about_dialog_creation_and_links(qapp: QApplication, monkeypatch: pytest.MonkeyPatch):
    """Vérifie l'affichage du dialogue À propos et le fonctionnement des liens externes."""
    get_i18n().set_language("fr")
    dialog = AboutDialog()

    assert dialog.windowTitle() == tr("dialog.about_title")
    assert hasattr(dialog, "btn_donate")
    assert hasattr(dialog, "btn_github")
    assert hasattr(dialog, "btn_itch")
    assert hasattr(dialog, "btn_sponsors")
    assert hasattr(dialog, "btn_close")

    # Vérification des appels QDesktopServices.openUrl
    opened_urls: list[str] = []

    def mock_open_url(url: QUrl) -> bool:
        opened_urls.append(url.toString())
        return True

    monkeypatch.setattr(QDesktopServices, "openUrl", mock_open_url)

    dialog.btn_donate.click()
    assert URL_KO_FI in opened_urls

    dialog.btn_github.click()
    assert URL_GITHUB_REPO in opened_urls

    dialog.btn_itch.click()
    assert URL_ITCH_IO in opened_urls

    dialog.btn_sponsors.click()
    assert URL_GITHUB_SPONSORS in opened_urls

    dialog.close()


def test_update_banner_widget(qapp: QApplication, monkeypatch: pytest.MonkeyPatch):
    """Vérifie le cycle de vie de la bannière non-bloquante de mise à jour."""
    get_i18n().set_language("fr")
    banner = UpdateBannerWidget()

    # Cachée initialement
    assert banner.isVisible() is False

    # Affichage d'une nouvelle version
    banner.show_update("v0.2.0", "https://github.com/LEF97/Audio-Multi-Source-Organizer/releases/tag/v0.2.0")
    assert banner.isVisible() is True
    assert "0.2.0" in banner.text_label.text()
    assert "Ko-fi" in banner.text_label.text()

    # Clic sur le bouton télécharger
    opened_urls: list[str] = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda url: opened_urls.append(url.toString()) or True)
    banner.btn_download.click()
    assert "releases/tag/v0.2.0" in opened_urls[0]

    # Clic sur le bouton soutien
    banner.btn_support.click()
    assert URL_KO_FI in opened_urls[1]

    # Clic sur fermer
    banner.btn_dismiss.click()
    assert banner.isVisible() is False


def test_update_checker_worker_success(qapp: QApplication, monkeypatch: pytest.MonkeyPatch):
    """Vérifie la détection d'une mise à jour disponible via le worker."""
    fake_json = json.dumps({
        "tag_name": "v0.2.0",
        "html_url": "https://github.com/LEF97/Audio-Multi-Source-Organizer/releases/tag/v0.2.0",
    }).encode("utf-8")

    class MockResponse:
        def __init__(self):
            self.status = 200

        def read(self):
            return fake_json

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: MockResponse())

    worker = UpdateCheckerWorker(current_version="0.1.0")

    received_updates: list[tuple[str, str]] = []
    worker.update_available.connect(lambda tag, url: received_updates.append((tag, url)))

    worker.run()

    assert len(received_updates) == 1
    assert received_updates[0][0] == "v0.2.0"
    assert "releases/tag/v0.2.0" in received_updates[0][1]


def test_update_checker_worker_no_update(qapp: QApplication, monkeypatch: pytest.MonkeyPatch):
    """Vérifie le comportement silencieux lorsqu'AMSO est déjà à jour."""
    fake_json = json.dumps({
        "tag_name": "v0.1.0",
        "html_url": "https://github.com/LEF97/Audio-Multi-Source-Organizer/releases/tag/v0.1.0",
    }).encode("utf-8")

    class MockResponse:
        def __init__(self):
            self.status = 200

        def read(self):
            return fake_json

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: MockResponse())

    worker = UpdateCheckerWorker(current_version="0.1.0")

    received_updates: list[tuple[str, str]] = []
    finished_results: list[tuple[bool, str]] = []

    worker.update_available.connect(lambda tag, url: received_updates.append((tag, url)))
    worker.check_finished.connect(lambda ok, ver: finished_results.append((ok, ver)))

    worker.run()

    assert len(received_updates) == 0
    assert len(finished_results) == 1
    assert finished_results[0][0] is False


def test_update_checker_worker_network_error(qapp: QApplication, monkeypatch: pytest.MonkeyPatch):
    """Vérifie la robustesse en cas d'erreur réseau (échec silencieux sans crash)."""

    def mock_fail(req, timeout):
        raise urllib.error.URLError("No connection")

    monkeypatch.setattr(urllib.request, "urlopen", mock_fail)

    worker = UpdateCheckerWorker(current_version="0.1.0")

    received_updates: list[tuple[str, str]] = []
    finished_results: list[tuple[bool, str]] = []

    worker.update_available.connect(lambda tag, url: received_updates.append((tag, url)))
    worker.check_finished.connect(lambda ok, ver: finished_results.append((ok, ver)))

    worker.run()

    assert len(received_updates) == 0
    assert len(finished_results) == 1
    assert finished_results[0][0] is False


def test_main_window_menu_and_shortcuts(qapp: QApplication, db: DatabaseManager):
    """Vérifie la disparition du menu Aide, la navigation vers la page À propos et le raccourci F1."""
    window = MainWindow(db)

    # La barre de menu "Aide" a disparu / est masquée
    assert window.menuBar().isVisible() is False

    # Actions et raccourcis F1
    assert hasattr(window, "action_about")
    assert window.action_about.shortcut().toString() == "F1"
    assert hasattr(window, "action_check_updates")
    assert hasattr(window, "shortcut_f1")

    # Bannière de mise à jour
    assert hasattr(window, "update_banner")
    assert isinstance(window.update_banner, UpdateBannerWidget)

    # Page dédiée À propos dans les paramètres
    assert hasattr(window, "page_settings_about")
    assert hasattr(window, "btn_settings_about")
    assert window.btn_settings_about.text() != ""

    # Ordre des boutons dans le tiroir Paramètres : Général, Lecteur, Sources, Logs, À propos
    assert hasattr(window, "btn_settings_general")
    assert hasattr(window, "btn_settings_player")
    assert hasattr(window, "btn_settings_sources")
    assert hasattr(window, "btn_settings_logs")

    # Clic sur le logo AMSO (en haut à gauche) mène directement à la page À propos
    assert hasattr(window, "btn_quick_about")
    window.btn_quick_about.clicked.emit()
    assert window.stacked_widget.currentWidget() == window.page_settings_about
    assert window._current_active_page == "settings_about"
    assert window.btn_settings_about.isChecked() is True

    # Clic sur le bouton À propos des Paramètres
    window._on_settings_general_clicked()
    assert window.stacked_widget.currentWidget() == window.page_settings
    window.btn_settings_about.click()
    assert window.stacked_widget.currentWidget() == window.page_settings_about

    window.close()


def test_about_page_ui_and_visual_effect(qapp: QApplication, db: DatabaseManager):
    """Vérifie le titre 'À propos' épuré, le widget d'effet rétro-bars en arrière-plan et les dimensions."""
    get_i18n().set_language("fr")
    window = MainWindow(db)

    # 1. Titre épuré sans "Settings >" ou "Paramètres >"
    assert window.lbl_settings_about_page_title.text() == "À propos"
    get_i18n().set_language("en")
    assert window.lbl_settings_about_page_title.text() == "About"
    get_i18n().set_language("fr")

    # 2. Présence de l'animation rétro-bars synchronisée avec la musique (non-démo)
    assert hasattr(window, "about_visual_effect")
    assert window.about_visual_effect._demo_mode is False
    assert window.about_visual_effect._effect_type == window.about_visual_effect.EFFECT_BARS
    assert window.about_visual_effect._bars_align_left is True

    # 3. Éléments d'interface et boutons de mise à jour
    assert hasattr(window, "btn_check_updates_about")
    assert hasattr(window, "lbl_update_status_about")
    assert hasattr(window, "btn_update_download")

    # 4. Nouveaux sous-titres et boutons réorganisés
    assert hasattr(window, "lbl_about_credits_title")
    assert "👍" in window.lbl_about_credits_title.text()
    assert hasattr(window, "lbl_about_support_title")
    assert "💖" in window.lbl_about_support_title.text()
    assert hasattr(window, "lbl_about_official_title")
    assert "🌐" in window.lbl_about_official_title.text()
    assert hasattr(window, "btn_about_kofi")
    assert hasattr(window, "btn_about_sponsors")
    assert hasattr(window, "btn_about_github")
    assert hasattr(window, "btn_about_itch")

    window.close()


def test_about_page_update_status_flow(qapp: QApplication, db: DatabaseManager, monkeypatch: pytest.MonkeyPatch):
    """Vérifie la mise à jour réactive du statut (À jour, Version disponible avec date, Télécharger)."""
    get_i18n().set_language("fr")
    window = MainWindow(db)

    # 1. Simuler l'état "À jour"
    window._on_update_check_finished(False, "v0.1.0", manual=False)
    assert "✓ À jour" in window.lbl_update_status_about.text()
    assert __version__ in window.lbl_update_status_about.text()
    assert window.btn_update_download.isHidden() is True

    # 2. Simuler une nouvelle version disponible avec date
    class FakeWorker:
        latest_tag = "v0.2.0"
        release_url = "https://github.com/LEF97/Audio-Multi-Source-Organizer/releases/tag/v0.2.0"
        published_date = "2026-10-17"

    window.update_worker = FakeWorker()  # type: ignore[assignment]
    window._on_update_check_finished(True, "v0.2.0", manual=False)

    assert "🎉" in window.lbl_update_status_about.text()
    assert "v0.2.0" in window.lbl_update_status_about.text()
    assert "2026-10-17" in window.lbl_update_status_about.text()
    assert window.btn_update_download.isHidden() is False

    # Clic sur le bouton Télécharger
    opened_urls: list[str] = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda url: opened_urls.append(url.toString()) or True)
    window.btn_update_download.click()
    assert "v0.2.0" in opened_urls[0]

    # 3. Simuler une erreur de vérification
    window._on_update_check_finished(False, "URLError: timed out", manual=False)
    assert "⚠️" in window.lbl_update_status_about.text()
    assert window.btn_update_download.isHidden() is True

    window.close()
