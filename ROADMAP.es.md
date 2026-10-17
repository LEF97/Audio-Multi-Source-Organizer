# Hoja de Ruta (Roadmap) — AMSO

<p align="right">
  <a href="ROADMAP.fr.md">Français</a> • <a href="ROADMAP.md">English</a> • <b>Español</b> • <a href="ROADMAP.de.md">Deutsch</a> • <a href="ROADMAP.it.md">Italiano</a>
</p>

---

Este documento detalla las directrices estratégicas, las funciones planificadas y los futuros hitos del proyecto **Audio Multi-Source Organizer (AMSO)**.

---

## 🎯 Visión del Proyecto

AMSO tiene como objetivo convertirse en el **hub musical universal y descentralizado** de referencia: una aplicación rápida, ligera, elegante y sin compromisos en materia de privacidad, que permite controlar la colección de audio tanto si está almacenada en discos duros, archivada en la nube o en servicios de streaming.

---

## 🗺️ Hitos y Versiones

### 🟢 Versión 0.1.0 — Lanzamiento Inicial & Fundaciones (Octubre 2026)
- **Estado :** ✅ Terminado
- Motor de reproducción nativo con soporte python-vlc y descarga automática portátil.
- Escaneo multihilo e indexación SQLite de alta velocidad.
- Gestión de listas de reproducción con drag & drop y guardado de sesión.
- Interfaz gráfica moderna PySide6 (Dark Mode) con 5 idiomas (FR, EN, ES, DE, IT).
- Verificación automática y manual de actualizaciones in-app (GitHub Releases).

---

### 🟡 Versión 0.2.0 — Gestión de Artistas & Calidad de Audio (Noviembre 2026)
- **Vista dedicada por Artista :** Exploración por artista con biografía, álbumes y sencillos.
- **Ecualizador gráfico (EQ) :** Ajustes preestablecidos y ecualizador paramétrico multibanda.
- **Transiciones avanzadas :** Modos Gapless y Crossfade totalmente configurables.

---

### ⚪ Versión 0.3.0 — Conectores en la Nube (Diciembre 2026)
- **Google Drive :** Conexión OAuth 2.0 y sincronización de colecciones en la nube.
- **Amazon Music :** Exploración remota y sincronización de carpetas musicales.

---

### ⚪ Versión 0.4.0 — Desduplicación Inteligente & Streaming (Enero 2027)
- **Desduplicación avanzada :** Detección de duplicados mediante huella acústica (Chromaprint / AcoustID) y metadatos difusos.
- **Spotify / Deezer :** Importación de listas de reproducción y correspondencia híbrida.

---

### ⚪ Versión 1.0.0 — Estabilidad y Ecosistema Completo (Primer trimestre 2027)
- Sincronización bidireccional completa.
- Sistema de complementos (plugins).
- Rendimiento y pruebas de estrés para bibliotecas de más de 100.000 títulos.
