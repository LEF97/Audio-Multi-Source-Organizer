# Hoja de ruta (Roadmap) — AMSO

<p align="right">
  <a href="ROADMAP.fr.md">Français</a> • <a href="ROADMAP.md">English</a> • <b>Español</b> • <a href="ROADMAP.de.md">Deutsch</a> • <a href="ROADMAP.it.md">Italiano</a>
</p>

---

Este documento detalla las orientaciones estratégicas, las funciones planificadas y los futuros hitos del proyecto **Audio Multi-Source Organizer (AMSO)**.

---

## 🎯 Visión del proyecto

AMSO tiene como objetivo convertirse en el **hub musical universal y descentralizado** de referencia: una aplicación rápida, ligera, elegante y sin compromisos en materia de privacidad, que permite controlar la colección de audio tanto si está almacenada en discos duros, archivada en la nube o en servicios de streaming.

---

## 🗺️ Hitos y Versiones

### 🟢 Versión 0.1.0 — La Base Local Robusta
- [x] Escáner local multihilo de alto rendimiento con extracción de metadatos (ID3, Vorbis Comments, FLAC).
- [x] Motor de reproducción de audio integrado (python-vlc) con auto-instalación portátil de VLC.
- [x] Vista completa de Playlist con reorganización por arrastrar y soltar, reproducción aleatoria y repetición.
- [x] Guardado automático de la sesión de reproducción (posición, volumen, lista activa).
- [x] Interfaz moderna en Modo Oscuro con efectos visuales reactivos en tiempo real.
- [x] Internacionalización completa (FR, EN, ES, DE, IT).
- [x] Sistema de notificaciones y comprobador de actualizaciones mediante GitHub Releases.

---

### 🟢 Versión 0.2.0 — Modo Blind Test, Papelera & Ergonomía
- [x] **Modo inmersivo « 🎲 Juegos / Blind Test »:** Cuenta atrás animada con pulsación, revelación progresiva en fundido suave, encadenamiento automático y ajustes dedicados.
- [x] **Gestión de la Papelera & Restauración:** Exclusión de pistas, envío a la papelera de Windows y vista dedicada Papelera AMSO con restauración instantánea en la biblioteca.
- [x] **Rediseño del modo Aleatorio (Shuffle) & Arrastrar y Soltar:** Mezcla visual completa, orden original reversible y reordenación de playlist con el ratón.
- [x] **Optimizaciones de rendimiento y persistencia v2:** Formato de guardado asíncrono compacto en SQLite (-99% de espacio en disco) y eliminación de latencias al arrancar.
- [x] **Ergonomía del Reproductor & Navegación:** Nuevo panel lateral « Juegos », deslizador de volumen integrado en la cabecera del Reproductor e inicio directo en la vista Reproductor.

---

### 🟢 Versión 0.3.0 — Soporte de Playlists, Fundido de Audio & Robustez *(Actual)*
- [x] **Compatibilidad total con listas de reproducción:** Indexación automática de formatos `.m3u`, `.m3u8`, `.pls`, `.xspf`, `.wpl` en el árbol de carpetas con el icono `🎶`.
- [x] **Orden secuencial y detección de pistas ausentes:** Respeto estricto del orden original de la playlist y señalización visual de archivos faltantes (`⚠️`) sin interrumpir la reproducción.
- [x] **Fundido acústico de entrada (*Fade-in*):** Subida progresiva de volumen durante 1 segundo al iniciar o reanudar una pista de audio.
- [x] **Fluidez de la sincronización en segundo plano:** Cola silenciosa continua en segundo plano sin cuadros de diálogo intrusivos y preservación del despliegue del árbol de carpetas.
- [x] **Ajuste dinámico de carátulas:** Centrado y redimensionamiento fluido al alternar pantalla completa o cambiar el tamaño de ventana.

---

### 🟡 Versión 0.4.0 — Experiencia de Audio Avanzada, Artistas & Empaquetado Multiplataforma
- [ ] **Despliegue multiplataforma automatizado (Linux & macOS):** Compilación nativa y empaquetado automatizado mediante GitHub Actions para Linux (`.AppImage` / `.tar.gz`) y macOS Apple Silicon ARM & Intel (`.dmg`), junto al ejecutable de Windows.
- [ ] **Gestión de artistas y discografía asociada:** Vista dedicada por artista con álbumes, sencillos y discografía completa.
- [ ] **Ecualizador gráfico (EQ):** Presets de sonido (Rock, Pop, Jazz, Bass Boost) y ecualizador paramétrico multibanda.
- [ ] **Editor de metadatos integrado:** Edición directa de etiquetas ID3 / Vorbis en pistas individuales o selecciones múltiples.
- [ ] **Descarga automática de carátulas:** Búsqueda en línea (MusicBrainz / Cover Art Archive) de portadas faltantes.
- [ ] **Filtros de búsqueda avanzados:** Filtrado combinado por género, año, tasa de bits (bitrate) y formato sin pérdidas (Lossless).
- [ ] **Crossfade configurable:** Transición personalizada en fundido encadenado entre canciones.

---

### 🔵 Versión 0.5.0 — Conector Cloud Google Drive
- [ ] **Autenticación segura OAuth 2.0:** Conexión simplificada mediante navegador web sin almacenar secretos en texto plano.
- [ ] **Escaneo remoto de carpetas de Google Drive:** Indexación de archivos de audio presentes en carpetas configuradas.
- [ ] **Reproducción directa en streaming en la nube:** Escucha de pistas remotas con almacenamiento en caché local transparente.
- [ ] **Sincronización bidireccional selectiva:** Descarga local de pistas desde la nube o subida de pistas locales a Google Drive.

---

### 🟣 Versión 0.6.0 — Integraciones de Streaming (Spotify, Deezer & Amazon Music)
- [ ] **Conector Spotify (Web API):** Conexión de la cuenta de usuario para importar playlists y biblioteca.
- [ ] **Conector Amazon Music:** Escaneo, reproducción en streaming y sincronización de colecciones remotas (OAuth 2.0).
- [ ] **Coincidencia híbrida inteligente:** Correspondencia entre títulos de playlists remotas y pistas locales existentes en alta fidelidad.
- [ ] **Vista unificada de la colección:** Visualización lado a lado de pistas locales y pistas exclusivas de streaming.

---

### 🌟 Versión 1.0.0 — Desduplicación Inteligente & Versión Estable
- [ ] **Huella acústica digital (Audio Fingerprinting):** Detección de duplicados independientemente de etiquetas erróneas o remuestreo de tasas de bits.
- [ ] **Asistente de resolución de duplicados:** Comparación inteligente de calidad (selección automática de la mejor fuente bitrate/lossless) con archivado seguro.
- [ ] **Empaquetado multiplataforma oficial:** Instaladores firmados para Windows (`.exe` / portable), macOS (`.dmg` Apple Silicon & Intel) y Linux (`AppImage` / `.deb`).
- [ ] **Documentación completa para el usuario:** Guía ilustrada paso a paso y sitio web en GitHub Pages.

---

## 💡 Proponer una función

¿Tienes una idea o una necesidad específica?
- Abre un debate o reporte en [GitHub Issues](https://github.com/LEF97/Audio-Multi-Source-Organizer/issues) utilizando la plantilla *Feature Request*.
- ¡Vota en las propuestas comunitarias para priorizar el desarrollo!
