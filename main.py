"""Audio Multi-Source Organizer (AMSO) — Point d'entrée principal."""

import os
from pathlib import Path
import sys

from dotenv import load_dotenv
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

# Charger les variables d'environnement (.env)
load_dotenv()

# S'assurer que le package amso est importable
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from amso.core.database import DatabaseManager, get_database_path
from amso.core.i18n import get_i18n, tr
from amso.ui.views.main_window import MainWindow


def main() -> int:
    """Initialise la base locale et démarre l'interface graphique PySide6."""
    db_path = get_database_path()

    # Initialisation de la persistance SQLite3 (crée les tables si nécessaire)
    db = DatabaseManager(db_path=db_path)

    # Initialisation de la langue et des préférences utilisateur
    i18n = get_i18n()
    i18n.init_language()

    # Initialisation de l'application Qt
    app = QApplication(sys.argv)
    app.setApplicationName(tr("app.name"))
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("LEF97")

    # Typographie par défaut
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    # Affichage de la fenêtre principale
    window = MainWindow(db=db)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
