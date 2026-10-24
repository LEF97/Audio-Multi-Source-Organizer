# AMSO — Consignes pour l'assistant (économie de jetons)

Contexte projet : voir `context.md`. Ne pas le relire si déjà connu.

## Dossiers et fichiers à IGNORER (ne jamais lister, lire ni rechercher dedans)
- `.venv/`, `build/`, `dist/`, `__pycache__/`, `.git/`
- `.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`, `.coverage`
- `*.db`, `*.spec`, `Thumbs.db`
- `screenshots/`, `*.png`, `*.ico`, `*.icns` (ne lire une image que si demandé explicitement)
- `_work/`, `scratch/`

## Lecture de code
- Gros fichiers encore > 500 lignes (`amso/ui/views/blind_test_view.py` ~860, `amso/ui/views/player_view.py` ~715, `amso/ui/pages/settings_player.py` ~670, `amso/ui/theme.py` ~630, `amso/ui/models.py` ~630, `amso/core/metadata.py` ~620, `amso/ui/views/playlist_view.py` ~600) : ne JAMAIS les lire en entier.
  Utiliser `grep_search` pour localiser, puis lire uniquement la plage de lignes nécessaire.
- Lancer les recherches avec `SearchPath` limité à `amso/` ou `tests/`, jamais à la racine.
- Ne pas relire un fichier déjà lu dans la conversation, sauf s'il a changé.

## Documentation multilingue
- Ne modifier les fichiers `*.fr/es/de/it.md` que pour une release ou sur demande explicite.
- Pour une modif de code courante, ne pas toucher README/CHANGELOG/ROADMAP.
- Utiliser `python scripts/check_docs_sync.py` plutôt que relire les 15 fichiers. Procédure : skill `docs-sync`.

## Exécution et boucles
- Tests : lancer d'abord seulement les tests concernés (`pytest -q tests/<fichier>`), la suite complète uniquement avant release.
- Si un test, une compilation ou une commande échoue 2 fois de suite avec la même erreur, ARRÊTER et expliquer le problème à l'utilisateur au lieu de réessayer.
- Limiter les sorties de commandes (`| Select-Object -First 40`, `-q`).

## Scripts
- Tout script Python créé (`scripts/`, `scratch/`…) s'accompagne SYSTÉMATIQUEMENT d'un `.bat` du même nom, à côté, qui le lance avec `.venv\Scripts\python.exe` depuis la racine du projet, affiche le déroulé et le résultat, puis finit par `pause` (fenêtre ouverte).
  Modèle : `@echo off` / `cd /d "%~dp0.."` / `.venv\Scripts\python.exe scratch\nom.py %*` / `echo Code de sortie : %ERRORLEVEL%` / `pause`.
- **Fins de ligne Windows obligatoires (CRLF)** : tout fichier `.bat` doit impérativement être enregistré avec des fins de ligne `\r\n` (CRLF) sous peine de bugs de décalage de caractères dans l'interpréteur `cmd.exe`.

## Style de travail
- Faire des modifications ciblées, pas de réécriture complète de fichier.
- Réponses concises, sans re-résumer ce qui vient d'être fait.
- Skills (`.agents/skills/`) à charger à la demande : `release` (toute release), `split-module` (découpage de fichiers), `add-i18n-key` (nouveau texte UI), `docs-sync` (doc multilingue), `add-source-connector` (nouvelle source), `db-migration` (schéma/requêtes SQLite), `quality-gate` (fin de tâche : ruff/mypy/pytest), `write-tests` (tests pytest), `qt-threading` (QThread/workers), `build-exe` (PyInstaller).
- Suivi du découpage : `python scripts/check_file_sizes.py` (liste courte des fichiers > 500 lignes).

## Rationalisation (anti-duplication)
- AVANT d'écrire du code : `grep_search` (limité à `amso/`) pour vérifier qu'un helper, style (QSS) ou widget équivalent n'existe pas déjà ; le réutiliser.
- Dès qu'un bloc existe en 2 exemplaires (même logique, seuls des paramètres changent) : l'extraire dans un module partagé (`amso/ui/styles.py`, `amso/ui/widgets/`, mixin) au lieu de le copier.
- Couleurs et QSS : jamais de littéral répété (`#0284C7`, `#20242D`…) ; passer par `theme.py` / `styles.py`.

