# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <b>Français</b> • <a href="README.md">English</a> • <a href="docs/i18n/README.es.md">Español</a> • <a href="docs/i18n/README.de.md">Deutsch</a> • <a href="docs/i18n/README.it.md">Italiano</a> • <a href="docs/i18n/README.pt.md">Português</a> • <a href="docs/i18n/README.zh_cn.md">简体中文</a> • <a href="docs/i18n/README.ja.md">日本語</a> • <a href="docs/i18n/README.ru.md">Русский</a> • <a href="docs/i18n/README.ar.md">العربية</a>
</p>
<details>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="docs/i18n/README.pl.md">Polski</a> • <a href="docs/i18n/README.tr.md">Türkçe</a> • <a href="docs/i18n/README.nl.md">Nederlands</a> • <a href="docs/i18n/README.sv.md">Svenska</a> • <a href="docs/i18n/README.id.md">Bahasa Indonesia</a> • <a href="docs/i18n/README.bg.md">Български</a> • <a href="docs/i18n/README.sr.md">Српски</a> • <a href="docs/i18n/README.be.md">Беларуская</a> • <a href="docs/i18n/README.el.md">Ελληνικά</a> • <a href="docs/i18n/README.ca.md">Català</a> • <a href="docs/i18n/README.eu.md">Euskara</a> • <a href="docs/i18n/README.gl.md">Galego</a> • <a href="docs/i18n/README.cs.md">Čeština</a> • <a href="docs/i18n/README.sk.md">Slovenčina</a> • <a href="docs/i18n/README.hu.md">Magyar</a> • <a href="docs/i18n/README.hr.md">Hrvatski</a> • <a href="docs/i18n/README.sl.md">Slovenščina</a> • <a href="docs/i18n/README.bs.md">Bosanski</a> • <a href="docs/i18n/README.et.md">Eesti</a> • <a href="docs/i18n/README.lv.md">Latviešu</a> • <a href="docs/i18n/README.lt.md">Lietuvių</a> • <a href="docs/i18n/README.no.md">Norsk</a> • <a href="docs/i18n/README.da.md">Dansk</a> • <a href="docs/i18n/README.fi.md">Suomi</a> • <a href="docs/i18n/README.is.md">Íslenska</a> • <a href="docs/i18n/README.ms.md">Bahasa Melayu</a> • <a href="docs/i18n/README.tl.md">Tagalog</a> • <a href="docs/i18n/README.sw.md">Kiswahili</a> • <a href="docs/i18n/README.eo.md">Esperanto</a> • <a href="docs/i18n/README.zh_tw.md">繁體中文</a> • <a href="docs/i18n/README.ko.md">한국어</a> • <a href="docs/i18n/README.he.md">עברית</a> • <a href="docs/i18n/README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](CHANGELOG.fr.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](ROADMAP.fr.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) est un lecteur audio de bureau moderne, réactif et multiplateforme (Windows, Linux, macOS). Conçu pour offrir aux audiophiles un contrôle total sur leur bibliothèque musicale locale (MP3, FLAC, OGG…), il prend désormais en charge les listes de lecture (M3U, PLS, XSPF, WPL), les feuilles CUE (albums d'un seul fichier découpés en pistes) et intègre un tout nouveau mode blind test audio ! Le projet évolue pour devenir un centre de commande unifié capable d'organiser, dédoublonner et synchroniser des collections musicales hybrides réparties entre disques locaux, stockage cloud (Google Drive) et services de streaming (Spotify, Deezer, Amazon Music).

---

<p align="center">
  <img src="screenshots/2026-10-29%20v0.4.1.png" alt="Audio Multi-Source Organizer (AMSO) - Lecteur audio avec l'ambiance visuelle Hyperespace (champ d'étoiles 3D)" width="850">
</p>

<p align="center">
  <img src="screenshots/2026-10-25%20v0.4.0%2002.png" alt="Audio Multi-Source Organizer (AMSO) - Arborescence par dossiers & feuille CUE 💿 (pistes virtuelles)" width="850">
</p>

<p align="center">
  <img src="screenshots/2026-10-25%20v0.4.0.png" alt="Audio Multi-Source Organizer (AMSO) - Liste de lecture d'une feuille CUE (pistes virtuelles)" width="850">
</p>

<p align="center">
  <img src="screenshots/2026-10-18%20v0.3.0%20blind%20test.png" alt="Audio Multi-Source Organizer (AMSO) - Mini-jeu Blind Test & Décompte dynamique" width="850">
</p>

---

## 📌 Fonctionnalités & Statut du projet

