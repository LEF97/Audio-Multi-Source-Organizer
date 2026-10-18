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

> **AMSO** es una aplicación de escritorio de código abierto y multiplataforma diseñada para unificar, desduplicar y sincronizar bibliotecas musicales híbridas distribuidas entre discos locales, almacenamiento en la nube (Google Drive) y plataformas de streaming (Spotify, Deezer y Amazon Music).

---

<p align="center">
  <img src="screenshots/2026-10-18%20v0.2.0.png" alt="Captura de pantalla de Audio Multi-Source Organizer (AMSO) - Reproductor" width="850">
</p>

<p align="center">
  <img src="screenshots/2026-10-18%20v0.2.0%2002.png" alt="Captura de pantalla de Audio Multi-Source Organizer (AMSO) - Espectro y Volumen" width="850">
</p>

---

## 📌 Características y Estado del Proyecto

| Característica | Descripción | Estado |
| :--- | :--- | :---: |
| **Escáner local multihilo** | Exploración e indexación rápida y recursiva de archivos de audio locales (MP3, FLAC, AAC, OGG...) | 🟢 Implementado |
| **Extracción de metadatos** | Lectura/escritura de etiquetas ID3, comentarios Vorbis y huella digital acústica (`mutagen`) | 🟢 Implementado |
| **Motor de reproducción VLC integrado** | Reproductor de audio ligero y autónomo con auto-instalación portátil de VLC y control de volumen fluido | 🟢 Implementado |
| **Gestor de Listas de Reproducción** | Cola virtualizada, arrastrar y soltar (drag & drop), aleatorio (shuffle) y repetición | 🟢 Implementado |
| **Interfaz gráfica moderna PySide6** | Modo oscuro de alta gama, visualizador de audio en tiempo real, interfaz en 5 idiomas | 🟢 Implementado |
| **Actualizaciones in-app** | Comprobación automática y manual de nuevas versiones a través de GitHub Releases | 🟢 Implementado |
| **Gestión de Artistas y Discografía** | Vista dedicada por artista con álbumes, sencillos y discografía completa | 🟡 Previsto |
| **Ecualizador gráfico (EQ)** | Ajustes preestablecidos de sonido y ecualizador multibanda paramétrico | 🟡 Previsto |
| **Conector Google Drive** | Escaneo y sincronización de colecciones remotas mediante OAuth 2.0 | ⚪ Planificado |
| **Conector Amazon Music** | Escaneo y sincronización de carpetas musicales remotas mediante OAuth 2.0 | ⚪ Planificado |
| **Integración Spotify / Deezer** | Importación de listas de reproducción y correspondencia de pistas | ⚪ Planificado |
| **Desduplicación inteligente** | Detección de duplicados basada en metadatos difusos y huellas acústicas | ⚪ Planificado |

> 💡 *Para consultar los detalles de los hitos y versiones planificadas, consulte la [Hoja de Ruta (Roadmap)](ROADMAP.es.md).*

---

## 🚀 Inicio Rápido

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

# 3. Activar el entorno
# En Windows (PowerShell):
.venv\Scripts\Activate.ps1
# En Linux / macOS:
source .venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# Para desarrollo y pruebas:
pip install -e .[dev]

# 5. Iniciar AMSO
python main.py
```

---

## 🧪 Ejecución de Pruebas

La suite de pruebas automatizadas está basada en `pytest`:

```bash
pytest -v
```

---

## 💖 Apoyar el Proyecto y Distribución

AMSO es software libre y de código abierto. Si disfrutas del proyecto y deseas apoyar su desarrollo:

* 🎮 **Descargar y Pagar lo que Quieras:** [AMSO en Itch.io](https://lef97.itch.io/audio-multi-source-organizer) (ejecutable portátil independiente precompilado)
* ☕ **Donación Directa:** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
* ⭐ **GitHub Sponsors:** [Patrocinar a LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licencia

Este proyecto está bajo la licencia **GNU General Public License v3.0 (GPL-3.0)** — consulte el archivo [LICENSE](LICENSE) para más detalles.
