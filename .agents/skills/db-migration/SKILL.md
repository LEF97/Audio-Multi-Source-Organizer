---
name: db-migration
description: Modifier le schéma SQLite d'AMSO (nouvelle table, colonne, index) et ajouter des requêtes dans amso/core/db/. À utiliser pour tout changement de base de données ou nouvelle méthode de repository.
---

# Migration et requêtes SQLite

## Structure
- `amso/core/database.py` : `DatabaseManager` (assemble les mixins de repo) et initialisation du schéma (`CREATE TABLE IF NOT EXISTS …`, puis `ALTER TABLE … ADD COLUMN` pour les migrations).
- `amso/core/db/` : un fichier par domaine — `sources_repo`, `tracks_repo`, `curation_repo`, `playlists_repo`, `activity_repo`, `library_queries`, `models` (dataclasses/enums), `paths`.
- `database.py` réexporte `db/models.py` : garder cette API stable.

## Nouvelle colonne / table
1. Ajouter le champ au dataclass dans `db/models.py` (`dataclass(slots=True)`, valeur par défaut).
2. Dans l'init du schéma de `database.py`, suivre le motif existant : vérifier l'absence de la colonne (`PRAGMA table_info(<table>)`), puis `ALTER TABLE <table> ADD COLUMN … DEFAULT …` (valeur par défaut obligatoire pour les lignes existantes). Une nouvelle table : `CREATE TABLE IF NOT EXISTS` + index nécessaires (`CREATE INDEX IF NOT EXISTS`).
3. Mettre à jour les `INSERT`/`SELECT` et la conversion ligne → dataclass dans le repo concerné.
4. Une migration ne doit jamais supprimer ni réécrire de données utilisateur ; elle doit être idempotente (relancer deux fois = sans effet).

## Requêtes
- **Paramétrées uniquement** (`?` ou `:nom`), jamais de f-string dans le SQL. Les noms de colonnes dynamiques doivent venir d'une liste blanche.
- Nouvelle méthode → dans le fichier de repo du domaine, pas dans `database.py`. Si le fichier dépasse ~500 lignes, créer un nouveau mixin (voir `split-module`).
- Opérations en lot : une transaction (`executemany`), pas de commit par ligne.
- Appels longs hors du thread UI.

## Tests (obligatoires)
- Dans `tests/test_database.py` (ou fichier dédié) avec une base temporaire (`tmp_path`).
- Tester : création sur base vierge, migration depuis une base ancienne (sans la nouvelle colonne), idempotence, et la requête elle-même.
- Lancer `pytest -q tests/test_database.py`, puis `ruff check` et `mypy amso`.
