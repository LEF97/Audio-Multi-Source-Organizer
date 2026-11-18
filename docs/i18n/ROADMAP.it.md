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

### 🟢 Version 0.1.0 — Il Fondamento Locale Robusto

- [x] Scanner locale multithread con estrazione dei metadati (ID3, Vorbis Comments, FLAC).
- [x] Motore di riproduzione audio integrato (python-vlc) con auto-installazione VLC portatile.
- [x] Visualizzazione Playlist completa con riorganizzazione drag-and-drop, riproduzione casuale e cicli.
- [x] Salvataggio automatico della sessione di riproduzione (posizione, volume, lista).
- [x] Interfaccia moderna in Dark Mode con effetti visivi reattivi.
- [x] Internazionalizzazione completa (FR, EN, ES, DE, IT).
- [x] Sistema di notifica e verifica degli aggiornamenti tramite GitHub Releases.

---

### 🟢 Version 0.2.0 — Modalità Blind Test, Cestino & Ergonomia

- [x] **Modalità « 🎲 Giochi / Blind Test » immersiva:** Contatore con pulsazione animata, rivelazione progressiva con dissolvenza dolce, sequenziamento automatico e parametri dedicati.
- [x] **Gestione del Cestino e Ripristino:** Esclusione di brani, invio al cestino Windows e visualizzazione dedicata Cestino AMSO con ripristino istantaneo nella libreria.
- [x] **Riprogettazione della modalità Casuale (Shuffle) e Drag-and-Drop:** Miscelazione visiva completa, ordine reversibile e riorganizzazione della playlist con il mouse.
- [x] **Ottimizzazioni delle prestazioni e persistenza:** Formato di salvataggio compatto asincrono (-99 % di spazio su disco) ed eliminazione delle latenze all'avvio.
- [x] **Ergonomia del Lettore e Navigazione:** Nuovo « Giochi » drawer, cursore del volume integrato nell'intestazione del Lettore, avvio predefinito sul Lettore.

---

### 🟢 Version 0.3.0 — Supporto per le Playlist, Dissolvenza Audio & Robustezza

- [x] **Supporto completo delle playlist:** Indicizzazione automatica dei formati `.m3u`, `.m3u8`, `.pls`, `.xspf`, `.wpl` nella vista per cartella con l'icona `🎶`.
- [x] **Ordine sequenziale e gestione dei brani mancanti:** Rispetta l'ordine originale della playlist e rileva visivamente i file mancanti (`⚠️`) senza interruzione della riproduzione.
- [x] **Dissolvenza sonora acustica (*Fade-in*)**: Aumento graduale del volume all'avvio e alla ripresa di una riproduzione audio.
- [x] **Fluidità della sincronizzazione:** Coda continua in background senza pop-up intrusivi e preservazione dell'albero delle cartelle.
- [x] **Regolazione dinamica delle copertine:** Ricentro e dimensionamento fluido durante il passaggio da schermo intero / finestra.

---

### 🟢 Version 0.4.0 — Esperienza Audio Avanzata & Fogli CUE

- [x] **Rifacimento modulare dell'architettura e Quality Gate:** Suddivisione dell'applicazione in moduli coesivi (< 500 righe), modularizzazione di MainWindow in mixins dedicati (amso/ui/pages/), decomposizione del servizio audio in sottosistemi indipendenti (player_transport, player_queue, player_transitions) e implementazione di un telaio di validazione automatizzato (scripts/verify.py & .bat : ruff, mypy, pytest, controllo delle dimensioni).
- [x] **Integrazione Windows Shell e barra delle applicazioni:** Pinaggio nativo diretto dall'icona attiva (AppUserModelID esplicito LEF97.AMSO.AudioPlayer) fin dal punto di ingresso main.py e persistenza del collegamento durante gli aggiornamenti.
- [x] **Ascolto perfetto Gapless 0 tra due tracce:** Ora sono disponibili 2 motori, uno basato su VLC_direct, l'altro che funziona in modalità buffer (modalità preferita). Queste modalità consentono un ascolto fluido per gli album con tracce collegate (Alan Parsons, Pink Floyd, Mike Oldfield, ecc...)
- [x] **Supporto per i fogli CUE (`.cue`) :** Un file `.cue` viene visualizzato come una cartella di tracce virtuali (💿) con la loro durata e viene riprodotto come vere tracce (motore a buffer continuo).

---

### 🟢 Version 0.4.1 — Affidabilità audio, log tradotto & versioni Linux / macOS sperimentali

- [x] **Uscita audio indipendente dal thread dell'interfaccia:** il `QAudioSink` del motore `buffer` è alimentato da un thread audio dedicato (modalità pull); spostare o ridimensionare la finestra non altera più l'audio.
- [x] **Blind Test nel motore `buffer`:** Riproduzione, Avanti e Indietro avviano l'audio senza dover ripremere Riproduzione.
- [x] **Traduzioni completate:** registro attività salvato in chiave + parametri e tradotto visualmente, testi hardcoded convertiti, fallback al francese, controllo dei marcatori `{nom}` alla sincronizzazione.
- [x] **Stato di libVLC:** versione e provenienza (copia AMSO o VLC del sistema) nelle impostazioni del lettore.
- [x] **Deployment multi-piattaforma (Linux & macOS), versione sperimentale non testata:** packaging automatizzato tramite GitHub Actions per Linux (.AppImage / .tar.gz) e macOS Apple Silicon ARM & Intel (.dmg non firmato), VLC richiesto; i tester restituiscono `startup.log` e `crash.log`.

