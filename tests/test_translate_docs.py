"""Tests de la traduction Markdown par blocs et du sélecteur de langue des README."""

from __future__ import annotations

import pytest

from scripts import translate_docs as tr

SAMPLE = """# Titre (AMSO)

<!-- lang-nav:start -->
<p align="right">x</p>
<!-- lang-nav:end -->

[![Badge](https://img.shields.io/a.svg)](https://example.com)

## Fonctionnalités

| Nom | Statut |
| :--- | :---: |
| Lecteur | OK |

- Premier [lien](CHANGELOG.fr.md)

```bash
pip install -r requirements.txt
```
"""


def test_split_blocks_roundtrip_preserves_text() -> None:
    joined = "\n".join(line for _blank, lines in tr.split_blocks(SAMPLE) for line in lines)
    assert joined == SAMPLE


def test_code_html_badges_and_title_are_not_translatable() -> None:
    blocks = [lines for blank, lines in tr.split_blocks(SAMPLE) if not blank]
    flags = {lines[0]: tr.is_translatable(lines) for lines in blocks}
    assert flags["# Titre (AMSO)"] is False
    assert flags["<!-- lang-nav:start -->"] is False
    assert flags["```bash"] is False
    assert flags["## Fonctionnalités"] is True
    assert flags["| Nom | Statut |"] is True


def test_rebase_links_only_touches_relative_urls() -> None:
    text = '[a](CHANGELOG.fr.md) [b](https://x.io) <img src="screenshots/a.png"> [c](#top)'
    assert tr.rebase_links(text, "../../") == (
        '[a](../../CHANGELOG.fr.md) [b](https://x.io) <img src="../../screenshots/a.png"> [c](#top)'
    )


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        ("- Primero [enlace](CHANGELOG.fr.md)", True),
        ("- Primero [enlace](otro.md)", False),  # lien modifié
        ("Primero [enlace](CHANGELOG.fr.md)", False),  # marqueur de liste perdu
        ("- Primero\n- [enlace](CHANGELOG.fr.md)", False),  # nombre de lignes différent
    ],
)
def test_validate_rejects_structural_changes(candidate: str, expected: bool) -> None:
    assert tr.validate("- Premier [lien](CHANGELOG.fr.md)", candidate) is expected


def test_translate_text_uses_cache_and_falls_back_on_invalid_output() -> None:
    calls: list[str] = []

    def fake(block: str, lang: str) -> str:
        calls.append(block)
        if block.startswith("- Premier"):
            return "- sans lien"  # invalide : le lien a disparu
        return block.replace("Fonctionnalités", "Funciones").replace("Lecteur", "Reproductor")

    cache: dict[str, str] = {}
    text, failures = tr.translate_text(SAMPLE, "es", fake, cache)
    assert failures == 1
    assert "## Funciones" in text and "| Reproductor | OK |" in text
    assert "- Premier [lien](CHANGELOG.fr.md)" in text  # repli sur le français
    assert "pip install -r requirements.txt" in text and "https://img.shields.io/a.svg" in text

    calls.clear()
    tr.translate_text(SAMPLE, "es", fake, cache)
    assert all(block.startswith("- Premier") for block in calls)  # seuls les blocs échoués sont retentés


def test_build_nav_shows_main_languages_and_collapses_others(monkeypatch: pytest.MonkeyPatch) -> None:
    available = ["fr", "en", "es", "de", "it", "pt", "ko", "sw"]
    nav = tr.build_nav("ko", available)
    assert nav.startswith(tr.NAV_START) and nav.endswith(tr.NAV_END)
    main_part, details = nav.split("<details", 1)
    assert "Português" in main_part and "한국어" not in main_part
    assert details.startswith(" open>") and "<b>한국어</b>" in details and "Kiswahili" in details
    assert 'href="../../README.fr.md"' in nav  # fichier de docs/i18n/ -> README racine


