"""Module de gestion de l'inhibition de la mise en veille du système et de l'écran pendant la lecture audio."""

from __future__ import annotations

import ctypes
import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtCore import QTimer

logger = logging.getLogger(__name__)

# Constantes Windows pour SetThreadExecutionState
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002
ES_AWAYMODE_REQUIRED = 0x00000040


class SleepInhibitor:
    """Empêche la mise en veille automatique du système et de l'écran pendant la lecture audio."""

    _is_inhibited: bool = False
    _prevent_display: bool = False
    _timer: QTimer | None = None

    @classmethod
    def is_inhibited(cls) -> bool:
        """Indique si la mise en veille système est actuellement inhibée."""
        return cls._is_inhibited

    @classmethod
    def is_display_inhibited(cls) -> bool:
        """Indique si la mise en veille de l'écran est également inhibée."""
        return cls._is_inhibited and cls._prevent_display

    @classmethod
    def inhibit(cls, prevent_display: bool = False) -> bool:
        """Inhibe la mise en veille du système, et optionnellement la veille de l'écran."""
        if cls._is_inhibited and cls._prevent_display == prevent_display:
            return True

        cls._is_inhibited = True
        cls._prevent_display = prevent_display
        cls._apply_state()
        cls._ensure_timer()
        return True

    @classmethod
    def release(cls) -> bool:
        """Rétablit le comportement normal de mise en veille de l'OS."""
        if not cls._is_inhibited:
            return True

        if cls._timer:
            try:
                cls._timer.stop()
            except Exception:
                pass
            cls._timer = None

        cls._is_inhibited = False
        cls._prevent_display = False

        if sys.platform == "win32":
            try:
                ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
                logger.debug("Mise en veille normale du système rétablie.")
                return True
            except Exception as exc:
                logger.warning("Échec de la réactivation de la veille Windows: %s", exc)
                return False
        return True

    @classmethod
    def _apply_state(cls) -> None:
        if sys.platform == "win32":
            try:
                flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED
                if cls._prevent_display:
                    flags |= ES_DISPLAY_REQUIRED
                res = ctypes.windll.kernel32.SetThreadExecutionState(flags)
                if res != 0:
                    logger.debug(
                        "Mise en veille Windows configurée (display=%s, flags=0x%08X).",
                        cls._prevent_display,
                        flags,
                    )
            except Exception as exc:
                logger.warning("Échec de l'inhibition de veille Windows: %s", exc)

    @classmethod
    def _ensure_timer(cls) -> None:
        """Lance un heartbeat de rafraîchissement périodique (30s) pour garantir le maintien allumé de l'écran."""
        try:
            from PySide6.QtCore import QCoreApplication, QTimer

            if QCoreApplication.instance() is None:
                return
            if cls._timer is None:
                cls._timer = QTimer()
                cls._timer.setInterval(30000)  # 30 secondes
                cls._timer.timeout.connect(cls._on_heartbeat)
            if not cls._timer.isActive():
                cls._timer.start()
        except Exception as exc:
            logger.debug("Heartbeat d'inhibition non actif: %s", exc)

    @classmethod
    def _on_heartbeat(cls) -> None:
        if cls._is_inhibited:
            cls._apply_state()
