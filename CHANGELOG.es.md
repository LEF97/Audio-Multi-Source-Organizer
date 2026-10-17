# Registro de cambios (Changelog) — AMSO

<p align="right">
  <a href="CHANGELOG.fr.md">Français</a> • <a href="CHANGELOG.md">English</a> • <b>Español</b> • <a href="CHANGELOG.de.md">Deutsch</a> • <a href="CHANGELOG.it.md">Italiano</a>
</p>

---

Todos los cambios notables realizados en el proyecto **Audio Multi-Source Organizer (AMSO)** se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y este proyecto sigue la especificación [Semantic Versioning (SemVer)](https://semver.org/).

---

## [0.2.0-dev] - En desarrollo

### En curso / Planificado
- Consultar la [Hoja de ruta (ROADMAP.es.md)](ROADMAP.es.md) para conocer los hitos y funciones planificadas para v0.2.0.

---

## [0.1.0] - 2026-10-17

### Added
- **Motor de reproducción de audio integrado (python-vlc):**
  - Compatibilidad nativa con formatos populares: MP3, FLAC, WAV, AAC, OGG, M4A, WMA.
  - Detección y descarga automática y transparente de un binario VLC portátil si no está instalado.
  - Controles completos de reproducción: Reproducir, Pausar, Detener, Pista anterior/siguiente, barra de progreso (Seekbar) y volumen fluido.
  - Modos de reproducción: aleatorio (*Shuffle*) y modos de repetición.
  - Efectos visuales animados en tiempo real sincronizados con la música (partículas, ondas, estrellas, hiperespacio, aurora boreal, barras de espectro).
- **Gestor de Listas de Reproducción y Cola:**
  - Vista dedicada con tabla virtualizada que admite decenas de miles de pistas sin retraso.
  - Reorganización intuitiva mediante arrastrar y soltar (*Drag & Drop*).
  - Menús contextuales completos y guardado automático de sesión.
- **Escáner local multihilo de alto rendimiento:**
  - Recorrido asíncrono y recursivo de directorios con barra de progreso en tiempo real.
  - Extracción rápida de metadatos (título, artista, álbum, año, género, duración, tasa de bits) vía `mutagen`.
  - Extracción y caché de portadas de álbumes integradas sin bloqueo de la interfaz.
- **Base de datos SQLite optimizada:**
  - Arquitectura relacional rápida para indexación y registro de actividad.
- **Interfaz moderna de usuario (PySide6 / Modo oscuro):**
  - Tema oscuro de alta calidad con animaciones suaves.
  - Panel lateral plegable para navegación principal y configuración.
  - Compatibilidad multilingüe completa (francés, inglés, español, alemán, italiano) con cambio dinámico.
  - Página dedicada «Acerca de» en Configuración con detalles del proyecto, enlaces a repositorios y donaciones (Ko-fi, GitHub Sponsors).
  - Verificador de actualizaciones manual y automático integrado con la API de GitHub Releases.
