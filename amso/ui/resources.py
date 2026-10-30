"""Gestionnaire des ressources graphiques et icônes pour AMSO."""

from __future__ import annotations

import sys
from functools import cache, lru_cache
from pathlib import Path

from PySide6.QtGui import QIcon, QPixmap


# Mis en cache : ces fonctions sont appelées par le splash, la fenêtre et plusieurs pages, et chaque appel
# refait des stat() sur disque et recharge/décode le fichier image.
@cache
def get_resource_path(relative_name: str) -> Path:
    """Retourne le chemin absolu d'une ressource embarquée (gère l'exécution dev et PyInstaller)."""
    candidates: list[Path] = []

    if getattr(sys, "frozen", False) or hasattr(sys, "_MEIPASS"):
        if hasattr(sys, "_MEIPASS"):
            meipass = Path(sys._MEIPASS)
            candidates.extend(
                [
                    meipass / "amso" / "resources" / relative_name,
                    meipass / "resources" / relative_name,
                    meipass / relative_name,
                    meipass / "amso" / relative_name,
                ]
            )
        exe_dir = Path(sys.executable).parent
        candidates.extend(
            [
                exe_dir / "_internal" / "amso" / "resources" / relative_name,
                exe_dir / "_internal" / "resources" / relative_name,
                exe_dir / "resources" / relative_name,
                exe_dir / relative_name,
            ]
        )

    root_dir = Path(__file__).resolve().parent.parent.parent  # racine du projet
    amso_dir = Path(__file__).resolve().parent.parent  # amso/

    # Si le fichier est présent à la fois à la racine et dans amso/resources, prendre le plus récent
    root_file = root_dir / relative_name
    res_file = amso_dir / "resources" / relative_name

    if root_file.exists() and res_file.exists():
        try:
            if root_file.stat().st_mtime >= res_file.stat().st_mtime:
                candidates.insert(0, root_file)
            else:
                candidates.insert(0, res_file)
        except OSError:
            candidates.insert(0, res_file)
    elif res_file.exists():
        candidates.insert(0, res_file)
    elif root_file.exists():
        candidates.insert(0, root_file)

    candidates.extend(
        [
            res_file,
            root_file,
            root_dir / "resources" / relative_name,
            amso_dir / relative_name,
        ]
    )

    for p in candidates:
        if p.exists():
            return p
    return candidates[0] if candidates else Path(relative_name)


@lru_cache(maxsize=1)
def get_app_icon() -> QIcon:
    """Retourne l'icône officielle de l'application AMSO adaptée à l'OS (Windows .ico, macOS .icns, Linux .png)."""
    icon = QIcon()
    if sys.platform == "darwin":
        icns_path = get_resource_path("icon.icns")
        if icns_path.exists():
            icon.addFile(str(icns_path))
    elif sys.platform == "win32":
        ico_path = get_resource_path("icon.ico")
        if ico_path.exists():
            icon.addFile(str(ico_path))

    # PNG universel haute définition (indispensable pour Linux X11/Wayland et repli tous OS)
    for name in ["AMSO.png", "icon.png"]:
        png_path = get_resource_path(name)
        if png_path.exists():
            icon.addFile(str(png_path))
            break

    # Repli final
    if icon.isNull():
        ico_path = get_resource_path("icon.ico")
        if ico_path.exists():
            icon.addFile(str(ico_path))

    return icon


@lru_cache(maxsize=1)
def get_app_logo_pixmap() -> QPixmap:
    """Retourne le logo / icône sous forme de QPixmap haute définition."""
    for name in ["AMSO.png", "icon.png", "logo.png"]:
        p = get_resource_path(name)
        if p.exists():
            pm = QPixmap(str(p))
            if not pm.isNull():
                return pm
    ico_path = get_resource_path("icon.ico")
    if ico_path.exists():
        return QIcon(str(ico_path)).pixmap(256, 256)
    return QPixmap()
