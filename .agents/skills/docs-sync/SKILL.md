---
name: docs-sync
description: Mise à jour de la documentation multilingue AMSO (README, CHANGELOG, ROADMAP, RELEASE_PROCESS en FR/EN/ES/DE/IT, soit 15 fichiers). À utiliser uniquement pour une release ou sur demande explicite de modifier la doc.
---

# Synchronisation de la documentation multilingue

Fichiers : `README.*.md`, `CHANGELOG.*.md`, `ROADMAP.*.md` (+ `RELEASE_PROCESS.*.md`) pour `fr`, `en`, `es`, `de`, `it`.
Pour une modif de code courante : **ne pas toucher** à ces fichiers.

## Procédure
1. Éditer d'abord la version française (`*.fr.md`), qui sert de référence.
2. Ne lire que les sections concernées (grep sur le titre `## [`, ou le badge/numéro de ligne), pas les 15 fichiers entiers.
3. Reporter la même modification structurelle dans les 4 autres langues (mêmes titres de section, même ordre, mêmes lignes, texte traduit).
4. Lancer `python scripts/check_docs_sync.py` : il détecte les écarts de structure. Corriger jusqu'à succès (bloquant en CI).
5. Si le script échoue 2 fois avec la même erreur, arrêter et expliquer.

## Conventions
- CHANGELOG : `## [X.Y.Z-dev] - AAAA-MM-JJ` en tête pendant le développement ; clôturé en `## [X.Y.Z]` à la release.
- README : 13 lignes de fonctionnalités, captures selon `screenshots/*vX.Y.Z*.png` et `screenshots/Global*.png`.
- ROADMAP : cocher les objectifs atteints, réajuster les jalons.
- Les textes d'interface se traduisent via le skill `add-i18n-key`, pas ici.
