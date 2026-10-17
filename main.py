"""Audio Multi-Source Organizer (AMSO) — Point d'entrée principal."""

import sys
from pathlib import Path

from dotenv import load_dotenv
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

# Charger les variables d'environnement (.env)
load_dotenv()

# S'assurer que le package amso est importable
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from amso.core.database import DatabaseManager, get_database_path  # noqa: E402
from amso.core.i18n import get_i18n, tr  # noqa: E402
from amso.ui.views.main_window import MainWindow  # noqa: E402
from amso.ui.views.splash_screen import SplashScreen  # noqa: E402


def main() -> int:
    """Initialise la base locale, affiche l'écran de chargement et démarre l'interface graphique PySide6."""
    # Identification unique du processus Windows pour afficher l'icône personnalisée dans la barre des tâches
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("LEF97.AMSO.AudioOrganizer.1.0")
        except Exception:
            pass

    # 1. Initialisation prioritaire de l'application Qt pour affichage instantané du splash screen
    app = QApplication(sys.argv)
    app.setApplicationName("Audio Multi-Source Organizer")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("LEF97")

    # Icône officielle de l'application
    from amso.ui.theme import DARK_THEME_QSS, get_app_icon

    app_icon = get_app_icon()
    app.setWindowIcon(app_icon)

    # Typographie par défaut
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    # 2. Affichage immédiat de l'écran de chargement sans aucun écran blanc
    splash = SplashScreen()
    splash.show()
    app.processEvents()

    # Étape 1 : Préférences et internationalisation (20%)
    splash.set_progress(20, "Chargement des préférences et de la langue...")
    i18n = get_i18n()
    i18n.init_language()
    app.setApplicationName(tr("app.name"))

    # Étape 2 : Thème sombre (40%)
    splash.set_progress(40, tr("splash.loading_theme"))
    app.setStyleSheet(DARK_THEME_QSS)

    # Étape 3 : Persistance et base de données SQLite3 (60%)
    splash.set_progress(60, tr("splash.loading_db"))
    db_path = get_database_path()
    db = DatabaseManager(db_path=db_path)

    # Étape 4 : Construction de l'interface principale et restauration (85%)
    splash.set_progress(85, tr("splash.loading_ui"))
    window = MainWindow(db=db)
    window.setWindowIcon(app_icon)

    # Étape 5 : Finalisation (100%)
    splash.set_progress(100, tr("splash.ready"))

    # Affichage fluide de la fenêtre principale
    window.show()
    splash.finish(window)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
