"""Contrôle de la taille des fichiers et fonctions Python d'AMSO (cibles de GEMINI.md).

Usage:
    python scripts/check_file_sizes.py [--max-lines 500] [--max-func 60] [--top 10]

Affiche uniquement les fichiers dépassant la limite (sortie courte, économe en jetons).
Code de sortie 0 : informatif (n'échoue pas), sauf avec --strict.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IGNORED = {".venv", "build", "dist", "__pycache__", "scratch", "_work", ".git"}


def iter_sources(base: Path) -> list[Path]:
    """Liste les fichiers .py de `base` hors dossiers ignorés."""
    return sorted(p for p in base.rglob("*.py") if not IGNORED.intersection(p.parts))


def long_functions(path: Path, max_func: int) -> list[tuple[str, int]]:
    """Retourne (nom, longueur) des fonctions dépassant `max_func` lignes."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []
    found: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.end_lineno:
            size = node.end_lineno - node.lineno + 1
            if size > max_func:
                found.append((node.name, size))
    return found


def main() -> int:
    """Point d'entrée du script."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-lines", type=int, default=500)
    parser.add_argument("--max-func", type=int, default=60)
    parser.add_argument("--top", type=int, default=10, help="Nombre de lignes affichées par catégorie")
    parser.add_argument("--strict", action="store_true", help="Code de sortie 1 si dépassement")
    args = parser.parse_args()

    big_files: list[tuple[int, str]] = []
    big_funcs: list[tuple[int, str]] = []
    for path in iter_sources(ROOT / "amso"):
        rel = path.relative_to(ROOT).as_posix()
        n_lines = len(path.read_text(encoding="utf-8").splitlines())
        if n_lines > args.max_lines:
            big_files.append((n_lines, rel))
        big_funcs.extend((size, f"{rel}::{name}") for name, size in long_functions(path, args.max_func))

    big_files.sort(reverse=True)
    big_funcs.sort(reverse=True)
    sys.stdout.write(f"Fichiers > {args.max_lines} lignes : {len(big_files)}\n")
    for n, rel in big_files[: args.top]:
        sys.stdout.write(f"  {n:5d}  {rel}\n")
    sys.stdout.write(f"Fonctions > {args.max_func} lignes : {len(big_funcs)}\n")
    for n, ref in big_funcs[: args.top]:
        sys.stdout.write(f"  {n:5d}  {ref}\n")
    return 1 if args.strict and (big_files or big_funcs) else 0


if __name__ == "__main__":
    raise SystemExit(main())
