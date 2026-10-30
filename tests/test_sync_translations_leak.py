"""Le script de synchronisation repère les traductions qui reprennent le français (« français (romaji) »)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from sync_translations import has_source_leak, is_invalid_translation, needs_retranslation


def test_has_source_leak_texte_francais_suivi_de_romaji_est_detecte() -> None:
    assert has_source_leak("Ne pas autoriser la veille (Non autoriser furyou)", "Ne pas autoriser la veille")


def test_has_source_leak_traduction_normale_nest_pas_detectee() -> None:
    assert not has_source_leak("スリープを許可しない", "Ne pas autoriser la veille")


def test_has_source_leak_texte_court_nest_pas_detecte() -> None:
    assert not has_source_leak("Blind Test ja", "Blind")


def test_needs_retranslation_valeur_identique_ou_doublee_est_a_retraduire() -> None:
    ref = "Personnalisez la façon dont les morceaux s'enchaînent"
    assert needs_retranslation("k", ref, ref, "ja")
    assert needs_retranslation("k", ref + " (romaji)", ref, "ja")
    assert not needs_retranslation("k", "曲のつなぎ方を設定します", ref, "ja")


def test_is_invalid_translation_marqueur_perdu_ou_ajoute_est_detecte() -> None:
    assert is_invalid_translation("Charger des morceaux", "Charger {count} morceaux")
    assert is_invalid_translation("{count} {count_plural}", "{count} morceaux")
    assert not is_invalid_translation("{count} 曲を読み込む", "Charger {count} morceaux")


def test_has_source_leak_valeur_identique_aux_espaces_pres_nest_pas_une_fuite() -> None:
    assert not has_source_leak("  + {name}", "  + {name}")


def test_sync_locales_forced_key_flagged_even_when_value_differs_from_french(tmp_path, monkeypatch, capsys):
    """`--keys` désigne des clés à retraduire alors que leur valeur n'est pas restée identique au français."""
    import json

    import sync_translations as st

    (tmp_path / "fr.json").write_text(json.dumps({"unit.size_gb": "{value} Go"}), encoding="utf-8")
    (tmp_path / "ja.json").write_text(json.dumps({"unit.size_gb": "{value} ギガ"}), encoding="utf-8")
    monkeypatch.setattr(st, "is_ollama_online", lambda: True)

    st.sync_locales(tmp_path, check_only=True, retranslate_untranslated=True, target_languages=["ja"])
    assert "Parfaitement synchronisé" in capsys.readouterr().out

    st.sync_locales(
        tmp_path,
        check_only=True,
        retranslate_untranslated=True,
        target_languages=["ja"],
        forced_keys=frozenset({"unit.size_gb"}),
    )
    assert "unit.size_gb" in capsys.readouterr().out
