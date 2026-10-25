# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <b>Galego</b> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) é un reprodutor de audio de escritorio moderno, reactivo e multiplatforma (Windows, Linux, macOS). Diseñado para ofrecer aos audiófilos un control total sobre a súa biblioteca musical local (MP3, FLAC, OGG…), agora ademós suporta listas de reprodución (M3U, PLS, XSPF, WPL), ficheiros CUE (álbums dun único ficheiro partidos en pistas) e integra un modo completamente novo de *blind test* de audio! O proxecto evolúcoa para ser un centro de comando unificado capaz de organizar, desduplicar e sincronizar coleccións musicais híbridas repartidas entre discos locais, armazenamento na nube (Google Drive) e servizos de *streaming* (Spotify, Deezer, Amazon Music).

---

<p align="center">
  <img src="../../screenshots/2026-10-25%20v0.4.0%2002.png" alt="Audio Multi-Source Organizer (AMSO) - Arborescence par dossiers & feuille CUE 💿 (pistes virtuelles)" width="850">
</p>

<p align="center">
  <img src="../../screenshots/2026-10-25%20v0.4.0.png" alt="Audio Multi-Source Organizer (AMSO) - Liste de lecture d'une feuille CUE (pistes virtuelles)" width="850">
</p>

<p align="center">
  <img src="../../screenshots/2026-10-18%20v0.3.0%20blind%20test.png" alt="Audio Multi-Source Organizer (AMSO) - Mini-jeu Blind Test & Décompte dynamique" width="850">
</p>

---

## 📌 Funcionalidades & Estado do proxecto

| Funcionalidade | Descripción | Estado |
| :--- | :---: | :---: |
| **Motor de reprodución VLC integrado** | Reproductor de audio ligero e autónomo con auto-instalación VLC portátil e xestión fluida do volume | 🟢 Implementado |
| **Scanner local multihilo** | Descubrimento recursivo e rápido de ficheiros de audio locais (MP3, FLAC, AAC, OGG...) | 🟢 Implementado |
| **Extracción de metadatos** | Lectura/escritura ID3, Vorbis Comments e cálculo de impresión de audio (`mutagen`) | 🟢 Implementado |
| **Suporte de Playlists (M3U, PLS, XSPF, WPL) e follas CUE** | Indexación arbórea (🎶), orde secuencial de escuta, localización visual das estrofas faltantes; os ficheiros `.cue` (💿) ábreanse como unha carpeta de pistas virtuais coa súa duración e reproxéctanse como pistas reais | 🟢 Implementado |
| **Gestor de Playlist e Arrastre-Solxe** | Cola virtualizada, drag & drop fluido, aleatorio (shuffle) reversible e liñas | 🟢 Implementado |
| **Modo « 🎲 Blind Test » interactivo** | Xogo musical inmersivo con conta atrás animada, fundido sonoro, revelación suave e enxaxamento automático | 🟢 Implementado |
| **Actualizacións in-app** | Verificación automática/manual das versións vía GitHub Releases | 🟢 Implementado |
| **Xestión de artistas & Discografía** | Vista dedicada por artista con álbums, singles e discografía completa | 🟡 Previsto |
| **Ecualizador gráfico (EQ)** | Presets de audio e ecualizador multibande paramétrico | 🟡 Previsto |
| **Connector Google Drive** | Scan e sincronización de coleccións de audio distantes vía OAuth 2.0 | ⚪ Planificado |
| **Connector Amazon Music** | Scan e sincronización de coleccións distantes vía OAuth 2.0 | ⚪ Planificado |
| **Connector Spotify / Deezer** | Importación de playlists e correspondencia de pistas | ⚪ Planificado |
| **Desduplicación inteligente** | Detección de duplicados (título/artista borrosos + huellas acústicas) | ⚪ Planificado |

> 💡 *Para consultar o detalle dos hitos e versións previstas, refrérese á [Feixe de ruta (Roadmap)](../../ROADMAP.md).*

---

## 📌 Idiomas dispoñibles

Inglés, Francés, Español, Alemán, Italiano, Portugués, Japonés, Ruso, Polaco, Turco, Neerlandés, Sueco, Indonesio, Búlgaro, Serbio, Bielorruso, Griego, Catalán, Vasco, Gallego, Checo, Eslovaco, Húngaro, Croata, Esloveno, Bosnio, Estonio, Letón, Lituanio, Noruego, Danés, Finlandés, Islandés, Malayo, Tagalo, Suajili, Esperanto, Chino simplificado, Chino tradicional, Coreano, Árabe, Hebreo, Vietnamita

---

## 🚀 Inicio rápido

### Prerreisitos

- **Python 3.11** ou superior instalado
- Git

### Instalación

```bash
# 1. Cloner le dépôt
git clone https://github.com/LEF97/Audio-Multi-Source-Organizer.git
cd audio-multi-source-organizer

# 2. Créer l'environnement virtuel
python -m venv .venv

# 3. Activer l'environnement
# Sous Windows (PowerShell) :
.venv\Scripts\Activate.ps1
# Sous Linux / macOS :
source .venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# Pour le développement et les tests :
pip install -e .[dev]

# 5. Configurer les variables d'environnement
cp .env.example .env

# 6. Lancer l'application
python main.py
```

---

## 🧪 Lanzamento dos testes

O proxecto utiliza `pytest` con un conjunto de tests unitarios e de integración :

```bash
pytest -v
```

Os testaxes executanse automáticamente en **Windows, macOS e Ubuntu** con cada push vía GitHub Actions.

---

## 🔒 Seguridade & Chaves de API

- **Nunca commiteis claves de API ni tokens de autenticación reais.**
- O ficheiro `.gitignore` está pré-configurado para bloquear `.env`, `credentials.json`, `token.json` e todas as bases de datos SQLite locais.
- Utilizai `.env.example` como modelo para o vosso ambiente de desenvolvemento.

---

## 📋 Documentación & Seguemento do proxecto

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Diario detallado das versións, novas funcionalidades e correccións de fallos.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Mapa de ruta dos futuros hitos (Artistas, Cloud, Spotify, Desduplicación).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Carta de arquitectura de software e regras de calidad de código.

---

## 💖 Apoistar o proxecto & Distribución

AMSO é un software libre e gratuito (open source). Se apreciades a aplicación e queres fomentar o seu desenvolvemento:

- 🎮 **Descarga & Paga o que queiras :** [Páxina Itch.io de AMSO](https://lef97.itch.io/audio-multi-source-organizer) (executable précompilado listo para usar)
- ☕ **Facer unha doación directa :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **Sponsors de GitHub :** [Sponsorizar LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licencia

Este proxecto está bajo licencia **GNU General Public License v3.0 (GPL-3.0)** — consulta o ficheiro [LICENSE](../../LICENSE) para máis detalles.
