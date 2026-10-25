"""Script de validation unifiée de la Quality Gate d'AMSO.

Exécute successivement :
1. Vérification du formatage avec Ruff
2. Vérification des règles de lint avec Ruff
3. Contrôle strict des types avec Mypy
4. Contrôle des tailles de fichiers et de fonctions
5. Exécution de la suite de tests avec Pytest
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

# Assurer la compatibilité d'affichage UTF-8 sur terminal Windows (évite les erreurs cp1252)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
PYTHON = sys.executable


def run_step(step_num: int, total_steps: int, title: str, cmd: list[str]) -> bool:
    """Exécute une étape et affiche son statut."""
    print(f"\n[{step_num}/{total_steps}] {title}...")
    start = time.perf_counter()
    res = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace")
    duration = time.perf_counter() - start

    stdout_str = (res.stdout or "").strip()
    stderr_str = (res.stderr or "").strip()

    if res.returncode == 0:
        print(f"  [OK] Succès ({duration:.1f}s)")
        if stdout_str:
            # Affiche un extrait si informatif (ex: check_file_sizes)
            lines = stdout_str.splitlines()
            if len(lines) <= 6:
                for line in lines:
                    print(f"       {line}")
        return True

    print(f"  [FAIL] ÉCHEC ({duration:.1f}s)")
    if stdout_str:
        print("--- Sortie standard ---")
        print(stdout_str[:2000])
    if stderr_str:
        print("--- Erreurs ---")
        print(stderr_str[:2000])
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Harnais de vérification qualité AMSO.")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Exécute la suite complète de tests pytest (au lieu des tests rapides ciblés).",
    )
    args = parser.parse_args()

    print("==================================================")
    print("      AMSO — Harnais de Validation Qualité        ")
    print("==================================================")

    steps: list[tuple[str, list[str]]] = [
        ("Vérification du formatage (Ruff)", [PYTHON, "-m", "ruff", "format", "--check", "amso", "tests"]),
        ("Analyse statique et linter (Ruff)", [PYTHON, "-m", "ruff", "check", "amso", "tests"]),
        ("Vérification du typage (Mypy)", [PYTHON, "-m", "mypy", "amso"]),
        ("Contrôle des tailles de fichiers", [PYTHON, "scripts/check_file_sizes.py"]),
        ("Cohérence de context.md", [PYTHON, "scripts/check_context.py"]),
    ]

    if args.all:
        steps.append(("Tests unitaires complets (Pytest)", [PYTHON, "-m", "pytest", "-q", "tests/"]))
    else:
        steps.append(
            (
                "Tests unitaires rapides (Pytest)",
                [PYTHON, "-m", "pytest", "-q", "tests/test_player.py", "tests/test_ui.py"],
            )
        )

    all_passed = True
    for i, (title, cmd) in enumerate(steps, start=1):
        success = run_step(i, len(steps), title, cmd)
        if not success:
            all_passed = False
            break

    print("\n==================================================")
    if all_passed:
        print("  >>> QUALITY GATE STATUS: PASSED (AMSO Conforme) <<<")
        print("==================================================")
        return 0

    print("  >>> QUALITY GATE STATUS: FAILED <<<")
    print("==================================================")
    return 1


if __name__ == "__main__":
    sys.exit(main())
