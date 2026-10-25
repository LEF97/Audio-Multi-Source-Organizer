---
name: qt-threading
description: Traitements longs et signaux dans l'interface PySide6 d'AMSO (QThread, workers, Signal/Slot, cycle de vie des objets). À utiliser dès qu'une tâche (scan, réseau, métadonnées, I/O) doit s'exécuter sans bloquer l'UI.
---

# Threads et signaux PySide6

## Règles
- Aucun traitement long (scan, lecture de tags, réseau, SQL volumineux) dans le thread UI.
- Modèle : un `QObject` worker (`run()` + signaux `progress`, `finished`, `error`) déplacé dans un `QThread` via `moveToThread`, ou `QRunnable` + `QThreadPool` pour les petites tâches.
- Le worker ne touche **jamais** un widget : il émet un `Signal`, c'est le slot (thread UI) qui met à jour l'interface.
- Les connexions worker → UI sont queued automatiquement entre threads ; ne pas appeler directement les méthodes de l'UI depuis le worker.

## Cycle de vie
- Garder une référence au thread et au worker (attribut de l'objet) tant qu'ils tournent, sinon destruction prématurée.
- Fin propre : `worker.finished → thread.quit`, puis `worker.deleteLater` et `thread.deleteLater`.
- À la fermeture de la fenêtre : demander l'arrêt (drapeau `cancel` testé dans la boucle), `thread.quit(); thread.wait()`.
- Une erreur dans un worker : attraper, `logger.exception(...)`, émettre `error(str)` ; ne jamais laisser l'exception tuer le thread silencieusement.

## SQLite
Une connexion SQLite par thread (ne pas partager l'objet de connexion entre threads) ; passer par `DatabaseManager` selon le motif existant.

## Existant à imiter
Voir `amso/ui/pages/scan_controller.py` et `amso/core/scanner.py` avant de créer un nouveau worker (`grep_search "QThread"` dans `amso/`).

## Tests
Tester la logique du worker sans Qt quand c'est possible ; pour l'intégration, utiliser `qtbot`-like avec `QEventLoop`/`QSignalSpy` en mode offscreen, avec timeout.
