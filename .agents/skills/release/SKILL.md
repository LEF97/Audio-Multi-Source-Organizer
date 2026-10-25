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
  - `CHANGELOG.fr.md` : clôturer `[X.Y.Z-dev]` sous `## [X.Y.Z] - AAAA-MM-JJ` (les autres langues suivent via la traduction ci-dessus).
  - `README.fr.md` (source) : captures, badges, résumé et 13 lignes de fonctionnalités ; `README.md` (EN) traduit depuis le français par l'assistant. C'est la seule langue traduite par un assistant.
  - **Toutes les autres langues (README ×41, CHANGELOG et ROADMAP es/de/it, tous dans `docs/i18n/`) : Ollama uniquement**, jamais de traduction manuelle. Ollama démarré : `python scripts/translate_docs.py --ollama` (blocs modifiés seulement ; relancer si des fragments restent en français). Il régénère aussi les sélecteurs de langue.
  - `ROADMAP.fr.md` : cocher les objectifs atteints en vX.Y.Z et réajuster les jalons (les autres langues suivent via la traduction).
- `python scripts/check_docs_sync.py --release` (43 README + sélecteur de langue ; bloquant en CI si non synchronisé).
- `python scripts/build_exe.py`, puis préparer `dist/AMSO-Windows-vX.Y.Z/` (exe, les 6 `.md` de la racine (README, CHANGELOG, ROADMAP en fr et en), `locales/`, `LICENSE` ; pas le dossier `docs/i18n/`).
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
- Ajouter `## [X.Y.Z-dev] - ...` en tête de `CHANGELOG.fr.md` (les autres langues suivent à la prochaine traduction).
- `python scripts/check_docs_sync.py`.
- Mettre à jour le tableau « Vision & état » de `context.md` (skill `update-context`) : version publiée, nouveau cycle `-dev`.
- Nettoyer les caches et committer l'ouverture du cycle.
