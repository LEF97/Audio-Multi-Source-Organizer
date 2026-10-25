# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <b>Dansk</b> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) er en moderne, responsiv og tværmodsat desktop-lydafspiller (Windows, Linux, macOS). Designet til at give audiophiler fuld kontrol over deres lokale musikbibliotek (MP3, FLAC, OGG…), understøtter den nu også playlister (M3U, PLS, XSPF, WPL), CUE-ark (albummer i én fil opdelt i spor) og integrerer en helt ny blind test audio-tilstand! Projektet udvikler sig til at blive et samlet kontrolcenter, der kan organisere, de-duplikere og synkronisere hybride musiksamlinger spredt mellem lokale diske, cloud-lagring (Google Drive) og streamingtjenester (Spotify, Deezer, Amazon Music).

---

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

## 📌 Funktionaliteter & Status for projektet

| Funktion | Beskrivelse | Status |
| :--- | :---: | :---: |
| **Integreret VLC afspilningsmotor** | Letvægts, selvstændig lydafspiller med automatisk installation af VLC portable og flydende volumenkontrol | 🟢 Implementeret |
| **Multitrådet lokal scanner** | Hurtig og rekursiv opdagelse af lokale lydfiler (MP3, FLAC, AAC, OGG...) | 🟢 Implementeret |
| **Metadataekstraktion** | Læsning/skrivning af ID3, Vorbis Comments og beregning af lydaftryk (`mutagen`) | 🟢 Implementeret |
| **Understøttelse af playlister (M3U, PLS, XSPF, WPL) & CUE-ark** | Træindeksering (🎶), sekventiel lytteorden, visuel identifikation af manglende numre; .cue-filer (💿) åbnes som en mappe med virtuelle spor med deres varighed og afspilles som rigtige spor | 🟢 Implementeret |
| **Playlist-administrator & Træk-og-slip** | Virtualiseret kø, flydende drag & drop, reversibel tilfældig (shuffle) og loops | 🟢 Implementeret |
| **Interaktiv "🎲 Blind Test" tilstand** | Immersiv musikalsk spil med animeret nedtælling, lydfade, blød afsløring og automatisk sekvensering | 🟢 Implementeret |
| **Opdateringer i appen** | Automatisk/manuel versionskontrol via GitHub Releases | 🟢 Implementeret |
| **Håndtering af kunstnere & diskografi** | Dedikeret visning pr. kunstner med album, singler og komplet diskografi | 🟡 Planlagt |
| **Grafisk equalizer (EQ)** | Audio presets og parametrisk multi-bånd equalizer | 🟡 Planlagt |
| **Google Drive-forbindelse** | Scan og synkronisering af fjerne lydsamlinger via OAuth 2.0 | ⚪ Planlagt |
| **Amazon Music-forbindelse** | Scan og synkronisering af fjerne samlinger via OAuth 2.0 | ⚪ Planlagt |
| **Spotify / Deezer-forbindelse** | Import af playlister og spor-matching | ⚪ Planlagt |
| **Intelligent deduplikering** | Detektion af duplikater (fuzzy titel/artist + akustiske fingeraftryk) | ⚪ Planlagt |

> 💡 *For at se detaljerne for milepælene og de planlagte versioner, henvis til [Roadmap (Roadmap)](../../ROADMAP.md).*

---

## 📌 Tilgængelige sprog

Engelsk, Fransk, Spansk, Tysk, Italiensk, Portugisisk, Japansk, Russisk, Polsk, Tyrkisk, Hollandsk, Svensk, Indonesisk, Bulgarsk, Serbisk, Hviderussisk, Græsk, Katalansk, Baskisk, Galicisk, Tjekkisk, Slovakisk, Ungarsk, Kroatisk, Slovenisk, Bosnisk, Estisk, Lettisk, Litauisk, Norsk, Dansk, Finsk, Islandsk, Malajisk, Tagalogisk, Swahili, Esperanto, Forenklet kinesisk, Traditionelt kinesisk, Koreansk, Arabisk, Hebrewisk, Vietnamesisk

---

## 🚀 Hurtig start

### Forudsætninger

- **Python 3.11** eller højere installeret
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

## 🧪 Lancering af tests

Projektet bruger `pytest` med enhedstests og integrationstests:

```bash
pytest -v
```

Testene kører automatisk på **Windows, macOS og Ubuntu** ved hvert push via GitHub Actions.

---

## 🔒 Sikkerhed & API-nøgler

- **Commit aldrig virkelige API-nøgler eller autentifikationstokens.**
- Filen `.gitignore` er forkonfigureret til at blokere `.env`, `credentials.json`, `token.json` og alle lokale SQLite-databasér.
- Brug `.env.example` som skabelon for dit udviklingsmiljø.

---

## 📋 Dokumentation & Projektsporing

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Detaljeret log over versioner, nye funktioner og fejlrettelser.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Vejviser for fremtidige milepæle (Kunstnere, Cloud, Spotify, De-duplikering).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Charter for softwarearkitektur og regler for kodekvalitet.

---

## 💖 Støtte til projektet & Distribution

AMSO er en fri og gratis software (open source). Hvis du kan lide applikationen og ønsker at støtte dens udvikling:

- 🎮 **Download & Pay What You Want :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (færdigkompilerbar, klar til brug)
- ☕ **Gør en direkte donation :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [Sponsorér LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licens

Dette projekt er under licens **GNU General Public License v3.0 (GPL-3.0)** — se filen [LICENSE](../../LICENSE) for flere detaljer.
