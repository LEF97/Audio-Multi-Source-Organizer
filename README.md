# Audio Multi-Source Organizer (AMSO)

<p align="right">
  <a href="README.fr.md">Français</a> • <b>English</b> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a>
</p>

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Future%20Milestones-purple.svg)](ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) is a modern, responsive, cross-platform desktop audio player (Windows, Linux, macOS). Built to give audiophiles complete control over their local music library (MP3, FLAC, OGG…), it now supports playlist files (M3U, PLS, XSPF, WPL) and features an interactive audio blind test game! The project is expanding to become a unified command center capable of organizing, deduplicating, and synchronizing hybrid music collections across local storage, cloud services (Google Drive), and streaming platforms (Spotify, Deezer, Amazon Music).

---

<p align="center">
  <img src="screenshots/2026-10-18%20v0.3.0%2002.png" alt="Audio Multi-Source Organizer (AMSO) - Folder Tree & Playlists 🎶" width="850">
</p>

<p align="center">
  <img src="screenshots/2026-10-18%20v0.3.0.png" alt="Audio Multi-Source Organizer (AMSO) - Audio Player & Hyperspace Ambience" width="850">
</p>

<p align="center">
  <img src="screenshots/2026-10-18%20v0.3.0%20blind%20test.png" alt="Audio Multi-Source Organizer (AMSO) - Interactive Blind Test Mini-game" width="850">
</p>

---

## 📌 Features & Project Status

| Feature | Description | Status |
| :--- | :--- | :---: |
| **Integrated VLC Playback Engine** | Lightweight, standalone audio player with automatic portable VLC setup and smooth volume control | 🟢 Implemented |
| **High-Speed Multithreaded Scanner** | Fast recursive traversal and indexing of local audio files (MP3, FLAC, AAC, OGG...) | 🟢 Implemented |
| **Metadata & Artwork Extraction** | ID3 tags, Vorbis Comments, and audio fingerprinting extraction (`mutagen`) | 🟢 Implemented |
| **Playlist Files Support (M3U, PLS, XSPF, WPL)** | Tree-based indexing (🎶), natural sequential track ordering, and visual missing track alerts | 🟢 Implemented |
| **Playlist & Queue Management** | Virtualized queue table, smooth drag & drop reordering, reversible shuffle, and repeat modes | 🟢 Implemented |
| **Interactive « 🎲 Blind Test » Mode** | Immersive music guessing game with animated pulsing countdown, soft audio fade-out, smooth reveal, and auto-progression | 🟢 Implemented |
| **In-App Update Checker** | Automatic and manual version checking via GitHub Releases | 🟢 Implemented |
| **Artists & Discography Hub** | Dedicated artist overview with albums, singles, and full discographies | 🟡 Planned |
| **Graphical Equalizer (EQ)** | Curated sound presets and multi-band parametric equalizer | 🟡 Planned |
| **Google Drive Cloud Connector** | Remote audio library indexing and streaming via OAuth 2.0 | ⚪ Planned |
| **Amazon Music Connector** | Remote music folder scanning and cloud sync via OAuth 2.0 | ⚪ Planned |
| **Spotify / Deezer Streaming Integration** | Playlist import and hybrid collection track matching | ⚪ Planned |
| **Intelligent Deduplication** | Duplicate detection based on fuzzy metadata and acoustic audio fingerprints | ⚪ Planned |

> 💡 *For detailed milestones and version planning, refer to the [Project Roadmap](ROADMAP.md).*

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11** or newer
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/LEF97/Audio-Multi-Source-Organizer.git
cd audio-multi-source-organizer

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# For development & running tests:
pip install -e .[dev]

# 5. Configure environment variables
cp .env.example .env

# 6. Launch AMSO
python main.py
```

---

## 🧪 Running Tests

The test suite is built with `pytest` covering unit and integration scenarios:

```bash
pytest -v
```

Tests run automatically across **Windows, macOS, and Ubuntu** on every push via GitHub Actions.

---

## 🔒 Security & API Keys

- **Never commit real API keys, secrets, or OAuth tokens.**
- The project `.gitignore` file is pre-configured to exclude `.env`, `credentials.json`, `token.json`, and local SQLite database files.
- Use `.env.example` as a template for your local development environment.

---

## 📋 Documentation & Project Tracking

- 📜 **[CHANGELOG.md](CHANGELOG.md)** ([Version Française](CHANGELOG.fr.md)): Detailed version logs, new features, and bug fixes.
- 🗺️ **[ROADMAP.md](ROADMAP.md)** ([Version Française](ROADMAP.fr.md)): Upcoming development milestones (Artists, Cloud, Spotify, Deduplication).
- 📐 **[CODE_QUALITY.md](CODE_QUALITY.md)**: Software architecture principles and code quality standards.

---

## 💖 Support the Project & Distribution

AMSO is 100% free and open-source software. If you enjoy the project and want to support ongoing development:

* 🎮 **Download & Pay What You Want:** [AMSO on Itch.io](https://lef97.itch.io/audio-multi-source-organizer) (precompiled portable standalone executable)
* ☕ **Direct Donation:** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
* ⭐ **GitHub Sponsors:** [Sponsor LEF97](https://github.com/sponsors/LEF97)

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)** — see the [LICENSE](LICENSE) file for full details.
