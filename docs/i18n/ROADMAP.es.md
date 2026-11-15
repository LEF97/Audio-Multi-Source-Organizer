# Hoja de ruta (Roadmap) — AMSO

<p align="right">
  <a href="../../ROADMAP.fr.md">Français</a> • <a href="../../ROADMAP.md">English</a> • <b>Español</b> • <a href="ROADMAP.de.md">Deutsch</a> • <a href="ROADMAP.it.md">Italiano</a>
</p>

---

Este documento detalla las orientaciones estratégicas, las funcionalidades planificadas y los hitos futuros del proyecto **Audio Multi-Source Organizer (AMSO)**.

---

## 🎯 Visión del proyecto

AMSO tiene como vocación convertirse en el **hub musical universal y descentralizado** de referencia: una aplicación rápida, ligera, elegante y sin compromisos con la privacidad, que permite a cada uno dominar su colección de audio ya sea que esté almacenada en disco duro, archivada en la nube o consultada en servicios de streaming.

---

## 🗺️ Hitos y Versiones

### 🟢 Version 0.1.0 — La Base Local Robusta

- [x] Scanner local multihilo con extracción de metadatos (ID3, Vorbis Comments, FLAC).
- [x] Motor de reproducción de audio integrado (python-vlc) con auto-instalación VLC portable.
- [x] Vista de Playlist completa con reorganización de arrastrar y soltar, reproducción aleatoria y bucles.
- [x] Guardado automático de la sesión de reproducción (posición, volumen, lista).
- [x] Interfaz moderna en Dark Mode con efectos visuales reactivos.
- [x] Internacionalización completa (FR, EN, ES, DE, IT).
- [x] Sistema de notificación y verificación de actualizaciones vía GitHub Releases.

---

### 🟢 Version 0.2.0 — Modo Prueba Ciega, Papelera & Ergonomía

- [x] **Modo « 🎲 Juegos / Blind Test » inmersivo:** Cuenta regresiva con pulsación animada, revelación progresiva con fundido suave, encadenamiento automático y parámetros dedicados.
- [x] **Gestión de la Papelera & Restauración:** Exclusión de pistas, envío a la papelera de Windows y vista dedicada Papelera AMSO con restauración instantánea en la biblioteca.
- [x] **Rediseño del modo Aleatorio (Shuffle) & Arrastrar y Soltar:** Mezcla visual completa, orden reversible y reorganización de la lista de reproducción con el ratón.
- [x] **Optimización de rendimiento y persistencia:** Formato de copia de seguridad compacto asíncrono (-99 % de espacio en disco) y eliminación de latencias al inicio.
- [x] **Ergonomía del Reproductor & Navegación:** Nuevo cajón « Juegos », control deslizante de volumen integrado en el encabezado del Reproductor, inicio por defecto en el Reproductor.

---

### 🟢 Version 0.3.0 — Soporte de Listas de Reproducción, Fundido de Audio & Robustez

- [x] **Soporte integral de listas de reproducción:** Indexación automática de formatos `.m3u`, `.m3u8`, `.pls`, `.xspf`, `.wpl` en la vista por carpeta con el icono `🎶`.
- [x] **Orden secuencial y gestión de pistas faltantes:** Respeto del orden original de la lista de reproducción y detección visual de archivos faltantes (`⚠️`) sin interrupción de la reproducción.
- [x] **Fundido sonoro acústico (*Fade-in*)**: Aumento progresivo del volumen durante 1 segundo al iniciar y reanudar una reproducción de audio.
- [x] **Fluidez de la sincronización:** Cola continua en segundo plano sin pop-ups intrusivos y preservación del árbol de carpetas.
- [x] **Ajuste dinámico de las portadas:** Recéntramiento y dimensionamiento fluido al cambiar a pantalla completa / ventana.

---

### 🟢 Version 0.4.0 — Experiencia de Audio Avanzada & Hojas CUE

- [x] **Refactorización modular de la arquitectura y Quality Gate:** Desglose de la aplicación en módulos cohesivos (< 500 líneas), modularización de MainWindow en mixins dedicados (amso/ui/pages/), descomposición del servicio de audio en subsistemas independientes (player_transport, player_queue, player_transitions) y establecimiento de un arnés de validación automatizado (scripts/verify.py & .bat : ruff, mypy, pytest, control de tamaños).
- [x] **Integración con Windows Shell y barra de tareas:** Fijación nativa directa desde el icono activo (AppUserModelID explícito LEF97.AMSO.AudioPlayer) desde el punto de entrada main.py y persistencia del acceso directo durante las actualizaciones.
- [x] **Escucha perfecta Gapless 0 entre dos pistas:** Ahora están disponibles 2 motores, uno basado en VLC_direct, el otro funcionando en modo buffer (funcionamiento preferido). Estos modos permiten una escucha fluida en álbumes con pistas relacionadas (Alan Parsons, Pink Floyd, Mike Oldfield, etc...)
- [x] **Soporte para hojas CUE (.cue):** Un archivo .cue se muestra como una carpeta de pistas virtuales (💿) con su duración y se reproduce como pistas reales (motor de búfer continuo).

---

### 🟢 Version 0.4.1 — Fiabilidad de audio, registro traducido & versiones experimentales de Linux / macOS

