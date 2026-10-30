"""Version, provenance et aide à l'installation de la libvlc chargée par python-vlc."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from amso.core.database import get_default_data_dir
from amso.services.vlc_binding import vlc


class LibVlcOrigin(StrEnum):
    AMSO_COPY = "amso_copy"  # téléchargée par AMSO (Windows) ou posée à côté de l'exécutable
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass(slots=True, frozen=True)
class LibVlcInfo:
    version: str
    path: str
    origin: LibVlcOrigin


def classify_origin(lib_path: str, amso_dirs: list[Path]) -> LibVlcOrigin:
    """`AMSO_COPY` si la bibliothèque est sous l'un des dossiers gérés par AMSO, `SYSTEM` sinon."""
    if not lib_path:
        return LibVlcOrigin.UNKNOWN
    resolved = Path(lib_path).resolve()
    for folder in amso_dirs:
        if resolved.is_relative_to(folder.resolve()):
            return LibVlcOrigin.AMSO_COPY
    return LibVlcOrigin.SYSTEM


def _amso_dirs() -> list[Path]:
    return [Path(sys.executable).parent / "vlc", Path(__file__).parents[2] / "vlc", get_default_data_dir() / "vlc"]


def describe_libvlc() -> LibVlcInfo | None:
    """None si python-vlc n'est pas chargé. La version vient de la libvlc réellement liée, pas de python-vlc."""
    module = vlc.module
    if module is None:
        return None
    version = module.libvlc_get_version()
    text = version.decode("utf-8", "replace") if isinstance(version, bytes) else str(version)
    lib_path = str(getattr(getattr(module, "dll", None), "_name", "") or "")
    return LibVlcInfo(version=text.split(" ")[0], path=lib_path, origin=classify_origin(lib_path, _amso_dirs()))


def supports_vlc_download(platform: str = sys.platform) -> bool:
    """Seule l'archive Windows est téléchargée ; ailleurs VLC vient du système (Linux) ou de VLC.app (macOS)."""
    return platform == "win32"


def macos_user_vlc_dir() -> Path | None:
    """VLC.app installée dans ~/Applications : python-vlc ne cherche que dans /Applications."""
    candidate = Path.home() / "Applications" / "VLC.app" / "Contents" / "MacOS"
    return candidate if (candidate / "lib" / "libvlc.dylib").is_file() else None


def setup_macos_user_vlc(platform: str = sys.platform) -> Path | None:
    """Pointe python-vlc vers ~/Applications/VLC.app si la copie système de /Applications est absente."""
    if platform != "darwin" or Path("/Applications/VLC.app").exists() or "PYTHON_VLC_LIB_PATH" in os.environ:
        return None
    base = macos_user_vlc_dir()
    if base is None:
        return None
    os.environ["PYTHON_VLC_LIB_PATH"] = str(base / "lib" / "libvlc.dylib")
    os.environ["PYTHON_VLC_MODULE_PATH"] = str(base / "plugins")
    return base
