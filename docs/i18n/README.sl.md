# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <b>Slovenščina</b> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) je sodoben, reaktivni in večplatformski stacijski avdio speler (Windows, Linux, macOS). Zasumen za zagotavljanje audiofilev popolne kontrole nad njihovo lokalno glasbeno knjižnico (MP3, FLAC, OGG…), zdaj pa podpira sezname avdio (M3U, PLS, XSPF, WPL), CUE datoteke (albumi v eni datoteki, razdeljeni na spore) in vključuje popolnoma nov način avdio blind testa! Projekt se razvija v smeru, da postane centralizirano upravljanje, sposobno organizirati, odstraniti duplikate in sinhronizirati hibridne glasbene zbirke, razporejene med lokalnimi diski, oblakskladišča (Google Drive) in storitvemi za streaming (Spotify, Deezer, Amazon Music).

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

## 📌 Funkcionalnosti & Status projekta

| Funkcionalnost | Opis | Status |
| :--- | :---: | :---: |
| **Motor za avdio reprodukcijo** | Lagani in samostojni avdio speler (VLC portable, avtomatsko namestitev pod Windows). Dva motorja za izbiro: neposredno izku VLC, ali motor s stalnim predpomnikovanjem za brezprekinjeno prehodno povezovanje med dvema sledljivima (Gapless 0 ms, prehod z enakim močjo, brez prekinitve avdio izхода) | 🟢 Implementirano |
| **Upravljanje knjižnice** | Rekurzivno, multi-threaded skeniranje lokalnih direktorijev (MP3, FLAC, AAC, OGG...), ročna, zakladirana ali v realnem času sinhronizacija, koš za smeti in statistika knjižnice | 🟢 Implementirano |
| **Izvračanje metadata** | Čtikanje/pisanje ID3, Vorbis Comments in izračun avdio prajevja (`mutagen`) | 🟢 Implementirano |
| **Podpora za spletne liste (M3U, PLS, XSPF, WPL) in CUE listine** | Drevočno indeksiranje (🎶), sekvenčni red slušanja, vizualno zaznavanje manjših delov; datoteke `.cue` (💿) se odpirajo kot virtualna zbirka sledilnikov z njihov trajanje in se spigajo kot pravi sledilniki | 🟢 Implementirano |
| **Upravitelj spletne liste in Drag & Drop** | Virtualiziran zavajalnik, tekoč drag & drop, obratna nasumična (shuffle) in zanki | 🟢 Implementirano |
| **Interaktivni način « 🎲 Blind Test »** | Immerzivna glasbena igra z animiranojo številčnico, zvokom prehodom, nežno razkritjem in avtomatskim povezovanjem | 🟢 Implementirano |
| **Znotrajne nadgradnje** | Avtomatsko/ručno preverjanje različic preko GitHub Releases | 🟢 Implementirano |
| **Različice za Linux in macOS** | Paketi .AppImage / .tar.gz (Linux) in nepodpisano .dmg (macOS), potreben je VLC | 🟡 Eksperimentalno (ni testirano) |
| **Upravljanje umetnikov in diskografije** | Dedicirana razglednica po umetniku z albumi, singliji in celotno diskografijo | 🟡 Predvideno |
| **Grafični ekvalizator (EQ)** | Audio prednastavitve in parametrični multiband ekvalizator | 🟡 Predvideno |
| **Konektor Google Drive** | Skeniranje in sinhronizacija oddaljenih audio zbiramščin preko OAuth 2.0 | ⚪ Planirano |
| **Konektor Amazon Music** | Skeniranje in sinhronizacija oddaljenih zbiramščin preko OAuth 2.0 | ⚪ Planirano |
| **Konektor Spotify / Deezer** | Importiranje seznamov predvsem in poravnavanje tokov | ⚪ Planirano |
| **Pametno odstranjevanje duplikatov** | Detekcija duplikatov (naslov/umetnik + akustični prajevzi) | ⚪ Planirano |

