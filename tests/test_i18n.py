"""Tests unitaires pour le système d'internationalisation (i18n) et de configuration INI."""

from pathlib import Path
from unittest.mock import patch

import pytest

from amso.core.config import ConfigManager
from amso.core.i18n import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    I18nManager,
    detect_os_language,
    get_locales_dir,
)


@pytest.fixture
def temp_config_file(tmp_path: Path) -> Path:
    """Fournit un chemin de fichier INI temporaire et isolé."""
    return tmp_path / "test_config.ini"


def test_config_manager_crud(temp_config_file: Path):
    """Vérifie la création, lecture, écriture et persistance dans config.ini."""
    assert not temp_config_file.exists()

    cfg = ConfigManager(temp_config_file)
    assert cfg.get_language() is None

    # Enregistrement d'une langue
    cfg.set_language("fr")
    assert temp_config_file.exists()
    assert cfg.get_language() == "fr"

    # Rechargement depuis le disque
    cfg2 = ConfigManager(temp_config_file)
    assert cfg2.get_language() == "fr"

    # Modification
    cfg2.set_language("es")
    assert cfg2.get_language() == "es"
    cfg3 = ConfigManager(temp_config_file)
    assert cfg3.get_language() == "es"


def test_detect_os_language_supported():
    """Vérifie que les langues prises en charge sont correctement reconnues."""
    with patch("locale.getlocale", return_value=("fr_FR", "cp1252")), \
         patch("sys.platform", "linux"):
        assert detect_os_language() == "fr"

    with patch("locale.getlocale", return_value=("es_ES", "utf-8")), \
         patch("sys.platform", "linux"):
        assert detect_os_language() == "es"

    with patch("locale.getlocale", return_value=("it_IT", "utf-8")), \
         patch("sys.platform", "linux"):
        assert detect_os_language() == "it"

    with patch("locale.getlocale", return_value=("de_DE", "utf-8")), \
         patch("sys.platform", "linux"):
        assert detect_os_language() == "de"

    with patch("locale.getlocale", return_value=("en_US", "utf-8")), \
         patch("sys.platform", "linux"):
        assert detect_os_language() == "en"


def test_detect_os_language_unsupported_defaults_to_english():
    """Vérifie qu'une langue non supportée (ex: japonais, russe) bascule sur l'anglais."""
    with patch("locale.getlocale", return_value=("ja_JP", "utf-8")), \
         patch("sys.platform", "linux"):
        assert detect_os_language() == DEFAULT_LANGUAGE

    with patch("locale.getlocale", return_value=("ru_RU", "utf-8")), \
         patch("sys.platform", "linux"):
        assert detect_os_language() == DEFAULT_LANGUAGE

    with patch("locale.getlocale", return_value=(None, None)), \
         patch("sys.platform", "linux"), \
         patch.dict("os.environ", {}, clear=True):
        assert detect_os_language() == DEFAULT_LANGUAGE


def test_first_run_persists_detected_language(temp_config_file: Path):
    """Au premier démarrage (sans ini), la langue de l'OS est détectée et enregistrée."""
    cfg = ConfigManager(temp_config_file)
    assert cfg.get_language() is None

    # Simuler un OS en français
    with patch("amso.core.i18n.detect_os_language", return_value="fr"):
        i18n = I18nManager(config_manager=cfg)
        assert i18n.current_language == "fr"
        # Vérifier que le choix est désormais persisté dans le fichier INI
        assert cfg.get_language() == "fr"

    # Deuxième démarrage : la langue du fichier INI doit être respectée même si l'OS change
    with patch("amso.core.i18n.detect_os_language", return_value="es"):
        i18n2 = I18nManager(config_manager=cfg)
        assert i18n2.current_language == "fr"


def test_first_run_unsupported_os_language_persists_english(temp_config_file: Path):
    """Au premier démarrage avec un OS non supporté, l'anglais par défaut est choisi et persisté."""
    cfg = ConfigManager(temp_config_file)
    assert cfg.get_language() is None

    with patch("amso.core.i18n.detect_os_language", return_value="en"):
        i18n = I18nManager(config_manager=cfg)
        assert i18n.current_language == "en"
        assert cfg.get_language() == "en"


def test_translation_lookups_and_fallback(temp_config_file: Path):
    """Vérifie les traductions, les variables interpolées et les mécanismes de repli."""
    cfg = ConfigManager(temp_config_file)
    i18n = I18nManager(config_manager=cfg)

    # Test en français
    i18n.set_language("fr")
    assert i18n.tr("sidebar.section_library") == "BIBLIOTHÈQUE"
    assert i18n.tr("table.col_title") == "Titre"
    assert i18n.tr("topbar.track_count", count="15") == "15 morceaux"

    # Test en anglais
    i18n.set_language("en")
    assert i18n.tr("sidebar.section_library") == "LIBRARY"
    assert i18n.tr("table.col_title") == "Title"
    assert i18n.tr("topbar.track_count", count="15") == "15 tracks"

    # Test en espagnol
    i18n.set_language("es")
    assert i18n.tr("sidebar.section_library") == "BIBLIOTECA"
    assert i18n.tr("table.col_title") == "Título"

    # Test en italien
    i18n.set_language("it")
    assert i18n.tr("sidebar.section_library") == "LIBRERIA"
    assert i18n.tr("table.col_title") == "Titolo"

    # Test clé inconnue -> retourne le fallback par défaut ou la clé brute
    assert i18n.tr("cle.totalement.inconnue") == "cle.totalement.inconnue"
    assert i18n.tr("cle.inconnue", default="Repli") == "Repli"


def test_all_locale_files_match_vf_reference():
    """Garantit que tous les fichiers de traduction possèdent 100% des clés de fr.json (VF)."""
    locales_dir = get_locales_dir()
    ref_path = locales_dir / "fr.json"
    assert ref_path.exists(), "Le fichier de référence fr.json doit exister"

    import json
    with open(ref_path, "r", encoding="utf-8") as f:
        ref_data = json.load(f)

    ref_keys = set(ref_data.keys())
    assert len(ref_keys) > 0

    # Vérifier chaque langue déclarée dans SUPPORTED_LANGUAGES
    for code in SUPPORTED_LANGUAGES.keys():
        target_path = locales_dir / f"{code}.json"
        assert target_path.exists(), f"Le fichier de langue {code}.json doit exister"
        with open(target_path, "r", encoding="utf-8") as f:
            target_data = json.load(f)

        target_keys = set(target_data.keys())
        missing_keys = ref_keys - target_keys
        extra_keys = target_keys - ref_keys

        assert not missing_keys, f"Clés manquantes dans {code}.json par rapport à fr.json : {missing_keys}"
        assert not extra_keys, f"Clés superflues dans {code}.json absentes de fr.json : {extra_keys}"


def test_dynamic_language_switch_notifies_listener(temp_config_file: Path):
    """Vérifie que changer la langue notifie les écouteurs enregistrés."""
    cfg = ConfigManager(temp_config_file)
    i18n = I18nManager(config_manager=cfg)

    events: list[str] = []

    def on_lang_changed(code: str):
        events.append(code)

    i18n.add_listener(on_lang_changed)

    i18n.set_language("es")
    assert events == ["es"]
    assert cfg.get_language() == "es"

    i18n.set_language("fr")
    assert events == ["es", "fr"]
    assert cfg.get_language() == "fr"

    i18n.remove_listener(on_lang_changed)
    i18n.set_language("en")
    assert events == ["es", "fr"]  # pas de nouvel événement après déréférencement
