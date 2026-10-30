# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <b>Magyar</b> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) egy modern, reaktív és multiplatformos asztali hanglejátszó (Windows, Linux, macOS). Létrehozva, hogy az audiofilek rajongóinak teljes kontrollt biztosítson helyi zenei könyvtárjuk felett (MP3, FLAC, OGG…), most támogatja a lejátszási listákat (M3U, PLS, XSPF, WPL), a CUE lapokat (albumok, amelyek egy fájlban vannak és trackekre bontva) és beépít egy teljesen új hangos blind test módot! A projekt fejlődik egy egységes vezérlő központá, amely képes rendszerezni, duplázatosítást eltávolítani és szinkronizálni azokat a hibrid zenei gyűjteményeket, amelyek helyi lemezek között, cloud tárolásban (Google Drive) és streaming szolgáltatásokban (Spotify, Deezer, Amazon Music) vannak elosztva.

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

## 📌 Funkciók és Projekt státusza

| Funkció | Leírás | Státusz |
| :--- | :---: | :---: |
| **Hangjátszási motor** | Könnyű és független hangjátszó (VLC portable automatikusan telepítve Windows alatt). Két motor választékban: közvetlen VLC kimenet, vagy folyamatos tamponmotor két dal között zökkenőmentes átmenethez (Gapless 0 ms, egyenletes teljesítményű fade, hangkimenet megszakítás nélkül) | 🟢 Megvalósítva |
| **Könyvtárkezelés** | Multithread rékurzív szkennelés helyi könyvtárakból (MP3, FLAC, AAC, OGG...), kézi, ütemezett vagy valós idejű szinkronizáció, kosár és könyvtárstatisztika | 🟢 Megvalósítva |
| **Metadátum-kivonás** | ID3, Vorbis Comments olvasása/írása és hangajnyom számítása (`mutagen`) | 🟢 Megvalósítva |
| **Playlist támogatás (M3U, PLS, XSPF, WPL) és CUE lapok** | Önváló indexelés (🎶), sorrendi hallgatási sorrend, hiányzó dalok vizuális azonosítása; a .cue fájlok (💿) virtuális dalok mappájaként nyílnak, időtartalmukkal, és való dalokként játszhatók | 🟢 Megvalósítva |
| **Playlist Kezelő & Húzás-Dobozás** | Virtualizált sorbaépítés, zökkenőmentes drag & drop, visszafordítható véletlenszerű (shuffle) és ciklusok | 🟢 Megvalósítva |
| **Interaktív „🎲 Blind Test” mód** | Immerziós zenei játék animált számlálóval, hangfade-vel, puha felfedezéssel és automatikus átmenettel | 🟢 Megvalósítva |
| **Alkalmazásbelüli frissítések** | Automatikus/manuális verzióellenőrzés a GitHub Releases-en keresztül | 🟢 Megvalósítva |
| **Linux és macOS verziók** | `.AppImage` / `.tar.gz` csomagok (Linux) és nem aláírt `.dmg` (macOS), VLC szükséges | 🟡 Eksperimentális (nem tesztelt) |
| **Artistok és diskográfia kezelése** | Dedikált nézet művősök számára albumokkal, singlekkel és teljes diskográfíával | 🟡 Tervezett |
| **Grafikus égalizer (EQ)** | Hangszín alapok és paraméteres többbandás égalizer | 🟡 Tervezett |
| **Google Drive kapcsolat** | Táv hangszíngyűjtemények szkennelése és szinkronizálása OAuth 2.0 segítségével | ⚪ Tervezett |
| **Amazon Music kapcsolat** | Táv gyűjtemények szkennelése és szinkronizálása OAuth 2.0 segítségével | ⚪ Tervezett |
| **Spotify / Deezer kapcsolat** | Playlistek importálása és dalek eşleştirése | ⚪ Tervezett |
| **Okos duplikátkezelés** | Duplikatok detektálása (cím/művész borús + hangajomlatok) | ⚪ Tervezett |

> 💡 *A tervezett mérföldkövei és verziók részletes áttekintéséhez, kérjük, tekintse meg a [Feuille de route (Roadmap)](../../ROADMAP.md).*

