# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <b>Deutsch</b> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](CHANGELOG.de.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](ROADMAP.de.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) ist ein modernes, responsives und plattformübergreifendes Desktop-Audioplayer (Windows, Linux, macOS). Entwickelt, um Audiophilen eine vollständige Kontrolle über ihre lokale Musikbibliothek (MP3, FLAC, OGG…) zu bieten, unterstützt es nun Wiedergabelisten (M3U, PLS, XSPF, WPL), CUE-Dateien (Alben in einer Datei aufgeteilt in Tracks) und integriert einen brandneuen Audio-Blind-Test-Modus! Das Projekt entwickelt sich zu einem zentralen Kommandozentrum, das in der Lage ist, hybride Musiksammlungen zu organisieren, Duplikate zu entfernen und zu synchronisieren, die auf lokale Festplatten, Cloud-Speicher (Google Drive) und Streaming-Dienste (Spotify, Deezer, Amazon Music) verteilt sind.

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

## 📌 Funktionen & Status des Projekts

| Funktionalität | Beschreibung | Status |
| :--- | :--- | :---: |
| **Audio-Wiedergabemotor** | Leichter, eigenständiger Audio-Player (VLC portable wird automatisch unter Windows installiert). Zwei Motoren zur Auswahl: direkte VLC-Ausgabe oder ein kontinuierlicher Puffermotor für einen nahtlosen Übergang zwischen zwei Tracks (Gapless 0 ms, sanfter Übergang bei gleicher Lautstärke, ohne Unterbrechung der Audioausgabe) | 🟢 Implementiert |
| **Bibliotheksverwaltung** | Multithread-Rekursiv-Scan lokaler Ordner (MP3, FLAC, AAC, OGG...), manuelle, geplante oder Echtzeit-Synchronisierung, Papierkorb und Bibliotheksstatistiken | 🟢 Implementiert |
| **Metadaten-Extraktion** | ID3-, Vorbis Comments-Lese-/Schreibzugriff und Berechnung des Audio-Fingerabdrucks (`mutagen`) | 🟢 Implementiert |
| **Unterstützung von Playlists (M3U, PLS, XSPF, WPL) & CUE-Dateien** | Baumartige Indizierung (🎶), sequenzieller Abspielordner, visuelle Erkennung fehlender Tracks; .cue-Dateien (💿) öffnen sich wie ein virtueller Trackordner mit ihrer Dauer und werden wie echte Tracks abgespielt | 🟢 Implementiert |
| **Playlist-Manager & Drag-and-Drop** | Virtualisierte Warteschlange, flüssiges Drag & Drop, umkehrbares Zufallsprinzip (shuffle) und Schleifen | 🟢 Implementiert |
| **Interaktiver „🎲 Blind Test“-Modus** | Immersives Musikspiel mit animiertem Countdown, Sound-Fade, sanfter Enthüllung und automatischer Abfolge | 🟢 Implementiert |
| **In-App-Updates** | Automatische/Manuelle Versionsprüfung über GitHub Releases | 🟢 Implementiert |
| **Versions Linux & macOS** | Pakete .AppImage / .tar.gz (Linux) und nicht signiertes .dmg (macOS), VLC erforderlich | 🟡 Experimentell (nicht getestet) |
| **Künstler- & Diskographieverwaltung** | Dedizierte Ansicht pro Künstler mit Alben, Singles und vollständiger Diskographie | 🟡 Geplant |
| **Graphischer Equalizer (EQ)** | Audio-Presets und parametrisierter Multiband-Equalizer | 🟡 Geplant |
| **Google Drive-Konnektor** | Scan und Synchronisierung von entfernten Audio-Sammlungen via OAuth 2.0 | ⚪ Geplant |
| **Amazon Music-Konnektor** | Scan und Synchronisierung von entfernten Sammlungen via OAuth 2.0 | ⚪ Geplant |
| **Spotify / Deezer-Konnektor** | Import von Playlists und Titelabgleich | ⚪ Geplant |
| **Intelligente Duplikaterkennung** | Duplikaterkennung (verschwommene Titel/Künstler + akustische Fingerabdrücke) | ⚪ Geplant |

> 💡 *Um die Details der geplanten Meilensteine und Versionen einzusehen, verweisen Sie auf die [Feuille de route (Roadmap)](ROADMAP.de.md).*

---

## 📌 Verfügbare Sprachen

