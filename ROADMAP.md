# Project Roadmap — AMSO

<p align="right">
  <a href="ROADMAP.fr.md">Français</a> • <b>English</b> • <a href="docs/i18n/ROADMAP.es.md">Español</a> • <a href="docs/i18n/ROADMAP.de.md">Deutsch</a> • <a href="docs/i18n/ROADMAP.it.md">Italiano</a>
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

### 🟢 Version 0.3.0 — Full Playlist Support, Audio Fade-in & Robustness
- [x] **Full Playlist Files Support:** Automatic indexing of `.m3u`, `.m3u8`, `.pls`, `.xspf`, and `.wpl` formats in folder tree with dedicated `🎶` icons.
- [x] **Sequential Playback Order & Missing Track Alerts:** Preservation of natural playlist track order (`#` column) and clear visual alert (`⚠️`) without playback interruption.
- [x] **Acoustic Audio Fade-in:** Smooth 1-second volume progression from 0% on playback start or track resumption.
- [x] **Fluid Background Synchronization:** Seamless background scan queuing without intrusive dialogs, and preserving folder tree expansion state.
- [x] **Dynamic Cover Art Presentation:** Smooth resizing and recentering when toggling fullscreen/windowed modes.

---

### 🟢 Version 0.4.0 — Advanced Audio Experience & CUE Sheets
- [x] **Modular architecture refactoring & Quality Gate:** Application split into cohesive modules (< 500 lines), MainWindow modularized into dedicated mixins (amso/ui/pages/), audio service broken down into independent subsystems (player_transport, player_queue, player_transitions) and an automated validation harness put in place (scripts/verify.py & .bat: ruff, mypy, pytest, size checks).
- [x] **Windows Shell & taskbar integration:** Native pinning directly from the active icon (explicit AppUserModelID LEF97.AMSO.AudioPlayer) from the main.py entry point, and shortcut persistence across updates.
- [x] **Perfect Gapless 0 listening between two tracks:** 2 engines are now available, one based on VLC_direct, the other working in buffer mode (preferred). These modes allow smooth listening on albums with linked tracks (Alan Parsons, Pink Floyd, Mike Oldfield, etc.).
- [x] **CUE sheet (`.cue`) support:** A `.cue` file is displayed as a folder of virtual tracks (💿) with their duration and plays like real tracks (continuous buffer engine).

---

### 🟢 Version 0.4.1 — Audio Reliability, Translated Log & Experimental Linux / macOS Versions *(Current)*
- [x] **Audio output independent of the UI thread:** the `buffer` engine's `QAudioSink` is fed by a dedicated audio thread (pull mode); moving or resizing the window no longer distorts the sound.
- [x] **Blind Test with the `buffer` engine:** Play, Next and Previous start the sound without pressing Play again.
- [x] **Completed translations:** activity log stored as a key + parameters and translated when displayed, hard-coded texts converted, fallback to French, `{name}` placeholder check during synchronization.
- [x] **libVLC status:** version and origin (AMSO copy or system VLC) in the player settings.
- [x] **Cross-platform deployment (Linux & macOS), experimental untested version:** automated packaging via GitHub Actions for Linux (.AppImage / .tar.gz) and macOS Apple Silicon ARM & Intel (unsigned .dmg), VLC required; testers send back `startup.log` and `crash.log`.

---

### 🔵 Version 0.4.2 — Linux & macOS Network Compatibility
- [ ] **Network mount detection (Linux & macOS):** `amso/core/network_paths.py` only recognizes UNC paths and mapped Windows drives today; recognize NFS / SMB / AFP mounts (`/proc/self/mountinfo`, `statfs`) to avoid any blocking disk probing at startup on those systems.
- [ ] **Validation on Linux and macOS:** `buffer` engine, transitions and packaging to be confirmed on real systems based on testers' feedback.

---

### 🔵 Version 0.5.0 — Album Navigation in Playlists
- [ ] **Playlists in album mode:** « Show in album mode » option (enabled by default) that groups a playlist's tracks into virtual folders by album in the tree, with « (unknown album) » for tracks without an album and a per-playlist override through right-click.

---

### 🌟 Version x.0.0 — Smart Deduplication & Stable Release
- [ ] **Acoustic fingerprint detection (Audio Fingerprinting):** Identification of duplicates even with wrong tags or re-encoded files.
- [ ] **Duplicate resolution assistant:** Smart quality comparison (automatic selection of the best bitrate / lossless) with safe archiving.
- [ ] **Official cross-platform packaging:** Signed executables for Windows (`.exe` / portable), macOS (`.dmg` Apple Silicon & Intel) and Linux (`AppImage` / `.deb`).
- [ ] **Complete user documentation:** Illustrated step-by-step guide and GitHub Pages showcase site.
- [ ] **Spotify connector (Web API):** User account connection and retrieval of playlists and favorites.
- [ ] **Amazon Music connector:** Scan, streaming and synchronization of remote music collections (OAuth 2.0).
- [ ] **Smart hybrid matching:** Matching between the tracks of a remote playlist and the files already present locally (high fidelity).
- [ ] **Unified view:** Side-by-side display of the tracks available locally and those available only through streaming.
- [ ] **Secure OAuth 2.0 authentication:** Simplified connection through the browser without storing secrets in clear text.
- [ ] **Remote scan of Google Drive folders:** Indexing of the audio files present in the configured folders.
- [ ] **Direct cloud streaming playback:** Listening to remote tracks with transparent local caching.
- [ ] **Selective two-way synchronization:** Local download of tracks from the cloud or backup of local tracks to Drive.
- [ ] **Artist management and associated discography:** Dedicated view per artist with albums, singles and complete discography.
- [ ] **Graphical equalizer (EQ):** Presets (Rock, Pop, Jazz, Bass Boost) and multi-band parametric equalizer.
- [ ] **In-app metadata editor:** Direct editing of ID3 / Vorbis tags on one or several selected files.
- [ ] **Automatic cover art download:** Online search (MusicBrainz / Cover Art Archive) for missing covers.
- [ ] **Advanced search filters:** Combined filtering by genre, year, bitrate and lossless format.
- [x] **Configurable crossfade & advanced audio sequencing:** Support for gapless transitions (Gapless 0 ms), high-precision crossfade (Equal-Power Crossfade) and the standard no-gap mode.

---

## 💡 Suggest a Feature

Have an idea or a specific feature request?
- Open a discussion or ticket on [GitHub Issues](https://github.com/LEF97/Audio-Multi-Source-Organizer/issues) using the *Feature Request* template.
- Vote on community feature suggestions to help shape development priorities!
