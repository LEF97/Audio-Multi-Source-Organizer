# Project Roadmap — AMSO

<p align="right">
  <a href="ROADMAP.fr.md">Français</a> • <b>English</b> • <a href="ROADMAP.es.md">Español</a> • <a href="ROADMAP.de.md">Deutsch</a> • <a href="ROADMAP.it.md">Italiano</a>
</p>

---

This document outlines strategic goals, planned features, and future development milestones for the **Audio Multi-Source Organizer (AMSO)** project.

---

## 🎯 Project Vision

AMSO aims to become the definitive **universal and decentralized music hub**: a fast, lightweight, visually stunning, and privacy-first desktop application empowering users to manage and unify their music collections whether stored on local hard drives, archived in the cloud, or streamed via online services.

---

## 🗺️ Milestones & Versions

### 🟢 Version 0.1.0 — Robust Local Foundation *(Current)*
- [x] High-performance multithreaded local scanner with metadata extraction (ID3, Vorbis Comments, FLAC).
- [x] Integrated audio playback engine (python-vlc) with automatic portable VLC binary setup.
- [x] Full-featured Playlist view with drag-and-drop queue reordering, shuffle, and repeat modes.
- [x] Automatic playback session persistence (track position, volume level, active queue).
- [x] Sleek Dark Mode interface with real-time reactive audio visualizer effects.
- [x] Full internationalization (FR, EN, ES, DE, IT).
- [x] In-app notification system and update checker querying GitHub Releases.

---

### 🟡 Version 0.2.0 — Advanced Audio, Artists & Discography
- [ ] **Artist profiles & discography view:** Dedicated artist hub showcasing albums, singles, and discographies.
- [ ] **Graphical Equalizer (EQ):** Curated presets (Rock, Pop, Jazz, Bass Boost) and multi-band parametric equalizer.
- [ ] **In-app metadata editor:** Direct editing of ID3 / Vorbis tags on selected tracks or entire albums.
- [ ] **Automated album artwork fetcher:** Online artwork search (MusicBrainz / Cover Art Archive) for missing album covers.
- [ ] **Advanced search filters:** Multi-criteria filtering by genre, release year, bitrate, and lossless audio formats.
- [ ] **Configurable crossfade:** Customizable smooth transitions between songs.

---

### 🔵 Version 0.3.0 — Google Drive Cloud Connector
- [ ] **Secure OAuth 2.0 Browser Authentication:** Seamless browser sign-in without storing raw secrets.
- [ ] **Remote Google Drive Indexing:** Recursive scanning and indexing of audio tracks stored in selected Drive folders.
- [ ] **Direct Cloud Streaming:** Play remote audio files with background local caching.
- [ ] **Selective Bidirectional Sync:** Download remote cloud tracks or upload local files to Drive.

---

### 🟣 Version 0.4.0 — Streaming Integrations (Spotify, Deezer & Amazon Music)
- [ ] **Spotify Connector (Web API):** Connect user accounts to import playlists and saved library tracks.
- [ ] **Amazon Music Connector:** Remote music library scanning, streaming, and synchronization (OAuth 2.0).
- [ ] **Smart Hybrid Matching:** Match streaming playlist tracks against existing high-fidelity local files.
- [ ] **Unified Collection View:** Side-by-side display of local lossless audio and streaming-only tracks.

---

### 🌟 Version 1.0.0 — Intelligent Deduplication & Stable Release
- [ ] **Acoustic Audio Fingerprinting:** Duplicate detection regardless of corrupted metadata or re-encoded bitrates.
- [ ] **Smart deduplication wizard:** Quality comparison engine (automated selection of best bitrate/lossless source) with safe archival.
- [ ] **Official cross-platform packages:** Signed installers for Windows (`.exe` / portable), macOS (`.dmg` Apple Silicon & Intel), and Linux (`AppImage` / `.deb`).
- [ ] **Comprehensive user documentation:** Illustrated guide and official GitHub Pages showcase website.

---

## 💡 Suggest a Feature

Have an idea or a specific feature request?
- Open a discussion or ticket on [GitHub Issues](https://github.com/LEF97/Audio-Multi-Source-Organizer/issues) using the *Feature Request* template.
- Vote on community feature suggestions to help shape development priorities!
