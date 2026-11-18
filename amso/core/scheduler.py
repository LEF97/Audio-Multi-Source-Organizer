"""Réexport de compatibilité : le planificateur dépend de Qt et vit dans `amso.services.scheduler`."""

from __future__ import annotations

from amso.services.scheduler import SyncScheduler

__all__ = ["SyncScheduler"]
