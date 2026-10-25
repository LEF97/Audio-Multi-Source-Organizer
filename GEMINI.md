# AMSO — Consignes pour l'assistant (économie de jetons)

Contexte projet : voir `context.md`. Ne pas le relire si déjà connu.
**Tenir `context.md` à jour** : toute création, déplacement ou suppression de module/dossier (`amso/`, `scripts/`) impose d'y refléter le changement dans la même tâche (skill `update-context`, contrôle : `python scripts/check_context.py`, exécuté par `verify`).

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

## Documentation (FR source de vérité)
- **Fichiers français (`*.fr.md`)** : Les 3 fichiers de référence (`README.fr.md`, `CHANGELOG.fr.md`, `ROADMAP.fr.md`) sont la source de vérité et sont mis à jour au fur et à mesure des développements.
- **Documentation dans les autres langues (`*.md`, `*.es.md`, `*.de.md`, `*.it.md`)** : Ne pas les modifier au fil de l'eau. Elles seront traduites et synchronisées uniquement lors de la release (procédure : skill `docs-sync`).
- Utiliser `python scripts/check_docs_sync.py` uniquement avant une release pour contrôler l'alignement des 15 fichiers.

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
- Skills (`.agents/skills/`) à charger à la demande : `audio-pipeline` (architecture audio/tampon continu), `release` (toute release), `split-module` (découpage de fichiers), `add-i18n-key` (nouveau texte UI), `docs-sync` (doc multilingue), `add-source-connector` (nouvelle source), `db-migration` (schéma/requêtes SQLite), `quality-gate` (fin de tâche : ruff/mypy/pytest), `write-tests` (tests pytest), `qt-threading` (QThread/workers), `build-exe` (PyInstaller), `update-context` (mise à jour de `context.md`).
- Suivi du découpage : `python scripts/check_file_sizes.py` (liste courte des fichiers > 500 lignes).

## Rationalisation (anti-duplication)
- AVANT d'écrire du code : `grep_search` (limité à `amso/`) pour vérifier qu'un helper, style (QSS) ou widget équivalent n'existe pas déjà ; le réutiliser.
- Dès qu'un bloc existe en 2 exemplaires (même logique, seuls des paramètres changent) : l'extraire dans un module partagé (`amso/ui/styles.py`, `amso/ui/widgets/`, mixin) au lieu de le copier.
- Couleurs et QSS : jamais de littéral répété (`#0284C7`, `#20242D`…) ; passer par `theme.py` / `styles.py`.
- **Textes UI & Traductions (FR source de vérité)** : Au fil de l'eau en développement, **seul `amso/locales/fr.json` doit être modifié**. Les autres langues (`en.json`, `es.json`, `de.json`, `it.json`...) et la synchronisation (Ollama / `scripts/sync_translations.py`) ne sont exécutées **QUE lors de la release ou sur demande explicite**, jamais au cours des tâches courantes. AVANT d'ajouter une clé dans `amso/locales/fr.json`, vérifier avec `scripts/audit_translations.bat` ou `grep_search` si un libellé équivalent n'existe pas déjà (ex. boutons génériques `common.cancel`, `common.refresh`, `common.close`, colonnes partagées `table.col_*`). Réutiliser la clé existante plutôt que de créer un doublon.

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
- Qt : tout traitement long dans un `QThread`/worker, jamais dans le thread UI ; textes via `tr()` (clés dans `amso/locales/*.json`, 43 langues).
- SQL : requêtes paramétrées uniquement (jamais de f-string dans une requête).
- **Tests** : tout nouveau comportement = test pytest. Nomenclature recommandée : `test_<sujet>_<condition>_<resultat_attendu>`.
- **Validation unifiée** : lancer `scripts/verify.bat` ou `python scripts/verify.py` avant tout commit ou fin de tâche majeure.

## Règle Absolue : Étanchéité des Moteurs Audio (`vlc_direct` & `buffer`)
- **Deux moteurs strictement étanches** : AMSO supporte le mode `vlc_direct` (VLC natif, focus actuel) et le mode `buffer` (`ContinuousAudioEngine` / `QAudioSink`, finalisation en temps 2).
- **Zéro interférence** : Les deux moteurs sont hermétiques. Aucune modification de code, de logique, de paramétrage ou d'utilisation sur un moteur ne doit avoir d'impact ou d'effet de bord sur l'autre.
- **Règles spécifiques au mode `buffer` (ContinuousAudioEngine - temps 2)** :
  - *Flux audio unique* : La sortie physique vers la carte son est gérée exclusivement par un `QAudioSink` unique (mode Push) ouvert en continu.
  - *Tampon mémoire continu (Ring Buffer)* : Les transitions (Gapless 0, Crossfade cos/sin, silences purs) s'opèrent intégralement en mémoire dans le tampon PCM sans coupure matérielle.
  - *Décodage* : Le décodeur (amem) alimente le tampon sans passer par la sortie haut-parleur.

## Invariants de Contrôle de Lecture & Anti-Régression (valable pour les DEUX moteurs)
- **Respect strict de l'état de pause lors des retours (`previous()`)** :
  - Si le lecteur est en pause, la commande piste précédente (`previous()`) doit impérativement charger le titre en pause (`load_index()`) et ne JAMAIS démarrer la lecture (`play_index()`).
- **Invalidation systématique des préchargements et vidages lors d'un `seek` ou `pause`** :
  - Tout déplacement temporel (`seek_ms`, `seek_ratio`) ou mise en pause (`pause()`) doit immédiatement neutraliser le lecteur standby (`_reset_standby_player()`) et annuler tout timer de vidage matériel (`_is_draining_standard_end`).
  - Sur une piste terminée (`State.Ended`), le seek ne doit jamais provoquer d'enchaînement automatique vers le titre suivant, mais repositionner le morceau actuel en respectant l'état de pause.
- **Hermétisme de navigation inter-menus (Blind Test & modes exclusifs)** :
  - Toute navigation quittant un mode exclusif (Blind Test vers Lecteur, Playlist, etc.) doit impérativement couper la lecture (`pause()`), arrêter tous les timers et réinitialiser les lecteurs standby.
  - Aucun son ne doit se redéclencher spontanément en arrière-plan lors des déplacements dans les menus.
- **Figement définitif du moteur `vlc_direct` (Sortie directe LibVLC)** :
  - Les 3 types de transition (Pas de fondu, Gapless 0 ms, Crossfade) sont validés à 100 % et figés.
  - Pilotage des sorties VLC sous Windows : `mmdevice` (WASAPI natif) pour le mode standard et le mode gapless 0 ; `directsound` pour le mode crossfade (isolation matérielle des volumes).
  - Règle d'or : aucune régression ni modification de transport sur ces 3 modes lors des développements futurs.





