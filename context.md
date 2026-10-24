# Audio Multi-Source Organizer (AMSO) — Project Context

## 1. Vision & Objectifs
**Audio Multi-Source Organizer (AMSO)** est une application de bureau open-source multiplateforme (Windows, macOS, Linux) conçue pour unifier, organiser et synchroniser des bibliothèques audio hybrides réparties entre :
* **Stockage local :** fichiers haute fidélité (MP3, FLAC, AAC, etc.) répartis sur plusieurs dossiers ou disques.
* **Stockage cloud :** archives et sauvegardes sur Google Drive (v0.5.0).
* **Services de streaming :** playlists et bibliothèques en ligne Spotify, Deezer (v0.6.0).

---

## 2. Stack Technique & Dépendances
* **Langage :** Python 3.11+
* **Interface graphique :** PySide6 (Qt pour Python officiel). Utilisation stricte de modèles virtualisés (`QAbstractTableModel`) pour garantir la fluidité sur de grands volumes (> 50 000 titres).
* **Moteur audio :** `python-vlc` (VLC portable intégré avec fondu doux, transitions et spectre sonore).
* **Traitement audio & tags :** `mutagen` (extraction et écriture des tags ID3, Vorbis Comments, FLAC).
* **Persistance locale :** SQLite3 via le module natif standard (pas d'ORM lourd, requêtes SQL optimisées).
* **Packaging & Distribution :** PyInstaller (`scripts/build_exe.py`) pour générer les exécutables natifs (`.exe`, `.dmg`, `.AppImage`).

---

## 3. Architecture Logicielle
L'application repose sur une architecture modulaire et découplée (modules < 500 lignes) :

```text
amso/
├── amso/
│   ├── core/           # Moteur métier pur (zéro dépendance Qt)
│   │   ├── scanner.py  # Parcours récursif du disque, détection multithread
│   │   ├── metadata.py # Extraction tags (Mutagen), formats, pochettes
│   │   ├── database.py # Schéma SQLite, indexation, requêtes CRUD
│   │   ├── config.py   # Gestion de la configuration persistante (JSON)
│   │   ├── scheduler.py# Planification automatique des synchronisations
│   │   └── i18n.py     # Moteur d'internationalisation et détection de langue
│   ├── services/       # Services et sous-systèmes
│   │   ├── player_service.py     # Façade publique du lecteur audio (python-vlc)
│   │   ├── player_transport.py   # Gestion bas niveau du transport et du volume
│   │   ├── player_queue.py       # Gestion de la liste de lecture et historique
│   │   ├── player_transitions.py # Transitions (standard, gapless, crossfade)
│   │   ├── sleep_inhibitor.py    # Prévention de la veille système
│   │   └── update_checker.py     # Vérification des mises à jour distantes (GitHub)
│   └── ui/             # Couche graphique PySide6 (architecture modulaire)
│       ├── pages/      # Mixins spécialisés de MainWindow (< 500 lignes/fichier)
│       │   ├── folders_*.py      # Vue arborescente, navigation et corbeille
│       │   ├── settings_*.py     # Paramètres général, lecteur, sources, à propos
│       │   ├── navigation.py     # Routage et basculement des tiroirs/onglets
│       │   └── retranslate.py    # Retraduction dynamique de l'interface
│       ├── views/      # Vues composites autonomes (PlayerView, PlaylistView, BlindTestView, LogsView)
│       ├── widgets/    # Composants réutilisables (tiroirs, badges, combos)
│       ├── dialogs/    # Boîtes de dialogue (sources, VLC, confirmation suppression)
│       └── workers.py  # QThread et signaux Qt (déport des scans et calculs lourds)
├── tests/              # Tests unitaires et d'intégration (pytest)
├── scripts/            # Outils de vérification qualité, synchronisation et build
├── main.py             # Point d'entrée de l'application
├── pyproject.toml      # Configuration du projet et dépendances
└── context.md          # Présent document de référence
```