# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <b>Slovenčina</b> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) je moderný, reaktívny a multiplatformový desktopový audio prehrávač (Windows, Linux, macOS). Navrhnutý, aby audiofilom poskytol úplnú kontrolu nad ich lokálnou muzickú knižnicou (MP3, FLAC, OGG…), teraz podporuje playlisty (M3U, PLS, XSPF, WPL), CUE listy (albumy z jedného súboru rozdelené na skladby) a integruje úplne nový režim audio blind testu! Projekt sa vyvíja na smer jednotné ovládacie centrum schopné organizovať, odstraňovať duplikáty a synchronizovať hybridné muzické kolekcie rozptípané medzi lokálnymi diskovými médiami, cloudovým skladovaním (Google Drive) a streaming službami (Spotify, Deezer, Amazon Music).

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

## 📌 Funkcie & Stav projektu

| Funkcia | Popis | Stav |
| :--- | :---: | :---: |
| **Integrovaný VLC prehrávač** | Lehký a samostatný audio prehrávač s automatickou instaláciou VLC portable a plynulou správou hlasitosti | 🟢 Implementované |
| **Multithreadový lokálny skener** | Rekurzívna a rýchla detekcia lokálnych audio súborov (MP3, FLAC, AAC, OGG...) | 🟢 Implementované |
| **Extrakcia metadát** | Čítanie/zápis ID3, Vorbis Comments a výpočet audio fingerprintu (`mutagen`) | 🟢 Implementované |
| **Podpora playlistov (M3U, PLS, XSPF, WPL) a CUE listov** | Stromové indexovanie (🎶), sekvenčný poradie počúvania, vizuálna identifikácia chýbajúceho obsahu; súbory `.cue` (💿) sa otvoria ako adresár virtuálnych skladieb s ich trvaním a prehrávajú sa ako skutočné skladby | 🟢 Implementované |
| **Správca playlistov a pretaženie (Drag & Drop)** | Virtualizovaná výčka, plynulé pretaženie, zvracie šuffle a smiečky | 🟢 Implementované |
| **Interaktívny režim „🎲 Blind Test“** | Imerzitívna hudobná hra s animovaným odpočítavaniím, zvukovým fadeom, jemným odhalením a automatickým prechádzaním | 🟢 Implementované |
| **Aktualizácie v aplikácii** | Automatická/ručná kontrola verzií cez GitHub Releases | 🟢 Implementované |
| **Správa umelníkov a diskografie** | Dedikovaný prehľad umelníka s albumami, singlmi a kompletnou diskografiou | 🟡 Plánované |
| **Grafický ekvalizér (EQ)** | Audio prednastavenia a parametrický viacúrovňový ekvalizér | 🟡 Plánované |
| **Konektor Google Drive** | Skenering a synchronizácia vzdialených audio kolekcií cez OAuth 2.0 | ⚪ Plánované |
| **Konektor Amazon Music** | Skenering a synchronizácia vzdialených kolekcií cez OAuth 2.0 | ⚪ Plánované |
| **Konektor Spotify / Deezer** | Importovanie playlistov a zhoda skladieb | ⚪ Plánované |
| **Inteligentná deduplikácia** | Detekcia duplicitných záznamov (rozmazaný názov/umeník + akustické fingerprighty) | ⚪ Plánované |

> 💡 *Ak chcete zistiť podrobnosti plánovaných milníkov a verzií, pozrite sa na [Mapu cesty (Roadmap)](../../ROADMAP.md).*

---

## 📌 Dostupné jazyky

Anglický, Francúzsky, Španielsky, Nemecký, Taliansky, Portugalský, Japonský, Ruský, Poľský, Turecký, Nemecký, Švédsky, Indonésky, Bulgarský, Srbský, Bieloruský, Grécky, Katalánsky, Baskický, Galický, Česky, Slovenský, Maďarský, Chorvatský, Slovinský, Bosnský, Estónsky, Latinský, Litovský, Nórvejský, Dánsky, Fínsky, Íslenský, Malajský, Tagalogský, Swahilský, Esperantský, Китайčina (zjednodušená), Китайčina (tradičná), Korejský, Arabsky, Hebraický, Vietnamský

---

## 🚀 Rýchly štart

### Predpoklady

- **Python 3.11** alebo vyšší nainštalovaný
- Git

### Inštalácia

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

## 🧪 Spustenie testov

Projekt používa `pytest` s sadou jednotkových a integračných testov:

```bash
pytest -v
```

Testy sa spúšťajú automaticky na **Windows, macOS a Ubuntu** pri každom pushu cez GitHub Actions.

---

## 🔒 Bezpečnosť & API kľúče

- **Nikdy ne commitujte skutočné kľúče API ani tokeny autentifikácie.**
- Súbor `.gitignore` je predkonfigurovaný na blokovanie `.env`, `credentials.json`, `token.json` a všetkých lokálnych databáz SQLite.
- Použite `.env.example` ako šablónu pre vaše vývojové prostredie.

---

## 📋 Dokumentácia & Monitorovanie projektu

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Podrobný záznam verzií, nových funkcií a opravných balíkov chyby.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Mapa cieleňovania budúceho kroku (Umelci, Cloud, Spotify, De-duplikácia).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Karta softvérového architektúry a pravidlá kvality kódu.

---

## 💖 Podpora projektu & Distribúcia

AMSO je bezplatný a voľný softvéar (open source). Ak sa vám páči aplikácia a chcete podporiť jej rozvoj:

- 🎮 **Stiahnutie & Zaplaťte, čo chcete :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (predkompilovaný spustiteľný súbor pripravený na použitie)
- ☕ **Priemyselné darovanie :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Spatrovníci :** [Sponsoriser LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licencia

Tento projekt je pod licenciou **GNU General Public License v3.0 (GPL-3.0)** — pozrite si súbor [LICENSE](../../LICENSE) pre viac detailov.
