"""Configuration globale pytest pour AMSO."""

import os

# Forcer Qt en mode offscreen pour tous les tests headless (CI Linux / macOS / Windows)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Isoler complètement l'environnement AMSO (data dir, config, playlist, DB)
# pour qu'aucun test n'écrase ni ne pollue les fichiers réels de l'utilisateur (%APPDATA%\AMSO).
import tempfile
from pathlib import Path

import pytest

_isolated_test_dir = Path(tempfile.gettempdir()) / "amso_pytest_isolated_global"
_isolated_test_dir.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("AMSO_DATA_DIR", str(_isolated_test_dir))
os.environ.setdefault("AMSO_CONFIG_PATH", str(_isolated_test_dir / "config.ini"))
os.environ.setdefault("AMSO_PLAYLIST_PATH", str(_isolated_test_dir / "saved_playlist.json"))
os.environ.setdefault("AMSO_DB_PATH", str(_isolated_test_dir / "isolated_test.db"))


@pytest.fixture(autouse=True)
def isolate_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Garantit un environnement vierge et totalement isolé pour chaque test et réinitialise les singletons."""
    import amso.core.config as cfg_mod
    import amso.core.i18n as i18n_mod

    test_data_dir = tmp_path / "amso_test_data"
    test_data_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("AMSO_DATA_DIR", str(test_data_dir))
    monkeypatch.setenv("AMSO_CONFIG_PATH", str(test_data_dir / "config.ini"))
    monkeypatch.setenv("AMSO_PLAYLIST_PATH", str(test_data_dir / "saved_playlist.json"))
    monkeypatch.setenv("AMSO_DB_PATH", str(test_data_dir / "amso_library.db"))

    # Réinitialisation des singletons
    cfg_mod._default_config_manager = None
    i18n_mod._global_i18n = None

    yield

    cfg_mod._default_config_manager = None
    i18n_mod._global_i18n = None


@pytest.fixture(autouse=True)
def close_audio_output_threads(monkeypatch: pytest.MonkeyPatch):
    """Ferme à la fin de chaque test les threads audio (QAudioSink) des moteurs créés.

    Les PlayerService de test ne sont libérés qu'au ramasse-miettes : sans cela, les threads et sorties audio
    s'accumulent sur la suite complète et finissent par faire échouer `libvlc_new` (abort natif).
    """
    from amso.services.audio_output import SinkOutput

    created: list[SinkOutput] = []
    original_init = SinkOutput.__init__

    def tracking_init(self: SinkOutput, *args, **kwargs) -> None:
        original_init(self, *args, **kwargs)
        created.append(self)

    monkeypatch.setattr(SinkOutput, "__init__", tracking_init)
    yield
    for output in created:
        output.shutdown()
