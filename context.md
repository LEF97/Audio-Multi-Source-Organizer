# Audio Multi-Source Organizer (AMSO) — Project Context

## 1. Vision & Objectifs
**Audio Multi-Source Organizer (AMSO)** est une application de bureau open-source multiplateforme (Windows, macOS, Linux) conçue pour unifier, organiser et synchroniser des bibliothèques audio hybrides réparties entre :
* **Stockage local :** fichiers haute fidélité (MP3, FLAC, AAC, etc.) répartis sur plusieurs dossiers ou disques.
* **Stockage cloud :** archives et sauvegardes sur Google Drive.
* **Services de streaming :** playlists et bibliothèques en ligne (Spotify, Deezer).

---

## 2. Stack Technique & Dépendances
* **Langage :** Python 3.11+
* **Interface graphique :** PySide6 (Qt pour Python officiel). Utilisation stricte de modèles virtualisés (`QAbstractTableModel`) pour garantir la fluidité sur de grands volumes (> 50 000 titres).
* **Traitement audio & tags :** `mutagen` (extraction et écriture des tags ID3, Vorbis Comments, FLAC).
* **Persistance locale :** SQLite3 via le module natif standard (pas d'ORM lourd, requêtes SQL optimisées).
* **Intégrations distantes :**
  * `google-api-python-client` / `google-auth-oauthlib` pour l'API Google Drive v3.
  * `spotipy` pour l'écosystème Spotify.
* **Packaging & Distribution :** PyInstaller ou Nuitka pour générer les exécutables natifs (`.exe`, `.dmg`, `AppImage`).

---

## 3. Architecture Logicielle
L'application repose sur un découplage strict entre la logique métier et l'interface utilisateur :

```text
amso/
├── amso/
│   ├── core/           # Moteur métier pur (zéro dépendance Qt)
│   │   ├── scanner.py  # Parcours récursif du disque, détection multithread
│   │   ├── metadata.py # Extraction tags (Mutagen), hash & empreinte audio
│   │   └── database.py # Schéma SQLite, migrations et requêtes CRUD
│   ├── services/       # Connecteurs distants & OAuth
│   │   ├── gdrive.py   # Client Google Drive (OAuth 2.0, scan, cache)
│   │   └── streaming.py# Connecteurs Spotify / Deezer
│   └── ui/             # Couche graphique PySide6
│       ├── views/      # Composants graphiques, fenêtres et vues de listes
│       └── workers.py  # QThread et signaux Qt (déport des scans et calculs lourds)
├── tests/              # Tests unitaires et d'intégration (pytest)
├── main.py             # Point d'entrée de l'application
├── .env.example        # Modèle de variables d'environnement (clés API)
├── .gitignore          # Exclusion des fichiers binaires, DB locales et secrets
├── pyproject.toml      # Configuration du projet et dépendances
└── context.md          # Présent document de référence