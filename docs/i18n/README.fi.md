# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <b>Suomi</b> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) on moderni, reaktiivinen ja monialustainen pöytäkotelo äänisoitin (Windows, Linux, macOS). Se on suunniteltu tarjoamaan audiophileille täydellinen hallinta paikallisessa musiikkikirjastossa (MP3, FLAC, OGG…), ja se tukee nyt soittolistoja (M3U, PLS, XSPF, WPL), CUE-tiedostoja (yksi tiedosto, jaettu kappaleiksi) ja sisällyttää täysin uuden äänitestitilan (blind test)! Projekti kehittyy yhtenäiseksi komentokeskukseksi, joka pystyy järjestämään, poistamaan duplikaatit ja synkronoimaan hybridejä musiikkikokoelmia, jotka on hajautettu paikallisille levyille, pilvipalveluille (Google Drive) ja suoratoistopalveluille (Spotify, Deezer, Amazon Music).

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

## 📌 Ominaisuudet ja projektin tila

| Toiminto | Kuvaus | Tila |
| :--- | :---: | :---: |
| **Integroitu VLC-soittimo** | Kevyt ja itsenäinen äänisoitin, jossa on VLC portable -autoinstallaatio ja sujuva äänenvoimakkuuden hallinta | 🟢 Toteutettu |
| **Multithreadinen paikallinen skanneri** | Rekursiivinen ja nopea paikallisten äänitiedostojen löytäminen (MP3, FLAC, AAC, OGG...) | 🟢 Toteutettu |
| **Metatietojen poiminta** | ID3- ja Vorbis Comments -lukeminen/kirjoittaminen sekä äänijalanjäljen laskeminen (`mutagen`) | 🟢 Toteutettu |
| **Soittolistan tuki (M3U, PLS, XSPF, WPL) & CUE-tiedostot** | Puurakenteinen indeksointi (🎶), sarjallinen kuuntelujärjestys, puuttuvien kappaleiden visuaalinen paikannus; .cue-tiedostot (💿) avautuvat kuin virtuaalinen kappalelista, jonka kesto näkyy ja joka toistuu kuin oikea kappale | 🟢 Toteutettu |
| **Soittolistan hallinta & Vedä-Irrotta** | Virtualisoitu jonotus, sujuva vedä-irrotta, käänteinen satunnaistaminen (shuffle) ja silmukoinnit | 🟢 Toteutettu |
| **Interaktiivinen "🎲 Blind Test" -tila** | Immersiivinen musiikkipeli animoidulla laskurilla, äänivaaimella, pehmeällä paljastuksella ja automaattisella jatkumisella | 🟢 Toteutettu |
| **Sovelluksen sisäiset päivitykset** | Versioiden automaattinen/manuaalinen tarkistus GitHub Releasesin kautta | 🟢 Toteutettu |
| **Artistien ja diskografian hallinta** | Omatoitettu näkymä artistikohtaisesti albumeilla, singleillä ja koko diskografialla | 🟡 Suunniteltu |
| **Graafinen ekvalisaattori (EQ)** | Äänialustukset ja parametrisen monikaista-ekvalisaattori | 🟡 Suunniteltu |
| **Google Drive -liitin** | Skannaus ja synkronointi etäpaikkojen äänikokoelmien kanssa OAuth 2.0:n kautta | ⚪ Suunniteltu |
| **Amazon Music -liitin** | Skannaus ja synkronointi etäpaikkojen kokoelmien kanssa OAuth 2.0:n kautta | ⚪ Suunniteltu |
| **Spotify / Deezer -liitin** | Soittolistojen tuonti ja kappaleiden vastaavuus | ⚪ Suunniteltu |
| **Älykäs duplikaattien poisto** | Duplikaattien tunnistus (epäselvä otsikko/artisti + akustiset jälkennäytökset) | ⚪ Suunniteltu |

> 💡 *Suunnitellut virstanpylväät ja versiot löytyvät tarkemmin [Feuille de route (Roadmap)](../../ROADMAP.md).*

---

## 📌 Saatavilla olevat kielet

Englanti, Ranska, Espanja, Saksa, Italia, Portugali, Japani, Venäjä, Puola, Turkki, Alankomaat, Ruotsi, Indonesia, Bulgari, Serbia, Valko-Venäjä, Kreikka, Katalonia, Baskia, Galisia, Tšekki, Slovakia, Unkari, Kroatia, Sloveni, Bosnia, Eesti, Latvia, Liettua, Norja, Tanska, Suomi, Islanti, Malesia, Tagalog, Swahili, Esperanto, Kiina (yksinkertaistettu), Kiina (perinteinen), Korea, Arabia, Heprea, Vietnam

---

## 🚀 Nopea käynnistys

### Edellytykset

- **Python 3.11** tai uudempi asennettu
- Git

### Asennus

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

## 🧪 Testien käynnistys

Projekti käyttää `pytest` yksikkö- ja integraatiotestejä sisältävällä testisarjalla:

```bash
pytest -v
```

Testit suoritetaan automaattisesti **Windows, macOS ja Ubuntu** -käyttöjärjestelmillä jokaisella pushilla GitHub Actionsin kautta.

---

## 🔒 Turvallisuus & API-avaimet

- **Älä koskaan commitata oikeita API-avaimia tai tunnistautumistunnuksia.**
- Tiedosto `.gitignore` on esitäytetty estämään `.env`, `credentials.json`, `token.json` ja kaikki paikalliset SQLite-tietokannat.
- Käytä `.env.example` mallina kehitysympäristöä varten.

---

## 📋 Dokumentaatio & Projektin seuranta

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Yksityiskohtainen loki versioista, uusista ominaisuuksista ja bugikorjauksista.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Kartta tuleville maaleille (Taiteilijat, Cloud, Spotify, Duplikaattien poisto).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Ohjelmistoarkkitehtuurin ja koodin laatuohjeistus ja säännöt.

---

## 💖 Tukea projektia & Jakelu

AMSO on vapaa ja ilmainen ohjelmisto (open source). Jos pidät sovelluksesta ja haluat tukea sen kehitystä:

- 🎮 **Lataus & Pay What You Want :** [AMSO:n Itch.io-sivu](https://lef97.itch.io/audio-multi-source-organizer) (Ennaltaäänteistetty, valmis käyttöön oleva suoritettava tiedosto)
- ☕ **Suora lahjoitus :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsorit :** [Sponsoroi LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Lisenssi

Tämä projekti on lisenssin alla **GNU General Public License v3.0 (GPL-3.0)** — katso tiedosto [LICENSE](../../LICENSE) saadaksesi lisätietoja.
