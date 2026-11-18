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

### 🟢 Version 0.1.0 — Die Robuste Lokale Basis

- [x] Lokaler multithreaded Scanner mit Metadaten-Extraktion (ID3, Vorbis Comments, FLAC).
- [x] Integrierter Audio-Player (python-vlc) mit automatischer Installation von portablem VLC.
- [x] Vollständige Playlist-Ansicht mit Drag-and-Drop-Neuordnung, Zufallswiedergabe und Schleifen.
- [x] Automatische Speicherung der Wiedergabesitzung (Position, Lautstärke, Liste).
- [x] Moderne Dark-Mode-Oberfläche mit reaktiven visuellen Effekten.
- [x] Vollständige Internationalisierung (FR, EN, ES, DE, IT).
- [x] Benachrichtigungs- und Update-Überprüfungssystem über GitHub Releases.

---

### 🟢 Version 0.2.0 — Blind-Test-Modus, Papierkorb & Ergonomie

- [x] **Immersiver „🎲 Spiele / Blindtest“-Modus:** Countdown mit animiertem Pulsieren, progressive Enthüllung durch sanftes Dimmen, automatisches Aneinanderreihen und dedizierte Einstellungen.
- [x] **Papierkorb- und Wiederherstellungsverwaltung:** Ausschluss von Titeln, Senden in den Windows-Papierkorb und dedizierte AMSO-Papierkorb-Ansicht mit sofortiger Wiederherstellung in der Bibliothek.
- [x] **Überarbeitung des Zufallsmodus (Shuffle) & Drag-and-Drop:** Vollständiges visuelles Mischen, umkehrbare Reihenfolge und Neuanordnung der Playlist mit der Maus.
- [x] **Performance-Optimierungen und Persistenz:** Kompaktes asynchrones Backup-Format (-99 % Festplattenspeicher) und Eliminierung von Startlatenzen.
- [x] **Ergonomie des Players & Navigation:** Neue „Spiele“-Schublade, Lautstärkeregler integriert im Player-Header, Standardstart im Player.

---

### 🟢 Version 0.3.0 — Support für Playlists, Audio-Fade & Robustheit

- [x] **Vollständige Unterstützung von Playlists:** Automatische Indizierung der Formate `.m3u`, `.m3u8`, `.pls`, `.xspf`, `.wpl` in der Ordneransicht mit dem Icon `🎶`.
- [x] **Sequenzielle Reihenfolge und Verwaltung fehlender Titel:** Beibehaltung der ursprünglichen Reihenfolge der Playlist und visuelle Erkennung fehlender Dateien (`⚠️`) ohne Unterbrechung der Wiedergabe.
- [x] **Akustisches Sound-Fade (*Fade-in*) :** Progressives Ansteigen der Lautstärke über 1 Sekunde beim Starten und Wiederaufnehmen einer Audio-Wiedergabe.
- [x] **Flüssigkeit der Synchronisierung :** Kontinuierlicher Hintergrund-Warteschlange ohne störende Pop-ups und Erhaltung der Verzeichnisstruktur.
- [x] **Dynamische Anpassung der Cover :** Flüssige Neuzentrierung und Dimensionierung beim Wechsel zwischen Vollbild / Fenster.

---

### 🟢 Version 0.4.0 — Erweiterte Audioerfahrung & CUE-Blätter

- [x] **Modulare Architektur-Überarbeitung & Quality Gate:** Aufteilung der Anwendung in kohäsive Module (< 500 Zeilen), Modularisierung von MainWindow in dedizierte Mixins (amso/ui/pages/), Zerlegung des Audio-Service in unabhängige Untersysteme (player_transport, player_queue, player_transitions) und Implementierung eines automatisierten Validierungs-Harnußes (scripts/verify.py & .bat: ruff, mypy, pytest, Größenkontrolle).
- [x] **Windows Shell- & Taskleisten-Integration:** Native Verankerung direkt vom aktiven Icon (AppUserModelID explizit LEF97.AMSO.AudioPlayer) ab dem Einstiegspunkt main.py und Persistenz des Shortcuts bei Updates.
- [x] **Perfektes Gapless-Abspielen 0 zwischen Tracks:** Zwei Engines sind nun verfügbar, eine basiert auf VLC_direct, die andere arbeitet im Puffer-Modus (bevorzugter Betrieb). Diese Modi ermöglichen ein flüssiges Abspielen von Alben mit verbundenen Tracks (Alan Parsons, Pink Floyd, Mike Oldfield, etc...)
- [x] **Unterstützung von CUE-Sheets (`.cue`):** Eine `.cue`-Datei wird als Verzeichnis virtueller Tracks (💿) mit deren Dauer angezeigt und wird wie echte Tracks abgespielt (kontinuierlicher Puffer-Engine).

