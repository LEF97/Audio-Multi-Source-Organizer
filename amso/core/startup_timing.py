"""Chronométrage des étapes de démarrage, écrit dans `startup.log` (dossier de données).

Les blocages de démarrage (E/S réseau, init VLC, antivirus) ne laissent aucune trace ailleurs :
ce journal horodaté donne la durée de chaque étape et permet de désigner la coupable.
"""

from __future__ import annotations

import logging
import sys
import time
from functools import lru_cache
from logging.handlers import RotatingFileHandler

from amso.core.db.paths import get_default_data_dir

LOG_NAME = "startup.log"
SLOW_STEP_SECONDS = 0.5
# Fixé à l'import du module, que main.py charge avant Qt, pour inclure le coût des imports lourds.
_IMPORT_T0 = time.perf_counter()

logger = logging.getLogger("amso.startup")


class StartupClock:
    """Mesure le temps écoulé depuis sa création et depuis la dernière étape."""

    def __init__(self) -> None:
        self._t0 = _IMPORT_T0
        self._last = self._t0
        self._attached = False
        self.steps: list[tuple[str, float]] = []

    def _attach_file_handler(self) -> None:
        if self._attached:
            return
        self._attached = True
        try:
            handler = RotatingFileHandler(
                get_default_data_dir() / LOG_NAME, maxBytes=200_000, backupCount=1, encoding="utf-8"
            )
        except OSError as exc:
            # Dossier de données en lecture seule : le chronométrage reste disponible en mémoire.
            logger.warning("Journal de démarrage indisponible : %s", exc)
            return
        handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

    def begin(self) -> None:
        """Ouvre un nouveau bloc dans le journal avec le contexte d'exécution."""
        self._attach_file_handler()
        frozen = bool(getattr(sys, "frozen", False))
        # `_MEIPASS` hors du dossier de l'exe = mode onefile : extraction dans %TEMP% à chaque lancement.
        logger.info(
            "=== Démarrage AMSO | frozen=%s | meipass=%s | exe=%s",
            frozen,
            getattr(sys, "_MEIPASS", "-"),
            sys.executable,
        )

    def mark(self, label: str) -> float:
        """Enregistre la fin d'une étape et retourne sa durée en secondes."""
        now = time.perf_counter()
        step = now - self._last
        self._last = now
        self.steps.append((label, step))
        level = logging.WARNING if step >= SLOW_STEP_SECONDS else logging.INFO
        logger.log(level, "%-34s +%7.3fs  (total %7.3fs)", label, step, now - self._t0)
        return step

    def note(self, message: str, *args: object) -> None:
        """Ajoute une ligne informative sans toucher au chronométrage des étapes."""
        logger.info(message, *args)


@lru_cache(maxsize=1)
def get_startup_clock() -> StartupClock:
    """Retourne l'horloge de démarrage unique du processus."""
    return StartupClock()
