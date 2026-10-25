# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <b>Euskara</b> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) da amaierako reproduktore audio modernu, erantzun handiko eta plataformak askoan funtzionatzeko aukera dagoen bat (Windows, Linux, macOS). Audiophileek sira koherentzia osoa izan dezatenko (MP3, FLAC, OGG…) bestelako liburutegian diseinatuta dago, orain babestuteko aukera ditu playlistak (M3U, PLS, XSPF, WPL), CUE lehenak (arkibo bakar batean dagoen albumak urteetan zedeinak) eta mode blind test audio baten bidaibite berri bat arteko! Proiektua unifikatu zutabe-komando-zentro bateat izateko geratzen da, funtzionatzeko gaitasuna du liburutegiak sortzeko, duplikazioak nehiztzeko eta sinkronizatzeko, liburutegiak hibriduak, amaierako diskoetan, gordetxan *cloud* (Google Drive) eta *streaming* zerbitzuetan (Spotify, Deezer, Amazon Music) banatuak.

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

## 📌 Funtzionalitateak & Estatusa proiektuaren

| Funtzionalitatea | Deskribapioa | Estatusa |
| :--- | :--- | :---: |
| **VLC reproduktzaile integrazioa** | Reproduktzaile audio arrun eta autonomia, VLC portable auto-instalazioarekin eta gutxiak eragiltzenako volumen-eragozpenarekin | 🟢 Implémenté |
| **Skaner lokal multithread** | Arrendatu eta azkar audio-fitxak lokalak aurkitzea (MP3, FLAC, AAC, OGG...) | 🟢 Implémenté |
| **Metadatuak txukidatzea** | ID3, Vorbis Comments irakurri/izanji eta audio-hizkarrarako kalkulak (`mutagen`) | 🟢 Implémenté |
| **Playlistak (M3U, PLS, XSPF, WPL) eta CUE lehenpizkakoak babestekoa** | Indeksazio arboreskoa (🎶), bidaia sekuentziariko, iraupenak falta diren parluak ikusko; .cue fitxak (💿) virtuale bideak osatutako dosierrak irekitzen dira eta parluak benetako bideak zituzte | 🟢 Implémenté |
| **Playlist-er bestelaria eta Drag & Drop** | Cola virtualizatua, drag & drop gutxiak, aleatorra (shuffle) berratu eta zikloak | 🟢 Implémenté |
| **Modu « 🎲 Blind Test » interaktibo** | Joko musikal immersibo batekin animazioko kontua, izkatu-soinuak, irekitzaldi zaintzailea eta lotura otomatikoa | 🟢 Implémenté |
| **Günultzak in-app** | Zigitalko/manuelrako birrageak egiaztatzeko GitHub Releases-aren bidez | 🟢 Implémenté |
| **Artisteak eta Diskografiaren Kudeaketa** | Artista bakoitzeko ikuspegi dedikatuak, albumak, singleak eta diskografia osoa | 🟡 Prévu |
| **Grafikoeko Ekuilizatzailea (EQ)** | Audio presetak eta ekuilizatzaile parametriko multibanda | 🟡 Prévu |
| **Google Drive Konektatzailea** | Kolekzio audio ururakak azkakarrenetik sinkronizatzea OAuth 2.0-aren bidez | ⚪ Planifié |
| **Amazon Music Konektatzailea** | Kolekzio ururakak azkakarrenetik sinkronizatzea OAuth 2.0-aren bidez | ⚪ Planifié |
| **Spotify / Deezer Konektatzailea** | Playlistak importatzea eta laburrak urromatzea | ⚪ Planifié |
| **Deduklizazioak Inteligenteak** | Duplikazioak ezkutak detektatzea (titulu/artista ezkutak + empreintza akustikoak) | ⚪ Planifié |

> 💡 *Planifikatako hitzegiak eta berseemakkoen ayrıntesia ikusteko, zuzenatu [Feuille de route (Roadmap)](../../ROADMAP.md).*

---

## 📌 Sailbolak

Inglés, Francés, Español, Alemán, Italiano, Portugués, Japonés, Ruso, Polaco, Turco, Neerlandés, Sueco, Indonesio, Búlgaro, Serbio, Bielorruso, Griego, Catalán, Euskara, Gallego, Checo, Eslovaco, Húngaro, Croata, Esloveno, Bosnio, Estonio, Letón, Lituano, Noruego, Danés, Finlandés, Islandés, Malayo, Tagalo, Suajili, Esperanto, Chino simplificado, Chino tradicional, Coreano, Árabe, Hebreo, Vietnamita

---

## 🚀 Hazirbaitazkera

### Aurreko beharrezkoak

- **Python 3.11** edo hobego instalatuta
- Git

### Instalazioa

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

## 🧪 Probakak hasten ematea

Proiektuak `pytest` erabiltzen du, unitari eta integrazio testak sortzen duen suite batekin:

```bash
pytest -v
```

Probakak automatikoki egiten dira **Windows, macOS et Ubuntu**-an, bako push-ean GitHub Actionsaren bidez.

---

## 🔒 Segurtatea & API nøketeak

- **Ez komitatu API keyak edo autentifikazio tokenak moztu.**
- `.gitignore` kalanak `.env`, `credentials.json`, `token.json` eta paikuneko SQLite base de datos guztiak blokeatzeko da aurre-konfiguratu.
- Erabili `.env.example` zure ingurumenareako modelo gisa.

---

## 📋 Dokumentazioa & Proiektariko Aurrekoitzea

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Bertsioak, funtzionalitate berriak eta bug-etakoak (erregistro) detallatua.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Etorkizuneko hitzegilearen planifikazioa (Artistes, Cloud, Spotify, Dédoublonnage).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Arkitektura logikoaren altermann eta kódigoaren kalitateko arauak.

---

## 💖 Proiektua babestu & Tsebarketa

AMSO da software hardoa eta ingurubi (open source). Aplikazioa gustatzen zaizkio eta desarowera bixikatu nahi dizkio:

- 🎮 **Deskarga & Ordaindu Zerbait :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (erakutle prekompilatuta, erabiltzeko prest)
- ☕ **Donazio zuzen bat egitea :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [LEF97-ari sponsoratu](https://github.com/sponsors/LEF97)

---

## 📄 Lizentzia

Proiektua lizentzia batetik dago **GNU General Public License v3.0 (GPL-3.0)** — ikusi gaiak [LICENSE](../../LICENSE) gehi detalak.
