# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <b>Tagalog</b> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) ay isang modernong, responsive, at cross-platform na desktop audio player (Windows, Linux, macOS). Dinisenyo ito upang bigyan ang mga audiophile ng ganap na kontrol sa kanilang lokal na music library (MP3, FLAC, OGG...), at ngayon ay sinusuportahan na nito ang mga playlist (M3U, PLS, XSPF, WPL), CUE sheets (mga album na isang file lang na hinati sa mga track), at nag-iincorporate ng isang bagong audio blind test mode! Ang proyekto ay nagbabago upang maging isang unified command center na kayang mag-organisa, mag-deduplicate, at mag-synchronize ng mga hybrid music collection na nakakalat sa mga lokal na drive, cloud storage (Google Drive), at streaming services (Spotify, Deezer, Amazon Music).

---

<p align="center">
  <img src="../../screenshots/2026-10-29%20v0.4.1.png" alt="Audio Multi-Source Organizer (AMSO) - Lecteur audio avec l'ambiance visuelle Hyperespace (champ d'étoiles 3D)" width="850">
</p>

<p align="center">
  <img src="../../screenshots/2026-10-25%20v0.4.0%2002.png" alt="Audio Multi-Source Organizer (AMSO) - Arborescence par dossiers & feuille CUE 💿 (pistes virtuelles)" width="850">
</p>

<p align="center">
  <img src="../../screenshots/2026-10-25%20v0.4.0.png" alt="Audio Multi-Source Organizer (AMSO) - Liste de lecture d'une feuille CUE (pistes virtuelles)" width="850">
</p>

<p align="center">
  <img src="../../screenshots/2026-10-18%20v0.3.0%20blind%20test.png" alt="Audio Multi-Source Organizer (AMSO) - Mini-jeu Blind Test & Décompte dynamique" width="850">
</p>

---

## 📌 Mga Tampok & Katayuan ng Proyekto

| Katangian | Deskripsyon | Katayuan |
| :--- | :---: | :---: |
| **Audio Playback Engine** | Magaan at self-contained na audio player (VLC portable na awtomatikong naka-install sa Windows). Dalawang engine na pagpipilian: direktang output ng VLC, o continuous buffer engine para sa maayos na paglipat sa pagitan ng dalawang track (Gapless 0 ms, equal power crossfade, walang putol sa audio output) | 🟢 Naipatupad |
| **Library Management** | Recursive multithreaded scan ng mga lokal na folder (MP3, FLAC, AAC, OGG...), manual, scheduled, o real-time synchronization, trash, at library statistics | 🟢 Naipatupad |
| **Metadata Extraction** | Pagbasa/pagsulat ng ID3, Vorbis Comments, at pag-compute ng audio fingerprint (`mutagen`) | 🟢 Naipatupad |
| **Support for Playlists (M3U, PLS, XSPF, WPL) & CUE sheets** | Tree indexing (🎶), sequential listening order, visual locator para sa mga nawawalang kanta; ang mga file na `.cue` (💿) ay nagbubukas tulad ng isang virtual track folder kasama ang kanilang tagal at pinapatugtog tulad ng totoong track | 🟢 Naipatupad |
| **Playlist Manager & Drag-and-Drop** | Virtualized queue, smooth drag & drop, reversible shuffle, at loops | 🟢 Naipatupad |
| **Interactive "🎲 Blind Test" Mode** | Immersive music game na may animated countdown, sound fade, soft reveal, at automatic sequencing | 🟢 Naipatupad |
| **Mga Pag-update sa App** | Automatic/manual version checking via GitHub Releases | 🟢 Na-implementa |
| **Mga Bersyon ng Linux & macOS** | Paquets `.AppImage` / `.tar.gz` (Linux) at `.dmg` non-signed (macOS), VLC required | 🟡 Eksperimental (hindi pa nasubukan) |
| **Pamamahala ng Artista & Diskograpiya** | Dedicated view per artist with albums, singles, and complete discography | 🟡 Planado |
| **Graphic Equalizer (EQ)** | Audio presets at parametric multi-band equalizer | 🟡 Planado |
| **Google Drive Connector** | Scanning and synchronizing remote audio collections via OAuth 2.0 | ⚪ Planado |
| **Amazon Music Connector** | Scanning and synchronizing remote collections via OAuth 2.0 | ⚪ Planado |
| **Spotify / Deezer Connector** | Importing playlists and track matching | ⚪ Planado |
| **Smart Deduplication** | Duplicate detection (fuzzy title/artist + acoustic fingerprints) | ⚪ Planado |

