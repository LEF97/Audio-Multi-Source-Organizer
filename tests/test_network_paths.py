"""Tests de la détection des chemins réseau."""

from __future__ import annotations

import pytest

from amso.core.network_paths import is_network_path


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (r"\\NAS\Audio\a.flac", True),
        ("//nas/audio/a.flac", True),
        (r"\\?\UNC\nas\audio\a.flac", True),
        (r"\\?\C:\Musique\a.flac", False),
        ("", False),
        (None, False),
        ("/home/user/a.flac", False),
    ],
)
def test_is_network_path_chemin_donne_detection_attendue(path: str | None, expected: bool) -> None:
    assert is_network_path(path) is expected
