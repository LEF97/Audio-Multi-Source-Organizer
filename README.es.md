# Audio Multi-Source Organizer (AMSO)

<p align="right">
  <a href="README.fr.md">Français</a> • <a href="README.md">English</a> • <b>Español</b> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a>
</p>

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](CHANGELOG.es.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Hitos%20futuros-purple.svg)](ROADMAP.es.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) es un reproductor de audio de escritorio moderno, reactivo y multiplataforma (Windows, Linux, macOS). Diseñado para ofrecer a los audiófilos un control total sobre su biblioteca musical local (MP3, FLAC, OGG…), ahora es compatible con archivos de listas de reproducción (M3U, PLS, XSPF, WPL) e integra un minijuego interactivo de blind test musical. El proyecto evoluciona para convertirse en un centro de mando unificado capaz de organizar, desduplicar y sincronizar colecciones musicales híbridas repartidas entre discos locales, almacenamiento en la nube (Google Drive) y servicios de streaming (Spotify, Deezer, Amazon Music).

---

<p align="center">
  <img src="screenshots/2026-10-18%20v0.3.0%2002.png" alt="Audio Multi-Source Organizer (AMSO) - Explorador de carpetas y listas de reproducción 🎶" width="850">
</p>

<p align="center">
  <img src="screenshots/2026-10-18%20v0.3.0.png" alt="Audio Multi-Source Organizer (AMSO) - Reproductor de Audio & Ambiente Hyperspace" width="850">
</p>

<p align="center">
  <img src="screenshots/2026-10-18%20v0.3.0%20blind%20test.png" alt="Audio Multi-Source Organizer (AMSO) - Minijuego interactivo Blind Test" width="850">
</p>

---

## 📌 Características & Estado del proyecto

| Característica | Descripción | Estado |
| :--- | :--- | :---: |
| **Motor de reproducción VLC integrado** | Reproductor de audio ligero y autónomo con auto-instalación portátil de VLC y control de volumen fluido | 🟢 Implementado |
| **Escáner local multihilo** | Exploración recursiva y rápida de archivos de audio locales (MP3, FLAC, AAC, OGG...) | 🟢 Implementado |
| **Extracción de metadatos** | Lectura/escritura de etiquetas ID3, comentarios Vorbis y huella digital acústica (`mutagen`) | 🟢 Implementado |
| **Soporte de Playlists (M3U, PLS, XSPF, WPL)** | Indexación en el árbol de carpetas (🎶), orden secuencial de reproducción y alerta visual de pistas ausentes | 🟢 Implementado |
| **Gestor de Listas de Reproducción & Drag-and-Drop** | Cola virtualizada, arrastrar y soltar fluido, modo aleatorio (shuffle) reversible y bucles | 🟢 Implementado |
| **Modo « 🎲 Blind Test » interactivo** | Juego musical inmersivo con cuenta atrás dinámica, fundido sonoro, revelación suave y avance automático | 🟢 Implementado |
| **Actualizaciones in-app** | Comprobación automática y manual de nuevas versiones a través de GitHub Releases | 🟢 Implementado |
| **Gestión de Artistas & Discografía** | Vista dedicada por artista con álbumes, sencillos y discografía completa | 🟡 Previsto |
| **Ecualizador gráfico (EQ)** | Ajustes preestablecidos de sonido y ecualizador paramétrico multibanda | 🟡 Previsto |
| **Conector Google Drive** | Escaneo y sincronización de colecciones remotas en la nube mediante OAuth 2.0 | ⚪ Planificado |
| **Conector Amazon Music** | Escaneo y sincronización de carpetas musicales remotas mediante OAuth 2.0 | ⚪ Planificado |
| **Integración de streaming Spotify / Deezer** | Importación de listas de reproducción y correspondencia híbrida de pistas | ⚪ Planificado |
| **Desduplicación inteligente** | Detección de duplicados basada en metadatos difusos y huellas acústicas | ⚪ Planificado |

> 💡 *Para consultar el detalle de los hitos y versiones planificadas, consulte la [Hoja de ruta (Roadmap)](ROADMAP.es.md).*

---

## 🚀 Inicio rápido

### Requisitos previos
- **Python 3.11** o superior instalado
- Git

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/LEF97/Audio-Multi-Source-Organizer.git
cd audio-multi-source-organizer

# 2. Crear el entorno virtual
python -m venv .venv

# 3. Activar el entorno virtual
# En Windows (PowerShell) :
.venv\Scripts\Activate.ps1
# En Linux / macOS :
source .venv/bin/activate

# 4. Instalar las dependencias
pip install -r requirements.txt

# Para desarrollo y pruebas :
pip install -e .[dev]

# 5. Configurar las variables de entorno
cp .env.example .env

# 6. Iniciar la aplicación
python main.py
```

---

## 🧪 Ejecución de pruebas

La suite de pruebas automatizadas está basada en `pytest` y cubre pruebas unitarias e integración:

```bash
pytest -v
```

Las pruebas se ejecutan automáticamente en **Windows, macOS y Ubuntu** en cada push mediante GitHub Actions.

---

## 🔒 Seguridad & Claves de API

- **Nunca incluya claves de API reales ni tokens de autenticación en los commits.**
- El archivo `.gitignore` está configurado para bloquear `.env`, `credentials.json`, `token.json` y bases de datos SQLite locales.
- Utilice `.env.example` como plantilla para su entorno de desarrollo local.

---

## 📋 Documentación & Seguimiento del proyecto

- 📜 **[CHANGELOG.es.md](CHANGELOG.es.md)** ([Version Française](CHANGELOG.fr.md) • [English Version](CHANGELOG.md)): Registro detallado de versiones, nuevas funciones y correcciones.
- 🗺️ **[ROADMAP.es.md](ROADMAP.es.md)** ([Version Française](ROADMAP.fr.md) • [English Version](ROADMAP.md)): Hoja de ruta con futuros hitos (Artistas, Nube, Spotify, Desduplicación).
- 📐 **[CODE_QUALITY.md](CODE_QUALITY.md)**: Carta de arquitectura y normas de calidad del código.

---

## 💖 Apoyar el proyecto & Distribución

AMSO es software libre y de código abierto (open source). Si disfrutas de la aplicación y deseas apoyar su desarrollo:

* 🎮 **Descargar y Pagar lo que Quieras:** [Página de AMSO en Itch.io](https://lef97.itch.io/audio-multi-source-organizer) (ejecutable portátil precompilado)
* ☕ **Donación directa:** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
* ⭐ **GitHub Sponsors:** [Patrocinar a LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licencia

Este proyecto está bajo la licencia **GNU General Public License v3.0 (GPL-3.0)** — consulte el archivo [LICENSE](LICENSE) para más detalles.
