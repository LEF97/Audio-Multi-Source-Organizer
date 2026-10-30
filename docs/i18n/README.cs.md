# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <b>Čeština</b> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) je moderní, reaktivní a multiplatformní desktopový audio přehrávač (Windows, Linux, macOS). Navržen tak, aby audiofilům poskytoval plnou kontrolu nad jejich lokální müzickou knihovnou (MP3, FLAC, OGG…), nyní podporuje seznamy přehrávání (M3U, PLS, XSPF, WPL), CUE soubory (albumy z jednoho souboru rozdělené na skladby) a integruje zcela nový režim audio blind testu! Projekt se vyvíjí, aby se stal jednotrem řídicím centrem schopným organizovat, odstraňovat duplicity a synchronizovat hybridní müzické sbírky rozdělené mezi lokální disky, cloudové úložiště (Google Drive) a streamovací služby (Spotify, Deezer, Amazon Music).

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

## 📌 Funkce a stav projektu

| Funkce | Popis | Stav |
| :--- | :--- | :---: |
| **Audio přehrávačový motor** | Lehčí, samostatný audio přehrávač (VLC portable automaticky nainstalován pod Windows). Dva motory na výběr: přímý výstup VLC, nebo neustálý vyrovnávací paměťový motor pro plynulý přechod mezi dvěma skladbami (Gapless 0 ms, vyrovnávací fade na rovnoměrnou sílu, bez přerušení audio výstupu) | 🟢 Implementováno |
| **Správa knihovny** | Rekurzivní multithreadový sken lokálních složek (MP3, FLAC, AAC, OGG...), ruční, plánovaná nebo v reálném čase synchronizace, koše a statistiky knihovny | 🟢 Implementováno |
| **Extrakce metadat** | Čtení/zápis ID3, Vorbis Comments a výpočet audio fingerprintu (`mutagen`) | 🟢 Implementováno |
| **Podpora playlistů (M3U, PLS, XSPF, WPL) a CUE souborů** | Strojové indexování (🎶), sekvenční pořadí poslechu, vizuální lokalizace chybějících skladeb; soubory `.cue` (💿) se otevírají jako složka virtuálních skladeb se svou délkou a přehrávají se jako skutečné sklady | 🟢 Implementováno |
| **Správce playlistů a přetahování (Drag & Drop)** | Virtualizovaná fronta, plynulý drag & drop, zvratné náhodné (shuffle) a smyčky | 🟢 Implementováno |
| **Interaktivní režim „🎲 Blind Test“** | Imersivní hudební hra s animovaným počítáním, zvukovým fade, jemným odhalováním a automatickým přechodem | 🟢 Implementováno |
| **Aktualizace v aplikaci** | Automatické/ruční ověření verzí přes GitHub Releases | 🟢 Implementováno |
| **Verze pro Linux a macOS** | Balíčky .AppImage / .tar.gz (Linux) a neověřené .dmg (macOS), vyžaduje VLC | 🟡 Experimentální (netestováno) |
| **Správa umělců a diskografie** | Vyklená sekce pro umělce s albumy, singly a kompletní diskografií | 🟡 Plánováno |
| **Grafický ekvalizátor (EQ)** | Audio přednastavení a parametryický multibándový ekvalizátor | 🟡 Plánováno |
| **Konektor Google Drive** | Skenování a synchronizace vzdálených audio kolekcí přes OAuth 2.0 | ⚪ Plánováno |
| **Konektor Amazon Music** | Skenování a synchronizace vzdálených kolekcí přes OAuth 2.0 | ⚪ Plánováno |
| **Konektor Spotify / Deezer** | Importování playlistů a shoda skladeb | ⚪ Plánováno |
| **Inteligentní odstraňování duplicit** | Detekce duplicit (rozmazané titulky/umělství + akustické otisky) | ⚪ Plánováno |

> 💡 *Pro zobrazení podrobností plánovaných milníků a verzí se podívejte na [Feuille de route (Roadmap)](../../ROADMAP.md).*

---

## 📌 Dostupná jazyky

Anglais, Francouzština, Španělština, Němčina, Ýtalský, Portugalský, Japonský, Rusština, Polština, Turecká, Nizuchtština, Švédština, Indonéská, Bulharský, Srbský, Bieloruský, Řecký, Katalánština, Baskština, Galicština, Čeština, Slovensky, Maďarština, Chorvatský, Slovinsko, Bosnánština, Estonský, Lettovský, Litvinsko, Norský, Dánský, Finský, Islandský, Malajská, Tagalog, Swahilština, Esperanto, Čínština, Tradiční čínština, Korejština, Arabština, Hebréjština, Vietnamština

---

## 🚀 Rychlý start

### Předpoklady

- **Python 3.11** nebo vyšší instalovaný
- Git

### Instalace

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

## 🐧🍎 Linux a macOS: experimentální verze (netestované)

Linux balíčky (`.AppImage` / `.tar.gz`) a macOS (`.dmg`) jsou poskytovány **bez testování**: AMSO bylo ověřeno pouze na Windows. Audio motor s nepřetržitým bufferem (`buffer`) nebyl ověřen na těchto systémech. Vaše zpětná vazba je cenná.

- **VLC je zapadá** (AMSO jej stahuje pouze pro Windows) :
  - Linux : `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) nebo `sudo pacman -S vlc` (Arch).
  - macOS : nainstalujte **VLC.app** z [videolan.org](https://www.videolan.org/vlc/) do složky Applications.
- **Linux, systémové knihovny** : rozhraní Qt vyžaduje zejména `libpulse0` (zvuk), `libxcb-cursor0` a `libxkbcommon-x11-0` (např. `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, nesignovaný `.dmg`** : při prvním spuštění klikněte pravým tlačítkem na AMSO a poté **Otevřít**, nebo spusťte `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage** : staňte ho spustitelným pomocí `chmod +x AMSO*.AppImage`.
- **V případě problémů**, prosím o zaslání souborů `startup.log` a `crash.log` (pokud existují) nacházejících se v adresáři s daty: `~/Library/Application Support/AMSO/` pod macOS, `~/.local/share/AMSO/` pod Linux. Uveďte svůj systém a verzi VLC.

---

## 🧪 Spuštění testů

Projekt používá `pytest` s sadou jednotkových a integračních testů:

```bash
pytest -v
```

Testy běží automaticky na **Windows, macOS a Ubuntu** při každém pushu přes GitHub Actions.

---

## 🔒 Bezpečnost a API klíče

- **Nikdy necommitujte skutečné API klíče ani tokeny autentizace.**
- Soubor `.gitignore` je předkonfigurován k blokování `.env`, `credentials.json`, `token.json` a všech lokálních SQLite databází.
- Používejte `.env.example` jako šablonu pro vaše vývojové prostředí.

---

## 📋 Dokumentace a sledování projektu

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Podrobný záznam verzí, nových funkcí a oprav chyb.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Mapa cesty budoucích milníků (Umělci, Cloud, Spotify, Dekuplikační).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Charter softwarové architektury a pravidla kvality kódu.

---

## 💖 Podpora projektu & Distribuce

AMSO je volný a bezplatný software (open source). Pokud vám aplikace líbí a chcete podporovat její vývoj:

- 🎮 **Stahování & Zaplať co chceš :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (předkompilovatelný spouštěč připraven k použití)
- ☕ **Přímá podpora :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [Sponzorovat LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licence

Tento projekt je pod licencí **GNU General Public License v3.0 (GPL-3.0)** — konzultujte soubor [LICENSE](../../LICENSE) pro více podrobností.
