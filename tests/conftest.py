"""Configuration globale pytest pour AMSO."""

import os

# Forcer Qt en mode offscreen pour tous les tests headless (CI Linux / macOS / Windows)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
