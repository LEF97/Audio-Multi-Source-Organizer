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

| Funktsionaalus | Kirjeldus | Staatus |
| :--- | :---: | :---: |
| **Integreeritud VLC toitumemmootor** | Kevelik ja iseseisv, VLC portable automaatne installatsioon ja sümme volumikohutus audiolugija | 🟢 Implementeeritud |
| **Multithreadne kohalik skanner** | Rekursiivne ja kiire avastamine kohalikest audiolugikutest (MP3, FLAC, AAC, OGG...) | 🟢 Implementeeritud |
| **Metaandmete ekstraheerimine** | ID3, Vorbis Comments lugemine/kirjutamine ja audiolajuga sünkpunkti arvutamine (`mutagen`) | 🟢 Implementeeritud |
| **Playlista tugi (M3U, PLS, XSPF, WPL) ja CUE-lehted** | Puuvärvi indekseerimine (🎶), sekventsiaalne kuulamise järgmine, kadunud lõikede visuaalne tuvastamine; `.cue` failid (💿) avanevad nagu virtuaalne lõikede kausta oma kestusega ja toituvad nagu tõelised lõiked | 🟢 Implementeeritud |
| **Playlista haldaja ja vedaja-asetus** | Virtuaalne ootamisrijad, sümme vedaja-asetus, vastutav (shuffle) ja tsüklid | 🟢 Implementeeritud |
| **Interaktiivne „🎲 Blind Test“ režiim** | Immersiivne muusika mäng animatiivse laskuriga, helivähemusega, pehme paljastusega ja automaatse järgnevusega | 🟢 Implementeeritud |
| **Uuendused kasutusliidesel** | Automaatiline/manuaalne versioonide kontrollimine GitHub Releases kaudu | 🟢 Reaal |
| **Artiste ja diskograafia haldamine** | Arsti dedikeeritud vaade albumite, singlite ja täieliku diskograafiaga | 🟡 Planeeritud |
| **Graafiline ekvailaator (EQ)** | Audio eelregi ja parametriline hulkva ekvailaator | 🟡 Planeeritud |
| **Google Drive ühendaja** | Kaugaudio kogumiste skaneerimine ja sünkroonimine OAuth 2.0 kaudu | ⚪ Planeeritud |
| **Amazon Music ühendaja** | Kaugkogumiste skaneerimine ja sünkroonimine OAuth 2.0 kaudu | ⚪ Planeeritud |
| **Spotify / Deezer ühendaja** | Playlista impordimine ja loetelu eşitmine | ⚪ Planeeritud |
| **Nutekorduvus vähendamine** | Duplikaatide tuvastamine (bluus/kunst + akustilised žirgud) | ⚪ Planeeritud |

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
