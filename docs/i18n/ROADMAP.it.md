# Roadmap (Roadmap) — AMSO

<p align="right">
  <a href="../../ROADMAP.fr.md">Français</a> • <a href="../../ROADMAP.md">English</a> • <a href="ROADMAP.es.md">Español</a> • <a href="ROADMAP.de.md">Deutsch</a> • <b>Italiano</b>
</p>

---

Questo documento dettaglia le direzioni strategiche, le funzionalità pianificate e i traguardi futuri del progetto **Audio Multi-Source Organizer (AMSO)**.

---

## 🎯 Visione del progetto

AMSO ha lo scopo di diventare l'hub musicale universale e decentralizzato di riferimento: un'applicazione veloce, leggera, elegante e senza compromessi sulla privacy, che permette a tutti di gestire la propria collezione audio, sia che sia archiviata su disco rigido, salvata nel cloud o consultata sui servizi di streaming.

---

## 🗺️ Tappe e Versioni

### 🟢 Version 0.1.0 — La Base Locale Robusta
- [x] Scanner locale multithread con estrazione dei metadati (ID3, Vorbis Comments, FLAC).
- [x] Motore di riproduzione audio integrato (python-vlc) con auto-installazione VLC portatile.
- [x] Visualizzazione Playlist completa con riorganizzazione drag-and-drop, riproduzione casuale e cicli.
- [x] Salvataggio automatico della sessione di riproduzione (posizione, volume, lista).
- [x] Interfaccia moderna in Dark Mode con effetti visivi reattivi.
- [x] Internazionalizzazione completa (FR, EN, ES, DE, IT).
- [x] Sistema di notifica e verifica aggiornamenti tramite GitHub Releases.

---

### 🟢 Versione 0.2.0 — Modalità Blind Test, Cestino & Ergonomia
- [x] **Modalità « 🎲 Giochi / Blind Test » immersiva:** Contatore con pulsazione animata, rivelazione progressiva con dissolvenza dolce, sequenziamento automatico e parametri dedicati.
- [x] **Gestione del Cestino & Ripristino:** Esclusione di brani, invio al cestino Windows e visualizzazione dedicata Cestino AMSO con ripristino istantaneo nella libreria.
- [x] **Riprogettazione della modalità Casuale (Shuffle) & Drag-and-Drop:** Miscelazione visiva completa, ordine reversibile e riorganizzazione della playlist con il mouse.
- [x] **Ottimizzazioni delle prestazioni e persistenza:** Formato di salvataggio compatto asincrono (-99 % di spazio disco) ed eliminazione delle latenze all'avvio.
- [x] **Ergonomia del Lettore & Navigazione:** Nuovo cassetto « Giochi », cursore del volume integrato nell'intestazione del Lettore, avvio predefinito sul Lettore.

---

### 🟢 Versione 0.3.0 — Supporto Playliste, Dissolvenza Audio & Robustezza
- [x] **Supporto completo delle playlist:** Indicizzazione automatica dei formati `.m3u`, `.m3u8`, `.pls`, `.xspf`, `.wpl` nella vista per cartella con l'icona `🎶`.
- [x] **Ordine sequenziale e gestione dei brani mancanti:** Rispetto dell'ordine originale della playlist e rilevamento visivo dei file mancanti (`⚠️`) senza interruzione della riproduzione.
- [x] **Dissolvenza sonora acustica (*Fade-in*) :** Aumento progressivo del volume nell'arco di 1 secondo all'avvio e alla ripresa di una riproduzione audio.
- [x] **Fluidità della sincronizzazione:** Coda continua in background senza pop-up invasivi e preservazione dell'albero delle cartelle.
- [x] **Regolazione dinamica delle copertine:** Ricentraggio e dimensionamento fluido durante il passaggio a schermo intero / finestra.

---

### 🟢 Versione 0.4.0 — Esperienza Audio Avanzata & Foglie CUE
- [x] **Rifacimento modulare dell'architettura & Quality Gate:** Suddivisione dell'applicazione in moduli coesi (< 500 righe), modularizzazione di MainWindow in mixins dedicati (amso/ui/pages/), decomposizione del servizio audio in sottosistemi indipendenti (player_transport, player_queue, player_transitions) e implementazione di un telaio di validazione automatizzato (scripts/verify.py & .bat : ruff, mypy, pytest, controllo delle dimensioni).
- [x] **Integrazione Windows Shell & barra delle applicazioni:** Pinaggio nativo diretto dall'icona attiva (AppUserModelID esplicito LEF97.AMSO.AudioPlayer) fin dal punto di ingresso main.py e persistenza del collegamento durante gli aggiornamenti.
- [x] **Ascolto Gapless 0 perfetto tra due tracce:** Ora sono disponibili 2 motori, uno basato su VLC_direct, l'altro che funziona in modalità buffer (funzionamento preferito). Queste modalità consentono un ascolto fluido sugli album con tracce collegate (Alan Parsons, Pink Floyd, Mike Oldfield, ecc...)
- [x] **Supporto per le foglie CUE (`.cue`) :** Un file `.cue` viene visualizzato come una cartella di tracce virtuali (💿) con la loro durata e viene letto come tracce reali (motore a buffer continuo).

---

