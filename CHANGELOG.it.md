# Registro delle modifiche (Changelog) — AMSO

<p align="right">
  <a href="CHANGELOG.fr.md">Français</a> • <a href="CHANGELOG.md">English</a> • <a href="CHANGELOG.es.md">Español</a> • <a href="CHANGELOG.de.md">Deutsch</a> • <b>Italiano</b>
</p>

---

Tutte le modifiche rilevanti apportate al progetto **Audio Multi-Source Organizer (AMSO)** sono documentate in questo file.

Il formato si basa su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/) e aderisce a [Semantic Versioning (SemVer)](https://semver.org/).

---

## [0.2.0-dev] - In sviluppo

### In corso / Pianificato
- Consultare la [Tabella di marcia (ROADMAP.it.md)](ROADMAP.it.md) per i dettagli delle tappe e funzionalità per la v0.2.0.

---

## [0.1.0] - 2026-10-17

### Added
- **Motore di riproduzione audio integrato (python-vlc):**
  - Supporto nativo per i formati audio più diffusi: MP3, FLAC, WAV, AAC, OGG, M4A, WMA.
  - Download automatico trasparente di VLC portatile se non presente sul sistema.
  - Controlli completi: Play, Pausa, Stop, Traccia successiva/precedente, Seekbar e volume fluido.
  - Modalità di riproduzione: casuale (*Shuffle*) e ripetizione.
  - Effetti visivi in tempo reale sincronizzati con la musica.
- **Gestore Playlist e Coda:**
  - Tabella virtualizzata fluida per decine di migliaia di brani.
  - Riordinamento intuitivo tramite trascinamento (*Drag & Drop*).
  - Salvataggio automatico della sessione.
- **Scanner locale multithreading ad alte prestazioni:**
  - Scansione ricorsiva asincrona con barra di avanzamento in tempo reale.
  - Estrazione rapida di metadati e copertine via `mutagen`.
- **Interfaccia moderna PySide6 (Tema Scuro):**
  - Tema scuro curato con animazioni fluide.
  - Supporto multilingue completo (francese, inglese, spagnolo, tedesco, italiano).
  - Pagina dedicata «Informazioni» con dettagli, link per donazioni e verifica aggiornamenti in-app via GitHub Releases.
