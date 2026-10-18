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

### 🟢 Version 0.1.0 — Robust Local Foundation
- [x] High-performance multithreaded local scanner with metadata extraction (ID3, Vorbis Comments, FLAC).
- [x] Integrated audio playback engine (python-vlc) with automatic portable VLC binary setup.
- [x] Full-featured Playlist view with drag-and-drop queue reordering, shuffle, and repeat modes.
- [x] Automatic playback session persistence (track position, volume level, active queue).
- [x] Sleek Dark Mode interface with real-time reactive audio visualizer effects.
- [x] Full internationalization (FR, EN, ES, DE, IT).
- [x] In-app notification system and update checker querying GitHub Releases.

---

### 🟢 Version 0.2.0 — Blind Test Mode, Trash Bin & UX Refinements
- [x] **Immersive "🎲 Games / Blind Test" Mode:** Animated pulsing countdown, soft fade-in reveal, automated round progression, and dedicated audio settings.
- [x] **Trash Bin Management & Instant Restoration:** Track exclusion, send to Windows Recycle Bin, and dedicated AMSO Trash view with one-click library restore.
- [x] **Reversible Shuffle & Drag-and-Drop Reordering:** Full visual queue shuffle, persistent original queue order upon toggle off, and mouse drag-and-drop reordering.
- [x] **Performance Optimization & Persistence v2:** Ultra-compact asynchronous SQLite session format (-99% disk footprint) and zero startup lag.
- [x] **Player Ergonomics & Navigation:** New "Games" drawer, top-bar integrated volume slider, and instant cold startup directly onto the Player view.

---

### 🟢 Version 0.3.0 — Full Playlist Support, Audio Fade-in & Robustness *(Current)*
- [x] **Full Playlist Files Support:** Automatic indexing of `.m3u`, `.m3u8`, `.pls`, `.xspf`, and `.wpl` formats in folder tree with dedicated `🎶` icons.
- [x] **Sequential Playback Order & Missing Track Alerts:** Preservation of natural playlist track order (`#` column) and clear visual alert (`⚠️`) without playback interruption.
- [x] **Acoustic Audio Fade-in:** Smooth 1-second volume progression from 0% on playback start or track resumption.
- [x] **Fluid Background Synchronization:** Seamless background scan queuing without intrusive dialogs, and preserving folder tree expansion state.
- [x] **Dynamic Cover Art Presentation:** Smooth resizing and recentering when toggling fullscreen/windowed modes.

---

### 🟡 Version 0.4.0 — Advanced Audio Experience, Artists & Multiplatform Packaging
- [ ] **Automated Cross-Platform Deployment (Linux & macOS):** Native compilation and automated packaging via GitHub Actions for Linux (`.AppImage` / `.tar.gz`) and macOS Apple Silicon ARM & Intel (`.dmg`), alongside Windows executables.
- [ ] **Artist Hub & Full Discography View:** Dedicated artist browser showcasing albums, singles, and full discographies.
- [ ] **Graphical Equalizer (EQ):** Curated sound presets (Rock, Pop, Jazz, Bass Boost) and multi-band parametric equalizer.
- [ ] **In-App Metadata Editor:** Direct ID3 / Vorbis tag editing on single or batch-selected tracks.
- [ ] **Automated Cover Art Fetcher:** Online artwork search (MusicBrainz / Cover Art Archive) for missing album covers.
- [ ] **Advanced Search Filters:** Combined filtering by genre, release year, bitrate, and lossless audio formats.
- [ ] **Configurable Crossfade:** Smooth, customizable crossfade transitions between songs.

---

### 🔵 Version 0.5.0 — Google Drive Cloud Connector
- [ ] **Secure OAuth 2.0 Browser Authentication:** Seamless browser sign-in without storing raw secrets.
- [ ] **Remote Google Drive Indexing:** Recursive scanning and indexing of audio tracks stored in selected Drive folders.
- [ ] **Direct Cloud Streaming:** Play remote audio files with background local caching.
- [ ] **Selective Bidirectional Sync:** Download remote cloud tracks or upload local files to Drive.

---

### 🟣 Version 0.6.0 — Streaming Integrations (Spotify, Deezer & Amazon Music)
- [ ] **Spotify Connector (Web API):** Connect user accounts to import playlists and saved library tracks.
- [ ] **Amazon Music Connector:** Remote music library scanning, streaming, and synchronization (OAuth 2.0).
- [ ] **Smart Hybrid Matching:** Match streaming playlist tracks against existing high-fidelity local files.
- [ ] **Unified Collection View:** Side-by-side display of local lossless audio and streaming-only tracks.

---

### 🌟 Version 1.0.0 — Intelligent Deduplication & Stable Release
- [ ] **Acoustic Audio Fingerprinting:** Duplicate detection regardless of corrupted metadata or re-encoded bitrates.
- [ ] **Smart Deduplication Wizard:** Quality comparison engine (automated selection of best bitrate/lossless source) with safe archival.
- [ ] **Official Cross-Platform Packages:** Signed installers for Windows (`.exe` / portable), macOS (`.dmg` Apple Silicon & Intel), and Linux (`AppImage` / `.deb`).
- [ ] **Comprehensive User Documentation:** Illustrated step-by-step user guide and official GitHub Pages showcase website.

---

## 💡 Suggest a Feature

Have an idea or a specific feature request?
- Open a discussion or ticket on [GitHub Issues](https://github.com/LEF97/Audio-Multi-Source-Organizer/issues) using the *Feature Request* template.
- Vote on community feature suggestions to help shape development priorities!
