# Audio Multi-Source Organizer (AMSO)

<p align="right">
  <a href="README.fr.md">Français</a> • <a href="README.md">English</a> • <a href="README.es.md">Español</a> • <b>Deutsch</b> • <a href="README.it.md">Italiano</a>
</p>

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](CHANGELOG.de.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Zuk%C3%BCnftige%20Meilensteine-purple.svg)](ROADMAP.de.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) ist ein moderner, responsiver und plattformübergreifender Desktop-Audioplayer (Windows, Linux, macOS). Entwickelt, um Audiophilen die volle Kontrolle über ihre lokale Musiksammlung (MP3, FLAC, OGG…) zu geben, unterstützt er nun auch Playlist-Dateien (M3U, PLS, XSPF, WPL) und bietet ein interaktives Audio-Blind-Test-Spiel! Das Projekt wächst zu einem zentralen Hub heran, um hybride Musiksammlungen über lokale Festplatten, Cloud-Speicher (Google Drive) und Streaming-Dienste (Spotify, Deezer, Amazon Music) zu organisieren, deduplizieren und synchronisieren.

---

<p align="center">
  <img src="screenshots/2026-10-18%20v0.3.0%2002.png" alt="Audio Multi-Source Organizer (AMSO) - Ordnerbaum & Playlists 🎶" width="850">
</p>

<p align="center">
  <img src="screenshots/2026-10-18%20v0.3.0.png" alt="Audio Multi-Source Organizer (AMSO) - Audioplayer & Hyperspace" width="850">
</p>

<p align="center">
  <img src="screenshots/2026-10-18%20v0.3.0%20blind%20test.png" alt="Audio Multi-Source Organizer (AMSO) - Interaktives Blind-Test-Spiel" width="850">
</p>

---

## 📌 Funktionen & Projektstatus

| Funktion | Beschreibung | Status |
| :--- | :--- | :---: |
| **Integrierte VLC-Audiowiedergabe** | Schlanker, eigenständiger Player mit automatischer portabler VLC-Einrichtung und feinfühliger Lautstärkeregelung | 🟢 Implementiert |
| **Multithread-Lokaler Scanner** | Schnelle rekursive Erkennung lokaler Audiodateien (MP3, FLAC, AAC, OGG...) | 🟢 Implementiert |
| **Metadaten- & Cover-Extraktion** | Lesen/Schreiben von ID3-Tags, Vorbis-Kommentaren und Audio-Fingerprints (`mutagen`) | 🟢 Implementiert |
| **Unterstützung von Playlists (M3U, PLS, XSPF, WPL)** | Anzeige im Ordnerbaum (🎶), sequenzielle Reihenfolge und visuelle Warnung vor fehlenden Titeln | 🟢 Implementiert |
| **Playlist- & Warteschlangenverwaltung** | Virtualisierte Tabelle, flüssiges Drag & Drop, reversibler Zufallsmodus (Shuffle) und Schleifen | 🟢 Implementiert |
| **Interaktiver « 🎲 Blind-Test »-Modus** | Immersives Musikspiel mit animiertem Puls-Countdown, sanfter Enthüllung und automatischer Rundenabfolge | 🟢 Implementiert |
| **In-App-Update-Prüfung** | Automatische und manuelle Versionsprüfung über GitHub Releases | 🟢 Implementiert |
| **Künstler- & Diskografie-Hub** | Eigene Ansicht pro Künstler mit Alben, Singles und kompletter Diskografie | 🟡 Geplant |
| **Grafischer Equalizer (EQ)** | Klangprofile und parametrischer Mehrband-Equalizer | 🟡 Geplant |
| **Google Drive Cloud-Konnektor** | Synchronisation entfernter Audiosammlungen in der Cloud über OAuth 2.0 | ⚪ Geplant |
| **Amazon Music-Konnektor** | Synchronisation entfernter Musikordner über OAuth 2.0 | ⚪ Geplant |
| **Spotify / Deezer-Streaming-Integration** | Import von Wiedergabelisten und hybrider Titelabgleich | ⚪ Geplant |
| **Intelligente Deduplizierung** | Duplikaterkennung über unscharfe Metadaten und akustische Fingerabdrücke | ⚪ Geplant |

> 💡 *Detaillierte Meilensteine und Versionsplanungen finden Sie in der [Roadmap (ROADMAP.de.md)](ROADMAP.de.md).*

---

## 🚀 Schnellstart

### Voraussetzungen
- **Python 3.11** oder neuer
- Git

### Installation

```bash
# 1. Repository klonen
git clone https://github.com/LEF97/Audio-Multi-Source-Organizer.git
cd audio-multi-source-organizer

# 2. Virtuelle Umgebung erstellen
python -m venv .venv

# 3. Virtuelle Umgebung aktivieren
# Unter Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Unter Linux / macOS:
source .venv/bin/activate

# 4. Abhängigkeiten installieren
pip install -r requirements.txt

# Für Entwicklung und Tests:
pip install -e .[dev]

# 5. Umgebungsvariablen einrichten
cp .env.example .env

# 6. Anwendung starten
python main.py
```

---

## 🧪 Tests ausführen

Die automatisierte Testsuite basiert auf `pytest` und umfasst Unit- und Integrationstests:

```bash
pytest -v
```

Die Tests laufen bei jedem Push über GitHub Actions automatisch auf **Windows, macOS und Ubuntu**.

---

## 🔒 Sicherheit & API-Schlüssel

- **Übertragen Sie niemals echte API-Schlüssel oder Authentifizierungs-Token in Commits.**
- Die Datei `.gitignore` ist so eingerichtet, dass `.env`, `credentials.json`, `token.json` und lokale SQLite-Datenbanken blockiert werden.
- Nutzen Sie `.env.example` als Vorlage für Ihre lokale Entwicklungsumgebung.

---

## 📋 Dokumentation & Projektverfolgung

- 📜 **[CHANGELOG.de.md](CHANGELOG.de.md)** ([Version Française](CHANGELOG.fr.md) • [English Version](CHANGELOG.md)): Detailliertes Versionsprotokoll, neue Funktionen und Fehlerbehebungen.
- 🗺️ **[ROADMAP.de.md](ROADMAP.de.md)** ([Version Française](ROADMAP.fr.md) • [English Version](ROADMAP.md)): Roadmap künftiger Meilensteine (Künstler, Cloud, Spotify, Deduplizierung).
- 📐 **[CODE_QUALITY.md](CODE_QUALITY.md)**: Architektur- und Code-Qualitätsstandards.

---

## 💖 Projekt unterstützen & Download

AMSO ist freie Open-Source-Software. Wenn Ihnen die Anwendung gefällt und Sie die Weiterentwicklung unterstützen möchten:

* 🎮 **Herunterladen & Zahlen, was Sie möchten:** [AMSO auf Itch.io](https://lef97.itch.io/audio-multi-source-organizer) (fertig vorkompilierte portable Datei)
* ☕ **Direkt spenden:** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
* ⭐ **GitHub Sponsors:** [LEF97 sponsern](https://github.com/sponsors/LEF97)

---

## 📄 Lizenz

Dieses Projekt steht unter der **GNU General Public License v3.0 (GPL-3.0)** — siehe [LICENSE](LICENSE) für weitere Details.