> 💡 *Upang tingnan ang detalye ng mga nakaplanong milestone at bersyon, tumukoy sa [Feuille de route (Roadmap)](../../ROADMAP.md).*

---

## 📌 Mga magagamit na wika

English, Pranses, Espanyol, Aleman, Italyano, Portuges, Hapon, Ruso, Polish, Turki, Dutch, Sueyde, Indonesian, Bulgaro, Serbiano, Belarusian, Griyego, Catalan, Basque, Galician, Tsyeko, Slovak, Hungarian, Kroatis, Slovenian, Bosnian, Estonian, Latvian, Lituanian, Norwegian, Danish, Finnish, Icelandic, Malay, Tagalog, Swahili, Esperanto, Simpleng Tsino, Tradisyonal na Tsino, Koreano, Arabe, Hebreo, Vietnamese

---

## 🚀 Mabilisang pagsisimula

### Mga Kinakailangan

- **Python 3.11** o mas mataas na naka-install
- Git

### Pag-i-install

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

## 🐧🍎 Linux at macOS: mga bersyon na eksperimental (hindi nasubukan)

Ang mga package ng Linux (`.AppImage` / `.tar.gz`) at macOS (`.dmg`) ay ibinibigay **nang hindi nasubukan**: Ang AMSO ay na-validate lamang sa Windows. Ang audio engine na may continuous buffer (`buffer`) ay partikular na hindi na-check sa mga sistemang ito. Mahalaga ang iyong feedback.

- **Kailangan ang VLC** (Ang AMSO ay nagda-download lamang nito sa Windows):
  - Linux : `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) o `sudo pacman -S vlc` (Arch).
  - macOS : i-install ang **VLC.app** mula sa [videolan.org](https://www.videolan.org/vlc/) sa Applications folder.
- **Linux, system libraries** : Hinihingi ng Qt interface ang `libpulse0` (tunog), `libxcb-cursor0` at `libxkbcommon-x11-0` (halimbawa `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, hindi nilagdaan na `.dmg`** : sa unang paglunsad, mag-right-click sa AMSO pagkatapos ay **Open**, o patakbuhin ang `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage** : gawin itong executable gamit ang `chmod +x AMSO*.AppImage`.
- **Kung may problema**, paki-send ang mga file na `startup.log` at `crash.log` (kung umiiral) na matatagpuan sa data folder: `~/Library/Application Support/AMSO/` sa macOS, `~/.local/share/AMSO/` sa Linux. Tukuyin ang iyong sistema at ang bersyon ng VLC.

---

## 🧪 Paglulunsad ng mga pagsubok

Gumagamit ang proyekto ng `pytest` kasama ang isang suite ng mga unit at integration tests:

```bash
pytest -v
```

Ang mga test ay awtomatikong tumatakbo sa **Windows, macOS, at Ubuntu** sa bawat push via GitHub Actions.

---

## 🔒 Seguridad & Mga Susi ng API

- **Huwag kailanman i-commit ang mga tunay na API key o authentication token.**
- Ang file na `.gitignore` ay pre-configured para harangan ang `.env`, `credentials.json`, `token.json`, at lahat ng lokal na SQLite database.
- Gamitin ang `.env.example` bilang template para sa iyong development environment.

---

## 📋 Dokumentasyon & Pagsubaybay sa proyekto

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Detalyadong talaan ng mga bersyon, bagong tampok, at pagtatama ng bug.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Roadmap ng mga susunod na milestone (Artistas, Cloud, Spotify, Pag-aalis ng Duplicates).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Patakaran sa arkitektura ng software at mga alituntunin sa kalidad ng code.

---

## 💖 Pagsuporta sa Proyekto & Pamamahagi

AMSO ay isang libre at open-source na software. Kung nagugustuhan mo ang application at gusto mong suportahan ang pag-unlad nito:

- 🎮 **Pag-download & Pay What You Want :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (pre-compiled executable ready to use)
- ☕ **Direktang Donasyon :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [Sponsoriser LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Lisensya

Ang proyektong ito ay nasa ilalim ng lisensya **GNU General Public License v3.0 (GPL-3.0)** — tingnan ang file [LICENSE](../../LICENSE) para sa mas maraming detalye.
