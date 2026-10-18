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
- Mettre à jour l'ensemble des fichiers Markdown dans les 5 langues officielles (FR, EN, ES, DE, IT) :
  - `CHANGELOG.*.md` : clôturer `[X.Y.Z-dev]` sous `## [X.Y.Z] - AAAA-MM-JJ` dans les 5 fichiers.
  - `README.*.md` : actualiser captures, badges, résumé et 13 lignes de fonctionnalités.
  - `ROADMAP.*.md` : pointer et cocher les objectifs atteints en vX.Y.Z et réajuster les jalons.
- Exécuter la vérification automatisée : `python scripts/check_docs_sync.py` (bloquant en CI si non synchronisé).
- Compiler avec `python scripts/build_exe.py` et préparer le dossier `dist/AMSO-Windows-vX.Y.Z/` contenant l'exe, les 15 `.md`, `locales/` et `LICENSE`.
- Créer l'archive `dist/AMSO-Windows-vX.Y.Z.zip` (à partir de v0.4.0+, étendre la GitHub Action pour packager également Linux `.AppImage` et macOS `.dmg`).
- Demander la validation manuelle de l'exécutable compilé à l'utilisateur.

### 3. Release (Publication)
- Committer et merger `develop` vers `main`.
- Créer le tag Git annoté `vX.Y.Z` et pousser les branches et tags (`git push origin main develop --tags`).
- Exécuter la publication automatisée sur GitHub : `python scripts/publish_github_release.py` (extraction changelog, captures, tableau et zip).
- Déploiement itch.io automatisé via GitHub Actions & Butler (clé secrète `BUTLER_API_KEY`).
- Sur Itch.io : vérifier que le canal `amso-windows.zip` est bien à jour, que les anciens fichiers obsolètes sont supprimés, et que le « Nom affiché » du build est configuré.
- **Devlog Itch.io obligatoire :** l'assistant DOIT obligatoirement rédiger et fournir à l'utilisateur le contenu complet du Devlog d'annonce en français et en anglais (bilingue) prêt à publier.


### 4. Post-release (Nouveau cycle dev)
- Revenir sur `develop`.
- Incrémenter la version vers le cycle suivant : `v(X).(Y+1).0-dev` dans `amso/__init__.py`.
- Ajouter la section `## [X.Y.Z-dev] - ...` en tête des 5 fichiers `CHANGELOG.*.md`.
- Valider l'alignement : `python scripts/check_docs_sync.py`.
- Nettoyer les caches et committer l'ouverture du cycle.
