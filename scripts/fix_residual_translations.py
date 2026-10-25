"""Script de détection et réparation des résidus de traduction dans les 41 langues cibles.

Détecte :
1. Les chaînes restées identiques au français (fr.json) hors termes légitimes.
2. Les chaînes restées identiques à l'anglais (en.json) pour les langues non-anglaises.
3. Les chaînes hybrides contenant des fragments anglais non traduits.
4. Les libellés d'actions partagés (ex: common.refresh) mal traduits.

Traduit les clés détectées via l'IA locale Ollama (mistral:latest) par petits lots JSON.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def log(msg: str = "") -> None:
    print(msg)
    sys.stdout.flush()


LANG_NAMES: dict[str, str] = {
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

# Clés qui doivent légitimement rester identiques
LEGIT_IDENTICAL_KEYS: set[str] = {
    "app.name",
    "app.version",
    "app.tagline_status",
    "app.window_title",
    "table.col_order",
    "table.col_isrc",
    "table.col_id",
    "table.col_playing",
    "table.col_format",
    "table.col_bitrate",
    "table.col_file_hash",
    "settings.col_bitrate",
    "settings.col_format",
    "time.ms_unit",
    "time.sec_unit",
}

# Termes / acronymes invariables
IMMUTABLE_VALUES: set[str] = {
    "AMSO",
    "MP3",
    "FLAC",
    "WAV",
    "AAC",
    "OGG",
    "WMA",
    "M4A",
    "VLC",
    "Hash MD5",
    "ISRC",
    "#",
    "",
}


def is_ollama_online() -> bool:
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/", timeout=2) as res:
            return res.status == 200
    except Exception:
        return False


def load_json(path: Path) -> dict[str, str]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict[str, str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def is_residual_untranslated(
    key: str, val: str, ref_fr: str, ref_en: str, lang_code: str
) -> bool:
    """Détermine si une clé est un résidu non traduit en français ou anglais."""
    if key in LEGIT_IDENTICAL_KEYS:
        return False
    if key.startswith("lang.") or key.startswith("quality."):
        return False
    if val in IMMUTABLE_VALUES or not val.strip():
        return False
    if val.startswith("http"):
        return False

    val_lower = val.lower()
    ref_fr_lower = ref_fr.lower()
    ref_en_lower = ref_en.lower()

    # 1. Résidus d'anglais connus
    if any(frag in val_lower for frag in ("according to", "visual ambience", "sources and synchronization")):
        return True

    # 2. Copie identique du français (insensible à la casse)
    if val_lower == ref_fr_lower:
        clean_word = "".join(c for c in val if c.isalnum()).strip().lower()
        if clean_word not in {"pause", "album", "genre", "solo", "trio", "duo"}:
            return True

    # 3. Copie identique de l'anglais pour une langue non-anglaise (insensible à la casse)
    if lang_code != "en" and val_lower == ref_en_lower:
        clean_word = "".join(c for c in val if c.isalnum()).strip().lower()
        if clean_word not in {"pause", "album", "genre", "solo", "trio", "duo", "ok"}:
            return True

    # 4. Bouton refresh resté en français
    if key == "common.refresh" and "actualiser" in val_lower and lang_code not in ("fr",):
        return True

    # 5. Détection de phrases latines dans des langues non-latines (zh, ja, ko, ru, ar, etc.)
    non_latin_langs = {"zh_cn", "zh_tw", "ja", "ko", "ru", "ar", "he", "el", "bg", "sr", "be"}
    if lang_code in non_latin_langs:
        # Si la chaîne contient des mots anglais typiques de plus de 4 lettres
        english_indicators = ("settings", "player", "sources", "playlist", "library", "search", "browse", "folder")
        if any(w in val_lower.split() for w in english_indicators):
            return True

    return False


def flatten_dict(d: dict, prefix: str = "") -> dict[str, str]:
    """Aplatit récursivement un dictionnaire imbriqué (ex: {'common': {'refresh': '...'}} -> {'common.refresh': '...'})."""
    result: dict[str, str] = {}
    for k, v in d.items():
        full_key = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            result.update(flatten_dict(v, full_key))
        else:
            result[full_key] = str(v)
    return result


def translate_with_ollama(
    items: dict[str, str], target_lang: str, model: str
) -> dict[str, str]:
    """Traduit un dictionnaire de clés via Ollama en forçant le format JSON."""
    lang_name = LANG_NAMES.get(target_lang, target_lang)
    prompt = (
        f"You are a native professional software localization translator for {lang_name}.\n"
        f"Translate the following French UI strings into authentic, native {lang_name}.\n"
        "CRITICAL RULES:\n"
        f"1. Translate EVERYTHING naturally into {lang_name}. DO NOT keep French or English words.\n"
        "2. Do NOT leave technical words in English (e.g., translate 'Visual Ambience', 'Hyperspace', 'Bars', 'Sources and synchronization').\n"
        "3. Keep all placeholders like {title}, {count}, {name}, {path}, {version}, {format}, {size} EXACTLY intact.\n"
        "4. Keep emojis (🔄, 🗑️, 💾, 💖, ☕, ⭐, 🎮, 🔍, 🎵, 📜, ℹ️) intact at their initial positions.\n"
        "5. Return ONLY a valid JSON dictionary mapping the exact same keys to the translated strings.\n\n"
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
        with urllib.request.urlopen(req, timeout=90) as res:
            data = json.loads(res.read().decode("utf-8"))
            resp_text = data.get("response", "").strip()
            parsed = json.loads(resp_text)
            if isinstance(parsed, dict):
                return flatten_dict(parsed)
            log(f"    [!] Réponse Ollama non-dict : {resp_text[:80]}")
            return {}
    except Exception as exc:
        log(f"    [!] Erreur Ollama ({exc})")
        return {}


def repair_locale(
    lang_code: str,
    locales_dir: Path,
    fr_data: dict[str, str],
    en_data: dict[str, str],
    model: str,
    dry_run: bool = False,
) -> int:
    """Répare les clés résiduelles pour une langue donnée."""
    target_path = locales_dir / f"{lang_code}.json"
    if not target_path.exists():
        return 0

    target_data = load_json(target_path)
    to_fix: dict[str, str] = {}

    for k in fr_data.keys():
        val = target_data.get(k, "")
        ref_fr = fr_data[k]
        ref_en = en_data.get(k, ref_fr)
        if is_residual_untranslated(k, val, ref_fr, ref_en, lang_code):
            to_fix[k] = ref_fr

    if not to_fix:
        log(f"  [OK] {lang_code:6s} : 0 résidu détecté.")
        return 0

    log(f"  [..] {lang_code:6s} ({LANG_NAMES.get(lang_code, lang_code)}) : {len(to_fix)} résidus à corriger...")
    if dry_run:
        for k, v in list(to_fix.items())[:5]:
            log(f"       - {k}: {target_data.get(k)!r} -> FR: {v!r}")
        return len(to_fix)

    keys_list = list(to_fix.items())
    batch_size = 25
    fixed_count = 0

    for i in range(0, len(keys_list), batch_size):
        chunk = dict(keys_list[i : i + batch_size])
        translated = translate_with_ollama(chunk, lang_code, model)
        if translated:
            for k, trans_val in translated.items():
                if k in target_data and trans_val.strip():
                    target_data[k] = trans_val
                    fixed_count += 1
                else:
                    log(f"       [?] Clé inconnue retournée par Ollama : {k!r}")
        else:
            log("       [!] Aucune traduction reçue d'Ollama.")

    save_json(target_path, target_data)
    log(f"  [OK] {lang_code:6s} : {fixed_count}/{len(to_fix)} clés mises à jour avec succès.")
    return fixed_count


def main() -> int:
    parser = argparse.ArgumentParser(description="Réparation des résidus de traduction.")
    parser.add_argument("--model", default="mistral:latest", help="Modèle Ollama (défaut: mistral:latest)")
    parser.add_argument("--lang", help="Cibler une seule langue (ex: zh_cn, de, ja)")
    parser.add_argument("--dry-run", action="store_true", help="Audit sans écriture")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.resolve()
    locales_dir = project_root / "amso" / "locales"

    fr_data = load_json(locales_dir / "fr.json")
    en_data = load_json(locales_dir / "en.json")

    log("=" * 65)
    log("  AMSO — Réparation ciblée des résidus de traduction")
    log("=" * 65)

    if not args.dry_run and not is_ollama_online():
        log("[!] Le serveur local Ollama n'est pas joignable sur http://127.0.0.1:11434.")
        log("    Veuillez démarrer Ollama avant de relancer.")
        return 1

    langs_to_process = [args.lang.strip().lower()] if args.lang else sorted(LANG_NAMES.keys())

    total_fixed = 0
    for code in langs_to_process:
        if code in ("fr", "en"):
            continue
        count = repair_locale(code, locales_dir, fr_data, en_data, args.model, dry_run=args.dry_run)
        total_fixed += count

    log("-" * 65)
    log(f"Terminé. Total des clés traitées : {total_fixed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
