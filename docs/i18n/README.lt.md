# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <b>Lietuvių</b> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) yra modernus, atkrečiamas ir daugialapertinis stališkas audio pleitinas (Windows, Linux, macOS). Dizgintas, kad audiolūšiams būtų suteiktas visiškas kontrolis savo lokalioji muzikos bibliotekai (MP3, FLAC, OGG…), jis dabar palaiko lentelelių sąrašus (M3U, PLS, XSPF, WPL), CUE lapelius (albumai viename failiame, išdaliniai į stacionijas) ir įtraukia visiškai naują „slėpiamojoji bandos“ audio režimą! Projektas tobulėja, kad taptų vienizuodžiu komandavimo centru, galinčiu organizuoti, pašalinti duplikacijas ir sinchronizuoti hibridines muzikos kolekcijas, išdalinatas tarp lokalioji diskų, judesioji skaitmeninė saugojimas (Google Drive) ir sraunuojimo paslaugos (Spotify, Deezer, Amazon Music).

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

## 📌 Funkcijos & Statusas projekto

| Funkcija | Aprašymas | Statusas |
| :--- | :---: | :---: |
| **Įmontuotas VLC įrašo variklis** | Lekštas ausinio failų, autonomiškai su VLC portanti įraktais ir lengva garumas valdymas | 🟢 Įgyvendintas |
| **Lokalusis multi-treudinė skanasuotojas** | Rekursyvinė ir greita lokalų ausinio failų paieška (MP3, FLAC, AAC, OGG...) | 🟢 Įgyvendintas |
| **Metaduomenų ištraukimas** | ID3, Vorbis Comments skaitymas/rašymas ir ausinio įspėjos skaičiavimas (`mutagen`) | 🟢 Įgyvendintas |
| **Pagalbos failams (M3U, PLS, XSPF, WPL) ir CUE lapams palaikymas** | Medžiaginė indeksavimas (🎶), sekvencinis klausymasis, vizualus praradusių dalų pažymėjimas; `.cue` failai (💿) atsidaro kaip virtualus stulpelių katalogas su jų trumpe ir skaito kaip tikri stulpeliai | 🟢 Įgyvendintas |
| **Pagalbos failų valdytojas ir įtraukti/ištraukti** | Virtualus eilė, lengvas įtraukti/ištraukti, atgal atkuriamas atsitiktinis (shuffle) ir ciklai | 🟢 Įgyvendintas |
| **Interaktyvus „🎲 Blind Test“ režimas** | Immersyvus muzikos žaidimas su animaciniu laikmeniu, garso išblėjimais, subtili atskleidimas ir automatinis išsaugavimas | 🟢 Įgyvendintas |
| **Atnaujinimai į programoje** | Automatinis/manuális versijų patikrinimas per GitHub Releases | 🟢 Įgyvendintas |
| **Menėjų valdymas ir diskografija** | Išskirtinė peržiūra pagal menėją su albumais, singliais ir pilna diskografija | 🟡 Planuojama |
| **Grafinis ekvalizatorius (EQ)** | Audio išankstiniai nustatymai ir parametrinis daugiaspadžius ekvalizatorius | 🟡 Planuojama |
| **Google Drive jungties įranga** | Skaitmeninių audio kolekcijų skenavimas ir sinchronizavimas per OAuth 2.0 | ⚪ Planuojama |
| **Amazon Music jungties įranga** | Skaitmeninių kolekcijų skenavimas ir sinchronizavimas per OAuth 2.0 | ⚪ Planuojama |
| **Spotify / Deezer jungties įranga** | Playlistų importavimas ir strogų atitikimas | ⚪ Planuojama |
| **Išmanus dublikatų pašalinimas** | Dublikatų aptikimas (pašvirškūs pavadinimai/menėjai + akustiniai atspvarai) | ⚪ Planuojama |

> 💡 *Norėdami peržiūrėti planuojamų etapų ir versijų detales, patyrėkite į [Feuille de route (Roadmap)](../../ROADMAP.md).*

---

## 📌 Teikiamos kalbos

Anglų, Prancūziškai, Ispanija, Vokališkai, Italija, Portugališkai, Japonų, Rusų, Polonija, Turkų, Neterlandičiu, Švedų, Indoneziški, Bulgariškai, Serbija, Baltarusijos, Grekaiškai, Katalonija, Baskų, Galicijškai, Češių, Slovakija, Ungariškai, Kroatiškai, Slovėnija, Bosnija, Estonija, Latviškai, Lietuviškai, Norvegų, Danija, Finlandijos, Islandų, Malajų, Tagalogų, Swahili, Esperanto, Kinotaisyklė, Kinotradicinė, Korėanų, Arabija, Hebrajų, Vietnamų

---

## 🚀 Greitas pradžia

### Reikalavimai

- **Python 3.11** arba aukštesnis įdiegtas
- Git

### Instaliacija

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

## 🧪 Testų paleidimas

Projektas naudoja `pytest` su vieneto ir integracijos testų rinkiniu:

```bash
pytest -v
```

Testai vyksta automatiškai **Windows, macOS ir Ubuntu** kiekviename push'e per GitHub Actions.

---

## 🔒 Saugumas ir API raktai

- **Niekada neįkelkite realių API raktų ar autentifikacijos tokenių.**
- Failas `.gitignore` yra išankst}}}, konfigūruotas, kad blokuotų `.env`, `credentials.json`, `token.json` ir visus vietinius SQLite duomenų bazes.
- Naudokite `.env.example` kaip šabloną savo plėtros aplinkai.

---

## 📋 Dokumentacija & Projekto stebėjimas

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Detalių versijų, naujų funkcijų ir klaidos korekcijų žurnalas.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Žymėlapis ateities etapams (Menininkai, Skločius, Spotify, Dublionų pašalinimas).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Programinės įrangos architektūros charta ir kodavimo kokybės taisyklės.

---

## 💖 Patikti projektą ir Plėtra

AMSO yra nemokamas ir laisvių kodų programinė įranga (open source). Jei jums patinka ši programa ir norite padėti palaikti jos vystymą:

- 🎮 **Keičiantis & Pay What You Want :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (pasirengęs, išankstiai sukompuotavęs)
- ☕ **Atlikti tiesioginį dovanojimą :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [Patikiuoti LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licencija

Šis projektas yra pagal licenciją **GNU General Public License v3.0 (GPL-3.0)** — patikrinkite failą [LICENSE](../../LICENSE) daugiau detalių.
