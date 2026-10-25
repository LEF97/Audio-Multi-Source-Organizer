"""Script de synchronisation des fichiers de traduction sur la base de la VF (fr.json).

Usage:
    python scripts/sync_translations.py [--check-only] [--ollama [MODELE]] [--retranslate-untranslated] [--lang CODE]

Description:
    Prend fr.json comme fichier de référence (source de vérité).
    Pour chaque langue supportée (en, es, it, de, pt, ja, ru, etc.) :
    - Crée le fichier de langue s'il n'existe pas encore.
    - Identifie les clés manquantes et les ajoute.
    - Si --retranslate-untranslated est activé (ou via Ollama), identifie les textes restés en français
      et les traduit vers la langue cible par lots JSON rapides via l'IA locale (Ollama).
    - Sinon (mode classique), applique le repli standard (en.json ou fr.json).
    - Identifie les clés obsolètes absentes de fr.json et les retire.
    - Réordonne les clés dans le même ordre que fr.json.
    - Formate proprement le JSON (UTF-8, indentation de 2 espaces).
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Forcer UTF-8 sur stdout pour éviter les erreurs charmap cp1252 sous Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def log(msg: str = "") -> None:
    """Affiche un message et force le vidage du tampon stdout."""
    print(msg)
    sys.stdout.flush()


# Noms des langues en anglais pour les instructions de prompt vers Ollama
LANG_NAMES: dict[str, str] = {
    "en": "English",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ja": "Japanese",
    "ru": "Russian",
    "pl": "Polish",
    "tr": "Turkish",
    "nl": "Dutch",
    "sv": "Swedish",
    "id": "Indonesian",
    "bg": "Bulgarian",
    "sr": "Serbian",
    "be": "Belarusian",
    "el": "Greek",
    "ca": "Catalan",
    "eu": "Basque",
    "gl": "Galician",
    "cs": "Czech",
    "sk": "Slovak",
    "hu": "Hungarian",
    "hr": "Croatian",
    "sl": "Slovenian",
    "bs": "Bosnian",
    "et": "Estonian",
    "lv": "Latvian",
    "lt": "Lithuanian",
    "no": "Norwegian",
    "da": "Danish",
    "fi": "Finnish",
    "is": "Icelandic",
    "ms": "Malay",
    "tl": "Tagalog",
    "sw": "Swahili",
    "eo": "Esperanto",
    "zh_cn": "Simplified Chinese",
    "zh_tw": "Traditional Chinese",
    "ko": "Korean",
    "ar": "Arabic",
    "he": "Hebrew",
    "vi": "Vietnamese",
}

COMMON_IDENTICAL_TERMS = {
    "album",
    "genre",
    "format",
    "sources",
    "source",
    "audio",
    "isrc",
    "radio",
    "pause",
    "solo",
    "trio",
    "duo",
    "remix",
    "version",
}


def get_locales_dir() -> Path:
    project_root = Path(__file__).parent.parent.resolve()
    return project_root / "amso" / "locales"


def load_json(path: Path) -> dict[str, str]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict[str, str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def is_ollama_online() -> bool:
    """Vérifie si le serveur local Ollama est joignable."""
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/", timeout=2) as res:
            return res.status == 200
    except Exception:
        return False


def is_untranslated(key: str, val: str, ref_val: str, target_lang: str) -> bool:
    """Détecte si une chaîne est restée en français par défaut au lieu d'être traduite."""
    if target_lang == "fr":
        return False
    if val != ref_val:
        return False
    if val.startswith("http") or not val.strip():
        return False
    if key in ("app.name", "app.window_title", "dialog.about_app_name", "app.version"):
        return False
    if key.startswith("quality.") and "{" in val:
        return False
    if key in ("sidebar.nav_blind_test", "dialog.about_btn_sponsors"):
        return False

    clean = "".join(c for c in val if c.isalnum() or c.isspace()).strip().lower()
    if clean in COMMON_IDENTICAL_TERMS:
        return False

    return len(val) >= 4


