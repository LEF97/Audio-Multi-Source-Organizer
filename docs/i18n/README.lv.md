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

## 📌 Funkcionalitātes & Stāvoklis projekta

| Funkcionalitāte | Apraksts | Stāvoklis |
| :--- | :--- | :---: |
| **Audio atspēdes motors** | 가벼vs un autonoms audio atspēdes spēklais (VLC portable automātiski instalēts Windows lietotājiem). Divi motorsu izvēles: tieša VLC izgāde vai turpmaka bumba motors glāsi pārejai divās dziesmās (Gapless 0 ms, vienā vērienā spēcīgā fade, bez audio izgādes pārtraukumu) | 🟢 Implementēts |
| **Bibliotēkas vadība** | Rekurzīvs multithreaded skenēšana no vietējiem karordiņiem (MP3, FLAC, AAC, OGG...), manuāla, plāno vai real-time senkronizācija, papērba un bibliotēkas statistika | 🟢 Implementēts |
| **Metadatu ekstrakcija** | ID3, Vorbis Comments lasīšana/rakstīšana un audio atspoguļojuma (fingerprint) aprēķināšana (`mutagen`) | 🟢 Implementēts |
| **Atbalsts playlistām (M3U, PLS, XSPF, WPL) un CUE lapām** | Izakrojums (🎶), sekvenciāls klausīšanās pasākums, vizuāla atzīšana trūkstošajās dziesmās; `.cue` faili (💿) atver kā virtuālu dziesmu karordiņu ar to trūkumu un atspēlo kā patiešas dziesmas | 🟢 Implementēts |
| **Playlist vadītājs un Drag & Drop** | Virtualizēta gaida, glāds drag & drop, reversīvs izrīkojums (shuffle) un cikli | 🟢 Implementēts |
| **Interaktīvs « 🎲 Blind Test » režīms** | Imazīgs mūzikas spēles spēle ar animētu skaitītāju, skaņas fade, maigu atklāšanu un automātisku pāreju | 🟢 Implementēts |
| **In-app atjauninājumi** | Otomātiska/manuālā versiju pārbaude caur GitHub Releases | 🟢 Implementēts |
| **Linux & macOS versijas** | Pirksti .AppImage / .tar.gz (Linux) un neparakstīts .dmg (macOS), nepieciešams VLC | 🟡 Eksperimentāls (neierobešots) |
| **Iznaudotāju & Diskografijas pārvaldība** | Idedinata skatīšanās pēc iznaudotājiem ar albumiem, singliem un pilnu diskografiju | 🟡 Plānotas |
| **Grafisks ekvalizators (EQ)** | Audio iestatījumi un parametrisisks multi-bandu ekvalizators | 🟡 Plānotas |
| **Google Drive konektors** | Skeneris un senkronizācija attālām audio kolekcijām caur OAuth 2.0 | ⚪ Plānotas |
| **Amazon Music konektors** | Skeneris un senkronizācija attālām kolekcijām caur OAuth 2.0 | ⚪ Plānotas |
| **Spotify / Deezer konektors** | Reproduktorietuveju importēšana un dziesmu atbalstība | ⚪ Plānotas |
| **Gudrs dubultu dzēšana** | Dubultu atklāšana (tituls/iznaudotājs + akustiskie atspoguļojumi) | ⚪ Plānotas |

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

## 🐧🍎 Linux un macOS: eksperimentālie versijas (neierobežotas)

Linux paketi (`.AppImage` / `.tar.gz`) un macOS (`.dmg`) tiek nodoti **bez testēšanas**: AMSO ir validizēts tikai Windows lietotā. Akustiskais motors ar turpinającego tamponu (`buffer`) īpaši nav pārbaudīts šajos sistēmās. Jūsu atgriezenums ir vērtīgs.

- **VLC ir nepieciešams** (AMSO nedlejalo tikai Windows lietotā.​):
  - Linux: `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) vai `sudo pacman -S vlc` (Arch).
  - macOS: instalējiet **VLC.app** no [videolan.org](https://www.videolan.org/vlc/) "Applications" kataloga.
- **Linux, sistēmas bibliotēkas**: Qt interfeiss prasa, piemēram, `libpulse0` (audio), `libxcb-cursor0` un `libxkbcommon-x11-0` (piemēram, `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, nav parakstīts .dmg**: pirmo startu veikt, noklikšķiniet labā (right click) uz AMSO un izvēli **Ouvrir**, vai izpildiet komandu `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage**: padarīt to izpildījamu ar `chmod +x AMSO*.AppImage`.
- **Ja ir problēma**, lūdzu, nosūtiet failus `startup.log` un `crash.log` (ja tie nav) datu kataloggā: `~/Library/Application Support/AMSO/` macOS lietotā, `~/.local/share/AMSO/` Linux lietotā. Norādiet savu operētājsistēmu un VLC versiju.

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
