---
name: split-module
description: Procédure pour découper un gros fichier Python AMSO (main_window.py, player_service.py, folders_page.py, player_view.py, blind_test_view.py, playlist_view.py…) en modules < 500 lignes sans changer la logique. À utiliser pour tout refactoring de découpage, extraction de mixin ou de widget.
---

# Découpage d'un module (déplacement pur)

## Principes
- Cible : < 500 lignes/fichier, < 60 lignes/fonction. Un module = une responsabilité.
- Déplacement pur : AUCUNE modification de logique. Commit séparé.
- Ne jamais lire le gros fichier en entier : `grep_search` (`def |class `) pour cartographier, puis lire les plages utiles.

## Procédure
1. **Baseline** : `pytest -q` (ou les tests concernés) + `ruff check amso` + `mypy amso`. Noter le résultat.
2. **Cartographier** : lister les méthodes et leurs lignes avec grep ; regrouper par responsabilité (≈ 300-450 lignes/groupe).
3. **Choisir la destination** :
   - `amso/core/` (+ `core/db/` un fichier par domaine) : logique pure, zéro Qt.
   - `amso/services/` : lecteur, mises à jour, VLC.
   - `amso/ui/pages/` : mixin de `MainWindow` (`class XxxMixin:`), un par fichier.
   - `amso/ui/widgets/` : widgets réutilisables ; types partagés dans `widgets/common.py`.
   - `amso/ui/dialogs/`, `amso/ui/views/` : dialogues et vues autonomes.
4. **Extraire** via un script jetable dans `scratch/` (modèles existants : `scratch/extract_mixins2.py`, `split_db_a.py`, `split_effects.py`) : copier les lignes telles quelles, ne pas retaper le code à la main.
5. **Brancher** : ajouter le mixin à l'héritage de la classe d'origine, ou importer le module.
6. **Garder l'API publique stable** : réexporter depuis l'ancien module (ex. `database.py` réexporte `db/models.py`).
7. **Imports** : un import par symbole utilisé, triés (`ruff check --fix`). Éviter les imports circulaires : types/widgets partagés dans un module neutre, jamais importés depuis `main_window.py`.
8. **Pièges** :
   - Variables de module réaffectées via `global` (ex. `vlc` dans `player_service.py`) : ne pas déplacer sans encapsulation.
   - Signaux/slots Qt : vérifier que les `connect(self.méthode)` pointent toujours vers une méthode existante.
   - Les tests qui font `patch("ancien.module.X")` doivent suivre le déplacement.
9. **Vérifier** : `pytest -q`, `ruff check`, `ruff format --check`, `mypy amso`, `python -c "import amso.ui.views.main_window"`, puis `wc -l` sur les fichiers touchés.
10. Docstring courte sur chaque nouveau module ; conserver les commentaires existants.

## Arrêt
Si un test échoue 2 fois avec la même erreur, arrêter et expliquer.
