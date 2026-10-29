"""Packaging des versions Linux (.tar.gz, .AppImage) et macOS (.dmg) à partir du dossier produit par build_exe.py.

Usage (sur la machine cible, après `python scripts/build_exe.py`) :
    python scripts/package_unix.py [--appimagetool CHEMIN]

Linux : dist/AMSO/ -> AMSO-Linux-vX.Y.Z-<arch>.tar.gz et, si `appimagetool` est fourni, .AppImage.
macOS : dist/AMSO.app -> AMSO-macOS-<arch>-vX.Y.Z.dmg (non signé, non notarisé).
Windows : sans objet (voir `build_exe.py --package`).
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOC_PATTERNS = ("README*.md", "CHANGELOG*.md", "ROADMAP*.md", "LICENSE")

DESKTOP_ENTRY = """[Desktop Entry]
Type=Application
Name=AMSO
GenericName=Audio Multi-Source Organizer
Comment=Audio player and library organizer
Exec=AMSO
Icon=AMSO
Categories=AudioVideo;Audio;Player;
Terminal=false
"""

APPRUN = """#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/lib/amso/AMSO" "$@"
"""


def normalized_arch(machine: str | None = None) -> str:
    machine = (machine or platform.machine()).lower()
    return {"amd64": "x86_64", "x86_64": "x86_64", "arm64": "arm64", "aarch64": "arm64"}.get(machine, machine)


def release_file_name(system: str, version: str, arch: str, extension: str) -> str:
    """Noms publiés : AMSO-Linux-vX-<arch>.<ext> et AMSO-macOS-<arch>-vX.<ext>."""
    if system == "macos":
        return f"AMSO-macOS-{arch}-v{version}.{extension}"
    return f"AMSO-Linux-v{version}-{arch}.{extension}"


def read_version() -> str:
    sys.path.insert(0, str(PROJECT_ROOT))
    import amso

    return str(amso.__version__)


def _copy_docs(target: Path) -> None:
    for pattern in DOC_PATTERNS:
        for doc in sorted(PROJECT_ROOT.glob(pattern)):
            shutil.copy2(doc, target / doc.name)


def package_linux_tarball(version: str, arch: str) -> Path:
    app_dir = PROJECT_ROOT / "dist" / "AMSO"
    if not app_dir.is_dir():
        raise FileNotFoundError(f"{app_dir} introuvable : lancer d'abord scripts/build_exe.py")
    staging = PROJECT_ROOT / "dist" / "tarball" / "AMSO"
    if staging.parent.exists():
        shutil.rmtree(staging.parent)
    shutil.copytree(app_dir, staging)
    _copy_docs(staging)
    archive = PROJECT_ROOT / "dist" / release_file_name("linux", version, arch, "tar.gz")
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(staging, arcname="AMSO")
    return archive


def build_appdir(version: str) -> Path:
    app_dir = PROJECT_ROOT / "dist" / "AMSO"
    appdir = PROJECT_ROOT / "dist" / "AMSO.AppDir"
    if appdir.exists():
        shutil.rmtree(appdir)
    payload = appdir / "usr" / "lib" / "amso"
    shutil.copytree(app_dir, payload)
    (appdir / "AppRun").write_text(APPRUN, encoding="utf-8", newline="\n")
    (appdir / "AppRun").chmod(0o755)
    (appdir / "AMSO.desktop").write_text(DESKTOP_ENTRY, encoding="utf-8", newline="\n")
    icon = PROJECT_ROOT / "amso" / "resources" / "icon.png"
    if icon.exists():
        shutil.copy2(icon, appdir / "AMSO.png")
    return appdir


def package_linux_appimage(version: str, arch: str, appimagetool: str) -> Path:
    appdir = build_appdir(version)
    output = PROJECT_ROOT / "dist" / release_file_name("linux", version, arch, "AppImage")
    env_arch = {"x86_64": "x86_64", "arm64": "aarch64"}.get(arch, arch)
    # --appimage-extract-and-run : les runners CI n'ont pas toujours FUSE
    subprocess.run(
        [appimagetool, "--appimage-extract-and-run", str(appdir), str(output)],
        check=True,
        env={**os.environ, "ARCH": env_arch},
    )
    return output


def package_macos_dmg(version: str, arch: str) -> Path:
    app = PROJECT_ROOT / "dist" / "AMSO.app"
    if not app.is_dir():
        raise FileNotFoundError(f"{app} introuvable : lancer d'abord scripts/build_exe.py")
    staging = PROJECT_ROOT / "dist" / "dmg"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    # symlinks=True : un bundle .app contient des liens symboliques (Frameworks) qu'il faut conserver
    shutil.copytree(app, staging / "AMSO.app", symlinks=True)
    _copy_docs(staging)
    (staging / "Applications").symlink_to("/Applications")
    output = PROJECT_ROOT / "dist" / release_file_name("macos", version, arch, "dmg")
    subprocess.run(
        ["hdiutil", "create", "-volname", "AMSO", "-srcfolder", str(staging), "-ov", "-format", "UDZO", str(output)],
        check=True,
    )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Packager AMSO pour Linux ou macOS")
    parser.add_argument("--appimagetool", help="Chemin de appimagetool (Linux) : active la production de l'AppImage")
    args = parser.parse_args()

    version, arch = read_version(), normalized_arch()
    outputs: list[Path] = []
    if sys.platform.startswith("linux"):
        outputs.append(package_linux_tarball(version, arch))
        if args.appimagetool:
            outputs.append(package_linux_appimage(version, arch, args.appimagetool))
    elif sys.platform == "darwin":
        outputs.append(package_macos_dmg(version, arch))
    else:
        print("Ce script ne s'applique qu'à Linux et macOS (Windows : scripts/build_exe.py --package).")
        return 1

    for path in outputs:
        print(f"Archive produite : {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
