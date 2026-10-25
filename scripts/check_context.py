"""Contrôle que context.md décrit bien la structure réelle de amso/.

Usage:
    python scripts/check_context.py

Vérifie que chaque module de amso/core, amso/core/db et amso/services (hors __init__) et chaque
sous-dossier de amso/ui apparaît dans context.md (par son nom de fichier sans extension, ou de dossier).
Code de sortie 1 si un élément manque : mettre à jour context.md (skill `update-context`).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTEXT = ROOT / "context.md"
MODULE_DIRS = ("amso/core", "amso/core/db", "amso/services")
IGNORED_DIRS = {"__pycache__"}


def expected_names() -> list[str]:
    """Noms de modules et de dossiers qui doivent figurer dans context.md."""
    names: list[str] = []
    for rel in MODULE_DIRS:
        names.extend(p.stem for p in sorted((ROOT / rel).glob("*.py")) if p.stem != "__init__")
    ui = ROOT / "amso" / "ui"
    names.extend(p.name for p in sorted(ui.rglob("*")) if p.is_dir() and not IGNORED_DIRS.intersection(p.parts))
    return names


def main() -> int:
    """Point d'entrée du script."""
    text = CONTEXT.read_text(encoding="utf-8")
    missing = [name for name in expected_names() if name not in text]
    if missing:
        sys.stdout.write(f"context.md : {len(missing)} élément(s) absent(s) de la description :\n")
        for name in missing:
            sys.stdout.write(f"  - {name}\n")
        sys.stdout.write("Mettre à jour context.md (skill update-context).\n")
        return 1
    sys.stdout.write("context.md : structure à jour.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
