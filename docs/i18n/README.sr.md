# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <b>Српски</b> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) je moderan, reaktivni i višedostruki desktop audio plejer (Windows, Linux, macOS). Dizajniran da pruži audiofilima potpunu kontrolu nad njihovom lokalnom muzičkom bibliotekom (MP3, FLAC, OGG…), sada podržava plejliste (M3U, PLS, XSPF, WPL), CUE fajlove (albumi u jednom fajlu isečeni na numere) i integriše potpuno novi režim audio blind testa! Projekat se razvija da postane centralizovani kontrolni centar sposoban da organizuje, de-duplira i sinhronizuje hibridne muzičke kolekcije raspoređene između lokalnih diskova, cloud skladišta (Google Drive) i streaming servisa (Spotify, Deezer, Amazon Music).

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
| **Integrisan VLC plejer** | Lagani i samostalan audio plejer sa automatskim instaliranjem VLC portable i glatkim upravljanjem jačinom | 🟢 Implementirano |
| **Multithread lokalni skener** | Rekurzivno i brzo otkrivanje lokalnih audio fajlova (MP3, FLAC, AAC, OGG...) | 🟢 Implementirano |
| **Ekstrakcija metapodataka** | Čitanje/pisanje ID3, Vorbis Comments i izračunavanje audio otiska (`mutagen`) | 🟢 Implementirano |
| **Podrška za plejliste (M3U, PLS, XSPF, WPL) & CUE fajlove** | Hijerarhijsko indeksiranje (🎶), sekvencijalni red slušanja, vizuelno lociranje nedostajućih numera; fajlovi `.cue` (💿) se otvaraju kao direktorijum virtuelnih numera sa njihovom dužinom i reprodukuju se kao prave numere | 🟢 Implementirano |
| **Menadžer plejlista & Povlačenje-Pritiskanje** | Virtualizovani red čekanja, glatko drag & drop, reverzibilno nasumično (shuffle) i petlje | 🟢 Implementirano |
| **Interaktivni režim « 🎲 Blind Test »** | Imersivna muzička igra sa animiranim brojačem, zvučnim fade-om, blagim otkrivanjem i automatskim sekvenciranjem | 🟢 Implementirano |
| **Ažuriranja u aplikaciji** | Automatska/ručna provera verzija preko GitHub Releases | 🟢 Implementirano |
| **Upravljanje izvođačima i diskografijom** | Posveđeni pregled po izvođaču sa albumima, singlovima i kompletnom diskografijom | 🟡 Planirano |
| **Grafički ekvailajzer (EQ)** | Audio predlošci i parametrični multi-band ekvailajzer | 🟡 Planirano |
| **Google Drive Konektor** | Skeniranje i sinhronizacija udaljenih audio kolekcija preko OAuth 2.0 | ⚪ Planirano |
| **Amazon Music Konektor** | Skeniranje i sinhronizacija udaljenih kolekcija preko OAuth 2.0 | ⚪ Planirano |
| **Spotify / Deezer Konektor** | Uvoz plejlista i podudarnost numera | ⚪ Planirano |
| **Pametno uklanjanje duplikata** | Detekcija duplikata (nejasni naslov/izvođač + akustički otisci) | ⚪ Planirano |

> 💡 *Da biste videli detalje planiranih prekretnica i verzija, pogledajte [Mapa puta (Roadmap)](../../ROADMAP.md).*

---

## 📌 Dostupni jezici

Engleski, Francuski, Španski, Nemački, Talijanski, Portugalski, Japanski, Ruski, Poljski, Turski, Holandski, Švedski, Indonezijski, Bugarski, Srpski, Beloruski, Grčki, Katalonski, Baskijski, Galicijski, Češki, Slovački, Mađarski, Hrvatski, Slovenski, Bosanski, Estonski, Letonski, Litvanski, Norveški, Danski, Finski, Islandski, Malajski, Tagalski, Swahilijski, Esperanski, Kineski (jednostavni znakovi), Kineski (tradicionalni znakovi), Korejski, Arapski, Hebrejski, Vijetnamski

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

Projekat koristi `pytest` sa paketom jedinica i integracionih testova:

```bash
pytest -v
```

Testovi se automatski pokreću na **Windows, macOS i Ubuntu** pri svakom push-u preko GitHub Actions.

---

## 🔒 Bezbednost & API Ključevi

- **Nikada ne commitujte stvarne API ključeve niti tokene za autentifikaciju.**
- Fajl `.gitignore` je predkonfigurisan da blokira `.env`, `credentials.json`, `token.json` i sve lokalne SQLite baze podataka.
- Koristite `.env.example` kao šablon za vaše razvojno okruženje.

---

## 📋 Dokumentacija & Praćenje projekta

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Detaljan dnevnik verzija, novih funkcija i popravki grešaka.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Mapa puta budućih prekretnica (Umjenici, Cloud, Spotify, De-dupliranje).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Pravilnik arhitekture softvera i pravila za kvalitet koda.

---

## 💖 Podržati projekat & Distribucija

AMSO je slobodan i besplatan softver (open source). Ako vam se sviđa aplikacija i želite da podstaknete njen razvoj:

- 🎮 **Preuzimanje & Plati koliko želiš :** [Itch.io stranica AMSO](https://lef97.itch.io/audio-multi-source-organizer) (predkompajlirani izvršni fajl spreman za upotrebu)
- ☕ **Direktni doprinos :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponzori :** [Sponzorišati LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licenca

Ovaj projekat je pod licencom **GNU General Public License v3.0 (GPL-3.0)** — pogledajte fajl [LICENSE](../../LICENSE) za više detalja.
