---
name: release
description: Protocole de release AMSO en 4 étapes (recette, packaging, publication, nouveau cycle dev). À utiliser pour toute demande de release, nouvelle version, tag, publication GitHub/itch.io, changelog de version, devlog.
---

# Protocole de Release et Publication AMSO

Appliquer strictement les 4 étapes ci-dessous (référence : `RELEASE_PROCESS.fr.md`).
Ne lire les 15 fichiers `.md` multilingues que dans cette procédure ; utiliser `scripts/check_docs_sync.py` pour vérifier.

## 1. Pré-release / 1 (Recette & Qualité)
- Relister ce qui est prévu dans la release (fonctionnalités, améliorations, bugs corrigés).
- Auditer la qualité du code : `ruff check .`, `mypy amso`, `radon cc amso`.
- Exécuter la suite complète : `pytest -q` (100 % de réussite obligatoire).
- Demander la validation manuelle explicite de l'utilisateur avant de continuer.

## 2. Pré-release / 2 (Packaging & Documentation)
- Screenshots : captures de la version courante (`screenshots/*vX.Y.Z*.png`) + globales (`screenshots/Global*.png`).
- Passer la version officielle dans `amso/__init__.py` et `pyproject.toml` (retirer le suffixe `-dev`).
- `python scripts/sync_translations.py` pour valider l'i18n.
- Mettre à jour les Markdown dans les 5 langues (FR, EN, ES, DE, IT) :
  - `CHANGELOG.*.md` : clôturer `[X.Y.Z-dev]` sous `## [X.Y.Z] - AAAA-MM-JJ` dans les 5 fichiers.
  - `README.*.md` : captures, badges, résumé et 13 lignes de fonctionnalités.
  - `ROADMAP.*.md` : cocher les objectifs atteints en vX.Y.Z et réajuster les jalons.
- `python scripts/check_docs_sync.py` (bloquant en CI si non synchronisé).
- `python scripts/build_exe.py`, puis préparer `dist/AMSO-Windows-vX.Y.Z/` (exe, les 15 `.md`, `locales/`, `LICENSE`).
- Créer l'archive `dist/AMSO-Windows-vX.Y.Z.zip` (dès v0.4.0+, étendre la GitHub Action pour Linux `.AppImage` et macOS `.dmg`).
- Demander la validation manuelle de l'exécutable compilé.

## 3. Release (Publication)
- Committer et merger `develop` vers `main`.
- Tag Git annoté `vX.Y.Z`, puis `git push origin main develop --tags`.
- `python scripts/publish_github_release.py` (extraction changelog, captures, tableau et zip).
- itch.io : déploiement automatisé via GitHub Actions & Butler (secret `BUTLER_API_KEY`).
- Sur itch.io : vérifier le canal `amso-windows.zip`, supprimer les anciens fichiers obsolètes, configurer le « Nom affiché » du build.
- **Devlog itch.io obligatoire** : rédiger et fournir le contenu complet, bilingue FR/EN, prêt à publier.

## 4. Post-release (Nouveau cycle dev)
- Revenir sur `develop`.
- Version suivante `v(X).(Y+1).0-dev` dans `amso/__init__.py`.
- Ajouter `## [X.Y.Z-dev] - ...` en tête des 5 `CHANGELOG.*.md`.
- `python scripts/check_docs_sync.py`.
- Nettoyer les caches et committer l'ouverture du cycle.