## Architecture : fichiers petits et cohésifs
- Cible : **< 500 lignes par fichier**, **< 60 lignes par fonction**. Au-delà de ~800 lignes, découper avant d'ajouter du code.
- Ne JAMAIS ajouter une nouvelle fonctionnalité dans un gros fichier existant : créer un module dédié et l'importer.
- Un module = une responsabilité. Placement :
  - `amso/core/` : logique métier pure, zéro Qt. `amso/core/db/` : un fichier par domaine (sources, pistes, playlists, journal...).
  - `amso/services/` : connecteurs externes et services (lecteur, mises à jour, VLC).
  - `amso/ui/pages/` : une page ou un contrôleur par fichier (mixins de `MainWindow`).
  - `amso/ui/widgets/` : widgets réutilisables. `amso/ui/dialogs/` : dialogues. `amso/ui/views/` : vues autonomes.
- Nouvelle page/contrôleur de `MainWindow` : créer un mixin dans `amso/ui/pages/` plutôt que d'agrandir `main_window.py`.
- Découpage = déplacement pur, sans modification de logique : commit séparé, `pytest -q` avant et après.
- Garder l'API publique stable : réexporter depuis l'ancien module (ex. `database.py` réexporte `db/models.py`).
- Éviter les imports circulaires : les widgets/types partagés vont dans un module neutre (`widgets/common.py`, `db/models.py`), jamais importés depuis `main_window.py`.
- Attention aux variables de module réaffectées via `global` (ex. `vlc` dans `player_service.py`) : ne pas les déplacer entre modules sans les encapsuler.

## Bonnes pratiques Python & Standards de qualité logicielle
- Python 3.11+, `from __future__ import annotations`, annotations de type partout (`mypy amso` doit passer).
- Formatage et lint : `ruff` (`ruff check`, `ruff format`) ; imports triés, aucun import inutilisé.
- **Zéro masquage d'avertissement** : interdiction de contourner linter et typage via `# noqa` ou `# type: ignore` sans justification impérative documentée (bug de typage d'une lib tierce).
- **Zéro catch silencieux** : pas de `except:` nu ni de `except Exception: pass` muet. Cibler l'exception précise ; consigner (`logger`) ou documenter sur une ligne la raison exacte pour laquelle elle est tolérée.
- **Zéro marqueur lexical d'IA** : proscrire les qualificatifs mélioratifs/pompeux (`Robust`, `Seamless`, `Smart`, `Advanced`, `Comprehensive`, `Resilient`) dans le code, classes, commits et commentaires. Nommer par l'intention technique factuelle (`FileScannerWithRetries`).
- **Commentaires du POURQUOI** : ne jamais paraphraser le code (auto-documenté). Commenter exclusivement le POURQUOI (contraintes OS Windows/Linux, synchronisation Qt/VLC, contournements de bugs tiers).
- Pas de logique dans `__init__.py`. Pas de variable globale mutable. Pas de découpage cosmétique vide (`Part1`, `SubMethodA`) : extraire des abstractions métier réelles.
- Préférer `pathlib`, `dataclass(slots=True)`, `StrEnum`, f-strings. Pas de `print` : utiliser `logging` (`logger = logging.getLogger(__name__)`).
- Qt : tout traitement long dans un `QThread`/worker, jamais dans le thread UI ; textes via `tr()` (clés dans `amso/locales/*.json`, 5 langues).
- SQL : requêtes paramétrées uniquement (jamais de f-string dans une requête).
- **Tests** : tout nouveau comportement = test pytest. Nomenclature recommandée : `test_<sujet>_<condition>_<resultat_attendu>`.
- **Validation unifiée** : lancer `scripts/verify.bat` ou `python scripts/verify.py` avant tout commit ou fin de tâche majeure.

