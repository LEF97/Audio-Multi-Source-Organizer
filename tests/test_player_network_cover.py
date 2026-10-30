"""Revérification périodique de la pochette des pistes réseau dans la vue Lecteur."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication

from amso.core.database import SourceType, TrackRecord
from amso.services.player_service import PlayerService
from amso.ui.views.player_view import NETWORK_COVER_POLL_MS, PlayerView

NETWORK_FILE = r"\\NAS\Audio\Artiste\a.flac"


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        app = QApplication([])
    return app


def _track(path: str, folder: str) -> TrackRecord:
    return TrackRecord(
        source_type=SourceType.LOCAL,
        source_ref=path,
        source_path=path,
        file_name="a.flac",
        title="A",
        artist="B",
        folder_path=folder,
    )


def test_update_track_info_piste_reseau_demarre_le_minuteur(qapp: QApplication) -> None:
    view = PlayerView(PlayerService())
    with patch("amso.ui.views.player_view.load_cover_async", MagicMock()):
        view.update_track_info(_track(NETWORK_FILE, r"\\NAS\Audio\Artiste"))
    assert view._network_cover_timer.isActive()
    assert view._network_cover_timer.interval() == NETWORK_COVER_POLL_MS


def test_update_track_info_piste_locale_arrete_le_minuteur(qapp: QApplication, tmp_path: Path) -> None:
    view = PlayerView(PlayerService())
    with patch("amso.ui.views.player_view.load_cover_async", MagicMock()):
        view.update_track_info(_track(NETWORK_FILE, r"\\NAS\Audio\Artiste"))
        view.update_track_info(_track(str(tmp_path / "a.flac"), str(tmp_path)))
    assert not view._network_cover_timer.isActive()
