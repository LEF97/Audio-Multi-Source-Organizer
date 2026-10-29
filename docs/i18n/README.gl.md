# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <b>Galego</b> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) é un reprodutor de audio de escritorio moderno, reactivo e multiplatforma (Windows, Linux, macOS). Diseñado para ofrecer aos audiófilos un control total sobre a súa biblioteca musical local (MP3, FLAC, OGG…), agora ademós suporta listas de reprodución (M3U, PLS, XSPF, WPL), ficheiros CUE (álbums dun único ficheiro partidos en pistas) e integra un modo completamente novo de *blind test* de audio! O proxecto evolúcoa para ser un centro de comando unificado capaz de organizar, desduplicar e sincronizar coleccións musicais híbridas repartidas entre discos locais, armazenamento na nube (Google Drive) e servizos de *streaming* (Spotify, Deezer, Amazon Music).

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

## 📌 Funcionalidades & Estado do proxecto

| Funcionalidade | Descripción | Estado |
| :--- | :---: | :---: |
| **Motor de reprodución de audio** | Reproductor de audio leve e autónomo (VLC portable instalado automáticamente bajo Windows). Dúo motores a elección: saída directa VLC, ou motor de búfer continuo para un enxame fluído entre dúas pistas (Gapless 0 ms, fondue enxame a potencia igual, sen interrupción da saída de audio) | 🟢 Implémentado |
| **Gestión da biblioteca** | Scan recursivo multihilo dos directorios locais (MP3, FLAC, AAC, OGG...), sincronización manual, programada ou en tempo real, papelera e estatísticas da biblioteca | 🟢 Implémentado |
| **Extracción de metadatos** | Lectura/escritura ID3, Vorbis Comments e cálculo de impresión de audio (`mutagen`) | 🟢 Implémentado |
| **Suporte de Playlists (M3U, PLS, XSPF, WPL) & follas CUE** | Indexación arbórea (🎶), orden secuencial de escoita, localización visual das pezas faltantes; os ficheiros `.cue` (💿) ábreanse como un directorio de pistas virtuais coa súa duración e líanse como pezas reais | 🟢 Implémentado |
| **Gestor de Playlist & Arrastrar-Soltar** | Cola virtualizada, drag & drop fluído, aleatorio (shuffle) reversible e liñas | 🟢 Implémentado |
| **Modo « 🎲 Blind Test » interactivo** | Xogo musical inmersivo con conta atrás animada, fondue sonora, revelación suave e enxame automático | 🟢 Implémentado |
| **Actualizacións in-app** | Verificación automática/manual das versións vía GitHub Releases | 🟢 Implementado |
| **Versións Linux & macOS** | Paquetes `.AppImage` / `.tar.gz` (Linux) e `.dmg` non firmado (macOS), VLC necesario | 🟡 Experimental (non testado) |
| **Xestión de artistas & Discografía** | Vista dedicada por artista con álbums, singles e discografía completa | 🟡 Previsto |
| **Ecualizador gráfico (EQ)** | Presets de audio e ecualizador multibanda paramétrico | 🟡 Previsto |
| **Conector Google Drive** | Scan e sincronización de coleccións de audio distantes vía OAuth 2.0 | ⚪ Planificado |
| **Conector Amazon Music** | Scan e sincronización de coleccións distantes vía OAuth 2.0 | ⚪ Planificado |
| **Conector Spotify / Deezer** | Importación de playlists e correspondencia de pistas | ⚪ Planificado |
| **Desduplicación intelixente** | Detección de duplicados (título/artista borrosos + huellas acústicas) | ⚪ Planificado |

> 💡 *Para consultar o detalle dos hitos e versións previstas, refrérese á [Feixe de ruta (Roadmap)](../../ROADMAP.md).*

---

## 📌 Idiomas dispoñibles

Inglés, Francés, Español, Alemán, Italiano, Portugués, Japonés, Ruso, Polaco, Turco, Neerlandés, Sueco, Indonesio, Búlgaro, Serbio, Bielorruso, Griego, Catalán, Vasco, Gallego, Checo, Eslovaco, Húngaro, Croata, Esloveno, Bosnio, Estonio, Letón, Lituanio, Noruego, Danés, Finlandés, Islandés, Malayo, Tagalo, Suajili, Esperanto, Chino simplificado, Chino tradicional, Coreano, Árabe, Hebreo, Vietnamita

---

## 🚀 Inicio rápido

### Prerreisitos

- **Python 3.11** ou superior instalado
- Git

### Instalación

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

## 🐧🍎 Linux e macOS: versións experimentais (non testadas)

Os paquetes Linux (`.AppImage` / `.tar.gz`) e macOS (`.dmg`) son fornidados **sen haber sido testados**: AMSO só foi validado en Windows. O motor de áudio de tampón continuo (`buffer`), en particular, non foi verificado nestes sistemas. O seu feedback é precioso.

- **VLC é necesario** (AMSO só o descarrega en Windows) :
  - Linux: `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) ou `sudo pacman -S vlc` (Arch).
  - macOS: instalar **VLC.app** desde [videolan.org](https://www.videolan.org/vlc/) na carpeta Applications.
- **Linux, bibliotecas do sistema** : a interface Qt requir, nomeadamente `libpulse0` (son), `libxcb-cursor0` e `libxkbcommon-x11-0` (por exemplo `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, `.dmg` non firmado** : no primeiro lanzamiento, facer un clic droit sobre AMSO e despois **Abrir**, ou executar `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage** : facelo executable con `chmod +x AMSO*.AppImage`.
- **En caso de problema**, por favor, envía os ficheiros `startup.log` e `crash.log` (se existen) situados na carpeta de datos: `~/Library/Application Support/AMSO/` en macOS, `~/.local/share/AMSO/` en Linux. Especifica o teu sistema e a versión de VLC.

---

## 🧪 Lanzamento dos testes

O proxecto utiliza `pytest` con un conjunto de tests unitarios e de integración :

```bash
pytest -v
```

Os testaxes executanse automáticamente en **Windows, macOS e Ubuntu** con cada push vía GitHub Actions.

---

## 🔒 Seguridade & Chaves de API

- **Nunca commiteis claves de API ni tokens de autenticación reais.**
- O ficheiro `.gitignore` está pré-configurado para bloquear `.env`, `credentials.json`, `token.json` e todas as bases de datos SQLite locais.
- Utilizai `.env.example` como modelo para o vosso ambiente de desenvolvemento.

---

## 📋 Documentación & Seguemento do proxecto

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Diario detallado das versións, novas funcionalidades e correccións de fallos.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Mapa de ruta dos futuros hitos (Artistas, Cloud, Spotify, Desduplicación).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Carta de arquitectura de software e regras de calidad de código.

---

## 💖 Apoistar o proxecto & Distribución

AMSO é un software libre e gratuito (open source). Se apreciades a aplicación e queres fomentar o seu desenvolvemento:

- 🎮 **Descarga & Paga o que queiras :** [Páxina Itch.io de AMSO](https://lef97.itch.io/audio-multi-source-organizer) (executable précompilado listo para usar)
- ☕ **Facer unha doación directa :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **Sponsors de GitHub :** [Sponsorizar LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licencia

Este proxecto está bajo licencia **GNU General Public License v3.0 (GPL-3.0)** — consulta o ficheiro [LICENSE](../../LICENSE) para máis detalles.
