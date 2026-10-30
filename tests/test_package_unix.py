"""Noms de fichiers et contenu des fichiers générés pour les versions Linux et macOS."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from package_unix import APPRUN, DESKTOP_ENTRY, normalized_arch, release_file_name


@pytest.mark.parametrize(
    ("system", "arch", "extension", "expected"),
    [
        ("linux", "x86_64", "tar.gz", "AMSO-Linux-v0.4.1-x86_64.tar.gz"),
        ("linux", "x86_64", "AppImage", "AMSO-Linux-v0.4.1-x86_64.AppImage"),
        ("macos", "arm64", "dmg", "AMSO-macOS-arm64-v0.4.1.dmg"),
        ("macos", "x86_64", "dmg", "AMSO-macOS-x86_64-v0.4.1.dmg"),
    ],
)
def test_release_file_name_suit_la_convention_de_publication(
    system: str, arch: str, extension: str, expected: str
) -> None:
    assert release_file_name(system, "0.4.1", arch, extension) == expected


@pytest.mark.parametrize(
    ("machine", "expected"),
    [("AMD64", "x86_64"), ("x86_64", "x86_64"), ("arm64", "arm64"), ("aarch64", "arm64")],
)
def test_normalized_arch_unifie_les_noms_de_machine(machine: str, expected: str) -> None:
    assert normalized_arch(machine) == expected


def test_apprun_lance_l_executable_pyinstaller_embarque() -> None:
    assert APPRUN.startswith("#!/bin/sh")
    assert "usr/lib/amso/AMSO" in APPRUN


def test_desktop_entry_declare_l_executable_et_l_icone() -> None:
    assert "Exec=AMSO" in DESKTOP_ENTRY
    assert "Icon=AMSO" in DESKTOP_ENTRY
    assert "\r" not in DESKTOP_ENTRY