---

## 📌 Elérhető nyelvek

Angol, Francia, Spanyol, Német, Olasz, Portugál, Japán, Orosz, Lengyel, Török, Hollanda, Sverdi, Indonéz, Bulgar, Szerb, Belorús, Grek, Katalán, Bask, Galíciai, Cseh, Szlovák, Magyar, Hrvatski, Szlovén, Boszniak, Estonoma, Lett, Litván, Norvég, Dán, Finnsz, Izlandi, Malaj, Tagalog, Swahili, Esperanto, Kínai (egyszerű), Kínai (tradicionális), Koreai, Arabi, Hébra, Việt

---

## 🚀 Gyors elindítás

### Előfeltételek

- **Python 3.11** vagy újabb verzió telepítve
- Git

### Telepítés

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

## 🐧🍎 Linux és macOS: eksperimentális verziók (nem tesztelt)

A Linux (`.AppImage` / `.tar.gz`) és macOS (`.dmg`) csomagok **tesztelés nélkül** biztosítottak: Az AMSO csak Windows alatt volt validálva. A folyamatos tamponú hangmotor (`buffer`) különösen ezeken a rendszereken nem volt ellenőrizve. Az Ön visszajelzése értékes.

- **A VLC szükséges** (AMSO csak Windows alatt töltse le) :
  - Linux : `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) vagy `sudo pacman -S vlc` (Arch).
  - macOS : telepíteni **VLC.app**-et [videolan.org](https://www.videolan.org/vlc/) adreséről az Applications mappában.
- **Linux, rendszerbibliothékok** : az Qt felület például `libpulse0`-t (hang), `libxcb-cursor0`-t és `libxkbcommon-x11-0`-t igényel (például `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, nem aláírt \`.dmg\`** : az első indításkor jobb gombbal kattintson az AMSO-ra, majd **Megnyitás**, vagy futtassa el `xattr -dr com.apple.quarantine /Applications/AMSO.app`-et.
- **Linux, AppImage** : teheti végrehajthatóvá `chmod +x AMSO*.AppImage`-del.
- **Probléma esetén**, kérjük küldje el a `startup.log` és `crash.log` fájlokat (ha léteznek), amelyek a adatkönyvtárban találhatók: `~/Library/Application Support/AMSO/` macOS alatt, `~/.local/share/AMSO/` Linux alatt. Kérjük pontosítsa a rendszerét és a VLC verzióját.

---

## 🧪 Tesztelés elindítása

A projekt `pytest`-et egység- és integrációs tesztcsoporttal használja:

```bash
pytest -v
```

A tesztek automatikusan futnak **Windows, macOS et Ubuntu** minden pushon keresztül via GitHub Actions.

---

## 🔒 Biztonság és API kulcsok

- **Soha ne commitelje élő API kulcsait vagy hitelesítő tokeneket.**
- Az `.gitignore` fájl előrekonfigurált, hogy blokkolja az `.env`, `credentials.json`, `token.json` és minden helyi SQLite adatbázist.
- Használja az `.env.example`-ot mint sablon a fejlesztői környezetéhez.

---

## 📋 Dokumentáció & Projektkövetés

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Részletes verzió-, új funkció- és hibajavítási napló.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Újraérhetővé tételekre vonatkozó útvonal (Artistes, Cloud, Spotify, Dédoublonnage).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Szoftverarchitektúra és kódminőségi szabályzat.

---

## 💖 Projekt támogatása & Elosztás

AMSO egy ingyenes és szabad forráskódú (open source) szoftver. Ha kedveli az alkalmazást, és szeretné támogatni a fejlesztését:

- 🎮 **Letöltés & Fizessen, amennyit akar :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (előkompilált, használatra kész végrehajtható fájl)
- ☕ **Közvetlen adományozás :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [LEF97 támogatása](https://github.com/sponsors/LEF97)

---

## 📄 Licenc

Ez a projekt licenc alatt van **GNU General Public License v3.0 (GPL-3.0)** — tekintse meg a [LICENSE](../../LICENSE) fájlt további részletekhez.
