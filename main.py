"""Audio Multi-Source Organizer (AMSO) — Point d'entrée principal."""

import faulthandler
import sys
import threading

from amso.core.startup_timing import get_startup_clock  # importé en premier : fixe l'origine du chronométrage

# Sous Windows, définir l'AppUserModelID impérativement AVANT tout import Qt/GUI
# afin de garantir l'épinglage à la barre des tâches et le regroupement d'icônes
if sys.platform == "win32":
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("LEF97.AMSO.AudioPlayer")
    except Exception:
        pass

from pathlib import Path

from dotenv import load_dotenv
from PySide6.QtCore import QThread
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

# Charger les variables d'environnement (.env)
load_dotenv()

# S'assurer que le package amso est importable
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from amso import __version__  # noqa: E402
from amso.core.i18n import get_i18n, tr  # noqa: E402
from amso.core.pcm_mixer import prewarm_numpy  # noqa: E402
from amso.ui.views.splash_screen import SplashScreen  # noqa: E402


def main() -> int:
    """Initialise la base locale, affiche l'écran de chargement et démarre l'interface graphique PySide6."""
    startup_clock = get_startup_clock()
    startup_clock.begin()
    startup_clock.mark("imports (Qt, splash)")
    if "--debug-i18n" in sys.argv:
        from amso.core.i18n import set_debug_i18n

        set_debug_i18n(True)

    # Un crash natif (LibVLC, Qt Multimedia) ferme le processus sans exception Python : faulthandler
    # écrit la pile dans crash.log, seule trace exploitable ; le fichier doit rester ouvert jusqu'à la sortie.
    from amso.core.db.paths import get_default_data_dir

    crash_log = (get_default_data_dir() / "crash.log").open("a", encoding="utf-8")
    faulthandler.enable(file=crash_log, all_threads=True)

    # 1. Initialisation prioritaire de l'application Qt pour affichage instantané du splash screen
    app = QApplication(sys.argv)
    app.setApplicationName("Audio Multi-Source Organizer")
    app.setApplicationVersion(__version__)
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
    startup_clock.mark("QApplication + splash affiché")

    # Étape 1 : Préférences et internationalisation (15%)
    splash.set_progress(15, tr("splash.loading_config"))
    i18n = get_i18n()
    i18n.init_language()
    app.setApplicationName(tr("app.name"))
    startup_clock.mark("config + i18n")

    # Étape 2 : Thème sombre et ressources graphiques (25%)
    splash.set_progress(25, tr("splash.loading_theme"))
    app.setStyleSheet(DARK_THEME_QSS)
    startup_clock.mark("thème QSS")

    # Étape 3 : Base de données SQLite3 (35%)
    splash.set_progress(35, tr("splash.loading_db"))
    # Importés après l'affichage du splash : ces modules concentrent l'essentiel du temps d'import
    # (mutagen, VLC, toutes les pages), et le splash doit apparaître sans attendre.
    from amso.core.database import DatabaseManager, get_database_path
    from amso.ui.views.main_window import MainWindow

    startup_clock.mark("imports (DB, MainWindow)")
    db_path = get_database_path()
    db = DatabaseManager(db_path=db_path)
    startup_clock.mark("base SQLite (schéma)")

    # Étape 4 : Construction modulaire de l'interface et services (45% -> 90%)
    window = MainWindow(db=db, progress_callback=splash.set_progress)
    window.setWindowIcon(app_icon)
    startup_clock.mark("MainWindow (total)")

    # Étape 5 : Finalisation (100%)
    splash.set_progress(100, tr("splash.ready"))
    QThread.msleep(80)

    # Affichage fluide de la fenêtre principale
    window.show()
    splash.finish(window)
    startup_clock.mark("fenêtre affichée")

    # numpy est chargé hors du thread UI, une fois la fenêtre visible, avant le premier crossfade.
    threading.Thread(target=prewarm_numpy, daemon=True, name="NumpyPrewarm").start()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
