"""Système d'internationalisation (i18n) et de localisation pour AMSO.

Gère :
- La détection automatique de la langue de l'OS au premier démarrage.
- Le repli sur l'anglais par défaut si la langue système n'est pas prise en charge.
- La persistance dans le fichier INI (%APPDATA%/AMSO/config.ini).
- Le chargement dynamique des fichiers JSON (amso/locales/).
- La traduction instantanée (tr()) et la notification de changement de langue.
"""

from __future__ import annotations

import ctypes
import json
import locale
import logging
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from amso.core.config import ConfigManager, get_config_manager

logger = logging.getLogger(__name__)

# Langues supportées (code ISO 639-1 -> Libellé affiché)
SUPPORTED_LANGUAGES: dict[str, str] = {
    "fr": "Français",
    "en": "English",
    "es": "Español",
    "it": "Italiano",
    "de": "Deutsch",
}

# Langue de repli internationale par défaut
DEFAULT_LANGUAGE: str = "en"

# Référence de master VF
REFERENCE_LANGUAGE: str = "fr"


def get_locales_dir() -> Path:
    """Retourne le chemin absolu du répertoire des fichiers de traduction.

    Prend en compte le mode exécutable autonome PyInstaller (sys._MEIPASS et onedir _internal).
    """
    candidates: list[Path] = []

    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            meipass = Path(sys._MEIPASS)
            candidates.extend(
                [
                    meipass / "amso" / "locales",
                    meipass / "locales",
                ]
            )
        exe_dir = Path(sys.executable).parent
        candidates.extend(
            [
                exe_dir / "_internal" / "amso" / "locales",
                exe_dir / "_internal" / "locales",
                exe_dir / "amso" / "locales",
                exe_dir / "locales",
            ]
        )

    # Mode script Python normal ou développement
    candidates.extend(
        [
            Path(__file__).parent.parent / "locales",
            Path.cwd() / "amso" / "locales",
        ]
    )

    for p in candidates:
        if p.exists() and (p / "fr.json").exists():
            return p

    return Path(__file__).parent.parent / "locales"


def detect_os_language() -> str:
    """Détecte la langue de l'OS et retourne le code à 2 lettres.

    Si la langue de l'OS figure dans SUPPORTED_LANGUAGES, elle est retournée.
    Sinon, DEFAULT_LANGUAGE ("en") est retourné.
    """
    detected_code: str | None = None

    # 1. Sous Windows : interroger l'API native GetUserDefaultUILanguage via ctypes
    if sys.platform == "win32":
        try:
            windll = getattr(ctypes, "windll", None)
            if windll and hasattr(windll, "kernel32"):
                lcid = windll.kernel32.GetUserDefaultUILanguage()
                win_loc = getattr(locale, "windows_locale", {}).get(lcid)
                if win_loc:
                    detected_code = win_loc.split("_")[0].lower()
        except Exception:
            pass

    # 2. Repli cross-platform sur locale standard
    if not detected_code:
        try:
            loc = locale.getlocale()[0]
            if loc:
                detected_code = loc.split("_")[0].lower()
        except Exception:
            pass

    # 3. Repli sur les variables d'environnement (LANG, LC_ALL, LC_MESSAGES)
    if not detected_code:
        for env_var in ("LANG", "LC_ALL", "LC_MESSAGES", "LANGUAGE"):
            val = os.getenv(env_var)
            if val and val.strip():
                # ex: fr_FR.UTF-8 -> fr
                clean = val.split(".")[0].split("_")[0].split("-")[0].lower()
                if len(clean) == 2:
                    detected_code = clean
                    break

    # Vérification de prise en charge
    if detected_code and detected_code in SUPPORTED_LANGUAGES:
        return detected_code

    return DEFAULT_LANGUAGE


class I18nManager:
    """Gestionnaire centralisé des traductions et de la langue active."""

    def __init__(self, config_manager: ConfigManager | None = None) -> None:
        self.config_manager = config_manager or get_config_manager()
        self.locales_dir = get_locales_dir()
        self._current_language: str = DEFAULT_LANGUAGE
        self._translations: dict[str, str] = {}
        self._fallback_translations: dict[str, str] = {}
        self._listeners: list[Callable[[str], None]] = []

        # Chargement initial du fichier de repli anglais
        self._load_fallback_translations()

        # Initialisation de la langue active selon config ou OS
        self.init_language()

    def _load_json(self, lang_code: str) -> dict[str, str]:
        path = self.locales_dir / f"{lang_code}.json"
        if path.exists() and path.is_file():
            try:
                with open(path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning("[i18n] Erreur de lecture de %s : %s", path, e)
        return {}

    def _load_fallback_translations(self) -> None:
        self._fallback_translations = self._load_json(DEFAULT_LANGUAGE)

    def init_language(self) -> str:
        """Détermine la langue à utiliser au démarrage.

        1. Si une langue est déjà persistée dans config.ini et supportée, on l'utilise.
        2. Si première exécution (pas de langue dans l'ini) :
           - On teste la langue de l'OS.
           - Si supportée, on la choisit ; sinon on bascule sur l'anglais par défaut.
           - On persiste immédiatement ce choix dans config.ini.
        """
        saved_lang = self.config_manager.get_language()
        if saved_lang and saved_lang in SUPPORTED_LANGUAGES:
            target_lang = saved_lang
        else:
            # Premier démarrage ou langue absente de l'ini
            target_lang = detect_os_language()
            # Persister ce premier choix dans config.ini
            self.config_manager.set_language(target_lang)

        self.set_language(target_lang, save_to_config=False)
        return self._current_language

    @property
    def current_language(self) -> str:
        return self._current_language

    def set_language(self, lang_code: str, save_to_config: bool = True) -> bool:
        """Change la langue active, recharge le dictionnaire et notifie les composants."""
        code = lang_code.strip().lower()
        if code not in SUPPORTED_LANGUAGES:
            return False

        self._current_language = code
        self._translations = self._load_json(code)

        if save_to_config:
            self.config_manager.set_language(code)

        # Notifier les observateurs
        for listener in list(self._listeners):
            try:
                listener(self._current_language)
            except Exception as e:
                logger.warning("[i18n] Erreur lors de la notification de listener : %s", e)

        return True

    def add_listener(self, callback: Callable[[str], None]) -> None:
        """Enregistre un callback exécuté lors d'un changement de langue."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[str], None]) -> None:
        if callback in self._listeners:
            self._listeners.remove(callback)

    def tr(self, key: str, default: str | None = None, **kwargs: Any) -> str:
        """Traduit une clé selon la langue active avec repli et interpolation."""
        template = self._translations.get(key)
        if template is None:
            template = self._fallback_translations.get(key)
        if template is None:
            template = default if default is not None else key

        if kwargs:
            try:
                return template.format(**kwargs)
            except Exception:
                return template
        return template


# Instance singleton globale
_global_i18n: I18nManager | None = None


def get_i18n(config_manager: ConfigManager | None = None) -> I18nManager:
    """Fournit l'instance globale d'I18nManager."""
    global _global_i18n
    if _global_i18n is None:
        _global_i18n = I18nManager(config_manager=config_manager)
    return _global_i18n


def tr(key: str, default: str | None = None, **kwargs: Any) -> str:
    """Raccourci global de traduction pour faciliter l'usage dans tout le projet."""
    return get_i18n().tr(key, default=default, **kwargs)
