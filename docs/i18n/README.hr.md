# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <b>Hrvatski</b> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) je moderni, reaktivni i višedostruki desktop audio plejer (Windows, Linux, macOS). Dizajniran da pruži audiofilima potpunu kontrolu nad njihovom lokalnom glazbenom bibliotekom (MP3, FLAC, OGG…), sada podržava liste za reprodukciju (M3U, PLS, XSPF, WPL), CUE datoteke (albumi u jednoj datoteci, razbijeni na numere) i integrira potpuno novi režim audio blind testa! Projekt se razvija u jedinstreno kontrolno središte sposobno organizirati, ukloniti duplikate i sinhronizirati hibridne glazbene kolekcije raspoređene između lokalnih diskova, cloud pohrane (Google Drive) i streaming usluga (Spotify, Deezer, Amazon Music).

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

## 📌 Funkcionalnosti & Status projekta

| Funkcionalnost | Opis | Status |
| :--- | :---: | :---: |
| **Integrirani VLC reproduktor** | Lagani i samostalni audio reproduktor s automatskom instalacijom VLC Portable i glatkim upravljanjem volumena | 🟢 Implementirano |
| **Multithread lokalni skener** | Rekurzivno i brzo otkrivanje lokalnih audio datoteka (MP3, FLAC, AAC, OGG...) | 🟢 Implementirano |
| **Ekstrakcija metapodataka** | Čitanje/pisanje ID3, Vorbis Comments i izračun audio otiska prsta (`mutagen`) | 🟢 Implementirano |
| **Podrška za playliste (M3U, PLS, XSPF, WPL) i CUE listice** | Stablo indeksiranje (🎶), sekvencijalni red slušanja, vizualno lociranje nedostajućih pjesama; .cue datoteke (💿) otvaraju se kao virtualni direktorij pjeva s trajanju i reprodukuju se kao prave pjesme | 🟢 Implementirano |
| **Upravitelj playlista & Povlačenje-Otpuštanje** | Virtualizirana redovna lista, glatko drag & drop, obrnuto nasumično (shuffle) i petlje | 🟢 Implementirano |
| **Interaktivni način rada « 🎲 Blind Test »** | Imurzivna glazbena igra s animiranim brojačem, zvučnim fade-outom, nježnim otkrivanjem i automatskim povezivanjem | 🟢 Implementirano |
| **Ažuriranja u aplikaciji** | Automatska/ručna provjera verzija putem GitHub Releases | 🟢 Implementirano |
| **Upravljanje izvođačima i diskografijom** | Posvećeni pregled po izvođaču s albumima, singlovima i kompletnom diskografijom | 🟡 Planirano |
| **Grafički ekvalizator (EQ)** | Audio predumjetne postavke i parametrični multiband ekvalizator | 🟡 Planirano |
| **Konektor Google Drive** | Skeniranje i sinhronizacija udaljenih audio kolekcija putem OAuth 2.0 | ⚪ Planirano |
| **Konektor Amazon Music** | Skeniranje i sinhronizacija udaljenih kolekcija putem OAuth 2.0 | ⚪ Planirano |
| **Konektor Spotify / Deezer** | Uvoz playlista i podudarnost pjesama | ⚪ Planirano |
| **Inteligentno uklanjanje duplikata** | Detekcija duplikata (zamagljeno imeno/izvođač + akustički otisci) | ⚪ Planirano |

> 💡 *Za pregled detalja planiranih prekretnica i verzija, pogledajte [Mapu puta (Roadmap)](../../ROADMAP.md).*

---

## 📌 Dostupni jezici

Engleski, Francuski, Španjolski, Njemački, Talijanski, Portugalski, Japanski, Ruski, Poljski, Turski, Nizozemski, Švedski, Indonezijski, Bugarski, Srpski, Białoruski, Grčki, Katalonski, Baskijski, Galijski, Češki, Slovački, Mađarski, Hrvatski, Slovenski, Bosanski, Estonski, Letonski, Litvanski, Norveški, Danski, Finski, Islandski, Malezijski, Tagalogski, Swahili, Esperantski, Kineski (pojednostavljeno), Kineski (tradicionalno), Korejski, Arapski, Hebrejski, Vijetnamski

---

## 🚀 Brzo pokretanje

### Preduslovi

- **Python 3.11** ili viši instaliran
- Git

### Instalacija

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

## 🧪 Pokretanje testova

Projekt koristi `pytest` s nizom jedinica i integracijskih testova:

```bash
pytest -v
```

Testovi se automatski izvršavaju na **Windows, macOS i Ubuntu** pri svakom pushu putem GitHub Actions.

---

## 🔒 Sigurnost & API ključeve

- **Nikada ne commitirajte stvarne API ključeve niti tokene za autentifikaciju.**
- Datoteka `.gitignore` je predkonfigurirana za blokiranje `.env`, `credentials.json`, `token.json` i svih lokalnih SQLite baza podataka.
- Koristite `.env.example` kao predložak za vaše razvojno okruženje.

---

## 📋 Dokumentacija & Praćenje projekta

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Detaljni dnevnik verzija, novih značajnosti i popravaka grešaka.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Mapa puta budućih prekretnica (Umjetnici, Cloud, Spotify, De-dupliranje).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Povelja arhitekture softvera i pravila kvalitete koda.

---

## 💖 Podrška projektu & Distribucija

AMSO je slobodan i besplatan softver (open source). Ako vam se sviđa aplikacija i želite potaknuti njen razvoj:

- 🎮 **Preuzimanje & Plati koliko želiš:** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (predkompajlirani izvršni fajl spreman za upotrebu)
- ☕ **Direktni doprinos:** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponzori:** [Sponzoriraj LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licence

Ovaj projekt je pod licencom **GNU General Public License v3.0 (GPL-3.0)** — pogledajte datoteku [LICENSE](../../LICENSE) za više detalja.
