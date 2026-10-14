# Audio Multi-Source Organizer (AMSO)

[![CI Tests](https://github.com/votre-user/audio-multi-source-organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/votre-user/audio-multi-source-organizer/actions)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** est une application de bureau open-source et multiplateforme conçue pour unifier, dédoublonner et synchroniser vos bibliothèques musicales hybrides réparties entre vos disques locaux, vos archives cloud (Google Drive) et vos plateformes de streaming (Spotify, Deezer).

---

## 📌 Fonctionnalités & Statut du projet

| Fonctionnalité | Description | Statut |
| :--- | :--- | :---: |
| **Scanner local multithreadé** | Découverte récursive et rapide des fichiers audio locaux (MP3, FLAC, AAC, OGG...) | 🟡 En cours |
| **Extraction de métadonnées** | Lecture/écriture ID3, Vorbis Comments et calcul d'empreinte audio (`mutagen`) | 🟡 En cours |
| **Base de données SQLite3** | Stockage persistant optimisé avec schéma relationnel dédié (sans ORM lourd) | 🟡 En cours |
| **Interface graphique PySide6** | Modèle tabulaire virtualisé (`QAbstractTableModel`) pour > 50 000 morceaux | ⚪ Prévu |
| **Connecteur Google Drive** | Scan et synchronisation de collections audio distantes via OAuth 2.0 | ⚪ Prévu |
| **Connecteur Spotify / Streaming** | Importation de playlists et correspondance de pistes | ⚪ Prévu |
| **Dédoublonnage intelligent** | Détection de doublons (titre/artiste flous + empreintes audio) | ⚪ Prévu |

---

## 🚀 Démarrage rapide

### Prérequis
- **Python 3.11** ou supérieur installé
- Git

### Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/<votre-user>/audio-multi-source-organizer.git
cd audio-multi-source-organizer

# 2. Créer l'environnement virtuel
python -m venv .venv

# 3. Activer l'environnement
# Sous Windows (PowerShell) :
.venv\Scripts\Activate.ps1
# Sous Linux / macOS :
source .venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# Pour le développement et les tests :
pip install -e .[dev]

# 5. Configurer les variables d'environnement
cp .env.example .env
# Renseignez vos identifiants dans .env si vous utilisez Google Drive ou Spotify

# 6. Lancer l'application
python main.py
```

---

## 🧪 Lancement des tests

Le projet utilise `pytest` avec une suite de tests unitaires et d'intégration :

```bash
pytest -v
```

Les tests s'exécutent automatiquement sur **Windows, macOS et Ubuntu** à chaque push via GitHub Actions.

---

## 🔒 Sécurité & Clés d'API

- **Ne commitez jamais de clés d'API ni de tokens d'authentification réels.**
- Le fichier `.gitignore` est pré-configuré pour bloquer `.env`, `credentials.json`, `token.json` et toutes les bases de données SQLite locales.
- Utilisez `.env.example` comme modèle pour votre environnement de développement.

---

## 📄 Licence

Ce projet est sous licence **GNU General Public License v3.0 (GPL-3.0)** — consultez le fichier [LICENSE](LICENSE) pour plus de détails.
