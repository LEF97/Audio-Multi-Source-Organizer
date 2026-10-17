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

> **AMSO** ist eine quelloffene, plattformübergreifende Desktop-Anwendung zur Vereinheitlichung, Deduplizierung und Synchronisierung hybrider Musiksammlungen über lokale Laufwerke, Cloud-Speicher (Google Drive) und Streaming-Dienste (Spotify, Deezer und Amazon Music).

---

## 📌 Funktionen & Projektstatus

| Funktion | Beschreibung | Status |
| :--- | :--- | :---: |
| **Multithread-Lokaler Scanner** | Schnelle rekursive Erkennung lokaler Audiodateien (MP3, FLAC, AAC, OGG...) | 🟢 Implementiert |
| **Metadaten- & Cover-Extraktion** | Lesen/Schreiben von ID3-Tags, Vorbis-Kommentaren und Audio-Fingerprints (`mutagen`) | 🟢 Implementiert |
| **Integrierte VLC-Audiowiedergabe** | Schlanker Audioplayer mit automatischer portabler VLC-Einrichtung und feinfühliger Lautstärkeregelung | 🟢 Implementiert |
| **Playlist- & Warteschlangenverwaltung**| Virtualisierte Warteschlange, Drag & Drop, Zufallswiedergabe (Shuffle) und Wiederholung | 🟢 Implementiert |
| **Moderne PySide6-Benutzeroberfläche** | Eleganter Dark Mode, responsiver Echtzeit-Audiovisualisierer, 5 Sprachen | 🟢 Implementiert |
| **In-App-Update-Prüfung** | Automatische und manuelle Versionsprüfung über GitHub Releases | 🟢 Implementiert |
| **Künstler- & Diskografie-Übersicht** | Eigene Ansicht pro Künstler mit Alben, Singles und Diskografie | 🟡 Geplant |
| **Grafischer Equalizer (EQ)** | Klangprofile und parametrischer Mehrband-Equalizer | 🟡 Geplant |
| **Google Drive Cloud-Konnektor** | Synchronisation entfernter Audiosammlungen über OAuth 2.0 | ⚪ Geplant |
| **Amazon Music-Konnektor** | Synchronisation entfernter Musikordner über OAuth 2.0 | ⚪ Geplant |
| **Spotify / Deezer-Integration** | Import von Wiedergabelisten und Titelabgleich | ⚪ Geplant |
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

# 3. Umgebung aktivieren
# Unter Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Unter Linux / macOS:
source .venv/bin/activate

# 4. Abhängigkeiten installieren
pip install -r requirements.txt

# Für Entwicklung und Tests:
pip install -e .[dev]

# 5. AMSO starten
python main.py
```

---

## 🧪 Tests ausführen

Die automatisierte Testsuite basiert auf `pytest`:

```bash
pytest -v
```

---

## 💖 Projekt unterstützen & Bezugsquellen

AMSO ist freie und quelloffene Software. Wenn Ihnen das Projekt gefällt:

* 🎮 **Herunterladen & Bezahlen was Sie wollen:** [AMSO auf Itch.io](https://lef97.itch.io/audio-multi-source-organizer) (vorkompilierte portable Standalone-Anwendung)
* ☕ **Direktspende:** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
* ⭐ **GitHub Sponsors:** [LEF97 sponsern](https://github.com/sponsors/LEF97)

---

## 📄 Lizenz

Dieses Projekt ist unter der **GNU General Public License v3.0 (GPL-3.0)** lizenziert — siehe [LICENSE](LICENSE).
