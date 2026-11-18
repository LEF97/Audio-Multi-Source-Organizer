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
from collections.abc import Iterator
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
KEY_BLIND_TEST_VISUAL_EFFECT = "blind_test_visual_effect"
KEY_ENABLED_EFFECTS_PLAYER = "enabled_effects_player"
KEY_ENABLED_EFFECTS_BLIND_TEST = "enabled_effects_blind_test"
KEY_VISUAL_EFFECT_RANDOM_INTERVAL = "visual_effect_random_interval"
KEY_BLIND_TEST_VISUAL_EFFECT_RANDOM_INTERVAL = "blind_test_visual_effect_random_interval"
KEY_POSITION_MS = "position_ms"

VISUAL_EFFECT_IDS = (
    "none",
    "particles",
    "waves",
    "stars",
    "warp",
    "warp_dynamic",
    "aurora",
    "bars",
    "bars_full",
)
VALID_VISUAL_EFFECTS = set(VISUAL_EFFECT_IDS) | {"random"}
RANDOM_EFFECT_INTERVALS = ("track", "15", "30", "60", "120", "300")
KEY_BLIND_TEST_COUNTDOWN = "blind_test_countdown"
KEY_BLIND_TEST_REVEAL = "blind_test_reveal"
KEY_BLIND_TEST_FADE = "blind_test_fade"
KEY_FADE_IN_TRACK_ENABLED = "fade_in_track_enabled"
KEY_FADE_IN_TRACK_DURATION = "fade_in_track_duration"
KEY_FADE_IN_RESUME_ENABLED = "fade_in_resume_enabled"
KEY_FADE_IN_RESUME_DURATION = "fade_in_resume_duration"
KEY_AUDIO_ENGINE = "audio_engine"
KEY_AUDIO_OUTPUT_DEVICE = "audio_output_device"
KEY_EQ_ENABLED = "eq_enabled"
KEY_EQ_PRESET = "eq_preset"
KEY_EQ_BANDS = "eq_bands"
KEY_REPLAYGAIN_ENABLED = "replaygain_enabled"
KEY_VLC_GAPLESS_LATENCY = "vlc_gapless_latency_ms"
KEY_COVER_TRANSITION = "cover_transition"

COVER_TRANSITION_MODES = ("fade", "slide", "zoom", "flip", "none")

SECTION_UI = "UI"
KEY_WINDOW_WIDTH = "window_width"
KEY_WINDOW_HEIGHT = "window_height"
KEY_WINDOW_X = "window_x"
KEY_WINDOW_Y = "window_y"
KEY_WINDOW_MAXIMIZED = "window_maximized"
KEY_SIDEBAR_WIDTH = "sidebar_width"
DEFAULT_SIDEBAR_WIDTH = 240
# Bornes alignées sur min-width / max-width de QFrame#sidebarFrame (qss_base.py)
MIN_SIDEBAR_WIDTH = 170
MAX_SIDEBAR_WIDTH = 320
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 780
MIN_WINDOW_WIDTH = 950
MIN_WINDOW_HEIGHT = 620


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


_INT64_MAX = 2**63 - 1