Englisch, Französisch, Spanisch, Deutsch, Italienisch, Portugiesisch, Japanisch, Russisch, Polnisch, Türkisch, Niederländisch, Schwedisch, Indonesisch, Bulgarisch, Serbisch, Weißrussisch, Griechisch, Katalanisch, Baskisch, Galicisch, Tschechisch, Slowakisch, Ungarisch, Kroatisch, Slowenisch, Bosnisch, Estnisch, Lettisch, Litauisch, Norwegisch, Dänisch, Finnisch, Isländisch, Malaiisch, Tagalogisch, Swahilisch, Esperanto, Vereinfachtes Chinesisch, Traditionelles Chinesisch, Koreanisch, Arabisch, Hebräisch, Vietnamesisch

---

## 🚀 Schneller Start

### Voraussetzungen

- **Python 3.11** oder höher installiert
- Git

### Installation

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

## 🐧🍎 Linux und macOS : experimentelle Versionen (nicht getestet)

Die Linux-Pakete (`.AppImage` / `.tar.gz`) und macOS (`.dmg`) werden **ohne Testung** geliefert: AMSO wurde nur unter Windows validiert. Der kontinuierliche Puffer-Audiotreiber (`buffer`) wurde insbesondere auf diesen Systemen nicht überprüft. Ihr Feedback ist wertvoll.

- **VLC ist erforderlich** (AMSO lädt es nur unter Windows herunter) :
  - Linux : `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) oder `sudo pacman -S vlc` (Arch).
  - macOS : **VLC.app** von [videolan.org](https://www.videolan.org/vlc/) im Ordner Anwendungen installieren.
- **Linux, Systembibliotheken** : Die Qt-Schnittstelle erfordert unter anderem `libpulse0` (Audio), `libxcb-cursor0` und `libxkbcommon-x11-0` (zum Beispiel `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, nicht signifiziertes \`.dmg\`** : Beim ersten Start mit der rechten Maustaste auf AMSO klicken und dann **Öffnen**, oder `xattr -dr com.apple.quarantine /Applications/AMSO.app` ausführen.
- **Linux, AppImage** : Es mit `chmod +x AMSO*.AppImage` ausführbar machen.
- **Bei Problemen**, senden Sie bitte die Dateien `startup.log` und `crash.log` (falls vorhanden), die sich im Datenverzeichnis befinden: `~/Library/Application Support/AMSO/` unter macOS, `~/.local/share/AMSO/` unter Linux. Geben Sie Ihr System und die VLC-Version an.

---

## 🧪 Start der Tests

Das Projekt verwendet `pytest` mit einer Suite von Unit- und Integrationstests:

```bash
pytest -v
```

Die Tests werden automatisch auf **Windows, macOS und Ubuntu** bei jedem Push über GitHub Actions ausgeführt.

---

## 🔒 Sicherheit & API-Schlüssel

- **Commit niemals echte API-Schlüssel oder Authentifizierungstoken.**
- Die Datei `.gitignore` ist vorab konfiguriert, um `.env`, `credentials.json`, `token.json` und alle lokalen SQLite-Datenbanken zu blockieren.
- Verwenden Sie `.env.example` als Vorlage für Ihre Entwicklungsumgebung.

---

## 📋 Dokumentation & Projektüberwachung

- 📜 **[CHANGELOG.fr.md](CHANGELOG.de.md)** : Detailliertes Protokoll der Versionen, neuen Funktionen und Fehlerbehebungen.
- 🗺️ **[ROADMAP.fr.md](ROADMAP.de.md)** : Roadmap zukünftiger Meilensteine (Künstler, Cloud, Spotify, Deduplizierung).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Charta für die Softwarearchitektur und Regeln für die Codequalität.

---

## 💖 Projekt unterstützen & Distribution

AMSO ist eine freie und kostenlose Software (open source). Wenn Ihnen die Anwendung gefällt und Sie die Entwicklung unterstützen möchten:

- 🎮 **Download & Pay What You Want :** [Itch.io Seite von AMSO](https://lef97.itch.io/audio-multi-source-organizer) (fertige, vorinstallierte ausführbare Datei)
- ☕ **Direkte Spende :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [LEF97 unterstützen](https://github.com/sponsors/LEF97)

---

## 📄 Lizenz

Dieses Projekt steht unter der Lizenz **GNU General Public License v3.0 (GPL-3.0)** — siehe die Datei [LICENSE](../../LICENSE) für weitere Details.
