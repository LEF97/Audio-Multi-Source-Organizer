# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <b>Íslenska</b> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) er nútímaleg, áhrifamikkur og fleiriplattsviðs hljóðspilara fyrir skrefja (Windows, Linux, macOS). Það er hönnuð til að veita áhlutinn hljóðhöfundum fullkominn stjórn á staðbundnu tónlistabibliókani þeirra (MP3, FLAC, OGG…), og það stuðlar nú að spilalistum (M3U, PLS, XSPF, WPL), CUE-blöðum (albúma í efninu eina skráar, skipt í stefnurnar) og innihalda nýlega blinda prófunarhagker (blind test audio)! Verkefnið er að þróast til að verða sameina stjórnborð sem getur skipulagað, fjarlægt sýnilega og synkrast tónlistakolleksiur sem eru greyttar milli staðbundra skrána, skýrskráningar (Google Drive) og straumþjónustu (Spotify, Deezer, Amazon Music).

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

## 📌 Eigishæktir & Staða þróunarverkefnis

| Eigishætti | Greining | Staða |
| :--- | :---: | :---: |
| **Inntækka VLC spilkerfi** | Ljósvægt og sjálfstætt áðurhöfnarspilkerfi með sjálfvirknun VLC og slétt stjórnun á hljóðnívi | 🟢 Implémenté |
| **Flanna-þráðar stafrænn skannar** | Endrætt og hraðrar uppgötvun stafræna hljóðskrára stafrænt (MP3, FLAC, AAC, OGG...) | 🟢 Implémenté |
| **Úrvinning stafrænnra gögnanna** | Lesing/skrifun ID3, Vorbis Comments og reikning stafrænnar vingarnar (`mutagen`) | 🟢 Implémenté |
| **Stuðningur Playlista (M3U, PLS, XSPF, WPL) og CUE-blöð** | Tré-índeksing (🎶), muntræð lífhöfnun, sýnileg greining á þrautum sem eru fjölaðir; `.cue` skráir (💿) opnast eins og stafrænt skráarhóll með varanlega tíma og spila eins og raunverulegar þrautir | 🟢 Implémenté |
| **Playlist Stjórnandi og Trekka-og-Droppa** | Sjálfvirk lífhöfnun, slétt trekkja-og-droppa, endurskoðuleg tilfeldig (shuffle) og hringrásir | 🟢 Implémenté |
| **Interaktív „🎲 Blind Test“ aðgerð** | Innslitleg tónlistaleikur með lífænni afturtelningu, hljóðlegum blöndun, mjúk uppgötvun og sjálfvirnu samræmi | 🟢 Implémenté |
| **In-app uppdateringar** | Sjálfvirk/handvirkra útgáfuströkkingar með GitHub Releases | 🟢 Framkvæmt |
| **Stjórnun listamanna og diskógrafía** | Sérstaka sýn fyrir listamanna með albúmum, singlum og fullkominnri diskógrafíu | 🟡 Áætlað |
| **Grafískur yfirberærsleiki (EQ)** | Ljóðhöfundarinnstillingar ályddu og parametrískur yfirberærsleiki | 🟡 Áætlað |
| **Google Drive tenging** | Skannun og synkrastilling á fjarlægum ályddu safninu með OAuth 2.0 | ⚪ Áætlað |
| **Amazon Music tenging** | Skannun og synkrastilling á fjarlægum ályddu safninu með OAuth 2.0 | ⚪ Áætlað |
| **Spotify / Deezer tenging** | Skráning spillistanna og samræmi stafræða | ⚪ Áætlað |
| **Snjallraflun** | Greining á sýnilegum stafræðum (titill/listamann + hljóðmyndir) | ⚪ Áætlað |

> 💡 *Til að skoða detaljar um áhrifastig og áætlaðar útgáfur, vinsamlegast persónuðu þér á [Ferðalög (Roadmap)](../../ROADMAP.md).*

---

## 📌 Til staipað tungumörk

English, French, Spanish, German, Italian, Portuguese, Japanese, Russian, Polish, Turkish, Dutch, Swedish, Indonesian, Bulgarian, Serbian, Belarusian, Greek, Catalan, Basque, Galician, Czech, Slovak, Hungarian, Croatian, Slovenian, Bosnian, Estonian, Latvian, Lithuanian, Norwegian, Danish, Finnish, Icelandic, Malay, Tagalog, Swahili, Esperanto, Simplified Chinese, Traditional Chinese, Korean, Arabic, Hebrew, Vietnamese

---

## 🚀 Hraðbyrjun

### Upplýsingar sem eru nauðsynlegar

- **Python 3.11** eða nýrri útgáfu
- Git

### Rauðferð

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

## 🧪 Prófunarupphaf

Projektið notar `pytest` með samsetningu einingatestum og samþættutestum:

```bash
pytest -v
```

Prófunirnir keyrja sér svættlega á **Windows, macOS et Ubuntu** við hverja push með GitHub Actions.

---

## 🔒 Öryggi & API lykilorð

- **Ekki komítið aldrei raunverulegar API-hlutgreinar eða staðfestatokana.**
- Skráin `.gitignore` er fyrirhugað til að blokkra `.env`, `credentials.json`, `token.json` og öll stafrætur SQLite á staðnum.
- Notaðu `.env.example` sem blæxa fyrir þróunarmiljón þitt.

---

## 📋 Skjalasafn & Projektafylgni

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Nákvæmt skráning af útgáfum, nýraraxtur og lagabætur.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Stigskrá fyrir framtíðarmarkmiðum (Listarlegar, Ský, Spotify, Skilgreining).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Skýrsluskrá um hugbúnaðararkitektúr og reglur um kóðagæði.

---

## 💖 Stuðningur fyrir verkefnið & Starfsnauðveldi

AMSO er loftið og óvaðveitt hugbúnaður (open source). Ef þú þykir forritinu vel og vilt stuðningsköllu þróun þess:

- 🎮 **Hlaða niður & Greiða það sem þú vilt :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (uppbyggt framkvæmdarþætti sem er tilbúinn til notkunar)
- ☕ **Grafa beint :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Stafræðingar :** [Stafræðingar LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Lýsmi

Þetta verk er undir leyfi **GNU General Public License v3.0 (GPL-3.0)** — skoðaðu skjalinu [LICENSE](../../LICENSE) fyrir frekari upplýsingar.
