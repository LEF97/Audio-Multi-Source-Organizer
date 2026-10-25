# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <b>Latviešu</b> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) ir moderns, reakcijas un multiplatformu galda audio spēlētājs (Windows, Linux, macOS). Izveidots, lai sniegt audiofili pilnīgu kontroli par viņu vietējo mūzikas bibliotēku (MP3, FLAC, OGG…), tas tagad atbalsta spēles sarakstes (M3U, PLS, XSPF, WPL), CUE lapas (albumi vienā failā, kas sadalīti par trajektorām) un integrē pilnīgi jaunu audio "blind test" režīmu! Projekts attīstās, lai kļūtu par vienotu komandaprojektu, kas spēj organizēt, nodublēt un sinhronizēt hibrīdas mūzikas kolekcijas, kas sadalītas starp vietējajiem diskām, mākoņmemu saglabāšanu (Google Drive) un strīma pakalpojumiem (Spotify, Deezer, Amazon Music).

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

## 📌 Funkcionalitātes & Stāvoklis projekta

| Funkcija | Apraksts | Stāvoklis |
| :--- | :--- | :---: |
| **Integrēts VLC atspēlēšanas motors** | 가벼vs unautonomisks audio atspēlētājs ar VLC portatīva automātiskā instalāciju un glāsu volumkontroli | 🟢 Implementēts |
| **Multithredisks vietējais skeneris** | Rekurzīva un ātra vietējo audio failu atklāšana (MP3, FLAC, AAC, OGG...) | 🟢 Implementēts |
| **Metadatu ekstrakcija** | ID3, Vorbis Comments lasīšana/rakstīšana un audio atspoguļojuma (mutagen) aprēķināšana | 🟢 Implementēts |
| **Atbalsts për spēklı (M3U, PLS, XSPF, WPL) un CUE lapas** | Izakstīšana (🎶), sekvenciāls klausīšanās pasākums, vizuāla atzīšana trūkstošo dziesmu; `.cue` faili (💿) atver kā virtuālu dziesmu sarakstu ar to trūkumu un atspēlē kā patiešas dziesmas | 🟢 Implementēts |
| **Spēklı vadītājs un Drag-Drop** | Virtualizēta gaidašana, glāss Drag & Drop, reversīva izrādīšana (shuffle) un cikli | 🟢 Implementēts |
| **Interaktīvs "🎲 Blind Test" režīms** | Izdīcināta mūzikas spēle ar animētu skaitītāju, audio fade, maigu atklāšanu un automātisku pārliecību | 🟢 Implementēts |
| **Atjauninājumi lietotnē** | Otomātiska/Manuālā versiju pārbaude via GitHub Releases | 🟢 Implementēts |
| **Izgatavošana un diskogrāfija** | Ieceltā skatīšanās pēc izskata ar albumiem, singliem un pilnu diskogrāfiju | 🟡 Plānotas |
| **Grafisks ekvalizators (EQ)** | Audio iestatījumi un parametrisisks multi-bandu ekvalizators | 🟡 Plānotas |
| **Google Drive konektors** | Skeneris un sinhkronizācija attālām audio kolekcijām via OAuth 2.0 | ⚪ Plānotas |
| **Amazon Music konektors** | Skeneris un sinhkronizācija attālām kolekcijām via OAuth 2.0 | ⚪ Plānotas |
| **Spotify / Deezer konektors** | Playlista importēšana un trajektoru atbilstība | ⚪ Plānotas |
| **Gudrs dubultu noņemšana** | Dubultu detekcija (vārds/izskats + akustiskie atspoguļojumi) | ⚪ Plānotas |

> 💡 *Lai uzzinātu plānotas milestones un versijas detalizāciju, atsaucieties uz [Ceļveikls (Roadmap)](../../ROADMAP.md).*

---

## 📌 Pieejamās valodas

Angļu, Francūsis, Spāņu, Vācu, Itāļu, Portugāļu, Japāņu, Krievu, Poloniski, Turku, Niederlandu, Švediski, Indonēziski, Bulģiski, Serbiskie, Bielorussiski, Grieķiski, Katalāņu, Baskiski, Galīsciski, Čehiski, Slovākiski, Ungāriski, Kroātiski, Slovēniski, Bosniski, Estoniski, Latviešu, Lietuvišu, Nordiešu, Dāniski, Fīnīšu, Islandiski, Malajiski, Tagaligu, Swahili, Esperanto, Ķīniski (vienkāršs), Ķīniski (tradicionālais), Korejiski, Arabiski, Ivrišu, Vietnami

---

## 🚀 Ātrā startēšana

### Priekšrequisāti

- **Python 3.11** vai augstāks instalēts
- Git

### Instalācija

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

## 🧪 Testu startēšana

Projekts izmanto `pytest` ar vienības un integrācijas testu sēklojumu:

```bash
pytest -v
```

Testi tiek izturēti automātiski uz **Windows, macOS un Ubuntu** katrā pushā ar GitHub Actions.

---

## 🔒 Drošība & API atslēgas

- **Nekad neielkopojiet patiesus API atslolas vai autentifikācijas tokenus.**
- Failu `.gitignore` ir konfigūrēts, lai bloķētu `.env`, `credentials.json`, `token.json` un visus vietējie SQLite datubāzes.
- Izmantojiet `.env.example` kā šablonu savai attīstības videi.

---

## 📋 Dokumentācija & Projekta uzraudzība

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Detalizēts vēsturīciņš par versijām, jauniem funkcionalitātei un kļūdu labojumiem.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Plāns par nākotnes milniektos (Artisti, Cloud, Spotify, Dublikātu noņemšana).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Programmatūras arhitektūras statūts un koda kvalitātes noteikumi.

---

## 💖 Atbalstīt projektu & Distribucija

AMSO ir bezmaksas un atvērta kods programmatūra (open source). Ja jums patīk lietotne un vēlaties atbalstīt tās attīstību:

- 🎮 **Ilejotāšana & Makšķerot, cik vēlies :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (pārinstalējs, kas ir priekšaprasējis un gatavs lietošanai)
- ☕ **Darīt tiešu dāvanu :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Patrunīji :** [Sponsoriser LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licenču

Šis projekts ir zem licenču **GNU General Public License v3.0 (GPL-3.0)** — skatiet failu [LICENSE](../../LICENSE) par vairāk informāciju.
