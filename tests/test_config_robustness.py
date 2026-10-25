"""Tests de robustesse de l'écriture et du chargement de config.ini (écriture atomique, sauvegarde en .bak)."""

from __future__ import annotations

import os
import threading
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


def test_save_retries_when_windows_refuses_the_replacement_for_a_moment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "config.ini"
    cfg = ConfigManager(path)
    real_replace = os.replace
    calls = {"n": 0}

    def flaky(src: object, dst: object) -> None:
        calls["n"] += 1
        if calls["n"] <= 3:
            raise PermissionError("[WinError 5] Accès refusé (simulé)")
        real_replace(src, dst)  # type: ignore[arg-type]

    monkeypatch.setattr(os, "replace", flaky)
    monkeypatch.setattr("amso.core.config.time.sleep", lambda _s: None)
    cfg.set("Player", "volume", "42")
    monkeypatch.undo()
    assert calls["n"] == 4
    assert ConfigManager(path).get("Player", "volume") == "42"
    assert not (tmp_path / "config.ini.tmp").exists()


def test_concurrent_saves_from_several_threads_do_not_collide(tmp_path: Path) -> None:
    """Comme dans l'application : un gestionnaire partagé, des écritures simultanées (timers, threads)."""
    path = tmp_path / "config.ini"
    shared = ConfigManager(path)
    errors: list[Exception] = []

    def worker(idx: int) -> None:
        try:
            for i in range(25):
                shared.set("Player", f"key_{idx}", str(i))
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert errors == []
    assert not (tmp_path / "config.ini.tmp").exists()
    reloaded = ConfigManager(path)
    assert [reloaded.get("Player", f"key_{i}") for i in range(4)] == ["24"] * 4
