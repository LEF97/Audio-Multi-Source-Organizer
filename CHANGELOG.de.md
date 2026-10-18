# Änderungsprotokoll (Changelog) — AMSO

<p align="right">
  <a href="CHANGELOG.fr.md">Français</a> • <a href="CHANGELOG.md">English</a> • <a href="CHANGELOG.es.md">Español</a> • <b>Deutsch</b> • <a href="CHANGELOG.it.md">Italiano</a>
</p>

---

Alle wichtigen Änderungen am Projekt **Audio Multi-Source Organizer (AMSO)** werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/) und folgt [Semantic Versioning (SemVer)](https://semver.org/).

---

## [0.4.0-dev] - In Entwicklung

### Added
- Beginn des Entwicklungszyklus für Version 0.4.0 (Erweiterte Audio-Erfahrung, Künstler-Hub und plattformübergreifendes Packaging für Linux/macOS).

---

## [0.3.0] - 2026-10-18

### Added
- **Vollständige Unterstützung von Playlist-Dateien**:
  - Automatische Erkennung und Indizierung der Playlist-Formate `.m3u`, `.m3u8`, `.pls`, `.xspf` und `.wpl`.
  - Dedizierte Knoten im Ordnerbaum mit dem Icon **`🎶`**.
  - Strikte Einhaltung der sequenziellen Reihenfolge der Playlist (Spalte `#` mit 1, 2, 3...) ohne erzwungene alphabetische Sortierung.
  - Visuelle Erkennung fehlender oder verschobener Dateien (Warnsymbol **`⚠️`**, farbliche Hervorhebung und Tooltip), ohne das Abspielen anderer Titel zu blockieren.
  - Erweitertes Kontextmenü für Playlists: Direktes Abspielen, zur Warteschlange hinzufügen, als Nächstes abspielen und im Windows-Explorer öffnen.
- **Sanftes Audio-Fade-in**:
  - Sanfte Lautstärkeanhebung von 0 % auf den Zielwert über 1 Sekunde beim Start oder Fortsetzen der Wiedergabe (außer im Blind-Test-Modus).
- **Stabilität und flüssige Hintergrundsynchronisation**:
  - Ersetzung des blockierenden Dialogs «Scan already running» durch eine leise Hintergrund-Warteschlange.
  - Beibehaltung der Auswahl und des Zustands des Ordnerbaums ohne unnötige Neuladungen.
- **Dynamische Cover-Präsentation**:
  - Korrektur von Skalierung und Zentrierung beim Wechsel zwischen Vollbild und Fenstermodus oder freier Fenstergrößenänderung.

---

## [0.2.0] - 2026-10-18

### Added
- **Blind-Test-Modus und Spielebereich**:
  - Neues ausklappbares Menü « 🎲 SPIELE » in der Seitenleiste für das interaktive Blind-Test-Minispiel (in 5 Sprachen lokalisiert).
  - Immersives Spielerlebnis: Animierter Puls-Countdown auf verdecktem Cover, sanfte Enthüllung, automatische Rundenabfolge und asynchrone Cover-Vorladung im RAM.
- **Player-Ergonomie und Playlist-Verwaltung**:
  - Überarbeiteter Zufallsmodus (*Shuffle*): Vollständige visuelle Mischung der Warteschlange bei Erhalt des aktiven Titels, Direkt-Button « 🎲 Titel mischen » und Wiederherstellung der Ursprungsreihenfolge bei Deaktivierung.
  - Flüssiges Umsortieren per Drag & Drop in der Playlist-Tabelle ohne Wiedergabeunterbrechung.
  - Asynchrone Persistenz v2 mit kompakten SQLite-IDs zur Reduzierung des Speicherplatzbedarfs um 99 % (blockierungsfrei bei 60 FPS).
  - Lautstärkeregler in die obere Navigationsleiste integriert für eine aufgeräumte Player-Ansicht.
- **Bibliotheksverwaltung und intelligenter Papierkorb**:
  - Zwei-Stufen-Löschung: Logischer Ausschluss aus der Bibliothek (wird bei künftigen Scans gemerkt) oder physisches Löschen in den Windows-Papierkorb.
  - Dedizierte Ansicht « 🗑️ Papierkorb » mit 1-Klick-Wiederherstellung in die Datenbank.
- **Oberfläche und offizielle Links**:
  - Modernisierte « Über »-Seite in den Einstellungen mit interaktivem Spektrum und offiziellen Unterstützer-Links (Ko-fi, GitHub Sponsors, GitHub, Itch.io).
  - Vollständige Mehrsprachigkeit (Französisch, Englisch, Spanisch, Deutsch, Italienisch).

### Fixed
- **Behebung von `disk I/O error` (SQLite unter Windows)**: Einmalige Aktivierung des WAL-Modus bei der Initialisierung, `PRAGMA busy_timeout = 30000`, In-Memory-Speicherung temporärer Daten (`PRAGMA temp_store = MEMORY`) und automatischer Wiederholungsmechanismus mit exponentiellem Backoff zur Beseitigung von Dateisperren bei Multithread-Scans.
- **Unterdrückung störender modaler Warnungen bei Hintergrundsynchronisation**: Automatische Hintergrundscans öffnen bei vorübergehenden Fehlern keine blockierenden Dialogfenster mehr, sondern protokollieren Fehler sauber im Aktivitätsjournal und in der Statusleiste.
- **Zu geringe Lautstärke beim Start**: Beseitigung einer Race-Condition bei der Initialisierung der VLC-Engine und Vermeidung des automatischen Ducking durch den Windows-Audiomixer.
- **Anzeige des offiziellen Logos in der Windows-EXE**: Korrektur der Pfadauflösung für eingebettete PyInstaller-Ressourcen (`sys._MEIPASS`), damit das hochauflösende AMSO-Logo in der Seitenleiste und auf der Über-Seite anstelle des Fallback-Icons 🎵 geladen wird.
- **Optimierung der Startzeit bei großen Bibliotheken**: Beseitigung synchroner Festplattenprüfungen beim Wiederherstellen von Sitzungen, Beschleunigung des Starts auf O(1) via SQLite.
- **Flüssiger Splash-Screen**: Kontinuierliche Schritt-für-Schritt-Animation (1 % bis 100 %) ohne optischen Rücksprung der Fortschrittsanzeige.

---

## [0.1.0] - 2026-10-17

### Added
- **Integrierte VLC-Audiowiedergabe (python-vlc):**
  - Native Unterstützung für gängige Audioformate: MP3, FLAC, WAV, AAC, OGG, M4A, WMA.
  - Automatische und transparente portable VLC-Einrichtung, falls kein VLC installiert ist.
  - Vollständige Steuerung: Wiedergabe, Pause, Stopp, Nächster/Vorheriger Titel, Seekbar und Lautstärke.
  - Wiedergabemodi: Zufall (*Shuffle*) und Wiederholungsmodi.
  - Animierte Echtzeit-Visualisierungen synchron zur Musik (Partikel, Wellen, Sterne, Hyperspace, Polarlicht, Spektrumbalken).
- **Playlist- & Warteschlangenverwaltung:**
  - Virtualisierte Tabelle für zehntausende Titel ohne Latenz.
  - Intuitive Neuanordnung per Drag & Drop.
  - Vollständige Kontextmenüs und automatische Sitzungsspeicherung.
- **Leistungsstarker Multithread-Lokaler Scanner:**
  - Asynchrone rekursive Erkennung mit Echtzeit-Fortschrittsanzeige.
  - Schnelle Extraktion von Metadaten und Coverbildern via `mutagen`.
- **Moderne PySide6-Benutzeroberfläche (Dark Mode):**
  - Hochwertiges Dark-Design mit flüssigen Animationen.
  - Vollständige Mehrsprachigkeit (Französisch, Englisch, Spanisch, Deutsch, Italienisch).
  - Eigene «Über»-Seite mit Versionsstand, Spendenlinks (Ko-fi, GitHub Sponsors) und GitHub Releases Update-Prüfung.
