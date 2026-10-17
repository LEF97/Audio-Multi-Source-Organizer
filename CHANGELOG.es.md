# Registro de cambios (Changelog) — AMSO

<p align="right">
  <a href="CHANGELOG.fr.md">Français</a> • <a href="CHANGELOG.md">English</a> • <b>Español</b> • <a href="CHANGELOG.de.md">Deutsch</a> • <a href="CHANGELOG.it.md">Italiano</a>
</p>

---

Todos los cambios notables realizados en el proyecto **Audio Multi-Source Organizer (AMSO)** se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y este proyecto sigue la especificación [Semantic Versioning (SemVer)](https://semver.org/).

---

## [0.2.0-dev] - En desarrollo

### Fixed
- **Resolución de errores `disk I/O error` (SQLite en Windows)**: configuración del modo WAL una sola vez al inicializar la base de datos, `PRAGMA busy_timeout = 30000`, almacenamiento temporal en memoria RAM (`PRAGMA temp_store = MEMORY`) y mecanismo de reintentos automáticos con retroceso exponencial para eliminar bloqueos de archivos en escaneos multihilo.
- **Supresión de alertas modales intrusivas en sincronizaciones en segundo plano**: las sincronizaciones automáticas ya no muestran ventanas modales de error que bloqueen la aplicación, registrándolas en el diario de actividad y la barra de estado.
- **Volumen de audio demasiado bajo al iniciar**: eliminación de una condición de carrera durante la inicialización del motor VLC y anulación de la atenuación automática (*ducking*) del mezclador de audio de Windows.
- **Visualización del logotipo oficial en el ejecutable de Windows**: corrección de la resolución multirruta de recursos incrustados en PyInstaller (`sys._MEIPASS`) para mostrar el logo AMSO en la barra lateral y la página Acerca de en lugar del icono alternativo 🎵.

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
