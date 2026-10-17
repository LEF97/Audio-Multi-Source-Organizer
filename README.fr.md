# Audio Multi-Source Organizer (AMSO)

<p align="right">
  <b>Français</b> • <a href="README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a>
</p>

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](CHANGELOG.fr.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](ROADMAP.fr.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** est une application de bureau open-source et multiplateforme conçue pour unifier, dédoublonner et synchroniser vos bibliothèques musicales hybrides réparties entre vos disques locaux, vos archives cloud (Google Drive) et vos plateformes de streaming (Spotify, Deezer et Amazon Music).

---

<p align="center">
  <img src="screenshots/2026-10-17%20v0.1.0.png" alt="Capture d'écran Audio Multi-Source Organizer (AMSO)" width="850">
</p>

---

## 📌 Fonctionnalités & Statut du projet

| Fonctionnalité | Description | Statut |
| :--- | :--- | :---: |
| **Scanner local multithreadé** | Découverte récursive et rapide des fichiers audio locaux (MP3, FLAC, AAC, OGG...) | 🟢 Implémenté |
| **Extraction de métadonnées** | Lecture/écriture ID3, Vorbis Comments et calcul d'empreinte audio (`mutagen`) | 🟢 Implémenté |
| **Moteur de lecture VLC intégré** | Lecteur audio léger et autonome avec auto-installation VLC portable et gestion fluide du volume | 🟢 Implémenté |
| **Gestionnaire de Playlist** | File d'attente virtualisée, drag & drop, aléatoire (shuffle), répétition (repeat) | 🟢 Implémenté |
| **Interface graphique PySide6** | Dark Mode haut de gamme, visualiseur audio temps réel, internationalisation 5 langues | 🟢 Implémenté |
| **Mises à jour in-app** | Vérification automatique/manuelle des versions via GitHub Releases | 🟢 Implémenté |
| **Gestion des artistes & Discographie** | Vue dédiée par artiste avec albums, singles et discographie complète | 🟡 Prévu |
| **Égaliseur graphique (EQ)** | Presets audio et égaliseur multibandes paramétrique | 🟡 Prévu |
| **Connecteur Google Drive** | Scan et synchronisation de collections audio distantes via OAuth 2.0 | ⚪ Planifié |
| **Connecteur Amazon Music** | Scan et synchronisation de collections distantes via OAuth 2.0 | ⚪ Planifié |
| **Connecteur Spotify / Deezer** | Importation de playlists et correspondance de pistes | ⚪ Planifié |
| **Dédoublonnage intelligent** | Détection de doublons (titre/artiste flous + empreintes acoustiques) | ⚪ Planifié |

> 💡 *Pour consulter le détail des jalons et versions prévues, référez-vous à la [Feuille de route (Roadmap)](ROADMAP.fr.md).*

---

## 🚀 Démarrage rapide

### Prérequis
- **Python 3.11** ou supérieur installé
- Git

### Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/LEF97/Audio-Multi-Source-Organizer.git
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

## 📋 Documentation & Suivi du projet

- 📜 **[CHANGELOG.fr.md](CHANGELOG.fr.md)** : Journal détaillé des versions, nouvelles fonctionnalités et correctifs de bugs.
- 🗺️ **[ROADMAP.fr.md](ROADMAP.fr.md)** : Feuille de route des futurs jalons (Artistes, Cloud, Spotify, Dédoublonnage).
- 📐 **[CODE_QUALITY.md](CODE_QUALITY.md)** : Charte d'architecture logicielle et règles de qualité de code.

---

## 💖 Soutenir le projet & Distribution

AMSO est un logiciel libre et gratuit (open source). Si vous appréciez l'application et souhaitez encourager son développement :

* 🎮 **Téléchargement & Pay What You Want :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (exécutable précompilé prêt à l'emploi)
* ☕ **Faire un don direct :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
* ⭐ **GitHub Sponsors :** [Sponsoriser LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licence

Ce projet est sous licence **GNU General Public License v3.0 (GPL-3.0)** — consultez le fichier [LICENSE](LICENSE) pour plus de détails.
