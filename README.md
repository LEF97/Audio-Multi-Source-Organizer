# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="README.fr.md">Français</a> • <b>English</b> • <a href="docs/i18n/README.es.md">Español</a> • <a href="docs/i18n/README.de.md">Deutsch</a> • <a href="docs/i18n/README.it.md">Italiano</a> • <a href="docs/i18n/README.pt.md">Português</a> • <a href="docs/i18n/README.zh_cn.md">简体中文</a> • <a href="docs/i18n/README.ja.md">日本語</a> • <a href="docs/i18n/README.ru.md">Русский</a> • <a href="docs/i18n/README.ar.md">العربية</a>
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
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Future%20Milestones-purple.svg)](ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) is a modern, responsive, cross-platform desktop audio player (Windows, Linux, macOS). Built to give audiophiles complete control over their local music library (MP3, FLAC, OGG…), it now supports playlist files (M3U, PLS, XSPF, WPL), CUE sheets (single-file albums split into tracks) and features an interactive audio blind test game! The project is expanding to become a unified command center capable of organizing, deduplicating, and synchronizing hybrid music collections across local storage, cloud services (Google Drive), and streaming platforms (Spotify, Deezer, Amazon Music).

---

<p align="center">
  <img src="screenshots/2026-10-29%20v0.4.1.png" alt="Audio Multi-Source Organizer (AMSO) - Audio player with the Hyperspace (3D starfield) visual ambience" width="850">
</p>

<p align="center">
  <img src="screenshots/2026-10-25%20v0.4.0%2002.png" alt="Audio Multi-Source Organizer (AMSO) - Folder tree & CUE sheet 💿 (virtual tracks)" width="850">
</p>

<p align="center">
  <img src="screenshots/2026-10-25%20v0.4.0.png" alt="Audio Multi-Source Organizer (AMSO) - Playlist of a CUE sheet (virtual tracks)" width="850">
</p>

<p align="center">
  <img src="screenshots/2026-10-18%20v0.3.0%20blind%20test.png" alt="Audio Multi-Source Organizer (AMSO) - Interactive Blind Test Mini-game" width="850">
</p>

---

## 📌 Features & Project Status

| Feature | Description | Status |
| :--- | :--- | :---: |
| **Audio Playback Engine** | Lightweight, standalone audio player (portable VLC set up automatically on Windows). Two engines to choose from: direct VLC output, or a continuous buffer engine for smooth transitions between two tracks (Gapless 0 ms, equal-power crossfade, no cut in the audio output) | 🟢 Implemented |
| **Library Management** | Multithreaded recursive scan of local folders (MP3, FLAC, AAC, OGG...), manual, scheduled or real-time synchronization, trash and library statistics | 🟢 Implemented |
| **Metadata & Artwork Extraction** | ID3 tags, Vorbis Comments, and audio fingerprinting extraction (`mutagen`) | 🟢 Implemented |
| **Playlist Files Support (M3U, PLS, XSPF, WPL) & CUE sheets** | Tree-based indexing (🎶), natural sequential track ordering, visual missing track alerts; `.cue` files (💿) open like a folder of virtual tracks with their duration and play like real tracks | 🟢 Implemented |
| **Playlist & Queue Management** | Virtualized queue table, smooth drag & drop reordering, reversible shuffle, and repeat modes | 🟢 Implemented |
| **Interactive « 🎲 Blind Test » Mode** | Immersive music guessing game with animated pulsing countdown, soft audio fade-out, smooth reveal, and auto-progression | 🟢 Implemented |
| **In-App Update Checker** | Automatic and manual version checking via GitHub Releases | 🟢 Implemented |
| **Linux & macOS versions** | `.AppImage` / `.tar.gz` packages (Linux) and unsigned `.dmg` (macOS), VLC required | 🟡 Experimental (untested) |
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

## 🐧🍎 Linux and macOS: experimental versions (untested)

The Linux (`.AppImage` / `.tar.gz`) and macOS (`.dmg`) packages are provided **without having been tested**: AMSO has only been validated on Windows. The continuous buffer audio engine (`buffer`) in particular has not been verified on these systems. Your feedback is valuable.

- **VLC is required** (AMSO only downloads it on Windows):
  - Linux: `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) or `sudo pacman -S vlc` (Arch).
  - macOS: install **VLC.app** from [videolan.org](https://www.videolan.org/vlc/) into the Applications folder.
- **Linux, system libraries**: the Qt interface notably needs `libpulse0` (sound), `libxcb-cursor0` and `libxkbcommon-x11-0` (for example `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, unsigned `.dmg`**: on first launch, right-click AMSO then choose **Open**, or run `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage**: make it executable with `chmod +x AMSO*.AppImage`.
- **If you run into a problem**, please send the `startup.log` and `crash.log` files (if it exists) located in the data folder: `~/Library/Application Support/AMSO/` on macOS, `~/.local/share/AMSO/` on Linux. Please mention your system and your VLC version.

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
