"""Résolution des chemins de données AMSO (dossier de données, base SQLite, playlist sauvegardée)."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def get_default_data_dir() -> Path:
    """Retourne le répertoire de données standard utilisateur selon l'OS (AppData, etc.)."""
    custom = os.getenv("AMSO_DATA_DIR")
    if custom and custom.strip():
        app_dir = Path(custom.strip()).resolve()
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir

    if sys.platform == "win32":
        base = os.getenv("APPDATA") or (Path.home() / "AppData" / "Roaming")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = os.getenv("XDG_DATA_HOME") or (Path.home() / ".local" / "share")
    app_dir = Path(base) / "AMSO"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_database_path() -> Path:
    """Détermine l'emplacement standardisé de la base SQLite.

    Priorité :
    1. Variable d'environnement AMSO_DB_PATH si explicitement définie
    2. Répertoire AppData utilisateur (%APPDATA%/AMSO/amso_library.db sous Windows)
    """
    custom = os.getenv("AMSO_DB_PATH")
    if custom and custom.strip():
        p = Path(custom.strip()).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    db_file = get_default_data_dir() / "amso_library.db"
    return db_file


def get_saved_playlist_path() -> Path:
    """Détermine l'emplacement standardisé du fichier de sauvegarde de la playlist courante."""
    custom = os.getenv("AMSO_PLAYLIST_PATH")
    if custom and custom.strip():
        p = Path(custom.strip()).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    return get_default_data_dir() / "saved_playlist.json"