---

### 🟢 Version 0.4.1 — Audio-Zuverlässigkeit, übersetztes Protokoll & experimentelle Linux / macOS Versionen

- [x] **Audioausgabe unabhängig vom Interface-Thread:** Der `QAudioSink` des `buffer`-Motors wird von einem dedizierten Audiothread (Pull-Modus) gespeist; das Verschieben oder Neugrößenanpassen des Fensters beeinflusst den Ton nicht mehr.
- [x] **Blindtest im `buffer`-Motor:** Abspielen, Nächster und Vorheriger starten den Ton, ohne erneut auf Abspielen zu klicken.
- [x] **Übersetzungen abgeschlossen:** Aktivitätsprotokoll gespeichert als Schlüssel + Parameter und übersetzt zur Anzeige, hartcodierte Texte konvertiert, Rückfall auf Französisch, Steuerung der Marker `{nom}` bei der Synchronisation.
- [x] **libVLC Status:** Version und Herkunft (AMSO-Kopie oder VLC des Systems) in den Player-Einstellungen.
- [x] **Multiplattform-Deployment (Linux & macOS), experimentelle, nicht getestete Version:** Automatisches Packaging über GitHub Actions für Linux (.AppImage / .tar.gz) und macOS Apple Silicon ARM & Intel (.dmg nicht signiert), VLC erforderlich; die Tester senden `startup.log` und `crash.log` zurück.

---

### 🟢 Version 0.5.0 — Quellen & Bibliothek, Playlist-Editor & Übergänge *(Aktuell)*

- [x] **Ansicht „Quellen & Bibliothek“:** einheitliches Dashboard mit Gesundheitsstatus der Quellen/Playlists, Navigation nach Quelle und Schnellaktionen.
- [x] **Editor, Reparatur und Export von Playlists:** Neuorganisation, manuelle oder automatische Neulokalisierung (lokal + Datenbank) und Speichern in `.m3u`, `.m3u8`, `.pls`, `.xspf` oder `.wpl`.
- [x] **Playlists im Album-Modus:** Gruppierung von Titeln einer Playlist in virtuelle Ordner nach Album in der Verzeichnisstruktur, mit „(unbekanntes Album)“ für Titel ohne Album.
- [x] **Cover-Übergänge, 3-Phasen-Scan & Fenstergeometrie:** 5 Übergangseffekte, detaillierter Scan-Fortschritt und Fensterwiederherstellung.
- [x] **Neues AMSO-Icon:** hochauflösendes Multi-Größen-Icon (PNG, ICO, ICNS).
- [x] **Audio-Tools:** 10-Band-Grafik-Equalizer mit Presets, ReplayGain-Normalisierung, Wiedergabegeschwindigkeit, Auswahl der Audioausgabe und Abschalt-Timer (Motor `buffer`).
- [x] **Kontinuierliches Verknüpfen von CUE-Tracks:** benachbarte Tracks aus derselben Datei werden in einen einzigen Stream dekodiert (Motor `buffer`).
- [x] **Hilfeführer, Sound- und Effektseiten, Warp Pilot Effekt & Zufallsmodus:** Kontextuelle Hilfe auf jeder Seite, dedizierte Einstellungen für Sound und visuelle Effekte.
- [x] **Windows-Integration:** Taskleiste und Icon im Benachrichtigungsbereich.
- [x] **Parametrisierbarer Crossfade & Erweiterte Audio-Verknüpfungen:** Unterstützung für nahtlose Übergänge (Gapless 0 ms), hochpräzisen Crossfade (Crossfade Equal-Power) und Standardmodus ohne Stille.

