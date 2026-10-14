"""Gestionnaire de configuration persistante (config.ini) pour AMSO.

Permet de stocker et charger les préférences de l'utilisateur (langue,
options d'affichage, etc.) dans un fichier INI standardisé situé
dans le répertoire utilisateur (%APPDATA%/AMSO/config.ini sous Windows).
"""

from __future__ import annotations

import configparser
import os
from pathlib import Path
from typing import Optional

from amso.core.database import get_default_data_dir

# Nom du fichier de configuration par défaut
CONFIG_FILENAME = "config.ini"

# Section par défaut
SECTION_GENERAL = "General"
KEY_LANGUAGE = "language"


def get_config_path() -> Path:
    """Détermine le chemin absolu du fichier config.ini.

    Priorité :
    1. Variable d'environnement AMSO_CONFIG_PATH si définie
    2. Répertoire de données standard utilisateur (get_default_data_dir() / config.ini)
    """
    custom = os.getenv("AMSO_CONFIG_PATH")
    if custom and custom.strip():
        p = Path(custom.strip()).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    cfg_file = get_default_data_dir() / CONFIG_FILENAME
    return cfg_file


class ConfigManager:
    """Gestionnaire de lecture/écriture du fichier config.ini."""

    def __init__(self, config_path: Optional[str | Path] = None) -> None:
        if config_path is None:
            self.config_path = get_config_path()
        else:
            self.config_path = Path(config_path).resolve()

        self._config = configparser.ConfigParser()
        self.load()

    def load(self) -> None:
        """Charge le fichier INI depuis le disque s'il existe."""
        if self.config_path.exists() and self.config_path.is_file():
            try:
                self._config.read(self.config_path, encoding="utf-8")
            except Exception:
                # En cas de corruption, on repart sur une configuration vierge
                self._config = configparser.ConfigParser()
        else:
            self._config = configparser.ConfigParser()

    def save(self) -> None:
        """Sauvegarde la configuration actuelle dans le fichier INI."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            self._config.write(f)

    def get(self, section: str, key: str, fallback: Optional[str] = None) -> Optional[str]:
        """Récupère une valeur de configuration."""
        if self._config.has_section(section) and self._config.has_option(section, key):
            return self._config.get(section, key)
        return fallback

    def set(self, section: str, key: str, value: str) -> None:
        """Définit une valeur de configuration et persiste sur le disque."""
        if not self._config.has_section(section):
            self._config.add_section(section)
        self._config.set(section, key, str(value))
        self.save()

    def get_language(self) -> Optional[str]:
        """Retourne la langue configurée ou None si non définie."""
        lang = self.get(SECTION_GENERAL, KEY_LANGUAGE)
        return lang.strip().lower() if lang else None

    def set_language(self, lang_code: str) -> None:
        """Persiste le code de langue choisi (ex: 'fr', 'en', 'es', 'it')."""
        self.set(SECTION_GENERAL, KEY_LANGUAGE, lang_code.strip().lower())


# Instance singleton globale pour simplifier l'accès à travers l'application
_default_config_manager: Optional[ConfigManager] = None


def get_config_manager(custom_path: Optional[str | Path] = None) -> ConfigManager:
    """Fournit l'instance globale du ConfigManager."""
    global _default_config_manager
    if custom_path is not None:
        return ConfigManager(config_path=custom_path)
    if _default_config_manager is None:
        _default_config_manager = ConfigManager()
    return _default_config_manager
