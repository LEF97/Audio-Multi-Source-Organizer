# Registro de cambios (Changelog) — AMSO

<p align="right">
  <a href="../../CHANGELOG.fr.md">Français</a> • <a href="../../CHANGELOG.md">English</a> • <b>Español</b> • <a href="CHANGELOG.de.md">Deutsch</a> • <a href="CHANGELOG.it.md">Italiano</a>
</p>

---

Todas las modificaciones notables realizadas al proyecto **Audio Multi-Source Organizer (AMSO)** están documentadas en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/)
y este proyecto se adhiere a la especificación [Semantic Versioning (SemVer)](https://semver.org/lang/fr/).

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
- **Motor de audio nativo WASAPI y resolución de la interrupción prematura al final de la pista:**
  - *Salida de audio nativa Windows WASAPI (`mmdevice`)*: eliminación de la forzada de `--aout=directsound` bajo Windows. El módulo DirectSound de VLC truncaba de manera anormal los 1,3 a 1,4 segundos finales de los archivos de audio (cortando el final de *Sirius*). La alineación en `mmdevice` permite a LibVLC transmitir el flujo de audio completo hasta el último milisegundo en 32-bit float.
  - *Eliminación de bops y artefactos de clics rápidos*: eliminación de cortes artificiales de volumen a 0 durante el `seek` y `stop` que provocaban discontinuidades de fase y colisiones de temporizadores asíncronos durante clics rápidos. El reposicionamiento temporal (`set_time`) y la detención ahora se ejecutan de manera nativa y fluida.
  - *Eliminación de micro-fallos al final de la pista / pasajes tranquilos*: detención del sondeo permanente de volumen en el bucle de tick, evitando enviar ajustes de ganancia de hardware repetitivos continuamente durante la reproducción.
- **Precisión milimétrica de las transiciones y transiciones fluidas (Gapless y Sin fundido) :**
  - *Eliminación de chasquidos y pops al iniciar la siguiente pista*: eliminación de la forzada de volumen a 0 en el segundo reproductor en espera, lo que provocaba una interrupción global de la sesión bajo WASAPI y luego un transitorio impulsivo («chasquido») al desbloquear la pausa. El segundo reproductor se precarga en pausa (`:start-paused`) con el volumen nominal sin alterar la pista actual.
  - *Enchaînement sans blanc (Gapless 0)* : consideración exacta de la latencia del pipeline LibVLC (`vlc_gapless_latency_ms`, 250 ms por defecto) para desbloquear el siguiente reproductor antes del final exacto de la pista actual, asegurando una continuidad musical ininterrumpida sin ningún hueco de silencio entre pistas enlazadas (*Sirius* -> *Eye In The Sky*).
  - *Enchaînement naturel en mode Pas de fondu* : eliminación del retraso artificial de 400 ms después de `State.Ended`, lo que permite una transición inmediata y limpia al finalizar la reproducción del título anterior.
- **Eliminación de los disparadores de reproducción de audio intempestivos:**
  - *Retroceso (`previous` / `seek`)* : el comando de pista anterior (`previous()`) respeta estrictamente el estado de pausa del reproductor y utiliza `load_index()` para cargar el título sin iniciar la reproducción si el reproductor estaba en pausa. De manera similar, un desplazamiento temporal (`seek_ms`) anula cualquier preacarga en espera o vaciado de transición pendiente, y reposiciona la pista sin reproducción forzada si el reproductor estaba en pausa o al final de una canción (`State.Ended`).
  - *Navegación entre menús (salida del Blind Test a otras pestañas)* : centralización de la navegación de pestañas (`_switch_to_page`), detención forzada del Blind Test y reinicio de cualquier standby activo al salir de la página para prohibir cualquier reinicio autónomo de la música en segundo plano.
- **Fundido en cadena sin cortes (Crossfade Equal-Power) :**
  - *Aislamiento de volúmenes a nivel de hardware bajo Windows* : asignación dinámica de la salida de audio `directsound` para el modo de fundido en cadena (los modos estándar y gapless permanecen en `mmdevice` nativo sin truncamiento). A diferencia de WASAPI (`mmdevice`), cuyo ajuste de volumen afecta la sesión global del proceso y generaba un conflicto violento (hachado / tartamudeo de 40 Hz entre el título saliente y el entrante), DirectSound aísla el volumen propio de cada búfer secundario (`IDirectSoundBuffer::SetVolume`).
  - *Curvas de fundido perfectamente suaves* : transición continua de potencia igual (coseno para el título saliente, seno para el título entrante) sin ningún valle acústico ni tartamudeo al activar el fundido.
- **Fiabilización del Motor de Búfer Continuo en Memoria (Fase 2 - QAudioSink / Ring Buffer):**
  - *Respeto absoluto de la pausa al retroceder (`previous()`)*: `previous()` ahora conserva fielmente el estado de pausa, carga la pista anterior sin iniciar la reproducción, y suspende el flujo de audio sin microcortes ni reinicio improvisado.
  - *Transición natural en modo Sin fundido*: eliminación de la precarga en espera innecesaria en modo estándar, transición directa a través del ciclo de carga estándar con actualización inmediata del título, de la carátula y de la duración exacta.
  - *Resolución de colisiones y saltos en modo Gapless 0*: ciclo de vida hermético del decodificador en espera, desconexiones/reconexiones completas de los signos (`ready_to_play`, `chunk_decoded`), restablecimiento del seek después de la conexión, y rechazo estricto de paquetes PCM no asociados a la pista actual en el búfer de memoria.
  - *Fundido cruzado en memoria de potencia igual (Modo Crossfade)*:
    - Mezcla PCM matemática de muestras de 16 bits (curvas cos/sin de potencia igual) a partir del desplazamiento de reproducción actual (`_play_offset`), con *clamping* anti-recorte.
    - Separación estricta entre el inicio de audio del fundido y el cambio de la interfaz gráfica: la UI permanece visible en la pista saliente durante su desvanecimiento progresivo, y cambia a la pista entrante exactamente en el apagado natural de la canción, eliminando la interrupción visual y sonora prematura.
    - Sincronización y ajuste temporal continuos: purga instantánea de los datos PCM consumidos de la pista saliente al apagarse (`finish_crossfade`), recalibración precisa del desplazamiento de reproducción (`_base_offset_ms`) sobre la duración exacta del fundido, garantizando un desplazamiento continuo del cursor sin teletransportación, así como un reposicionamiento temporal (`seek_ms`) perfectamente alineado.
- Desglose modular: extracción de `amso/services/player_vlc_transitions.py` (transiciones directas LibVLC) que permite mantener todos los archivos del reproductor por debajo de las 450 líneas.
  - *Restablecimiento integral en caliente del reproductor (`reset_playback`)*:
    - Cualquier modificación en la Configuración del motor de audio (*VLC directo* vs *Búfer continuo*) o del modo de transición (*Sin fundido*, *Gapless 0*, *Crossfade*) interrumpe inmediatamente la reproducción en curso y restablece completamente los flujos (destrucción limpia de `QAudioSink`, vaciado de búferes PCM en memoria, detención de decodificadores, desvinculación de medios LibVLC, anulación de todos los temporizadores de transición/fundido).
    - La pista activa permanece seleccionada en pausa en 00:00, lista para ser reproducida bajo la nueva configuración sin necesidad de reiniciar la aplicación.


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
- **Resolución de errores `disk I/O error` (SQLite en Windows)**: configuración del modo WAL una sola vez al inicializar la base de datos, adición de `PRAGMA busy_timeout = 30000`, almacenamiento temporal en memoria RAM (`PRAGMA temp_store = MEMORY`) y mecanismo de reintentos automáticos con backoff exponencial para eliminar conflictos de bloqueo de archivos durante escaneos multihilo.
- **Eliminación de alertas modales bloqueantes en segundo plano**: las sincronizaciones automáticas en segundo plano ya no muestran un diálogo modal intrusivo en caso de error transitorio, sino que registran la alerta correctamente en el registro de actividad y en la barra de estado cliqueable.
- **Volumen de audio demasiado bajo al iniciar**: eliminación de una condición de carrera durante la inicialización del motor de reproducción VLC y neutralización del atenuamiento automático (*ducking*) del mezclador de audio de Windows.
- **Visualización del logo oficial en el ejecutable de Windows**: corrección de la resolución multi-rutas de recursos incrustados de PyInstaller (`sys._MEIPASS`) para mostrar el logo AMSO en alta definición en la barra lateral y la página Acerca de en lugar del icono de reserva 🎵.
- **Restauración de la lista de reproducción y aislamiento hermético de las pruebas**: eliminación de una contaminación del perfil de usuario donde la ejecución de pruebas automatizadas podía sobrescribir `saved_playlist.json` con pistas ficticias (*Track 1, Track 2, Track 3*) y una posición temporal errónea (14:10 en una canción de 3:00). Aislamiento completo de `AMSO_DATA_DIR`, `AMSO_PLAYLIST_PATH` y `AMSO_DB_PATH` en el entorno de prueba, filtrado automático de pistas locales fantasma o no encontradas al cargar la lista de reproducción, y aseguramiento de la posición inicial para no exceder nunca la duración del título.
- **Optimización del tiempo de inicio con listas de reproducción grandes (eliminación del bloqueo al 85 %)**: eliminación de un cuello de botella bloqueante en el hilo principal durante la restauración de la sesión de reproducción. La validación de la lista de reproducción ejecutaba miles de llamadas de disco síncronas `Path.exists()` (~40 segundos para 12 000 canciones). Ahora prefiere una verificación instantánea en memoria O(1) (< 1 ms) para todas las pistas provenientes de la base de datos SQLite activa, haciendo que el inicio de la aplicación sea instantáneo.
- **Progresión fluida paso a paso y eliminación del retroceso visual del Splash Screen**: rediseño del seguimiento de progreso al iniciar con animación fluida paso a paso del 1 % en 1 % (10 ms por incremento) para una transición continua y pulcra entre los niveles regulares (15 % preferencias, 25 % tema, 35 % SQLite, 45 % motor de audio, 60 % interfaz, 75 % biblioteca, 90 % restauración de sesión, 100 % finalización). Resolución de un conflicto de estilo CSS global donde la aplicación del tema oscuro imponía un `max-width: 220px` en todas las barras de progreso, dividiendo repentinamente el ancho del splash screen a la mitad y dando la ilusión visual de un retroceso de la aguja azul. Santuario del ancho (`#splashProgressBar`), bloqueo de la progresión estrictamente monótona y eliminación de la mención superflua a la derecha del pie de página.
- **Renderizado visual de la carátula por defecto (vinilo y nota)**: eliminación del recorte vertical en el borde derecho del icono de la nota musical en el centro del vinilo, causado por la aplicación de un negrita sintético (*synthetic bold*) por el motor de fuentes DirectWrite en el emoji bajo Windows.
- **Detección estricta de carátulas de carpeta (*folder cover*)**: fiabilización del algoritmo de búsqueda de imágenes en el directorio para aceptar solo nombres de carátulas legítimos (`folder`, `cover`, `front`, nombre de la canción, `album`, `artwork`) y rechazar imágenes arbitrarias o con prefijo (ej. `exfolder.webp`). Invalidación inmediata de la caché ante cualquier renombrado o eliminación en el directorio para cambiar fielmente al visual de vinilo por defecto (« carátula integrada > imagen de carpeta > vinilo música »).

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
