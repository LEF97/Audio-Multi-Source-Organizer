# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <b>Italiano</b> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](CHANGELOG.it.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](ROADMAP.it.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) è un lettore audio desktop moderno, reattivo e multi-piattaforma (Windows, Linux, macOS). Progettato per offrire agli audiofili un controllo totale sulla loro libreria musicale locale (MP3, FLAC, OGG…), ora supporta le playlist (M3U, PLS, XSPF, WPL), i file CUE (album di un singolo file tagliati in tracce) e integra una nuovissima modalità blind test audio! Il progetto si evolve per diventare un centro di comando unificato in grado di organizzare, de-duplicare e sincronizzare collezioni musicali ibride distribuite tra dischi locali, storage cloud (Google Drive) e servizi di streaming (Spotify, Deezer, Amazon Music).

---

<p align="center">
  <img src="../../screenshots/2026-10-25%20v0.4.0%2002.png" alt="Audio Multi-Source Organizer (AMSO) - Arborescence par dossiers & feuille CUE 💿 (pistes virtuelles)" width="850">
</p>

<p align="center">
  <img src="../../screenshots/2026-10-25%20v0.4.0.png" alt="Audio Multi-Source Organizer (AMSO) - Liste de lecture d'une feuille CUE (pistes virtuelles)" width="850">
</p>

<p align="center">
  <img src="../../screenshots/2026-10-18%20v0.3.0%20blind%20test.png" alt="Audio Multi-Source Organizer (AMSO) - Mini-jeu Blind Test & Décompte dynamique" width="850">
</p>

---

## 📌 Funzionalità & Stato del progetto

| Funzionalità | Descrizione | Stato |
| :--- | :---: | :---: |
| **Motore di riproduzione VLC integrato** | Lettore audio leggero e autonomo con auto-installazione VLC portatile e gestione fluida del volume | 🟢 Implementato |
| **Scanner locale multithread** | Scoperta ricorsiva e rapida dei file audio locali (MP3, FLAC, AAC, OGG...) | 🟢 Implementato |
| **Estrazione metadati** | Lettura/scrittura ID3, Vorbis Comments e calcolo dell'impronta audio (`mutagen`) | 🟢 Implementato |
| **Supporto Playliste (M3U, PLS, XSPF, WPL) e fogli CUE** | Indicizzazione ad albero (🎶), ordine di ascolto sequenziale, rilevamento visivo dei brani mancanti; i file `.cue` (💿) si aprono come una cartella di tracce virtuali con la loro durata e si riproducono come tracce reali | 🟢 Implementato |
| **Gestore Playliste e Drag & Drop** | Coda virtualizzata, drag & drop fluido, casuale (shuffle) reversibile e cicli | 🟢 Implementato |
| **Modalità "🎲 Blind Test" interattiva** | Gioco musicale immersivo con conto alla rovescia animato, dissolvenza sonora, rivelazione graduale e sequenziamento automatico | 🟢 Implementato |
| **Aggiornamenti in-app** | Verifica automatica/manuale delle versioni via GitHub Releases | 🟢 Implementato |
| **Gestione artisti & Discografia** | Vista dedicata per artista con album, singoli e discografia completa | 🟡 Previsto |
| **Equalizzatore grafico (EQ)** | Preset audio e equalizzatore multibanda parametrico | 🟡 Previsto |
| **Connettore Google Drive** | Scansione e sincronizzazione di collezioni audio remote via OAuth 2.0 | ⚪ Pianificato |
| **Connettore Amazon Music** | Scansione e sincronizzazione di collezioni remote via OAuth 2.0 | ⚪ Pianificato |
| **Connettore Spotify / Deezer** | Importazione di playlist e corrispondenza di tracce | ⚪ Pianificato |
| **Deduping intelligente** | Rilevamento duplicati (titolo/artista sfocati + impronte acustiche) | ⚪ Pianificato |

> 💡 *Per consultare il dettaglio delle tappe e delle versioni previste, fare riferimento alla [Roadmap (Roadmap)](ROADMAP.it.md).*

---

## 📌 Lingue disponibili

Inglese, Francese, Spagnolo, Tedesco, Italiano, Portoghese, Giapponese, Russo, Polacco, Turco, Olandese, Svedese, Indonesiano, Bulgaro, Serbo, Bielorusso, Greco, Catalano, Basco, Galiziano, Ceco, Slovacco, Ungherese, Croato, Sloveno, Bosniaco, Estone, Lettone, Lituano, Norvegese, Danese, Finlandese, Islandese, Malese, Tagalog, Swahili, Esperanto, Cinese semplificato, Cinese tradizionale, Coreano, Arabo, Ebraico, Vietnamita

---

## 🚀 Avvio rapido

### Prerequisiti

- **Python 3.11** o superiore installato
- Git

### Installazione

```bash
# 1. Cloner le dépôt
git clone https://github.com/LEF97/Audio-Multi-Source-Organizer.git
cd audio-multi-source-organizer

# 2. Créer l'environnement virtuel
python -m venv .venv

# 3. Activer l'environnement
# Sous Windows (PowerShell) :
.venv\Scripts\Activate.ps1
# Sous Linux / macOS :
source .venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# Pour le développement et les tests :
pip install -e .[dev]

# 5. Configurer les variables d'environnement
cp .env.example .env

# 6. Lancer l'application
python main.py
```

---

## 🧪 Avvio dei test

Il progetto utilizza `pytest` con una suite di test unitari e di integrazione:

```bash
pytest -v
```

I test vengono eseguiti automaticamente su **Windows, macOS e Ubuntu** ad ogni push tramite GitHub Actions.

---

## 🔒 Sicurezza & Chiavi API

- **Non committare mai chiavi API o token di autenticazione reali.**
- Il file `.gitignore` è pre-configurato per bloccare `.env`, `credentials.json`, `token.json` e tutti i database SQLite locali.
- Usa `.env.example` come modello per il tuo ambiente di sviluppo.

---

## 📋 Documentazione & Monitoraggio del progetto

- 📜 **[CHANGELOG.fr.md](CHANGELOG.it.md)** : Registro dettagliato delle versioni, delle nuove funzionalità e delle correzioni di bug.
- 🗺️ **[ROADMAP.fr.md](ROADMAP.it.md)** : Roadmap dei futuri traguardi (Artisti, Cloud, Spotify, De-duplicazione).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Carta di architettura software e regole di qualità del codice.

---

## 💖 Supportare il progetto & Distribuzione

AMSO è un software libero e gratuito (open source). Se apprezzate l'applicazione e desiderate incoraggiare il suo sviluppo:

- 🎮 **Download & Paga Quanto Vuoi :** [Pagina Itch.io di AMSO](https://lef97.itch.io/audio-multi-source-organizer) (eseguibile precompilato pronto all'uso)
- ☕ **Fare una donazione diretta :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [Sponsorizza LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licenza

Questo progetto è sotto licenza **GNU General Public License v3.0 (GPL-3.0)** — consulta il file [LICENSE](../../LICENSE) per maggiori dettagli.