class ConfigManager:
    """Gestionnaire de lecture/écriture du fichier config.ini."""

    def __init__(self, config_path: str | Path | None = None) -> None:
        if config_path is None:
            self.config_path = get_config_path()
        else:
            self.config_path = Path(config_path).resolve()

        self._config = configparser.ConfigParser()
        self._batch_depth = 0
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

    @contextlib.contextmanager
    def batch(self) -> Iterator[None]:
        """Regroupe plusieurs écritures de configuration en une seule sauvegarde disque."""
        self._batch_depth += 1
        try:
            yield
        finally:
            self._batch_depth -= 1
            if self._batch_depth == 0:
                self.save()

    def set(self, section: str, key: str, value: str) -> None:
        """Définit une valeur de configuration et persiste sur le disque."""
        if not self._config.has_section(section):
            self._config.add_section(section)
        self._config.set(section, key, str(value))
        if self._batch_depth == 0:
            self.save()

    def _get_bool(self, section: str, key: str, default: bool) -> bool:
        val = self.get(section, key)
        if val is None:
            return default
        return val.lower() in ("true", "1", "yes", "on")

    def _set_bool(self, section: str, key: str, value: bool) -> None:
        self.set(section, key, "true" if value else "false")

    def _get_int(self, section: str, key: str, default: int, lo: int, hi: int) -> int:
        """Entier borné à [lo, hi] ; `default` si la valeur est absente ou illisible."""
        try:
            return max(lo, min(hi, int(self.get(section, key, str(default)))))
        except ValueError:
            return default

    def _get_float(self, section: str, key: str, default: float, lo: float, hi: float) -> float:
        try:
            return max(lo, min(hi, float(self.get(section, key, str(default)))))
        except ValueError:
            return default

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
            "library_sources",
            "settings_player",
            "settings_effects",
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

    def get_audio_output_device(self) -> str:
        """Retourne l'identifiant du périphérique de sortie audio ('auto' par défaut)."""
        val = self.get(SECTION_PLAYER, KEY_AUDIO_OUTPUT_DEVICE, "auto")
        return str(val).strip() or "auto"

    def set_audio_output_device(self, device_id: str) -> None:
        """Persiste l'identifiant du périphérique de sortie audio ('auto' ou id hex)."""
        self.set(SECTION_PLAYER, KEY_AUDIO_OUTPUT_DEVICE, (device_id or "auto").strip() or "auto")

    def get_eq_enabled(self) -> bool:
        """Retourne True si l'égaliseur logiciel est activé."""
        return self._get_bool(SECTION_PLAYER, KEY_EQ_ENABLED, False)

    def set_eq_enabled(self, enabled: bool) -> None:
        """Persiste l'activation de l'égaliseur logiciel."""
        self._set_bool(SECTION_PLAYER, KEY_EQ_ENABLED, enabled)

    def get_eq_preset(self) -> str:
        """Retourne le nom du préset d'égaliseur actif ('flat' par défaut)."""
        val = self.get(SECTION_PLAYER, KEY_EQ_PRESET, "flat")
        return str(val).strip() or "flat"

    def set_eq_preset(self, preset: str) -> None:
        """Persiste le préset d'égaliseur actif."""
        self.set(SECTION_PLAYER, KEY_EQ_PRESET, (preset or "flat").strip() or "flat")

    def get_eq_bands(self) -> list[float]:
        """Retourne les 10 gains d'égaliseur en dB (0.0 par défaut)."""
        raw = str(self.get(SECTION_PLAYER, KEY_EQ_BANDS, ""))
        if not raw.strip():
            return [0.0] * 10
        parts = raw.split(",")
        if len(parts) != 10:
            return [0.0] * 10
        try:
            return [max(-12.0, min(12.0, float(p))) for p in parts]
        except ValueError:
            return [0.0] * 10

    def set_eq_bands(self, bands: list[float]) -> None:
        """Persiste les 10 gains d'égaliseur en dB."""
        clamped = [f"{max(-12.0, min(12.0, float(g))):.1f}" for g in (bands[:10] + [0.0] * 10)[:10]]
        self.set(SECTION_PLAYER, KEY_EQ_BANDS, ",".join(clamped))

    def get_replaygain_enabled(self) -> bool:
        """Retourne True si la normalisation ReplayGain est activée."""
        return self._get_bool(SECTION_PLAYER, KEY_REPLAYGAIN_ENABLED, False)

    def set_replaygain_enabled(self, enabled: bool) -> None:
        """Persiste l'activation de la normalisation ReplayGain."""
        self._set_bool(SECTION_PLAYER, KEY_REPLAYGAIN_ENABLED, enabled)

    def get_vlc_gapless_latency(self) -> int:
        """Retourne la latence DirectSound/LibVLC en ms pour le gapless 0 (défaut : 250)."""
        return self._get_int(SECTION_PLAYER, KEY_VLC_GAPLESS_LATENCY, 250, 0, 2000)

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
        return self._get_int(SECTION_PLAYER, KEY_CROSSFADE_SECONDS, 3, 1, 20)

    def set_crossfade_duration(self, seconds: int) -> None:
        """Définit la durée du fondu enchaîné en secondes (1 à 20)."""
        self.set(SECTION_PLAYER, KEY_CROSSFADE_SECONDS, str(max(1, min(20, seconds))))

    def get_player_shuffle(self) -> bool:
        """Retourne True si la lecture aléatoire était activée (False par défaut)."""
        return self._get_bool(SECTION_PLAYER, KEY_SHUFFLE, False)

    def set_player_shuffle(self, enabled: bool) -> None:
        """Définit l'état de la lecture aléatoire."""
        self._set_bool(SECTION_PLAYER, KEY_SHUFFLE, enabled)

    def get_player_repeat_mode(self) -> int:
        """Retourne le mode de boucle (0=OFF, 1=ALL, 2=ONE). 0 par défaut."""
        try:
            return int(self.get(SECTION_PLAYER, KEY_REPEAT_MODE, "0")) % 3
        except ValueError:
            return 0

    def set_player_repeat_mode(self, mode: int) -> None:
        """Définit le mode de boucle."""
        self.set(SECTION_PLAYER, KEY_REPEAT_MODE, str(mode % 3))

    def get_player_volume(self) -> int:
        """Retourne le volume sonore sauvegardé (0 à 100). 80 par défaut."""
        return self._get_int(SECTION_PLAYER, KEY_VOLUME, 80, 0, 100)

    def set_player_volume(self, volume: int) -> None:
        """Définit le volume sonore."""
        self.set(SECTION_PLAYER, KEY_VOLUME, str(max(0, min(100, volume))))

    def get_player_muted(self) -> bool:
        """Retourne True si le son était en sourdine (False par défaut)."""
        return self._get_bool(SECTION_PLAYER, KEY_MUTED, False)

    def set_player_muted(self, muted: bool) -> None:
        """Définit l'état de la sourdine."""
        self._set_bool(SECTION_PLAYER, KEY_MUTED, muted)

    def get_visual_effect(self) -> str:
        """Retourne l'effet visuel configuré pour le lecteur ('particles' par défaut)."""
        val = self.get(SECTION_PLAYER, KEY_VISUAL_EFFECT, "particles")
        return val if val in VALID_VISUAL_EFFECTS else "particles"

    def set_visual_effect(self, effect: str) -> None:
        """Définit l'effet visuel configuré pour le lecteur."""
        if effect in VALID_VISUAL_EFFECTS:
            self.set(SECTION_PLAYER, KEY_VISUAL_EFFECT, effect)

    def get_blind_test_visual_effect(self) -> str:
        """Retourne l'effet visuel configuré pour le Blind Test."""
        val = self.get(SECTION_PLAYER, KEY_BLIND_TEST_VISUAL_EFFECT)
        if val in VALID_VISUAL_EFFECTS:
            return str(val)
        return self.get_visual_effect()

    def set_blind_test_visual_effect(self, effect: str) -> None:
        """Définit l'effet visuel configuré pour le Blind Test."""
        if effect in VALID_VISUAL_EFFECTS:
            self.set(SECTION_PLAYER, KEY_BLIND_TEST_VISUAL_EFFECT, effect)

    def get_enabled_effects(self, context: str) -> list[str]:
        """Retourne la liste ordonnée des effets activés pour 'player' ou 'blind_test'."""
        key = KEY_ENABLED_EFFECTS_BLIND_TEST if context == "blind_test" else KEY_ENABLED_EFFECTS_PLAYER
        raw = self.get(SECTION_PLAYER, key)
        if raw is None or not str(raw).strip():
            return list(VISUAL_EFFECT_IDS)
        selected = {item.strip() for item in str(raw).split(",") if item.strip()}
        filtered = [eff for eff in VISUAL_EFFECT_IDS if eff in selected]
        return filtered if filtered else list(VISUAL_EFFECT_IDS)

    def set_enabled_effects(self, context: str, effects: list[str]) -> None:
        """Persiste la liste des effets activés pour 'player' ou 'blind_test'."""
        key = KEY_ENABLED_EFFECTS_BLIND_TEST if context == "blind_test" else KEY_ENABLED_EFFECTS_PLAYER
        selected = set(effects)
        ordered = [eff for eff in VISUAL_EFFECT_IDS if eff in selected]
        if not ordered:
            ordered = ["none"]
        self.set(SECTION_PLAYER, key, ",".join(ordered))

    def get_visual_effect_random_interval(self, context: str = "player") -> str:
        """Retourne la fréquence du mode aléatoire ('track', '15', '30', '60', '120', '300') par contexte."""
        if context == "blind_test":
            val = self.get(SECTION_PLAYER, KEY_BLIND_TEST_VISUAL_EFFECT_RANDOM_INTERVAL, "track")
            return val if val in RANDOM_EFFECT_INTERVALS else "track"
        val = self.get(SECTION_PLAYER, KEY_VISUAL_EFFECT_RANDOM_INTERVAL, "30")
        return val if val in RANDOM_EFFECT_INTERVALS else "30"

    def set_visual_effect_random_interval(self, interval: str, context: str = "player") -> None:
        """Persiste la fréquence de changement du mode aléatoire pour un contexte."""
        if interval in RANDOM_EFFECT_INTERVALS:
            key = (
                KEY_BLIND_TEST_VISUAL_EFFECT_RANDOM_INTERVAL
                if context == "blind_test"
                else KEY_VISUAL_EFFECT_RANDOM_INTERVAL
            )
            self.set(SECTION_PLAYER, key, interval)

    def get_cover_transition(self) -> str:
        """Retourne l'effet de transition de pochette configuré ('fade', 'slide', 'zoom', 'flip', 'none')."""
        val = self.get(SECTION_PLAYER, KEY_COVER_TRANSITION, "fade")
        return val if val in COVER_TRANSITION_MODES else "fade"

    def set_cover_transition(self, mode: str) -> None:
        """Définit l'effet de transition lors d'un changement de pochette."""
        if mode in COVER_TRANSITION_MODES:
            self.set(SECTION_PLAYER, KEY_COVER_TRANSITION, mode)

    def get_player_position_ms(self) -> int:
        """Retourne la dernière position temporelle de lecture sauvegardée en ms (0 par défaut)."""
        return self._get_int(SECTION_PLAYER, KEY_POSITION_MS, 0, 0, _INT64_MAX)

    def set_player_position_ms(self, pos_ms: int) -> None:
        """Définit la dernière position temporelle de lecture en ms."""
        self.set(SECTION_PLAYER, KEY_POSITION_MS, str(max(0, pos_ms)))

    def get_blind_test_countdown(self) -> int:
        """Retourne la durée en secondes du décompte Blind Test (20s par défaut)."""
        return self._get_int(SECTION_PLAYER, KEY_BLIND_TEST_COUNTDOWN, 20, 5, 120)

    def set_blind_test_countdown(self, seconds: int) -> None:
        """Définit la durée du décompte Blind Test en secondes."""
        self.set(SECTION_PLAYER, KEY_BLIND_TEST_COUNTDOWN, str(max(5, min(120, seconds))))

    def get_blind_test_reveal(self) -> int:
        """Retourne la durée en secondes de la découverte Blind Test (10s par défaut)."""
        return self._get_int(SECTION_PLAYER, KEY_BLIND_TEST_REVEAL, 10, 3, 60)

    def set_blind_test_reveal(self, seconds: int) -> None:
        """Définit la durée de la découverte Blind Test en secondes."""
        self.set(SECTION_PLAYER, KEY_BLIND_TEST_REVEAL, str(max(3, min(60, seconds))))

    def get_blind_test_fade(self) -> int:
        """Retourne la durée en secondes du fondu sonore de fin de manche Blind Test (2s par défaut)."""
        return self._get_int(SECTION_PLAYER, KEY_BLIND_TEST_FADE, 2, 0, 10)

    def set_blind_test_fade(self, seconds: int) -> None:
        """Définit la durée du fondu sonore Blind Test en secondes (0 à 10s)."""
        self.set(SECTION_PLAYER, KEY_BLIND_TEST_FADE, str(max(0, min(10, seconds))))

    def get_fade_in_track_enabled(self) -> bool:
        """Retourne True si le fondu est activé au lancement d'une piste (False par défaut)."""
        return self._get_bool(SECTION_PLAYER, KEY_FADE_IN_TRACK_ENABLED, False)

    def set_fade_in_track_enabled(self, enabled: bool) -> None:
        """Active ou désactive le fondu au lancement d'une piste."""
        self._set_bool(SECTION_PLAYER, KEY_FADE_IN_TRACK_ENABLED, enabled)

    def get_fade_in_track_duration(self) -> float:
        """Retourne la durée du fondu au lancement d'une piste en secondes (0.1 à 5.0, défaut 1.0)."""
        return self._get_float(SECTION_PLAYER, KEY_FADE_IN_TRACK_DURATION, 1.0, 0.1, 5.0)

    def set_fade_in_track_duration(self, seconds: float) -> None:
        """Définit la durée du fondu au lancement d'une piste en secondes."""
        self.set(SECTION_PLAYER, KEY_FADE_IN_TRACK_DURATION, f"{max(0.1, min(5.0, seconds)):.1f}")

    def get_fade_in_resume_enabled(self) -> bool:
        """Retourne True si le fondu est activé à la reprise après pause (True par défaut)."""
        return self._get_bool(SECTION_PLAYER, KEY_FADE_IN_RESUME_ENABLED, True)

    def set_fade_in_resume_enabled(self, enabled: bool) -> None:
        """Active ou désactive le fondu à la reprise de lecture."""
        self._set_bool(SECTION_PLAYER, KEY_FADE_IN_RESUME_ENABLED, enabled)

    def get_fade_in_resume_duration(self) -> float:
        """Retourne la durée du fondu à la reprise de lecture en secondes (0.1 à 5.0, défaut 1.0)."""
        return self._get_float(SECTION_PLAYER, KEY_FADE_IN_RESUME_DURATION, 1.0, 0.1, 5.0)

    def set_fade_in_resume_duration(self, seconds: float) -> None:
        """Définit la durée du fondu à la reprise de lecture en secondes."""
        self.set(SECTION_PLAYER, KEY_FADE_IN_RESUME_DURATION, f"{max(0.1, min(5.0, seconds)):.1f}")

    def get_library_sources_expanded_nodes(self) -> list[str]:
        """Retourne la liste des clés de nœuds dépliés dans la page Gestion de la bibliothèque > Sources."""
        raw = self.get(SECTION_UI, "library_sources_expanded", "")
        if not raw:
            return []
        return [part.strip() for part in str(raw).split(",") if part.strip()]

    def set_library_sources_expanded_nodes(self, node_keys: list[str]) -> None:
        """Persiste la liste des clés de nœuds dépliés dans Gestion de la bibliothèque > Sources."""
        clean = [k.strip() for k in node_keys if k and k.strip()]
        self.set(SECTION_UI, "library_sources_expanded", ",".join(clean))

    def get_window_size(self) -> tuple[int, int]:
        """Retourne la taille mémorisée en mode fenêtré (largeur, hauteur)."""
        raw_w = self.get(SECTION_UI, KEY_WINDOW_WIDTH)
        raw_h = self.get(SECTION_UI, KEY_WINDOW_HEIGHT)
        try:
            w = int(raw_w) if raw_w is not None else DEFAULT_WINDOW_WIDTH
            h = int(raw_h) if raw_h is not None else DEFAULT_WINDOW_HEIGHT
        except (ValueError, TypeError):
            return (DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        return (max(MIN_WINDOW_WIDTH, w), max(MIN_WINDOW_HEIGHT, h))

    def get_window_position(self) -> tuple[int, int] | None:
        """Retourne la position mémorisée en mode fenêtré (x, y) ou None si absente/invalide."""
        raw_x = self.get(SECTION_UI, KEY_WINDOW_X)
        raw_y = self.get(SECTION_UI, KEY_WINDOW_Y)
        if raw_x is None or raw_y is None:
            return None
        try:
            return (int(raw_x), int(raw_y))
        except (ValueError, TypeError):
            return None

    def get_sidebar_width(self) -> int:
        """Largeur du menu de gauche choisie par l'utilisateur (défaut si absente ou invalide)."""
        raw = self.get(SECTION_UI, KEY_SIDEBAR_WIDTH)
        try:
            width = int(raw) if raw is not None else DEFAULT_SIDEBAR_WIDTH
        except (ValueError, TypeError):
            return DEFAULT_SIDEBAR_WIDTH
        return max(MIN_SIDEBAR_WIDTH, min(MAX_SIDEBAR_WIDTH, width))

    def set_sidebar_width(self, width: int) -> None:
        """Persiste la largeur du menu de gauche."""
        if not self._config.has_section(SECTION_UI):
            self._config.add_section(SECTION_UI)
        self._config.set(SECTION_UI, KEY_SIDEBAR_WIDTH, str(max(MIN_SIDEBAR_WIDTH, min(MAX_SIDEBAR_WIDTH, int(width)))))
        if self._batch_depth == 0:
            self.save()

    def get_window_maximized(self) -> bool:
        """Retourne True si la fenêtre était agrandie lors de la dernière fermeture."""
        return self._get_bool(SECTION_UI, KEY_WINDOW_MAXIMIZED, False)

    def set_window_state(
        self,
        width: int,
        height: int,
        maximized: bool,
        x: int | None = None,
        y: int | None = None,
    ) -> None:
        """Persiste la taille, la position en mode fenêtré et l'état agrandi en une seule écriture."""
        if not self._config.has_section(SECTION_UI):
            self._config.add_section(SECTION_UI)
        self._config.set(SECTION_UI, KEY_WINDOW_WIDTH, str(max(MIN_WINDOW_WIDTH, int(width))))
        self._config.set(SECTION_UI, KEY_WINDOW_HEIGHT, str(max(MIN_WINDOW_HEIGHT, int(height))))
        if x is not None and y is not None:
            self._config.set(SECTION_UI, KEY_WINDOW_X, str(int(x)))
            self._config.set(SECTION_UI, KEY_WINDOW_Y, str(int(y)))
        self._config.set(SECTION_UI, KEY_WINDOW_MAXIMIZED, "true" if maximized else "false")
        if self._batch_depth == 0:
            self.save()


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
