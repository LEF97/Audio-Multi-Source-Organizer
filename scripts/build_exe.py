"""Script d'automatisation de la compilation de l'exécutable AMSO avec PyInstaller."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


def build(onefile: bool = False) -> int:
    """Compile l'application AMSO en exécutable natif Windows."""
    project_root = Path(__file__).parent.parent.resolve()
    main_py = project_root / "main.py"
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"

    print("=" * 60)
    print("  AMSO — Compilation de l'exécutable Windows (.exe)")
    print(f"  Mode : {'Fichier unique portable (--onefile)' if onefile else 'Dossier optimisé (--onedir)'}")
    print("=" * 60)

    # Commande PyInstaller
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=AMSO",
        "--windowed",       # Pas de console noire en arrière-plan
        "--noconfirm",      # Écrase les builds précédents sans demander
        "--clean",          # Nettoie les caches de compilation
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        # Ajouter le package amso pour garantir que tous les sous-modules sont inclus
        f"--paths={project_root}",
        "--hidden-import=amso.core.database",
        "--hidden-import=amso.core.metadata",
        "--hidden-import=amso.core.scanner",
        "--hidden-import=amso.ui.models",
        "--hidden-import=amso.ui.theme",
        "--hidden-import=amso.ui.workers",
        "--hidden-import=amso.ui.views.main_window",
        "--hidden-import=sqlite3",
        "--hidden-import=mutagen",
        "--hidden-import=dotenv",
    ]

    if onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    cmd.append(str(main_py))

    print(f"\nExécution de la compilation PyInstaller...")
    res = subprocess.run(cmd, cwd=str(project_root))
    if res.returncode == 0:
        print("\n" + "=" * 60)
        print("  SUCCÈS : Compilation terminée avec succès !")
        if onefile:
            print(f"  Exécutable généré : {dist_dir / 'AMSO.exe'}")
        else:
            print(f"  Exécutable généré : {dist_dir / 'AMSO' / 'AMSO.exe'}")
        print("=" * 60)
    else:
        print("\n" + "!" * 60)
        print(f"  ERREUR : La compilation a échoué (code {res.returncode}).")
        print("!" * 60)

    return res.returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compiler AMSO en .exe avec PyInstaller")
    parser.add_argument("--onefile", action="store_true", help="Générer un fichier .exe unique portable")
    args = parser.parse_args()
    sys.exit(build(onefile=args.onefile))
