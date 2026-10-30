# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <b>Català</b> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) és un reproductor de àudio de sobretaula modern, reactiu i multiplataforma (Windows, Linux, macOS). Dissenyat per oferir als audiófiles un control total sobre la seva biblioteca musical local (MP3, FLAC, OGG…), ara suporta llistes de reproducció (M3U, PLS, XSPF, WPL), les hores CUE (àlbums d'un únic fitxer tallats en pistes) i incorpora un mode blind test audio totalment nou! El projecte evoluciona per convertir-se en un centre de control unitari capa d'organitzar, desduplicar i sincronitzar col·leccions musicals hibrides repartides entre discs locals, emmagatzematge núvol (Google Drive) i serveis de *streaming* (Spotify, Deezer, Amazon Music).

---

<p align="center">
  <img src="../../screenshots/2026-10-29%20v0.4.1.png" alt="Audio Multi-Source Organizer (AMSO) - Lecteur audio avec l'ambiance visuelle Hyperespace (champ d'étoiles 3D)" width="850">
</p>

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

## 📌 Funcionalitats & Estat del projecte

| Funcionalitat | Descripció | Estat |
| :--- | :---: | :---: |
| **Motor de reproducció de àudio** | Reproductor de àudio lleuger i autònom (VLC portàtil instal·lat automàticament amb Windows). Dos motors a escollir: sortida directa VLC, o motor de buffer contínu per a una transició fluida entre dues pistes (Gapless 0 ms, fonament de transició a potència igual, sense interrupció de la sortida de àudio) | 🟢 Implementat |
| **Gestió de la biblioteca** | Scan recursiu multihilo de carpetes locals (MP3, FLAC, AAC, OGG...), sincronització manual, programada o en temps real, papureres i estadístiques de la biblioteca | 🟢 Implementat |
| **Extracció de metadades** | Lectura/escritura ID3, Vorbis Comments i càlcul d'empressat de àudio (`mutagen`) | 🟢 Implementat |
| **Suport de llistes de reproducció (M3U, PLS, XSPF, WPL) & fitxes CUE** | Indexació arborescente (🎶), ordre seqüencial d'escolta, localització visual de les peces faltants; els fitxers `.cue` (💿) s'obre com una carpeta de pistes virtuals amb la seva durada i es reproduuen com a pistes reals | 🟢 Implementat |
| **Gestor de llista de reproducció i Arrastar-Soltar** | Cola virtualitzada, arrastrar i soltar fluida, aleatori (shuffle) reversible i bucles | 🟢 Implementat |
| **Mode « 🎲 Blind Test » interactiu** | Joc musical immersiu amb compte regressiu animat, fonament sonorr, revelació suau i transició automàtica | 🟢 Implementat |
| **Actualitzacions in-app** | Verificació automàtica/manual de versions a través de GitHub Releases | 🟢 Implementat |
| **Versió de Linux i macOS** | Paquets .AppImage / .tar.gz (Linux) i .dmg no signat (macOS), VLC requerit | 🟡 Experimental (no provat) |
| **Gestió d'artistes i discografia** | Vista dedicada per artista amb àlbums, singles i discografia completa | 🟡 Previst |
| **Ecualitzador gràfic (EQ)** | Presets de l'àudio i ecualitzador multibanda paramètric | 🟡 Previst |
| **Conector Google Drive** | Scan i sincronització de col·leccions d'àudio distants a través d'OAuth 2.0 | ⚪ Planificat |
| **Conector Amazon Music** | Scan i sincronització de col·leccions distants a través d'OAuth 2.0 | ⚪ Planificat |
| **Conector Spotify / Deezer** | Importació de playlists i correspondència de pistes | ⚪ Planificat |
| **Deduplicació intel·ligent** | Detecció de duplicats (títol/artista borros + improntes acústiques) | ⚪ Planificat |

> 💡 *Per consultar el detall dels hito i les versions previstes, refereu-vos a la [Feuella de ruta (Roadmap)](../../ROADMAP.md).*

---

## 📌 Idiomes disponibles

Anglès, Català, Castellà, Alemanyc, Italià, Portugès, Japonès, Rus, Polonès, Turc, Netherlandès, Suec, Indonesès, Bulgar, Serb, Bielorusi, Grec, Catalan, Vascà, Galicià, Tchec, Eslovac, Hongàric, Croat, Sloven, Bosniàc, Estonià, Leton, Litouani, Norveg, Danès, Finlandès, Islandès, Malai, Tagalog, Swahili, Esperant, Xinesi simplificat, Xinesi tradicional, Coreà, Arab, Ebreu, Vietnamès

---

## 🚀 Inici ràpid

### Prerequis

- **Python 3.11** o superior instal·lat
- Git

### Instal·lació

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

## 🐧🍎 Linux i macOS: versions experimentals (no provades)

Els paquets Linux (`.AppImage` / `.tar.gz`) i macOS (`.dmg`) són proveïts **sense haver estat provats** : AMSO només s'ha validat amb Windows. El motor de àudio de búfer continu (`buffer`) en particular no s'ha verificat en aquests sistemes. La vostra retroalimentació és preu.

- **VLC és requerit** (AMSO només el descarrega amb Windows) :
  - Linux : `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) o `sudo pacman -S vlc` (Arch).
  - macOS : instal·lar **VLC.app** des de [videolan.org](https://www.videolan.org/vlc/) a la carpeta Applications.
- **Linux, bibliothèques de sistema** : l'interface Qt demana especialment `libpulse0` (son), `libxcb-cursor0` i `libxkbcommon-x11-0` (per exemple `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, `.dmg` no signat** : al primer inici, fer un clic dret sobre AMSO i després **Obrir**, o executar `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage** : fer-la ejecutable amb `chmod +x AMSO*.AppImage`.
- **En cas de problema**, si us plau envieu els fitxers `startup.log` i `crash.log` (si existeixen) situats a la carpeta de dades: `~/Library/Application Support/AMSO/` amb macOS, `~/.local/share/AMSO/` amb Linux. Especificueu el vostre sistema i la versió de VLC.

---

## 🧪 Llançament de les proves

El projecte utilitza `pytest` amb una suite de tests unitaris i d'integració:

```bash
pytest -v
```

Els tests s'executen automàticament sobre **Windows, macOS et Ubuntu** amb cada push via GitHub Actions.

---

## 🔒 Seguretat i Claues d'API

- **Nunca commativeu claues d'API ni tokens d'autenticació reals.**
- El fitxer `.gitignore` està preconfigurat per blocar `.env`, `credentials.json`, `token.json` i totes les bases de dades SQLite locals.
- Utilizeu `.env.example` com a model per al vostre entorn de desenvolupament.

---

## 📋 Documentació & Seguiment del projecte

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Diari detallat de les versions, noves funcionalitats i correccions de bugs.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Hoja de ruta dels futurs hito (Artistes, Cloud, Spotify, Desduplicació).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Constitució d'arquitectura de programari i regles de qualitat de codi.

---

## 💖 Sostenir el projecte & Distribució

AMSO és un programari lliure i gratuït (open source). Si us agrada l'aplicació i voleu fomentar el seu desenvolupament:

- 🎮 **Descàrrega & Pay What You Want :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (executiu precompilat preparat per a l'ús)
- ☕ **Faire una donació directa :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [Patrocinar LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Llicència

Aquest projecte està sota la llicència **GNU General Public License v3.0 (GPL-3.0)** — consulteu el fitxer [LICENSE](../../LICENSE) per més detalls.
