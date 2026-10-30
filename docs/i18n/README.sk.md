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

## 📌 Funkcie & Stav projektu

| Funkcia | Popis | Status |
| :--- | :---: | :---: |
| **Audio prehrávacie meno** | Ľahké a samostatné audio prehrávače (VLC portable automaticky nainštalovaný na Windows). Dve voľné motory: priamy výstup VLC alebo nepretržitý búforový motor pre plynulý prechod medzi dvoma skladbami (Gapless 0 ms, prechod s rovnakou hlasitosťou, bez prerušenia audio výstupu) | 🟢 Implementované |
| **Správa knižnice** | Multithreadový rekurzívny sken lokálnych priečastí (MP3, FLAC, AAC, OGG...), manuálna, plánovaná alebo v reálnom čase synchronizácia, koš a štatistiky knižnice | 🟢 Implementované |
| **Extrakcia metadát** | Čítanie/zápis ID3, Vorbis Comments a výpočet audio fingerprintu (`mutagen`) | 🟢 Implementované |
| **Podpora playlistov (M3U, PLS, XSPF, WPL) a CUE listov** | Strukturované indexovanie (🎶), sekvenčný poradie počúvania, vizuálna lokalizácia chýbajúceho obsahu; súbory `.cue` (💿) sa otvoria ako virtuálna priečka so skladbami s ich trvaním a prehrávajú sa ako skutočné skladby | 🟢 Implementované |
| **Správca playlistov a Preťahovanie-Odlepovanie** | Virtualizovaná výčka, plynulé drag & drop, zvratené náhodné (shuffle) a slučky | 🟢 Implementované |
| **Interaktívny režim „🎲 Blind Test“** | Imerzitívna hudobná hra s animovaným odpočítavaniím, zvukovým prechodom, jemným odhalením a automatickým prechodom | 🟢 Implementované |
| **Aktualizácie v aplikácii** | Automatická/ručná kontrola verzií cez GitHub Releases | 🟢 Implémenté |
| **Verzie pre Linux a macOS** | Balíčky .AppImage / .tar.gz (Linux) a nepodpísaný .dmg (macOS), vyžaduje sa VLC | 🟡 Experimentálne (neteštené) |
| **Správa umelníkov a diskografie** | Dedikovaná prehliadka podľa umelníka s albumami, singlmi a kompletnou diskografiou | 🟡 Plánované |
| **Grafický ekvalizér (EQ)** | Audio prednastavenia a paramatrický multibándový ekvalizér | 🟡 Plánované |
| **Pripojka Google Drive** | Skenerovanie a synchronizácia vzdialených audio kolekcií cez OAuth 2.0 | ⚪ Plánované |
| **Pripojka Amazon Music** | Skenerovanie a synchronizácia vzdialených kolekcií cez OAuth 2.0 | ⚪ Plánované |
| **Pripojka Spotify / Deezer** | Importovanie playlistov a zodpovednosť skladieb | ⚪ Plánované |
| **Inteligentné odstraňovanie duplicitných záznamov** | Detekcia duplicitných záznamov (rozmazané názvy/umelníkov + akustické fingerprnty) | ⚪ Plánované |

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

## 🐧🍎 Linux a macOS : experimentálne verzie (netestované)

Linux balíčky (`.AppImage` / `.tar.gz`) a macOS (`.dmg`) sú poskytované **bez testovania**: AMSO bolo validované iba pod Windows. Audio motor s nepretržitým búforom (`buffer`) konkrétne nebol overený na týchto systémoch. Vaša spätná väzba je cenná.

- **VLC je potrebný** (AMSO ho stiaží iba pod Windows) :
  - Linux: `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) alebo `sudo pacman -S vlc` (Arch).
  - macOS: nainštalovať **VLC.app** z [videolan.org](https://www.videolan.org/vlc/) do adresára Applications.
- **Linux, systémové biblioteky** : rozhranie Qt vyžaduje napríklad `libpulse0` (zvuk), `libxcb-cursor0` a `libxkbcommon-x11-0` (napríklad `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, neoznačený `.dmg`** : pri prvom spustení, kliknite pravým tlačidlom na AMSO a potom **Otvoriť**, alebo vykonajte `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage** : urobiť ho spustiteľným pomocou `chmod +x AMSO*.AppImage`.
- **V prípade problémov**, prosím o zaslanie súborov `startup.log` a `crash.log` (ak existujú) umiestnených v adresári dát: `~/Library/Application Support/AMSO/` pod macOS, `~/.local/share/AMSO/` pod Linuxom. Uveďte svoj systém a verziu VLC.

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
