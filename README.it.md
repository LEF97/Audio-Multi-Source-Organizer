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

> **AMSO** è un'applicazione desktop open-source e multipiattaforma progettata per unificare, deduplicare e sincronizzare librerie musicali ibride distribuite tra dischi locali, archiviazione cloud (Google Drive) e piattaforme di streaming (Spotify, Deezer e Amazon Music).

---

## 📌 Funzionalità e Stato del Progetto

| Funzionalità | Descrizione | Stato |
| :--- | :--- | :---: |
| **Scanner locale multithreading** | Esplorazione e indicizzazione rapida e ricorsiva di file audio locali (MP3, FLAC, AAC, OGG...) | 🟢 Implementato |
| **Estrazione di metadati e copertine** | Lettura/scrittura tag ID3, commenti Vorbis e impronta acustica (`mutagen`) | 🟢 Implementato |
| **Motore di riproduzione VLC integrato** | Lettore audio leggero con auto-installazione di VLC portatile e controllo fluido del volume | 🟢 Implementato |
| **Gestione Playlist e Coda** | Coda virtualizzata, drag & drop, riproduzione casuale (shuffle) e ripetizione | 🟢 Implementato |
| **Interfaccia grafica moderna PySide6** | Tema scuro elegante, visualizzatore audio in tempo reale, interfaccia in 5 lingue | 🟢 Implementato |
| **Verifica aggiornamenti in-app** | Controllo automatico e manuale delle versioni tramite GitHub Releases | 🟢 Implementado |
| **Hub Artisti e Discografia** | Vista dedicata per artista con album, singoli e discografia completa | 🟡 Previsto |
| **Equalizzatore grafico (EQ)** | Profili sonori predefiniti ed equalizzatore parametrico multibanda | 🟡 Previsto |
| **Connettore Google Drive** | Scansione e sincronizzazione di raccolte musicali remote tramite OAuth 2.0 | ⚪ Pianificato |
| **Connettore Amazon Music** | Scansione e sincronizzazione di cartelle musicali remote tramite OAuth 2.0 | ⚪ Pianificato |
| **Integrazione Spotify / Deezer** | Importazione di playlist e corrispondenza delle tracce | ⚪ Pianificato |
| **Deduplicazione intelligente** | Rilevamento duplicati basato su metadati sfumati e impronte acustiche | ⚪ Pianificato |

> 💡 *Per consultare i dettagli delle tappe e delle versioni future, consultare la [Tabella di marcia (ROADMAP.it.md)](ROADMAP.it.md).*

---

## 🚀 Guida Rapida

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

# 3. Attivare l'ambiente
# Su Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Su Linux / macOS:
source .venv/bin/activate

# 4. Installare le dipendenze
pip install -r requirements.txt

# Per sviluppo e test:
pip install -e .[dev]

# 5. Avviare AMSO
python main.py
```

---

## 🧪 Esecuzione dei Test

La suite di test automatizzati si basa su `pytest`:

```bash
pytest -v
```

---

## 💖 Sostieni il Progetto e Distribuzione

AMSO è un software libero e open-source. Se ti piace il progetto e desideri supportarne lo sviluppo:

* 🎮 **Scarica e Paga quanto vuoi:** [AMSO su Itch.io](https://lef97.itch.io/audio-multi-source-organizer) (eseguibile portatile precompilato)
* ☕ **Donazione Diretta:** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
* ⭐ **GitHub Sponsors:** [Sponsorizza LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licenza

Questo progetto è rilasciato sotto licenza **GNU General Public License v3.0 (GPL-3.0)** — consultare il file [LICENSE](LICENSE) per tutti i dettagli.
