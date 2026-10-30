"""Accès unique aux réglages Qt de l'interface (colonnes et tri des tables)."""

from __future__ import annotations

import os

from PySide6.QtCore import QSettings

ORGANIZATION = "AMSO"
APPLICATION = "AudioMultiSourceOrganizer"


def app_settings() -> QSettings:
    """Réglages de l'interface ; `AMSO_QSETTINGS_PATH` les redirige vers un fichier ini (tests : pas de registre ni de plist partagés)."""
    override = os.environ.get("AMSO_QSETTINGS_PATH")
    if override:
        return QSettings(override, QSettings.Format.IniFormat)
    return QSettings(ORGANIZATION, APPLICATION)
