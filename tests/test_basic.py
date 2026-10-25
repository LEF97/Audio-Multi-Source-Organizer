"""Basic smoke tests for project structure and imports."""

import re
import tomllib
from pathlib import Path

import amso


def test_amso_version():
    """Verify package version is defined, SemVer-formatted and identical to the one in pyproject.toml."""
    assert hasattr(amso, "__version__")
    assert re.fullmatch(r"\d+\.\d+\.\d+(-dev)?", amso.__version__)
    pyproject = tomllib.loads((Path(__file__).parent.parent / "pyproject.toml").read_text(encoding="utf-8"))
    assert amso.__version__ == pyproject["project"]["version"]
