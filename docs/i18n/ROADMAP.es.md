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

### 🟢 Version 0.1.0 — La Base Local Sólida
- [x] Escáner local multihilo con extracción de metadatos (ID3, Vorbis Comments, FLAC).
- [x] Motor de reproducción de audio integrado (python-vlc) con auto-instalación VLC portátil.
- [x] Vista de Playlist completa con reorganización arrastrar y soltar, reproducción aleatoria y bucles.
- [x] Guardado automático de la sesión de reproducción (posición, volumen, lista).
- [x] Interfaz moderna en Dark Mode con efectos visuales reactivos.
- [x] Internacionalización completa (FR, EN, ES, DE, IT).
- [x] Sistema de notificación y verificación de actualizaciones vía GitHub Releases.

---

### 🟢 Versión 0.2.0 — Modo Blind Test, Papelera y Ergonomía
- [x] **Modo « 🎲 Juegos / Blind Test » inmersivo:** Conteo con pulsación animada, revelación progresiva en fundido suave, encadenamiento automático y parámetros dedicados.
- [x] **Gestión de la Papelera y Restauración:** Exclusión de canciones, envío a la papelera de Windows y vista dedicada Papelera AMSO con restauración instantánea en la biblioteca.
- [x] **Rediseño del modo Aleatorio (Shuffle) y Arrastrar-Soltar:** Mezcla visual integral, orden reversible y reorganización de la lista de reproducción con el ratón.
- [x] **Optimizaciones de rendimiento y persistencia:** Formato de copia de seguridad compacto asíncrono (-99 % de espacio en disco) y eliminación de latencias al inicio.
- [x] **Ergonomía del Reproductor y Navegación:** Nuevo cajón « Juegos », control de volumen integrado en el encabezado del Reproductor, inicio predeterminado en el Reproductor.

---

### 🟢 Versión 0.3.0 — Soporte de Listas de Reproducción, Fundido de Audio y Robustez
- [x] **Soporte integral de listas de reproducción:** Indexación automática de formatos `.m3u`, `.m3u8`, `.pls`, `.xspf`, `.wpl` en la vista por carpeta con el icono `🎶`.
- [x] **Orden secuencial y gestión de pistas faltantes:** Respeto del orden original de la lista de reproducción y detección visual de archivos faltantes (`⚠️`) sin interrupción de la reproducción.
- [x] **Fundido sonoro acústico (*Fade-in*) :** Aumento progresivo del volumen durante 1 segundo al iniciar y reanudar una reproducción de audio.
- [x] **Fluidez de la sincronización:** Cola continua en segundo plano sin pop-up intrusivos y preservación del árbol de carpetas.
- [x] **Ajuste dinámico de portadas:** Recéntramiento y dimensionamiento fluido al pasar a pantalla completa / ventana.

---

### 🟢 Versión 0.4.0 — Experiencia de Audio Avanzada y Hojas CUE *(Actual)*
- [x] **Rediseño modular de la arquitectura y Quality Gate:** Desglose de la aplicación en módulos cohesivos (< 500 líneas), modularización de MainWindow en mixins dedicados (amso/ui/pages/), descomposición del servicio de audio en subsistemas independientes (player_transport, player_queue, player_transitions) e implementación de un arnés de validación automatizado (scripts/verify.py & .bat : ruff, mypy, pytest, control de tamaños).
- [x] **Integración Windows Shell y barra de tareas:** Fijación nativa directa desde el icono activo (AppUserModelID explícito LEF97.AMSO.AudioPlayer) desde el punto de entrada main.py y persistencia del acceso directo durante las actualizaciones.
- [x] **Escucha perfecta Gapless 0 entre dos pistas:** Ahora están disponibles 2 motores, uno basado en VLC_direct, el otro funcionando en modo buffer (funcionamiento preferido). Estos modos permiten una escucha fluida en álbumes con pistas relacionadas (Alan Parsons, Pink Floyd, Mike Oldfield, etc...)
- [x] **Soporte de hojas CUE (`.cue`):** Un archivo `.cue` se muestra como una carpeta de pistas virtuales (💿) con su duración y se reproduce como pistas reales (motor de búfer continuo).

---

### 🔵 Version 0.4.1 — Packaging Linux & macOS
- [ ] **Despliegue multiplataforma automatizado (Linux & macOS) :** Compilación nativa y empaquetado automatizado vía GitHub Actions para Linux (.AppImage / .tar.gz) y macOS Apple Silicon ARM & Intel (.dmg), complementario al ejecutable de Windows.

---

### 🌟 Versión x.0.0 — Desduplicación Inteligente & Versión Estable
- [ ] **Detección acústica de huella (Audio Fingerprinting) :** Identificación de duplicados incluso con etiquetas erróneas o archivos re-codificados.
- [ ] **Asistente de resolución de duplicados :** Comparación inteligente de calidad (selección automática del mejor bitrate / lossless) con archivo seguro.
- [ ] **Empaquetado multiplataforma oficial :** Ejecutables firmados para Windows (`.exe` / portable), macOS (`.dmg` Apple Silicon & Intel) y Linux (`AppImage` / `.deb`).
- [ ] **Documentación de usuario completa :** Guía paso a paso ilustrada y sitio web GitHub Pages.
- [ ] **Conector Spotify (Web API) :** Conexión de la cuenta de usuario y recuperación de listas de reproducción y favoritos.
- [ ] **Conector Amazon Music :** Escaneo, streaming y sincronización de colecciones musicales remotas (OAuth 2.0).
- [ ] **Coincidencia híbrida inteligente :** Correspondencia entre los títulos de una lista de reproducción remota y los archivos ya presentes localmente (alta fidelidad).
- [ ] **Vista unificada:** Visualización lado a lado de las pistas disponibles localmente y de las disponibles solo en streaming.
- [ ] **Autenticación segura OAuth 2.0:** Conexión simplificada a través del navegador sin almacenar secretos en texto claro.
- [ ] **Escaneo remoto de carpetas de Google Drive:** Indexación de archivos de audio presentes en las carpetas configuradas.
- [ ] **Reproducción directa en streaming en la nube:** Escucha de pistas remotas con caché local transparente.
- [ ] **Sincronización bidireccional selectiva:** Descarga local de pistas de la nube o respaldo de pistas locales a Drive.
- [ ] **Gestión de artistas y discografía asociada:** Vista dedicada por artista con álbumes, sencillos y discografía completa.
- [ ] **Ecualizador gráfico (EQ):** Preajustes (Rock, Pop, Jazz, Bass Boost) y ecualizador paramétrico multibanda.
- [ ] **Editor de metadatos en la aplicación:** Modificación directa de las etiquetas ID3 / Vorbis en un o varios archivos seleccionados.
- [ ] **Descarga automática de carátulas :** Búsqueda en línea (MusicBrainz / Cover Art Archive) de las carátulas faltantes.
- [ ] **Filtros de búsqueda avanzados :** Filtrado combinado por género, año, bitrate y formato sin pérdidas (Lossless).
- [x] **Crossfade configurable y Transiciones de audio avanzadas :** Soporte de transiciones sin interrupción (Gapless 0 ms), de fundido en cadena de alta precisión (Crossfade Equal-Power) y del modo estándar sin blanco.

---

## 💡 Proponer una funcionalidad

¿Una idea o una necesidad específica?
- Abre una discusión o un ticket en [GitHub Issues](https://github.com/LEF97/Audio-Multi-Source-Organizer/issues) utilizando la plantilla *Feature Request*.
- ¡Participa en las votaciones comunitarias para priorizar los desarrollos!
