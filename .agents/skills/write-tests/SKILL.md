---
name: write-tests
description: Écrire ou corriger des tests pytest pour AMSO (base SQLite temporaire, Qt offscreen, mocks VLC/réseau, parametrize). À utiliser pour tout nouveau comportement, correction de bug ou ajout de fichier dans tests/.
---

# Conventions de tests AMSO

## Environnement déjà fourni (`tests/conftest.py`, ne pas redéfinir)
- `QT_QPA_PLATFORM=offscreen` : les tests Qt tournent sans fenêtre.
- Fixture autouse `isolate_config` : répertoire de données, `config.ini` et base SQLite isolés dans `tmp_path`, singletons `config`/`i18n` réinitialisés.

## Règles
- Un test = un comportement. Nom : `test_<unité>_<cas>_<résultat attendu>`.
- Cas multiples → `@pytest.mark.parametrize`, pas de copier-coller.
- Fichiers : utiliser `tmp_path` ; jamais de chemin réel ni de `%APPDATA%`.
- Base de données : instancier `DatabaseManager` sur `tmp_path`, jamais sur une base existante.
- Mocker VLC (`player_service`), réseau, Spotify/Google, horloge ; aucun appel externe réel.
- Tester le comportement observable, pas les détails internes.
- Bug corrigé = test de non-régression qui échoue avant le correctif.
- Types annotés (`-> None`) sur les tests ; imports triés (ruff).

## Placement
Fichier existant par domaine : `test_database.py`, `test_scanner.py`, `test_metadata.py`, `test_playlist_parser.py`, `test_i18n.py`, `test_player.py`, `test_blind_test.py`, `test_ui.py`, `test_sync_and_scheduler.py`… Ajouter à l'existant si < 500 lignes, sinon créer `tests/test_<domaine>_<sujet>.py` (`test_player.py` est déjà trop gros).

## Exécution
`pytest -q tests/<fichier>::<test>` d'abord ; `pytest -q` complet seulement avant release. Couverture : `pytest --cov=amso --cov-report=term-missing tests/<fichier>` à la demande.
