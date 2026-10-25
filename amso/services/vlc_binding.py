"""Liaison unique vers python-vlc, partagée entre PlayerService et ses mixins.

`vlc` est un proxy : il délègue à la dernière version du module chargée
(y compris après `reload_vlc`), ce qui évite toute variable globale réaffectée.
"""

from __future__ import annotations

import logging
import types
from typing import Any

logger = logging.getLogger(__name__)


class _VlcBinding:
    """Proxy vers le module python-vlc courant."""

    def __init__(self) -> None:
        self.module: types.ModuleType | None = None
        self.available = False

    def __getattr__(self, name: str) -> Any:
        if self.module is None:
            raise AttributeError(name)
        return getattr(self.module, name)


vlc = _VlcBinding()
