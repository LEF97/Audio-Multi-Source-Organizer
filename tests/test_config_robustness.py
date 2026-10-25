"""Tests de robustesse de l'écriture et du chargement de config.ini (écriture atomique, sauvegarde en .bak)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from amso.core.config import ConfigManager


def test_save_is_atomic_and_leaves_no_temporary_file(tmp_path: Path) -> None:
    path = tmp_path / "config.ini"
    cfg = ConfigManager(path)
    cfg.set("Player", "transition_mode", "crossfade")
    assert "transition_mode = crossfade" in path.read_text(encoding="utf-8")
    assert not (tmp_path / "config.ini.tmp").exists()
    assert ConfigManager(path).get("Player", "transition_mode") == "crossfade"


def test_failed_write_keeps_previous_file_intact(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "config.ini"
    cfg = ConfigManager(path)
    cfg.set("Player", "audio_engine", "buffer")
    before = path.read_text(encoding="utf-8")

    def boom(src: object, dst: object) -> None:
        raise OSError("coupure simulée")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(OSError):
        cfg.set("Player", "audio_engine", "vlc_direct")
    monkeypatch.undo()

    assert path.read_text(encoding="utf-8") == before  # ancien fichier intact
    assert not (tmp_path / "config.ini.tmp").exists()  # fichier temporaire nettoyé


def test_corrupted_file_is_backed_up_before_reset(tmp_path: Path) -> None:
    path = tmp_path / "config.ini"
    path.write_text("[Player]\nvolume = 80\n[Player]\nvolume = 90\n", encoding="utf-8")  # section dupliquée : invalide
    cfg = ConfigManager(path)
    assert cfg.get("Player", "volume") is None  # repart sur une configuration vierge
    backup = tmp_path / "config.ini.bak"
    assert backup.exists() and "volume = 90" in backup.read_text(encoding="utf-8")
    cfg.set("Player", "volume", "50")  # la configuration reste utilisable après la réinitialisation
    assert ConfigManager(path).get("Player", "volume") == "50"