- [x] **Salida de audio independiente del hilo de la interfaz:** el `QAudioSink` del motor `buffer` es alimentado por un hilo de audio dedicado (modo pull); mover o redimensionar la ventana ya no altera el sonido.
- [x] **Prueba ciega en motor `buffer`:** Reproducir, Siguiente y Anterior inician el sonido sin volver a pulsar Reproducir.
- [x] **Traducciones completadas:** registro de actividad guardado en clave + parámetros y traducido en la visualización, textos codificados en duro convertidos, respaldo al francés, control de marcadores `{nom}` en la sincronización.
- [x] **Estado de libVLC:** versión y procedencia (copia AMSO o VLC del sistema) en la configuración del reproductor.
- [x] **Despliegue multiplataforma (Linux & macOS), versión experimental no probada:** empaquetado automatizado vía GitHub Actions para Linux (.AppImage / .tar.gz) y macOS Apple Silicon ARM & Intel (.dmg no firmado), VLC requerido; los probadores devuelven `startup.log` y `crash.log`.

---

### 🟢 Version 0.5.0 — Sources & Biblioteca, Editor de Listas de Reproducción & Transiciones *(Actual)*

- [x] **Vista « Fuentes y Biblioteca »:** panel unificado con estado de salud de fuentes/listas de reproducción, navegación por fuente y acciones rápidas.
- [x] **Editor, reparación y exportación de listas de reproducción:** reorganización, relocalización manual o automática (local + base de datos), y guardado en `.m3u`, `.m3u8`, `.pls`, `.xspf` o `.wpl`.
- [x] **Listas de reproducción en modo álbum:** agrupación de títulos de una lista de reproducción en carpetas virtuales por álbum en el árbol, con « (álbum desconocido) » para los títulos sin álbum.
- [x] **Transiciones de portadas, escaneo en 3 fases y geometría de ventana:** 5 efectos de transición, progresión detallada del escaneo y restauración de la ventana.
- [x] **Nuevo icono AMSO:** icono de alta resolución de múltiples tamaños (PNG, ICO, ICNS).
- [x] **Crossfade configurable y Enlaces de audio avanzados:** Soporte para transiciones sin interrupción (Gapless 0 ms), fundido cruzado de alta precisión (Crossfade Equal-Power) y modo estándar sin blanco.

---

### 🌟 Versión x.0.0 — Deduplicación Inteligente & Versión Estable

- [ ] **Detección acústica de huella (Audio Fingerprinting) :** Identificación de duplicados incluso con etiquetas erróneas o archivos re-codificados.
- [ ] **Asistente de resolución de duplicados :** Comparación inteligente de calidad (selección automática del mejor bitrate / lossless) con archivo seguro.
- [ ] **Empaquetado multiplataforma oficial :** Ejecutables firmados para Windows (`.exe` / portable), macOS (`.dmg` Apple Silicon & Intel) y Linux (`AppImage` / `.deb`).
- [ ] **Documentación de usuario completa :** Guía paso a paso ilustrada y sitio web de presentación GitHub Pages.
- [ ] **Conector Spotify (Web API) :** Conexión de la cuenta de usuario y recuperación de listas de reproducción y favoritos.
- [ ] **Conector Amazon Music :** Escaneo, streaming y sincronización de colecciones musicales remotas (OAuth 2.0).
- [ ] **Coincidencia híbrida inteligente :** Correspondencia entre los títulos de una lista de reproducción remota y los archivos ya presentes localmente (alta fidelidad).
- [ ] **Vista unificada :** Visualización lado a lado de pistas disponibles localmente y de aquellas disponibles solo en streaming.
- [ ] **Autenticación segura OAuth 2.0:** Conexión simplificada a través del navegador sin almacenar secretos en texto claro.
- [ ] **Escaneo remoto de carpetas de Google Drive:** Indexación de archivos de audio presentes en las carpetas configuradas.
- [ ] **Reproducción directa en streaming en la nube:** Escucha de pistas remotas con caché local transparente.
- [ ] **Sincronización bidireccional selectiva:** Descarga local de pistas de la nube o copia de seguridad de pistas locales a Drive.
- [ ] **Gestión de artistas y discografía asociada:** Vista dedicada por artista con álbumes, sencillos y discografía completa.
- [ ] **Ecualizador gráfico (EQ):** Preajustes (Rock, Pop, Jazz, Bass Boost) y ecualizador paramétrico multibanda.
- [ ] **Editor de metadatos en la aplicación:** Modificación directa de las etiquetas ID3 / Vorbis en uno o varios archivos seleccionados.
- [ ] **Descarga automática de portadas:** Búsqueda en línea (MusicBrainz / Cover Art Archive) de portadas faltantes.
- [ ] **Filtros de búsqueda avanzados:** Filtrado combinado por género, año, bitrate y formato sin pérdidas (Lossless).

---

### 🔵 Version 0.4.2 — Compatibilidad de red Linux & macOS

- [ ] **Detección de montajes de red (Linux & macOS):** `amso/core/network_paths.py` solo reconoce hoy las rutas UNC y las unidades mapeadas de Windows; reconocer los montajes NFS / SMB / AFP (`/proc/self/mountinfo`, `statfs`) para evitar cualquier sondeo de disco bloqueante al inicio en estos sistemas.
- [ ] **Validación en Linux y macOS:** motor `buffer`, transiciones y packaging a confirmar en sistemas reales a partir de los comentarios de los probadores.

---

## 💡 Proponer una funcionalidad

¿Una idea o una necesidad específica?

- Abre una discusión o un ticket en [GitHub Issues](https://github.com/LEF97/Audio-Multi-Source-Organizer/issues) utilizando la plantilla *Feature Request*.
- ¡Participa en las votaciones comunitarias para priorizar los desarrollos!
