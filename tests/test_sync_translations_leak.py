"""Le script de synchronisation repère les traductions qui reprennent le français (« français (romaji) »)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from sync_translations import has_source_leak, needs_retranslation


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
