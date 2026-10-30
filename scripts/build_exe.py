"""Script d'automatisation de la compilation de l'exécutable AMSO avec PyInstaller."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def build(onefile: bool = False) -> int:
    """Compile l'application AMSO en exécutable natif (Windows .exe, Linux dossier, macOS .app)."""
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
        f"--add-data={resources_dir}{sep}.",
        "--collect-all=amso",
        "--hidden-import=sqlite3",
        "--hidden-import=mutagen",
        "--hidden-import=dotenv",
    ]

    if icon_file.exists():
        cmd.append(f"--icon={icon_file}")
    if sys.platform == "darwin":
        cmd.append("--osx-bundle-identifier=com.lef97.amso")

    if onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    cmd.append(str(main_py))

    print("\nExécution de la compilation PyInstaller...")
    res = subprocess.run(cmd, cwd=str(project_root))
    if res.returncode == 0:
        # Copie de sécurité des fichiers de traduction dans les dossiers de l'exécutable. Ignorée sur macOS : le
        # système de fichiers n'y distingue pas la casse, `dist/AMSO/amso` y désignerait l'exécutable `AMSO`, et les
        # données sont déjà dans le bundle .app
        if not onefile and sys.platform != "darwin":
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
        exe_name = "AMSO.exe" if sys.platform == "win32" else "AMSO"
        if sys.platform == "darwin":
            print(f"  Application générée : {dist_dir / 'AMSO.app'}")
        elif onefile:
            print(f"  Exécutable généré : {dist_dir / exe_name}")
        else:
            print(f"  Exécutable généré : {dist_dir / 'AMSO' / exe_name}")
        print("=" * 60)
    else:
        print("\n" + "!" * 60)
        print(f"  ERREUR : La compilation a échoué (code {res.returncode}).")
        print("!" * 60)

    return res.returncode


def package_release(onefile: bool = True) -> int:
    """Prépare le dossier de distribution et l'archive zip selon le protocole de release."""
    project_root = Path(__file__).parent.parent.absolute()
    dist_dir = project_root / "dist"
    locales_dir = project_root / "amso" / "locales"

    # Récupérer la version courante
    sys.path.insert(0, str(project_root))
    try:
        import amso
        version = amso.__version__
    except Exception:
        version = "0.0.0"

    release_name = f"AMSO-Windows-v{version}"
    release_dir = dist_dir / release_name

    print("\n" + "=" * 60)
    print(f"  AMSO — Packaging de distribution : {release_name}")
    print("=" * 60)

    # Nettoyage et création du dossier cible
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copie de l'exécutable
    if onefile:
        exe_src = dist_dir / "AMSO.exe"
        if exe_src.exists():
            print(f"  -> Copie de {exe_src.name} vers {release_dir}")
            shutil.copy2(exe_src, release_dir / "AMSO.exe")
        else:
            print(f"  [ATTENTION] Fichier {exe_src} introuvable.")
    else:
        app_dir = dist_dir / "AMSO"
        if app_dir.exists():
            print(f"  -> Copie du dossier AMSO vers {release_dir / 'AMSO'}")
            shutil.copytree(app_dir, release_dir / "AMSO", dirs_exist_ok=True)
        else:
            print(f"  [ATTENTION] Dossier {app_dir} introuvable.")

    # 2. Copie de la documentation utilisateur (README, CHANGELOG, ROADMAP en fr et en ; pas les fichiers de développement)
    for pattern in ("README*.md", "CHANGELOG*.md", "ROADMAP*.md"):
        for md_file in sorted(project_root.glob(pattern)):
            print(f"  -> Ajout documentation : {md_file.name}")
            shutil.copy2(md_file, release_dir / md_file.name)

    # 3. Copie de la licence
    license_file = project_root / "LICENSE"
    if license_file.exists():
        shutil.copy2(license_file, release_dir / "LICENSE")

    # 4. Copie des fichiers de langues
    if locales_dir.exists():
        print("  -> Copie des traductions locales")
        shutil.copytree(locales_dir, release_dir / "locales", dirs_exist_ok=True)

    # 5. Création de l'archive ZIP
    zip_dest = dist_dir / release_name
    print(f"  -> Création de l'archive ZIP : {zip_dest}.zip")
    shutil.make_archive(str(zip_dest), "zip", root_dir=str(release_dir))

    print("\n" + "=" * 60)
    print(f"  SUCCÈS : Packaging {release_name} terminé !")
    print(f"  Dossier : {release_dir}")
    print(f"  Archive : {zip_dest}.zip")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compiler et packager AMSO en .exe avec PyInstaller")
    parser.add_argument("--onefile", action="store_true", help="Générer un fichier .exe unique portable")
    parser.add_argument("--package", action="store_true", help="Générer le dossier de release et l'archive .zip")
    args = parser.parse_args()

    ret = build(onefile=args.onefile)
    if ret == 0 and args.package:
        ret = package_release(onefile=args.onefile)

    sys.exit(ret)
