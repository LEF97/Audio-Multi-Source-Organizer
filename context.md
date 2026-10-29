# Audio Multi-Source Organizer (AMSO) — Contexte projet

> **Référence unique** du projet pour tous les assistants (Gemini, Claude) et pour les humains.
> Les règles de travail sont dans `GEMINI.md`, les procédures dans `.agents/skills/`. En cas de doute, le code fait foi.
> **À tenir à jour** à chaque ajout, déplacement ou suppression de module (skill `update-context`, contrôle : `python scripts/check_context.py`, intégré à `verify`).

## 1. Vision & état
Application de bureau open-source (GPL-3.0, auteur LEF97), Windows / macOS / Linux, qui unifie des bibliothèques audio réparties entre
**disque local**, **cloud (Google Drive)** et **streaming (Spotify, Deezer, Amazon Music)**, sans compromis sur la vie privée.
Distribution : GitHub Releases + itch.io (Butler, « Pay What You Want »), dons Ko-fi / GitHub Sponsors.

| Version | Contenu | État |
|---|---|---|
| 0.1–0.3 | scanner local multithread, tags, lecteur VLC, playlists M3U/PLS/XSPF/WPL, Blind Test, corbeille, mises à jour in-app, effets visuels | publiées |
| 0.4.0 | refonte modulaire + quality gate, 43 langues, moteur audio `buffer` (QAudioSink), crossfade/gapless, feuilles CUE | publiée |
| **0.4.1-dev** | correctifs audio : crossfade au fil du décodage, Blind Test en mode `buffer`, TNR des transitions ; restent (0.4.x) : packaging Linux/macOS, artistes/discographie, égaliseur, éditeur de tags, pochettes en ligne, filtres avancés | **en cours** (branche `develop`) |
| 0.5.0 | connecteur Google Drive (OAuth2, scan distant, streaming avec cache) | planifié |
| 0.6.0 | Spotify / Deezer / Amazon Music, matching hybride, vue unifiée | planifié |
| 1.0.0 | dédoublonnage par empreinte acoustique, packaging signé, doc complète | planifié |

Idée validée, non planifiée : serveur web embarqué (FastAPI/uvicorn) + client Android → `docs/plan_serveur_web_android.md`.
Détail des jalons : `ROADMAP.fr.md` ; historique : `CHANGELOG.fr.md`.

## 2. Stack
Python 3.11+ (venv `.venv`) · PySide6 (modèles virtualisés `QAbstractTableModel`, > 50 000 titres) · python-vlc + VLC portable auto-téléchargé ·
mutagen (ID3, Vorbis, FLAC) · SQLite natif sans ORM · PyInstaller · ruff, mypy, radon, pytest(-cov), SonarLint · i18n JSON maison ·
CI GitHub Actions (`tests.yml` : 3 OS × Python 3.11-3.13 ; `release.yml`). Spotipy et les libs Google figurent déjà dans `requirements.txt` mais les connecteurs n'existent pas encore.
Qualité et réinstallation de la stack : `CODE_QUALITY.md`.

## 3. Architecture
```text
main.py                       point d'entrée (AppUserModelID Windows, option --debug-i18n)
amso/
├── core/                     logique métier pure, ZÉRO dépendance Qt
│   ├── database.py           DatabaseManager (assemble les mixins) + schéma / migrations
│   ├── db/                   models, sources_repo, tracks_repo, curation_repo, playlists_repo, activity_repo, library_queries, paths
│   ├── scanner.py            parcours récursif multithread
│   ├── metadata.py           tags (mutagen), formats, pochettes embarquées
│   ├── playlist_parser.py    M3U / PLS / XSPF / WPL (+ CUE)
│   ├── pcm_mixer.py          mixage PCM Int16 stéréo (numpy) : gains égale puissance, StreamingCrossfade (fondu au fil du décodage)
│   ├── cue_parser.py         feuilles CUE : pistes virtuelles (début/fin dans un fichier audio)
│   ├── cover_art.py          pochettes
│   ├── scheduler.py          synchronisation automatique planifiée
│   ├── network_paths.py      détection UNC / lecteur réseau (sans E/S) : jamais de exists()/isdir() réseau sur le thread UI
│   ├── startup_timing.py     chronométrage des étapes de démarrage → `%APPDATA%/AMSO/startup.log`
│   ├── config.py             préférences persistantes (config.ini)
│   ├── i18n.py               traduction `tr()`, détection de langue (43 langues)
│   └── constants.py
├── services/                 lecteur et services système
│   ├── player_service.py     façade publique du lecteur
│   ├── player_transport.py   transport bas niveau
│   ├── player_queue.py       file d'attente, historique
│   ├── player_transitions.py transitions (standard, gapless, crossfade)
│   ├── player_vlc_transitions.py transitions matérielles VLC direct
│   ├── player_volume.py, player_types.py
│   ├── player_cue.py         lecture des pistes CUE (moteur tampon) : décalage/arrêt de décodage, clé de flux
│   ├── audio_engine.py       ContinuousAudioEngine (ring buffer PCM, `read_pcm` appelé par le thread audio)
│   ├── audio_output.py       SinkOutput : QAudioSink en mode pull dans son propre QThread (indépendant du thread UI)
│   ├── audio_decoder.py      décodeur PCM (amem)
│   ├── audio_spectrum.py     analyse du spectre
│   ├── vlc_binding.py, vlc_downloader.py   liaison et auto-installation de VLC
│   ├── windows_audio.py, sleep_inhibitor.py   spécifique OS
│   └── update_checker.py     mises à jour via GitHub Releases
└── ui/                       PySide6
    ├── views/                vues autonomes : main_window, player, playlist, logs, splash…
    │   ├── blind_test/       sous-modules du mode Blind Test
    │   └── effects/          effets visuels (types, painters, barres de spectre)
    ├── pages/                mixins de MainWindow (folders_*, settings_*, navigation, retranslate, scan_controller…)
    ├── widgets/              composants réutilisables (tiroirs, badges, combos)
    ├── dialogs/              boîtes de dialogue (sources, VLC, suppression…)
    ├── models*.py, folder_track_model.py, playlist_table_model.py   modèles Qt virtualisés
    ├── theme.py, styles.py, qss_*.py   couleurs et QSS centralisés
    └── workers.py            QThread / signaux (scans et calculs lourds hors thread UI)
amso/locales/*.json           43 langues, fr.json = source de vérité
scripts/                      outils (+ .bat jumeau pour chaque script) : verify, check_file_sizes, check_docs_sync, check_context,
                              sync_translations(_ollama), tnr_transitions (non-régression des transitions sur pistes réelles), translate_docs (README en 43 langues, CHANGELOG/ROADMAP es/de/it, via Ollama), audit_translations, build_exe, publish_github_release, sync_skills
docs/i18n/                    toutes les langues sauf fr et en (README ×41, CHANGELOG et ROADMAP es/de/it), générées par Ollama ; sélecteur de langue partagé
tests/                        pytest, Qt offscreen, config et DB isolées (conftest autouse)
tests/tnr/                    banc de non-régression audio (pistes de référence : `_work/tnr/`, sinon NAS) : sortie factice (capture_sink), décodage de référence, analyse, scénario ; lancé par scripts/tnr_transitions.bat ou `pytest -m tnr` ; journaux horodatés dans `tests/tnr/log/` (ignoré par git)
.agents/skills/               procédures (copie pour Claude dans .claude/skills via scripts/sync_skills.py)
```
Données utilisateur : `%APPDATA%/AMSO/` (config.ini, base SQLite). Hors périmètre de lecture : `.venv`, `build`, `dist`, caches, `*.db`, `screenshots`, `_work`, `scratch` (scripts jetables).