def translate_batch_with_ollama(
    items: dict[str, str], target_lang: str, model: str
) -> dict[str, str]:
    """Traduit un lot de chaînes en une seule requête vers Ollama en mode JSON structuré."""
    lang_name = LANG_NAMES.get(target_lang, target_lang)
    prompt = (
        f"You are a professional software localization translator for audio/music player applications.\n"
        f"Translate the values of the following JSON dictionary from French to {lang_name}.\n"
        "Strict rules:\n"
        "1. Return ONLY a valid JSON dictionary mapping the exact same keys to their translations.\n"
        "2. Keep all placeholders like {title}, {count}, {name}, {path}, {version}, {format}, {time}, {seconds}, {bitrate} EXACTLY intact.\n"
        "3. Keep any emojis or leading symbols (e.g. 🔄, 🗑️, 💾, ⚡, ✓, •, 👍, 💖, 🌐, 🎵, 📁, 📜, ⚙️, 📊) exactly at their position.\n"
        "4. Do not include markdown code blocks, prefixes or explanations.\n\n"
        + json.dumps(items, ensure_ascii=False)
    )
    payload = json.dumps(
        {"model": model, "prompt": prompt, "stream": False, "format": "json"}
    ).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            data = json.loads(res.read().decode("utf-8"))
            resp_text = data.get("response", "").strip()
            parsed = json.loads(resp_text)
            if isinstance(parsed, dict):
                return {str(k): str(v) for k, v in parsed.items()}
            return {}
    except Exception as exc:
        log(f"    [!] Erreur Ollama par lot ({exc}), repli standard.")
        return {}


