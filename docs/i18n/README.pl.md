# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <b>Polski</b> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) to nowoczesny, responsywny i wieloplatformowy odtwarzacz audio stacjonarny (Windows, Linux, macOS). Zaprojektowany, aby zapewnić audiofilom pełną kontrolę nad ich lokalną biblioteką muzyczną (MP3, FLAC, OGG…), obsługuje teraz playlisty (M3U, PLS, XSPF, WPL), pliki CUE (albumy w jednym pliku podzielone na utwory) i integruje zupełnie nowy tryb blind test audio! Projekt ewoluuje w kierunku unifikowanego centrum dowodzenia, które jest w stanie organizować, usuwać duplikaty i synchronizować hybrydowe kolekcje muzyczne rozproszone między dyskami lokalnymi, przechowywaniem w chmurze (Google Drive) i usługami strumieniowania (Spotify, Deezer, Amazon Music).

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

## 📌 Funkcje & Status projektu

| Funkcjonalność | Opis | Status |
| :--- | :---: | :---: |
| **Wbudowany silnik odtwarzania VLC** | Lekki i niezależny odtwarzacz audio z automatyczną instalacją VLC portable i płynnym zarządzaniem głośnością | 🟢 Zaimplementowano |
| **Lokalny skaner wielowątkowy** | Rekurencyjne i szybkie wykrywanie lokalnych plików audio (MP3, FLAC, AAC, OGG...) | 🟢 Zaimplementowano |
| **Ekstrakcja metadanych** | Odczyt/zapis ID3, Vorbis Comments i obliczanie sygnatury audio (`mutagen`) | 🟢 Zaimplementowano |
| **Obsługa playlist (M3U, PLS, XSPF, WPL) i arkuszy CUE** | Indeksowanie drzewiaste (🎶), sekwencyjny porządek słuchania, wizualne lokalizowanie brakujących utworów; pliki `.cue` (💿) otwierają się jak folder z wirtualnymi ścieżkami z ich czasem trwania i odtwarzają się jak prawdziwe ścieżki | 🟢 Zaimplementowano |
| **Menedżer playlist i przeciąganie/upuszczanie** | Wirtualna kolejka, płynne przeciąganie i upuszczanie, odwracalna losowość (shuffle) i pętle | 🟢 Zaimplementowano |
| **Interaktywny tryb „🎲 Blind Test”** | Immersywna gra muzyczna z animowanym odliczaniem, wyciszeniem dźwięku, łagodnym ujawnianiem i automatycznym ciąganiem | 🟢 Zaimplementowano |
| **Aktualizacje w aplikacji** | Automatyczna/ręczna weryfikacja wersji za pomocą GitHub Releases | 🟢 Zaimplementowano |
| **Zarządzanie artystami i dyskografią** | Dedykowany widok dla artysty z albumami, singlami i pełną dyskografią | 🟡 Planowane |
| **Graficzny ekwalizer (EQ)** | Presety audio i parametryczny ekwalizer wielopasmowy | 🟡 Planowane |
| **Konnektor Google Drive** | Skanowanie i synchronizacja zdalnych kolekcji audio za pomocą OAuth 2.0 | ⚪ Planowane |
| **Konnektor Amazon Music** | Skanowanie i synchronizacja zdalnych kolekcji za pomocą OAuth 2.0 | ⚪ Planowane |
| **Konnektor Spotify / Deezer** | Importowanie playlist i dopasowywanie utworów | ⚪ Planowane |
| **Inteligentne usuwanie duplikatów** | Wykrywanie duplikatów (rozmyte tytuły/artyści + odciski akustyczne) | ⚪ Planowane |

> 💡 *Aby zapoznać się ze szczegółami planowanych kamieni milowych i wersji, zapoznaj się z [Mapą drogową (Roadmap)](../../ROADMAP.md).*

---

## 📌 Dostępne języki

Angielski, Francuski, Hiszpański, Niemiecki, Włoski, Portugalski, Japoński, Rosyjski, Polski, Turecki, Niderlandzki, Szwedzki, Indonezyjski, Bułgarski, Sérbski, Białoruski, Grecki, Kataloński, Baskijski, Galicyjski, Czeski, Słowacki, Węgierski, Chorwacki, Słoweński, Bośniacki, Estoński, Łotyński, Litewski, Norweski, Duński, Fiński, Islandzki, Malezyjski, Tagalogski, Suahili, Esperanto, Chiński uproszczony, Chiński tradycyjny, Koreański, Arabski, Hebrajski, Wietnamski

---

## 🚀 Szybki start

### Wymagania wstępne

- **Python 3.11** lub nowsza wersja zainstalowana
- Git

### Instalacja

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

## 🧪 Uruchomienie testów

Projekt wykorzystuje `pytest` z zestawem testów jednostkowych i integracyjnych:

```bash
pytest -v
```

Testy uruchamiają się automatycznie na **Windows, macOS i Ubuntu** przy każdym pushu za pośrednictwem GitHub Actions.

---

## 🔒 Bezpieczeństwo i klucze API

- **Nigdy nie commituj rzeczywistych kluczy API ani tokenów uwierzytelniających.**
- Plik `.gitignore` jest wstępnie skonfigurowany, aby blokować `.env`, `credentials.json`, `token.json` oraz wszystkie lokalne bazy danych SQLite.
- Użyj `.env.example` jako szablonu dla swojego środowiska deweloperskiego.

---

## 📋 Dokumentacja & Monitorowanie projektu

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Szczegółowy dziennik wersji, nowych funkcji i poprawek błędów.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Mapa drogowa przyszłych kamieni milowych (Artyści, Chmura, Spotify, Usuwanie duplikatów).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Karta architektury oprogramowania i zasady jakości kodu.

---

## 💖 Wsparcie projektu & Dystrybucja

AMSO jest darmowym i wolnym oprogramowaniem (open source). Jeśli cenisz tę aplikację i chcesz wspierać jej rozwój:

- 🎮 **Pobieranie & Płać ile chcesz :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (wykonywalny plik przedkompilowany gotowy do użycia)
- ☕ **Wsparcie bezpośrednie :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [Sponsoriser LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licencja

Ten projekt podlega licencji **GNU General Public License v3.0 (GPL-3.0)** — zapoznaj się z plikiem [LICENSE](../../LICENSE), aby uzyskać więcej szczegółów.
