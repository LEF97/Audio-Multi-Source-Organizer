# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <b>Eesti</b> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) on moodesan, reaktiivne ja mitmekaitse tööpäevade audiolugija (Windows, Linux, macOS). Disainitud, et pakkuda audiophilele täieliku kontrolli oma kohalikuga muusikaarhivi (MP3, FLAC, OGG…) üle, toetab see nüüd pillelistaid (M3U, PLS, XSPF, WPL), CUE-lehti (albumid ühes failis, lõigatud loeteltesse) ja sisaldab täiesti uue audioliste testi režiimi! Projekt areneb ühised juhtimiskeskuseks, mis on võimeline organiseerima, dublikaatide eemaldama ja pikaajalised muusikaarhivid, mis on jagatud kohalike diskude, pilvsalvestuse (Google Drive) ja straaminguteenuste (Spotify, Deezer, Amazon Music) vahel.

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

## 📌 Funktsioonid & Staatus projektist

| Funktsioon | Kirjeldus | Staatus |
| :--- | :---: | :---: |
| **Audio toitummootor** | Kevetas ja iseseisv audio toitur (VLC portable automaatselt installitud Windowsi all). Kahe toitummootori valik: otsene VLC väljund, või kontinuaalne tellitud mootor kahte loetlist vahel sujuva üleminekuga (Gapless 0 ms, võrdsed vahemikuga fade, ilma audio väljundikohast katkestuse). | 🟢 Implementeeritud |
| **Biblioteevi haldamine** | Rekursiivne multithreadi skaneerimine kohalikest kaustadest (MP3, FLAC, AAC, OGG...), käsitsi, ajastatud või rajaline sünkroonimine, korvi ja biblioteekistatud statistika | 🟢 Implementeeritud |
| **Metadata ekstraheerimine** | ID3, Vorbis Comments lugemine/kirjutamine ja audio žärgimuse arvutamine (`mutagen`) | 🟢 Implementeeritud |
| **Tugitus Playlistidele (M3U, PLS, XSPF, WPL) & CUE-lehtletile** | Arvoomstruktuuriline indekseerimine (🎶), loetlemine järjepikut, puuduvate numbrite visuaalne tuvastamine; `.cue` failid (💿) avanevad nagu virtuaalne numbrite kausta oma kestusega ja toituvad nagu tõelised numbrid | 🟢 Implementeeritud |
| **Playlista haldaja & Vedamine-asetamine** | Virtuaalne ootamisosa, sujuv vedamine-asetamine, vastutav (shuffle) ja tsüklid | 🟢 Implementeeritud |
| **Interaktiivne „🎲 Blind Test“ režiim** | Immersiivne muusikaline mäng animatiivse arvutusega, kõlajärgemusega, pehme avaldamisega ja automaatse tellitumega | 🟢 Implementeeritud |
| **Kasutaja-liidese uuendused** | Versioonide automaatne/manuaalne kontroll GitHub Releases kaudu | 🟢 Implementeeritud |
| **Linuxi ja macOS versioonid** | Paquets .AppImage / .tar.gz (Linux) ja .dmg mitte-allkirjastatud (macOS), VLC vajalik | 🟡 Eksperimentaals (testitud pole) |
| **Kunstnikute ja diskograafia haldamine** | Kunstnikile pühendatud vaade albumite, singlite ja täieliku diskograafiaga | 🟡 Planeeritud |
| **Graafiline ekvailaator (EQ)** | Audio eelregiistrid ja parametriline hulkbåndse ekvailaator | 🟡 Planeeritud |
| **Google Drive ühendus** | Kaug audio kogumiste skaneerimine ja sünkroonimine OAuth 2.0 kaudu | ⚪ Planeeritud |
| **Amazon Music ühendus** | Kaug kogumiste skaneerimine ja sünkroonimine OAuth 2.0 kaudu | ⚪ Planeeritud |
| **Spotify / Deezer ühendus** | Playlista impordimine ja loogade vastavus | ⚪ Planeeritud |
| **Nutekorduvuse vältimine** | Duplikaatide tuvastamine (peen/kunstnik + akustilised jäljed) | ⚪ Planeeritud |