def sync_locales(
    locales_dir: Path,
    check_only: bool = False,
    ollama_model: str | None = None,
    retranslate_untranslated: bool = False,
    target_languages: list[str] | None = None,
) -> int:
    ref_file = locales_dir / "fr.json"
    if not ref_file.exists():
        log(f"Erreur : Le fichier de référence {ref_file} est introuvable.")
        return 1

    ref_data = load_json(ref_file)
    ref_keys = list(ref_data.keys())

    # Importer SUPPORTED_LANGUAGES depuis amso.core.i18n si possible
    try:
        from amso.core.i18n import SUPPORTED_LANGUAGES

        all_languages = [c for c in SUPPORTED_LANGUAGES.keys() if c != "fr"]
    except Exception:
        all_languages = [c for c in LANG_NAMES.keys() if c != "fr"]

    if target_languages:
        # Filtrer sur les langues demandées
        selected_langs = [c.strip().lower() for c in target_languages if c.strip().lower() != "fr"]
    else:
        selected_langs = all_languages

    log("=" * 65)
    log("  AMSO — Synchronisation i18n sur la base de la VF (fr.json)")
    if ollama_model:
        log(f"  Mode : IA Locale Ollama par lots rapides (Modèle : {ollama_model})")
        if retranslate_untranslated:
            log("  Option : Retraduction active des textes restés en français")
    else:
        log("  Mode : Classique (Repli standard instantané)")
    log(f"  Répertoire : {locales_dir}")
    log(f"  Nombre de clés dans la référence VF : {len(ref_keys)}")
    log(f"  Nombre de langues cibles à traiter : {len(selected_langs)}")
    log("=" * 65)

    if ollama_model and not check_only:
        if not is_ollama_online():
            log("\n[AVERTISSEMENT] Ollama n'est pas joignable sur http://127.0.0.1:11434.")
            log("                Bascule automatique en mode repli classique.\n")
            ollama_model = None

    en_file = locales_dir / "en.json"
    en_data = load_json(en_file) if en_file.exists() else {}

    has_diff = False

    for target_lang in selected_langs:
        target_path = locales_dir / f"{target_lang}.json"
        if not target_path.exists():
            target_data: dict[str, str] = {}
        else:
            target_data = load_json(target_path)

        missing_keys = [k for k in ref_keys if k not in target_data]
        obsolete_keys = [k for k in target_data if k not in ref_data]
        untranslated_keys = [
            k for k in ref_keys
            if k in target_data and is_untranslated(k, target_data[k], ref_data[k], target_lang)
        ]

        log(f"\n[{target_lang}] Analyse de {target_path.name} ({LANG_NAMES.get(target_lang, target_lang)}) :")
        if not missing_keys and not obsolete_keys and not (retranslate_untranslated and untranslated_keys):
            log(f"  [OK] Parfaitement synchronisé ({len(target_data)} clés).")
            continue

        has_diff = True
        if missing_keys:
            log(
                f"  + {len(missing_keys)} clé(s) manquante(s) : {', '.join(missing_keys[:5])}{'...' if len(missing_keys) > 5 else ''}"
            )
        if untranslated_keys and retranslate_untranslated:
            log(
                f"  ~ {len(untranslated_keys)} texte(s) resté(s) en français à traduire : {', '.join(untranslated_keys[:5])}{'...' if len(untranslated_keys) > 5 else ''}"
            )
        if obsolete_keys:
            log(
                f"  - {len(obsolete_keys)} clé(s) obsolète(s) : {', '.join(obsolete_keys[:5])}{'...' if len(obsolete_keys) > 5 else ''}"
            )

        if not check_only:
            keys_to_translate = set(missing_keys)
            if retranslate_untranslated and ollama_model:
                keys_to_translate.update(untranslated_keys)

            translated_results: dict[str, str] = {}
            keys_list = [k for k in ref_keys if k in keys_to_translate]

            if ollama_model and keys_list:
                batch_size = 25
                total_batches = (len(keys_list) + batch_size - 1) // batch_size
                for b_idx in range(0, len(keys_list), batch_size):
                    chunk_keys = keys_list[b_idx : b_idx + batch_size]
                    chunk_dict = {k: ref_data[k] for k in chunk_keys}
                    batch_num = (b_idx // batch_size) + 1
                    log(
                        f"    -> Lot {batch_num}/{total_batches} ({len(chunk_keys)} clés en cours via {ollama_model})..."
                    )
                    batch_res = translate_batch_with_ollama(chunk_dict, target_lang, ollama_model)
                    translated_results.update(batch_res)

            synced_data: dict[str, str] = {}
            for k in ref_keys:
                if k in translated_results and translated_results[k]:
                    synced_data[k] = translated_results[k]
                elif k in target_data and k not in keys_to_translate:
                    synced_data[k] = target_data[k]
                elif k in en_data and en_data[k]:
                    synced_data[k] = en_data[k]
                else:
                    synced_data[k] = ref_data[k]

            save_json(target_path, synced_data)
            log(f"  -> {target_path.name} mis à jour et aligné sur fr.json.")

    log("\n" + "=" * 65)
    if check_only:
        if has_diff:
            log("  ATTENTION : Des différences ont été détectées (--check-only).")
            return 2
        else:
            log("  SUCCÈS : Tous les fichiers de traduction sont parfaitement alignés.")
            return 0
    else:
        log("  SUCCÈS : Synchronisation terminée avec succès !")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchroniser les fichiers i18n sur fr.json")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Vérifier l'alignement sans modifier les fichiers sur le disque",
    )
    parser.add_argument(
        "--ollama",
        nargs="?",
        const="mistral:latest",
        default=None,
        help="Traduire les clés avec Ollama (défaut : mistral:latest)",
    )
    parser.add_argument(
        "--retranslate-untranslated",
        action="store_true",
        help="Traduire également les clés dont la valeur est restée identique au français",
    )
    parser.add_argument(
        "--lang",
        nargs="+",
        default=None,
        help="Code(s) de langue(s) spécifique(s) à traiter (ex: --lang pt ja ru)",
    )
    args = parser.parse_args()

    locales_dir = get_locales_dir()
    return sync_locales(
        locales_dir=locales_dir,
        check_only=args.check_only,
        ollama_model=args.ollama,
        retranslate_untranslated=args.retranslate_untranslated or (args.ollama is not None),
        target_languages=args.lang,
    )


if __name__ == "__main__":
    sys.exit(main())
