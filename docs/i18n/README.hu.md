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
| **Beépített VLC lejátszó motor** | Könnyű, önálló hanglejátszó, hordozható VLC automatikus telepítésével és zökkenőmentes hangszín szabályozásával | 🟢 Implementált |
| **Multithread-es helyi szkanner** | Rekurziív és gyors helyi hang fájlok felfedezése (MP3, FLAC, AAC, OGG...) | 🟢 Implementált |
| **Metadát-kivonás** | ID3, Vorbis Comments olvasása/írása és hangajakkép számítása (`mutagen`) | 🟢 Implementált |
| **Playlista támogatás (M3U, PLS, XSPF, WPL) és CUE lapok** | Árkok indexelés (🎶), sorrendi hallgatási sorrend, hiányzó darabok vizuális azonosítása; a .cue fájlok (💿) virtuális sávok mappájaként nyílnak, időtartammal, és való sávokként játszhatók | 🟢 Implementált |
| **Playlista menedzsment és húz-dobálás** | Virtualizált sorbaépítés, zökkenőmentes húz-dobálás, visszafordítható véletlenszerű (shuffle) és ciklusok | 🟢 Implementált |
| **Interaktív „🎲 Blind Test” mód** | Immerziós zenei játék animált számlálóval, hangfadekkal, puha felfedezéssel és automatikus sorrendel | 🟢 Implementált |
| **In-app frissítések** | Automata/manuális verzióellenőrzés GitHub Releases-en keresztül | 🟢 Implémenté |
| **Művészek és diskográfia kezelése** | Dedikált nézet művészről albumokkal, single-ekkel és teljes diskográfiával | 🟡 Prévu |
| **Grafikus égalizer (EQ)** | Hangpresetek és paraméteres multibánd égalizer | 🟡 Prévu |
| **Google Drive kapcsoló** | Táv hangkolekciók szkennelése és szinkronizálása OAuth 2.0-on keresztül | ⚪ Planifié |
| **Amazon Music kapcsoló** | Táv kolekciók szkennelése és szinkronizálása OAuth 2.0-on keresztül | ⚪ Planifié |
| **Spotify / Deezer kapcsoló** | Playlist importálás és dalek eşleştirése | ⚪ Planifié |
| **Intelligens duplikátumeltávolítás** | Duplikatok felismerése (homályos cím/művész + hangajomtatványok) | ⚪ Planifié |

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
