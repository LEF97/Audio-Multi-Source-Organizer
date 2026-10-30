"""Une clé présente seulement dans fr.json (développement) ne doit jamais s'afficher sous son nom technique."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from amso.core.config import get_config_manager
from amso.core.i18n import I18nManager


def _locales(tmp_path: Path, fr: dict[str, str], en: dict[str, str], ja: dict[str, str]) -> Path:
    for code, data in (("fr", fr), ("en", en), ("ja", ja)):
        (tmp_path / f"{code}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return tmp_path


def _manager(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, **files: dict[str, str]) -> I18nManager:
    locales = _locales(tmp_path, files["fr"], files["en"], files["ja"])
    monkeypatch.setattr("amso.core.i18n.get_locales_dir", lambda: locales)
    manager = I18nManager(config_manager=get_config_manager())
    manager._translations = files["ja"]
    return manager


def test_tr_cle_absente_de_la_langue_et_de_en_retombe_sur_le_francais(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = _manager(tmp_path, monkeypatch, fr={"a": "Bibliothèque"}, en={}, ja={})

    assert manager.tr("a") == "Bibliothèque"


def test_tr_langue_puis_anglais_priment_sur_le_francais(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manager = _manager(tmp_path, monkeypatch, fr={"a": "FR", "b": "FR"}, en={"a": "EN", "b": "EN"}, ja={"b": "JA"})

    assert (manager.tr("a"), manager.tr("b")) == ("EN", "JA")


def test_tr_cle_inconnue_partout_retourne_la_cle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manager = _manager(tmp_path, monkeypatch, fr={}, en={}, ja={})

    assert manager.tr("inconnue") == "inconnue"
