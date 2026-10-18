# Tabella di marcia (Roadmap) — AMSO

<p align="right">
  <a href="ROADMAP.fr.md">Français</a> • <a href="ROADMAP.md">English</a> • <a href="ROADMAP.es.md">Español</a> • <a href="ROADMAP.de.md">Deutsch</a> • <b>Italiano</b>
</p>

---

Questo documento illustra la direzione strategica, le funzionalità pianificate e le tappe future del progetto **Audio Multi-Source Organizer (AMSO)**.

---

## 🎯 Visione del Progetto

AMSO mira a essere l'**hub musicale universale e decentralizzato** per eccellenza: veloce, leggero, elegante e rispettoso della privacy. Consente a ciascuno di gestire la propria collezione musicale sia che si trovi su dischi locali, archiviata nel cloud o nei servizi di streaming online.

---

## 🗺️ Tappe e Versioni

### 🟢 Versione 0.1.0 — La Solida Base Locale
- [x] Scanner locale multithreading ad alte prestazioni con estrazione metadati (ID3, Vorbis Comments, FLAC).
- [x] Motore di riproduzione audio integrato (python-vlc) con download automatico di VLC portatile.
- [x] Vista completa della Playlist con riorganizzazione drag & drop, riproduzione casuale e ripetizione.
- [x] Salvataggio automatico della sessione (posizione di ascolto, volume, coda attiva).
- [x] Interfaccia moderna in Dark Mode con effetti visivi reattivi in tempo reale.
- [x] Internazionalizzazione completa (FR, EN, ES, DE, IT).
- [x] Sistema di notifiche e verifica degli aggiornamenti tramite GitHub Releases.

---

### 🟢 Versione 0.2.0 — Modalità Blind Test, Cestino & Ergonomia
- [x] **Modalità immersiva « 🎲 Giochi / Blind Test »:** Conto alla rovescia animato ad impulsi, rivelazione graduale in dissolvenza morbida, avanzamento automatico e impostazioni audio dedicate.
- [x] **Gestione del Cestino & Ripristino:** Esclusione tracce, invio al cestino di Windows e vista Cestino AMSO con ripristino istantaneo nella libreria.
- [x] **Nuova modalità Casuale (Shuffle) & Drag & Drop:** Rimescolamento visivo completo, ordine originale reversibile e riordinamento della playlist tramite mouse.
- [x] **Ottimizzazioni delle prestazioni e persistenza v2:** Formato compatto asincrono in SQLite (-99% di spazio su disco) e avvio istantaneo senza latenze.
- [x] **Ergonomia del Riproduttore & Navigazione:** Nuovo cassetto « Giochi » nella barra laterale, cursore del volume nell'intestazione e avvio diretto sul Riproduttore.

---

### 🟢 Versione 0.3.0 — Supporto Completo Playlist, Dissolvenza Audio & Robustezza *(Attuale)*
- [x] **Supporto completo dei file di playlist:** Indicizzazione automatica dei formati `.m3u`, `.m3u8`, `.pls`, `.xspf`, `.wpl` nella vista cartelle con l'icona `🎶`.
- [x] **Ordine sequenziale & segnalazione tracce mancanti:** Rispetto dell'ordine nativo della playlist (`#`) e avviso visivo per file mancanti (`⚠️`) senza interrompere la riproduzione.
- [x] **Dissolvenza audio in ingresso (*Fade-in*):** Aumento graduale del volume da 0% in 1 secondo all'avvio o alla ripresa di un brano.
- [x] **Sincronizzazione in background fluida:** Accodamento silenzioso in background senza finestre modali invasive e mantenimento dell'albero delle cartelle.
- [x] **Adattamento dinamico delle copertine:** Ridimensionamento e ricentratura fluida durante il passaggio tra schermo intero e finestra.

---

### 🟡 Versione 0.4.0 — Esperienza Audio Avanzata, Artisti & Packaging Multipiattaforma
- [ ] **Deployment multipiattaforma automatizzato (Linux & macOS):** Compilazione nativa e packaging automatizzato tramite GitHub Actions per Linux (`.AppImage` / `.tar.gz`) e macOS Apple Silicon ARM & Intel (`.dmg`), insieme all'eseguibile Windows.
- [ ] **Hub Artisti e Discografia Completa:** Vista dedicata per artista con album, singoli e discografia dettagliata.
- [ ] **Equalizzatore Grafico (EQ):** Preset audio (Rock, Pop, Jazz, Bass Boost) ed equalizzatore parametrico a più bande.
- [ ] **Editor di metadati integrato:** Modifica diretta dei tag ID3 / Vorbis su tracce singole o selezioni multiple.
- [ ] **Download automatico delle copertine:** Ricerca online (MusicBrainz / Cover Art Archive) delle copertine mancanti.
- [ ] **Filtri di ricerca avanzati:** Filtraggio combinato per genere, anno di pubblicazione, bitrate e formati senza perdita (Lossless).
- [ ] **Crossfade configurabile:** Transizione fluida e personalizzabile in dissolvenza incrociata tra i brani.

---

### 🔵 Versione 0.5.0 — Connettore Cloud Google Drive
- [ ] **Autenticazione sicura OAuth 2.0:** Accesso rapido tramite browser web senza salvare credenziali in chiaro.
- [ ] **Scansione remota delle cartelle Google Drive:** Indicizzazione dei brani audio presenti nelle cartelle configurate.
- [ ] **Streaming diretto dal cloud:** Ascolto di file audio remoti con memorizzazione trasparente nella cache locale.
- [ ] **Sincronizzazione bidirezionale selettiva:** Download di tracce dal cloud o caricamento di brani locali su Google Drive.

---

### 🟣 Versione 0.6.0 — Integrazioni Streaming (Spotify, Deezer & Amazon Music)
- [ ] **Connettore Spotify (Web API):** Connessione dell'account utente per importare playlist e libreria.
- [ ] **Connettore Amazon Music:** Scansione, streaming e sincronizzazione di raccolte musicali remote (OAuth 2.0).
- [ ] **Corrispondenza ibrida intelligente:** Riconoscimento automatico tra brani delle playlist remote e file locali in alta fedeltà.
- [ ] **Vista unificata della raccolta:** Visualizzazione affiancata di brani locali e tracce disponibili solo in streaming.

---

### 🌟 Versione 1.0.0 — Deduplicazione Intelligente & Versione Stabile
- [ ] **Impronta acustica digitale (Audio Fingerprinting):** Rilevamento duplicati affidabile anche con tag errati o formati ricodificati.
- [ ] **Assistente per la risoluzione dei duplicati:** Motore di confronto qualità (selezione automatica del miglior bitrate/lossless) con archiviazione sicura.
- [ ] **Pacchetti multipiattaforma ufficiali:** Installer firmati per Windows (`.exe` / portatile), macOS (`.dmg` Apple Silicon & Intel) e Linux (`AppImage` / `.deb`).
- [ ] **Documentazione utente completa:** Guida passo-passo illustrata e sito web vetrina su GitHub Pages.

---

## 💡 Proponi una funzionalità

Hai un'idea o una richiesta specifica?
- Apri una discussione o un ticket su [GitHub Issues](https://github.com/LEF97/Audio-Multi-Source-Organizer/issues) con il template *Feature Request*.
- Vota le proposte della community per definire le priorità di sviluppo!
