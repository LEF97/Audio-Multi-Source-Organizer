"""Tests de non-régression pour la synchronisation de la documentation multilingue (5 langues)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.check_docs_sync import check_docs


def test_docs_synchronization() -> None:
    """Vérifie que les 15 fichiers de documentation (README, CHANGELOG, ROADMAP) sont synchronisés."""
    project_root = Path(__file__).parent.parent.resolve()
    errors = check_docs(project_root)
    assert not errors, f"Des désynchronisations de documentation ont été détectées : {errors}"


def test_check_docs_sync_cli() -> None:
    """Vérifie que le script CLI scripts/check_docs_sync.py s'exécute avec succès (code retour 0)."""
    project_root = Path(__file__).parent.parent.resolve()
    script_path = project_root / "scripts" / "check_docs_sync.py"
    res = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        cwd=str(project_root),
    )
    assert res.returncode == 0, f"Le script a échoué avec le code {res.returncode}:\n{res.stdout}\n{res.stderr}"