> 💡 *Za pregled podrobnosti predvidenih miljakov in verzij, se poskusite na [Mapa poti (Roadmap)](../../ROADMAP.md).*

---

## 📌 Dostpne jezike

Angleški, Francalski, Španski, Nemški, Italijanski, Portugalski, Japonski, Ruski, Poljski, Turkijski, Nizozemski, Švedski, Indonezijski, Bugarski, Srpski, Beloruski, Grški, Katalonski, Baskijski, Galicijski, Česki, Slovenski, Mađarski, Hrvatski, Slovenski, Bosanski, Estonski, Letonski, Litvanski, Norveški, Danski, Finski, Islandski, Malajski, Tagalski, Swahilijski, Esperantski, Kitajski (uproščeno), Kitajski (tradicionalni), Korejski, Arabski, Hebrejski, Vietnamski

---

## 🚀 Hitro začetje

### Predizogi

- **Python 3.11** ali višji instaliran
- Git

### Namestitev

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

## 🐧🍎 Linux in macOS: eksperimentalne različice (netestirane)

Paketi za Linux (`.AppImage` / `.tar.gz`) in macOS (`.dmg`) so dostavljeni **bre testiranja**: AMSO je bil validiran le pod Windows. Zlasti motor za audio z kontinuirnim predpomnikom (`buffer`) ni preverjen na teh sistemih. Vaš povratni odgovor je dragocen.

- **VLC je zahtevan** (AMSO ga nalagajo le pod Windows) :
  - Linux : `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) ou `sudo pacman -S vlc` (Arch).
  - macOS : namestite **VLC.app** z [videolan.org](https://www.videolan.org/vlc/) v imenik Applications.
- **Linux, sistemske knjižnice** : Qt vmesnik zahteva med spominjejo `libpulse0` (glas), `libxcb-cursor0` in `libxkbcommon-x11-0` (na primer `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, nesplošni .dmg** : pri prvem zagonu kliknite desno na AMSO in nato **Odprti**, ali pa izvedite `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage** : jo naredite izvršljiv z `chmod +x AMSO*.AppImage`.
- **V primeru težav**, prosim pošljite datoteke `startup.log` in `crash.log` (če obstajajo), ki so v imeniku podatkov: `~/Library/Application Support/AMSO/` pod macOS, `~/.local/share/AMSO/` pod Linux. Prosim navedite svoj sistem in različico VLC.

---

## 🧪 Začetek testov

Projekt uporablja `pytest` z skupino unitarnih in integracijskih testov:

```bash
pytest -v
```

Testi se samodejno izvršajo na **Windows, macOS in Ubuntu** pri vsakem pushu preko GitHub Actions.

---

## 🔒 Varnost in API ključi

- **Nikoli ne commitujte dejanskih API ključev ali tokenov za autentifikacijo.**
- Datoteka `.gitignore` je predkonfigurirana za blokiranje `.env`, `credentials.json`, `token.json` in vseh lokalnih baz podatkov SQLite.
- Uporabite `.env.example` kot predlogo za vaše razvojno okolje.

---

## 📋 Dokumentacija in spremljanje projekta

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Podrobni dnevnik različic, novih funkcij in popravkov napak.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Mapa poti za prihodnje meridijane (Umjenice, Oblak, Spotify, De-duplikacija).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Pravilnik za programske arhitekture in pravila kakovosti kode.

---

## 💖 Podpora za projekt & Distribucija

AMSO je brezplačna in prostopna programska oprema (open source). Če vam se všeč aplikacija in želite podporejšati njen razvoj:

- 🎮 **Prenos & Plača kar želiš :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (predkompilirana izvršna datoteka, pripravljena za uporabo)
- ☕ **Direktno donacija :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [Sponsorjajte LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licenca

Ta projekt je pod licenco **GNU General Public License v3.0 (GPL-3.0)** — preverite datoteko [LICENSE](../../LICENSE) za več podrobnosti.
