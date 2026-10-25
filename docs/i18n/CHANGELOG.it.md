# Registro delle modifiche (Changelog) — AMSO

<p align="right">
  <a href="../../CHANGELOG.fr.md">Français</a> • <a href="../../CHANGELOG.md">English</a> • <a href="CHANGELOG.es.md">Español</a> • <a href="CHANGELOG.de.md">Deutsch</a> • <b>Italiano</b>
</p>

---

Tutte le modifiche significative apportate al progetto **Audio Multi-Source Organizer (AMSO)** sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/)
e questo progetto aderisce alla specifica [Semantic Versioning (SemVer)](https://semver.org/lang/fr/).

---

## [0.4.0] - 2026-10-25

### Aggiunto
- **Supporto per i file CUE (`.cue`):**
  - Un file `.cue` appare nell'albero come una cartella virtuale (icona 💿) contenente i suoi brani con titolo, artista e durata; il file audio originale rimane leggibile normalmente.
  - Riproduzione di un brano CUE come porzione del file (inizio `INDEX 01`, fine all'inizio del brano successivo, ultimo brano fino alla fine del file) con posizione e durata proprie del brano, spostamento nel brano e collegamento gapless / crossfade tra porzioni (solo motore a buffer continuo; il motore `vlc_direct` visualizza un messaggio esplicativo).
  - Tolleranza per i file mal formati (riga `FILE` che punta al `.cue` stesso: fallback sul file audio dello stesso nome), più `FILE` per file, codifiche UTF-8 / CP1252.
- **Supporto esteso per 43 lingue internazionali:**
  - Integrazione di 38 nuove lingue con le loro etichette native nel selettore di lingua (`amso/core/i18n.py`).
  - Traduzione automatizzata e parità integrale (401 chiavi per lingua) tramite l'IA locale Ollama (`mistral:latest`).
  - Script di sincronizzazione globale con un clic: `scripts/sync_all_languages_ollama.bat`.
- **Modalità di diagnostica visiva delle traduzioni (`⟦...⟧`) :**
  - Aggiunta dell'argomento CLI `--debug-i18n` e dello script `run_debug_i18n.bat` che racchiude ogni testo tradotto tra i tag `⟦...⟧` per individuare immediatamente sullo schermo i testi dinamici e isolare eventuali stringhe hardcoded.
- **Strumento di audit e integrità i18n (`scripts/audit_translations.py`) :**
  - Rilevamento automatico della parità delle 43 lingue, rilevamento di duplicati di etichette da fondere e identificazione delle chiavi orfane tramite `scripts/audit_translations.bat`.
- **Selettore di architettura audio nelle Impostazioni / Riproduzione perfetta in modalità gapless 0 (rimangono alcune anomalie in modalità cross fade) :**
  - Scelta trasparente in `Paramètres > Lecteur` tra:
    - *Buffer continuo in memoria (QAudioSink / WASAPI)* : flusso unico ininterrotto verso la scheda audio, transizioni gapless 0 e dissolvenza senza interruzione hardware.
- *Uscita diretta LibVLC (doppio lettore hardware)* : motore hardware classico pilotato direttamente da LibVLC.
- **Telaio di validazione qualità unificato (Quality Gate) :** Creazione dello script `scripts/verify.py` e del suo wrapper radice `verify.bat` che esegue consecutivamente il formattamento (Ruff), il linter (Ruff check), il tipaggio rigoroso (Mypy senza mascheramento), il controllo dei limiti di dimensione dei file e i test automatizzati (Pytest).

### Fixed
- **Playliste e fogli CUE scoperti: registro di attività e aggiornamento dell'albero:** un'analisi che aggiungeva solo playlist (M3U, PLS, XSPF, WPL, CUE) non era menzionata da nessuna parte e non aggiornava l'albero delle cartelle (il nuovo nodo appariva solo dopo un riavvio). Il registro indica ora il numero di playlist/fogli CUE aggiunti, aggiornati o eliminati (con i primi nomi), e l'albero si aggiorna alla fine dell'analisi.
- **Motore audio nativo WASAPI & Risoluzione dell'interruzione prematura alla fine del brano:**
  - *Uscita audio nativa Windows WASAPI (`mmdevice`)*: eliminazione del forzare `--aout=directsound` su Windows. Il modulo DirectSound di VLC troncava in modo anomalo gli ultimi 1,3-1,4 secondi dei file audio (tagliando la fine di *Sirius*). L'allineamento su `mmdevice` consente a LibVLC di trasmettere l'intero flusso audio fino all'ultimo millisecondo in 32-bit float.
  - *Rimozione dei bops e artefatti di click rapidi*: eliminazione dei tagli artificiali di volume a 0 durante i `seek` e `stop` che causavano discontinuità di fase e collisioni di timer asincroni durante i click rapidi. Il riposizionamento temporale (`set_time`) e l'arresto vengono ora eseguiti in modo nativo e fluido.
  - *Rimozione dei micro-glitch alla fine del brano / passaggi calmi*: arresto del polling permanente del volume nel ciclo di tick, evitando di inviare continui e ripetitivi aggiustamenti di guadagno hardware durante la riproduzione.
- **Precisione millimetrica delle transizioni & Collegamenti fluidi (Gapless & Senza dissolvenza) :**
  - *Eliminazione di scatti e pop all'avvio del brano successivo* : soppressione del forzamento del volume a 0 sul secondo lettore in standby, che causava una interruzione globale della sessione sotto WASAPI e poi un transitorio impulsivo ("scatto") allo sblocco della pausa. Il secondo lettore viene precaricato in pausa (`:start-paused`) al volume nominale senza alterare il brano corrente.
  - *Collegamento senza interruzioni (Gapless 0)* : considerazione esatta della latenza del pipeline LibVLC (`vlc_gapless_latency_ms`, 250 ms di default) per sbloccare il lettore successivo prima della fine esatta del brano corrente, garantendo una continuità musicale ininterrotta senza alcun silenzio tra brani collegati (*Sirius* -> *Eye In The Sky*).
  - *Collegamento naturale in modalità Crossfade* : soppressione del ritardo artificiale di 400 ms dopo `State.Ended`, consentendo una transizione immediata e pulita alla fine della riproduzione del brano precedente.
- **Rimozione dei trigger di riproduzione audio inappropriati :**
  - *Ritorno indietro (`previous` / `seek`)* : il comando brano precedente (`previous()`) rispetta strettamente lo stato di pausa del lettore e utilizza `load_index()` per caricare il brano senza avviare la riproduzione se il lettore era in pausa. Allo stesso modo, uno spostamento temporale (`seek_ms`) annulla qualsiasi precaricamento in standby o svuotamento di transizione in attesa, e riposiziona il brano senza riproduzione forzata se il lettore era in pausa o alla fine del brano (`State.Ended`).
  - *Navigazione tra menu (uscita dal Blind Test verso altre schede)* : centralizzazione della navigazione delle schede (`_switch_to_page`), arresto forzato del Blind Test e ripristino di qualsiasi standby attivo all'uscita dalla pagina per impedire qualsiasi riavvio autonomo della musica in background.
- **Crossfade senza scatti (Crossfade Equal-Power) :**
  - *Isolation matérielle des volumes sous Windows* : affectation dynamique de la sortie audio `directsound` pour le mode fondu enchaîné (les modes standard et gapless demeurent sur `mmdevice` natif sans troncature). Contrairement à WASAPI (`mmdevice`) dont le réglage de volume affecte la session de processus globale et générait un conflit violent (hachage / saccades à 40 Hz entre le titre sortant et le titre entrant), DirectSound isole le volume propre à chaque mémoire tampon secondaire (`IDirectSoundBuffer::SetVolume`).
  - *Courbes de fondu parfaitement lisses* : transition en puissance égale continue (cosinus pour le titre sortant, sinus pour le titre entrant) sans aucun creux acoustique ni saccade au déclenchement du fondu.
- **Fiabilisation du Moteur Tampon Continu en Mémoire (Phase 2 - QAudioSink / Ring Buffer) :**
  - *Respect absolu de la pause sur retour arrière (`previous()`)* : `previous()` préserve désormais fidèlement l'état de pause, charge le morceau précédent sans déclencher la lecture, et suspend le flux audio sans micro-coupure ni redémarrage impromptu.
  - *Enchaînement naturel en mode Pas de fondu* : suppression du préchargement standby inutile en mode standard, transition directe via le cycle de chargement standard avec mise à jour immédiate du titre, de la pochette et de la durée exacte.
  - *Résolution des collisions et saccades en mode Gapless 0* : cycle de vie hermétique du décodeur standby, déconnexions/reconnexions complètes des signaux (`ready_to_play`, `chunk_decoded`), rétablissement du seek après raccord, et rejet strict des paquets PCM non appariés au titre courant dans le tampon mémoire.
  - *Fondu croisé en mémoire à puissance égale (Mode Crossfade)* :
    - Mixage PCM mathématique des échantillons 16-bit (courbes cos/sin à puissance égale) à partir de la tête de lecture courante (`_play_offset`), avec clamping anti-écrêtage.
- Separazione rigorosa tra l'attivazione audio del dissolvenza e il cambio dell'interfaccia grafica: l'UI rimane visualizzata sul titolo in uscita durante il suo progressivo dissolvenza, e passa al titolo in entrata esattamente all'estinzione naturale del brano, eliminando la rottura visiva e sonora prematura.
- Sincronizzazione e allineamento temporale continui: svuotamento istantaneo dei dati PCM consumati dalla traccia in uscita all'estinzione (`finish_crossfade`), ricalibrazione precisa dell'offset di riproduzione (`_base_offset_ms`) sulla durata esatta del dissolvenza, garantendo uno scorrimento continuo del cursore senza teletrasporto, così come un riposizionamento temporale (`seek_ms`) perfettamente allineato.
- Suddivisione modulare: estrazione di `amso/services/player_vlc_transitions.py` (transizioni dirette LibVLC) che permette di mantenere tutti i file del player sotto le 450 righe.
  - *Reset completo e a caldo del player (`reset_playback`)*:
    - Qualsiasi modifica nelle Impostazioni del motore audio (*VLC diretto* vs *Buffer continuo*) o del modo di transizione (*Nessun dissolvenza*, *Gapless 0*, *Crossfade*) interrompe immediatamente la riproduzione in corso e ripristina completamente i flussi (distruzione pulita di `QAudioSink`, svuotamento dei buffer PCM in memoria, arresto dei decoder, disconnessione dei media LibVLC, annullamento di tutti i timer di transizione/dissolvenza).
    - La traccia attiva rimane selezionata in pausa a 00:00 pronta per essere avviata con la nuova configurazione senza la necessità di riavviare l'applicazione.


### Modifiche
- **Suddivisione modulare completa dell'architettura (< 500 righe per file):**
  - Obiettivo raggiunto al 100 %: **0 file > 500 righe** su tutto il codice base AMSO (contro 8 file sopra la soglia inizialmente).
  - Alleggerimento di `main_window.py` (~1 500 -> 357 righe) tramite mixin specializzati in `amso/ui/pages/`.
  - Scomposizione di `player_service.py` (~1 400 -> 329 righe) con l'estrazione di `player_transport.py`, `player_queue.py`, `player_transitions.py` e `windows_audio.py`.
  - Divisione di `blind_test_view.py` (864 -> 447 righe) in `round_controller.py` e `compat.py`.
  - Divisione di `player_view.py` (693 -> 316 righe) in `player_ui_builder.py`.
  - Divisione di `settings_player.py` (668 -> 345 righe) in `settings_player_effects.py`.
  - Suddivisione di `theme.py` (633 -> 20 righe) in `resources.py`, `qss_base.py` e `qss_components.py`.
  - Suddivisione di `models.py` (631 -> 118 righe) in `models_base.py`, `folder_track_model.py` e `playlist_table_model.py`.
  - Suddivisione di `metadata.py` (621 -> 420 righe) in `cover_art.py`.
  - Suddivisione di `playlist_view.py` (603 -> 284 righe) in `playlist_ui_builder.py` e `playlist_table_view.py`.
  - Suddivisione di `logs_view.py` (512 -> 426 righe) in `log_detail_dialog.py`.
  - Suddivisione di `folders_page.py` (~970 -> 406 righe) in `folders_tree.py` e `folders_trash.py`.
- **Razionalizzazione e fusione dei duplicati:**
  - Centralizzazione dei componenti condivisi (`ClickableSlider`, `EffectContainer`, `EffectsViewMixin`).
- Fattorizzazione delle etichette UI generiche sotto il prefisso condiviso `common.*` (`common.cancel`, `common.close`, `common.refresh`, `common.later`, `common.open_explorer`, `table.col_filename`, `table.col_source`, `table.col_folder_name`).
- Normalizzazione obbligatoria delle fine riga Windows CRLF (`\r\n`) su tutti i file `.bat`.

### Corretti
- **Armonizzazione ed eliminazione dei residui di traduzione nelle 41 lingue:**
  - Eradicazione di oltre 1 400 chiavi rimaste in francese o in inglese predefinito tramite il nuovo strumento `scripts/fix_residual_translations.py` (`scripts/fix_residual_translations.bat`).
  - Correzione delle etichette di atmosfera visiva e degli effetti grafici (`player.visual_effect`, `effects.*`), ora tradotti nativamente in tutte le lingue.
  - Risoluzione dei placeholder di ricerca ibridi (`topbar.search_placeholder`) che mescolano lingua di destinazione e inglese sugli schermi Duplicati, Sorgenti e Navigazione.
  - Traduzione fedele dei titoli di configurazione delle sorgenti (`settings.page_sources_title`, `settings.section_sources_title`) e della configurazione generale (`settings.page_title`).
  - Traduzione completa del pulsante condiviso di aggiornamento (`common.refresh` : « 🔄 刷新 » in cinese, ecc.) invece di un residuo "Actualiser" francese nei log.
  - Localizzazione completa delle sezioni di supporto, donazioni e link ufficiali della pagina Chi siamo (`dialog.about_*`, `update.btn_support`).

---

## [0.3.0] - 2026-10-18

### Aggiunto
- **Supporto completo per i file di playlist** :
  - Indicizzazione automatica dei formati di playlist: `.m3u`, `.m3u8`, `.pls`, `.xspf` e `.wpl`.
  - Integrazione nell'albero "Per cartella" sotto forma di nodi dedicati che mostrano l'icona **`🎶`**.
  - Rispetto dell'ordine di ascolto sequenziale definito nella playlist (colonna `#` con l'ordine 1, 2, 3...) senza forzare un ordinamento alfabetico automatico.
  - Gestione e rilevamento visivo di brani mancanti o spostati: indicazione tramite un prefisso **`⚠️`**, colorazione di avviso delicata e tooltip descrittivo, senza bloccare la riproduzione degli altri brani.
  - Menu contestuale arricchito sui nodi di playlist: riproduzione diretta, aggiunta alla coda e apertura della posizione del file playlist nell'Esplora file di Windows.
- **Dolce dissolvenza d'ingresso (*Fade-in*)** :
  - Transizione graduale del volume dallo 0% al volume impostato in 1 secondo all'avvio o alla ripresa di una riproduzione audio (fuori modalità Blind Test).
- **Stabilità e fluidità della sincronizzazione** :
  - Rimozione della finestra di dialogo bloccante « Scan already running » a favore di una sequenza silenziosa in coda.
  - Mantenimento della selezione e non ricaricamento inutile dell'albero delle cartelle se non viene rilevato alcun cambiamento di cartella.
- **Visualizzazione dinamica delle copertine** :
  - Correzione del ridimensionamento e del riposizionamento della copertina durante il passaggio a schermo intero/finestra o il ridimensionamento libero della finestra.

---

## [0.2.0] - 2026-10-18

### Aggiunto

### Mode Blind Test & Sezione Giochi
- **Nuovo scomparto « 🎲 Giochi »** : Categoria dedicata e collassabile nella barra laterale che ospita la vista Blind Test (localizzata in 5 lingue).
- **Esperienza di gioco immersiva** : Contatore visivo dinamico al centro della copertina mascherata, rivelazione progressiva con dissolvenza dolce e sequenza automatica dei round.
- **Gestione acustica avanzata** : Regolazione precisa dei tempi di ricerca, di scoperta e della dissolvenza sonora in uscita (*fade-out*).
- **Configurazione dedicata** : Spostamento delle impostazioni del Blind Test in `Parametri > Lettore`.

### Ergonomia e Gestione Playlist
- **Riprogettazione della modalità Casuale (Shuffle)** : Mescolamento visivo completo della coda che preserva il brano attivo, pulsante d'azione diretta « 🎲 Mescola i brani » e ripristino fedele dell'ordine originale non appena disattivato.
- **Riorganizzazione tramite Drag-and-Drop** : Riordinamento fluido dei brani con il mouse nella griglia senza interrompere la riproduzione.
- **Backup asincrono v2** : Formato compatto tramite identificatori SQLite che riduce l'occupazione del disco del 99 % (accesso non bloccanti, 60 FPS costanti).
- **Comportamento « No Autoplay »** : L'aggiunta di brani alla coda non forza più l'avvio prematuro della riproduzione.

### Gestione libreria & Cestino intelligente
- **Eliminazione a doppio livello** : Scelta tra la semplice rimozione della libreria (con esclusione memorizzata per futuri scan) e l'eliminazione fisica nel Cestino Windows.
- **Vista dedicata « 🗑️ Cestino »** : Consultazione dei brani esclusi e ripristino con un clic con reintegrazione automatica nel database.
- **Struttura ad albero chiarificata** : Distinzione visiva tra fonti locali e cloud, struttura ad albero ripiegata di default all'avvio e menu contestuali uniformati.

### Stabilità del motore audio (LibVLC) & Prestazioni
- **Eliminazione dei blocchi critici** : Rimozione del deadlock tra il thread C interno di LibVLC e il ciclo eventi Qt (fine dei blocchi dell'interfaccia e degli schermi bianchi).
- **Robustezza delle transizioni** : Blocco anti-ri-entrata sui cambi rapidi di traccia e risoluzione dei blocchi durante i rewind successivi (« Brano precedente »).
- **Controlli del volume affidabili** : Integrazione del cursore del volume nella barra superiore del lettore e rimozione dei conflitti di attenuazione sonora DirectSound.

### Interfaccia e Link ufficiali
- **Modernizzazione della pagina "Chi siamo"** : Intestazione riallineata, analizzatore di spettro retro interattivo integrato sotto il testo e aggiunta dei pulsanti ufficiali (Ko-fi, GitHub Sponsors, GitHub, Itch.io).
- **Internazionalizzazione completa** : Sincronizzazione completa di tutte le etichette e opzioni in 5 lingue (FR, EN, ES, DE, IT).

### Fixed
- **Risoluzione degli errori `disk I/O error` (SQLite su Windows)**: configurazione della modalità WAL una sola volta all'inizializzazione del file del database, aggiunta di `PRAGMA busy_timeout = 30000`, archiviazione temporanea in memoria RAM (`PRAGMA temp_store = MEMORY`) e meccanismo di riprova automatico con backoff esponenziale per eliminare i conflitti di blocco dei file durante gli scans multithread.
- **Rimozione delle allerte modali bloccanti in background** : le sincronizzazioni automatiche in background non mostrano più un dialogo modale intrusivo in caso di errore transitorio, ma registrano correttamente l'allerta nel log di attività e nella barra di stato cliccabile.
- **Volume audio troppo basso all'avvio** : eliminazione di una condizione di gara durante l'inizializzazione del motore di riproduzione VLC e neutralizzazione dell'attenuazione automatica (*ducking*) del mixer audio di Windows.
- **Visualizzazione del logo ufficiale nell'eseguibile Windows** : correzione della risoluzione multi-percorso delle risorse incorporate PyInstaller (`sys._MEIPASS`) per visualizzare il logo AMSO ad alta definizione nella barra laterale e nella pagina Informazioni anziché l'icona di riserva 🎵.
- **Ripristino della playlist e isolamento ermetico dei test** : eliminazione di un inquinamento del profilo utente dove l'esecuzione dei test automatici poteva sovrascrivere `saved_playlist.json` con tracce fittizie (*Track 1, Track 2, Track 3*) e una posizione temporale errata (14:10 su un brano di 3:00). Isolamento completo di `AMSO_DATA_DIR`, `AMSO_PLAYLIST_PATH` e `AMSO_DB_PATH` nell'ambiente di test, filtraggio automatico delle tracce locali fantasma o irreperibili durante il caricamento della playlist, e sicurezza della posizione iniziale per non superare mai la durata del brano.
- **Ottimizzazione del tempo di avvio con grandi playlist (eliminazione del blocco all'85%)** : eliminazione di un collo di bottiglia bloccante sul thread principale durante il ripristino della sessione di riproduzione. La convalida della playlist eseguiva migliaia di chiamate disco sincrone `Path.exists()` (~40 secondi per 12 000 brani). Ora privilegia un controllo istantaneo in memoria O(1) (< 1 ms) per tutti i brani provenienti dal database SQLite attivo, rendendo l'avvio dell'applicazione istantaneo.
- **Progressione fluida passo-passo ed eliminazione del ritardo visivo dello Splash Screen** : riprogettazione del monitoraggio della progressione all'avvio con animazione fluida passo-passo dell'1% in 1% (10 ms per incremento) per una transizione continua e curata tra le tappe regolari (15% preferenze, 25% tema, 35% SQLite, 45% motore audio, 60% interfaccia, 75% libreria, 90% ripristino sessione, 100% finalizzazione). Risoluzione di un conflitto di stile CSS globale in cui l'applicazione del tema scuro imponeva un `max-width: 220px` su tutte le barre di progressione, dividendo improvvisamente la larghezza dello splash screen per due e dando l'illusione visiva di un ritorno indietro del contatore blu. Santuario della larghezza (`#splashProgressBar`), blocco della progressione strettamente monotona e rimozione della menzione superflua a destra del piè di pagina.
- **Rendering visivo della copertina predefinita (vinile e nota)** : rimozione del ritaglio verticale sul bordo destro dell'icona di nota musicale al centro del vinile, causato dall'applicazione di un grassetto sintetico (*synthetic bold*) dal motore di font DirectWrite sull'emoji sotto Windows.
- **Rilevamento rigoroso delle copertine delle cartelle (*folder cover*)** : affidabilità dell'algoritmo di ricerca di immagini nella directory per accettare solo nomi di copertina legittimi (`folder`, `cover`, `front`, nom du morceau, `album`, `artwork`) e rifiutare immagini arbitrarie o prefissate (es. `exfolder.webp`). Invalidazione immediata della cache in caso di qualsiasi rinomina o eliminazione nella cartella per passare fedelmente alla visualizzazione vinile predefinita (« pochette intégrée > image folder > vinyle musique »).

---

## [0.1.0] - 2026-10-17

### Aggiunto
- **Motore di riproduzione audio integrato (python-vlc) :**
  - Supporto nativo per formati audio popolari: MP3, FLAC, WAV, AAC, OGG, M4A, WMA.
  - Rilevamento e download automatico trasparente di un binario VLC portatile in caso di assenza di VLC sul sistema utente.
  - Controllo completo della riproduzione: Play, Pause, Stop, Traccia successiva, Traccia precedente, barra di avanzamento dinamica (Seekbar) e gestione del volume.
  - Modalità di riproduzione: riproduzione casuale (*Shuffle*) e modalità di ripetizione (*Disattivato*, *Ripeti la playlist*, *Ripeti il brano in loop*).
  - Effetti visivi animati in tempo reale sincronizzati con la riproduzione (particelle, onde, stelle, distorsione spaziale, aurora boreale, barre dello spettro).
- **Gestore di Playlist e Coda :**
  - Vista dedicata con tabella virtualizzata che supporta decine di migliaia di titoli senza latenza.
  - Riorganizzazione intuitiva della coda tramite trascinamento (*Drag & Drop*).
  - Menu contestuali completi: « Riproduci », « Aggiungi alla coda », « Rimuovi dalla coda », « Proprietà ».
  - Salvataggio automatico della sessione di riproduzione (titolo corrente, posizione temporale in ms, playlist attiva).
- **Scanner locale multithread ad alte prestazioni:**
  - Percorso ricorsivo asincrono delle directory locali con barra di avanzamento e metriche in tempo reale.
  - Estrazione rapida dei metadati (titolo, artista, album, anno, genere, durata, bitrate, numero di traccia) tramite `mutagen`.
  - Estrazione e caching delle copertine degli album integrate con rendering asincrono per evitare qualsiasi blocco dell'interfaccia.
  - Calcolo delle impronte di hash del file per identificare i duplicati fisici.
- **Database SQLite ottimizzata:**
  - Architettura relazionale senza ORM pesante per un'esecuzione quasi istantanea delle query.
  - Gestione delle fonti, dei brani scansionati e della cronologia di attività.
- **Interfaccia Utente Moderna (PySide6 / Dark Mode):**
  - Tema scuro personalizzato di alta gamma con palette di colori curata e animazioni fluide.
  - Cassettiere laterale retrattile per la navigazione principale e le impostazioni.
  - Supporto multilingue completo (Francese, Inglese, Spagnolo, Tedesco, Italiano) con cambio lingua a caldo.
  - Pagina dedicata "Informazioni" nelle Impostazioni: dettagli del progetto, badge di versione, tecnologie open-source, link a GitHub, Itch.io e piattaforme di mecenat (Ko-fi, GitHub Sponsors).
  - Verificatore manuale e automatico di aggiornamenti che interroga l'API GitHub Releases (`/releases/latest`) con banner di notifica interattivo.
  - Scorciatoia da tastiera <kbd>F1</kbd> e clic diretto sul logo AMSO per aprire la pagina "Informazioni".

### Modifiche
- Sostituzione del dialogo modale « Informazioni » con una sottosezione integrata e fluida nelle Impostazioni.
- Riorganizzazione della navigazione delle Impostazioni in 5 sezioni: Generale, Lettore, Fonti, Log, Informazioni.
- Occultamento della barra dei menu standard residua a favore di un'interfaccia snella senza un pulsante « Aiuto » orfano.

### Fixed
- **Avvio a 00:00 :** Reset sistematico della posizione temporale (`_pending_seek_ms = 0`) durante la selezione di una nuova musica dalla libreria o dalla playlist, riservando il ripristino della posizione solo al pulsante « Play » della sessione precedente ripristinata.
- **Persistenza immediata del volume :** Salvataggio istantaneo in `config.ini` non appena viene manipolato il cursore del volume o il pulsante muto.
- **Blocco del volume VLC :** Resincronizzazione automatica del volume audio quando si passa allo stato `Playing` nel ciclo dell'orologio per evitare qualsiasi perdita di impostazioni durante l'avvio a freddo del decoder VLC.
