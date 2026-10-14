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

from amso.core.database import DatabaseManager
from amso.ui.views.main_window import MainWindow


def main() -> int:
    """Initialise la base locale et démarre l'interface graphique PySide6."""
    db_path = os.getenv("AMSO_DB_PATH", "amso_library.db")

    # Initialisation de la persistance SQLite3 (crée les tables si nécessaire)
    db = DatabaseManager(db_path=db_path)

    # Initialisation de l'application Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Audio Multi-Source Organizer")
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
