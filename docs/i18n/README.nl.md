# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <b>Nederlands</b> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) is een moderne, responsieve en crossplatform desktop audio-speler (Windows, Linux, macOS). Ontworpen om audiophiles volledige controle te geven over hun lokale muziekbibliotheek (MP3, FLAC, OGG…), ondersteunt het nu ook afspeellijsten (M3U, PLS, XSPF, WPL), CUE-bestanden (albums van één bestand opgesplitst in tracks) en integreert een geheel nieuwe audio blind test modus! Het project evolueert naar een centrale commandocentrale die in staat is om hybride muziekcollecties te organiseren, duplicaten te verwijderen en te synchroniseren die verspreid zijn over lokale schijven, cloudopslag (Google Drive) en streamingdiensten (Spotify, Deezer, Amazon Music).

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

## 📌 Functionaliteiten & Status van het project

| Functionaliteit | Beschrijving | Status |
| :--- | :---: | :---: |
| **Geïntegreerde VLC-mediaspeler** | Lichte, autonome audio-speler met automatische installatie van VLC portable en vloeiende volumeregeling | 🟢 Implémenté |
| **Multithreaded lokale scanner** | Recursieve en snelle ontdekking van lokale audiobestanden (MP3, FLAC, AAC, OGG...) | 🟢 Implémenté |
| **Metadata-extractie** | Lezen/schrijven ID3, Vorbis Comments en berekening van audio-vingerafdruk (`mutagen`) | 🟢 Implémenté |
| **Ondersteuning van Playlists (M3U, PLS, XSPF, WPL) & CUE-bladen** | Boomstructuur-indexering (🎶), sequentiële luistervolgorde, visuele detectie van ontbrekende nummers; de bestanden `.cue` (💿) openen als een virtuele trackmap met hun duur en spelen als echte tracks | 🟢 Implémenté |
| **Playlistbeheerder & Drag-and-Drop** | Gevirtualiseerde wachtrij, vloeiend drag & drop, omkeerbare willekeurige volgorde (shuffle) en loops | 🟢 Implémenté |
| **Interactieve « 🎲 Blind Test » modus** | Immersief muzikaal spel met animatie-tijdtelling, geluidsfade, zachte onthulling en automatische opeenvolging | 🟢 Implémenté |
| **In-app updates** | Automatische/handmatige versiecontrole via GitHub Releases | 🟢 Geïmplementeerd |
| **Beheer van artiesten & Discografie** | Specifieke weergave per artiest met albums, singles en volledige discografie | 🟡 Gepland |
| **Grafische equalizer (EQ)** | Audio presets en parametrische multiband equalizer | 🟡 Gepland |
| **Google Drive Connector** | Scannen en synchroniseren van externe audio collecties via OAuth 2.0 | ⚪ Gepland |
| **Amazon Music Connector** | Scannen en synchroniseren van externe collecties via OAuth 2.0 | ⚪ Gepland |
| **Spotify / Deezer Connector** | Importeren van afspeellijsten en trackmatching | ⚪ Gepland |
| **Slim deduplicatie** | Detectie van duplicaten (vage titel/artiest + akoestische vingerafdrukken) | ⚪ Gepland |

> 💡 *Om de details van de geplande mijlpalen en versies te bekijken, raadpleeg de [Feuille de route (Roadmap)](../../ROADMAP.md).*

---

## 📌 Beschikbare talen

Engels, Frans, Spaans, Duits, Italiaans, Portugees, Japans, Russisch, Pools, Turks, Nederlands, Zweeds, Indonesisch, Bulgaars, Servisch, Witroetsisch, Grieks, Catalaans, Baskisch, Galiciërs, Tsjechisch, Slowaaks, Hongaars, Kroatisch, Sloveens, Bosnisch, Estoostens, Lets, Litouws, Noors, Deens, Fins, IJslands, Maleis, Tagalog, Swahili, Esperanto, Vereenvoudigd Chinees, Traditioneel Chinees, Koreaans, Arabisch, Hebreeuws, Vietnamees

---

## 🚀 Snelle start

### Vereisten

- **Python 3.11** of hoger geïnstalleerd
- Git

### Installatie

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

## 🧪 Start van de tests

Het project gebruikt `pytest` met een suite van unitair en integratietesten:

```bash
pytest -v
```

De tests draaien automatisch op **Windows, macOS en Ubuntu** bij elke push via GitHub Actions.

---

## 🔒 Veiligheid & API-sleutels

- **Commit nooit echte API-sleutels of authenticatietokens.**
- Het bestand `.gitignore` is vooraf geconfigureerd om `.env`, `credentials.json`, `token.json` en alle lokale SQLite-databases te blokkeren.
- Gebruik `.env.example` als sjabloon voor uw ontwikkelomgeving.

---

## 📋 Documentatie & Projectvervolging

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Gedetailleerd logboek van versies, nieuwe functies en bugfixes.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Roadmap van toekomstige mijlpalen (Artisten, Cloud, Spotify, Deduplicatie).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Softwarearchitectuurhandboek en regels voor codekwaliteit.

---

## 💖 Het project ondersteunen & Distributie

AMSO is een gratis en vrije software (open source). Als u de applicatie waardeert en het ontwikkelen ervan wilt steunen:

- 🎮 **Downloaden & Betaal wat je wilt :** [Itch.io pagina van AMSO](https://lef97.itch.io/audio-multi-source-organizer) (pre-gecompileerd uitvoerbaar bestand klaar voor gebruik)
- ☕ **Een directe donatie doen :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [LEF97 sponsoren](https://github.com/sponsors/LEF97)

---

## 📄 Licentie

Dit project is onder licentie **GNU General Public License v3.0 (GPL-3.0)** — raadpleeg het bestand [LICENSE](../../LICENSE) voor meer details.
