"""Getters typés de ConfigManager : valeur par défaut, bornes et valeurs illisibles."""

from __future__ import annotations

from pathlib import Path

import pytest

from amso.core.config import ConfigManager

_SECTION = "Player"


@pytest.fixture
def cfg(tmp_path: Path) -> ConfigManager:
    return ConfigManager(tmp_path / "config.ini")


@pytest.mark.parametrize(
    ("getter", "key", "default", "low", "high"),
    [
        ("get_player_volume", "volume", 80, 0, 100),
        ("get_crossfade_duration", "crossfade_seconds", 3, 1, 20),
        ("get_blind_test_countdown", "blind_test_countdown", 20, 5, 120),
        ("get_blind_test_fade", "blind_test_fade", 2, 0, 10),
        ("get_vlc_gapless_latency", "vlc_gapless_latency_ms", 250, 0, 2000),
    ],
)
def test_int_getter_absent_illisible_ou_hors_bornes_reste_dans_les_bornes(
    cfg: ConfigManager, getter: str, key: str, default: int, low: int, high: int
) -> None:
    read = getattr(cfg, getter)
    assert read() == default
    cfg.set(_SECTION, key, "pas_un_nombre")
    assert read() == default
    cfg.set(_SECTION, key, str(high + 500))
    assert read() == high
    cfg.set(_SECTION, key, str(low - 500))
    assert read() == low


def test_float_getter_borne_la_duree_du_fondu(cfg: ConfigManager) -> None:
    assert cfg.get_fade_in_track_duration() == 1.0
    cfg.set_fade_in_track_duration(99.0)
    assert cfg.get_fade_in_track_duration() == 5.0
    cfg.set(_SECTION, "fade_in_track_duration", "abc")
    assert cfg.get_fade_in_track_duration() == 1.0


@pytest.mark.parametrize("raw", ["true", "TRUE", "1", "yes", "on"])
def test_bool_getter_valeurs_vraies_acceptees(cfg: ConfigManager, raw: str) -> None:
    cfg.set(_SECTION, "shuffle", raw)
    assert cfg.get_player_shuffle() is True


def test_bool_getter_defauts_distincts_et_aller_retour(cfg: ConfigManager) -> None:
    assert cfg.get_player_shuffle() is False
    assert cfg.get_fade_in_resume_enabled() is True
    cfg.set_fade_in_resume_enabled(False)
    assert cfg.get_fade_in_resume_enabled() is False
    cfg.set_eq_enabled(True)
    assert cfg.get_eq_enabled() is True


def test_repeat_mode_et_position_valeurs_illisibles_retombent_a_zero(cfg: ConfigManager) -> None:
    cfg.set(_SECTION, "repeat_mode", "x")
    cfg.set(_SECTION, "position_ms", "x")
    assert cfg.get_player_repeat_mode() == 0
    assert cfg.get_player_position_ms() == 0
    cfg.set(_SECTION, "position_ms", "-5")
    assert cfg.get_player_position_ms() == 0
