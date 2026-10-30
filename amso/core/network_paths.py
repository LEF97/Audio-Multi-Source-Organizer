"""Détection des chemins réseau, pour ne jamais les sonder sur le thread UI.

Sur un partage injoignable (NAS éteint, VPN absent), un simple `os.path.exists` attend le délai SMB, qui peut atteindre
plusieurs dizaines de secondes par appel ; le thread UI se fige. La détection ne fait aucune E/S réseau.
"""

from __future__ import annotations

import os
import sys

_DRIVE_REMOTE = 4  # valeur de GetDriveTypeW pour un lecteur réseau mappé
_EXTENDED_PREFIX = "\\\\?\\"


def is_network_path(path: str | os.PathLike[str] | None) -> bool:
    """Indique si `path` est un chemin UNC ou un lecteur réseau mappé (Windows uniquement pour les lecteurs)."""
    if not path:
        return False
    p = os.fspath(path)
    # Le préfixe étendu (\\?\C:\...) désigne un chemin local ; seul \\?\UNC\... est réseau.
    if p.startswith(_EXTENDED_PREFIX):
        return p[len(_EXTENDED_PREFIX) :].upper().startswith("UNC\\")
    if p.startswith(("\\\\", "//")):
        return True
    if sys.platform == "win32" and len(p) >= 2 and p[1] == ":":
        import ctypes

        # GetDriveTypeW lit la table des lecteurs du système, sans contacter le partage.
        return bool(ctypes.windll.kernel32.GetDriveTypeW(p[:2] + "\\") == _DRIVE_REMOTE)
    return False
