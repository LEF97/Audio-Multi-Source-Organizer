# Änderungsprotokoll (Changelog) — AMSO

<p align="right">
  <a href="CHANGELOG.fr.md">Français</a> • <a href="CHANGELOG.md">English</a> • <a href="CHANGELOG.es.md">Español</a> • <b>Deutsch</b> • <a href="CHANGELOG.it.md">Italiano</a>
</p>

---

Alle wichtigen Änderungen am Projekt **Audio Multi-Source Organizer (AMSO)** werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/) und folgt [Semantic Versioning (SemVer)](https://semver.org/).

---

## [Unreleased]

### Demnächst (Geplant)
- Künstlerverwaltung und zugehörige Diskografie.
- Amazon Music-Konnektor für Cloud-Scan und -Synchronisierung (OAuth 2.0).
- Google Drive-Konnektor für Cloud-Scan und -Synchronisierung (OAuth 2.0).
- Spotify-Integration für Playlist-Import und Hybrid-Abgleich.
- Grafischer 10-Band-Equalizer im Audioplayer.
- Intelligentes Deduplizierungsmodul (akustischer Fingerabdruck & unscharfe Ähnlichkeit).

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
