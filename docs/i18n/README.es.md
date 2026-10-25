# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <b>Español</b> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
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
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](CHANGELOG.es.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](ROADMAP.es.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) es un reproductor de audio de escritorio moderno, reactivo y multiplataforma (Windows, Linux, macOS). Diseñado para ofrecer a los audiófilos un control total sobre su biblioteca musical local (MP3, FLAC, OGG…), ahora admite listas de reproducción (M3U, PLS, XSPF, WPL), hojas CUE (álbumes de un solo archivo divididos en pistas) e integra un flamante modo de prueba ciega de audio (blind test)! El proyecto evoluciona para convertirse en un centro de comando unificado capaz de organizar, desduplicar y sincronizar colecciones musicales híbridas distribuidas entre discos locales, almacenamiento en la nube (Google Drive) y servicios de streaming (Spotify, Deezer, Amazon Music).

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

## 📌 Funcionalidades & Estado del proyecto

| Funcionalidad | Descripción | Estado |
| :--- | :---: | :---: |
| **Motor de reproducción VLC integrado** | Reproductor de audio ligero y autónomo con auto-instalación VLC portable y gestión fluida del volumen | 🟢 Implementado |
| **Escáner local multihilo** | Detección recursiva y rápida de archivos de audio locales (MP3, FLAC, AAC, OGG...) | 🟢 Implementado |
| **Extracción de metadatos** | Lectura/escritura ID3, Vorbis Comments y cálculo de huella de audio (`mutagen`) | 🟢 Implementado |
| **Soporte de Playlists (M3U, PLS, XSPF, WPL) y hojas CUE** | Indexación arborescente (🎶), orden secuencial de escucha, localización visual de pistas faltantes; los archivos `.cue` (💿) se abren como una carpeta de pistas virtuales con su duración y se reproducen como pistas reales | 🟢 Implementado |
| **Gestor de Playlists y Arrastrar-Soltar** | Cola virtualizada, arrastrar y soltar fluido, aleatorio (shuffle) reversible y bucles | 🟢 Implementado |
| **Modo « 🎲 Blind Test » interactivo** | Juego musical inmersivo con cuenta regresiva animada, fundido de sonido, revelación suave y encadenamiento automático | 🟢 Implementado |
| **Actualizaciones en la aplicación** | Verificación automática/manual de versiones vía GitHub Releases | 🟢 Implementado |
| **Gestión de artistas y discografía** | Vista dedicada por artista con álbumes, sencillos y discografía completa | 🟡 Planificado |
| **Ecualizador gráfico (EQ)** | Preajustes de audio y ecualizador multibanda paramétrico | 🟡 Planificado |
| **Connectador Google Drive** | Escaneo y sincronización de colecciones de audio remotas vía OAuth 2.0 | ⚪ Planificado |
| **Connectador Amazon Music** | Escaneo y sincronización de colecciones remotas vía OAuth 2.0 | ⚪ Planificado |
| **Connectador Spotify / Deezer** | Importación de listas de reproducción y coincidencia de pistas | ⚪ Planificado |
| **Desduplicación inteligente** | Detección de duplicados (título/artista borrosos + huellas acústicas) | ⚪ Planificado |

> 💡 *Para consultar el detalle de los hitos y versiones previstas, consulte la [Hoja de ruta (Roadmap)](ROADMAP.es.md).*

---

## 📌 Idiomas disponibles

Inglés, Francés, Español, Alemán, Italiano, Portugués, Japonés, Ruso, Polaco, Turco, Neerlandés, Sueco, Indonesio, Búlgaro, Serbio, Bielorruso, Griego, Catalán, Vasco, Gallego, Checo, Eslovaco, Húngaro, Croata, Esloveno, Bosnio, Estonio, Letón, Lituano, Noruego, Danés, Finlandés, Islandés, Malayo, Tagalo, Suajili, Esperanto, Chino simplificado, Chino tradicional, Coreano, Árabe, Hebreo, Vietnamita

---

## 🚀 Inicio rápido

### Requisitos

- **Python 3.11** o superior instalado
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

## 🧪 Lanzamiento de pruebas

El proyecto utiliza `pytest` con un conjunto de pruebas unitarias e de integración:

```bash
pytest -v
```

Las pruebas se ejecutan automáticamente en **Windows, macOS y Ubuntu** con cada push a través de GitHub Actions.

---

## 🔒 Seguridad & Claves de API

- **Nunca commite claves de API ni tokens de autenticación reales.**
- El archivo `.gitignore` está preconfigurado para bloquear `.env`, `credentials.json`, `token.json` y todas las bases de datos SQLite locales.
- Use `.env.example` como plantilla para su entorno de desarrollo.

---

## 📋 Documentation & Seguimiento del proyecto

- 📜 **[CHANGELOG.fr.md](CHANGELOG.es.md)** : Diario detallado de versiones, nuevas funcionalidades y correcciones de errores.
- 🗺️ **[ROADMAP.fr.md](ROADMAP.es.md)** : Hoja de ruta de futuros hitos (Artistas, Cloud, Spotify, Desduplicación).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Carta de arquitectura de software y reglas de calidad de código.

---

## 💖 Apoyar el proyecto & Distribución

AMSO es un software libre y gratuito (open source). Si aprecia la aplicación y desea fomentar su desarrollo:

- 🎮 **Descarga & Paga lo que quieras :** [Página Itch.io de AMSO](https://lef97.itch.io/audio-multi-source-organizer) (ejecutable precompilado listo para usar)
- ☕ **Hacer una donación directa :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **Patrocinadores de GitHub :** [Patrocinar LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licencia

Este proyecto está bajo la licencia **GNU General Public License v3.0 (GPL-3.0)** — consulte el archivo [LICENSE](../../LICENSE) para más detalles.
