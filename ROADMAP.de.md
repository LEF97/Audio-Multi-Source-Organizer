# Roadmap — AMSO

<p align="right">
  <a href="ROADMAP.fr.md">Français</a> • <a href="ROADMAP.md">English</a> • <a href="ROADMAP.es.md">Español</a> • <b>Deutsch</b> • <a href="ROADMAP.it.md">Italiano</a>
</p>

---

Dieses Dokument beschreibt die strategische Ausrichtung, geplante Funktionen und zukünftige Meilensteine des Projekts **Audio Multi-Source Organizer (AMSO)**.

---

## 🎯 Projektvision

AMSO versteht sich als **universeller und dezentraler Musik-Hub**: schnell, ressourcenschonend, elegant und ohne Kompromisse beim Datenschutz. AMSO gibt Ihnen die volle Kontrolle über Ihre Musiksammlung – ob lokal auf der Festplatte gespeichert, in der Cloud archiviert oder über Streaming-Dienste abgespielt.

---

## 🗺️ Meilensteine & Versionen

### 🟢 Version 0.1.0 — Das Robuste Lokale Fundament
- [x] Leistungsstarker Multithread-Lokaler Scanner mit Metadaten-Extraktion (ID3, Vorbis Comments, FLAC).
- [x] Integrierte Audiowiedergabe (python-vlc) mit automatischer portabler VLC-Einrichtung.
- [x] Vollwertige Playlist-Ansicht mit Drag-and-Drop-Sortierung, Zufallswiedergabe (Shuffle) und Wiederholungsmodi.
- [x] Automatische Sitzungsspeicherung (Titelposition, Lautstärke, aktive Warteschlange).
- [x] Moderne Benutzeroberfläche im Dark Mode mit reaktiven Audio-Visualisierungen.
- [x] Vollständige Internationalisierung (FR, EN, ES, DE, IT).
- [x] Benachrichtigungssystem und Update-Prüfung über GitHub Releases.

---

### 🟢 Version 0.2.0 — Blind-Test-Modus, Papierkorb & Ergonomie
- [x] **Immersiver « 🎲 Spiele / Blind-Test »-Modus:** Animierter Countdown mit Puls-Effekt, sanfte Einblendung des Covers, automatische Rundenabfolge und dedizierte Audio-Einstellungen.
- [x] **Papierkorb-Verwaltung & Wiederherstellung:** Titel ausschließen, in den Windows-Papierkorb verschieben und eigene AMSO-Papierkorb-Ansicht mit 1-Klick-Wiederherstellung.
- [x] **Überarbeiteter Zufallsmodus (Shuffle) & Drag & Drop:** Vollständige visuelle Mischung, reversible Original-Reihenfolge und flüssiges Verschieben per Maus.
- [x] **Performance-Optimierungen & Persistenz v2:** Kompaktes asynchrones SQLite-Format (-99 % Speicherplatzbedarf) und Beseitigung jeglicher Startverzögerung.
- [x] **Player-Ergonomie & Navigation:** Neues « Spiele »-Menü in der Seitenleiste, Lautstärkeregler in der Kopfzeile und direkter Start auf dem Player.

---

### 🟢 Version 0.3.0 — Volle Playlist-Unterstützung, Audio-Fade-in & Robustheit *(Aktuell)*
- [x] **Vollständige Unterstützung von Playlist-Dateien:** Automatische Indizierung von `.m3u`, `.m3u8`, `.pls`, `.xspf`, `.wpl` in der Ordneransicht mit `🎶`-Icon.
- [x] **Sequenzielle Reihenfolge & Erkennung fehlender Titel:** Exakte Einhaltung der Playlist-Reihenfolge (`#`-Spalte) und visuelle Warnung (`⚠️`) ohne Unterbrechung der Wiedergabe.
- [x] **Sanftes Audio-Fade-in:** Sanfte Lautstärkeerhöhung über 1 Sekunde ab 0 % beim Starten oder Fortsetzen der Wiedergabe.
- [x] **Reibungslose Hintergrundsynchronisation:** Leise Hintergrundwarteschlange ohne störende Dialoge und Beibehaltung des Ordnerbaums.
- [x] **Dynamische Cover-Anpassung:** Flüssiges Zentrieren und Skalieren beim Wechsel zwischen Vollbild und Fenstermodus.

