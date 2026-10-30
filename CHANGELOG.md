# Changelog — AMSO

<p align="right">
  <a href="CHANGELOG.fr.md">Français</a> • <b>English</b> • <a href="docs/i18n/CHANGELOG.es.md">Español</a> • <a href="docs/i18n/CHANGELOG.de.md">Deutsch</a> • <a href="docs/i18n/CHANGELOG.it.md">Italiano</a>
</p>

---

All notable changes to the **Audio Multi-Source Organizer (AMSO)** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning (SemVer)](https://semver.org/).

---

## [0.5.0-dev] - 2026-10-30

### Added
- *(TBD)*

## [0.4.1] - 2026-10-29

### Added
- **Audio transition non-regression test (TNR):** `scripts/tnr_transitions.bat` replays the end of a track and then the start of the next one (Sirius → Eye in the Sky by default) in the real player, with a dummy audio output, and compares the recording with an ideal construction (sample-identical in gapless, equal-power fade in crossfade, no cut, single audio session).
- **TNR log:** every run writes `tests/tnr/log/tnr_YYYY-MM-DD_HH-MM-SS.log` (version, commit, tracks, detailed results, Qt messages and player logs); the folder is ignored by git.
- **Startup log:** `startup.log` in the data folder times each launch step, the session restoration and the threads still running at shutdown.
- **Native crash log:** `crash.log` in the data folder (`%APPDATA%/AMSO/`) receives the stack of a LibVLC or Qt crash.
- **libVLC status:** the player settings show the version of the libVLC actually loaded and where it comes from (AMSO copy or system VLC), with the path in a tooltip.
- **Linux and macOS preparation:** the automatic VLC download (Windows archive) is reserved for Windows; elsewhere, AMSO explains how to install VLC (package manager, VLC.app). On macOS, VLC.app is also detected in `~/Applications`.
- **Experimental Linux and macOS versions (untested):** `release.yml` produces a `.tar.gz` archive and an `.AppImage` (Linux x86_64), as well as an unsigned `.dmg` for macOS Apple Silicon and Intel, through `scripts/package_unix.py`. VLC must be installed (package manager or VLC.app) and, on Linux, the `libpulse0`, `libxcb-cursor0` and `libxkbcommon-x11-0` libraries. The `buffer` audio engine and the transition non-regression test have only been validated on Windows: feedback (`startup.log`, `crash.log`) is welcome. The Linux CI now installs `libpulse0` (QtMultimedia failed to import) and the workflow's itch.io deployment now only happens on a tag.

### Changed
- **Startup:** the « All tracks » table is no longer loaded (up to 3 times ~50,000 tracks) before its page is opened; the banner counter stays exact through a `COUNT` query.
- **Startup:** the loading screen is displayed before the main window and the database are imported, numpy is only loaded in the background once the window is visible, the icon and the logo are cached.

### Fixed
- **Startup without network:** no disk probing (`exists`, `isdir`) is done anymore on a network path (UNC or mapped drive) from the UI thread at startup (cover art, folder watching, session restoration); an unreachable share no longer freezes the window. The cover art of a network track is re-checked every 30 s in the background.
- **Shutdown:** fixed « QThread: Destroyed while thread is still running » (the cover worker's `finished` signal hid the one from `QThread`, cover threads were not awaited).
- **`buffer` engine — transition mode change:** after changing the mode in the player settings, a seek followed by Play no longer started anything (the reset left the engine without audio output, and the player wrongly switched to the VLC path). The audio session is now recreated immediately. The current track restarts from the beginning after an engine or mode change. Finally, resuming a track loaded in pause (after a reset or a seek while stopped) restarts the `buffer` engine's transfer timer: without it, Play produced no sound. The decoder no longer emits the blocks of a decoding that has been replaced in the meantime (reset followed by Play, close seeks): they could distort the position or prevent the `buffer` engine from starting.
- **Blind Test with the `buffer` engine:** Play, Next and Previous started no sound (the track stayed loaded in pause, Play had to be pressed again): the track change restarted the round, which repositioned the track before the first decoded block arrived. The round now only repositions a track that the player has not just started itself.
- **`buffer` engine — distorted sound when moving or resizing the window:** the sound card was fed by a UI thread timer (185 ms buffer); this thread, blocked by the Windows move loop (up to 400 ms measured), left it without data. The `QAudioSink` now runs in pull mode in a dedicated audio thread (`audio_output.py`): the memory buffer, gapless and crossfade are unchanged, and the `vlc_direct` engine is not affected.
- **Translations:** a key missing from the language and from English (recent key, only present in `fr.json`) was displayed under its technical name; the fallback now goes through French. `sync_translations.py` detects translations where the model repeated the French text followed by a transcription (« text (romaji) »), retranslates them, rejects such answers and no longer sends English to Ollama.
- **Hard-coded texts:** the Statistics page (« tracks », « GB », « h »), file sizes (KB, MB, GB) and the « s » suffix of the Blind Test durations now go through translation keys.
- **Hard-coded texts (continued):** scanner messages, player and decoder errors, the VLC download, « Stereo / Mono », the « File not found » tooltip, « SYSTEM READY » and the startup screen now go through translation keys. The 42 languages are resynchronized (Ollama), including 15 translations whose `{count}` / `{name}` placeholders had disappeared.
- **Translated activity log:** « Synchronization succeeded », « Duration », « Tracks added », the levels (SUCCESS…) and the export dialogs were displayed in French whatever the language. Messages are now stored as a key and parameters (new `i18n` column, added without touching existing entries) and translated when displayed. Entries already recorded remain in French.
- **`buffer` engine — manual « Next »:** with the next track preloaded (Gapless 0 or Crossfade), a « Next » did start the next track but kept the position of the previous one (e.g. 1:00). The sample-accurate join is now reserved for the natural end of the track; a manual « Next » restarts the next track at 0.
- **`buffer` engine — crossfade:** the crossfade is now mixed as decoding progresses (computed over the whole requested duration, vectorized). It no longer cuts the end of the outgoing track, no longer shortens the fade and no longer causes stutters (the former sample-by-sample computation blocked the UI thread).
- **Blind Test with the `buffer` engine:** fixed an infinite recursion (`track_changed` ↔ `seek_ratio`) that closed the application; the Blind Test volume fades now also act on this engine.
- **Audio decoder (`amem`):** the end of stream announced by VLC stopped a `QTimer` from VLC's event thread (`QObject::killTimer: Timers cannot be stopped from another thread`, undefined behavior on every track); it is now relayed to the Qt thread.
- **`buffer` engine — « No fade » mode:** the hardware audio session is no longer closed and reopened between two tracks.

---

## [0.4.0] - 2026-10-25

### Added
- **CUE sheet (`.cue`) support:**
  - A `.cue` file appears in the folder tree as a virtual folder (💿 icon) containing its tracks with their title, artist and duration; the original audio file remains playable as usual.
  - A CUE track plays as a portion of the file (start at `INDEX 01`, end at the start of the next track, last track up to the end of the file) with its own position and duration, seeking inside the track, and gapless / crossfade transitions between portions (continuous buffer engine only; the `vlc_direct` engine shows an explanatory message).
  - Tolerance for malformed sheets (a `FILE` line pointing to the `.cue` itself falls back to the audio file with the same name), several `FILE` entries per sheet, UTF-8 / CP1252 encodings.
- **Expanded support for 43 international languages:**
  - Added 38 new languages with their native names in the language selector (`amso/core/i18n.py`).
  - Automated translation and complete parity (401 keys per language) using the local Ollama AI (`mistral:latest`).
  - One-click global synchronization script: `scripts/sync_all_languages_ollama.bat`.
- **Visual translation diagnostic mode (`⟦...⟧`):**
  - Added the `--debug-i18n` command-line argument and the `run_debug_i18n.bat` launcher, which wrap every translated text in `⟦...⟧` markers to spot dynamic texts on screen at a glance and isolate any hard-coded strings.
- **i18n audit and integrity tool (`scripts/audit_translations.py`):**
  - Automatic parity check of the 43 languages, detection of duplicate labels to merge and identification of orphan keys through `scripts/audit_translations.bat`.
- **Audio architecture selector in Settings / Perfect playback in gapless 0 mode (some anomalies remain in crossfade mode):**
  - Transparent choice in `Settings > Player` between:
    - *Continuous in-memory buffer (QAudioSink / WASAPI)*: a single uninterrupted stream to the sound card, gapless 0 transitions and crossfade without hardware cuts.
    - *Direct LibVLC output (dual hardware players)*: the classic hardware engine driven directly by LibVLC.
- **Unified quality validation harness (Quality Gate):** added the `scripts/verify.py` script and its root wrapper `verify.bat`, which run in sequence formatting (Ruff), linting (Ruff check), strict typing (Mypy without masking), file size limit checks and automated tests (Pytest).

### Fixed
- **Discovered playlists and CUE sheets: activity log and tree refresh:** a scan that only added playlists (M3U, PLS, XSPF, WPL, CUE) was mentioned nowhere and did not refresh the folder tree (the new node only appeared after a restart). The log now reports the number of playlists / CUE sheets added, updated or deleted (with the first names), and the tree is refreshed at the end of the scan.
- **Native WASAPI audio engine & fix for the premature end-of-track cut:**
  - *Native Windows WASAPI audio output (`mmdevice`)*: removed the forced `--aout=directsound` on Windows. VLC's DirectSound module abnormally truncated the last 1.3 to 1.4 seconds of audio files (cutting the end of *Sirius*). Aligning on `mmdevice` lets LibVLC play the whole audio stream up to the last millisecond in 32-bit float.
  - *Removal of pops and rapid-click artifacts*: eliminated the artificial volume cuts to 0 during `seek` and `stop`, which caused phase discontinuities and asynchronous timer collisions on rapid clicks. Time repositioning (`set_time`) and stopping now run natively and smoothly.
  - *Removal of micro-glitches at the end of tracks / quiet passages*: stopped the permanent volume polling in the tick loop, avoiding continuous repeated hardware gain adjustments during playback.
- **Millimetre-accurate transitions & smooth sequencing (Gapless & No fade):**
  - *Elimination of crackles and pops when the next track starts*: removed the forced volume of 0 on the second standby player, which caused a global session cut under WASAPI and then an impulsive transient ("crackle") when the pause was released. The second player is now preloaded paused (`:start-paused`) at nominal volume without affecting the current track.
  - *Gap-free sequencing (Gapless 0)*: exact handling of the LibVLC pipeline latency (`vlc_gapless_latency_ms`, 250 ms by default) to release the next player before the exact end of the current track, ensuring uninterrupted musical continuity with no silent gap between chained tracks (*Sirius* -> *Eye In The Sky*).
  - *Natural sequencing in No fade mode*: removed the artificial 400 ms delay after `State.Ended`, allowing an immediate and clean transition as soon as the previous track finishes.
- **Removal of unwanted audio playback triggers:**
  - *Going back (`previous` / `seek`)*: the previous-track command (`previous()`) strictly respects the player's pause state and uses `load_index()` to load the track without starting playback if the player was paused. Likewise, a time jump (`seek_ms`) cancels any standby preload or pending transition drain, and repositions the track without forcing playback if the player was paused or at the end of a track (`State.Ended`).
  - *Navigation between menus (leaving the Blind Test for other tabs)*: centralized tab navigation (`_switch_to_page`), forced stop of the Blind Test and reset of any active standby as soon as the page is left, to prevent any autonomous restart of the music in the background.
- **Smooth crossfade (Equal-Power Crossfade):**
  - *Hardware isolation of volumes on Windows*: dynamic assignment of the `directsound` audio output for crossfade mode (standard and gapless modes remain on native `mmdevice` without truncation). Unlike WASAPI (`mmdevice`), whose volume setting affects the global process session and generated a violent conflict (chopping / stutter at 40 Hz between the outgoing and incoming tracks), DirectSound isolates the volume of each secondary buffer (`IDirectSoundBuffer::SetVolume`).
  - *Perfectly smooth fade curves*: continuous equal-power transition (cosine for the outgoing track, sine for the incoming track) without any acoustic dip or stutter when the fade starts.
- **Reliability of the Continuous In-Memory Buffer Engine (Phase 2 - QAudioSink / Ring Buffer):**
  - *Absolute respect of pause on going back (`previous()`)*: `previous()` now faithfully preserves the pause state, loads the previous track without starting playback, and suspends the audio stream without micro-cuts or unexpected restarts.
  - *Natural sequencing in No fade mode*: removed the useless standby preload in standard mode, direct transition through the standard loading cycle with immediate update of the title, cover and exact duration.
  - *Resolution of collisions and stutter in Gapless 0 mode*: sealed lifecycle of the standby decoder, full disconnection/reconnection of signals (`ready_to_play`, `chunk_decoded`), seek restored after the splice, and strict rejection of PCM packets that do not match the current track in the memory buffer.
  - *In-memory equal-power crossfade (Crossfade mode)*:
    - Mathematical PCM mixing of 16-bit samples (equal-power cos/sin curves) from the current playhead (`_play_offset`), with anti-clipping clamping.
    - Strict separation between the audio trigger of the fade and the switch of the graphical interface: the UI stays on the outgoing track while it fades out progressively, and switches to the incoming track exactly when the track naturally ends, eliminating the premature visual and audio cut.
    - Continuous synchronization and time alignment: immediate purge of the consumed PCM data of the outgoing track at the end of the fade (`finish_crossfade`), precise realignment of the playback offset (`_base_offset_ms`) on the exact fade duration, guaranteeing a continuous cursor movement without jumps, as well as perfectly aligned time repositioning (`seek_ms`).
    - Modular split: extraction of `amso/services/player_vlc_transitions.py` (direct LibVLC transitions) to keep all player files under 450 lines.
  - *Full hot reset of the player (`reset_playback`)*:
    - Any change in the audio engine settings (*Direct VLC* vs *Continuous buffer*) or in the transition mode (*No fade*, *Gapless 0*, *Crossfade*) immediately stops the current playback and thoroughly resets the streams (clean destruction of the `QAudioSink`, emptying of the in-memory PCM buffers, stopping of the decoders, detaching of the LibVLC media, cancellation of all transition/fade timers).
    - The active track stays selected, paused at 00:00, ready to be started under the new configuration without restarting the application.

### Changed
- **Complete modular split of the architecture (< 500 lines per file):**
  - Goal 100% achieved: **0 files > 500 lines** across the whole AMSO code base (versus 8 files above the threshold initially).
  - Lightening of `main_window.py` (~1,500 -> 357 lines) through specialized mixins in `amso/ui/pages/`.
  - Decomposition of `player_service.py` (~1,400 -> 329 lines) with the extraction of `player_transport.py`, `player_queue.py`, `player_transitions.py` and `windows_audio.py`.
  - Split of `blind_test_view.py` (864 -> 447 lines) into `round_controller.py` and `compat.py`.
  - Split of `player_view.py` (693 -> 316 lines) into `player_ui_builder.py`.
  - Split of `settings_player.py` (668 -> 345 lines) into `settings_player_effects.py`.
  - Split of `theme.py` (633 -> 20 lines) into `resources.py`, `qss_base.py` and `qss_components.py`.
  - Split of `models.py` (631 -> 118 lines) into `models_base.py`, `folder_track_model.py` and `playlist_table_model.py`.
  - Split of `metadata.py` (621 -> 420 lines) into `cover_art.py`.
  - Split of `playlist_view.py` (603 -> 284 lines) into `playlist_ui_builder.py` and `playlist_table_view.py`.
  - Split of `logs_view.py` (512 -> 426 lines) into `log_detail_dialog.py`.
  - Split of `folders_page.py` (~970 -> 406 lines) into `folders_tree.py` and `folders_trash.py`.
- **Rationalization and merging of duplicates:**
  - Centralization of shared components (`ClickableSlider`, `EffectContainer`, `EffectsViewMixin`).
  - Factorization of generic UI labels under the shared `common.*` prefix (`common.cancel`, `common.close`, `common.refresh`, `common.later`, `common.open_explorer`, `table.col_filename`, `table.col_source`, `table.col_folder_name`).
  - Mandatory normalization of Windows CRLF line endings (`\r\n`) across all `.bat` files.

### Fixed
- **Harmonization and removal of translation leftovers in the 41 languages:**
  - Eradication of more than 1,400 keys left in French or English by default through the new `scripts/fix_residual_translations.py` tool (`scripts/fix_residual_translations.bat`).
  - Fixed the visual ambiance and graphic effect labels (`player.visual_effect`, `effects.*`), now natively translated in all languages.
  - Resolution of hybrid search placeholders (`topbar.search_placeholder`) mixing the target language and English on the Duplicates, Sources and Navigation screens.
  - Faithful translation of the source settings titles (`settings.page_sources_title`, `settings.section_sources_title`) and of the general settings (`settings.page_title`).
  - Full translation of the shared refresh button (`common.refresh`: "🔄 刷新" in Chinese, etc.) instead of a leftover French "Actualiser" in the logs.
  - Complete localization of the support, donation and official link sections of the About page (`dialog.about_*`, `update.btn_support`).

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
