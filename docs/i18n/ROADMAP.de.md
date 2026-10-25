# Roadmap (Roadmap) — AMSO

<p align="right">
  <a href="../../ROADMAP.fr.md">Français</a> • <a href="../../ROADMAP.md">English</a> • <a href="ROADMAP.es.md">Español</a> • <b>Deutsch</b> • <a href="ROADMAP.it.md">Italiano</a>
</p>

---

Dieses Dokument beschreibt die strategischen Richtlinien, die geplanten Funktionen und die zukünftigen Meilensteine des Projekts **Audio Multi-Source Organizer (AMSO)**.

---

## 🎯 Vision des Projekts

AMSO ist bestrebt, das **universelle und dezentrale Musik-Hub** der Wahl zu werden: eine schnelle, leichte, elegante und datenschutzfreundliche Anwendung, die es jedem ermöglicht, seine Audio-Sammlung zu verwalten, egal ob sie auf einer Festplatte gespeichert, in der Cloud archiviert oder über Streaming-Dienste abgerufen wird.

---

## 🗺️ Meilensteine und Versionen

### 🟢 Version 0.1.0 — Die robuste lokale Basis
- [x] Multithread-Scanner mit Metadaten-Extraktion (ID3, Vorbis Comments, FLAC).
- [x] Integrierter Audio-Player (python-vlc) mit automatischer Installation von VLC portable.
- [x] Vollständige Playlist-Ansicht mit Drag-and-Drop-Neuordnung, Zufallswiedergabe und Schleifen.
- [x] Automatische Sicherung der Wiedergabesitzung (position, volume, liste).
- [x] Moderne Benutzeroberfläche im Dark Mode mit reaktiven visuellen Effekten.
- [x] Vollständige Internationalisierung (FR, EN, ES, DE, IT).
- [x] Benachrichtigungs- und Update-Überprüfungssystem über GitHub Releases.

---

### 🟢 Version 0.2.0 — Blindtest-Modus, Papierkorb & Ergonomie
- [x] **Immersiver Modus « 🎲 Spiele / Blind Test »:** Countdown mit animiertem Pulsieren, progressive Enthüllung durch sanftes Dimmen, automatisches Aneinanderreihen und dedizierte Einstellungen.
- [x] **Papierkorb- und Wiederherstellungsverwaltung:** Ausschluss von Titeln, Senden in den Windows-Papierkorb und dedizierte AMSO-Papierkorb-Ansicht mit sofortiger Wiederherstellung in der Bibliothek.
- [x] **Überarbeitung des Zufallsmodus (Shuffle) & Drag-and-Drop:** Vollständiges visuelles Mischen, umkehrbare Reihenfolge und Neuanordnung der Playlist mit der Maus.
- [x] **Performance- und Persistenzoptimierungen:** Komprimiertes asynchrones Backup-Format (-99 % Festplattenspeicher) und Eliminierung von Startverzögerungen.
- [x] **Player-Ergonomie & Navigation:** Neue „Spiele“-Schublade, integrierter Lautstärkeregler im Player-Header, Standardstart im Player.

---

### 🟢 Version 0.3.0 — Playlist-Unterstützung, Audio-Fade & Robustheit
- [x] **Volle Playlist-Unterstützung:** Automatische Indizierung der Formate `.m3u`, `.m3u8`, `.pls`, `.xspf`, `.wpl` in der Ordneransicht mit dem Icon `🎶`.
- [x] **Sequenzielle Reihenfolge und Umgang mit fehlenden Titeln:** Beibehaltung der ursprünglichen Reihenfolge der Playlist und visuelle Erkennung fehlender Dateien (`⚠️`) ohne Unterbrechung der Wiedergabe.
- [x] **Akustisches Sound-Fade (*Fade-in*) :** Progressiver Anstieg der Lautstärke über 1 Sekunde beim Start und beim Fortsetzen einer Audio-Wiedergabe.
- [x] **Flüssige Synchronisation:** Kontinuierliche Warteschlange im Hintergrund ohne störende Pop-ups und Beibehaltung der Verzeichnisstruktur.
- [x] **Dynamische Anpassung der Cover:** Fließendes Neuzentrieren und Skalieren beim Wechsel zwischen Vollbild / Fenster-Modus.

---

