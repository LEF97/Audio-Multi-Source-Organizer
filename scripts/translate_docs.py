"""Traduction de la documentation (README, CHANGELOG, ROADMAP) avec Ollama et gestion de la navigation entre langues.

Usage:
    python scripts/translate_docs.py [--ollama [MODELE]] [--docs README CHANGELOG ROADMAP] [--lang CODE ...]
                                     [--nav-only] [--force]

Règle : seules `fr` (source de vérité, `*.fr.md`) et `en` (traduite depuis `fr` par l'assistant, skill `docs-sync`) ne passent
pas par ce script. TOUTES les autres langues sont traduites par Ollama :
- README : 41 langues (es, de, it, … dans `docs/i18n/README.<code>.md`) ;
- CHANGELOG et ROADMAP : es, de, it (fichiers à la racine).
La traduction se fait par blocs Markdown (code, HTML, badges et titre du projet restent intacts). Chaque bloc traduit est
validé (mêmes liens, mêmes numéros de version et dates, même nombre de lignes, mêmes marqueurs de liste/titre/tableau),
réessayé une fois, puis conservé en français s'il reste invalide. Les blocs déjà traduits sont mémorisés
(`docs/i18n/.docs_cache.json`) : seuls les blocs modifiés sont retraduits.
Sans `--ollama` (ou avec `--nav-only`), seuls les sélecteurs de langue sont régénérés dans les fichiers existants.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from amso.core.i18n import SUPPORTED_LANGUAGES  # noqa: E402
from scripts.sync_translations import LANG_NAMES, is_ollama_online  # noqa: E402

SOURCE_LANG = "fr"
DOCS = ("README", "CHANGELOG", "ROADMAP")
DOC_LANGS = ["fr", "en", "es", "de", "it"]  # langues des CHANGELOG et ROADMAP
ROOT_README = {"fr": "README.fr.md", "en": "README.md"}
I18N_DIR = ROOT / "docs" / "i18n"
CACHE_FILE = I18N_DIR / ".docs_cache.json"
MANUAL_LANGS = {"fr", "en"}  # jamais traduits par Ollama (fr = source, en = assistant depuis fr)
MAIN_LANGS = ["fr", "en", "es", "de", "it", "pt", "zh_cn", "ja", "ru", "ar"]  # affichés en permanence
DEFAULT_MODEL = "gemma4:latest"  # meilleur que mistral sur ja/ar/zh/ko (test du 2026-10-25)
MAX_BLOCK_LINES = 10  # au-delà, le bloc est traduit par tranches de CHUNK_LINES lignes
CHUNK_LINES = 8
NAV_START = "<!-- lang-nav:start -->"
NAV_END = "<!-- lang-nav:end -->"
PRESERVED_NAMES = (
    "AMSO, VLC, Python, PySide6, GitHub, Ollama, Spotify, Deezer, Google Drive, Amazon Music, itch.io, Ko-fi"
)

Translator = Callable[[str, str], str]


def readme_path(lang: str) -> Path:
    """Chemin du README d'une langue (racine pour fr/en, docs/i18n/ pour les autres)."""
    if lang in ROOT_README:
        return ROOT / ROOT_README[lang]
    return I18N_DIR / f"README.{lang}.md"


def doc_path(doc: str, lang: str) -> Path:
    """Chemin d'un document (README, CHANGELOG ou ROADMAP) dans une langue."""
    if doc == "README":
        return readme_path(lang)
    return ROOT / (f"{doc}.md" if lang == "en" else f"{doc}.{lang}.md")


def doc_languages(doc: str) -> list[str]:
    """Langues dans lesquelles `doc` existe."""
    return list(SUPPORTED_LANGUAGES) if doc == "README" else DOC_LANGS


def generated_languages(doc: str = "README") -> list[str]:
    """Langues de `doc` traduites par Ollama (toutes sauf fr et en)."""
    return [lang for lang in doc_languages(doc) if lang not in MANUAL_LANGS]


def available_languages() -> list[str]:
    """Codes des langues dont le README existe, dans l'ordre de SUPPORTED_LANGUAGES."""
    return [lang for lang in SUPPORTED_LANGUAGES if readme_path(lang).exists()]