def test_apply_nav_replaces_marked_block_then_legacy_header() -> None:
    nav = f"{tr.NAV_START}\nNEW\n{tr.NAV_END}"
    marked = f"a\n{tr.NAV_START}\nold\n{tr.NAV_END}\nb"
    assert tr.apply_nav(marked, nav) == f"a\n{nav}\nb"
    legacy = 'a\n<p align="right">\n  old\n</p>\nb'
    assert tr.apply_nav(legacy, nav) == f"a\n{nav}\nb"


def test_generated_languages_exclude_manual_ones() -> None:
    generated = tr.generated_languages()
    assert not tr.MANUAL_LANGS & set(generated)
    assert len(generated) == len(tr.SUPPORTED_LANGUAGES) - len(tr.MANUAL_LANGS)


def test_restore_quote_markers_readds_stripped_blockquote() -> None:
    source = "> **AMSO** est un lecteur.\n> Deuxième ligne."
    assert (
        tr.restore_quote_markers(source, "**AMSO** is a player.\nSecond line.")
        == "> **AMSO** is a player.\n> Second line."
    )
    assert tr.restore_quote_markers(source, "une seule ligne") == "une seule ligne"


def test_only_fr_and_en_are_not_generated() -> None:
    assert tr.MANUAL_LANGS == {"fr", "en"}
    assert {"es", "de", "it", "ja"} <= set(tr.generated_languages())
    assert tr.generated_languages("CHANGELOG") == ["es", "de", "it"]
    assert tr.generated_languages("ROADMAP") == ["es", "de", "it"]


def test_doc_path_and_doc_nav() -> None:
    assert tr.doc_path("CHANGELOG", "en") == tr.ROOT / "CHANGELOG.md"
    assert tr.doc_path("CHANGELOG", "fr") == tr.ROOT / "CHANGELOG.fr.md"
    assert tr.doc_path("ROADMAP", "es") == tr.I18N_DIR / "ROADMAP.es.md"  # seules fr et en sont à la racine
    nav_es = tr.build_doc_nav("CHANGELOG", "es")
    assert "<b>Español</b>" in nav_es and 'href="../../CHANGELOG.md"' in nav_es and 'href="CHANGELOG.de.md"' in nav_es
    nav_fr = tr.build_doc_nav("CHANGELOG", "fr")
    assert 'href="docs/i18n/CHANGELOG.es.md"' in nav_fr and 'href="CHANGELOG.md"' in nav_fr


def test_validate_rejects_changed_version_or_date() -> None:
    source = "## [0.4.0-dev] - 2026-10-25"
    assert tr.validate(source, "## [0.4.0-dev] - 2026-10-25")
    assert not tr.validate(source, "## [0.4.1-dev] - 2026-10-25")
    assert not tr.validate(source, "## [0.4.0-dev] - 2026-10-26")


def test_long_blocks_are_split_into_chunks() -> None:
    lines = [f"- ligne {i}" for i in range(25)]
    parts = tr.chunks(lines)
    assert [len(p) for p in parts] == [8, 8, 8, 1]
    assert tr.chunks(lines[:10]) == [lines[:10]]


def test_finalize_points_to_documents_of_the_same_language() -> None:
    text = '[c](CHANGELOG.fr.md) [r](ROADMAP.fr.md) <img src="screenshots/a.png">'
    es = tr.finalize("README", "es", text)
    # le README es est dans docs/i18n/, comme CHANGELOG.es.md et ROADMAP.es.md : liens dans le même dossier
    assert "(CHANGELOG.es.md)" in es and "(ROADMAP.es.md)" in es and 'src="../../screenshots/a.png"' in es
    ja = tr.finalize("README", "ja", text)  # langue sans CHANGELOG propre -> anglais
    assert "(../../CHANGELOG.md)" in ja and "(../../ROADMAP.md)" in ja


def test_blocks_with_very_long_lines_are_split_by_size() -> None:
    long_lines = ["- " + "mot " * 125 for _ in range(10)]  # 10 lignes de ~500 caractères
    parts = tr.chunks(long_lines)
    assert len(parts) > 1 and sum(len(p) for p in parts) == 10
    assert all(sum(len(line) + 1 for line in p) <= tr.CHUNK_CHARS + 600 for p in parts)
    assert [line for p in parts for line in p] == long_lines
