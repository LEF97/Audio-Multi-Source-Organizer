# Tabella di marcia (Roadmap) — AMSO

<p align="right">
  <a href="ROADMAP.fr.md">Français</a> • <a href="ROADMAP.md">English</a> • <a href="ROADMAP.es.md">Español</a> • <a href="ROADMAP.de.md">Deutsch</a> • <b>Italiano</b>
</p>

---

Questo documento illustra la direzione strategica, le funzionalità pianificate e le tappe future del progetto **Audio Multi-Source Organizer (AMSO)**.

---

## 🎯 Visione del Progetto

AMSO mira a essere l'**hub musicale universale e decentralizzato** per eccellenza: veloce, leggero, elegante e rispettoso della privacy. Consente di gestire la propria musica su dischi locali, cloud o servizi di streaming.

---

## 🗺️ Tappe e Versioni

### 🟢 Versione 0.1.0 — Lancio Iniziale & Fondamenta (Ottobre 2026)
- **Stato :** ✅ Completato
- Motore di riproduzione nativo con supporto python-vlc e download automatico di VLC portatile.
- Scansione multithreading e indicizzazione rapida in SQLite.
- Gestione playlist con drag & drop e salvataggio della sessione.
- Interfaccia moderna PySide6 (Dark Mode) con 5 lingue (FR, EN, ES, DE, IT).
- Verifica in-app automatica e manuale degli aggiornamenti (GitHub Releases).

---

### 🟡 Versione 0.2.0 — Hub Artisti & Qualità Audio (Novembre 2026)
- **Vista Artisti :** Navigazione per artista con discografia completa.
- **Equalizzatore grafico (EQ) :** Preimpostazioni ed equalizzatore parametrico a più bande.
- **Transizioni avanzate :** Modalità Gapless e Crossfade fluide.

---

### ⚪ Versione 0.3.0 — Connettori Cloud (Dicembre 2026)
- **Google Drive :** Connessione OAuth 2.0 e sincronizzazione cloud.
- **Amazon Music :** Esplorazione remota e sincronizzazione cartelle musicali.

---

### ⚪ Versione 0.4.0 — Deduplicazione Intelligente & Streaming (Gennaio 2027)
- **Deduplicazione avanzata :** Rilevamento tramite impronta acustica e metadati approssimati.
- **Spotify / Deezer :** Importazione di playlist e corrispondenza ibrida.

---

### ⚪ Versione 1.0.0 — Stabilità ed Ecosistema Completo (Q1 2027)
- Sincronizzazione bidirezionale completa.
- Architettura a plugin.
- Test di carico per librerie con oltre 100.000 brani.
