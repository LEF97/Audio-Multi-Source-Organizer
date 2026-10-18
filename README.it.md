# Audio Multi-Source Organizer (AMSO)

<p align="right">
  <a href="README.fr.md">Français</a> • <a href="README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <b>Italiano</b>
</p>

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](CHANGELOG.it.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Traguardi%20futuri-purple.svg)](ROADMAP.it.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) è un riproduttore audio desktop moderno, reattivo e multipiattaforma (Windows, Linux, macOS). Progettato per offrire agli audiofili il pieno controllo sulla propria libreria musicale locale (MP3, FLAC, OGG…), supporta ora i file di playlist (M3U, PLS, XSPF, WPL) e include un nuovo minigioco interattivo di blind test musicale! Il progetto sta evolvendo per diventare un centro di comando unificato capace di organizzare, deduplicare e sincronizzare raccolte musicali ibride distribuite tra dischi locali, cloud storage (Google Drive) e servizi di streaming (Spotify, Deezer, Amazon Music).

---

<p align="center">
  <img src="screenshots/2026-10-18%20v0.3.0%2002.png" alt="Audio Multi-Source Organizer (AMSO) - Albero delle cartelle & Playlist 🎶" width="850">
</p>

<p align="center">
  <img src="screenshots/2026-10-18%20v0.3.0.png" alt="Audio Multi-Source Organizer (AMSO) - Riproduttore & Hyperspace" width="850">
</p>

<p align="center">
  <img src="screenshots/2026-10-18%20v0.3.0%20blind%20test.png" alt="Audio Multi-Source Organizer (AMSO) - Minigioco Blind Test" width="850">
</p>

---

## 📌 Funzionalità & Stato del Progetto

| Funzionalità | Descrizione | Stato |
| :--- | :--- | :---: |
| **Motore di riproduzione VLC integrato** | Lettore audio leggero e autonomo con installazione automatica di VLC portatile e controllo fluido del volume | 🟢 Implementato |
| **Scanner locale multithreading** | Esplorazione ricorsiva e rapida di file audio locali (MP3, FLAC, AAC, OGG...) | 🟢 Implementato |
| **Estrazione di metadati e copertine** | Lettura/scrittura tag ID3, commenti Vorbis e impronta acustica (`mutagen`) | 🟢 Implementato |
| **Supporto Playlist (M3U, PLS, XSPF, WPL)** | Indicizzazione nell'albero delle cartelle (🎶), ordine sequenziale di ascolto e avviso visivo tracce mancanti | 🟢 Implementato |
| **Gestione Playlist & Drag-and-Drop** | Coda virtualizzata, trascinamento fluido, modalità casuale (shuffle) reversibile e ripetizione | 🟢 Implementato |
| **Modalità « 🎲 Blind Test » interattiva** | Gioco musicale immersivo con conto alla rovescia animato, dissolvenza audio e avanzamento automatico | 🟢 Implementato |
| **Verifica aggiornamenti in-app** | Controllo automatico e manuale delle versioni tramite GitHub Releases | 🟢 Implementato |
| **Hub Artisti & Discografia** | Vista dedicata per artista con album, singoli e discografia completa | 🟡 Previsto |
| **Equalizzatore grafico (EQ)** | Profili sonori predefiniti ed equalizzatore parametrico multibanda | 🟡 Previsto |
| **Connettore Google Drive** | Scansione e sincronizzazione di raccolte remote nel cloud tramite OAuth 2.0 | ⚪ Pianificato |
| **Connettore Amazon Music** | Scansione e sincronizzazione di cartelle musicali remote tramite OAuth 2.0 | ⚪ Pianificato |
| **Integrazione streaming Spotify / Deezer** | Importazione di playlist e corrispondenza ibrida dei brani | ⚪ Pianificato |
| **Deduplicazione intelligente** | Rilevamento duplicati basato su metadati sfumati e impronte acustiche | ⚪ Pianificato |

> 💡 *Per consultare i dettagli delle tappe e delle versioni future, fare riferimento alla [Tabella di marcia (ROADMAP.it.md)](ROADMAP.it.md).*

---

## 🚀 Avvio Rapido

### Prerequisiti
- **Python 3.11** o superiore
- Git

### Installazione

```bash
# 1. Clonare il repository
git clone https://github.com/LEF97/Audio-Multi-Source-Organizer.git
cd audio-multi-source-organizer

# 2. Creare l'ambiente virtuale
python -m venv .venv

# 3. Attivare l'ambiente virtuale
# Su Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Su Linux / macOS:
source .venv/bin/activate

# 4. Installare le dipendenze
pip install -r requirements.txt

# Per lo sviluppo e l'esecuzione dei test:
pip install -e .[dev]

# 5. Configurare le variabili d'ambiente
cp .env.example .env

# 6. Avviare l'applicazione
python main.py
```

---

## 🧪 Esecuzione dei Test

La suite di test automatizzati si basa su `pytest` e copre test unitari e di integrazione:

```bash
pytest -v
```

I test vengono eseguiti automaticamente su **Windows, macOS e Ubuntu** a ogni push tramite GitHub Actions.

---

## 🔒 Sicurezza & Chiavi API

- **Non eseguire mai il commit di chiavi API o token di autenticazione reali.**
- Il file `.gitignore` è preconfigurato per escludere `.env`, `credentials.json`, `token.json` e database SQLite locali.
- Utilizzare `.env.example` come modello per l'ambiente di sviluppo locale.

---

## 📋 Documentazione & Tracciamento del Progetto

- 📜 **[CHANGELOG.it.md](CHANGELOG.it.md)** ([Version Française](CHANGELOG.fr.md) • [English Version](CHANGELOG.md)): Registro dettagliato delle versioni, nuove funzionalità e correzioni.
- 🗺️ **[ROADMAP.it.md](ROADMAP.it.md)** ([Version Française](ROADMAP.fr.md) • [English Version](ROADMAP.md)): Tabella di marcia con traguardi futuri (Artisti, Cloud, Spotify, Deduplicazione).
- 📐 **[CODE_QUALITY.md](CODE_QUALITY.md)**: Standard di architettura software e linee guida sulla qualità del codice.

---

## 💖 Supporta il Progetto & Distribuzione

AMSO è un software libero e open source. Se apprezzi l'applicazione e desideri sostenerne lo sviluppo:

* 🎮 **Scarica & Paga quello che desideri:** [Pagina di AMSO su Itch.io](https://lef97.itch.io/audio-multi-source-organizer) (eseguibile portatile precompilato)
* ☕ **Donazione diretta:** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
* ⭐ **GitHub Sponsors:** [Sponsorizza LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licenza

Questo progetto è rilasciato sotto licenza **GNU General Public License v3.0 (GPL-3.0)** — consultare il file [LICENSE](LICENSE) per tutti i dettagli.
