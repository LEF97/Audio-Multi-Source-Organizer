# Règle : Protocole de Release et Publication AMSO

Pour toute demande concernant la préparation, la finalisation ou le déploiement d'une nouvelle version (release) du projet AMSO, l'assistant DOIT appliquer strictement le processus en 4 étapes défini dans `RELEASE_PROCESS.fr.md`.

## Déroulement obligatoire en 4 étapes

### 1. Pré-release / 1 (Recette & Qualité)
- Relister ce qui est prévu dans la release (fonctionnalités, améliorations, bugs corrigés).
- Auditer la qualité du code : `ruff check .`, `mypy amso`, `radon cc amso`.
- Exécuter la suite complète de tests de non-régression (`pytest -q`, 100% de réussite obligatoire).
- Demander la validation manuelle explicite de l'utilisateur avant de passer à l'étape suivante.

### 2. Pré-release / 2 (Packaging & Documentation)
- Sélectionner les screenshots selon la règle : captures de la version courante (`screenshots/*vX.Y.Z*.png`) + captures globales (`screenshots/Global*.png`).
- Passer la version officielle dans `amso/__init__.py` et `pyproject.toml` (retirer le suffixe `-dev`).
- Exécuter `python scripts/sync_translations.py` pour valider l'i18n.
- Mettre à jour les 3 fichiers Markdown : `CHANGELOG.fr.md`, `README.fr.md`, `ROADMAP.fr.md`.
- Compiler avec `python scripts/build_exe.py` et préparer le dossier `dist/AMSO-Windows-vX.Y.Z/` contenant l'exe et les 3 `.md`.
- Créer l'archive `dist/AMSO-Windows-vX.Y.Z.zip`.
- Demander la validation manuelle de l'exécutable compilé à l'utilisateur.

### 3. Release (Publication)
- Committer et merger `develop` vers `main`.
- Créer le tag Git annoté `vX.Y.Z` et pousser les branches et tags (`git push origin main develop --tags`).
- Accompagner l'utilisateur pour la publication sur GitHub Release (notes de changelog + zip en pièce jointe).
- Accompagner l'utilisateur pour le téléversement sur itch.io (zip + descriptions et screenshots).

### 4. Post-release (Nouveau cycle dev)
- Revenir sur `develop`.
- Incrémenter la version vers le cycle suivant : `v(X).(Y+1).0-dev` dans `amso/__init__.py`.
- Ajouter la section `## [X.Y.Z-dev] - En cours de développement` dans `CHANGELOG.fr.md`.
- Nettoyer les caches et committer l'ouverture du cycle.
