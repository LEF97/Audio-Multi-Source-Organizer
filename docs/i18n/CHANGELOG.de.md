# Änderungsprotokoll (Changelog) — AMSO

<p align="right">
  <a href="../../CHANGELOG.fr.md">Français</a> • <a href="../../CHANGELOG.md">English</a> • <a href="CHANGELOG.es.md">Español</a> • <b>Deutsch</b> • <a href="CHANGELOG.it.md">Italiano</a>
</p>

---

Alle wesentlichen Änderungen am Projekt **Audio Multi-Source Organizer (AMSO)** werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/)
und dieses Projekt hält sich an die Spezifikation [Semantic Versioning (SemVer)](https://semver.org/lang/fr/).

---

## [0.5.0] - 2026-11-18

### Hinzugefügt

- **Schnelle Audio-Tools (⚙-Taste des Players):** Ein Registerkartenfenster, das die Auswahl des Ausgabegeräts, der Audio-Engine und des Übergangsmodus (Standard, Gapless 0 ms, Crossfade), einen **10-Band-Grafikequalizer** mit Voreinstellungen (Flach, Rock, Jazz, Klassik, Verstärkte Bässe, Stimme, Electro, Benutzerdefiniert), die **ReplayGain-Normalisierung**, die **Wiedergabegeschwindigkeit** und einen **Abschalt-Timer** (15, 30, 45 oder 60 Minuten, Ende des aktuellen Titels oder der Warteschlange) zusammenfasst. Ausgang, Equalizer, ReplayGain und Geschwindigkeit sind nur mit der Engine `buffer` verfügbar.
- **„Nächster“-Leiste:** Der nächste Titel wird angezeigt, wenn man über die „Weiter“-Taste fährt, und ein Klick spielt ihn sofort ab.
- **Anleitungen:** Eine Hilfe-Taste auf jeder Seite (Player, Blind Test, Playlists, Tracks, Duplikate, Ordner, Quellen & Bibliothek, Einstellungen, Verlauf) öffnet ein Fenster mit Erklärungen.
- **„Ton“ und „Effekte“ Seiten in den Einstellungen:** Einstellungen für die Normalisierung und die Wiedergabegeschwindigkeit sowie Auswahl der visuellen Effekte, die im Player und im Blind Test angeboten werden.
- **Visuelle Effekte:** Neuer Effekt „Warp Pilot“ und **Zufällige** Stimmung, die bei jedem Titel oder in einem einstellbaren Intervall (15 s, 30 s, 1, 2 oder 5 Minuten) wechselt, separat für den Player und den Blind Test.
- **Windows-Integration:** Integration in die Taskleiste und ein Icon im Benachrichtigungsbereich (Fenster anzeigen oder ausblenden, aktueller Titel, beenden).
- **Klickbarer Scan-Bericht:** Das Ergebnis eines Scans verlinkt zu den betroffenen Elementen.
- **Animierter Play/Pause-Button:** Bassreaktiver Halo und fließender Übergang zwischen Wiedergabe und Pause (blau bei Pause, bernsteinfarben bei Wiedergabe).
- **Speichereinstellung der linken Menübreite:** Sie wird beim Start wiederhergestellt und ändert sich nicht mehr von Seite zu Seite; nur der Benutzer kann sie ändern.

- **„Quellen & Bibliothek“-Ansicht:** neue dedizierte Seite, die den alten Statistikbildschirm ersetzt, mit globaler oder quellenweiser Ansicht, Gesundheitsindikatoren (offline Quellen, Scan-Fehler, fehlende Playlist-Dateien oder -Einträge) und Schnellaktionen (bearbeiten, neu scannen, löschen, in der Bibliothek öffnen).
- **Playlist-Editor und -Reparatur:** dediziertes Fenster zur Neuordnung von Titeln (nach oben/unten verschieben), zum Löschen von Einträgen, zum Neuladen vom Laufwerk, zur Neulokalisierung einer fehlenden Datei oder zum Starten einer automatischen Reparatur (lokale Suche gefolgt von Datenbank mit Vertrauensscore und Vorschau der Vorschläge).
- **Export / Sicherung von Playlists:** Sicherung der aktuellen Warteschlange in `.m3u`, `.m3u8`, `.pls`, `.xspf` oder `.wpl` mit sofortiger Datenbankindizierung.
- **Playlists nach Album gruppiert:** Anzeige in virtuellen Ordnern pro Album in der Playlist-Hierarchie (mit dem Ordner „unbekanntes Album“ für Titel ohne Album).
- **Visuelle Cover-Übergänge:** 5 konfigurierbare Stile in den Player-Einstellungen (Keine, Verblassen, Gleiten, Zoom, Umblättern).
- **Speicherung der Fenstergeometrie:** Speichern und Wiederherstellen von Größe, Position und maximiertem Zustand beim Neustart.

### Geändert

- **CUE-Sheets :** kontinuierliche Abfolge von Tracks aus derselben Datei (Engine `buffer`): Die Datei wird nur einmal für eine gesamte Reihe zusammenhängender Tracks dekodiert, und die Grenzen sind exakte Positionen im PCM-Puffer, berechnet aus dem CUE. Korrigiert das Ende des vorherigen Tracks am Anfang des nächsten (ungenauer Seek bei einem MP3 mit variabler Bitrate). Crossfade wird nicht zwischen zwei Tracks aus derselben CUE-Datei angewendet (der Stream ist bereits kontinuierlich).
- **3-Phasen-Scan :** klare Trennung von Inventar, Metadaten-Extraktion und Playlist-Analyse mit detaillierter Protokollierung und Fortschrittsanzeige.
- **Visuelle Identität :** neues AMSO-Icon (PNG hochauflösend, ICO 7 Größen, ICNS 4 Größen).
- **Schnellere Track-Tabellen :** Anzeige von Zellen pro Feld und zwischengespeicherte übersetzte Bezeichnungen (etwa 40 % weniger Zeit pro Zelle bei 50.000 Zeilen).
- **Interne Qualität :** deklaratives SQLite-Schema (`db/schema.py`), Tabellenspalten sind in `table_settings` faktorisiert, Themenfarben sind in `styles.py` zentralisiert, Titelzeile, Lautstärkesteuerung und Dialogfelder sind faktorisiert, gezielte oder protokollierte stille `except`. Keine sichtbare Verhaltensänderung.

### Behoben

- **Moteur \`buffer\` — ancien titre rejoué à la reprise :** le \`QAudioSink\` conservait environ 185 ms d'audio après une pause ou un arrêt, ce qui rejouait la fin de l'ancien titre après un Précédent/Suivant en pause ou un double clic après arrêt. Le tampon est maintenant purgé au chargement et à la réouverture de la sortie.
- **Bibliothèque :** la barre du haut ne se redimensionne plus, le fil d'Ariane est tronqué par « … » et l'arborescence n'a plus de défilement horizontal.

- **Moteur `buffer` — Haken beim Start eines Titels:** Nach einem Stopp wurde der Audio-Output kalt direkt auf den ersten dekodierten Block neu geöffnet, was den Anfang eines gehaltenen Tons (« TU-TUUU ») haken ließ. Der Output ist nun sofort bei der Wiedergabeanforderung geöffnet und spielt während der Dekodierung des ersten Blocks Stille ab: keine zusätzliche Latenz, immer noch eine einzige Audiositzung.
- **Moteur `buffer` — Pop beim manuellen Titelwechsel:** Den Titelwechsel mitten während der Wiedergabe kappte den alten Ton mitten in der Welle. Er endet nun mit einem Mikro-Fade-out von 10 ms (Output bleibt offen) und der nächste Titel beginnt mit einem Fade-in gleicher Dauer. Die automatische Verknüpfung und der Motor `vlc_direct` wurden nicht geändert.

### Tests

- **Dummy-Ausgabe der TNR:** `CaptureOutput` folgt der Schnittstelle von `SinkOutput` (die TNR detektierte weder das Ende eines Tracks noch einen Übergang).
- **Detektion von Pops in der TNR:** `tests/tnr/clicks.py` erkennt abrupte Stillekanten und misst den Amplitudensprung an einem bekannten Schnittpunkt, validiert an synthetischen Signalen (`tests/test_tnr_clicks.py`).

## [0.4.1] - 2026-10-29

### Hinzugefügt

- **Non-Regression der Audio-Übergänge (TNR):** `scripts/tnr_transitions.bat` spielt das Ende eines Titels und dann den Anfang des nächsten (Sirius → Eye in the Sky standardmäßig) im echten Player mit einem simulierten Audio-Output ab und vergleicht die Aufnahme mit einer idealen Konstruktion (bis auf die Abtastung gapless, ausgeglichener Fade bei Crossfade, kein Abbruch, einzelne Audiositzung).
- **TNR-Protokoll:** Jede Ausführung schreibt `tests/tnr/log/tnr_AAAA-MM-JJ_HH-MM-SS.log` (Version, Commit, Tracks, detaillierte Ergebnisse, Qt-Nachrichten und Player-Logs); das Verzeichnis wird von git ignoriert.
- **Startprotokoll:** `startup.log` im Datenverzeichnis zeichnet jeden Schritt des Starts, die Wiederherstellung der Sitzung und die noch aktiven Threads beim Schließen auf.
- **Native Absturzprotokoll:** `crash.log` im Datenverzeichnis (`%APPDATA%/AMSO/`) empfängt den Stack eines Absturzes von LibVLC oder Qt.
- **libVLC-Status:** Die Player-Einstellungen zeigen die tatsächlich geladene libVLC-Version und deren Herkunft (AMSO-Kopie oder System-VLC) mit dem Pfad im Tooltip an.
- **Vorbereitung für Linux und macOS:** Der automatische Download von VLC (Windows-Archiv) ist nur für Windows reserviert; andernorts zeigt AMSO an, wie VLC installiert wird (Paketmanager, VLC.app). Unter macOS wird VLC.app auch in `~/Applications` erkannt.
- **Experimentelle Versionen für Linux und macOS (nicht getestet):** `release.yml` erzeugt ein `.tar.gz`-Archiv und ein `.AppImage` (Linux x86_64) sowie ein nicht signiertes `.dmg` für macOS Apple Silicon und Intel, über `scripts/package_unix.py`. VLC muss installiert sein (Paketmanager oder VLC.app) und unter Linux die Bibliotheken `libpulse0`, `libxcb-cursor0` und `libxkbcommon-x11-0`. Der Audio-Engine `buffer` und die Nicht-Regression der Übergänge wurden nur unter Windows validiert: Rückmeldungen (`startup.log`, `crash.log`) sind willkommen. Das Linux CI installiert nun `libpulse0` (QtMultimedia scheiterte beim Import) und die itch.io Bereitstellung des Workflows erfolgt nur noch auf einem Tag.

### Geändert

- **Start:** Die Tabelle „Alle Titel“ wird nicht mehr geladen (bis zu 3 Mal ~50.000 Tracks) bevor ihre Seite geöffnet wird; der Zähler im Banner bleibt über eine `COUNT`-Abfrage genau.
- **Start:** Der Ladebildschirm wird vor dem Import des Hauptfensters und der Datenbank angezeigt; numpy wird nicht mehr nur im Hintergrund geladen, sobald das Fenster sichtbar ist; das Icon und das Logo werden zwischengespeichert.

### Behoben

- **Start ohne Netzwerk:** Es wird kein Dateisystem-Polling mehr (`exists`, `isdir`) auf einem Netzwerkpfad (UNC oder gemappter Laufwerk) vom Interface-Thread beim Start durchgeführt (Cover, Ordnerüberwachung, Sitzungswiederherstellung); ein nicht erreichbares Share friert das Fenster nicht mehr ein. Das Cover eines Netzwerk-Tracks wird alle 30 s im Hintergrund überprüft.
- **Schließung:** Korrektur von „QThread: Destroyed while thread is still running“ (Signal `finished` des Cover-Workers, das das von `QThread` maskierte, unerwartete Cover-Threads).
- **Motor `buffer` — Wechsel des Übergangsmodus:** Nach einem Moduswechsel in den Player-Einstellungen startete ein Seek und dann Play keine Funktion mehr (die Initialisierung ließ den Motor ohne Audioausgabe, und der Player wechselte fälschlicherweise zum VLC-Pfad). Die Audiositzung wird nun sofort neu erstellt. Der aktuelle Track startet nach einem Motor- oder Moduswechsel von vorne. Schließlich startet die Fortsetzung eines Pausenzustands (nach einem Reset oder einem Stopp-Seek) den Transfer-Timer des Motors `buffer`: Ohne ihn erzeugte Play keinen Ton. Der Decoder sendet nicht mehr die Blöcke einer zwischenzeitlich ersetzten Dekodierung (Reset gefolgt von Play, enge Seeks): Sie konnten die Position verfälschen oder den Start des Motors `buffer` verhindern.
- **Blind Test mit dem Motor `buffer`:** Play, Nächster und Vorheriger erzeugten keinen Ton (der Track blieb in Pausenzustand, man musste erneut auf Play drücken): Der Wechsel des Tracks startete die Runde neu, die den Track vor dem Eintreffen des ersten dekodierten Blocks neu positionierte. Die Runde positioniert nicht mehr einen Track, den der Player gerade selbst gestartet hat.
- **Moteur \`buffer\` — Ton verändert beim Verschieben oder Neugrößen des Fensters:** Die Soundkarte wurde von einem Timer des Interface-Threads (Puffer von 185 ms) gespeist; dieser Thread, blockiert durch die Windows-Verschiebeschleife (bis zu 400 ms gemessen), ließ sie ohne Daten zurück. Das \`QAudioSink\` wechselt in einen Pull-Modus in einen dedizierten Audio-Thread (\`audio_output.py\`): Der Speicherpuffer, das Gapless und der Crossfade bleiben unverändert, und der Motor \`vlc_direct\` ist nicht betroffen.
- **Übersetzungen:** Ein Schlüssel, der in der Sprache und im Englischen fehlt (neuer Schlüssel, nur in \`fr.json\` vorhanden), wurde unter seinem technischen Namen angezeigt; der Fallback erfolgt nun über Französisch. \`sync_translations.py\` erkennt Übersetzungen, bei denen das Modell den französischen Text gefolgt von einer Transkription (« texte (romaji) ») übernommen hat, übersetzt diese erneut, lehnt diese Antworten ab und sendet nicht mehr Englisch an Ollama.
- **Hardcodierte Texte:** Die Seite Statistiken (« morceaux », « Go », « h »), die Dateigrößen (Ko, Mo, Go) und das Suffix « s » der Blind-Test-Dauern werden über Übersetzungsschlüssel geführt.
- **Hardcodierte Texte (fortgesetzt):** Die Nachrichten des Scanners, die Fehler des Players und des Decoders, der VLC-Download, « Stéréo / Mono », das Tooltip « Fichier introuvable », « SYSTÈME PRÊT » und der Startbildschirm werden über Übersetzungsschlüssel geführt. Die 42 Sprachen werden resynchronisiert (Ollama), einschließlich 15 Übersetzungen, deren Marker \`{count}\` / \`{name}\` verschwunden waren.
- **Übersetztes Aktivitätsprotokoll:** « Synchronisation réussie », « Durée », « Morceaux ajoutés », die Level (SUCCESS…) und die Exportboxen wurden unabhängig von der Sprache auf Französisch angezeigt. Die Nachrichten werden nun als Schlüssel und Parameter gespeichert (neue Spalte \`i18n\`, hinzugefügt, ohne bestehende Einträge zu berühren) und bei der Anzeige übersetzt. Bereits gespeicherte Einträge bleiben auf Französisch.
- **`buffer`-Engine — Manuelles „Weiter“:** Mit dem vorab geladenen nächsten Titel (Gapless 0 oder Crossfade) startete ein „Weiter“ zwar den nächsten Titel, behielt aber die Position des vorherigen Titels bei (z. B. 1:00). Der nahtlose Übergang auf Sample-Ebene ist nun auf das natürliche Ende des Titels beschränkt; ein manuelles „Weiter“ startet den nächsten Titel bei 0.
- **`buffer`-Engine — Crossfade:** Der Crossfade wird nun während der Dekodierung gemischt (berechnet über die gesamte angeforderte Dauer, vektorisiert). Er schneidet nicht mehr das Ende des ausgehenden Titels ab, verkürzt den Fade nicht mehr und verursacht keine Ruckler (die frühere Berechnung Sample für Sample blockierte den Interface-Thread).
- **Blind Test mit der `buffer`-Engine:** Korrektur einer unendlichen Rekursion (`track_changed` ↔ `seek_ratio`), die die Anwendung geschlossen hat; die Lautstärkefades des Blind Tests wirken nun auch auf diese Engine.
- **Audio-Dekodierer (`amem`):** Das von VLC gemeldete Ende des Streams stoppte einen `QTimer` aus dem VLC-Ereignis-Thread (`QObject::killTimer: Timers cannot be stopped from another thread`, undefiniertes Verhalten bei jedem Titel); es wird nun in den Qt-Thread weitergeleitet.
- **`buffer`-Engine — Modus „Kein Fade“:** Die Hardware-Audiositzung wird zwischen zwei Titeln nicht mehr geschlossen und wieder geöffnet.
- **`vlc_direct`-Engine — Pause:** `pause()` pausierte nur die `buffer`-Engine (immer instanziiert) und ließ LibVLC laufen; das Öffnen des Blind Tests während einer Wiedergabe des Players unterbricht daher nicht die Musik.
- **Ladebildschirm:** Die Beschriftung „Verbindung zur Datenbank“ blieb während der Imports angezeigt (~5 s); sie zeigt nun „Start der Anwendung...“.

---

## [0.4.0] - 2026-10-25

### Hinzugefügt

- **Unterstützung von CUE-Sheets (`.cue`) :**
  - Eine `.cue`-Datei erscheint im Verzeichnisbaum als virtuelles Verzeichnis (Symbol 💿), das ihre Tracks mit Titel, Künstler und Dauer enthält; die ursprüngliche Audiodatei bleibt normal lesbar.
  - Abspielung eines CUE-Tracks als Abschnitt der Datei (Start bei `INDEX 01`, Ende am Anfang des nächsten Tracks, letzter Track bis zum Ende der Datei) mit eigener Position und Dauer, Verschiebung innerhalb des Tracks und nahtloses Abspielen / Crossfade zwischen Abschnitten (nur mit kontinuierlichem Puffer-Engine; die Engine `vlc_direct` zeigt eine erklärende Meldung an).
  - Toleranz gegenüber fehlerhaften Sheets (Zeile `FILE` zeigt auf die `.cue`-Datei selbst: Rückfall auf die Audiodatei mit demselben Namen), mehrere `FILE` pro Sheet, UTF-8 / CP1252-Kodierungen.
- **Erweiterter Support für 43 internationale Sprachen:**
  - Integration von 38 neuen Sprachen mit ihren nativen Bezeichnungen im Sprachauswähler (`amso/core/i18n.py`).
  - Automatisierte und vollständige Paritätsübersetzung (401 Schlüssel pro Sprache) über die lokale KI Ollama (`mistral:latest`).
  - Globales Synchronisierungsskript mit einem Klick: `scripts/sync_all_languages_ollama.bat`.
- **Visueller Diagnosemodus für Übersetzungen (`⟦...⟧`) :**
  - Hinzufügen des CLI-Arguments `--debug-i18n` und des Starters `run_debug_i18n.bat`, die jeden übersetzten Text mit den Tags `⟦...⟧` umrahmen, um dynamische Texte sofort auf dem Bildschirm zu erkennen und mögliche hartcodierte Zeichenketten zu isolieren.
- **i18n Audit- und Integritätswerkzeug (`scripts/audit_translations.py`) :**
  - Automatische Erkennung der Parität von 43 Sprachen, Erkennung von zu fusionierenden Beschriftungsdoppelungen und Identifizierung von verwaisten Schlüsseln über `scripts/audit_translations.bat`.
- **Auswahl der Audio-Architektur in den Einstellungen / Perfektes Abspielen im Gapless-Modus 0 (es bleiben einige Anomalien im Cross-Fade-Modus bestehen) :**
  - Transparente Auswahl in `Einstellungen > Player` zwischen:
    - *Kontinuierer Speicherpuffer (QAudioSink / WASAPI)* : einziger ununterbrochener Stream zur Soundkarte, Gapless-Übergänge 0 und Übergang ohne Hardwareunterbrechung.
    - *Direkter LibVLC-Ausgang (doppelter Hardware-Player)* : klassische Hardware-Engine, die direkt von LibVLC gesteuert wird.
- **Vereinheitlichter Qualitätsvalidierungs-Harness (Quality Gate):** Erstellung des Skripts `scripts/verify.py` und seines Root-Wrappers `verify.bat`, das nacheinander das Formatieren (Ruff), den Linter (Ruff check), das strikte Typisieren (Mypy ohne Maskierung), die Überprüfung der Dateigrößenlimits und die automatisierten Tests (Pytest) ausführt.

### Behoben

- **Entdeckte Playlists und CUE-Dateien: Aktivitätsprotokoll und Verzeichnisaktualisierung:** Ein Scan, der nur Playlists (M3U, PLS, XSPF, WPL, CUE) hinzufügte, wurde nirgends erwähnt und aktualisierte nicht die Verzeichnisstruktur (der neue Knoten erschien erst nach einem Neustart). Das Protokoll gibt nun die Anzahl der hinzugefügten, aktualisierten oder gelöschten Playlists/CUE-Dateien (mit den ersten Namen) an, und die Verzeichnisstruktur wird am Ende des Scans aktualisiert.
- **Native WASAPI Audio-Engine & Behebung des vorzeitigen End-of-Track-Abbruchs:**
  - *Native Windows WASAPI Audio-Ausgabe (`mmdevice`)*: Entfernung der Erzwingung von `--aout=directsound` unter Windows. Das DirectSound-Modul von VLC trennte die letzten 1,3 bis 1,4 Sekunden von Audiodateien abnormal (was das Ende von *Sirius* abschneiden würde). Die Ausrichtung auf `mmdevice` ermöglicht es LibVLC, den gesamten Audio-Stream bis zur letzten Millisekunde in 32-bit float auszugeben.
  - *Entfernung von Bops und Artefakten schneller Klicks*: Eliminierung künstlicher Volumenabbrüche auf 0 bei `seek` und `stop`, die Phaseninkonsistenzen und asynchrone Timer-Kollisionen bei schnellen Klicks verursachten. Die zeitliche Neupositionierung (`set_time`) und das Stoppen erfolgen nun nativ und flüssig.
  - *Entfernung von Mikro-Glitches am Ende des Tracks / in ruhigen Passagen*: Beendigung des permanenten Volumen-Pollings in der Tick-Schleife, wodurch keine wiederholten, kontinuierlichen Hardware-Gain-Anpassungen während der Wiedergabe gesendet werden.
- **Millimetergenaue Übergänge & Flüssige Übergänge (Gapless & Kein Fade-out):**
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

### Geändert

- **Vollständige modulare Aufteilung der Architektur (< 500 Zeilen pro Datei) :**
  - Ziel zu 100 % erreicht: **0 fichier > 500 lignes** im gesamten AMSO Codebase (gegenüber ursprünglich 8 Dateien über dem Schwellenwert).
  - Reduzierung von `main_window.py` (~1 500 -> 357 Zeilen) mittels spezialisierter Mixins in `amso/ui/pages/`.
  - Zerlegung von `player_service.py` (~1 400 -> 329 Zeilen) durch die Extraktion von `player_transport.py`, `player_queue.py`, `player_transitions.py` und `windows_audio.py`.
  - Aufteilung von `blind_test_view.py` (864 -> 447 Zeilen) nach `round_controller.py` und `compat.py`.
  - Aufteilung von `player_view.py` (693 -> 316 Zeilen) nach `player_ui_builder.py`.
  - Aufteilung von `settings_player.py` (668 -> 345 Zeilen) nach `settings_player_effects.py`.
  - Aufteilung von `theme.py` (633 -> 20 Zeilen) nach `resources.py`, `qss_base.py` und `qss_components.py`.
  - Aufteilung von `models.py` (631 -> 118 Zeilen) in `models_base.py`, `folder_track_model.py` und `playlist_table_model.py`.
  - Aufteilung von `metadata.py` (621 -> 420 Zeilen) in `cover_art.py`.
  - Aufteilung von `playlist_view.py` (603 -> 284 Zeilen) in `playlist_ui_builder.py` und `playlist_table_view.py`.
  - Aufteilung von `logs_view.py` (512 -> 426 Zeilen) in `log_detail_dialog.py`.
  - Aufteilung von `folders_page.py` (~970 -> 406 Zeilen) in `folders_tree.py` und `folders_trash.py`.
- **Rationalisierung und Zusammenführung von Duplikaten:**
  - Zentralisierung der gemeinsamen Komponenten (`ClickableSlider`, `EffectContainer`, `EffectsViewMixin`).
  - Faktorisierung generischer UI-Bezeichnungen unter dem gemeinsamen Präfix `common.*` (`common.cancel`, `common.close`, `common.refresh`, `common.later`, `common.open_explorer`, `table.col_filename`, `table.col_source`, `table.col_folder_name`).
- Obligatorische Normalisierung der Windows-Zeilenenden CRLF (`\r\n`) für alle `.bat`-Dateien.

### Behoben

- **Harmonisierung und Eliminierung von Übersetzungsresten in 41 Sprachen:**
  - Eliminierung von über 1.400 Schlüsseln, die noch auf Französisch oder als Standardenglisch verblieben waren, mittels des neuen Tools `scripts/fix_residual_translations.py` (`scripts/fix_residual_translations.bat`).
  - Korrektur der Beschriftungen für visuelle Atmosphäre und grafische Effekte (`player.visual_effect`, `effects.*`), die nun nativ in allen Sprachen übersetzt sind.
  - Behebung hybrider Such-Platzhalter (`topbar.search_placeholder`), die Zielsprache und Englisch auf den Bildschirmen Duplikate, Quellen und Navigation vermischen.
  - Treue Übersetzung der Titel für die Quellen-Einstellungen (`settings.page_sources_title`, `settings.section_sources_title`) und die allgemeine Konfiguration (`settings.page_title`).
  - Vollständige Übersetzung des gemeinsamen Aktualisierungs-Buttons (`common.refresh` : « 🔄 刷新 » auf Chinesisch, etc.) anstelle eines verbliebenen französischen „Actualiser“ in den Protokollen.
  - Vollständige Lokalisierung der Abschnitte für Unterstützung, Spenden und offizielle Links auf der Über-uns-Seite (`dialog.about_*`, `update.btn_support`).

---

## [0.3.0] - 2026-10-18

### Hinzugefügt

- **Volle Unterstützung von Playlist-Dateien** :
  - Automatische Indizierung von Playlist-Formaten: `.m3u`, `.m3u8`, `.pls`, `.xspf` und `.wpl`.
  - Integration in die Verzeichnisstruktur „Nach Ordner“ in Form dedizierter Knoten, die das Icon **`🎶`** tragen.
  - Beibehaltung der sequenziellen Abspielreihenfolge, die in der Playlist definiert ist (Spalte `#` mit der Reihenfolge 1, 2, 3...) ohne erzwungte automatische alphabetische Sortierung.
  - Verwaltung und visuelle Erkennung fehlender oder verschobener Titel: Indikation durch ein Präfix **`⚠️`**, sanfte Warnfarbgebung und beschreibender Info-Bubble, ohne die Wiedergabe anderer Titel zu blockieren.
  - Erweiterte Kontextmenüs für Playlist-Knoten: Direktwiedergabe, Hinzufügen zur Warteschlange und Öffnen des Playlist-Dateipfades im Windows Explorer.
- **Sanftes Einblenden des Klangs (*Fade-in*)** :
  - Progressiver Übergang der Lautstärke von 0% auf die eingestellte Lautstärke über 1 Sekunde beim Start oder Wiederaufnehmen einer Audiowiedergabe (außer im Blind Test Modus).
- **Stabilität und Flüssigkeit der Synchronisierung** :
  - Entfernung des blockierenden Dialogfensters „Scan already running“ zugunsten einer stillen Warteschlangenabfolge.
  - Beibehaltung der Auswahl und keine unnötige Neuladung der Ordnerstruktur, wenn keine Ordneränderung erkannt wird.
- **Dynamische Anzeige der Cover** :
  - Korrektur der Größenänderung und Neupositionierung des Covers beim Wechsel zwischen Vollbild / Fenster oder bei der freien Größenänderung des Fensters.

---

## [0.2.0] - 2026-10-18

### Hinzugefügt

### Blind Test-Modus & Spielebereich

- **Neue Schublade „🎲 Jeux“** : Dedizierte, ausklappbare Kategorie in der Seitenleiste, die die Blind Test-Ansicht beherbergt (verfügbar in 5 Sprachen).
- **Immersives Spielerlebnis** : Dynamischer visueller Countdown in der Mitte des verdeckten Covers, progressive Enthüllung durch sanftes Dimmen und automatische Staffelfolge.
- **Erweiterte Akustiksteuerung** : Präzereinstellung der Such-, Entdeckungs- und des ausgehenden Sound-Dimms (*fade-out*).
- **Dedizierte Konfiguration** : Verlagerung der Blind Test-Einstellungen in `Paramètres > Lecteur`.

### Ergonomie & Playlist-Verwaltung

- **Überarbeitung des Zufallsmodus (Shuffle)** : Visuelles Durchmischen der Warteschlange, wobei der aktive Titel erhalten bleibt, ein direkter Aktionsknopf „🎲 Titel mischen“ und eine treue Wiederherstellung der ursprünglichen Reihenfolge bei Deaktivierung.
- **Neuorganisation per Drag-and-Drop** : Fließende Neuordnung der Titel mit der Maus in der Liste, ohne die Wiedergabe zu unterbrechen.
- **Asynchrone Sicherung v2** : Kompaktes Format mittels SQLite-IDs, das den Speicherbedarf um 99 % reduziert (nicht-blockierende Zugriffe, konstante 60 FPS).
- **Verhalten „Kein Autoplay“** : Das Hinzufügen von Titeln zur Warteschlange erzwingt nicht mehr den vorzeitigen Start der Wiedergabe.

### Bibliotheksverwaltung & Intelligenter Papierkorb

- **Zwei-stufige Löschung** : Wahl zwischen dem einfachen Entfernen der Bibliothek (mit gespeicherter Auschlussliste für zukünftige Scans) und der physischen Löschung in den Windows-Papierkorb.
- **Dedizierte Ansicht „ 🗑️ Papierkorb“** : Überprüfung der ausgeschlossenen Titel und Wiederherstellung mit einem Klick mit automatischer Reintegration in die Datenbank.
- **Optimierte Verzeichnisstruktur** : Visuelle Unterscheidung zwischen lokalen und Cloud-Quellen, Verzeichnisstruktur standardmäßig beim Start eingeklappt und standardisierte Kontextmenüs.

### Stabilität der Audio-Engine (LibVLC) & Performance

- **Beseitigung kritischer Blockaden** : Entfernung des Deadlocks zwischen dem internen C-Thread von LibVLC und der Qt-Ereignisschleife (Ende von Interface-Einfrierungen und weißen Bildschirmen).
- **Robustheit der Übergänge** : Anti-Reentrant-Lock bei schnellen Titelwechseln und Behebung von Blockaden bei aufeinanderfolgenden Zurückspulen („Vorheriger Ausschnitt“).
- **Zuverlässige Lautstärkesteuerung** : Integration des Lautstärkereglers in die obere Leiste des Players und Behebung von Konflikten bei DirectSound-Dämpfungen.

### Interface & Offizielle Links

- **Modernisierung der Seite „Über uns“** : Neuausgerichtete Kopfzeile, interaktiver Retro-Spektrumanalysator unter dem Text integriert und Hinzufügen der offiziellen Buttons (Ko-fi, GitHub Sponsors, GitHub, Itch.io).
- **Vollständige Internationalisierung** : Vollständige Synchronisierung aller Bezeichnungen und Optionen in 5 Sprachen (FR, EN, ES, DE, IT).

### Behoben

- **Behebung von `disk I/O error`-Fehlern (SQLite unter Windows)**: einmalige Konfiguration des WAL-Modus bei der Initialisierung der Datenbankdatei, Hinzufügen von `PRAGMA busy_timeout = 30000`, temporärer Speicher im RAM-Speicher (`PRAGMA temp_store = MEMORY`) und ein Mechanismus für automatische Wiederholungsversuche mit exponentiellem Backoff, um Sperrkonflikte bei multithreaded Scans zu beseitigen.
- **Entfernung blockierender modaler Warnungen im Hintergrund**: führen automatische Hintergrundsynchronisierungen bei vorübergehenden Fehlern keine störenden modalen Dialogfelder mehr an, sondern protokollieren die Warnung sauber im Aktivitätsprotokoll und in der klickbaren Statusleiste.
- **Zu geringes Audio-Volumen beim Start**: Beseitigung eines Race-Conditions bei der Initialisierung des VLC-Player-Engines und Neutralisierung der automatischen Dämpfung (*ducking*) des Windows-Audio-Mixers.
- **Anzeige des offiziellen Logos in der Windows-Executable**: Korrektur der Multi-Pfad-Auflösung eingebetteter PyInstaller-Ressourcen (`sys._MEIPASS`), um das AMSO-Logo in hoher Auflösung in der Seitenleiste und der Über-uns-Seite anstelle des Platzhalter-Icons 🎵 anzuzeigen.
- **Wiederherstellung der Playlist und hermetische Isolierung der Tests**: Beseitigung einer Verunreinigung des Benutzerprofils, bei der die Ausführung automatisierter Tests `saved_playlist.json` mit gefälschten Tracks (*Track 1, Track 2, Track 3*) und einer falschen Zeitposition (14:10 bei einem Stück von 3:00) überschreiben konnte. Vollständige Isolierung von `AMSO_DATA_DIR`, `AMSO_PLAYLIST_PATH` und `AMSO_DB_PATH` in der Testumgebung, automatische Filterung lokaler Phantom- oder nicht auffindbarer Tracks beim Laden der Playlist und Sicherung der Startposition, um niemals die Dauer des Titels zu überschreiten.
- **Optimierung der Startzeit mit großen Playlists (Eliminierung des Einfrierens bei 85 %)**: Beseitigung eines blockierenden Engpasses im Hauptthread während der Wiederherstellung der Wiedergabesitzung. Die Validierung der Playlist führte Tausende synchroner Disk-Aufrufe `Path.exists()` durch (~40 Sekunden für 12 000 Titel). Sie verwendet nun eine sofortige In-Memory-Überprüfung O(1) (< 1 ms) für alle Titel aus der aktiven SQLite-Datenbank, was den Anwendungsstart augenblicklich macht.
- **Fließende Schritt-für-Schritt-Fortschrittsanzeige und Eliminierung des visuellen Rückspringens des Splash Screens**: Überarbeitung der Fortschrittsverfolgung beim Start mit einer fließenden Schritt-für-Schritt-Animation von 1 % auf 1 % (10 ms pro Inkrement) für einen kontinuierlichen und sauberen Übergang zwischen den regulären Stufen (15 % Präferenzen, 25 % Thema, 35 % SQLite, 45 % Audiomotor, 60 % Oberfläche, 75 % Bibliothek, 90 % Sitzungswiederherstellung, 100 % Fertigstellung). Behebung eines globalen CSS-Stilkonflikts, bei dem die Anwendung des Dark Themes ein `max-width: 220px` auf allen Fortschrittsbalken vorschrieb, wodurch die Breite des Splash Screens plötzlich halbiert und die visuelle Illusion eines Rückspringens der blauen Anzeige erzeugt wurde. Sicherung der Breite (`#splashProgressBar`), Sperrung des streng monotonen Fortschritts und Entfernung der überflüssigen Angabe rechts im Footer.
- **Visuelles Rendern des Standard-Cover-Art (Vinyl & Notiz)**: Entfernung des vertikalen Beschneidens an der rechten Kante des Notensymbols in der Mitte des Vinyls, das durch die Anwendung eines synthetischen Fettdrucks (*synthetic bold*) des DirectWrite-Schrifttreibers unter Windows verursacht wurde.
- **Strikte Erkennung von Ordner-Covern (*folder cover*)** : Verbesserung des Algorithmus zur Bildsuche im Verzeichnis, um nur legitime Covernamen zu akzeptieren (`folder`, `cover`, `front`, Titel, `album`, `artwork`) und willkürliche oder präfixierte Bilder abzulehnen (z. B. `exfolder.webp`). Sofortige Cache-Invalidierung bei jeder Umbenennung oder Löschung im Ordner, um zuverlässig auf das Standard-Vinyl-Visual zu wechseln (« integriertes Cover > Bildordner > Musik-Vinyl »).

---

## [0.1.0] - 2026-10-17

### Hinzugefügt

- **Integriertes Audio-Wiedergabe-Engine (python-vlc):**
  - Native Unterstützung gängiger Audioformate: MP3, FLAC, WAV, AAC, OGG, M4A, WMA.
  - Transparente Erkennung und automatischer Download eines portablen VLC-Binärs, falls VLC auf dem System des Benutzers fehlt.
  - Volle Wiedergabesteuerung: Play, Pause, Stop, Nächster Titel, Vorheriger Titel, dynamischer Fortschrittsbalken (Seekbar) und Lautstärkeregelung.
  - Wiedergabemodi: Zufallswiedergabe (*Shuffle*) und Wiederholungsmodi (*Deaktiviert*, *Playlist wiederholen*, *Titel in Schleife wiederholen*).
  - Echtzeit-animierte visuelle Effekte, synchronisiert mit der Wiedergabe (Partikel, Wellen, Sterne, räumliche Verzerrung, Nordlichter, Spektralbalken).
- **Playlist- und Warteschlangen-Manager:**
  - Dedizierte Ansicht mit virtualisierter Tabelle, die zehntausende von Titeln ohne Latenz unterstützt.
  - Intuitive Neuorganisation der Warteschlange per Drag & Drop (*Drag & Drop*).
  - Vollständige Kontextmenüs: „Abspielen“, „Zur Warteschlange hinzufügen“, „Aus der Warteschlange entfernen“, „Eigenschaften“.
- Automatische Speicherung der Wiedergabesitzung (aktueller Titel, zeitliche Position in ms, aktive Playlist).
- **Hochleistungsfähiger multithreaded lokaler Scanner:**
  - Asynchrone rekursive Durchsicht lokaler Verzeichnisse mit Fortschrittsbalken und Echtzeit-Metriken.
  - Schnelle Extraktion von Metadaten (Titel, Künstler, Album, Jahr, Genre, Dauer, Bitrate, Tracknummer) über `mutagen`.
  - Extraktion und Caching integrierter Album-Cover mit asynchroner Darstellung, um jegliches Einfrieren der Benutzeroberfläche zu vermeiden.
  - Berechnung von Datei-Hash-Prägen zur Identifizierung physischer Duplikate.
- **Optimierte SQLite-Datenbank:**
  - Relationale Architektur ohne schweres ORM für nahezu augenblickliche Abfrageausführung.
  - Verwaltung von Quellen, gescannten Titeln und Aktivitätsverlauf.
- **Moderne Benutzeroberfläche (PySide6 / Dark Mode) :**
  - Hochwertiges, personalisiertes Dark-Theme mit sorgfältiger Farbpalette und sanften Animationen.
  - Ausziehbare Seitenleiste für die Hauptnavigation und Einstellungen.
  - Vollständige Mehrsprachigkeit (Französisch, Englisch, Spanisch, Deutsch, Italienisch) mit Hot-Swap-Sprachwechsel.
  - Dedizierte „Über“-Seite in den Einstellungen: Projektdetails, Versions-Badge, Open-Source-Technologien, Links zu GitHub, Itch.io und Spendenplattformen (Ko-fi, GitHub Sponsors).
- Manueller und automatischer Update-Prüfer, der die GitHub Releases API (`/releases/latest`) abfragt, mit interaktiver Benachrichtigungsleiste.
- Tastenkürzel <kbd>F1</kbd> und direkter Klick auf das AMSO-Logo, um die Seite „Über uns“ zu öffnen.

### Geändert

- Ersetzen des Modal-Dialogs „Über“ durch eine integrierte und flüssige Unterseite in den Einstellungen.
- Neuorganisation der Einstellungsnavigation in 5 Abschnitte: Allgemein, Player, Quellen, Protokolle, Über.
- Verbergen der verbleibenden Standard-Menüleiste zugunsten einer aufgeräumten Oberfläche ohne verwaister „Hilfe“-Button.

### Behoben

- **Start bei 00:00:** Systematisches Zurücksetzen der Zeitposition (`_pending_seek_ms = 0`) bei der Auswahl einer neuen Musik aus der Bibliothek oder der Playlist, wobei die Wiederaufnahme der Position nur auf den « Play »-Button der wiederhergestellten vorherigen Sitzung beschränkt wird.
- **Sofortige Volumenpersistenz:** Sofortige Speicherung in `config.ini` bei jeder Manipulation des Lautstärkereglers oder des Stummschaltknopfes.
- **VLC-Volumenverriegelung:** Automatische Resynchronisierung der Audiolautstärke beim Übergang in den Zustand `Playing` in der Takt-Schleife, um jeglichen Verlust von Einstellungen beim Kaltstart des VLC-Decoders zu vermeiden.
