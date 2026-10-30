# Registro de cambios (Changelog) — AMSO

<p align="right">
  <a href="../../CHANGELOG.fr.md">Français</a> • <a href="../../CHANGELOG.md">English</a> • <b>Español</b> • <a href="CHANGELOG.de.md">Deutsch</a> • <a href="CHANGELOG.it.md">Italiano</a>
</p>

---

Todas las modificaciones notables realizadas al proyecto **Audio Multi-Source Organizer (AMSO)** están documentadas en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/)
y este proyecto se adhiere a la especificación [Semantic Versioning (SemVer)](https://semver.org/lang/fr/).

---

## [0.5.0-dev] - 2026-10-30

### Added
- *(TBD)*

## [0.4.1] - 2026-10-29

### Added
- **No regresión de transiciones de audio (TNR):** `scripts/tnr_transitions.bat` reproduce el final de un tema y luego el comienzo del siguiente (Sirius → Eye in the Sky por defecto) en el reproductor real, con una salida de audio ficticia, y compara la grabación con una construcción ideal (idéntica al muestreo en gapless, fundido a potencia igual en crossfade, ausencia de corte, sesión de audio única).
- **Registro de TNR:** cada ejecución escribe `tests/tnr/log/tnr_AAAA-MM-JJ_HH-MM-SS.log` (versión, commit, pistas, resultados detallados, mensajes de Qt y registros del reproductor); el directorio es ignorado por git.
- **Registro de inicio:** `startup.log` en el directorio de datos cronometra cada paso del lanzamiento, la restauración de la sesión y los hilos aún activos al cierre.
- **Registro de fallo nativo:** `crash.log` en el directorio de datos (`%APPDATA%/AMSO/`) recibe la pila de un fallo de LibVLC o de Qt.
- **Estado de libVLC:** la configuración del reproductor muestra la versión de libVLC realmente cargada y su procedencia (copia AMSO o VLC del sistema), con la ruta en la información emergente.
- **Preparación para Linux y macOS:** la descarga automática de VLC (archivo de Windows) está reservada para Windows; en otras partes, AMSO indica cómo instalar VLC (gestor de paquetes, VLC.app). En macOS, VLC.app también se detecta en `~/Applications`.
- **Versiones experimentales para Linux y macOS (no probadas):** `release.yml` produce un archivo `.tar.gz` y un `.AppImage` (Linux x86_64), así como un `.dmg` no firmado para macOS Apple Silicon e Intel, a través de `scripts/package_unix.py`. VLC debe estar instalado (gestor de paquetes o VLC.app) y, en Linux, las bibliotecas `libpulse0`, `libxcb-cursor0` y `libxkbcommon-x11-0`. El motor de audio `buffer` y la no regresión de las transiciones solo han sido validados en Windows: los comentarios (`startup.log`, `crash.log`) son bienvenidos. El CI Linux ahora instala `libpulse0` (QtMultimedia fallaba al importar) y el despliegue itch.io del flujo de trabajo solo ocurre en una etiqueta.

### Cambios
- **Inicio:** la tabla « Todas las canciones » ya no se carga (hasta ~3 veces 50 000 pistas) antes de abrir su página; el contador de la barra permanece exacto mediante una consulta `COUNT`.
- **Inicio:** la pantalla de carga se muestra antes de importar la ventana principal y la base, numpy ya no se carga más que en segundo plano una vez que la ventana es visible, el ícono y el logo se almacenan en caché.

### Corregido
- **Inicio sin red:** ya no se realiza ningún sondeo de disco (`exists`, `isdir`) en una ruta de red (UNC o unidad mapeada) desde el hilo de interfaz al iniciar (carátula, monitorización de carpetas, restauración de sesión); una carpeta compartida inaccesible ya no congela la ventana. La carátula de una pista de red se vuelve a verificar cada 30 s en segundo plano.
- **Cierre:** corrección de « QThread: Destroyed while thread is still running » (señal `finished` del worker de carátulas que enmascaraba la de `QThread`, hilos de carátulas no esperados).
- **Motor `buffer` — cambio de modo de transición:** después de un cambio de modo en la configuración del reproductor, un `seek` y luego Reproducir ya no iniciaban nada (la reinicialización dejaba el motor sin salida de audio, y el reproductor cambiaba erróneamente a la ruta VLC). La sesión de audio ahora se recrea inmediatamente. La pista actual vuelve a empezar desde el principio después de un cambio de motor o de modo. Por último, reanudar un título cargado en pausa (después de un reinicio o un `seek` a la detención) reinicia el temporizador de transferencia del motor `buffer`: sin él, Reproducir no producía sonido alguno. El decodificador ya no emite los bloques de un decodaje reemplazado entretanto (reinicio seguido de Reproducir, `seeks` cercanos): podían falsear la posición o impedir el inicio del motor `buffer`.
- **Prueba a ciegas con el motor `buffer`:** Reproducir, Siguiente y Anterior no emitían sonido alguno (la pista permanecía cargada en pausa, era necesario volver a pulsar Reproducir): el cambio de pista reiniciaba la ronda, que reposicionaba la pista antes de la llegada del primer bloque decodificado. La ronda ya no reposiciona una pista que el propio reproductor acaba de iniciar.
- **Motor \`buffer\` — sonido alterado al mover o redimensionar la ventana:** la tarjeta de sonido era alimentada por un temporizador del hilo de interfaz (búfer de 185 ms); este hilo, bloqueado por el bucle de movimiento de Windows (hasta 400 ms medidos), la dejaba sin datos. El `QAudioSink` pasa a modo pull en un hilo de audio dedicado (`audio_output.py`): el búfer de memoria, el gapless y el crossfade no cambian, y el motor `vlc_direct` no está afectado.
- **Traducciones :** una clave ausente en el idioma y en inglés (clave reciente, presente solo en `fr.json`) se mostraba con su nombre técnico; el respaldo pasa ahora por el francés. `sync_translations.py` detecta las traducciones donde el modelo ha tomado el texto francés seguido de una transcripción (« texte (romaji) »), las vuelve a traducir, rechaza estas respuestas y ya no envía el inglés a Ollama.
- **Textos codificados :** la página de Estadísticas (« morceaux », « Go », « h »), los tamaños de archivo (Ko, Mo, Go) y el sufijo « s » de las duraciones del Blind Test pasan por claves de traducción.
- **Textos codificados (continuación) :** los mensajes del escáner, los errores del reproductor y del decodificador, la descarga de VLC, « Stéréo / Mono », la burbuja de información « Fichier introuvable », « SYSTÈME PRÊT » y la pantalla de inicio pasan por claves de traducción. Las 42 lenguas están resincronizadas (Ollama), incluidas 15 traducciones de las cuales los marcadores `{count}` / `{name}` habían desaparecido.
- **Diario de actividad traducido :** « Synchronisation réussie », « Durée », « Morceaux ajoutés », los niveles (SUCCESS…) y las cajas de export se mostraban en francés independientemente del idioma. Los mensajes ahora se registran en forma de clave y parámetros (nueva columna `i18n`, añadida sin tocar las entradas existentes) y se traducen al mostrarse. Las entradas ya registradas permanecen en francés.
- **Moteur `buffer` — « Suivant » manuel :** con la pista siguiente precargada (Gapless 0 o Crossfade), un « Suivant » iniciaba bien la pista siguiente pero conservaba la posición de la pista anterior (ej. 1:00). El raccord al sample cerca está ahora reservado para el final natural de la pista; un « Suivant » manual reinicia la siguiente en 0.
- **Moteur `buffer` — crossfade :** el fundido enchaîné está ahora mezclado durante la decodificación (calculado durante toda la duración solicitada, vectorizado). Ya no corta el final del título saliente, no acorta el fundido y ya no provoca saltos (el antiguo cálculo muestra por muestra bloqueaba el hilo de la interfaz).
- **Blind Test con el moteur `buffer` :** corrección de una recursión infinita (`track_changed` ↔ `seek_ratio`) que cerraba la aplicación; los fundidos de volumen del Blind Test ahora actúan también sobre este motor.
- **Décodeur audio (`amem`) :** el final de flujo anunciado por VLC detenía un `QTimer` desde el hilo de eventos de VLC (`QObject::killTimer: Timers cannot be stopped from another thread`, comportamiento indefinido en cada pista); ahora se retransmite al hilo Qt.
- **Moteur `buffer` — modo « Pas de fondu » :** la sesión de audio hardware ya no se cierra y se vuelve a abrir entre dos títulos.

---

## [0.4.0] - 2026-10-25

### Añadido
- **Soporte para hojas CUE (`.cue`):**
  - Un archivo `.cue` aparece en el árbol de directorios como una carpeta virtual (icono 💿) que contiene sus pistas con su título, su artista y su duración; el archivo de audio original sigue siendo legible normalmente.
  - Reproducción de una pista CUE como porción del archivo (inicio `INDEX 01`, fin al inicio de la siguiente pista, última pista hasta el final del archivo) con posición y duración propias de la pista, desplazamiento dentro de la pista y enlazado gapless / crossfade entre porciones (motor de búfer continuo únicamente; el motor `vlc_direct` muestra un mensaje explicativo).
  - Tolerancia a hojas mal formadas (línea `FILE` apuntando al `.cue` mismo: retroceso al archivo de audio del mismo nombre), múltiples `FILE` por hoja, codificaciones UTF-8 / CP1252.
- **Soporte extendido para 43 idiomas internacionales:**
  - Integración de 38 nuevos idiomas con sus etiquetas nativas en el selector de idioma (`amso/core/i18n.py`).
  - Traducción automatizada y paridad integral (401 claves por idioma) a través de la IA local Ollama (`mistral:latest`).
- Script de sincronización global con un clic: `scripts/sync_all_languages_ollama.bat`.
- **Modo de diagnóstico visual de traducciones (`⟦...⟧`) :**
  - Adición del argumento CLI `--debug-i18n` y del lanzador `run_debug_i18n.bat` que encierran cada texto traducido con etiquetas `⟦...⟧` para identificar inmediatamente en pantalla los textos dinámicos y aislar posibles cadenas codificadas.
- **Herramienta de auditoría e integridad i18n (`scripts/audit_translations.py`) :**
  - Detección automática de la paridad de 43 idiomas, detección de duplicados de etiquetas para fusionar e identificación de claves huérfanas vía `scripts/audit_translations.bat`.
- **Selector de arquitectura de audio en Configuración / Reproducción perfecta en modo gapless 0 (aún quedan algunas anomalías en modo cross fade) :**
  - Elección transparente en `Configuración > Reproductor` entre:
    - *Búfer continuo en memoria (QAudioSink / WASAPI)*: flujo único ininterrumpido hacia la tarjeta de sonido, transiciones gapless 0 y fundido sin interrupción física.
- *Sortie directe LibVLC (double lecteur matériel)* : motor clásico de hardware pilotado directamente por LibVLC.
- **Harnais de validation qualité unifié (Quality Gate) :** Creación del script `scripts/verify.py` y de su wrapper raíz `verify.bat` que ejecutan consecutivamente el formateo (Ruff), el linter (Ruff check), el tipado estricto (Mypy sin enmascaramiento), el control de los límites de tamaño de archivos y las pruebas automatizadas (Pytest).

### Corregido
- **Playlists y hojas CUE descubiertas: registro de actividad y actualización del árbol de directorios:** un escaneo que solo añadía playlists (M3U, PLS, XSPF, WPL, CUE) no se mencionaba en ninguna parte y no actualizaba el árbol de directorios (el nuevo nodo solo aparecía después de un reinicio). El registro ahora indica el número de playlists / hojas CUE añadidas, actualizadas o eliminadas (con los primeros nombres), y el árbol se actualiza al final del escaneo.
- **Motor de audio nativo WASAPI y Resolución de la interrupción prematura al final de la pista:**
  - *Salida de audio nativa Windows WASAPI (`mmdevice`)*: eliminación de la forzadura de --aout=directsound bajo Windows. El módulo DirectSound de VLC truncaba de manera anormal los 1,3 a 1,4 segundos finales de los archivos de audio (cortando el final de *Sirius*). La alineación en `mmdevice` permite a LibVLC transmitir la totalidad del flujo de audio hasta el último milisegundo en 32-bit float.
  - *Eliminación de bops y artefactos de clics rápidos*: eliminación de cortes artificiales de volumen a 0 durante el `seek` y `stop` que provocaban discontinuidades de fase y colisiones de temporizadores asíncronos durante clics rápidos. El reposicionamiento temporal (`set_time`) y la detención ahora se ejecutan de manera nativa y fluida.
  - *Eliminación de micro-fallos al final de la pista / pasajes tranquilos*: parada del sondeo permanente de volumen en el bucle de tick, evitando enviar ajustes de ganancia de hardware repetitivos continuamente durante la reproducción.
- **Precisión milimétrica de las transiciones y transiciones fluidas (Gapless y Sin fundido) :**
  - *Eliminación de chasquidos y pops al iniciar la siguiente pista* : eliminación de la forzación de volumen a 0 en el segundo reproductor en espera, lo que provocaba una interrupción global de la sesión bajo WASAPI y luego un transitorio impulsivo ("chasquido") al desbloquear la pausa. El segundo reproductor se precarga en pausa (`:start-paused`) con el volumen nominal sin alterar la pista actual.
  - *Transición sin pausas (Gapless 0)* : consideración exacta de la latencia del pipeline LibVLC (`vlc_gapless_latency_ms`, 250 ms por defecto) para desbloquear el siguiente reproductor antes del final exacto de la pista actual, asegurando una continuidad musical ininterrumpida sin ningún vacío de silencio entre pistas enlazadas (*Sirius* -> *Eye In The Sky*).
  - *Encadenamiento natural en modo Sin fundido* : eliminación del retardo artificial de 400 ms después de `State.Ended`, lo que permite una transición inmediata y limpia al finalizar la reproducción de la pista anterior.
- **Eliminación de activaciones de reproducción de audio prematuras:**
  - *Retroceso (`previous` / `seek`)* : el comando de pista anterior (`previous()`) respeta estrictamente el estado de pausa del reproductor y utiliza `load_index()` para cargar la pista sin iniciar la reproducción si el reproductor estaba en pausa. Del mismo modo, un desplazamiento temporal (`seek_ms`) anula cualquier preacarga en espera o vaciado de transición pendiente, y reposiciona la pista sin reproducción forzada si el reproductor estaba en pausa o al final de la pista (`State.Ended`).
  - *Navegación entre menús (salida del Blind Test a otras pestañas)* : centralización de la navegación de pestañas (`_switch_to_page`), detención forzada del Blind Test y reinicio de cualquier estado de espera activo al salir de la página para impedir cualquier reinicio autónomo de la música en segundo plano.
- **Fundido en cadena sin cortes (Crossfade Equal-Power) :**
  - *Aislamiento físico de volúmenes bajo Windows* : asignación dinámica de salida de audio `directsound` para el modo desvanecimiento en cadena (los modos estándar y gapless se mantienen en `mmdevice` nativo sin truncamiento). A diferencia de WASAPI (`mmdevice`), cuyo ajuste de volumen afecta a la sesión global del proceso y generaba un conflicto violento (fragmentación / tartamudeos a 40 Hz entre el título saliente y el entrante), DirectSound aísla el volumen propio de cada búfer secundario (`IDirectSoundBuffer::SetVolume`).
  - *Curvas de desvanecimiento perfectamente suaves* : transición en potencia igual continua (coseno para el título saliente, seno para el título entrante) sin ningún valle acústico ni tartamudeo al iniciar el desvanecimiento.
- **Fiabilización del Motor Búfer Continuo en Memoria (Fase 2 - QAudioSink / Ring Buffer) :**
  - *Respeto absoluto de la pausa al retroceder (`previous()`)* : `previous()` ahora conserva fielmente el estado de pausa, carga la pista anterior sin iniciar la reproducción, y suspende el flujo de audio sin microcortes ni reinicios improvisados.
  - *Transición natural en modo Sin desvanecimiento* : eliminación de la precarga en espera innecesaria en modo estándar, transición directa a través del ciclo de carga estándar con actualización inmediata del título, la carátula y la duración exacta.
  - *Resolución de colisiones y tartamudeos en modo Gapless 0* : ciclo de vida hermético del decodificador en espera, desconexiones/reconexiones completas de las señales (`ready_to_play`, `chunk_decoded`), restablecimiento del *seek* después de la conexión, y rechazo estricto de paquetes PCM no emparejados con el título actual en el búfer de memoria.
  - *Desvanecimiento cruzado en memoria de potencia igual (Modo Crossfade)* :
    - Mezcla matemática PCM de muestras de 16 bits (curvas cos/sin de potencia igual) a partir del desplazamiento de reproducción actual (`_play_offset`), con *clamping* anti-recorte.
- Separación estricta entre el disparo de audio del fundido y el cambio de la interfaz gráfica: la UI permanece visible en el título saliente durante su atenuación progresiva, y cambia al título entrante exactamente en la extinción natural de la canción, eliminando la interrupción visual y sonora prematura.
- Sincronización y ajuste temporal continuos: purga instantánea de los datos PCM consumidos de la pista saliente al extinguirse (`finish_crossfade`), recalibración precisa del offset de reproducción (`_base_offset_ms`) durante la duración exacta del fundido, garantizando un desplazamiento continuo del cursor sin teletransportación, así como un reposicionamiento temporal (`seek_ms`) perfectamente alineado.
- Diseño modular: extracción de `amso/services/player_vlc_transitions.py` (transiciones directas LibVLC) que permite mantener todos los archivos del reproductor por debajo de las 450 líneas.
  - *Reinicialización integral en caliente del reproductor (`reset_playback`)*:
    - Cualquier modificación en los Ajustes del motor de audio (*VLC directo* vs *Búfer continuo*) o en el modo de transición (*Sin fundido*, *Gapless 0*, *Crossfade*) detiene inmediatamente la reproducción en curso y reinicia completamente los flujos (destrucción limpia de `QAudioSink`, vaciado de los búferes PCM en memoria, detención de los decodificadores, desvinculación de los medios de LibVLC, anulación de todos los temporizadores de transición/fundido).
    - La pista activa permanece seleccionada en pausa en 00:00 lista para ser reproducida bajo la nueva configuración sin necesidad de reiniciar la aplicación.


### Cambios
- **Descomposición modular completa de la arquitectura (< 500 líneas por archivo):**
  - Objetivo alcanzado al 100 %: **0 archivo > 500 líneas** en toda la base de código AMSO (frente a 8 archivos por encima del umbral inicialmente).
  - Aligeramiento de `main_window.py` (~1 500 -> 357 líneas) mediante mixins especializados en `amso/ui/pages/`.
  - Descomposición de `player_service.py` (~1 400 -> 329 líneas) con la extracción de `player_transport.py`, `player_queue.py`, `player_transitions.py` y `windows_audio.py`.
  - División de `blind_test_view.py` (864 -> 447 líneas) hacia `round_controller.py` y `compat.py`.
  - División de `player_view.py` (693 -> 316 líneas) hacia `player_ui_builder.py`.
  - División de `settings_player.py` (668 -> 345 líneas) hacia `settings_player_effects.py`.
  - Separación de `theme.py` (633 -> 20 líneas) hacia `resources.py`, `qss_base.py` y `qss_components.py`.
  - Separación de `models.py` (631 -> 118 líneas) hacia `models_base.py`, `folder_track_model.py` y `playlist_table_model.py`.
  - Separación de `metadata.py` (621 -> 420 líneas) hacia `cover_art.py`.
  - Separación de `playlist_view.py` (603 -> 284 líneas) hacia `playlist_ui_builder.py` y `playlist_table_view.py`.
  - Separación de `logs_view.py` (512 -> 426 líneas) hacia `log_detail_dialog.py`.
  - Separación de `folders_page.py` (~970 -> 406 líneas) hacia `folders_tree.py` y `folders_trash.py`.
- **Racionalización y fusión de duplicados:**
  - Centralización de componentes compartidos (`ClickableSlider`, `EffectContainer`, `EffectsViewMixin`).
  - Factorización de etiquetas UI genéricas bajo el prefijo compartido `common.*` (`common.cancel`, `common.close`, `common.refresh`, `common.later`, `common.open_explorer`, `table.col_filename`, `table.col_source`, `table.col_folder_name`).
  - Normalización obligatoria de los finales de línea Windows CRLF (`\r\n`) en todos los archivos `.bat`.

### Corregido
- **Armonización y eliminación de residuos de traducción en 41 idiomas:**
  - Erradicación de más de 1 400 claves que permanecían en francés o en inglés por defecto a través de la nueva herramienta `scripts/fix_residual_translations.py` (`scripts/fix_residual_translations.bat`).
  - Corrección de las etiquetas de ambiente visual y los efectos gráficos (`player.visual_effect`, `effects.*`), ahora traducidos de forma nativa en todos los idiomas.
  - Resolución de placeholders de búsqueda híbridos (`topbar.search_placeholder`) que mezclaban el idioma objetivo y el inglés en las pantallas Duplicados, Fuentes y Navegación.
  - Traducción fiel de los títulos de configuración de fuentes (`settings.page_sources_title`, `settings.section_sources_title`) y de configuración general (`settings.page_title`).
  - Traducción integral del botón compartido de actualización (`common.refresh` : « 🔄 刷新 » en chino, etc.) en lugar de un « Actualiser » francés residual en los registros.
  - Localización completa de las secciones de soporte, donaciones y enlaces oficiales de la página Acerca de (`dialog.about_*`, `update.btn_support`).

---

## [0.3.0] - 2026-10-18

### Añadido
- **Soporte completo de archivos de lista de reproducción** :
  - Indexación automática de formatos de listas de reproducción: `.m3u`, `.m3u8`, `.pls`, `.xspf` y `.wpl`.
  - Integración en el árbol « Por carpeta » en forma de nodos dedicados que muestran el icono **`🎶`**.
  - Respeto del orden de escucha secuencial definido en la lista de reproducción (columna `#` con el orden 1, 2, 3...) sin clasificación alfabética automática forzada.
  - Gestión y detección visual de pistas faltantes o movidas: indicación mediante un prefijo **`⚠️`**, coloración de advertencia suave e infoburbuja descriptiva, sin bloquear la reproducción de otras pistas.
  - Menú contextual enriquecido en los nodos de la lista de reproducción: reproducción directa, adición a la cola y apertura de la ubicación del archivo de lista de reproducción en el Explorador de Windows.
- **Suave fundido de entrada (*Fade-in*)** :
  - Transición progresiva del volumen de 0% al volumen definido en 1 segundo al iniciar o reanudar una reproducción de audio (fuera del modo Blind Test).
- **Estabilidad y fluidez de la sincronización** :
  - Eliminación del cuadro de diálogo bloqueante « Scan already running » en favor de una secuencia silenciosa en cola.
  - Preservación de la selección y no recarga innecesaria del árbol de directorios si no se detecta ningún cambio de carpeta.
- **Visualización dinámica de las portadas** :
  - Corrección del redimensionamiento y reposicionamiento de la portada al pasar a pantalla completa / ventana o al redimensionar libremente la ventana.

---

## [0.2.0] - 2026-10-18

### Añadido

### Modo Blind Test y Sección Juegos
- **Nuevo cajón « 🎲 Juegos »** : Categoría dedicada plegable en la barra lateral que alberga la vista Blind Test (localizada en 5 idiomas).
- **Experiencia de juego inmersiva** : Cuenta regresiva visual dinámica en el centro de la portada oculta, revelación progresiva con un suave fundido y encadenamiento automático de rondas.
- **Gestión acústica avanzada** : Ajuste preciso de los tiempos de búsqueda, descubrimiento y el fundido sonoro de salida (*fade-out*).
- **Configuración dedicada** : Reubicación de los ajustes del Blind Test en `Ajustes > Reproductor`.

### Ergonomía y Gestión de Playlist
- **Rediseño del modo Aleatorio (Shuffle)**: Mezcla visual integral de la cola preservando la pista activa, botón de acción directa « 🎲 Mezclar títulos » y restauración fiel del orden original al desactivar.
- **Reorganización por Arrastrar y Soltar**: Reordenamiento fluido de las canciones con el ratón en la tabla sin interrumpir la reproducción.
- **Copia de seguridad asíncrona v2**: Formato compacto por identificadores SQLite reduciendo la huella en disco en un 99 % (acceso no bloqueante, 60 FPS constantes).
- **Comportamiento « No Autoplay »**: Añadir canciones a la cola ya no fuerza el inicio prematuro de la reproducción.

### Gestión de biblioteca & Papelera inteligente
- **Eliminación de doble nivel** : Opción entre la simple retirada de la biblioteca (con exclusión memorizada para futuros escaneos) y la eliminación física a la Papelera de Windows.
- **Vista dedicada « 🗑️ Papelera »** : Consulta de pistas excluidas y restauración con un clic con reintegro automático en la base de datos.
- **Estructura de árbol clarificada** : Distinción visual entre fuentes locales y cloud, estructura de árbol plegada por defecto al inicio y menús contextuales uniformizados.

### Estabilidad del motor de audio (LibVLC) & Rendimiento
- **Eliminación de bloqueos críticos** : Supresión del deadlock entre el hilo C interno de LibVLC y el bucle de eventos Qt (fin de congelamientos de interfaz y pantallas en blanco).
- **Robustez de las transiciones** : Bloqueo anti-reentrada en los cambios rápidos de pistas y resolución de bloqueos durante retrocesos sucesivos (« Pista anterior »).
- **Controles de volumen fiables** : Integración del control deslizante de volumen en la barra superior del reproductor y eliminación de conflictos de atenuación de sonido DirectSound.

### Interfaz & Enlaces oficiales
- **Modernización de la página « Acerca de »** : Encabezado realineado, analizador de espectro retro interactivo integrado debajo del texto y adición de botones oficiales (Ko-fi, GitHub Sponsors, GitHub, Itch.io).
- **Internacionalización integral** : Sincronización completa de todos los rótulos y opciones en 5 idiomas (FR, EN, ES, DE, IT).

### Corregido
- **Resolución de errores `disk I/O error` (SQLite en Windows)**: configuración del modo WAL una sola vez al inicializar el archivo de base de datos, adición de `PRAGMA busy_timeout = 30000`, almacenamiento temporal en memoria RAM (`PRAGMA temp_store = MEMORY`) y mecanismo de reintentos automáticos con backoff exponencial para eliminar conflictos de bloqueo de archivos durante escaneos multihilo.
- **Eliminación de alertas modales bloqueantes en segundo plano**: las sincronizaciones automáticas en segundo plano ya no muestran un cuadro de diálogo modal intrusivo en caso de error transitorio, sino que registran la alerta correctamente en el registro de actividad y la barra de estado cliqueable.
- **Volumen de audio demasiado bajo al iniciar**: eliminación de una condición de carrera durante la inicialización del motor de reproducción VLC y neutralización del atenuamiento automático (*ducking*) del mezclador de audio de Windows.
- **Visualización del logo oficial en el ejecutable de Windows**: corrección de la resolución de múltiples rutas de recursos empaquetados PyInstaller (`sys._MEIPASS`) para mostrar el logo AMSO de alta definición en la barra lateral y la página Acerca de en lugar del icono de marcador de posición 🎵.
- **Restauración de la lista de reproducción y aislamiento hermético de las pruebas**: eliminación de una contaminación del perfil de usuario donde la ejecución de pruebas automatizadas podía sobrescribir `saved_playlist.json` con pistas ficticias (*Track 1, Track 2, Track 3*) y una posición temporal errónea (14:10 en una canción de 3:00). Aislamiento completo de `AMSO_DATA_DIR`, `AMSO_PLAYLIST_PATH` y `AMSO_DB_PATH` en el entorno de prueba, filtrado automático de pistas locales fantasma o no encontradas al cargar la lista de reproducción, y aseguramiento de la posición inicial para no exceder nunca la duración del título.
- **Optimización del tiempo de inicio con grandes listas de reproducción (eliminación del congelamiento del 85 %)**: eliminación de un cuello de botella bloqueante en el hilo principal durante la restauración de la sesión de reproducción. La validación de la lista de reproducción ejecutaba miles de llamadas de disco síncronas `Path.exists()` (~40 segundos para 12 000 canciones). Ahora prioriza una verificación instantánea en memoria O(1) (< 1 ms) para todas las pistas de la base de datos SQLite activa, haciendo que el lanzamiento de la aplicación sea instantáneo.
- **Progresión fluida paso a paso y eliminación del retroceso visual del Splash Screen**: rediseño del seguimiento de progreso al inicio con animación fluida paso a paso del 1 % en 1 % (10 ms por incremento) para una transición continua y pulcra entre los niveles regulares (15 % preferencias, 25 % tema, 35 % SQLite, 45 % motor de audio, 60 % interfaz, 75 % biblioteca, 90 % restauración de sesión, 100 % finalización). Resolución de un conflicto de estilo CSS global donde la aplicación del tema oscuro imponía un `max-width: 220px` en todas las barras de progreso, dividiendo repentinamente el ancho del splash screen por la mitad y dando la ilusión visual de un retroceso de la aguja azul. Sanctuarización del ancho (`#splashProgressBar`), bloqueo de la progresión estrictamente monótona y eliminación de la mención superflua a la derecha del pie de página.
- **Renderizado visual de la carátula por defecto (vinilo y nota)**: eliminación del recorte vertical en el borde derecho del icono de nota musical en el centro del vinilo, causado por la aplicación de un negrita sintético (*synthetic bold*) por el motor de fuente DirectWrite en el emoji bajo Windows.
- **Detección estricta de las portadas de carpeta (*folder cover*)** : fiabilización del algoritmo de búsqueda de imágenes en el directorio para aceptar solo los nombres de portada legítimos (`folder`, `cover`, `front`, nom du morceau, `album`, `artwork`) y rechazar imágenes arbitrarias o prefijadas (ej. `exfolder.webp`). Invalidación inmediata de la caché ante cualquier renombrado o eliminación en la carpeta para cambiar fielmente a la vista de vinilo por defecto (« pochette intégrée > image folder > vinyle musique »).

---

## [0.1.0] - 2026-10-17

### Añadido
- **Motor de reproducción de audio integrado (python-vlc) :**
  - Soporte nativo de formatos de audio populares: MP3, FLAC, WAV, AAC, OGG, M4A, WMA.
  - Detección y descarga automática transparente de un binario VLC portátil en caso de ausencia de VLC en el sistema del usuario.
  - Control completo de reproducción: Play, Pause, Stop, Pista siguiente, Pista anterior, barra de progreso dinámica (Seekbar) y gestión del volumen de sonido.
  - Modos de reproducción: reproducción aleatoria (*Shuffle*) y modos de repetición (*Desactivado*, *Repetir la lista de reproducción*, *Repetir el título en bucle*).
  - Efectos visuales animados en tiempo real sincronizados con la reproducción (partículas, ondas, estrellas, distorsión espacial, aurora boreal, barras de espectro).
- **Gestor de Lista de Reproducción & Cola :**
  - Vista dedicada con tabla virtualizada que soporta decenas de miles de títulos sin latencia.
  - Reorganización intuitiva de la cola mediante arrastrar y soltar (*Drag & Drop*).
  - Menús contextuales completos: « Reproducir », « Añadir a la cola », « Eliminar de la cola », « Propiedades ».
  - Guardado automático de la sesión de reproducción (título actual, posición temporal en ms, lista de reproducción activa).
- **Escáner local multihilo de alto rendimiento:**
  - Recorrido recursivo asíncrono de directorios locales con barra de progreso y métricas en tiempo real.
  - Extracción rápida de metadatos (título, artista, álbum, año, género, duración, bitrate, número de pista) vía `mutagen`.
  - Extracción y almacenamiento en caché de portadas de álbumes integradas con renderizado asíncrono para evitar cualquier congelamiento de la interfaz.
  - Cálculo de huellas de hash de archivos para identificar duplicados físicos.
- **Base de datos SQLite optimizada:**
  - Arquitectura relacional sin ORM pesado para una ejecución casi instantánea de las consultas.
  - Gestión de fuentes, pistas escaneadas e historial de actividad.
- **Interfaz de Usuario Moderna (PySide6 / Dark Mode) :**
  - Tema oscuro personalizado de alta gama con paleta de colores cuidada y animaciones suaves.
  - Cajón lateral retráctil para la navegación principal y la configuración.
  - Soporte multilingüe completo (Francés, Inglés, Español, Alemán, Italiano) con cambio de idioma en caliente.
- Página dedicada « Acerca de » en Configuración: detalles del proyecto, insignia de versión, tecnologías de código abierto, enlaces a GitHub, Itch.io y plataformas de mecenazgo (Ko-fi, GitHub Sponsors).
- Verificador manual y automático de actualizaciones que consulta la API de GitHub Releases (`/releases/latest`) con una insignia de notificación interactiva.
- Atajo de teclado <kbd>F1</kbd> y clic directo en el logo AMSO para abrir la página « Acerca de ».

### Cambios
- Reemplazo del diálogo modal « Acerca de » por una subpágina integrada y fluida en Configuración.
- Reorganización de la navegación de Configuración en 5 secciones: General, Reproductor, Fuentes, Logs, Acerca de.
- Ocultación de la barra de menú estándar residual en favor de una interfaz limpia sin botón « Ayuda » huérfano.

### Corregido
- **Inicio en 00:00:** Reinicialización sistemática de la posición temporal (`_pending_seek_ms = 0`) al seleccionar una nueva música desde la biblioteca o la lista de reproducción, reservando la reanudación de la posición únicamente al botón « Play » de la sesión anterior restaurada.
- **Persistencia inmediata del volumen:** Guardado instantáneo en `config.ini` al manipular el control deslizante de volumen o el botón de silencio.
- **Bloqueo del volumen VLC:** Resincronización automática del volumen de audio al pasar al estado `Playing` en el bucle del reloj para evitar cualquier pérdida de ajuste durante el arranque en frío del decodificador VLC.
