# Registro delle modifiche (Changelog) — AMSO

<p align="right">
  <a href="CHANGELOG.fr.md">Français</a> • <a href="CHANGELOG.md">English</a> • <a href="CHANGELOG.es.md">Español</a> • <a href="CHANGELOG.de.md">Deutsch</a> • <b>Italiano</b>
</p>

---

Tutte le modifiche rilevanti apportate al progetto **Audio Multi-Source Organizer (AMSO)** sono documentate in questo file.

Il formato si basa su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/) e aderisce a [Semantic Versioning (SemVer)](https://semver.org/).

---

## [0.4.0-dev] - In sviluppo

### Added
- **Supporto esteso per 43 lingue internazionali:**
  - Integrazione di 38 nuove lingue con nomi nativi nel selettore di lingua (`amso/core/i18n.py`).
  - Traduzione automatizzata a lotti e parità completa (401 chiavi per lingua) tramite IA locale Ollama (`mistral:latest`).
  - Script di sincronizzazione globale con un clic: `scripts/sync_all_languages_ollama.bat`.
- **Modalità di diagnosi visiva delle traduzioni (`⟦...⟧`):**
  - Argomento CLI `--debug-i18n` e file `run_debug_i18n.bat` che racchiudono le stringhe tradotte tra parentesi `⟦...⟧` per verificare sullo schermo i testi dinamici.
- **Strumento di audit e integrità i18n (`scripts/audit_translations.py`):**
  - Verifica automatica della parità di tutte le 43 lingue, rilevamento dei duplicati da unificare e identificazione delle chiavi orfane.
- **Integrazione Windows Shell e Barra delle applicazioni:** Dichiarazione prioritaria di `AppUserModelID` (`LEF97.AMSO.AudioPlayer`) in `main.py` prima dell'avvio di Qt.
- **Sistema unificato di controllo qualità (Quality Gate):** Script `scripts/verify.py` e `verify.bat` per eseguire Ruff, Mypy rigido, limiti di righe e Pytest.

### Changed
- **Suddivisione modulare completa dell'architettura (< 500 righe per file):**
  - Obiettivo raggiunto al 100%: **0 file > 500 righe** nell'intera base di codice AMSO.
  - Riduzione di `main_window.py` (~1 500 -> 357 righe) tramite mixin dedicati in `amso/ui/pages/`.
  - Decomposizione di `player_service.py` (~1 400 -> 329 righe) in `player_transport.py`, `player_queue.py`, `player_transitions.py` e `windows_audio.py`.
  - Suddivisione di `blind_test_view.py` (864 -> 447), `player_view.py` (693 -> 316), `settings_player.py` (668 -> 345), `theme.py` (633 -> 20), `models.py` (631 -> 118), `metadata.py` (621 -> 420), `playlist_view.py` (603 -> 284), `logs_view.py` (512 -> 426).
- **Razionalizzazione e unificazione dei duplicati:**
  - Componenti condivisi estratti (`ClickableSlider`, `EffectContainer`, `EffectsViewMixin`).
  - Azioni comuni unificate sotto `common.*` (`common.cancel`, `common.close`, `common.refresh`, `common.later`, `common.open_explorer`).
  - Fine riga Windows CRLF (`\r\n`) obbligatoria su tutti i file `.bat`.

---

## [0.3.0] - 2026-10-18

### Added
- **Supporto completo per i file di playlist**:
  - Scansione e indicizzazione automatica dei formati playlist `.m3u`, `.m3u8`, `.pls`, `.xspf` e `.wpl`.
  - Nodi dedicati nell'albero delle cartelle contrassegnati dall'icona **`🎶`**.
  - Rigoroso rispetto dell'ordine naturale di ascolto della playlist (colonna `#` con 1, 2, 3...) senza ordinamento alfabetico forzato.
  - Rilevamento visivo chiaro dei brani mancanti o spostati (prefisso **`⚠️`**, evidenziazione di avviso e tooltip descrittivo) senza interrompere la riproduzione.
  - Menu contestuale ampliato per i nodi playlist: riproduzione diretta, aggiunta alla coda, riproduci come successivo e mostra in Esplora file di Windows.
- **Dissolvenza audio in ingresso morbida (*Fade-in*)**:
  - Transizione graduale del volume da 0% al livello impostato in 1 secondo all'avvio o alla ripresa della riproduzione (eccetto in modalità Blind Test).
- **Stabilità e fluidità della sincronizzazione in background**:
  - Sostituzione della finestra modale invasiva «Scan already running» con un accodamento silenzioso in background.
  - Mantenimento della selezione e dello stato dell'albero delle cartelle senza ricaricamenti non necessari.
- **Presentazione dinamica delle copertine**:
  - Correzione di ridimensionamento e ricentratura durante il passaggio tra schermo intero e finestra o il ridimensionamento libero.

---

## [0.2.0] - 2026-10-18

### Added
- **Modalità Blind Test e sezione giochi**:
  - Nuovo cassetto comprimibile « 🎲 GIOCHI » nella barra laterale dedicato al minigioco interattivo Blind Test (localizzato in 5 lingue).
  - Esperienza immersiva: conto alla rovescia animato ad impulsi, rivelazione graduale in dissolvenza morbida, avanzamento automatico delle manche e precaricamento asincrono delle copertine in RAM.
- **Ergonomia del riproduttore e gestione playlist**:
  - Riprogettazione della modalità casuale (*Shuffle*): rimescolamento visivo dell'intera coda preservando il brano attivo, pulsante diretto « 🎲 Rimescola brani » e ripristino fedele dell'ordine originale alla disattivazione.
  - Riordinamento fluido tramite trascinamento (*Drag & Drop*) nella tabella della playlist senza interruzioni di riproduzione.
  - Persistenza asincrona v2 con identificatori SQLite compatti che riducono l'impronta su disco del 99% (accesso non bloccante a 60 FPS costanti).
  - Cursore del volume integrato nella barra superiore di navigazione per una vista del riproduttore chiara ed elegante.
- **Gestione libreria e cestino intelligente**:
  - Doppio livello di rimozione: esclusione logica dalla libreria (memorizzata per scansioni future) o eliminazione fisica nel Cestino di Windows.
  - Vista dedicata « 🗑️ Cestino » con ripristino in un clic e reinserimento immediato nel database.
- **Interfaccia e collegamenti ufficiali**:
  - Pagina « Info » rinnovata nelle Impostazioni con spettro interattivo e pulsanti di supporto ufficiali (Ko-fi, GitHub Sponsors, GitHub, Itch.io).
  - Internazionalizzazione completa in 5 lingue (francese, inglese, spagnolo, tedesco, italiano).

### Fixed
- **Risoluzione degli errori `disk I/O error` (SQLite su Windows)**: configurazione della modalità WAL una sola volta all'inizializzazione del database, `PRAGMA busy_timeout = 30000`, archiviazione temporanea in memoria RAM (`PRAGMA temp_store = MEMORY`) e meccanismo di tentativi automatici con backoff esponenziale per eliminare i conflitti di blocco dei file durante le scansioni multithread.
- **Eliminazione degli avvisi modali bloccanti in background**: le sincronizzazioni automatiche non mostrano più finestre modali di errore invadenti in caso di problemi temporanei, registrando l'evento nel registro attività e nella barra di stato cliccabile.
- **Volume audio troppo basso all'avvio**: rimozione di una race condition durante l'inizializzazione del motore VLC e neutralizzazione dell'attenuazione automatica (*ducking*) del mixer audio di Windows.
- **Visualizzazione del logo ufficiale nell'eseguibile Windows**: correzione della risoluzione multi-percorso delle risorse incorporate PyInstaller (`sys._MEIPASS`) per visualizzare il logo AMSO ad alta definizione nella barra laterale e nella pagina Info invece dell'icona di fallback 🎵.
- **Ottimizzazione del tempo di avvio con grandi librerie**: eliminazione di verifiche sincrone su disco durante il ripristino della sessione, rendendo l'avvio istantaneo in O(1) tramite SQLite.
- **Progressione fluida dello Splash Screen**: animazione passo-passo continua (1% all'1%) senza arretramento visivo della barra di caricamento.

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
