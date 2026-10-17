"""Configuration globale pytest pour AMSO."""

import os

# Forcer Qt en mode offscreen pour tous les tests headless (CI Linux / macOS / Windows)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Isoler le fichier config.ini pour qu'aucun test n'écrase la configuration réelle de l'utilisateur
import tempfile
from pathlib import Path

import pytest

_isolated_test_cfg = Path(tempfile.gettempdir()) / "amso_pytest_isolated_config.ini"
os.environ["AMSO_CONFIG_PATH"] = str(_isolated_test_cfg)


@pytest.fixture(autouse=True)
def isolate_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Garantit une configuration vierge et isolée pour chaque test et réinitialise les singletons."""
    import amso.core.config as cfg_mod
    import amso.core.i18n as i18n_mod

    cfg_file = tmp_path / "config.ini"
    monkeypatch.setenv("AMSO_CONFIG_PATH", str(cfg_file))

    # Réinitialisation des singletons
    cfg_mod._default_config_manager = None
    i18n_mod._global_i18n = None

    yield

    cfg_mod._default_config_manager = None
    i18n_mod._global_i18n = None
