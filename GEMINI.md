# AMSO — Consignes pour l'assistant (économie de jetons)

Contexte projet : voir `context.md`. Ne pas le relire si déjà connu.

## Dossiers et fichiers à IGNORER (ne jamais lister, lire ni rechercher dedans)
- `.venv/`, `build/`, `dist/`, `__pycache__/`, `.git/`
- `.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`, `.coverage`
- `*.db`, `*.spec`, `Thumbs.db`
- `screenshots/`, `*.png`, `*.ico`, `*.icns` (ne lire une image que si demandé explicitement)
- `_work/`, `scratch/`

## Lecture de code
- Gros fichiers (`amso/ui/views/main_window.py` ~1500 lignes, `amso/services/player_service.py` ~1400, `folders_page.py` ~970, `player_view.py`, `blind_test_view.py`, `playlist_view.py`) : ne JAMAIS les lire en entier.
  Utiliser `grep_search` pour localiser, puis lire uniquement la plage de lignes nécessaire.
- Lancer les recherches avec `SearchPath` limité à `amso/` ou `tests/`, jamais à la racine.
- Ne pas relire un fichier déjà lu dans la conversation, sauf s'il a changé.

## Documentation multilingue
- Ne modifier les fichiers `*.fr/es/de/it.md` que pour une release ou sur demande explicite.
- Pour une modif de code courante, ne pas toucher README/CHANGELOG/ROADMAP.
- Utiliser `python scripts/check_docs_sync.py` plutôt que relire les 15 fichiers.

## Exécution et boucles
- Tests : lancer d'abord seulement les tests concernés (`pytest -q tests/<fichier>`), la suite complète uniquement avant release.
- Si un test, une compilation ou une commande échoue 2 fois de suite avec la même erreur, ARRÊTER et expliquer le problème à l'utilisateur au lieu de réessayer.
- Limiter les sorties de commandes (`| Select-Object -First 40`, `-q`).

## Style de travail
- Faire des modifications ciblées, pas de réécriture complète de fichier.
- Réponses concises, sans re-résumer ce qui vient d'être fait.
- Pour une release, appliquer la règle `.agents/rules/release_process.md`.

## Architecture : fichiers petits et cohésifs
- Cible : **< 500 lignes par fichier**, **< 60 lignes par fonction**. Au-delà de ~800 lignes, découper avant d'ajouter du code.
- Ne JAMAIS ajouter une nouvelle fonctionnalité dans un gros fichier existant : créer un module dédié et l'importer.
- Un module = une responsabilité. Placement :
  - `amso/core/` : logique métier pure, zéro Qt. `amso/core/db/` : un fichier par domaine (sources, pistes, playlists, journal...).
  - `amso/services/` : connecteurs externes et services (lecteur, mises à jour, VLC).
  - `amso/ui/pages/` : une page ou un contrôleur par fichier (mixins de `MainWindow`).
  - `amso/ui/widgets/` : widgets réutilisables. `amso/ui/dialogs/` : dialogues. `amso/ui/views/` : vues autonomes.
- Nouvelle page/contrôleur de `MainWindow` : créer un mixin dans `amso/ui/pages/` plutôt que d'agrandir `main_window.py`.
- Découpage = déplacement pur, sans modification de logique : commit séparé, `pytest -q` avant et après.
- Garder l'API publique stable : réexporter depuis l'ancien module (ex. `database.py` réexporte `db/models.py`).
- Éviter les imports circulaires : les widgets/types partagés vont dans un module neutre (`widgets/common.py`, `db/models.py`), jamais importés depuis `main_window.py`.
- Attention aux variables de module réaffectées via `global` (ex. `vlc` dans `player_service.py`) : ne pas les déplacer entre modules sans les encapsuler.

## Bonnes pratiques Python
- Python 3.11+, `from __future__ import annotations`, annotations de type partout (`mypy amso` doit passer).
- Formatage et lint : `ruff` (`ruff check`, `ruff format`) ; imports triés, aucun import inutilisé.
- Docstring courte sur chaque module, classe et fonction publique ; conserver les commentaires existants non concernés.
- Pas de logique dans `__init__.py`. Pas de variable globale mutable. Préférer `pathlib`, `dataclass(slots=True)`, `StrEnum`, f-strings.
- Pas de `except:` nu ni de `print` : utiliser `logging` (`logger = logging.getLogger(__name__)`).
- Qt : tout traitement long dans un `QThread`/worker, jamais dans le thread UI ; textes via `tr()` (clés dans `amso/locales/*.json`, 5 langues).
- SQL : requêtes paramétrées uniquement (jamais de f-string dans une requête).
- Tout nouveau comportement = test pytest correspondant dans `tests/`.
