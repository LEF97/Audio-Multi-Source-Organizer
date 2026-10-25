---
name: add-source-connector
description: Ajouter un nouveau type de source audio à AMSO (cloud, streaming, service distant, en plus des dossiers locaux). À utiliser pour tout connecteur externe : enum SourceType, scan, lecture, UI des sources.
---

# Ajouter un connecteur de source

État actuel : `SourceType` (`amso/core/db/models.py`) ne définit que `LOCAL` ; le scan local est dans `amso/core/scanner.py`. Il n'existe pas encore d'interface de connecteur : **la première fois, la créer** plutôt que dupliquer la logique locale.

## Points d'intégration à vérifier (grep `SourceType`)
- `amso/core/db/models.py` : valeur d'enum (`StrEnum`) ; stockée en TEXT dans `sources.source_type` et `tracks.source_type`.
- `amso/core/scanner.py` : branches `SourceType.LOCAL` → ajouter le scan du nouveau type.
- `amso/core/scheduler.py` : la synchro temps réel est limitée à `LOCAL` (`sync_mode`, `sync_interval_*`).
- `amso/ui/pages/scan_controller.py`, `session_state.py` (pistes non locales), `folders_page.py`, `settings_sources.py` : icônes/libellés par type (`💾` local, `☁️` autre).
- `amso/ui/dialogs/source_config_dialog.py` (`SourceConfigData`) : champs de configuration (identifiants, URL…).
- `amso/services/player_service.py` : lecture d'un chemin/URL non local.

## Procédure
1. Si absent, définir un protocole `SourceConnector` (ex. `amso/services/connectors/base.py` : `list_tracks()`, `resolve_stream(track)`, `test_connection()`), logique pure sans Qt.
2. Un fichier par connecteur dans `amso/services/connectors/`.
3. Ajouter la valeur d'enum, brancher le scan et la lecture ; réseau/scan long dans un `QThread`/worker, jamais dans le thread UI.
4. Secrets (tokens) : ne jamais les mettre en base en clair ni dans les logs ; utiliser `keyring` ou équivalent.
5. UI : textes via `tr()` (skill `add-i18n-key`). Migration DB si nouvelle colonne (skill `db-migration`).
6. Tests : connecteur mocké (aucun appel réseau réel), cas d'erreur/timeout, déduplication avec pistes locales.
7. Vérifier `pytest -q tests/<fichier>`, `ruff check`, `mypy amso`.
8. Ne pas ajouter de code dans `main_window.py` : mixin dédié (skill `split-module`).
