"""Outil d'audit complet de l'internationalisation (i18n) pour AMSO.

Analyse :
1. Doublons de libellés dans fr.json (textes identiques sous plusieurs clés à fusionner).
2. Clés orphelines dans fr.json (clés définies mais jamais appelées dans le code source).
3. Textes potentiellement codés en dur dans amso/ui/ sans appel à tr().
4. Parité et intégrité de l'ensemble des fichiers de langues (fr, en, es, it, de).
"""

from __future__ import annotations

import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# Forcer UTF-8 sur stdout sous Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent
LOCALES_DIR = ROOT / "amso" / "locales"
AMSO_DIR = ROOT / "amso"


def load_json(path: Path) -> dict[str, str]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def audit_duplicate_labels(fr_data: dict[str, str]) -> list[tuple[str, list[str]]]:
    """Trouve les valeurs textuelles françaises identiques partagées par au moins 2 clés distinctes."""
    val_to_keys: dict[str, list[str]] = defaultdict(list)
    for k, v in fr_data.items():
        val = str(v).strip()
        # Ignorer les valeurs très courtes (symboles, séparateurs)
        if len(val) >= 3 and not val.startswith("{"):
            val_to_keys[val].append(k)

    duplicates = [(val, keys) for val, keys in val_to_keys.items() if len(keys) > 1]
    # Trier par nombre de doublons décroissant
    duplicates.sort(key=lambda item: len(item[1]), reverse=True)
    return duplicates


def find_all_code_keys(root_dir: Path) -> set[str]:
    """Extrait toutes les clés littérales appelées avec tr(...) ou présentes dans le code Python."""
    pattern = re.compile(r'tr\(\s*["\']([a-zA-Z0-9_\.]+)["\']')
    found_keys: set[str] = set()

    for py_file in root_dir.glob("**/*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            for m in pattern.finditer(content):
                found_keys.add(m.group(1))
            # On cherche aussi les tuples de colonnes UNIFIED_TRACK_COLUMNS qui utilisent "table.col_..."
            for col_match in re.findall(r'["\'](table\.col_[a-zA-Z0-9_]+)["\']', content):
                found_keys.add(col_match)
        except Exception:
            pass

    return found_keys


def audit_hardcoded_strings(ui_dir: Path) -> list[tuple[str, int, str]]:
    """Détecte les instanciations de widgets avec des chaînes françaises ou anglaises codées en dur."""
    findings: list[tuple[str, int, str]] = []
    # Widgets ou méthodes recevant souvent du texte UI
    ui_calls = {"QLabel", "QPushButton", "setToolTip", "setWindowTitle", "setHeaderLabels"}

    for py_file in ui_dir.glob("**/*.py"):
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except Exception:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr

                if func_name in ui_calls and node.args:
                    first_arg = node.args[0]
                    # Si le premier argument est un littéral de chaîne directe non vide
                    if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                        val = first_arg.value.strip()
                        # Ignorer les noms d'objets courts, QSS, émojis seuls ou séparateurs
                        if len(val) > 3 and not val.startswith(("#", "Q", "{", "color", "border", "font")):
                            rel_path = py_file.relative_to(ROOT)
                            findings.append((str(rel_path), node.lineno, val))
    return findings


def audit_locales_parity() -> dict[str, dict[str, int]]:
    """Vérifie la parité de chaque fichier de langue avec fr.json."""
    fr_data = load_json(LOCALES_DIR / "fr.json")
    fr_keys = set(fr_data.keys())
    results: dict[str, dict[str, int]] = {}

    for json_file in sorted(LOCALES_DIR.glob("*.json")):
        lang = json_file.stem
        data = load_json(json_file)
        cur_keys = set(data.keys())
        missing = len(fr_keys - cur_keys)
        extra = len(cur_keys - fr_keys)
        results[lang] = {"total": len(cur_keys), "missing": missing, "extra": extra}

    return results


def main() -> None:
    print("=" * 70)
    print("      AMSO — Audit et Diagnostic d'Internationalisation (i18n)")
    print("=" * 70)

    fr_json_path = LOCALES_DIR / "fr.json"
    if not fr_json_path.exists():
        print(f"Erreur : fichier introuvable {fr_json_path}")
        sys.exit(1)

    fr_data = load_json(fr_json_path)

    # 1. Parité des fichiers de langues
    print("\n[1/4] Intégrité et parité des fichiers de langues :")
    parity = audit_locales_parity()
    for lang, stats in parity.items():
        status = "✅ Conforme" if stats["missing"] == 0 and stats["extra"] == 0 else "❌ Anomalie"
        print(f"  • {lang}.json : {stats['total']} clés | Manquantes: {stats['missing']} | En trop: {stats['extra']} ({status})")

    # 2. Doublons de libellés dans fr.json
    print("\n[2/4] Libellés identiques dans fr.json (opportunités de fusion) :")
    duplicates = audit_duplicate_labels(fr_data)
    print(f"  Total de libellés partagés par plusieurs clés : {len(duplicates)}")
    for val, keys in duplicates[:15]:  # Afficher les 15 premiers
        print(f"  • Libellé « {val} » utilisé par {len(keys)} clés :")
        for k in keys:
            print(f"      - {k}")
    if len(duplicates) > 15:
        print(f"  ... et {len(duplicates) - 15} autres libellés partagés.")

    # 3. Clés orphelines (dans fr.json mais absentes du code)
    print("\n[3/4] Clés orphelines dans fr.json (inutilisées dans le code Python) :")
    code_keys = find_all_code_keys(AMSO_DIR)
    # Ignorer les clés dynamiques comme quality.*, sync_mode.*, effects.* qui peuvent être formées dynamiquement
    orphan_keys = [
        k for k in fr_data
        if k not in code_keys and not any(k.startswith(pfx) for pfx in ("quality.", "sync_mode.", "effects.", "lang."))
    ]
    print(f"  Clés orphelines potentielles détectées : {len(orphan_keys)}")
    for k in orphan_keys[:15]:
        print(f"  • {k} -> « {fr_data[k]} »")
    if len(orphan_keys) > 15:
        print(f"  ... et {len(orphan_keys) - 15} autres clés orphelines.")

    # 4. Textes potentiellement codés en dur dans l'UI
    print("\n[4/4] Détection de textes potentiellement codés en dur dans amso/ui/ :")
    hardcoded = audit_hardcoded_strings(ROOT / "amso" / "ui")
    print(f"  Occurrences identifiées nécessitant vérification : {len(hardcoded)}")
    for path, line, text in hardcoded[:15]:
        print(f"  • {path}:{line} -> \"{text}\"")
    if len(hardcoded) > 15:
        print(f"  ... et {len(hardcoded) - 15} autres occurrences.")

    print("\n" + "=" * 70)
    print("Conseil : Pour visualiser en temps réel les traductions à l'écran,")
    print("lancez l'application avec : run_debug_i18n.bat (ou --debug-i18n).")
    print("=" * 70)


if __name__ == "__main__":
    main()
