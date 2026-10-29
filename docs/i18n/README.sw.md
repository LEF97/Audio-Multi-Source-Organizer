# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <b>Kiswahili</b> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) ni kielektroniki cha sauti cha kompyuta kisasa, kinachoitikia, na cha multi-platform (Windows, Linux, macOS). Kimeundwa kutoa wapenzi wa sauti udhibiti kamili juu ya maktaba yao ya muziki ya ndani (MP3, FLAC, OGG…), sasa inashughulikia orodha za kucheza (M3U, PLS, XSPF, WPL), karatasi za CUE (albamu za faili moja zilizokatwa katika sehemu) na inajumuisha hali mpya kabisa ya kupima sauti bila kuona! Mradi unakua kuwa kituo kikuu kinachoweza kupanga, kuondoa kurudiwa, na kuunganisha makusanyiko ya muziki ya mchanganyiko yaliyotawanyika kati ya diski za ndani, kuhifadhi wingu (Google Drive) na huduma za streaming (Spotify, Deezer, Amazon Music).

---

<p align="center">
  <img src="../../screenshots/2026-10-29%20v0.4.1.png" alt="Audio Multi-Source Organizer (AMSO) - Lecteur audio avec l'ambiance visuelle Hyperespace (champ d'étoiles 3D)" width="850">
</p>

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

## 📌 Vipengele & Hali ya mradi

| Kipengele | Maelezo | Hali |
| :--- | :---: | :---: |
| **Injini ya Kusikiliza sauti** | Kisikilizaji sauti kidogo na kujisimamia (VLC portable inasakinishwa kiotomatiki chini ya Windows). Injini mbili za kuchagua: matokeo ya moja kwa moja ya VLC, au injini ya kibandiko endelevu kwa muunganiko laini kati ya sehemu mbili (Gapless 0 ms, fondu enchaîné à puissance égale, sans coupure de la sortie audio) | 🟢 Implemented |
| **Usimamizi wa maktaba** | Skanning ya rekursiv na ya 'multithread' ya folda za ndani (MP3, FLAC, AAC, OGG...), usawazishaji wa mikono, kupangwa, au kwa wakati halisi, kikapu cha taka na takwimu za maktaba | 🟢 Implemented |
| **Kutolewa kwa metadata** | Kuandika/kusoma ID3, Vorbis Comments na kukokotoa alama ya sauti (`mutagen`) | 🟢 Implemented |
| **Usaidizi wa Playlists (M3U, PLS, XSPF, WPL) & karatasi za CUE** | Uorodheshaji wa mti (🎶), mpangilio wa kusikiliza kwa mpangilio, kutambua kwa macho sehemu zinazokosekana; faili za `.cue` (💿) zinafunguliwa kama folda ya sehemu za kiakili na muda wake na zinausikilizwa kama sehemu halisi | 🟢 Implemented |
| **Msimamizi wa Playlist & Kushusha-Kushika** | Orodha ya kusubiri ya kubadilishwa, kishusha-kushika laini, nasibu (shuffle) kurevesha na mizunguko | 🟢 Implemented |
| **Hali ya « 🎲 Blind Test » ya mwingiliano** | Mchezo wa muziki wenye kuingiza kwa kuhesabu kwa uhai, kupungua kwa sauti, kufichuliwa kwa upole na muunganiko wa kiotomatiki | 🟢 Implemented |
| **Sasisho za ndani** | Uhakiki wa matoleo kiotomatiki/kwa mikono kupitia GitHub Releases | 🟢 Imetekelezwa |
| **Matoleo ya Linux & macOS** | Paquets `.AppImage` / `.tar.gz` (Linux) et `.dmg` non signé (macOS), VLC requis | 🟡 Ya majaribio (hayajaribiwa) |
| **Usimamizi wa wasanii & Discografia** | Mtazamo maalum kwa msanii na albamu, singles, na discografia kamili | 🟡 Kimepangwa |
| **Msawazi wa picha (EQ)** | Mapendekezo ya sauti na msawazi wa band za nyingi wa kimaelezo | 🟡 Kimepangwa |
| **Kiunganishi cha Google Drive** | Skanning na ulinganishaji wa makusanyiko ya sauti ya mbali kupitia OAuth 2.0 | ⚪ Kimepangwa |
| **Kiunganishi cha Amazon Music** | Skanning na ulinganishaji wa makusanyiko ya sauti ya mbali kupitia OAuth 2.0 | ⚪ Kimepangwa |
| **Kiunganishi cha Spotify / Deezer** | Kuingiza playlists na kupanga nyimbo | ⚪ Kimepangwa |
| **Kuondoa nakala kwa akili** | Kugundua nakala (kichwa/msanii kidogo + alama za sauti) | ⚪ Kimepangwa |