---

### 🟡 Version 0.4.0 — Erweiterte Audio-Erfahrung, Künstler & Plattformübergreifendes Packaging
- [ ] **Automatisiertes Cross-Platform Deployment (Linux & macOS):** Native Kompilierung und automatisiertes Packaging über GitHub Actions für Linux (`.AppImage` / `.tar.gz`) und macOS Apple Silicon ARM & Intel (`.dmg`), ergänzend zur Windows-EXE.
- [ ] **Künstler-Hub & Diskografie-Ansicht:** Dedizierte Ansicht nach Künstlern mit Alben, Singles und kompletter Diskografie.
- [ ] **Grafischer Equalizer (EQ):** Klangprofile (Rock, Pop, Jazz, Bass Boost) und parametrischer Mehrband-Equalizer.
- [ ] **In-App Metadaten-Editor:** Direktes Bearbeiten von ID3- und Vorbis-Tags einzelner oder mehrerer Titel.
- [ ] **Automatischer Cover-Download:** Online-Suche (MusicBrainz / Cover Art Archive) nach fehlenden Album-Covern.
- [ ] **Erweiterte Suchfilter:** Kombinierte Filter nach Genre, Erscheinungsjahr, Bitrate und verlustfreien Formaten (Lossless).
- [ ] **Konfigurierbares Crossfade:** Anpassbare weiche Überblendungen zwischen Titeln.

---

### 🔵 Version 0.5.0 — Google Drive Cloud-Konnektor
- [ ] **Sichere OAuth 2.0 Authentifizierung:** Nahtlose Browser-Anmeldung ohne Speicherung von Klartext-Zugangsdaten.
- [ ] **Entferntes Google Drive Scannen:** Rekursive Erkennung und Indizierung von Audiodateien in ausgewählten Drive-Ordnern.
- [ ] **Direktes Cloud-Streaming:** Wiedergabe entfernter Audiodateien mit transparentem lokalem Caching.
- [ ] **Selektive Zwei-Wege-Synchronisation:** Lokaler Download von Cloud-Titeln oder Hochladen lokaler Tracks auf Google Drive.

---

### 🟣 Version 0.6.0 — Streaming-Integrationen (Spotify, Deezer & Amazon Music)
- [ ] **Spotify-Konnektor (Web API):** Verbindung des Benutzerkontos zum Import von Playlists und Favoriten.
- [ ] **Amazon Music-Konnektor:** Durchsuchen, Streamen und Synchronisieren entfernter Musiksammlungen (OAuth 2.0).
- [ ] **Intelligenter Hybrid-Abgleich:** Automatischer Abgleich von Playlist-Titeln mit hochauflösenden lokalen Dateien.
- [ ] **Einheitliche Sammlungsansicht:** Parallele Anzeige lokaler Dateien und reiner Streaming-Titel.

---

### 🌟 Version 1.0.0 — Intelligente Deduplizierung & Stabile Version
- [ ] **Akustischer Fingerabdruck (Audio Fingerprinting):** Zuverlässige Duplikaterkennung trotz fehlerhafter Tags oder Re-Encodings.
- [ ] **Assistent zur Duplikatbereinigung:** Intelligenter Qualitätsvergleich (automatische Auswahl der besten Bitrate/Lossless-Quelle) mit sicherem Archivieren.
- [ ] **Offizielle plattformübergreifende Installationspakete:** Signierte Pakete für Windows (`.exe` / portabel), macOS (`.dmg` Apple Silicon & Intel) und Linux (`AppImage` / `.deb`).
- [ ] **Umfassende Benutzerdokumentation:** Bebilderte Schritt-für-Schritt-Anleitung und GitHub Pages Website.

---

## 💡 Funktion vorschlagen

Haben Sie eine Idee oder einen konkreten Wunsch?
- Eröffnen Sie eine Diskussion oder ein Ticket auf [GitHub Issues](https://github.com/LEF97/Audio-Multi-Source-Organizer/issues) mit der Vorlage *Feature Request*.
- Stimmen Sie für Community-Vorschläge ab, um die Entwicklungsschwerpunkte mitzugestalten!
