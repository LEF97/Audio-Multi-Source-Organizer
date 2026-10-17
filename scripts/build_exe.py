"""Script d'automatisation de la compilation de l'exécutable AMSO avec PyInstaller."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def build(onefile: bool = False) -> int:
    """Compile l'application AMSO en exécutable natif Windows."""
    project_root = Path(__file__).parent.parent.absolute()
    main_py = project_root / "main.py"
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    locales_dir = project_root / "amso" / "locales"
    resources_dir = project_root / "amso" / "resources"

    # Séparateur pour --add-data (';' sous Windows, ':' sous Linux/macOS)
    sep = ";" if sys.platform == "win32" else ":"

    # Sélection de l'icône selon l'OS cible
    if sys.platform == "darwin":
        icon_file = resources_dir / "icon.icns"
    elif sys.platform == "win32":
        icon_file = project_root / "icon.ico"
    else:  # Linux
        icon_file = resources_dir / "icon.png"

    # Fermer AMSO.exe s'il est en cours d'exécution pour éviter les verrous de fichiers
    if sys.platform == "win32":
        try:
            subprocess.run(["taskkill", "/F", "/IM", "AMSO.exe"], capture_output=True)
        except Exception:
            pass

    print("=" * 60)
    print(f"  AMSO — Compilation de l'exécutable natif ({sys.platform})")
    print(f"  Mode : {'Fichier unique portable (--onefile)' if onefile else 'Dossier optimisé (--onedir)'}")
    print("=" * 60)

    # Commande PyInstaller
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=AMSO",
        "--windowed",  # Pas de console noire en arrière-plan
        "--noconfirm",  # Écrase les builds précédents sans demander
        "--clean",  # Nettoie les caches de compilation
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        # Ajouter le package amso pour garantir que tous les sous-modules sont inclus
        f"--paths={project_root}",
        f"--add-data={locales_dir}{sep}amso/locales",
        f"--add-data={locales_dir}{sep}locales",
        f"--add-data={resources_dir}{sep}amso/resources",
        f"--add-data={resources_dir}{sep}resources",
        "--collect-all=amso",
        "--hidden-import=sqlite3",
        "--hidden-import=mutagen",
        "--hidden-import=dotenv",
    ]

    if icon_file.exists():
        cmd.append(f"--icon={icon_file}")

    if onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    cmd.append(str(main_py))

    print("\nExécution de la compilation PyInstaller...")
    res = subprocess.run(cmd, cwd=str(project_root))
    if res.returncode == 0:
        # Copie de sécurité des fichiers de traduction dans les dossiers de l'exécutable
        if not onefile:
            for sub_target in [
                "amso/locales",
                "locales",
                "_internal/amso/locales",
                "_internal/locales",
            ]:
                target_dest = dist_dir / "AMSO" / sub_target
                target_dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(locales_dir, target_dest, dirs_exist_ok=True)

            if resources_dir.exists():
                for sub_target in [
                    "amso/resources",
                    "resources",
                    "_internal/amso/resources",
                    "_internal/resources",
                ]:
                    target_dest = dist_dir / "AMSO" / sub_target
                    target_dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(resources_dir, target_dest, dirs_exist_ok=True)

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