def _write(path: Path, text: str) -> None:
    """Écrit en UTF-8 sans conversion des fins de ligne."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


# --- Navigation entre langues -------------------------------------------------------------------


def _entry(current: str, target: str) -> str:
    name = SUPPORTED_LANGUAGES[target]
    if target == current:
        return f"<b>{name}</b>"
    rel = os.path.relpath(readme_path(target), readme_path(current).parent).replace("\\", "/")
    return f'<a href="{rel}">{name}</a>'


def build_nav(current: str, available: list[str]) -> str:
    """Bloc de navigation README : 10 langues principales + bloc repliable pour les autres langues disponibles."""
    main = [lang for lang in MAIN_LANGS if lang in available]
    others = [lang for lang in SUPPORTED_LANGUAGES if lang not in MAIN_LANGS and lang in available]
    lines = [NAV_START, '<p align="right">', "  " + " • ".join(_entry(current, lang) for lang in main), "</p>"]
    if others:
        opened = " open" if current in others else ""
        lines += [
            f"<details{opened}>",
            f"<summary>🌐 Other languages / Autres langues ({len(others)})</summary>",
            '<p align="right">',
            "  " + " • ".join(_entry(current, lang) for lang in others),
            "</p>",
            "</details>",
        ]
    lines.append(NAV_END)
    return "\n".join(lines)


def build_doc_nav(doc: str, current: str) -> str:
    """Barre de navigation des CHANGELOG et ROADMAP (les 5 langues de DOC_LANGS)."""
    entries = [
        f"<b>{SUPPORTED_LANGUAGES[lang]}</b>"
        if lang == current
        else f'<a href="{doc_path(doc, lang).name}">{SUPPORTED_LANGUAGES[lang]}</a>'
        for lang in DOC_LANGS
    ]
    return '<p align="right">\n  ' + " • ".join(entries) + "\n</p>"


def apply_nav(text: str, nav: str) -> str:
    """Remplace le bloc entre marqueurs, ou à défaut le premier `<p align="right">…</p>`, par `nav`."""
    marked = re.compile(re.escape(NAV_START) + r".*?" + re.escape(NAV_END), re.DOTALL)
    legacy = re.compile(r'<p align="right">.*?</p>', re.DOTALL)
    pattern = marked if marked.search(text) else legacy
    return pattern.sub(lambda _m: nav, text, count=1)


def update_navigation() -> list[str]:
    """Régénère les sélecteurs de langue des README, CHANGELOG et ROADMAP existants ; retourne les fichiers modifiés."""
    available = available_languages()
    targets = [(readme_path(lang), build_nav(lang, available)) for lang in available]
    for doc in ("CHANGELOG", "ROADMAP"):
        targets += [
            (doc_path(doc, lang), build_doc_nav(doc, lang)) for lang in DOC_LANGS if doc_path(doc, lang).exists()
        ]
    changed: list[str] = []
    for path, nav in targets:
        old = path.read_text(encoding="utf-8")
        new = apply_nav(old, nav)
        if new != old:
            _write(path, new)
            changed.append(path.relative_to(ROOT).as_posix())
    return changed


# --- Découpage et validation Markdown -----------------------------------------------------------

_URL_PATTERNS = (re.compile(r"\]\(([^)\s]+)"), re.compile(r'(?:src|href)="([^"]+)"'))
_LINK_PATTERNS = (re.compile(r"(\]\()([^)\s]+)"), re.compile(r'((?:src|href)=")([^"]+)'))
_MARKER = re.compile(r"^\s*(#{1,6}(?=\s)|[-*+](?=\s)|\d+\.(?=\s)|>|\|)")
_TOKENS = re.compile(r"\d+\.\d+\.\d+(?:-dev)?|\d{4}-\d{2}-\d{2}")


def rebase_links(text: str, prefix: str) -> str:
    """Préfixe les liens relatifs (ex. `../../` pour un fichier placé dans docs/i18n/)."""

    def fix(match: re.Match[str]) -> str:
        url = match.group(2)
        if re.match(r"^(?:[a-z][a-z0-9+.-]*:|#|/)", url, re.IGNORECASE):
            return match.group(0)
        return match.group(1) + prefix + url

    for pattern in _LINK_PATTERNS:
        text = pattern.sub(fix, text)
    return text


def split_blocks(text: str) -> list[tuple[bool, list[str]]]:
    """Découpe en groupes (est_vide, lignes) ; la concaténation des lignes redonne exactement le texte."""
    groups: list[tuple[bool, list[str]]] = []
    in_fence = False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        blank = not in_fence and not line.strip()
        if groups and groups[-1][0] == blank:
            groups[-1][1].append(line)
        else:
            groups.append((blank, [line]))
    return groups


def is_translatable(lines: list[str]) -> bool:
    """Faux pour le code, le HTML, les badges, les images, les marqueurs de navigation et le titre du projet."""
    first = lines[0].lstrip()
    if first.startswith(("```", "<", "[![", "![", "---")):
        return False
    if first.startswith("# ") and "(AMSO)" in first:
        return False
    return re.search(r"[^\W\d_]{3,}", "\n".join(lines)) is not None


def _urls(text: str) -> list[str]:
    return sorted(url for pattern in _URL_PATTERNS for url in pattern.findall(text))


def _markers(text: str) -> list[str]:
    return [m.group(1) if (m := _MARKER.match(line)) else "" for line in text.split("\n")]


def validate(source: str, output: str) -> bool:
    """Mêmes lignes, marqueurs de structure, liens, numéros de version/dates et séparateurs de tableau."""
    src_lines, out_lines = source.split("\n"), output.split("\n")
    return (
        len(src_lines) == len(out_lines)
        and _markers(source) == _markers(output)
        and _urls(source) == _urls(output)
        and sorted(_TOKENS.findall(source)) == sorted(_TOKENS.findall(output))
        and [ln.count("|") for ln in src_lines] == [ln.count("|") for ln in out_lines]
    )


def chunks(lines: list[str]) -> list[list[str]]:
    """Un bloc court reste entier ; un bloc long est découpé en tranches pour fiabiliser la traduction."""
    if len(lines) <= MAX_BLOCK_LINES:
        return [lines]
    return [lines[i : i + CHUNK_LINES] for i in range(0, len(lines), CHUNK_LINES)]


# --- Traduction ---------------------------------------------------------------------------------


def restore_quote_markers(source: str, output: str) -> str:
    """Réinsère le `>` des citations Markdown que le modèle a retiré (même nombre de lignes requis)."""
    src_lines, out_lines = source.split("\n"), output.split("\n")
    if len(src_lines) != len(out_lines):
        return output
    fixed = [
        f"> {out.lstrip()}" if src.lstrip().startswith(">") and not out.lstrip().startswith(">") else out
        for src, out in zip(src_lines, out_lines, strict=True)
    ]
    return "\n".join(fixed)


def ollama_translate(model: str) -> Translator:
    """Traducteur de blocs Markdown (français -> langue cible) via l'API locale d'Ollama."""

    def translate(block: str, lang: str) -> str:
        prompt = (
            f"Translate this Markdown fragment from French to {LANG_NAMES.get(lang, lang)}.\n"
            "Rules: keep the Markdown syntax, line breaks, URLs, file names, emojis, HTML tags, version numbers, dates "
            f"and inline code exactly as they are; never translate these names: {PRESERVED_NAMES}. "
            "Return ONLY the translated fragment, without any comment.\n\n" + block
        )
        payload = json.dumps(
            {"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.2}}
        ).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate", data=payload, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=180) as res:
            out = str(json.loads(res.read().decode("utf-8")).get("response", "")).strip("\n")
        if "</think>" in out:
            out = out.split("</think>")[-1].strip("\n")
        if out.startswith("```") and not block.startswith("```"):
            out = "\n".join(out.split("\n")[1:-1]) if out.rstrip().endswith("```") else out
        return restore_quote_markers(block, out)

    return translate


def _translate_chunk(block: str, lang: str, translate: Translator, cache: dict[str, str]) -> str | None:
    """Traduit un fragment (cache, 2 essais, validation) ; None si aucune traduction valide."""
    key = hashlib.sha256(f"{lang}\0{block}".encode()).hexdigest()
    if key in cache:
        return cache[key]
    for _attempt in range(2):
        try:
            candidate = translate(block, lang)
        except Exception as exc:
            print(f"    [!] Ollama : {exc}")
            continue
        if validate(block, candidate):
            cache[key] = candidate
            return candidate
    return None


def translate_text(source: str, lang: str, translate: Translator, cache: dict[str, str]) -> tuple[str, int]:
    """Traduit `source` bloc par bloc ; retourne (texte, nombre de fragments restés en français)."""
    failures = 0
    out_lines: list[str] = []
    for blank, lines in split_blocks(source):
        if blank or not is_translatable(lines):
            out_lines.extend(lines)
            continue
        for part in chunks(lines):
            block = "\n".join(part)
            result = _translate_chunk(block, lang, translate, cache) if is_translatable(part) else block
            if result is None:
                failures += 1
                result = block
            out_lines.extend(result.split("\n"))
    return "\n".join(out_lines), failures


def finalize(doc: str, lang: str, text: str) -> str:
    """Adapte les liens d'un document généré : chemins relatifs (README) et documents associés dans la même langue."""
    if doc == "README":
        text = rebase_links(text, "../../")
    for other in ("CHANGELOG", "ROADMAP"):
        target = doc_path(other, lang if lang in DOC_LANGS else "en").name
        text = text.replace(f"{other}.fr.md", target)
    if doc != "README":
        text = text.replace("README.fr.md", os.path.relpath(readme_path(lang), ROOT).replace("\\", "/"))
    return text