### 🟢 Versione 0.4.1 — Affidabilità audio, log tradotto e versioni Linux / macOS sperimentali *(Attuale)*
- [x] **Uscita audio indipendente dal thread dell'interfaccia:** il `QAudioSink` del motore `buffer` è alimentato da un thread audio dedicato (modalità pull); spostare o ridimensionare la finestra non altera più l'audio.
- [x] **Test Cieco nel motore `buffer`:** Riproduzione, Avanti e Indietro avviano l'audio senza dover ripremere Riproduzione.
- [x] **Traduzioni completate:** registro di attività salvato con chiave + parametri e tradotto visualmente, testi hardcoded convertiti, fallback al francese, controllo dei marcatori `{nom}` alla sincronizzazione.
- [x] **Stato di libVLC:** versione e provenienza (copia AMSO o VLC del sistema) nelle impostazioni del lettore.
- [x] **Distribuzione multi-piattaforma (Linux e macOS), versione sperimentale non testata:** packaging automatizzato tramite GitHub Actions per Linux (.AppImage / .tar.gz) e macOS Apple Silicon ARM e Intel (.dmg non firmato), VLC richiesto; i tester restituiscono `startup.log` e `crash.log`.

---

### 🔵 Version 0.4.2 — Compatibilità di rete Linux & macOS
- [ ] **Rilevamento dei mount di rete (Linux & macOS):** `amso/core/network_paths.py` non riconosce oggi che i percorsi UNC e i drive mappati Windows; riconoscere i mount NFS / SMB / AFP (`/proc/self/mountinfo`, `statfs`) per evitare qualsiasi sondaggio disco bloccante all'avvio su questi sistemi.
- [ ] **Validazione su Linux e macOS:** motore `buffer`, transizioni e packaging da confermare su sistemi reali in base ai feedback dei tester.

---

### 🔵 Versione 0.5.0 — Navigazione per album nelle playlist
- [ ] **Playlist in modalità album:** opzione « Visualizza in modalità album » (attivata di default) che raggruppa i titoli di una playlist in cartelle virtuali per album nell'albero, con « (album sconosciuto) » per i titoli senza album e un'opzione aggiuntiva per playlist tramite clic destro.

---

### 🌟 Versione x.0.0 — De-duplicazione Intelligente & Versione Stabile
- [ ] **Rilevamento acustico dell'impronta (Audio Fingerprinting) :** Identificazione dei duplicati anche in caso di tag errati o file ri-encoderati.
- [ ] **Assistente di risoluzione dei duplicati :** Confronto intelligente di qualità (selezione automatica del miglior bitrate / lossless) con archiviazione sicura.
- [ ] **Packaging multi-piattaforma ufficiale :** Eseguabili firmati per Windows (`.exe` / portable), macOS (`.dmg` Apple Silicon & Intel) e Linux (`AppImage` / `.deb`).
- [ ] **Documentazione utente completa :** Guida passo-passo illustrata e sito vetrina GitHub Pages.
- [ ] **Connectore Spotify (Web API) :** Connessione dell'account utente e recupero di playlist e preferiti.
- [ ] **Connectore Amazon Music :** Scansione, streaming e sincronizzazione di collezioni musicali remote (OAuth 2.0).
- [ ] **Matching ibrido intelligente :** Corrispondenza tra i titoli di una playlist remota e i file già presenti localmente (alta fedeltà).
- [ ] **Vista unificata:** Visualizzazione affiancata dei brani disponibili localmente e di quelli disponibili solo in streaming.
- [ ] **Autenticazione sicura OAuth 2.0:** Connessione semplificata tramite browser senza memorizzare segreti in chiaro.
- [ ] **Scansione remota delle cartelle Google Drive:** Indicizzazione dei file audio presenti nelle cartelle configurate.
- [ ] **Riproduzione diretta in streaming cloud:** Ascolto dei brani remoti con cache locale trasparente.
- [ ] **Sincronizzazione bidirezionale selettiva:** Download locale dei brani dal cloud o backup dei brani locali su Drive.
- [ ] **Gestione artisti e discografia associata:** Vista dedicata per artista con album, singoli e discografia completa.
- [ ] **Equalizzatore grafico (EQ):** Preset (Rock, Pop, Jazz, Bass Boost) e equalizzatore parametrico multibanda.
- [ ] **Editor di metadati in-app:** Modifica diretta dei tag ID3 / Vorbis su un o più file selezionati.
- [ ] **Download automatico delle copertine :** Ricerca online (MusicBrainz / Cover Art Archive) delle copertine mancanti.
- [ ] **Filtri di ricerca avanzati :** Filtraggio combinato per genere, anno, bitrate e formato lossless.
- [x] **Crossfade parametrizzabile & Collegamenti audio avanzati :** Supporto per transizioni senza interruzioni (Gapless 0 ms), dello sfumare ad alta precisione (Crossfade Equal-Power) e della modalità standard senza bianco.

---

## 💡 Proporre una funzionalità

Un'idea o un bisogno specifico?
- Apri una discussione o un ticket su [GitHub Issues](https://github.com/LEF97/Audio-Multi-Source-Organizer/issues) utilizzando il modello *Feature Request*.
- Partecipa ai voti della comunità per dare priorità allo sviluppo!