---

### 🟢 Version 0.5.0 — Sources & Libreria, Editor di Playlist & Transizioni *(Attuale)*

- [x] **Vista "Sorgenti e Libreria":** dashboard unificato con stato di salute delle sorgenti/playlist, navigazione per sorgente e azioni rapide.
- [x] **Editor, riparazione ed esportazione delle playlist:** riorganizzazione, rilocazione manuale o automatica (locale + database), e salvataggio in `.m3u`, `.m3u8`, `.pls`, `.xspf` o `.wpl`.
- [x] **Playlist in modalità album:** raggruppamento dei brani di una playlist in cartelle virtuali per album nella struttura ad albero, con " (album sconosciuto) " per i brani senza album.
- [x] **Transizioni di copertina, scansione in 3 fasi e geometria della finestra:** 5 effetti di transizione, progressione dettagliata della scansione e ripristino della finestra.
- [x] **Nuova icona AMSO:** icona ad alta risoluzione multi-dimensioni (PNG, ICO, ICNS).
- [x] **Strumenti audio:** equalizzatore grafico a 10 bande con preset, normalizzazione ReplayGain, velocità di riproduzione, scelta dell'uscita audio e timer di spegnimento (motore `buffer`).
- [x] **Collegamento continuo delle tracce CUE:** le tracce contigue di un singolo file vengono decodificate in un unico flusso (motore `buffer`).
- [x] **Guide di aiuto, pagine Suono ed Effetti, effetto Warp Pilot e modalità Casuale:** aiuto contestuale su ogni pagina, impostazioni dedicate per il suono e gli effetti visivi.
- [x] **Integrazione Windows:** barra delle applicazioni e icona nell'area di notifica.
- [x] **Crossfade parametrizzabile e Collegamenti audio avanzati:** Supporto per transizioni senza interruzioni (Gapless 0 ms), dissolvenza incrociata ad alta precisione (Crossfade Equal-Power) e modalità standard senza bianco.

---

### 🌟 Version x.0.0 — De-duplicazione Intelligente & Versione Stabile

- [ ] **Rilevamento acustico dell'impronta (Audio Fingerprinting):** Identificazione dei duplicati anche in caso di tag errati o file ri-encoderati.
- [ ] **Assistente di risoluzione dei duplicati:** Confronto intelligente della qualità (selezione automatica del miglior bitrate / lossless) con archiviazione sicura.
- [ ] **Packaging multi-piattaforma ufficiale:** Eseguibili firmati per Windows (`.exe` / portable), macOS (`.dmg` Apple Silicon & Intel) e Linux (`AppImage` / `.deb`).
- [ ] **Documentazione utente completa:** Guida passo passo illustrata e sito vetrina GitHub Pages.
- [ ] **Connettore Spotify (Web API):** Connessione all'account utente e recupero di playlist e preferiti.
- [ ] **Connettore Amazon Music:** Scansione, streaming e sincronizzazione di collezioni musicali remote (OAuth 2.0).
- [ ] **Matching ibrido intelligente:** Corrispondenza tra i titoli di una playlist remota e i file già presenti localmente (alta fedeltà).
- [ ] **Vista unificata:** Visualizzazione affiancata dei brani disponibili localmente e di quelli disponibili solo in streaming.
- [ ] **Autenticazione sicura OAuth 2.0:** Connessione semplificata tramite browser senza memorizzare segreti in chiaro.
- [ ] **Scansione remota delle cartelle Google Drive:** Indicizzazione dei file audio presenti nelle cartelle configurate.
- [ ] **Riproduzione diretta in streaming cloud:** Ascolto di brani remoti con cache locale trasparente.
- [ ] **Sincronizzazione bidirezionale selettiva:** Download locale di tracce dal cloud o backup di tracce locali su Drive.
- [ ] **Gestione artisti e discografia associata:** Visualizzazione dedicata per artista con album, singoli e discografia completa.
- [ ] **Editor di metadati in-app:** Modifica diretta dei tag ID3 / Vorbis su un o più file selezionati.
- [ ] **Download automatico delle copertine:** Ricerca online (MusicBrainz / Cover Art Archive) delle copertine mancanti.
- [ ] **Filtri di ricerca avanzati:** Filtraggio combinato per genere, anno, bitrate e formato Lossless.
- [ ] **Rilevamento dei mount di rete (Linux e macOS):** `amso/core/network_paths.py` riconosce oggi solo i percorsi UNC e le unità mappate Windows; riconoscere i mount NFS / SMB / AFP (`/proc/self/mountinfo`, `statfs`) per evitare qualsiasi sondaggio disco bloccante all'avvio su questi sistemi.
- [ ] **Validazione su Linux e macOS:** motore `buffer`, transizioni e packaging da confermare su sistemi reali sulla base dei feedback dei tester.

---

## 💡 Proporre una funzionalità

Un'idea o un bisogno specifico?

- Apri una discussione o un ticket su [GitHub Issues](https://github.com/LEF97/Audio-Multi-Source-Organizer/issues) usando il modello *Feature Request*.
- Partecipa ai voti della comunità per dare priorità allo sviluppo!
