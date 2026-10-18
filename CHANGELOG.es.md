# Registro de cambios (Changelog) — AMSO

<p align="right">
  <a href="CHANGELOG.fr.md">Français</a> • <a href="CHANGELOG.md">English</a> • <b>Español</b> • <a href="CHANGELOG.de.md">Deutsch</a> • <a href="CHANGELOG.it.md">Italiano</a>
</p>

---

Todos los cambios notables realizados en el proyecto **Audio Multi-Source Organizer (AMSO)** se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y este proyecto sigue la especificación [Semantic Versioning (SemVer)](https://semver.org/).

---

## [0.4.0-dev] - En desarrollo

### Added
- Inicio del ciclo de desarrollo para la versión 0.4.0 (Experiencia de audio avanzada, Hub de artistas y empaquetado multiplataforma para Linux/macOS).
- **Integración con Windows Shell y barra de tareas:** Declaración prioritaria del identificador `AppUserModelID` (`LEF97.AMSO.AudioPlayer`) en la primera línea de `main.py` antes de cualquier importación de Qt, lo que permite anclar de forma nativa la aplicación en ejecución a la barra de tareas de Windows.

---

## [0.3.0] - 2026-10-18

### Added
- **Soporte completo de archivos de listas de reproducción**:
  - Indexación y escaneo automático de formatos `.m3u`, `.m3u8`, `.pls`, `.xspf` y `.wpl`.
  - Nodos dedicados en el árbol de carpetas identificados con el icono **`🎶`**.
  - Conservación estricta del orden secuencial natural de reproducción (columna `#` con orden 1, 2, 3...) sin forzar ordenación alfabética.
  - Detección visual clara de pistas ausentes o movidas (prefijo de advertencia **`⚠️`**, resaltado suave y mensaje explicativo) sin interrumpir la reproducción.
  - Menú contextual ampliado en los nodos de playlist: reproducción directa, añadir a la cola, reproducir a continuación y mostrar en el Explorador de Windows.
- **Fundido acústico de entrada (*Fade-in*)**:
  - Transición suave del volumen de 0% al nivel configurado durante 1 segundo al iniciar o reanudar la reproducción (excepto en modo Blind Test).
- **Estabilidad y fluidez de la sincronización**:
  - Sustitución de la ventana emergente intrusiva «Scan already running» por una cola silenciosa en segundo plano.
  - Conservación de la selección y el estado de despliegue del árbol de carpetas cuando no hay cambios estructurales.
- **Presentación dinámica de carátulas**:
  - Corrección del escalado, centrado y alineación al alternar pantalla completa o cambiar el tamaño de ventana.

---

## [0.2.0] - 2026-10-18

### Added
- **Modo Blind Test y sección de juegos**:
  - Nuevo panel lateral desplegable « 🎲 JUEGOS » con el minijuego interactivo Blind Test (localizado en 5 idiomas).
  - Experiencia inmersiva: cuenta atrás dinámica con pulsación animada, revelación suave en fundido, progresión automática de rondas y precarga asíncrona de carátulas en RAM.
- **Ergonomía de reproducción y gestión de playlists**:
  - Rediseño del modo aleatorio (*Shuffle*): mezcla visual completa de la cola preservando la pista activa, botón directo « 🎲 Mezclar pistas » y restauración fiel del orden original al desactivarse.
  - Reordenación fluida mediante arrastrar y soltar (*Drag & Drop*) en la tabla de reproducción sin cortes de audio.
  - Persistencia asíncrona v2 con identificadores SQLite compactos que reducen el tamaño en disco un 99% (acceso sin bloqueos a 60 FPS).
  - Deslizador de volumen reubicado en la barra superior de navegación para despejar la vista del reproductor.
- **Gestión de biblioteca y papelera inteligente**:
  - Doble nivel de eliminación: exclusión lógica de la biblioteca (recordada en futuros escaneos) o eliminación física hacia la Papelera de reciclaje de Windows.
  - Vista dedicada « 🗑️ Papelera » con restauración en un solo clic e integración inmediata en la base de datos.
- **Interfaz y enlaces oficiales**:
  - Página « Acerca de » modernizada en Configuración con espectro interactivo y botones oficiales de apoyo (Ko-fi, GitHub Sponsors, GitHub, Itch.io).
  - Soporte completo en 5 idiomas (francés, inglés, español, alemán, italiano).

### Fixed
- **Resolución de errores `disk I/O error` (SQLite en Windows)**: configuración del modo WAL una sola vez al inicializar la base de datos, `PRAGMA busy_timeout = 30000`, almacenamiento temporal en memoria RAM (`PRAGMA temp_store = MEMORY`) y mecanismo de reintentos automáticos con retroceso exponencial para eliminar bloqueos de archivos en escaneos multihilo.
- **Supresión de alertas modales intrusivas en sincronizaciones en segundo plano**: las sincronizaciones automáticas ya no muestran ventanas modales de error que bloqueen la aplicación, registrándolas en el diario de actividad y la barra de estado.
- **Volumen de audio demasiado bajo al iniciar**: eliminación de una condición de carrera durante la inicialización del motor VLC y anulación de la atenuación automática (*ducking*) del mezclador de audio de Windows.
- **Visualización del logotipo oficial en el ejecutable de Windows**: corrección de la resolución multirruta de recursos incrustados en PyInstaller (`sys._MEIPASS`) para mostrar el logo AMSO en la barra lateral y la página Acerca de en lugar del icono alternativo 🎵.
- **Optimización del tiempo de arranque con bibliotecas grandes**: eliminación de comprobaciones síncronas en disco al restaurar sesiones de reproducción, acelerando el arranque instantáneamente en O(1) vía SQLite.
- **Progresión fluida del Splash Screen**: animación continua y suave paso a paso (1% a 1%) sin retroceso visual de la barra de progreso.

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
