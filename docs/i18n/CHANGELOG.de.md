# Änderungsprotokoll (Changelog) — AMSO

<p align="right">
  <a href="../../CHANGELOG.fr.md">Français</a> • <a href="../../CHANGELOG.md">English</a> • <a href="CHANGELOG.es.md">Español</a> • <b>Deutsch</b> • <a href="CHANGELOG.it.md">Italiano</a>
</p>

---

Alle wesentlichen Änderungen am Projekt **Audio Multi-Source Organizer (AMSO)** werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/)
und dieses Projekt hält sich an die Spezifikation [Semantic Versioning (SemVer)](https://semver.org/lang/fr/).

---

## [0.4.0] - 2026-10-25

### Zugefügt
- **Unterstützung von CUE-Sheets (`.cue`) :**
  - Eine `.cue`-Datei erscheint im Verzeichnisbaum als virtueller Ordner (Symbol 💿), der ihre Titel mit Titel, Künstler und Dauer enthält; die ursprüngliche Audiodatei bleibt normal lesbar.
  - Wiedergabe eines CUE-Tracks als Teil der Datei (Start `INDEX 01`, Ende am Anfang des nächsten Tracks, letzter Track bis zum Ende der Datei) mit eigener Position und Dauer, Bewegung innerhalb des Tracks und gapless / crossfade-Verknüpfung zwischen den Teilen (nur mit kontinuierlichem Puffer-Engine; die Engine `vlc_direct` zeigt eine erklärende Nachricht an).
  - Toleranz gegenüber falsch formatierten Sheets (Zeile `FILE` verweist auf die `.cue` selbst: Rückfall auf die Audiodatei mit demselben Namen), mehrere `FILE` pro Sheet, UTF-8 / CP1252-Kodierungen.
- **Erweiterte Unterstützung von 43 internationalen Sprachen :**
  - Integration von 38 neuen Sprachen mit ihren nativen Bezeichnungen im Sprachauswähler (`amso/core/i18n.py`).
  - Automatisierte Übersetzung und vollständige Parität (401 Schlüssel pro Sprache) über die lokale KI Ollama (`mistral:latest`).
  - Skript zur globalen Synchronisierung mit einem Klick: `scripts/sync_all_languages_ollama.bat`.
- **Visueller Diagnosemodus für Übersetzungen (`⟦...⟧`) :**
  - Hinzufügen des CLI-Arguments `--debug-i18n` und des Launchers `run_debug_i18n.bat`, der jeden übersetzten Text mit den Tags `⟦...⟧` umgibt, um dynamische Texte auf dem Bildschirm sofort zu erkennen und mögliche hartcodierte Zeichenketten zu isolieren.
- **i18n Audit- und Integritätswerkzeug (`scripts/audit_translations.py`) :**
  - Automatische Erkennung der Parität von 43 Sprachen, Erkennung doppelter Bezeichnungen zum Zusammenführen und Identifizierung von verwaisten Schlüsseln über `scripts/audit_translations.bat`.
- **Auswahl der Audio-Architektur in den Einstellungen / Perfektes Abspielen im Gapless-Modus 0 (es verbleiben einige Anomalien im Cross-Fade-Modus) :**
  - Transparente Auswahl in `Einstellungen > Player` zwischen:
    - *Kontinuierer Speicherpuffer (QAudioSink / WASAPI)* : einziger ununterbrochener Stream zur Soundkarte, Gapless-0-Übergänge und Fade ohne Hardwareunterbrechung.
- *Direkter LibVLC-Output (doppelter Hardware-Player)*: klassische Hardware-Engine, die direkt von LibVLC gesteuert wird.
- **Vereinheitlichtes Qualitätsvalidierungs-Harness (Quality Gate):** Erstellung des Skripts `scripts/verify.py` und seines Root-Wrappers `verify.bat`, das nacheinander das Formatieren (Ruff), den Linter (Ruff check), die statische Typisierung (Mypy ohne Maskierung), die Überprüfung der maximalen Dateigrößen und die automatisierten Tests (Pytest) ausführt.

### Fixed
- **Entdeckte Playlists und CUE-Dateien: Aktivitätsprotokoll und Aktualisierung der Verzeichnisstruktur:** Ein Scan, der nur Playlists (M3U, PLS, XSPF, WPL, CUE) hinzufügte, wurde nirgends erwähnt und aktualisierte nicht die Verzeichnisstruktur (der neue Knoten erschien erst nach einem Neustart). Das Protokoll gibt nun die Anzahl der hinzugefügten, aktualisierten oder gelöschten Playlists/CUE-Dateien (mit den ersten Namen) an, und die Verzeichnisstruktur wird am Ende des Scans aktualisiert.
- **Native WASAPI Audio-Engine & Behebung des vorzeitigen Abbruchs am Ende des Tracks:**
  - *Native Windows WASAPI Audioausgabe (`mmdevice`)*: Entfernung der Erzwingung von `--aout=directsound` unter Windows. Das DirectSound-Modul von VLC trennte die letzten 1,3 bis 1,4 Sekunden der Audiodateien unnormal (unterbrach das Ende von *Sirius*). Die Ausrichtung auf `mmdevice` ermöglicht es LibVLC, den gesamten Audio-Stream bis zur letzten Millisekunde in 32-bit float auszugeben.
  - *Entfernung von Bops und Artefakten schneller Klicks*: Eliminierung künstlicher Volumenabbrüche auf 0 bei `seek` und `stop`, die Phaseninkonsistenzen und asynchrone Timer-Kollisionen bei schnellen Klicks verursachten. Die zeitliche Neupositionierung (`set_time`) und das Stoppen erfolgen nun nativ und flüssig.
  - *Entfernung von Mikro-Glitches am Ende des Tracks / in ruhigen Passagen*: Beendigung des permanenten Volumen-Pollings in der Tick-Schleife, wodurch keine wiederholten, kontinuierlichen Hardware-Gain-Anpassungen während der Wiedergabe gesendet werden.
- **Millimetergenaue Übergänge & Flüssige Übergänge (Gapless & Kein Fade-Out):**
  - *Eliminierung von Knackgeräuschen und Pops beim Start des nächsten Titels* : Entfernung der Zwangseinstellung der Lautstärke auf 0 beim zweiten Standby-Player, die eine globale Sitzungsunterbrechung unter WASAPI und anschließend einen impulsiven Übergang („Knackgeräusch“) bei der Freigabe der Pause verursachte. Der zweite Player wird im Pausenzustand vorgeladen (`:start-paused`) mit der nominalen Lautstärke, ohne den aktuellen Titel zu beeinträchtigen.
  - *Nahtloses Aneinanderreihen (Gapless 0)* : Exakte Berücksichtigung der LibVLC Pipeline-Latenz (`vlc_gapless_latency_ms`, 250 ms standardmäßig), um den nächsten Player vor dem genauen Ende des aktuellen Tracks freizugeben und so eine unterbrechungsfreie musikalische Kontinuität ohne jegliche Stille zwischen Aneinandergereihten (*Sirius* -> *Eye In The Sky*) zu gewährleisten.
  - *Natürliches Aneinanderreihen im Modus ohne Übergang* : Entfernung der künstlichen Verzögerung von 400 ms nach `State.Ended`, was einen sofortigen und sauberen Übergang unmittelbar nach Beendigung des vorherigen Titels ermöglicht.
- **Entfernung unzeitgemäßer Audio-Wiedergabestartungen:**
  - *Zurückspulen (`previous` / `seek`)* : Der Befehl zum vorherigen Titel (`previous()`) beachtet strikt den Pausenzustand des Players und verwendet `load_index()` zum Laden des Titels, ohne die Wiedergabe zu starten, falls der Player pausiert war. Ebenso hebt eine zeitliche Verschiebung (`seek_ms`) jegliches wartende Standby-Vorgeladen oder Übergangsleerung auf und positioniert den Titel ohne erzwungene Wiedergabe, falls der Player pausiert oder am Ende des Titels (`State.Ended`) war.
  - *Navigation zwischen Menüs (Verlassen des Blind Tests zu anderen Tabs)* : Zentralisierung der Tab-Navigation (`_switch_to_page`), erzwungener Stopp des Blind Tests und Zurücksetzen jeglichen aktiven Standbys beim Verlassen der Seite, um ein autonomes Neustarten der Musik im Hintergrund zu verhindern.
- **Nahtloser Crossfade (Crossfade Equal-Power) :**
  - *Hardware-Isolation der Lautstärken unter Windows* : Dynamische Zuweisung der Audioausgabe `directsound` für den Crossfade-Modus (Standard- und Gapless-Modi bleiben auf nativem `mmdevice` ohne Kürzung). Im Gegensatz zu WASAPI (`mmdevice`), dessen Lautstärkeregelung die globale Prozesssitzung beeinflusst und einen heftigen Konflikt erzeugte (Hacken / Ruckeln bei 40 Hz zwischen dem auslaufenden und dem einlaufenden Titel), isoliert DirectSound die Lautstärke für jeden sekundären Puffer (`IDirectSoundBuffer::SetVolume`).
  - *Perfekt glatte Fade-Kurven* : Kontinuierlicher Übergang gleicher Leistung (Kosinus für den auslaufenden Titel, Sinus für den einlaufenden Titel) ohne akustische Einbrüche oder Ruckeln beim Start des Fades.
- **Zuverlässigkeitsverbesserung des Kontinuierlichen Speicherpuffer-Motors (Phase 2 - QAudioSink / Ring Buffer) :**
  - *Absoluter Respekt für die Pause beim Zurückspulen (`previous()`)* : `previous()` speichert nun zuverlässig den Pausenzustand, lädt den vorherigen Titel ohne Wiedergabe auszulösen und hält den Audio-Stream ohne Mikropause oder spontanes Neustarten an.
  - *Natürliches Aneinanderhängen im Modus ohne Fade* : Entfernung des unnötigen Standby-Voreladens im Standardmodus, direkter Übergang über den Standard-Ladezyklus mit sofortiger Aktualisierung des Titels, des Covers und der genauen Dauer.
  - *Auflösung von Kollisionen und Ruckeln im Gapless 0-Modus* : Hermetischer Lebenszyklus des Standby-Decoders, vollständige Trennung/Wiederverbindung der Signale (`ready_to_play`, `chunk_decoded`), Wiederherstellung des Seeks nach dem Übergang und strikte Ablehnung von PCM-Paketen, die nicht mit dem aktuellen Titel im Speicherpuffer übereinstimmen.
  - *Crossfade im Speicher bei gleicher Leistung (Crossfade-Modus)* :
    - Mathematische PCM-Mischung der 16-Bit-Samples (cos/sin-Kurven gleicher Leistung) ab dem aktuellen Abspielkopf (`_play_offset`), mit Anti-Clipping-Clamping.
- Strikte Trennung zwischen dem Audio-Auslösen des Fades und dem Umschalten der grafischen Benutzeroberfläche: Die UI bleibt während des progressiven Ausblenden auf dem auslaufenden Titel sichtbar und wechselt genau bei der natürlichen Beendigung des Stücks zum einlaufenden Titel, wodurch ein vorzeitiger visueller und akustischer Bruch vermieden wird.
- Kontinuierliche Synchronisation und zeitliche Abstimmung: Sofortige Bereinigung der verbrauchten PCM-Daten vom auslaufenden Track bei der Beendigung (`finish_crossfade`), präzise Neukalibrierung des Wiedergabe-Offsets (`_base_offset_ms`) über die exakte Dauer des Fades, was ein kontinuierliches Scrollen des Reglers ohne Teleportation sowie eine perfekt ausgerichtete zeitliche Neupositionierung (`seek_ms`) gewährleistet.
- Modulares Schneiden: Extraktion von `amso/services/player_vlc_transitions.py` (direkte LibVLC-Übergänge), um alle Player-Dateien unter 450 Zeilen zu halten.
  - *Vollständige Hot-Reset des Players (`reset_playback`)*:
    - Jede Änderung in den Audio-Engine-Einstellungen (*VLC direkt* vs. *Kontinuierlicher Puffer*) oder im Übergangsmodus (*Kein Fade*, *Gapless 0*, *Crossfade*) unterbricht sofort die laufende Wiedergabe und initialisiert die Streams vollständig neu (saubere Zerstörung des `QAudioSink`, Leeren der PCM-Speicherpuffer, Stoppen der Decoder, Trennen der LibVLC-Medien, Abbrechen aller Übergangs-/Fade-Timer).
    - Der aktive Track bleibt auf Pause bei 00:00 ausgewählt und bereit, unter der neuen Konfiguration gestartet zu werden, ohne dass die Anwendung neu gestartet werden muss.


### Changed
- **Vollständige modulare Aufteilung der Architektur (< 500 Zeilen pro Datei):**
  - Ziel zu 100 % erreicht: **0 Datei > 500 Zeilen** über die gesamte AMSO-Codebasis (im Vergleich zu anfänglich über dem Schwellenwert befindlichen 8 Dateien).
  - Reduzierung von `main_window.py` (~1 500 -> 357 Zeilen) mittels spezialisierter Mixins in `amso/ui/pages/`.
  - Zerlegung von `player_service.py` (~1 400 -> 329 Zeilen) mit der Extraktion von `player_transport.py`, `player_queue.py`, `player_transitions.py` und `windows_audio.py`.
  - Aufspaltung von `blind_test_view.py` (864 -> 447 Zeilen) nach `round_controller.py` und `compat.py`.
  - Aufspaltung von `player_view.py` (693 -> 316 Zeilen) nach `player_ui_builder.py`.
  - Aufspaltung von `settings_player.py` (668 -> 345 Zeilen) nach `settings_player_effects.py`.
  - Aufteilung von `theme.py` (633 -> 20 Zeilen) auf `resources.py`, `qss_base.py` und `qss_components.py`.
  - Aufteilung von `models.py` (631 -> 118 Zeilen) auf `models_base.py`, `folder_track_model.py` und `playlist_table_model.py`.
  - Aufteilung von `metadata.py` (621 -> 420 Zeilen) auf `cover_art.py`.
  - Aufteilung von `playlist_view.py` (603 -> 284 Zeilen) auf `playlist_ui_builder.py` und `playlist_table_view.py`.
  - Aufteilung von `logs_view.py` (512 -> 426 Zeilen) auf `log_detail_dialog.py`.
  - Aufteilung von `folders_page.py` (~970 -> 406 Zeilen) auf `folders_tree.py` und `folders_trash.py`.
- **Rationalisierung und Zusammenführung von Duplikaten:**
  - Zentralisierung der geteilten Komponenten (`ClickableSlider`, `EffectContainer`, `EffectsViewMixin`).
  - Refaktorierung der generischen UI-Bezeichnungen unter dem gemeinsamen Präfix `common.*` (`common.cancel`, `common.close`, `common.refresh`, `common.later`, `common.open_explorer`, `table.col_filename`, `table.col_source`, `table.col_folder_name`):
  - Obligatorische Normalisierung der Windows-Zeilenenden CRLF (`\r\n`) für alle `.bat`-Dateien.

### Fixed
- **Harmonisierung und Eliminierung von Übersetzungsresten in 41 Sprachen:**
  - Eliminierung von über 1 400 Schlüsseln, die auf Französisch oder Englisch als Standard verblieben sind, mittels des neuen Tools `scripts/fix_residual_translations.py` (`scripts/fix_residual_translations.bat`).
  - Korrektur der Beschriftungen für visuelle Atmosphäre und grafische Effekte (`player.visual_effect`, `effects.*`), die nun nativ in allen Sprachen übersetzt sind.
  - Behebung der hybriden Such-Platzhalter (`topbar.search_placeholder`), die die Zielsprache und Englisch auf den Bildschirmen Duplikate, Quellen und Navigation vermischen.
  - Treue Übersetzung der Titel für die Quellen-Einstellungen (`settings.page_sources_title`, `settings.section_sources_title`) und die allgemeine Konfiguration (`settings.page_title`).
  - Vollständige Übersetzung des geteilten Aktualisierungsbuttons (`common.refresh` : « 🔄 刷新 » in Chinesisch, etc.) anstelle eines französischen Rest-„Actualiser“ in den Logs.
  - Vollständige Lokalisierung der Abschnitte für Unterstützung, Spenden und offizielle Links auf der „Über uns“-Seite (`dialog.about_*`, `update.btn_support`).

---

## [0.3.0] - 2026-10-18

### Neu hinzugefügt
- **Umfassende Unterstützung von Playlist-Dateien** :
  - Automatische Indizierung von Playlist-Formaten: `.m3u`, `.m3u8`, `.pls`, `.xspf` und `.wpl`.
  - Integration in die Verzeichnisstruktur „Nach Ordner“ in Form dedizierter Knoten mit dem Icon **`🎶`**.
  - Beibehaltung der sequenziellen Abspielreihenfolge, die in der Playlist definiert ist (Spalte `#` mit der Reihenfolge 1, 2, 3...) ohne erzwungte automatische alphabetische Sortierung.
  - Verwaltung und visuelle Erkennung fehlender oder verschobener Titel: Anzeige durch ein Präfix **`⚠️`**, sanfte Warnfarbgebung und beschreibendes Info-Bubble, ohne die Wiedergabe anderer Titel zu blockieren.
  - Erweitertes Kontextmenü für Playlist-Knoten: direktes Abspielen, Hinzufügen zur Warteschlange und Öffnen des Playlist-Dateipfades im Windows Explorer.
- **Sanftes Einblenden des Klangs (*Fade-in*)** :
  - Progressive Übergang der Lautstärke von 0% auf die eingestellte Lautstärke über 1 Sekunde beim Starten oder Fortsetzen einer Audio-Wiedergabe (außer im Blind Test Modus).
- **Stabilität und Flüssigkeit der Synchronisierung** :
  - Entfernung des blockierenden Dialogfelds „Scan already running“ zugunsten einer stillen Warteschlangenabfolge.
  - Beibehaltung der Auswahl und keine unnötige Neuladung der Ordnerstruktur, wenn keine Ordneränderung erkannt wird.
- **Dynamische Anzeige der Cover** :
  - Korrektur der Größenänderung und Neupositionierung des Covers beim Wechsel zwischen Vollbild / Fenster oder bei der freien Größenänderung des Fensters.

---

## [0.2.0] - 2026-10-18

### Hinzugefügt

### Blind Test Modus & Spiele-Sektion
- **Neue Schublade „🎲 Spiele“** : Dedizierte ausklappbare Kategorie in der Seitenleiste, die die Blind Test Ansicht (lokalisiert in 5 Sprachen) beherbergt.
- **Immersives Spielerlebnis** : Dynamischer visueller Countdown in der Mitte des verdeckten Covers, progressive Enthüllung durch sanftes Ausblenden und automatische Abfolge der Runden.
- **Erweiterte Akustiksteuerung** : Präzise Einstellung der Such-, Entdeckungs- und des ausgehenden Sound-Fade-Out-Zeiten (*fade-out*).
- **Dedizierte Konfiguration** : Verlagerung der Blind Test Einstellungen in `Paramètres > Lecteur`.

### Ergonomie & Playlist-Verwaltung
- **Überarbeitung des Zufallsmodus (Shuffle)**: Vollständiges visuelles Mischen der Warteschlange, das den aktiven Titel bewahrt, ein direkter Aktionsknopf „🎲 Titel mischen“ und eine genaue Wiederherstellung der ursprünglichen Reihenfolge nach Deaktivierung.
- **Neuorganisation per Drag-and-Drop**: Fließende Umordnung der Titel mit der Maus in der Liste, ohne die Wiedergabe zu unterbrechen.
- **Asynchrone Sicherung v2**: Kompaktes Format mittels SQLite-Identifikatoren, das den Speicherbedarf um 99 % reduziert (nicht blockierende Zugriffe, konstante 60 FPS).
- **Verhalten „No Autoplay“**: Das Hinzufügen von Titeln zur Warteschlange erzwingt nicht mehr den vorzeitigen Start der Wiedergabe.

### Verwaltung der Bibliothek & Intelligenter Papierkorb
- **Zwei-stufige Löschung** : Wahl zwischen dem einfachen Entfernen der Bibliothek (mit gespeicherter Ausgrenzung für zukünftige Scans) und der physischen Löschung in den Windows-Papierkorb.
- **Dedizierte „🗑️ Papierkorb“-Ansicht** : Einsicht in ausgeschlossene Tracks und Wiederherstellung mit einem Klick mit automatischer Wiedereingliederung in die Datenbank.
- **Klarere Verzeichnisstruktur** : Visuelle Unterscheidung zwischen lokalen und Cloud-Quellen, Verzeichnisstruktur standardmäßig beim Start eingeklappt und vereinheitlichte Kontextmenüs.

### Stabilität des Audiomotors (LibVLC) & Leistung
- **Beseitigung kritischer Blockaden** : Entfernung des Deadlocks zwischen dem internen C-Thread von LibVLC und der Qt-Ereignis-Schleife (Ende von UI-Einfrierungen und weißen Bildschirmen).
- **Robustheit der Übergänge** : Anti-Reentrancy-Lock bei schnellen Titelwechseln und Behebung von Blockaden bei aufeinanderfolgenden Rückspulen (« Vorheriger Titel »).
- **Zuverlässige Lautstärkesteuerung** : Integration des Lautstärkereglers in die obere Leiste des Players und Behebung von DirectSound-Dämpfungs-Konflikten.

### Schnittstelle & offizielle Links
- **Modernisierung der Seite „Über uns“** : Neuausgerichtete Kopfzeile, integrierter interaktiver Retro-Spektrumanalysator unter dem Text und Hinzufügen offizieller Buttons (Ko-fi, GitHub Sponsors, GitHub, Itch.io).
- **Volle Internationalisierung** : Vollständige Synchronisierung aller Bezeichnungen und Optionen in 5 Sprachen (FR, EN, ES, DE, IT).

### Fixed
- **Behebung von Fehlern `disk I/O error` (SQLite unter Windows)**: Konfiguration des WAL-Modus einmalig bei der Initialisierung der Datenbankdatei, Hinzufügen von `PRAGMA busy_timeout = 30000`, temporärer Speicher im RAM (`PRAGMA temp_store = MEMORY`) und Mechanismus der automatischen Wiederholungsversuche mit exponentiellem Backoff, um Konflikte bei der Dateisperrung während multithreaded Scans zu beseitigen.
- **Entfernung von blockierenden modalen Warnungen im Hintergrund** : Die automatischen Hintergrundsynchronisierungen zeigen bei einem vorübergehenden Fehler keine störenden modalen Dialogfelder mehr an, sondern protokollieren die Warnung ordnungsgemäß im Aktivitätsprotokoll und in der klickbaren Statusleiste.
- **Zu geringe Audiolautstärke beim Start** : Beseitigung eines Race-Conditions bei der Initialisierung des VLC-Wiedergabemotors und Neutralisierung der automatischen Dämpfung (*ducking*) des Windows-Audiomixers.
- **Anzeige des offiziellen Logos in der Windows-Ausführungsdatei** : Korrektur der Multi-Pfad-Auflösung eingebetteter PyInstaller-Ressourcen (`sys._MEIPASS`), um das AMSO-Logo in hoher Auflösung in der Seitenleiste und auf der Info-Seite anzuzeigen, anstelle des Ersatz-Icons 🎵.
- **Wiederherstellung der Playlist und hermetische Isolierung der Tests** : Beseitigung einer Verunreinigung des Benutzerprofils, bei der die Ausführung automatisierter Tests `saved_playlist.json` mit gefälschten Tracks (*Track 1, Track 2, Track 3*) und einer falschen Zeitposition (14:10 bei einem 3:00 Stück) überschreiben konnte. Vollständige Isolierung von `AMSO_DATA_DIR`, `AMSO_PLAYLIST_PATH` und `AMSO_DB_PATH` in der Testumgebung, automatische Filterung von lokalen, nicht existierenden oder nicht auffindbaren Tracks beim Laden der Playlist und Sicherung der Anfangsposition, um niemals die Dauer des Titels zu überschreiten.
- **Optimierung der Startzeit mit großen Playlists (Eliminierung des Einfrierens bei 85 %)**: Beseitigung eines blockierenden Engpasses im Hauptthread während der Wiederherstellung der Wiedergabesitzung. Die Validierung der Playlist führte Tausende synchroner Disk-Aufrufe `Path.exists()` durch (~40 Sekunden für 12 000 Titel). Sie verwendet nun eine sofortige In-Memory-Überprüfung O(1) (< 1 ms) für alle Titel aus der aktiven SQLite-Datenbank, was den Anwendungsstart augenblicklich macht.
- **Fließende Schritt-für-Schritt-Fortschrittsanzeige und Eliminierung des visuellen Rückspringens des Splash Screens**: Überarbeitung der Fortschrittsverfolgung beim Start mit einer fließenden Schritt-für-Schritt-Animation von 1 % auf 1 % (10 ms pro Inkrement) für einen kontinuierlichen und sauberen Übergang zwischen den regulären Stufen (15 % Präferenzen, 25 % Thema, 35 % SQLite, 45 % Audiomotor, 60 % Oberfläche, 75 % Bibliothek, 90 % Sitzungswiederherstellung, 100 % Fertigstellung). Behebung eines globalen CSS-Stilkonflikts, bei dem die Anwendung des Dark Themes ein `max-width: 220px` auf allen Fortschrittsbalken vorschrieb, wodurch die Breite des Splash Screens plötzlich halbiert und die visuelle Illusion eines Rückspringens der blauen Anzeige erzeugt wurde. Sicherung der Breite (`#splashProgressBar`), Sperrung des streng monotonen Fortschritts und Entfernung der überflüssigen Angabe rechts im Footer.
- **Visuelles Rendern des Standard-Cover-Art (Vinyl & Notiz)**: Entfernung des vertikalen Beschneidens an der rechten Kante des Notensymbols in der Mitte des Vinyls, das durch die Anwendung eines synthetischen Fettdrucks (*synthetic bold*) des DirectWrite-Schrifttreibers unter Windows verursacht wurde.
- **Strikte Erkennung von Ordner-Covern (*folder cover*)** : Verbesserung des Algorithmus zur Bildsuche im Verzeichnis, um nur legitime Covernamen zu akzeptieren (`folder`, `cover`, `front`, Titel, `album`, `artwork`) und willkürliche oder präfixierte Bilder abzulehnen (z. B. `exfolder.webp`). Sofortige Cache-Invalidierung bei jeder Umbenennung oder Löschung im Ordner, um zuverlässig auf das Standard-Vinyl-Visual zu wechseln (« integriertes Cover > Bildordner > Musik-Vinyl »).

---

## [0.1.0] - 2026-10-17

### Zugefügt
- **Integriertem Audio-Wiedergabe-Engine (python-vlc) :**
  - Native Unterstützung gängiger Audioformate: MP3, FLAC, WAV, AAC, OGG, M4A, WMA.
  - Transparente Erkennung und automatischer Download eines portablen VLC-Binärs, falls VLC auf dem System des Benutzers fehlt.
  - Volle Wiedergabesteuerung: Play, Pause, Stop, Nächster Titel, Vorheriger Titel, dynamer Fortschrittsbalken (Seekbar) und Lautstärkeregelung.
  - Wiedergabemodi: Zufällige Wiedergabe (*Shuffle*) und Wiederholungsmodi (*Deaktiviert*, *Playlist wiederholen*, *Titel in Schleife wiederholen*).
  - Echtzeit-animierte visuelle Effekte, synchronisiert mit der Wiedergabe (Partikel, Wellen, Sterne, räumliche Verzerrung, Nordlichter, Spektralbalken).
- **Playlist- und Warteschlangen-Manager :**
  - Dedizierte Ansicht mit virtualisierter Tabelle, die zehntausende Titel ohne Latenz unterstützt.
  - Intuitiv neu anordnen der Warteschlange per Drag & Drop (*Drag & Drop*).
  - Vollständige Kontextmenüs: „Abspielen“, „Zur Warteschlange hinzufügen“, „Aus der Warteschlange entfernen“, „Eigenschaften“.
  - Automatische Speicherung der Wiedergabesitzung (aktueller Titel, zeitliche Position in ms, aktive Playlist).
- **Hochleistungsfähiger multithreaded lokaler Scanner:**
  - Asynchrone rekursive Durchsuchung lokaler Verzeichnisse mit Fortschrittsbalken und Echtzeit-Metriken.
  - Schnelle Extraktion von Metadaten (Titel, Künstler, Album, Jahr, Genre, Dauer, Bitrate, Tracknummer) via `mutagen`.
  - Extraktion und Caching integrierter Album-Cover mit asynchroner Darstellung, um jegliches Einfrieren der Benutzeroberfläche zu vermeiden.
  - Berechnung von Datei-Hash-Prägen zur Identifizierung physischer Duplikate.
- **Optimierte SQLite-Datenbank:**
  - Relationale Architektur ohne schweres ORM für nahezu augenblickliche Abfrageausführung.
  - Verwaltung von Quellen, gescannten Tracks und Aktivitätsverlauf.
- **Moderne Benutzeroberfläche (PySide6 / Dark Mode):**
  - Hochwertiges, personalisiertes Dark-Theme mit sorgfältiger Farbpalette und sanften Animationen.
  - Ausziehbare Seitenleiste für die Hauptnavigation und Einstellungen.
  - Volle mehrsprachige Unterstützung (Französisch, Englisch, Spanisch, Deutsch, Italienisch) mit Hot-Language-Wechsel.
  - Dedizierte „Über uns“-Seite in den Einstellungen: Projektdetails, Versions-Badge, Open-Source-Technologien, Links zu GitHub, Itch.io und Förderplattformen (Ko-fi, GitHub Sponsors).
  - Manuelle und automatische Update-Prüfung, die die GitHub Releases API (`/releases/latest`) abfragt, mit interaktivem Benachrichtigungsbanner.
  - Tastenkürzel <kbd>F1</kbd> und direkter Klick auf das AMSO-Logo, um die „Über uns“-Seite zu öffnen.

### Geändert
- Ersetzen des modalen Dialogs „Über“ durch eine integrierte und flüssige Unterseite in den Einstellungen.
- Neuorganisation der Navigationsstruktur der Einstellungen in 5 Abschnitte: Allgemein, Player, Quellen, Protokolle, Über.
- Verbergen der verbleibenden Standardmenüleiste zugunsten einer aufgeräumten Oberfläche ohne verwaister „Hilfe“-Button.

### Fixed
- **Start bei 00:00 :** Systematische Zurücksetzung der Zeitposition (`_pending_seek_ms = 0`) bei der Auswahl einer neuen Musik aus der Bibliothek oder der Playlist, wobei die Wiederaufnahme der Position nur auf den « Play »-Button der wiederhergestellten vorherigen Sitzung beschränkt wird.
- **Sofortige Volumenpersistenz :** Sofortiges Speichern in `config.ini` bei jeder Manipulation des Lautstärkeschiebers oder des Stummschaltknopfes.
- **VLC-Lautstärkebeschränkung :** Automatische Resynchronisierung der Audio-Lautstärke beim Übergang in den Zustand `Playing` in der Uhrenschleife, um jeglichen Verlust von Einstellungen beim Kaltstart des VLC-Dekoders zu vermeiden.
