# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <b>Esperanto</b> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) estas moderna, reaktiva, kaj multiplataforma skribanga audiolektoro (Windows, Linux, macOS). Kreita por doni audiofiloj totalan kontrolon super ilia lokala muzika biblioteko (MP3, FLAC, OGG…), ĝi nun subtenas plejlistojn (M3U, PLS, XSPF, WPL), CUE-foliadilojn (albumoj de unu fiksta paĝo dividitaj en trakoj) kaj inkluzivas novan modon de audio-blind-test ! La projekto evoluas por fari unuigitan kontrolcentron kapablajn organizi, elimini duplikojn kaj sinkronigi hibredajn muzikalajn kolektojn, kiuj estas spreditaj inter lokaj diskoj, skuvola stoka loko (Google Drive) kaj stremiĝaj servoj (Spotify, Deezer, Amazon Music).

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

## 📌 Funkciójoj & Statuo de la projekto

| Funkcionaleco | Altigo | Stato |
| :--- | :---: | :---: |
| **Audiolektila motoro** | Lega kaj aŭtonoma audiolektilo (VLC portabla aŭtomate instigita sous Windows). Du motoroj por elekto: direkta VLC eliro, aŭ kontinua tamponmotoro por flua enĉeno inter du trakoj (Gapless 0 ms, fondu enĉeno kun ekvuala potenco, sen interpunkto de la audioeliro) | 🟢 Implimentita |
| **Ĝistamento de la biblioteko** | Rekurziva multithreada skano de lokaj dosieroj (MP3, FLAC, AAC, OGG...), manaĝa, planigita aŭ en reala tempo sinkronigo, papiroĵkesto kaj statistiko de la biblioteko | 🟢 Implimentita |
| **Ekstraktado de metadatumoj** | Legado/skribado de ID3, Vorbis Comments kaj kalkulo de audio-imprinto (`mutagen`) | 🟢 Implimentita |
| **Subteno de plejlistoj (M3U, PLS, XSPF, WPL) & CUE-foliaj** | Arbara indeksado (🎶), sekvenca ordono de aŭskultado, vizuala lokado de mankantaj trakoj; la `.cue` dosieroj (💿) forigas kiel dosiero de virtualaj trakoj kun ilia daŭro kaj ludas kiel veraj trakoj | 🟢 Implimentita |
| **Plejlist-administrado kaj Drag-&Drop** | Virtualigita ventoj, flua drag & drop, reversaj kaj cikliĝaj aleĝoj (shuffle) | 🟢 Implimentita |
| **Interagativa « 🎲 Blind Test » modo** | Immergeva muzika ludo kun animata kontaŭo, son-fondu, milda rivelado kaj aŭtomatika enĉeno | 🟢 Implimentita |
| **Aŭordigoj en la apliko** | Automata/manuala verigo de versioj tra GitHub Releases | 🟢 Implementita |
| **Versioj por Linux & macOS** | Paĉoj `.AppImage` / `.tar.gz` (Linux) kaj ne-signita `.dmg` (macOS), VLC necesa | 🟡 Eksperimenta (ne testita) |
| **Administrado de artistoj & Diskografio** | Dedikita vido por artisto kun albumoj, singloj kaj kompleta diskografio | 🟡 Planita |
| **Grafika egalizilo (EQ)** | Audio presetoj kaj parametra multbanda egalizilo | 🟡 Planita |
| **Konekto por Google Drive** | Skano kaj sinkronigo de malproksimaj audio-kolekcioj tra OAuth 2.0 | ⚪ Planigita |
| **Konekto por Amazon Music** | Skano kaj sinkronigo de malproksimaj kolecioj tra OAuth 2.0 | ⚪ Planigita |
| **Konekto por Spotify / Deezer** | Importado de plejlistoj kaj korespondado de trakoj | ⚪ Planigita |
| **Inteligenta duplikado-elimino** | Detekto de duplikoj (titolo/artisto flusitaj + akustikaj prientoj) | ⚪ Planigita |

> 💡 *Por konsulti la detalo de la milestonoj kaj planitaj versioj, atentuoksu la [Milestonaj paŝoj (Roadmap)](../../ROADMAP.md).*

