# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <b>Norsk</b> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) er en moderne, responsiv og tverrplattform desktop lydspiller (Windows, Linux, macOS). Designet for å gi audiophiler full kontroll over deres lokale musikkbibliotek (MP3, FLAC, OGG…), støtter det nå spillelister (M3U, PLS, XSPF, WPL), CUE-ark (album i én fil delt inn i spor) og integrerer en helt ny lyd blindtest-modus! Prosjektet utvikler seg til å bli et sentralisert kontrollsenter som er i stand til å organisere, fjerne duplikater og synkronisere hybride musikk-samlinger spredt mellom lokale disker, sky-lagring (Google Drive) og strømmetjenester (Spotify, Deezer, Amazon Music).

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

## 📌 Funksjoner & Status for prosjektet

| Funksjonalitet | Beskrivelse | Status |
| :--- | :---: | :---: |
| **Integrert VLC-avspillingsmotor** | Lett og selvstendig lydspiller med automatisk installasjon av VLC portable og jevn volumkontroll | 🟢 Implémenté |
| **Multitrådet lokal skanner** | Rask og rekursiv oppdagelse av lokale lydfiler (MP3, FLAC, AAC, OGG...) | 🟢 Implémenté |
| **Ekstraksjon av metadata** | Lesing/skriving av ID3, Vorbis Comments og beregning av lydavtrykk (`mutagen`) | 🟢 Implémenté |
| **Støtte for spillelister (M3U, PLS, XSPF, WPL) & CUE-ark** | Trestrukturert indeksering (🎶), sekvensiell avspillingsrekkefølge, visuell sporing av manglende spor; `.cue`-filer (💿) åpnes som en virtuell spormappe med varighet og spilles av som ekte spor | 🟢 Implémenté |
| **Spillelistehåndterer & Dra-og-slipp** | Virtualisert kø, jevn dra-og-slipp, reversibel tilfeldig (shuffle) og looper | 🟢 Implémenté |
| **Interaktiv « 🎲 Blind Test »-modus** | Immersivt musikalsk spill med animert nedtelling, lydfade, myk avsløring og automatisk sekvensering | 🟢 Implémenté |
| **In-app-oppdateringer** | Automatisk/manuel versjonskontroll via GitHub Releases | 🟢 Implementert |
| **Håndtering av artister & diskografi** | Dedikert visning per artist med album, singler og komplett diskografi | 🟡 Planlagt |
| **Grafisk equalizer (EQ)** | Lydpresets og parametrisk multibånd-equalizer | 🟡 Planlagt |
| **Google Drive-kobling** | Skanning og synkronisering av eksterne lydsamlinger via OAuth 2.0 | ⚪ Planlagt |
| **Amazon Music-kobling** | Skanning og synkronisering av eksterne samlinger via OAuth 2.0 | ⚪ Planlagt |
| **Spotify / Deezer-kobling** | Import av spillelister og spor-matching | ⚪ Planlagt |
| **Intelligent duplikatfjerning** | Deteksjon av duplikater (uklar tittel/artist + akustiske fingeravtrykk) | ⚪ Planlagt |

> 💡 *For å se detaljene for de planlagte milepælene og versjonene, se [Veikart (Roadmap)](../../ROADMAP.md).*

---

## 📌 Tilgjengelige språk

Engelsk, Fransk, Spansk, Tysk, Italiensk, Portugisisk, Japansk, Russisk, Polsk, Tyrkisk, Nederlandsk, Svensk, Indonesisk, Bulgarsk, Serbisk, Hviterussisk, Gresk, Katalansk, Baskisk, Galisisk, Tsjekkisk, Slovakisk, Ungarsk, Kroatisk, Slovenisk, Bosnisk, Estisk, Lettisk, Litauisk, Norsk, Dansk, Finsk, Islandsk, Malajisk, Tagalogisk, Swahili, Esperanto, Forenklet kinesisk, Tradisjonelt kinesisk, Koreansk, Arabisk, Hebraisk, Vietnamesisk

---

## 🚀 Rask oppstart

### Forutsetninger

- **Python 3.11** eller høyere installert
- Git

### Installasjon

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

## 🧪 Oppstart av tester

Prosjektet bruker `pytest` med en suite av enhetstester og integrasjonstester:

```bash
pytest -v
```

Testene kjøres automatisk på **Windows, macOS og Ubuntu** ved hvert push via GitHub Actions.

---

## 🔒 Sikkerhet & API-nøkler

- **Kom aldri med faktiske API-nøkler eller autentiseringstokener.**
- Filen `.gitignore` er forhåndskonfigurert for å blokkere `.env`, `credentials.json`, `token.json` og alle lokale SQLite-databaser.
- Bruk `.env.example` som mal for ditt utviklingsmiljø.

---

## 📋 Dokumentasjon & Prosjektsporing

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Detaljert logg over versjoner, nye funksjoner og feilrettinger.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Veikart for fremtidige milepæler (Artister, Cloud, Spotify, De-duplisering).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Arkitekturcharter for programvare og regler for kodekvalitet.

---

## 💖 Støtte prosjektet & Distribusjon

AMSO er en fri og gratis programvare (open source). Hvis du liker applikasjonen og ønsker å støtte utviklingen:

- 🎮 **Nedlasting & Betal det du vil :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (ferdigkompilert kjøremedie klart til bruk)
- ☕ **Doner direkte :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [Sponsorer LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Lisens

Dette prosjektet er under lisens **GNU General Public License v3.0 (GPL-3.0)** — se filen [LICENSE](../../LICENSE) for flere detaljer.