> 💡 *Ili kuona undani wa hatua na matoleo yanayopangwa, tazama [Feuille de route (Roadmap)](../../ROADMAP.md).*

---

## 📌 Lugha zinazopatikana

Kiingereza, Kifaransa, Kihispania, Kijerumani, Kiitaliano, Koporugua, Kijapani, Kirusi, Kapolishi, Kiturki, Kinendi, Kiswedu, Kihindi, Kibulgari, Kiserbi, Kibiularus, Kigiriki, Kikatalania, Kibask, Kigalikia, Kicheki, Kislovak, Kihungari, Kikroatia, Kislovenia, Kibosnia, Kiestonia, Kilatini, Kilituani, Kinorweji, Kidanis, Kifinis, Kiisleni, Kimalayo, Kitagalog, Kiswahili, Kispéranto, Kichina rahisi, Kichina jadi, Kikorea, Kiarabu, Kihekibri, Kivieta

---

## 🚀 Kuanza Haraka

### Mahitaji ya awali

- **Python 3.11** au zaidi ya kusakinishwa
- Git

### Usakinishaji

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

## 🐧🍎 Linux na macOS: matoleo ya majaribio (hazijaribiwa)

Vifaa vya Linux (`.AppImage` / `.tar.gz`) na macOS (`.dmg`) vinatolewa **bila kupimwa**: AMSO vimehakikiwa tu kwenye Windows. Injini ya sauti yenye *buffer* endelevu (`buffer`) hasa haijathibitishwa kwenye mifumo hii. Maoni yako ni muhimu.

- **VLC inahitajika** (AMSO inapakua tu chini ya Windows) :
  - Linux : `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) au `sudo pacman -S vlc` (Arch).
  - macOS : weka **VLC.app** kutoka [videolan.org](https://www.videolan.org/vlc/) kwenye folda Applications.
- **Linux, maktaba za mfumo** : kiolesura cha Qt kinahitaji hasa `libpulse0` (sauti), `libxcb-cursor0` na `libxkbcommon-x11-0` (kwa mfano `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, `.dmg` lisilo saini** : wakati wa kwanza kuendesha, bonyeza kulia kwenye AMSO kisha **Fungua**, au endesha `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage** : kuifanya iweze kutekelezwa kwa kutumia `chmod +x AMSO*.AppImage`.
- **Ikiwa kuna tatizo**, tafadhali tuma faili `startup.log` na `crash.log` (ikiwepo) zilizopo kwenye folda ya data: `~/Library/Application Support/AMSO/` chini ya macOS, `~/.local/share/AMSO/` chini ya Linux. Taja mfumo wako na toleo la VLC.

---

## 🧪 Kuanza majaribio

Mradi unatumia `pytest` na seti ya vipimo vya vitengo na vipimo vya ushirikiano:

```bash
pytest -v
```

Mitkaji hivi hivi inatendeka kiotomatiki kwenye **Windows, macOS et Ubuntu** kila push kupitia GitHub Actions.

---

## 🔒 Usalama & Funguo za API

- **Kamwe usikani funguo halisi za API wala token za uthibitisho.**
- Faili ya `.gitignore` imewekwa awali ili kuzuia `.env`, `credentials.json`, `token.json` na hifadhidata zote za SQLite za ndani.
- Tumia `.env.example` kama mfano kwa mazingira yako ya maendeleo.

---

## 📋 Waraka & Ufuatiliaji wa mradi

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Kibhakdihi cha kina cha matoleo, vipengele vipya, na marekebisho ya makosa.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Ramani ya njia ya hatua zijazo (Artistes, Cloud, Spotify, Dédoublonnage).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Kanuni ya usanifu wa programu na sheria za ubora wa msimbo.

---

## 💖 Kuunga mkono mradi & Usambazaji

AMSO ni programu huru na ya bure (open source). Ikiwa unapenda programu na unataka kusaidia maendeleo yake:

- 🎮 **Upakuaji & Lipa Unachotaka :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (programu inayofanywa tayari na tayari ya kutumika)
- ☕ **Kutoa sadaka moja kwa moja :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [Kuunga mkono LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Leseni

Mradi huu unatumia leseni **GNU General Public License v3.0 (GPL-3.0)** — tazama faili [LICENSE](../../LICENSE) kwa maelezo zaidi.
