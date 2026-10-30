"""Tests du chronométrage de démarrage."""

from __future__ import annotations

from pathlib import Path

import pytest

from amso.core import startup_timing
from amso.core.startup_timing import StartupClock


@pytest.fixture
def clean_logger():
    logger = startup_timing.logger
    yield logger
    for h in list(logger.handlers):
        h.close()
        logger.removeHandler(h)


def test_mark_etape_ecrit_duree_dans_startup_log(tmp_path: Path, monkeypatch, clean_logger) -> None:
    monkeypatch.setenv("AMSO_DATA_DIR", str(tmp_path))
    clock = StartupClock()
    clock.begin()
    step = clock.mark("etape test")
    for h in clean_logger.handlers:
        h.flush()

    content = (tmp_path / startup_timing.LOG_NAME).read_text(encoding="utf-8")
    assert step >= 0
    assert "Démarrage AMSO" in content
    assert "etape test" in content
    assert clock.steps[0][0] == "etape test"