---

### 🌟 Version x.0.0 — Intelligente Deduplizierung & Stabile Version

- [ ] **Akustische Fingerabdruckerkennung (Audio Fingerprinting) :** Identifizierung von Duplikaten, selbst bei fehlerhaften Tags oder neu kodierten Dateien.
- [ ] **Assistent zur Duplikatauflösung :** Intelligenter Qualitätsvergleich (automatische Auswahl des besten Bitrates / lossless) mit sicherer Archivierung.
- [ ] **Offizielles Multiplattform-Packaging :** Signierte ausführbare Dateien für Windows (`.exe` / portable), macOS (`.dmg` Apple Silicon & Intel) und Linux (`AppImage` / `.deb`).
- [ ] **Umfassende Benutzerdokumentation :** Illustrierter Schritt-für-Schritt-Leitfaden und GitHub Pages Showcase-Website.
- [ ] **Spotify-Connector (Web API) :** Verbindung des Benutzerkontos und Abrufen von Playlists und Favoriten.
- [ ] **Amazon Music-Connector :** Scan, Streaming und Synchronisierung entfernter Musiksammlungen (OAuth 2.0).
- [ ] **Intelligentes Hybrid-Matching :** Abgleich zwischen Titeln einer entfernten Playlist und lokal vorhandenen Dateien (hohe Treue).
- [ ] **Einheitliche Ansicht :** Nebeneinanderanzeige von lokal verfügbaren und nur im Streaming verfügbaren Tracks.
- [ ] **Sichere OAuth 2.0 Authentifizierung:** Vereinfachte Anmeldung über den Browser ohne Speicherung von Geheimnissen im Klartext.
- [ ] **Remote-Scan von Google Drive Ordnern:** Indizierung der in den konfigurierten Ordnern vorhandenen Audiodateien.
- [ ] **Direktes Cloud-Streaming-Abspielen:** Hören von entfernten Tracks mit transparenter lokaler Zwischenspeicherung.
- [ ] **Selektive bidirektionale Synchronisierung:** Lokaler Download von Cloud-Tracks oder Backup lokaler Tracks nach Drive.
- [ ] **Verwaltung von Künstlern und zugehöriger Diskografie:** Dedizierte Ansicht pro Künstler mit Alben, Singles und vollständiger Diskografie.
- [ ] **In-App-Metadaten-Editor:** Direkte Bearbeitung der ID3 / Vorbis Tags an einem oder mehreren ausgewählten Dateien.
- [ ] **Automatischer Download von Covern:** Online-Suche (MusicBrainz / Cover Art Archive) nach fehlenden Covern.
- [ ] **Erweiterte Suchfilter:** Kombinierte Filterung nach Genre, Jahr, Bitrate und verlustfreiem Format (Lossless).
- [ ] **Erkennung von Netzwerk-Mounts (Linux & macOS):** `amso/core/network_paths.py` erkennt heute nur UNC-Pfade und gemappte Windows-Laufwerke; Erkennung von NFS / SMB / AFP-Mounts (`/proc/self/mountinfo`, `statfs`) ist erforderlich, um blockierendes Festplatten-Probing beim Start auf diesen Systemen zu vermeiden.
- [ ] **Validierung unter Linux und macOS:** Motor `buffer`, Übergänge und Packaging müssen anhand des Feedbacks der Tester auf echten Systemen bestätigt werden.

---

## 💡 Eine Funktion vorschlagen

Eine Idee oder ein spezifischer Bedarf?

- Eröffnen Sie eine Diskussion oder ein Ticket auf [GitHub Issues](https://github.com/LEF97/Audio-Multi-Source-Organizer/issues) unter Verwendung der Vorlage *Feature Request*.
- Nehmen Sie an den Community-Abstimmungen teil, um die Entwicklungen zu priorisieren!
