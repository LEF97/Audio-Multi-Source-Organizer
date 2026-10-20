# AMSO — Consignes pour l'assistant (économie de jetons)

Contexte projet : voir `context.md`. Ne pas le relire si déjà connu.

## Dossiers et fichiers à IGNORER (ne jamais lister, lire ni rechercher dedans)
- `.venv/`, `build/`, `dist/`, `__pycache__/`, `.git/`
- `.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`, `.coverage`
- `*.db`, `*.spec`, `Thumbs.db`
- `screenshots/`, `*.png`, `*.ico`, `*.icns` (ne lire une image que si demandé explicitement)
- `_work/`, `scratch/`

## Lecture de code
- Les gros fichiers (`amso/ui/views/main_window.py` ~4200 lignes, `amso/core/database.py`, `blind_test_view.py`, `player_service.py`, `visual_effects.py`) : ne JAMAIS les lire en entier.
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