> 💡 *Et vaadata planeeritud etappide ja versioonide üksikasju, viitugege [Teekart (Roadmap)](../../ROADMAP.md).*

---

## 📌 Saadaval olevad keeled

Inglise, Prantsuse, Hispaania, Saabis, Itaalia, Portugali, Jaapani, Vene, Poola, Türgi, Neiderlandi, Rootsi, Indoneesia, Bulgaaria, Servia, Belaruse, Griik, Katalaan, Baskimaa, Galitsia, Tsjehi, Sloveenia, Ungari, Kroatsia, Slovenia, Bosnia, Eesti, Latvija, Liivland, Norvegi, Taani, Rootsi, Islandia, Maleesia, Tagalog, Swahili, Esperanto, Hiineski (lõikestatud), Hiineski (traditsiooniline), Korea, Arabi, Hebra, Vietnam

---

## 🚀 Kiire käivitamine

### Eelmised tingimused

- **Python 3.11** või kõrgem installitud
- Git

### Asennus

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

## 🐧🍎 Linux ja macOS: eksperimentaalsed versioonid (testimataoled)

Linux pakettid (`.AppImage` / `.tar.gz`) ja macOS (`.dmg`) on saadavad **testitamata**: AMSO on valideeritud ainult Windowsi all. Kontinuumse puffer audio mootor (`buffer`) pole eriti kontrollitud need süsteemid. Teie tagasiside on väärtuslik.

- **VLC on vajalik** (AMSO seda ei laadi vaid Windowsi jaoks) :
  - Linux : `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) või `sudo pacman -S vlc` (Arch).
  - macOS : installige **VLC.app** [videolan.org](https://www.videolan.org/vlc/) Applications kausta alt.
- **Linux, süsteembibliotekid** : Qt liides nõuab näiteks `libpulse0` (heli), `libxcb-cursor0` ja `libxkbcommon-x11-0` (näiteks `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, ebaallkirjastatud \`.dmg\`** : esimesel käivitamisel klõpsake AMSO päriba paremal pool ja vajutage **Ava**, või käivitage `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage** : tehakse see käivitatavaks `chmod +x AMSO*.AppImage`.
- **Probleemi korral**, palun saata failid `startup.log` ja `crash.log` (kui olemas), asukoohast andmed: `~/Library/Application Support/AMSO/` macOS-i all, `~/.local/share/AMSO/` Linuxi all. Palun täpsustada oma süsteem ja VLC versioon.

---

## 🧪 Testide käivitus

Projekt kasutab `pytest` ühik- ja integreerimistestide kogumikuga:

```bash
pytest -v
```

Testid käivad automaatselt **Windows, macOS ja Ubuntu** peaaegu iga pushi käigus via GitHub Actions.

---

## 🔒 Ohutus & API võtmed

- **Ärge koodistage kunagi reaalne API-võtme ega autentifitseerimistokenit.**
- Fail `.gitignore` on eelkonfigureeritud blokeerima `.env`, `credentials.json`, `token.json` ja kõik kohalikud SQLite andmebaasid.
- Kasutage `.env.example` kui malli oma arenduskeskkonnale.

---

## 📋 Dokumentatsioon ja projekti jälgimine

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Detailne loovuskatalog versioonidest, uutest funktsioonidest ja vigaomavendustest.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Reeglinähtus tulevaste etappide kohta (Artistid, Cloud, Spotify, Duplikaatide eemaldamine).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Tulemere arhitektuurivõige ja koodi kvaliteetireeglid.

---

## 💖 Projekti toetamine & Distributsioon

AMSO on vaba ja tasuta tarkvara (open source). Kui te hindate rakendust ja soovite selle arengut toetada:

- 🎮 **Laadimine & Maksa, mis sa tahad :** [AMSO's Itch.io leht](https://lef97.itch.io/audio-multi-source-organizer) (valmis kasutamiseks eelkompileeritud täituv)
- ☕ **Direktlahendus:** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsorid :** [Sponsorida LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Litsents

See projekt on litsentsi põhjal **GNU General Public License v3.0 (GPL-3.0)** — vaadake faili [LICENSE](../../LICENSE) rohkem üksikasju saamiseks.