def run(docs: list[str], langs: list[str] | None, translate: Translator | None, force: bool) -> int:
    """Traduit les documents et langues demandés (si `translate`), puis régénère la navigation. 0 si tout est valide."""
    cache: dict[str, str] = json.loads(CACHE_FILE.read_text("utf-8")) if CACHE_FILE.exists() else {}
    total_failures = 0
    for doc in docs if translate else []:
        source = doc_path(doc, SOURCE_LANG).read_text(encoding="utf-8")
        for lang in [lang for lang in generated_languages(doc) if langs is None or lang in langs]:
            print(f"[{doc} {lang}] {SUPPORTED_LANGUAGES[lang]}...")
            local_cache: dict[str, str] = {} if force else cache
            text, failures = translate_text(source, lang, translate, local_cache) if translate else ("", 0)
            cache.update(local_cache)
            _write(doc_path(doc, lang), finalize(doc, lang, text))
            _write(CACHE_FILE, json.dumps(cache, ensure_ascii=False, indent=1, sort_keys=True))
            total_failures += failures
            print(f"    {'OK' if not failures else f'{failures} fragment(s) laissé(s) en français'}")
    changed = update_navigation()
    missing = [lang for lang in generated_languages() if not readme_path(lang).exists()]
    print(f"Navigation mise à jour dans {len(changed)} fichier(s). Langues sans README : {len(missing)}.")
    return 1 if total_failures else 0


def main() -> int:
    """Point d'entrée du script."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--ollama", nargs="?", const=DEFAULT_MODEL, default=None, help=f"Modèle Ollama (défaut : {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--docs", nargs="+", choices=DOCS, default=list(DOCS), help="Documents à traduire (défaut : tous)"
    )
    parser.add_argument("--lang", nargs="+", default=None, help="Code(s) de langue à traiter (défaut : toutes)")
    parser.add_argument("--nav-only", action="store_true", help="Ne régénère que les sélecteurs de langue")
    parser.add_argument("--force", action="store_true", help="Ignore le cache et retraduit tout")
    args = parser.parse_args()

    unknown = [lang for lang in args.lang or [] if lang not in SUPPORTED_LANGUAGES or lang in MANUAL_LANGS]
    if unknown:
        print(f"Langues invalides ou non traduites par Ollama (fr = source, en = assistant) : {', '.join(unknown)}")
        return 2
    translate: Translator | None = None
    if args.ollama and not args.nav_only:
        if not is_ollama_online():
            print("Ollama n'est pas joignable sur http://127.0.0.1:11434 : démarrez-le ou utilisez --nav-only.")
            return 2
        translate = ollama_translate(args.ollama)
    return run(args.docs, args.lang, translate, args.force)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
