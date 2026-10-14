"""Script de synchronisation des fichiers de traduction sur la base de la VF (fr.json).

Usage:
    python scripts/sync_translations.py [--check-only]

Description:
    Prend fr.json comme fichier de référence (source de vérité).
    Pour chaque autre langue (en, es, it, de, etc.) :
    - Identifie les clés manquantes et les ajoute (avec repli sur en.json ou fr.json).
    - Identifie les clés obsolètes absentes de fr.json et les retire.
    - Réordonne les clés dans le même ordre que fr.json.
    - Formate proprement le JSON (UTF-8, indentation de 2 espaces).
"""

from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
import sys
from typing import Any

# Forcer UTF-8 sur stdout pour éviter les erreurs charmap cp1252 sous Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def get_locales_dir() -> Path:
    project_root = Path(__file__).parent.parent.resolve()
    return project_root / "amso" / "locales"


def load_json(path: Path) -> dict[str, str]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict[str, str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def sync_locales(locales_dir: Path, check_only: bool = False) -> int:
    ref_file = locales_dir / "fr.json"
    if not ref_file.exists():
        print(f"Erreur : Le fichier de référence {ref_file} est introuvable.")
        return 1

    ref_data = load_json(ref_file)
    ref_keys = list(ref_data.keys())

    print("=" * 60)
    print(f"  AMSO — Synchronisation i18n sur la base de la VF (fr.json)")
    print(f"  Répertoire : {locales_dir}")
    print(f"  Nombre de clés dans la référence VF : {len(ref_keys)}")
    print("=" * 60)

    # Récupérer en.json comme premier repli pour les nouvelles clés si disponible
    en_file = locales_dir / "en.json"
    en_data = load_json(en_file) if en_file.exists() else {}

    has_diff = False
    target_files = sorted(locales_dir.glob("*.json"))

    for target_path in target_files:
        if target_path.name == "fr.json":
            continue

        target_lang = target_path.stem
        target_data = load_json(target_path)

        missing_keys = [k for k in ref_keys if k not in target_data]
        obsolete_keys = [k for k in target_data if k not in ref_data]

        print(f"\n[{target_lang}] Analyse de {target_path.name} :")
        if not missing_keys and not obsolete_keys:
            print(f"  [OK] Parfaitement synchronisé ({len(target_data)} clés).")
            continue

        has_diff = True
        if missing_keys:
            print(f"  + {len(missing_keys)} clé(s) manquante(s) : {', '.join(missing_keys[:5])}{'...' if len(missing_keys) > 5 else ''}")
        if obsolete_keys:
            print(f"  - {len(obsolete_keys)} clé(s) obsolète(s) : {', '.join(obsolete_keys[:5])}{'...' if len(obsolete_keys) > 5 else ''}")

        if not check_only:
            # Construction du nouveau dictionnaire dans l'ordre strict de fr.json
            synced_data: dict[str, str] = {}
            for k in ref_keys:
                if k in target_data:
                    synced_data[k] = target_data[k]
                elif k in en_data:
                    # Repli sur l'anglais si existant
                    synced_data[k] = en_data[k]
                else:
                    # Repli sur la VF
                    synced_data[k] = ref_data[k]

            save_json(target_path, synced_data)
            print(f"  -> {target_path.name} mis à jour et aligné sur fr.json.")

    print("\n" + "=" * 60)
    if check_only:
        if has_diff:
            print("  ATTENTION : Des différences ont été détectées (--check-only).")
            return 2
        else:
            print("  SUCCÈS : Tous les fichiers de traduction sont parfaitement alignés.")
            return 0
    else:
        print("  SUCCÈS : Synchronisation terminée avec succès !")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchroniser les fichiers i18n sur fr.json")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Vérifier l'alignement sans modifier les fichiers sur le disque",
    )
    args = parser.parse_args()

    locales_dir = get_locales_dir()
    return sync_locales(locales_dir=locales_dir, check_only=args.check_only)


if __name__ == "__main__":
    sys.exit(main())
