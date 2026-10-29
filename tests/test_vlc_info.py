"""Provenance de la libvlc et comportement hors Windows."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from amso.services import vlc_info
from amso.services.vlc_info import LibVlcOrigin, classify_origin, supports_vlc_download


def test_classify_origin_chemin_sous_dossier_amso_donne_copie_amso(tmp_path: Path) -> None:
    lib = tmp_path / "vlc" / "libvlc.dll"
    lib.parent.mkdir()
    lib.touch()

    assert classify_origin(str(lib), [tmp_path / "vlc"]) is LibVlcOrigin.AMSO_COPY


def test_classify_origin_chemin_hors_dossiers_amso_donne_systeme(tmp_path: Path) -> None:
    assert classify_origin(str(tmp_path / "autre" / "libvlc.dll"), [tmp_path / "vlc"]) is LibVlcOrigin.SYSTEM


def test_classify_origin_chemin_vide_donne_inconnu() -> None:
    assert classify_origin("", []) is LibVlcOrigin.UNKNOWN


@pytest.mark.parametrize(("platform", "expected"), [("win32", True), ("linux", False), ("darwin", False)])
def test_supports_vlc_download_seulement_sous_windows(platform: str, expected: bool) -> None:
    assert supports_vlc_download(platform) is expected


def test_setup_macos_user_vlc_pointe_vers_applications_utilisateur(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = tmp_path / "Applications" / "VLC.app" / "Contents" / "MacOS"
    (base / "lib").mkdir(parents=True)
    (base / "lib" / "libvlc.dylib").touch()
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    original_exists = Path.exists
    monkeypatch.setattr(
        Path,
        "exists",
        lambda self: (
            False
            if self.as_posix().endswith("/Applications/VLC.app")
            and self.is_absolute()
            and self.parent == Path("/Applications")
            else original_exists(self)
        ),
    )
    monkeypatch.setenv(
        "PYTHON_VLC_LIB_PATH", ""
    )  # enregistre l'état initial pour que la fin du test retire la variable
    monkeypatch.delenv("PYTHON_VLC_LIB_PATH")
    monkeypatch.setenv(
        "PYTHON_VLC_MODULE_PATH", ""
    )  # enregistre l'état initial pour que la fin du test retire la variable
    monkeypatch.delenv("PYTHON_VLC_MODULE_PATH")

    assert vlc_info.setup_macos_user_vlc("darwin") == base


def test_setup_macos_user_vlc_ignore_les_autres_plateformes() -> None:
    assert vlc_info.setup_macos_user_vlc("linux") is None


def test_describe_libvlc_donne_version_et_origine_quand_python_vlc_charge() -> None:
    importlib.import_module("amso.services.player_service")  # charge python-vlc dans le proxy
    info = vlc_info.describe_libvlc()
    if info is None:
        pytest.skip("python-vlc indisponible")

    assert info.version[0].isdigit()
    assert info.origin in (LibVlcOrigin.AMSO_COPY, LibVlcOrigin.SYSTEM)