---

## 📌 Disajn lingvoj

Angla, Esperanto, Hispania, Alemañga, Italio, Portuga, Japonika, Rusika, Polaka, Turka, Nederlando, Sueca, Indonesa, Bulgara, Serva, Bieloruso, Greka, Katalanka, Baska, Galika, Čeka, Slovakanka, Hungarika, Kroata, Slovenca, Bosniaka, Estona, Letona, Litvana, Norvegika, Danika, Finika, Islandika, Malaja, Tagalog, Swahili, Esperanto, Sinicaj simpligita, Sinicaj tradicia, Koreana, Arabo, Hebrea, Vietnamika

---

## 🚀 Rapida komenco

### Premrequis

- **Python 3.11** aŭ pli alta instalita
- Git

### Instalado

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

## 🐧🍎 Linux kaj macOS : ekperimentaĵaj versioj (ne testitaj)

La pakoj de Linux (`.AppImage` / `.tar.gz`) kaj macOS (`.dmg`) estas provizitaj **sen esti testitaj**: AMSO estis validigita nur sub Windows. La audio-motoro kun konstanta tampon (`buffer`) en specialo ne estis verigita sur tiuj sistemoj. Via retopo estas precia.

- **VLC estas necesa** (AMSO elĉargigas ĝin nur sub Windows) :
  - Linux : `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) aŭ `sudo pacman -S vlc` (Arch).
  - macOS : instalu **VLC.app** el [videolan.org](https://www.videolan.org/vlc/) en la Aplikaĵoj dosiero.
- **Linux, sistemaj bibliotekoj** : la Qt-interfaco petas ekzemple `libpulse0` (sono), `libxcb-cursor0` kaj `libxkbcommon-x11-0` (ekzemple `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, ne-signata `.dmg`** : dum la unua lancigo, faru klak-dekstre sur AMSO kaj poste **Malfermi**, aŭ ekzekutu `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage** : farigu ĝin ekzekutebla kun `chmod +x AMSO*.AppImage`.
- **En la kazo de problemo**, bonvolu sendi la fajlojn `startup.log` kaj `crash.log` (se ili ekzistas) situantaj en la datumoj dosiero: `~/Library/Application Support/AMSO/` sub macOS, `~/.local/share/AMSO/` sub Linux. Specigu vian sistemon kaj la version de VLC.

---

## 🧪 Lanĉo de la testoj

La projekto uzas `pytest` kun serio de unitaj kaj integrado testoj:

```bash
pytest -v
```

Testoj ekzigrante aŭtomatiskaj sur **Windows, macOS et Ubuntu** ĉiu pŝo per GitHub Actions.

---

## 🔒 Sekureco & API-klavoj

- **Ne jamais komitu realajn API-klavojn aŭ aŭtentikig-tokenojn.**
- La skisto `.gitignore` estas pre-konfigurita por blokigi `.env`, `credentials.json`, `token.json` kaj ĉiujn lokajn SQLite-bazoj de datumoj.
- Uzigu `.env.example` kiel modelo por via plumboj-afero.

---

## 📋 Dokumentoj & Superado de la projekto

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Detala ĝislibro de versioj, novaj funkcioj kaj ĝustigoj de eraroj.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Mapo de estontaj milmiloj (Artistoj, Cloud, Spotify, Duplikado-elimino).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Statuto de loĝistika arkitekturo kaj reguloj de kodo-kvalito.

---

## 💖 Subteni la projekto & Distribuo

AMSO estas un libera kaj gratis programaro (open source). Se vi apreciigas la aplikaĵon kaj deziras stimuli ĝej dezvolviĝon:

- 🎮 **Avenemdonado & Pagonu Kion Vi Volas :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (prekompilita ekzekutablo parata por uzo)
- ☕ **Direkta Donacoj :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsoroj :** [Sponzori LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licenco

Ĉi tiu projekto estas sub licenco **GNU General Public License v3.0 (GPL-3.0)** — konsultu la fiilon [LICENSE](../../LICENSE) por pli da detajoj.
