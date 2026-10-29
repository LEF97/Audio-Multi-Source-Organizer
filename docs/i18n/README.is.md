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

## 📌 Eigishæktir & Staða þróunarverkefnis

| Hæggi | Greining | Staða |
| :--- | :---: | :---: |
| **Láttraudiohraðlætinn** | Léttur og sjálfstæður áudiohraðlætinn (VLC portable hlekkast í Windows). Tveir raunveruleikar til val: bein VLC útvísun, eða staðbundinn hraðlætinn fyrir slök flæði milli tónlistastakka (Gapless 0 ms, jafnsterk flæðandi innlæsing, án áhrif á áudioútganginn) | 🟢 Implémenté |
| **Stjórnun bókasafns** | Multithreadað endurskannun staðbundinna skjalasafna (MP3, FLAC, AAC, OGG...), handvirk, skipulagð eða í réaltíma samræming, skráning og bókasafnsstaðlistanir | 🟢 Implémenté |
| **Úrvinning staðlistana** | Lesa/skrifa ID3, Vorbis Comments og reikna áudio-blóðmerki (`mutagen`) | 🟢 Implémenté |
| **Stuðningur Playlists (M3U, PLS, XSPF, WPL) og CUE blækhljóð** | Tré-índeksing (🎶), viðræðisriðan áheykkun, skoðulegt greining á þörnum stakka; `.cue` skjalefni (💿) opnast eins og skjalasafn virkilegra stakka með varan og lesast eins og raunverulegar staklar | 🟢 Implémenté |
| **Playlist Stjórnkerfi og Drag & Drop** | Virkilega flæði, slök drag & drop, svofræði (shuffle) endurskráning og hringrásir | 🟢 Implémenté |
| **Interaktív „🎲 Blind Test“ aðgerð** | Ímyndalegi tónlistaleikur með líflegri reikningu, hljóðflæði, mjúk uppgötvun og sjálfvirku flæði | 🟢 Implémenté |
| **Uppfæringar innan appinnarinnar** | Automata/handvirkra útgáfustrullunar með GitHub Releases | 🟢 Implémentéð |
| **Linux og macOS útgáfur** | `.AppImage` / `.tar.gz` pakkar (Linux) og óskrifað `.dmg` (macOS), VLC krafist | 🟡 Tilraunarafkókur (ekki prufað) |
| **Stjörtastjórn og diskrófa** | Skipt staða fyrir stjörnu með blaðmyndum, singlum og fullkominnri diskrófu | 🟡 Áætlað |
| **Grafískur yfirberærsleiki (EQ)** |Ljóðhöfundarinnstillingar og raunverulegs yfirberærsleiki (parametric multi-band equalizer) | 🟡 Áætlað |
| **Google Drive tenging** | Skannun og synkróhanna fjarlægra ályddbyrjunar með OAuth 2.0 | ⚪ Áætlað |
| **Amazon Music tenging** | Skannun og synkróhanna fjarlægra ályddbyrjunar með OAuth 2.0 | ⚪ Áætlað |
| **Spotify / Deezer tenging** | Skráning spillistanna og samræmi stakkanna | ⚪ Áætlað |
| **Snjallt fjallaverð** | Uppgötva raföld (títol/stjarna flous + hljóðmyndir) | ⚪ Áætlað |

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

## 🐧🍎 Linux og macOS: prófunarúrgafa (ekki staðfestar)

Linux-þæknir (`.AppImage` / `.tar.gz`) og macOS (`.dmg`) eru veittir **án að hafa verið prófaðir** : AMSO hefur verið staðfest aðeins á Windows. Sérstaklega staðferð á hljóðkerfi með stöðugum búnað (`buffer`) hefur ekki verið staðfest á þessum kerfum. Tilvísun þín er mikilvæg.

- **VLC er nauðsynlegt** (AMSO aflaður aðeins á Windows) :
  - Linux : `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) eða `sudo pacman -S vlc` (Arch).
  - macOS : hlekkstu **VLC.app** frá [videolan.org](https://www.videolan.org/vlc/) í Applications skrá.
- **Linux, kerfisbókaflokkar** : Qt-grenifflokkur krefjast sérstaklega `libpulse0` (ljóð), `libxcb-cursor0` og `libxkbcommon-x11-0` (t.d. `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, óskrifað `.dmg`** : við fyrstu upphafi, svíka án þekktra á AMSO og síðan **Opna**, eða keyra `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage** : gerð það framkvæmt með `chmod +x AMSO*.AppImage`.
- **Í falnum**, vinsamlegast sendu skráarnir `startup.log` og `crash.log` (ef þau eru til) sem eru í gögufilmokkurinn: `~/Library/Application Support/AMSO/` á macOS, `~/.local/share/AMSO/` á Linux. Greina kerfi þitt og útgáfuna VLC.

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