## 4. Le moteur audio (zone la plus sensible)
Deux moteurs **étanches** (aucun effet de bord de l'un sur l'autre), choisis via `get_audio_engine()` :
- **`vlc_direct`** — sortie directe LibVLC (WASAPI `mmdevice` ; crossfade en DirectSound). **Finalisé et figé : ne plus y toucher.**
- **`buffer`** — `ContinuousAudioEngine` : un unique `QAudioSink` (pull, thread audio dédié) ouvert en continu, ring buffer PCM, transitions logicielles
  (gapless sample-accurate, crossfade égale puissance cos/sin, silence injecté). **Travail en cours.** Ne jamais fermer ni recréer la session matérielle
  entre deux titres, ni réintroduire deux lecteurs matériels.

Le décodeur `amem` livre l'audio **en temps réel** (1 s d'audio par seconde) : la fin de la piste sortante n'est pas en mémoire d'avance. Le crossfade est donc
mixé au fil de l'arrivée des blocs (`arm_crossfade` au préchargement, zone calée sur `durée - fondu`), jamais en bloc. Après un seek, LibVLC se place sur un bloc FLAC
(jusqu'à ~200 ms d'écart avec la position demandée). Un plantage natif laisse sa pile dans `%APPDATA%/AMSO/crash.log` (faulthandler).
**Toute modification du moteur `buffer` se valide avec `scripts/tnr_transitions.bat`** (standard, gapless, crossfade sur Sirius → Eye in the Sky).

Invariants communs : en pause, `previous()` charge sans lire (`load_index`, pas `play_index`) ; tout `seek`/`pause` réinitialise le standby
(`_reset_standby_player()`) et annule vidages et transitions ; un `seek` sur piste terminée ne saute pas au suivant ; quitter un mode exclusif
(Blind Test) coupe la lecture, les timers et le préchargement. Détail : skill `audio-pipeline`.

## 5. Conventions clés (le détail est dans GEMINI.md)
< 500 lignes/fichier, < 60 lignes/fonction · pas de duplication · couleurs via `theme.py`/`styles.py` · textes via `tr()` ; en développement seul `fr.json` change
(autres langues et docs EN/ES/DE/IT à la release) · tout script Python a son `.bat` jumeau en CRLF · même erreur 2 fois → s'arrêter et expliquer.

## 6. Skills disponibles
`audio-pipeline` (lecture/transitions) · `add-i18n-key` (textes UI) · `docs-sync` (doc multilingue) · `release` (4 étapes) · `quality-gate` (fin de tâche) ·
`write-tests` · `split-module` · `db-migration` · `qt-threading` · `add-source-connector` · `build-exe` · `update-context` (maintenir ce fichier).

## 7. Points d'attention connus
- `test_player.py` et plusieurs vues/modules (blind_test_view, player_view, settings_player, theme, models, metadata, playlist_view) approchent ou dépassent 500 lignes : candidats au skill `split-module`.
- La documentation Markdown reste en 5 langues (fr/en/es/de/it) mais l'interface compte 43 langues : ne pas confondre les deux (skills, release).
- Aucune interface de connecteur de source n'existe encore (`SourceType` ne définit que `LOCAL`) : la créer au premier connecteur.
