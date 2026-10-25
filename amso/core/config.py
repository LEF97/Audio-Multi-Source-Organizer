"""Gestionnaire de configuration persistante (config.ini) pour AMSO.

Permet de stocker et charger les préférences de l'utilisateur (langue,
options d'affichage, etc.) dans un fichier INI standardisé situé
dans le répertoire utilisateur (%APPDATA%/AMSO/config.ini sous Windows).
"""

from __future__ import annotations

import configparser
import contextlib
import logging
import os
import shutil
import threading
import time
from pathlib import Path
from typing import overload

from amso.core.database import get_default_data_dir

logger = logging.getLogger(__name__)

# Une seule écriture de config.ini à la fois (timers, threads et plusieurs ConfigManager partagent le même fichier)
_SAVE_LOCK = threading.Lock()
_REPLACE_ATTEMPTS = 8  # Windows peut refuser un instant le remplacement (antivirus, indexation) : on réessaie

# Nom du fichier de configuration par défaut
CONFIG_FILENAME = "config.ini"

# Sections
SECTION_GENERAL = "General"
KEY_LANGUAGE = "language"
KEY_ACTIVE_PAGE = "active_page"

SECTION_PLAYER = "Player"
KEY_PREVENT_SLEEP = "prevent_sleep"
KEY_SLEEP_MODE = "sleep_mode"
KEY_TRANSITION_MODE = "transition_mode"
KEY_CROSSFADE_SECONDS = "crossfade_seconds"
KEY_SHUFFLE = "shuffle"
KEY_REPEAT_MODE = "repeat_mode"
KEY_VOLUME = "volume"
KEY_MUTED = "muted"
KEY_VISUAL_EFFECT = "visual_effect"
KEY_POSITION_MS = "position_ms"
KEY_BLIND_TEST_COUNTDOWN = "blind_test_countdown"
KEY_BLIND_TEST_REVEAL = "blind_test_reveal"
KEY_BLIND_TEST_FADE = "blind_test_fade"
KEY_FADE_IN_TRACK_ENABLED = "fade_in_track_enabled"
KEY_FADE_IN_TRACK_DURATION = "fade_in_track_duration"
KEY_FADE_IN_RESUME_ENABLED = "fade_in_resume_enabled"
KEY_FADE_IN_RESUME_DURATION = "fade_in_resume_duration"
KEY_AUDIO_ENGINE = "audio_engine"
KEY_VLC_GAPLESS_LATENCY = "vlc_gapless_latency_ms"


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

    def __init__(self, config_path: str | Path | None = None) -> None:
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
            except Exception as exc:
                # En cas de corruption : copie de sauvegarde du fichier fautif, puis configuration vierge
                logger.warning(
                    "config.ini illisible (%s) : copie de sauvegarde en .bak, configuration réinitialisée", exc
                )
                with contextlib.suppress(OSError):
                    shutil.copy2(self.config_path, self.config_path.with_name(self.config_path.name + ".bak"))
                self._config = configparser.ConfigParser()
        else:
            self._config = configparser.ConfigParser()

    def save(self) -> None:
        """Sauvegarde la configuration dans le fichier INI de façon atomique (fichier temporaire puis remplacement).

        Une coupure pendant l'écriture laisse l'ancien fichier intact au lieu d'un fichier tronqué.
        """
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.config_path.with_name(self.config_path.name + ".tmp")
        with _SAVE_LOCK:
            try:
                with open(tmp_path, "w", encoding="utf-8") as f:
                    self._config.write(f)
                    f.flush()
                    os.fsync(f.fileno())
                for attempt in range(_REPLACE_ATTEMPTS):
                    try:
                        os.replace(tmp_path, self.config_path)
                        break
                    except PermissionError:
                        if attempt == _REPLACE_ATTEMPTS - 1:
                            raise
                        time.sleep(0.05 * (attempt + 1))
            except BaseException:
                with contextlib.suppress(OSError):
                    tmp_path.unlink()
                raise

    @overload
    def get(self, section: str, key: str) -> str | None: ...

    @overload
    def get(self, section: str, key: str, fallback: str) -> str: ...

    @overload
    def get(self, section: str, key: str, fallback: str | None) -> str | None: ...

    def get(self, section: str, key: str, fallback: str | None = None) -> str | None:
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

    def get_language(self) -> str | None:
        """Retourne la langue configurée ou None si non définie."""
        lang = self.get(SECTION_GENERAL, KEY_LANGUAGE)
        return lang.strip().lower() if lang else None

    def set_language(self, lang_code: str) -> None:
        """Persiste le code de langue choisi (ex: 'fr', 'en', 'es', 'it')."""
        self.set(SECTION_GENERAL, KEY_LANGUAGE, lang_code.strip().lower())

    def get_active_page(self, default: str = "player") -> str:
        """Retourne l'identifiant de la page active (par défaut 'player')."""
        val = self.get(SECTION_GENERAL, KEY_ACTIVE_PAGE, default)
        valid_pages = {
            "tracks",
            "folders",
            "duplicates",
            "stats",
            "player",
            "blind_test",
            "playlist",
            "settings_general",
            "settings_sources",
            "settings_player",
            "logs",
        }
        return val if val in valid_pages else default

    def set_active_page(self, page_id: str) -> None:
        """Définit la dernière page active."""
        self.set(SECTION_GENERAL, KEY_ACTIVE_PAGE, page_id)

    def remove_active_page(self) -> None:
        """Supprime la clé active_page du fichier de configuration ini."""
        if self._config.has_section(SECTION_GENERAL) and self._config.has_option(SECTION_GENERAL, KEY_ACTIVE_PAGE):
            self._config.remove_option(SECTION_GENERAL, KEY_ACTIVE_PAGE)
            self.save()

    def get_sleep_mode(self) -> str:
        """Retourne le mode d'inhibition de veille : 'allow', 'player_playlist' (défaut), ou 'always'."""
        val = self.get(SECTION_PLAYER, KEY_SLEEP_MODE)
        if val in ("allow", "player_playlist", "always"):
            return val
        old_val = self.get(SECTION_PLAYER, KEY_PREVENT_SLEEP)
        if old_val is not None:
            if str(old_val).lower() in ("false", "0", "no", "off"):
                return "allow"
            return "player_playlist"
        return "player_playlist"

    def set_sleep_mode(self, mode: str) -> None:
        """Définit le mode d'inhibition de veille ('allow', 'player_playlist', 'always')."""
        if mode in ("allow", "player_playlist", "always"):
            self.set(SECTION_PLAYER, KEY_SLEEP_MODE, mode)
            self.set(SECTION_PLAYER, KEY_PREVENT_SLEEP, "false" if mode == "allow" else "true")

    def get_prevent_sleep(self) -> bool:
        """Rétrocompatibilité : retourne True si la veille est inhibée pendant la lecture."""
        return self.get_sleep_mode() != "allow"

    def set_prevent_sleep(self, enabled: bool) -> None:
        """Rétrocompatibilité : active ou désactive l'inhibition de veille."""
        self.set_sleep_mode("player_playlist" if enabled else "allow")

    def get_audio_engine(self) -> str:
        """Retourne le moteur audio configuré : 'buffer' (défaut) ou 'vlc_direct'."""
        val = self.get(SECTION_PLAYER, KEY_AUDIO_ENGINE, "buffer")
        return "vlc_direct" if val == "vlc_direct" else "buffer"

    def set_audio_engine(self, engine: str) -> None:
        """Définit le moteur audio ('buffer' ou 'vlc_direct')."""
        val = "vlc_direct" if engine == "vlc_direct" else "buffer"
        self.set(SECTION_PLAYER, KEY_AUDIO_ENGINE, val)

    def get_vlc_gapless_latency(self) -> int:
        """Retourne la latence DirectSound/LibVLC en ms pour le gapless 0 (défaut : 250)."""
        val = self.get(SECTION_PLAYER, KEY_VLC_GAPLESS_LATENCY, "250")
        try:
            return max(0, min(2000, int(val)))
        except (ValueError, TypeError):
            return 250

    def set_vlc_gapless_latency(self, latency_ms: int) -> None:
        """Définit la latence DirectSound/LibVLC en ms (entre 0 et 2000 ms)."""
        val = max(0, min(2000, int(latency_ms)))
        self.set(SECTION_PLAYER, KEY_VLC_GAPLESS_LATENCY, str(val))

    def get_transition_mode(self) -> str:
        """Retourne le mode de transition ('standard', 'gapless', 'crossfade'). Par défaut 'gapless'."""
        val = self.get(SECTION_PLAYER, KEY_TRANSITION_MODE, "gapless")
        return val if val in ("standard", "gapless", "crossfade") else "gapless"

    def set_transition_mode(self, mode: str) -> None:
        """Définit le mode de transition ('standard', 'gapless', 'crossfade')."""
        if mode in ("standard", "gapless", "crossfade"):
            self.set(SECTION_PLAYER, KEY_TRANSITION_MODE, mode)

    def get_crossfade_duration(self) -> int:
        """Retourne la durée du fondu enchaîné en secondes (1 à 20, défaut 3)."""
        val = self.get(SECTION_PLAYER, KEY_CROSSFADE_SECONDS, "3")
        try:
            return max(1, min(20, int(val)))
        except Exception:
            return 3

    def set_crossfade_duration(self, seconds: int) -> None:
        """Définit la durée du fondu enchaîné en secondes (1 à 20)."""
        self.set(SECTION_PLAYER, KEY_CROSSFADE_SECONDS, str(max(1, min(20, seconds))))

    def get_player_shuffle(self) -> bool:
        """Retourne True si la lecture aléatoire était activée (False par défaut)."""
        val = self.get(SECTION_PLAYER, KEY_SHUFFLE, "false")
        return str(val).lower() in ("true", "1", "yes", "on")

    def set_player_shuffle(self, enabled: bool) -> None:
        """Définit l'état de la lecture aléatoire."""
        self.set(SECTION_PLAYER, KEY_SHUFFLE, "true" if enabled else "false")

    def get_player_repeat_mode(self) -> int:
        """Retourne le mode de boucle (0=OFF, 1=ALL, 2=ONE). 0 par défaut."""
        val = self.get(SECTION_PLAYER, KEY_REPEAT_MODE, "0")
        try:
            return int(val) % 3
        except Exception:
            return 0

    def set_player_repeat_mode(self, mode: int) -> None:
        """Définit le mode de boucle."""
        self.set(SECTION_PLAYER, KEY_REPEAT_MODE, str(mode % 3))

    def get_player_volume(self) -> int:
        """Retourne le volume sonore sauvegardé (0 à 100). 80 par défaut."""
        val = self.get(SECTION_PLAYER, KEY_VOLUME, "80")
        try:
            return max(0, min(100, int(val)))
        except Exception:
            return 80

    def set_player_volume(self, volume: int) -> None:
        """Définit le volume sonore."""
        self.set(SECTION_PLAYER, KEY_VOLUME, str(max(0, min(100, volume))))

    def get_player_muted(self) -> bool:
        """Retourne True si le son était en sourdine (False par défaut)."""
        val = self.get(SECTION_PLAYER, KEY_MUTED, "false")
        return str(val).lower() in ("true", "1", "yes", "on")

    def set_player_muted(self, muted: bool) -> None:
        """Définit l'état de la sourdine."""
        self.set(SECTION_PLAYER, KEY_MUTED, "true" if muted else "false")

    def get_visual_effect(self) -> str:
        """Retourne l'effet visuel configuré pour le lecteur ('none', 'particles', 'waves', 'stars', 'warp', 'warp_dynamic', 'aurora', 'bars', 'bars_full'). 'particles' par défaut."""
        val = self.get(SECTION_PLAYER, KEY_VISUAL_EFFECT, "particles")
        valid = {"none", "particles", "waves", "stars", "warp", "warp_dynamic", "aurora", "bars", "bars_full"}
        return val if val in valid else "particles"

    def set_visual_effect(self, effect: str) -> None:
        """Définit l'effet visuel configuré pour le lecteur."""
        valid = {"none", "particles", "waves", "stars", "warp", "warp_dynamic", "aurora", "bars", "bars_full"}
        if effect in valid:
            self.set(SECTION_PLAYER, KEY_VISUAL_EFFECT, effect)

    def get_player_position_ms(self) -> int:
        """Retourne la dernière position temporelle de lecture sauvegardée en ms (0 par défaut)."""
        val = self.get(SECTION_PLAYER, KEY_POSITION_MS, "0")
        try:
            return max(0, int(val))
        except Exception:
            return 0

    def set_player_position_ms(self, pos_ms: int) -> None:
        """Définit la dernière position temporelle de lecture en ms."""
        self.set(SECTION_PLAYER, KEY_POSITION_MS, str(max(0, pos_ms)))

    def get_blind_test_countdown(self) -> int:
        """Retourne la durée en secondes du décompte Blind Test (20s par défaut)."""
        val = self.get(SECTION_PLAYER, KEY_BLIND_TEST_COUNTDOWN, "20")
        try:
            return max(5, min(120, int(val)))
        except Exception:
            return 20

    def set_blind_test_countdown(self, seconds: int) -> None:
        """Définit la durée du décompte Blind Test en secondes."""
        self.set(SECTION_PLAYER, KEY_BLIND_TEST_COUNTDOWN, str(max(5, min(120, seconds))))

    def get_blind_test_reveal(self) -> int:
        """Retourne la durée en secondes de la découverte Blind Test (10s par défaut)."""
        val = self.get(SECTION_PLAYER, KEY_BLIND_TEST_REVEAL, "10")
        try:
            return max(3, min(60, int(val)))
        except Exception:
            return 10

    def set_blind_test_reveal(self, seconds: int) -> None:
        """Définit la durée de la découverte Blind Test en secondes."""
        self.set(SECTION_PLAYER, KEY_BLIND_TEST_REVEAL, str(max(3, min(60, seconds))))

    def get_blind_test_fade(self) -> int:
        """Retourne la durée en secondes du fondu sonore de fin de manche Blind Test (2s par défaut)."""
        val = self.get(SECTION_PLAYER, KEY_BLIND_TEST_FADE, "2")
        try:
            return max(0, min(10, int(val)))
        except Exception:
            return 2

    def set_blind_test_fade(self, seconds: int) -> None:
        """Définit la durée du fondu sonore Blind Test en secondes (0 à 10s)."""
        self.set(SECTION_PLAYER, KEY_BLIND_TEST_FADE, str(max(0, min(10, seconds))))

    def get_fade_in_track_enabled(self) -> bool:
        """Retourne True si le fondu est activé au lancement d'une piste (False par défaut)."""
        val = self.get(SECTION_PLAYER, KEY_FADE_IN_TRACK_ENABLED, "false")
        return str(val).lower() in ("true", "1", "yes", "on")

    def set_fade_in_track_enabled(self, enabled: bool) -> None:
        """Active ou désactive le fondu au lancement d'une piste."""
        self.set(SECTION_PLAYER, KEY_FADE_IN_TRACK_ENABLED, "true" if enabled else "false")

    def get_fade_in_track_duration(self) -> float:
        """Retourne la durée du fondu au lancement d'une piste en secondes (0.1 à 5.0, défaut 1.0)."""
        val = self.get(SECTION_PLAYER, KEY_FADE_IN_TRACK_DURATION, "1.0")
        try:
            return max(0.1, min(5.0, float(val)))
        except Exception:
            return 1.0

    def set_fade_in_track_duration(self, seconds: float) -> None:
        """Définit la durée du fondu au lancement d'une piste en secondes."""
        self.set(SECTION_PLAYER, KEY_FADE_IN_TRACK_DURATION, f"{max(0.1, min(5.0, seconds)):.1f}")

    def get_fade_in_resume_enabled(self) -> bool:
        """Retourne True si le fondu est activé à la reprise après pause (True par défaut)."""
        val = self.get(SECTION_PLAYER, KEY_FADE_IN_RESUME_ENABLED, "true")
        return str(val).lower() in ("true", "1", "yes", "on")

    def set_fade_in_resume_enabled(self, enabled: bool) -> None:
        """Active ou désactive le fondu à la reprise de lecture."""
        self.set(SECTION_PLAYER, KEY_FADE_IN_RESUME_ENABLED, "true" if enabled else "false")

    def get_fade_in_resume_duration(self) -> float:
        """Retourne la durée du fondu à la reprise de lecture en secondes (0.1 à 5.0, défaut 1.0)."""
        val = self.get(SECTION_PLAYER, KEY_FADE_IN_RESUME_DURATION, "1.0")
        try:
            return max(0.1, min(5.0, float(val)))
        except Exception:
            return 1.0

    def set_fade_in_resume_duration(self, seconds: float) -> None:
        """Définit la durée du fondu à la reprise de lecture en secondes."""
        self.set(SECTION_PLAYER, KEY_FADE_IN_RESUME_DURATION, f"{max(0.1, min(5.0, seconds)):.1f}")


# Instance singleton globale pour simplifier l'accès à travers l'application
_default_config_manager: ConfigManager | None = None


def get_config_manager(custom_path: str | Path | None = None) -> ConfigManager:
    """Fournit l'instance globale du ConfigManager."""
    global _default_config_manager
    if custom_path is not None:
        return ConfigManager(config_path=custom_path)
    current_path = get_config_path()
    if _default_config_manager is None or _default_config_manager.config_path != current_path:
        _default_config_manager = ConfigManager(config_path=current_path)
    return _default_config_manager