### 🟢 Version 0.4.0 — Erweiterte Audio-Erfahrung & CUE-Sheets *(Aktuell)*
- [x] **Modulare Neugestaltung der Architektur & Quality Gate:** Aufteilung der Anwendung in kohäsive Module (< 500 Zeilen), Modularisierung von MainWindow in dedizierte Mixins (amso/ui/pages/), Zerlegung des Audio-Dienstes in unabhängige Subsysteme (player_transport, player_queue, player_transitions) und Einrichtung eines automatisierten Validierungs-Frameworks (scripts/verify.py & .bat : ruff, mypy, pytest, Größenkontrolle).
- [x] **Integration der Windows Shell & Taskleiste:** Natives Anheften direkt von dem aktiven Icon (AppUserModelID explizit LEF97.AMSO.AudioPlayer) ab dem Einstiegspunkt main.py und Persistenz des Shortcuts bei Updates.
- [x] **Perfektes Gapless 0 Abspielen zwischen zwei Tracks:** Es stehen nun zwei Engines zur Verfügung, eine basiert auf VLC_direct, die andere arbeitet im Puffer-Modus (bevorzugter Betrieb). Diese Modi ermöglichen ein flüssiges Abspielen von Alben mit verbundenen Tracks (Alan Parsons, Pink Floyd, Mike Oldfield, etc...)
- [x] **Unterstützung von CUE-Sheets (`.cue`) :** Eine `.cue`-Datei wird als Verzeichnis virtueller Tracks (💿) mit deren Dauer angezeigt und wird wie echte Tracks abgespielt (kontinuierlicher Puffer-Engine).

---

### 🔵 Version 0.4.1 — Packaging Linux & macOS
- [ ] **Automatisierte Multiplattform-Bereitstellung (Linux & macOS) :** Native Kompilierung und automatisierte Verpackung über GitHub Actions für Linux (.AppImage / .tar.gz) und macOS Apple Silicon ARM & Intel (.dmg), ergänzend zum Windows-Executable.

---

### 🌟 Version x.0.0 — Intelligente Deduplizierung & Stabile Version
- [ ] **Akustische Fingerabdruckerkennung (Audio Fingerprinting):** Identifizierung von Duplikaten auch bei falschen Tags oder neu kodierten Dateien.
- [ ] **Assistent zur Duplikatlösung:** Intelligenter Qualitätsvergleich (automatische Auswahl des besten Bitrates / lossless) mit sicherer Archivierung.
- [ ] **Offizielles Multiplattform-Packaging:** Signierte ausführbare Dateien für Windows (`.exe` / portable), macOS (`.dmg` Apple Silicon & Intel) und Linux (`AppImage` / `.deb`).
- [ ] **Umfassende Benutzerdokumentation:** Illustrierter Schritt-für-Schritt-Guide und GitHub Pages Showcase-Website.
- [ ] **Spotify Connector (Web API):** Verbindung des Benutzerkontos und Abruf von Playlists und Favoriten.
- [ ] **Amazon Music Connector:** Scan, Streaming und Synchronisierung externer Musiksammlungen (OAuth 2.0).
- [ ] **Intelligentes Hybrid-Matching:** Abgleich zwischen Titeln einer externen Playlist und lokal vorhandenen Dateien (hohe Treue).
- [ ] **Einheitliche Ansicht:** Nebenläufige Anzeige lokaler und rein streambarer Titel.
- [ ] **Sichere OAuth 2.0 Authentifizierung:** Vereinfachte Anmeldung über den Browser ohne Speicherung von Geheimnissen im Klartext.
- [ ] **Fern-Scan von Google Drive Ordnern:** Indizierung der in den konfigurierten Ordnern vorhandenen Audiodateien.
- [ ] **Direktes Cloud-Streaming:** Hören von entfernten Titeln mit transparentem lokalem Caching.
- [ ] **Selektive bidirektionale Synchronisierung:** Lokaler Download von Cloud-Titeln oder Backup lokaler Titel zu Drive.
- [ ] **Künstler- und Diskografieverwaltung:** Dedizierte Ansicht pro Künstler mit Alben, Singles und vollständiger Diskografie.
- [ ] **Grafischer Equalizer (EQ):** Presets (Rock, Pop, Jazz, Bass Boost) und multiband-parametrischer Equalizer.
- [ ] **In-App-Metadaten-Editor:** Direkte Bearbeitung der ID3/Vorbis-Tags an einem oder mehreren ausgewählten Dateien.
- [ ] **Automatischer Download von Covern:** Online-Suche (MusicBrainz / Cover Art Archive) nach fehlenden Covern.
- [ ] **Erweiterte Suchfilter:** Kombinierte Filterung nach Genre, Jahr, Bitrate und verlustfreiem Format (Lossless).
- [x] **Einstellbarer Crossfade & Erweiterte Audio-Sequenzen:** Unterstützung für nahtlose Übergänge (Gapless 0 ms), hochpräzisen Crossfade (Crossfade Equal-Power) und Standardmodus ohne Stille.

---

## 💡 Eine Funktion vorschlagen

Eine spezifische Idee oder ein Bedarf?
- Öffnen Sie eine Diskussion oder ein Ticket auf [GitHub Issues](https://github.com/LEF97/Audio-Multi-Source-Organizer/issues) unter Verwendung der Vorlage *Feature Request*.
- Nehmen Sie an den Community-Abstimmungen teil, um die Entwicklungen zu priorisieren!
