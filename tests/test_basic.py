"""Basic smoke tests for project structure and imports."""

import amso


def test_amso_version():
    """Verify package version is defined."""
    assert hasattr(amso, "__version__")
    assert amso.__version__ == "0.3.0"
