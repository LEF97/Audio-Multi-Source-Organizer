# Changelog — AMSO

<p align="right">
  <a href="CHANGELOG.fr.md">Français</a> • <b>English</b> • <a href="CHANGELOG.es.md">Español</a> • <a href="CHANGELOG.de.md">Deutsch</a> • <a href="CHANGELOG.it.md">Italiano</a>
</p>

---

All notable changes to the **Audio Multi-Source Organizer (AMSO)** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning (SemVer)](https://semver.org/).

---

## [0.4.0-dev] - In Development

### Added
- Started development cycle for version 0.4.0 (Advanced Audio Experience, Artists Hub & Multiplatform Packaging for Linux/macOS).

---

## [0.3.0] - 2026-10-18

### Added
- **Full Playlist File Support**:
  - Automatic indexing and scanning of `.m3u`, `.m3u8`, `.pls`, `.xspf`, and `.wpl` playlist formats.
  - Dedicated folder tree nodes displayed with the **`🎶`** icon under their respective parent directories.
  - Strict preservation of the natural sequential playlist order (1, 2, 3...) in the `#` column without forced alphabetical sorting.
  - Clear visual detection of missing/moved tracks (**`⚠️`** warning prefix, warning highlight, and explanatory tooltip) without interrupting playback.
  - Context menu actions for playlist nodes: Direct playback, append to queue, play next, and reveal in Windows Explorer.
- **Acoustic Fade-in**:
  - Smooth 1-second volume fade-in (0% to set volume) on playback start and resume.
- **Background Synchronization & Tree Stability**:
  - Replaced the intrusive "Scan already running" popup with seamless background queue scheduling.
  - Eliminated unnecessary folder tree reloading when no directory structure changes occurred.
- **Dynamic Cover Art Presentation**:
  - Fixed scaling, recentering, and alignment when toggling fullscreen/windowed modes or resizing the window.

---

## [0.2.0] - 2026-10-18

### Added
- **Dedicated "Games / Blind Test" Sidebar Drawer**:
  - Added a collapsible "🎲 GAMES" drawer hosting the interactive Blind Test mini-game.
  - Session autonomy v2: dynamic countdown zoom, configurable reveal fade-out, instant stop on view leave, async cover art RAM preloading.
- **Audio Player UI Polish**:
  - Relocated volume slider to the top navigation header for an unobstructed player canvas.

### Fixed
- **SQLite `disk I/O error` resolution on Windows**: configured WAL mode once upon database initialization, configured `PRAGMA busy_timeout = 30000`, enabled in-memory temporary store (`PRAGMA temp_store = MEMORY`), and added automatic retry with exponential backoff to eliminate file locking contention during multithreaded scans.
- **Suppression of disruptive modal alerts during background sync**: automated background scans no longer pop up intrusive modal dialogs on transient errors, logging issues cleanly into the activity log and clickable status bar instead.
- **Startup low volume issue**: eliminated race condition during VLC engine initialization and prevented Windows audio mixer automatic ducking.
- **Official logo display in compiled Windows executable**: fixed multi-path resolution of embedded PyInstaller resources (`sys._MEIPASS`) to ensure the high-definition AMSO logo renders properly in the sidebar and About page instead of the fallback 🎵 icon.

---

## [0.1.0] - 2026-10-17

### Added
- **Integrated Audio Playback Engine (python-vlc):**
  - Native playback support for popular audio formats: MP3, FLAC, WAV, AAC, OGG, M4A, WMA.
  - Automatic and transparent download of a portable VLC binary if VLC is not present on the system.
  - Comprehensive playback controls: Play, Pause, Stop, Next track, Previous track, dynamic seekbar, and volume management.
  - Playback modes: Shuffle and repeat modes (*Disabled*, *Repeat playlist*, *Repeat single track*).
  - Real-time animated visualizer effects synchronized with playback (particles, waves, stars, spatial warp, aurora borealis, spectrum bars).
- **Playlist & Queue Management:**
  - Dedicated virtualized table view handling tens of thousands of tracks with zero lag.
  - Intuitive queue reordering via drag-and-drop.
  - Rich context menus: "Play", "Play Next", "Remove from Queue", "Track Info".
  - Automatic playback session persistence (current track, timestamp offset in ms, active playlist).
- **High-Performance Multithreaded Local Scanner:**
  - Fast asynchronous recursive directory traversal with live progress bar and metrics.
  - Rapid metadata extraction (title, artist, album, year, genre, duration, bitrate, track number) using `mutagen`.
  - Embedded cover art extraction and caching with asynchronous background rendering to prevent UI stutter.
  - File hash computation for duplicate file detection.
- **Optimized SQLite Database:**
  - Lean relational schema without heavy ORMs for instantaneous query execution.
  - Management of audio sources, scanned tracks, and activity history.
- **Modern User Interface (PySide6 / Dark Mode):**
  - Premium custom dark theme with sleek color palette and smooth animations.
  - Collapsible sidebar drawer for main navigation and settings.
  - Complete internationalization (French, English, Spanish, German, Italian) with runtime language switching.
  - Dedicated "About" page inside Settings: project details, version badge, open-source stack credits, links to GitHub, Itch.io, and funding platforms (Ko-fi, GitHub Sponsors).
  - Manual and automatic update checker querying GitHub Releases API (`/releases/latest`) with interactive notification banner.
  - Keyboard shortcut <kbd>F1</kbd> and direct click on the AMSO logo to access the "About" page.

### Changed
- Replaced the modal "About" popup with a fluid native page within Settings.
- Reorganized Settings navigation into 5 dedicated sections: General, Player, Sources, Logs, About.
- Hidden standard menu bar in favor of a modern, clean interface without orphan "Help" buttons.

### Fixed
- **Guaranteed 00:00 Start:** Reset pending seek offset (`_pending_seek_ms = 0`) whenever a new track or selection is launched from the library or playlist, reserving session offset resumption strictly for the player "Play" button.
- **Immediate Volume Persistence:** Instantaneous disk persistence in `config.ini` whenever the volume slider or mute toggle changes.
- **Reliable VLC Volume Enforcement:** Automatic resynchronization of audio volume upon entering the `Playing` state during internal player ticks, preventing volume jumps to 100% on cold VLC decoder starts.
