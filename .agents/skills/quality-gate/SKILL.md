---
name: quality-gate
description: Contrôle qualité avant de conclure une modification de code AMSO (ruff, mypy, pytest ciblé, tailles de fichiers, checklist). À utiliser à la fin de toute tâche qui modifie du code Python, ou quand l'utilisateur demande une vérification/revue.
---

# Quality gate (sorties courtes)

Exécuter depuis la racine, avec le venv (`.venv\Scripts\...`). Toujours limiter les sorties.

1. `ruff check amso tests --output-format concise | Select-Object -First 30`
2. `ruff format --check amso tests` (ne reformater que les fichiers touchés : `ruff format <fichiers>`).
3. `mypy amso | Select-Object -Last 15`
4. `pytest -q tests/<fichiers concernés>` (suite complète seulement avant release).
5. `python scripts/check_file_sizes.py` : aucun fichier touché ne doit dépasser 500 lignes ni introduire de fonction > 60 lignes.

6. `python scripts/check_context.py` : `context.md` doit refléter les modules créés/déplacés (skill `update-context`).

## Checklist de relecture (sur le diff uniquement, pas de relecture complète)
- Pas de `except:` nu, de `print`, ni de `except Exception: pass` silencieux (au minimum `logger.exception`).
- Pas de duplication d'une fonction existante : `grep_search` avant d'en créer une.
- SQL paramétré ; pas de secret, jeton ou chemin utilisateur en dur.
- Traitements longs hors du thread UI ; textes visibles via `tr()` (skill `add-i18n-key`).
- Nouveau comportement = test correspondant (skill `write-tests`).
- Annotations de type et docstring courte sur toute fonction publique ; commentaires existants conservés.

## Arrêt
Même erreur 2 fois de suite : arrêter et expliquer à l'utilisateur.
Conclure en une phrase : outils passés/échoués, sans re-résumer le diff.
