# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <b>Svenska</b> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) är en modern, responsiv och plattformsoberoende (Windows, Linux, macOS) skrivbords-audiospelare. Designad för att ge audiophiler total kontroll över deras lokala musikbibliotek (MP3, FLAC, OGG...), stöder den nu även spellistor (M3U, PLS, XSPF, WPL), CUE-filer (album i en enda fil uppdelade i spår) och integrerar ett helt nytt audio blind test-läge! Projektet utvecklas till ett enhetligt kontrollcenter som kan organisera, deduplicera och synkronisera hybrida musiksamlingar som är utspridda mellan lokala enheter, molnlagring (Google Drive) och streamingtjänster (Spotify, Deezer, Amazon Music).

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

## 📌 Funktioner & Projektstatus

| Funktion | Beskrivning | Status |
| :--- | :---: | :---: |
| **Integrerad VLC-spelare** | Lättviktig och oberoende ljudspelare med automatisk installation av portabel VLC och smidig volymhantering | 🟢 Implementerad |
| **Multitrådad lokal skanner** | Rekursiv och snabb upptäckt av lokala ljudfiler (MP3, FLAC, AAC, OGG...) | 🟢 Implementerad |
| **Metadataextraktion** | Läsa/skriva ID3, Vorbis Comments och beräkna ljudfingeravtryck (`mutagen`) | 🟢 Implementerad |
| **Stöd för spellistor (M3U, PLS, XSPF, WPL) & CUE-ark** | Träindexering (🎶), sekventiell lyssningsordning, visuell identifiering av saknade låtar; `.cue`-filer (💿) öppnas som en virtuell spårkatalog med varaktighet och spelas som riktiga spår | 🟢 Implementerad |
| **Spellistthanterare & Drag-and-Drop** | Virtualiserad kö, smidigt drag & drop, reversibel slumpmässighet (shuffle) och loopar | 🟢 Implementerad |
| **Interaktivt "🎲 Blind Test"-läge** | Immersivt musikspel med animerad nedräkning, ljudfade, mjuk avslöjande och automatisk sekvensering | 🟢 Implementerad |
| **Uppdateringar i appen** | Automatisk/manuell versionskontroll via GitHub Releases | 🟢 Implementerat |
| **Hantering av artister & diskografi** | Dedikerad vy per artist med album, singlar och komplett diskografi | 🟡 Planerat |
| **Grafisk equalizer (EQ)** | Audio-presets och parametrisk flerbånds-equalizer | 🟡 Planerat |
| **Google Drive-anslutning** | Skanning och synkronisering av fjärr-audio-samlingar via OAuth 2.0 | ⚪ Planerat |
| **Amazon Music-anslutning** | Skanning och synkronisering av fjärr-samlingar via OAuth 2.0 | ⚪ Planerat |
| **Spotify / Deezer-anslutning** | Importera spellistor och spårmatchning | ⚪ Planerat |
| **Smart deduplicering** | Detektering av dubletter (oskarp titel/artist + akustiska fingeravtryck) | ⚪ Planerat |

> 💡 *För att se detaljer om de planerade milstolparna och versionerna, hänvisa till [Karta (Roadmap)](../../ROADMAP.md).*

---

## 📌 Tillgängliga språk

Engelska, Franska, Spanska, Tyska, Italienska, Portugisiska, Japanska, Ryska, Polska, Turkiska, Nederländska, Svenska, Indonesiska, Bulgariska, Serbiska, Białorusiska, Grekiska, Katalanska, Baskiska, Galiciska, Tjeckiska, Slovakiska, Ungerska, Kroatiska, Sloveniska, Bosniska, Estniska, Lettiska, Litauiska, Norska, Danska, Finska, Islandiska, Malayiska, Tagalogiska, Swahiliska, Esperanto, Mandarin (förenklat), Mandarin (traditionellt), Koreanska, Arabiska, Hebreiska, Vietnamesiska

---

## 🚀 Snabbstart

### Förutsättningar

- **Python 3.11** eller högre installerat
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

## 🧪 Start av tester

Projektet använder `pytest` med en svit av enhetstester och integrationstester:

```bash
pytest -v
```

Testerna körs automatiskt på **Windows, macOS och Ubuntu** vid varje push via GitHub Actions.

---

## 🔒 Säkerhet & API-nycklar

- **Commit aldrig riktiga API-nycklar eller autentiseringstokens.**
- Filen `.gitignore` är förkonfigurerad för att blockera `.env`, `credentials.json`, `token.json` och alla lokala SQLite-databaser.
- Använd `.env.example` som mall för din utvecklingsmiljö.

---

## 📋 Dokumentation & Projektuppföljning

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Detaljerad logg över versioner, nya funktioner och buggfixar.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Framtida milstolpar (Artister, Cloud, Spotify, Avduplicering).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Charter för mjukvaruarkitektur och regler för kodkvalitet.

---

## 💖 Stödja projektet & Distribution

AMSO är en fri och gratis programvara (open source). Om du gillar applikationen och vill stödja dess utveckling:

- 🎮 **Nedladdning & Betala vad du vill :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (färdigkompilerbar exekverbar fil redo att användas)
- ☕ **Ge ett direkt bidrag :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [Sponsorera LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licens

Detta projekt är under licens **GNU General Public License v3.0 (GPL-3.0)** — konsultera filen [LICENSE](../../LICENSE) för mer information.