| Fonctionnalité | Description | Statut |
| :--- | :--- | :---: |
| **Moteur de lecture audio** | Lecteur audio léger et autonome (VLC portable installé automatiquement sous Windows). Deux moteurs au choix : sortie directe VLC, ou moteur à tampon continu pour un enchaînement fluide entre deux pistes (Gapless 0 ms, fondu enchaîné à puissance égale, sans coupure de la sortie audio) | 🟢 Implémenté |
| **Gestion de la bibliothèque** | Scan récursif multithreadé des dossiers locaux (MP3, FLAC, AAC, OGG...), synchronisation manuelle, planifiée ou en temps réel, corbeille et statistiques de la bibliothèque | 🟢 Implémenté |
| **Extraction de métadonnées** | Lecture/écriture ID3, Vorbis Comments et calcul d'empreinte audio (`mutagen`) | 🟢 Implémenté |
| **Support des Playlists (M3U, PLS, XSPF, WPL) & feuilles CUE** | Indexation arborescente (🎶), ordre séquentiel d'écoute, repérage visuel des morceaux manquants ; les fichiers `.cue` (💿) s'ouvrent comme un dossier de pistes virtuelles avec leur durée et se lisent comme de vraies pistes | 🟢 Implémenté |
| **Gestionnaire de Playlist & Glisser-Déposer** | File d'attente virtualisée, drag & drop fluide, aléatoire (shuffle) réversible et boucles | 🟢 Implémenté |
| **Mode « 🎲 Blind Test » interactif** | Jeu musical immersif avec décompte animé, fondu sonore, révélation douce et enchaînement automatique | 🟢 Implémenté |
| **Mises à jour in-app** | Vérification automatique/manuelle des versions via GitHub Releases | 🟢 Implémenté |
| **Versions Linux & macOS** | Paquets `.AppImage` / `.tar.gz` (Linux) et `.dmg` non signé (macOS), VLC requis | 🟡 Expérimental (non testé) |
| **Gestion des artistes & Discographie** | Vue dédiée par artiste avec albums, singles et discographie complète | 🟡 Prévu |
| **Égaliseur graphique (EQ)** | Presets audio et égaliseur multibandes paramétrique | 🟡 Prévu |
| **Connecteur Google Drive** | Scan et synchronisation de collections audio distantes via OAuth 2.0 | ⚪ Planifié |
| **Connecteur Amazon Music** | Scan et synchronisation de collections distantes via OAuth 2.0 | ⚪ Planifié |
| **Connecteur Spotify / Deezer** | Importation de playlists et correspondance de pistes | ⚪ Planifié |
| **Dédoublonnage intelligent** | Détection de doublons (titre/artiste flous + empreintes acoustiques) | ⚪ Planifié |

> 💡 *Pour consulter le détail des jalons et versions prévues, référez-vous à la [Feuille de route (Roadmap)](ROADMAP.fr.md).*

---

## 📌 Langues disponibles

Anglais, Français, Espagnol, Allemand, Italien, Portugais, Japonais, Russe, Polonais, Turc, Néerlandais, Suédois, Indonésien, Bulgare, Serbe, Biélorusse, Grec, Catalan, Basque, Galicien, Tchèque, Slovaque, Hongrois, Croate, Slovène, Bosniaque, Estonien, Letton, Lituanien, Norvégien, Danois, Finnois, Islandais, Malais, Tagalog, Swahili, Espéranto, Chinois simplifié, Chinois traditionnel, Coréen, Arabe, Hébreu, Vietnamien

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

## 🐧🍎 Linux et macOS : versions expérimentales (non testées)

Les paquets Linux (`.AppImage` / `.tar.gz`) et macOS (`.dmg`) sont fournis **sans avoir été testés** : AMSO n'a été validé que sous Windows. Le moteur audio à tampon continu (`buffer`) en particulier n'a pas été vérifié sur ces systèmes. Votre retour est précieux.

- **VLC est requis** (AMSO ne le télécharge que sous Windows) :
  - Linux : `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) ou `sudo pacman -S vlc` (Arch).
  - macOS : installer **VLC.app** depuis [videolan.org](https://www.videolan.org/vlc/) dans le dossier Applications.
- **Linux, bibliothèques système** : l'interface Qt demande notamment `libpulse0` (son), `libxcb-cursor0` et `libxkbcommon-x11-0` (par exemple `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, `.dmg` non signé** : au premier lancement, faire un clic droit sur AMSO puis **Ouvrir**, ou exécuter `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage** : la rendre exécutable avec `chmod +x AMSO*.AppImage`.
- **En cas de problème**, merci d'envoyer les fichiers `startup.log` et `crash.log` (s'il existe) situés dans le dossier de données : `~/Library/Application Support/AMSO/` sous macOS, `~/.local/share/AMSO/` sous Linux. Précisez votre système et la version de VLC.

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

- 🎮 **Téléchargement & Pay What You Want :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (exécutable précompilé prêt à l'emploi)
- ☕ **Faire un don direct :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [Sponsoriser LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licence

Ce projet est sous licence **GNU General Public License v3.0 (GPL-3.0)** — consultez le fichier [LICENSE](LICENSE) pour plus de détails.
