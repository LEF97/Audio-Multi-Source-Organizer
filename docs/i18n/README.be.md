# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <b>Беларуская</b> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) — гэта сучасны, рэактыўны і кросплатформенны аўдыёплеер для настольных камп'يوтараў (Windows, Linux, macOS). Сpectralізаваны для прадастаўлення аўдыёфілам поўнага кантролю над іх мясцовай музычнай бібліятэкай (MP3, FLAC, OGG…), ён цяпер падтрымлівае плейлісты (M3U, PLS, XSPF, WPL), CUE-файлы (альбамы ад аднаго файла, падзяленыя на трекі) і ўключае новы рэжым аўдыё-тэста без паطلعэння! Падпраект развіваецца ў кураторынты, які зможа арганізаваць, выяўляць дублікаты і синхронізаваць гібрыдныя музычныя кампазіцыі, распластаўленыя паміж мясцовымі дыскамі, хмарным астоўкам (Google Drive) і стрымінгавымі паслугамі (Spotify, Deezer, Amazon Music).

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

## 📌 Функцыянальнасці & Статус праекта

| Функцыянал | Апісан | Статус |
| :--- | :---: | :---: |
| **Мадыль праслухоўкі аўдыё** | Легка і самастойнае аўдыё-праслухоўванне (VLC portable аўтаматычна ўсталяваны ў Windows). Две мадылі на выбар: непасрэдны выхад VLC або мадыль з пастаянным буферым рэзкам для плаўнага пераходу паміж двума трекамі (Gapless 0 ms, змякчэнне пераходу на роўнамагутным узроўні, без перапынку аўдыёвыхаду) | 🟢 Implémenté |
| **Кантроль бібліятэкі** | Рэкурсіўны мульатрадны скан мясцовых каталогаў (MP3, FLAC, AAC, OGG...), ручная, распярэджаная або ў рэальным часе синхронізацыя, кошык і статыстыка бібліятэкі | 🟢 Implémenté |
| **Аócганіванне метададзеных** | Чытанне/запісанне ID3, Vorbis Comments і вылічэнне аўдыё-адчатку (`mutagen`) | 🟢 Implémenté |
| **Падтрымка плейлістаў (M3U, PLS, XSPF, WPL) і CUE-парадкаў** | Дрэвавая індексіраванне (🎶), паслядоўны парадак праслухоўкі, візуальнае выяўленне адсутных трекаў; файлы `.cue` (💿) адкрываюцца як каталог віртуальных трекаў з іх працягласцю і праходзяць, як сапраўдныя трекі | 🟢 Implémenté |
| **Кантролер плейлістаў і перацягванне-адпусканне** | Віртуальны спіс чакання, плаўнае drag & drop, адпісавальны (shuffle) і цыклі | 🟢 Implémenté |
| **Рэжым « 🎲 Blind Test » з інтэрактывам** | Імертыўная музыкальная гульня з анімаваным лічэннем, аўдыё-змякчэннем, мяккай адкрывальніцай і аўтаматычным пераходам | 🟢 Implémenté |
| **Абнаўленні ў прыватным рэжыме** | Аўтаматычная/ручная праверка версій праз GitHub Releases | 🟢 Упрэдраджвалена |
| **Версіі Linux і macOS** | Пакеты `.AppImage` / `.tar.gz` (Linux) і не падпісаваны `.dmg` (macOS), патрабуецца VLC | 🟡 Экспериментальна (не праверана) |
| **Кіраванне артыстамі і Дыскопаграфія** | Выкหลядная воедка па артыстах з альбомамі, சிங்களгітамі і поўнай дыскопаграфіяй | 🟡 Па планаванні |
| **Графічны эквалайзер (EQ)** | Аудыя-прадэкты і парамэтрычны манітыўны эквалайзер | 🟡 Па планаванні |
| **КаннеКТар Google Drive** | Сканванне і синхронізацыя аддальных аўдыя-калекцый праз OAuth 2.0 | ⚪ Запланавана |
| **КаннеКТар Amazon Music** | Сканванне і синхронізацыя аддальных калекцый праз OAuth 2.0 | ⚪ Запланавана |
| **КаннеКТар Spotify / Deezer** | Імпарт плейлістаў і адпаведнасць трекаў | ⚪ Запланавана |
| **Разумная адпавіна** | Выяўленне дублікатаў (загаловак/артыст + акустычныя адметкі) | ⚪ Запланавана |

> 💡 *Каб паглядзець падрабязнасці этапаў і прагледжаных версій, перайдзіце па [Карта маршруту (Roadmap)](../../ROADMAP.md).*

---

## 📌 Даступныя мовы

Англійская, Французская, Іспанская, Нэмецкая, Італьянская, Португальская, Японская, Руская, Польская, Турская, Нидэрландская, Шведская, Індонезійская, Болгарская, Сьёрбская, Беларуская, Грээка, Каталонская, Баскская, Галіцыйская, Чакаўская, Словацкая, Венгерская, Хорватская, Слаўвенская, Босняцкая, Эстэўская, Латвіяская, Літоўская, Норвежская, Данская, Фінляндская, Ісландская, Малайская, Тагалонгская, Свахілі, Эсперян, Кітайская (арыграфічны), Кітайская (традыцыйны), Карэйская, Арарабская, Іўдэўская, Вьетнамская

---

## 🚀 Швидкі старт

### Папярэднія патрабаванні

- **Python 3.11** або больш новы ўсталяваны
- Git

### Устаноўка

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

## 🐧🍎 Linux і macOS: eksperymentalныя версіі (не тэставаныя)

Пакетаў Linux (`.AppImage` / `.tar.gz`) і macOS (`.dmg`) прадстаўлены **без тэставання**: AMSO быў правераны толькі пад Windows. Аўдыё-мадылятар з пастаянным буферым (`buffer`) рэжымам, асабліва, не быў правераны на гэтых сістэмах. Ваша паведамленне каштоўна.

- **VLC патрабуецца** (AMSO спампаваць можа толькі пад Windows) :
  - Linux : `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) або `sudo pacman -S vlc` (Arch).
  - macOS : усталяваць **VLC.app** з [videolan.org](https://www.videolan.org/vlc/) у каталогі Applications.
- **Linux, сістэмныя бібліятэкі** : інтэрфейс Qt патрабуе, у тым ліку `libpulse0` (гук), `libxcb-cursor0` і `libxkbcommon-x11-0` (напрыклад `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, `.dmg` не падпісаваны** : пры першым запуску, правесці правы клік на AMSO, а потым **Адкрыць**, або выканаць `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage** : змяніць яго на выканальны з `chmod +x AMSO*.AppImage`.
- **У выпадку праблем**, калі ласка, адпраўце файлы `startup.log` і `crash.log` (калі існуюць), знаходзячыся ў каталогу дадзеных: `~/Library/Application Support/AMSO/` пад macOS, `~/.local/share/AMSO/` пад Linux. Укажыце свой сістэм і версію VLC.

---

## 🧪 Запуск тэставання

Падпраект выкарыстоўвае `pytest` з пакетам тэставання адзінкаў і інтэграцыі:

```bash
pytest -v
```

Тэсты праходзяць аўтаматычна на **Windows, macOS і Ubuntu** па кожным пуша праз GitHub Actions.

---

## 🔒 Безпека & Ключы API

- **Ніколі не каміцце сапраўдныя ключы API і токены аўтэнтыфікацыі.**
- Файл `.gitignore` папярэдні канфігураваны для блёкавання `.env`, `credentials.json`, `token.json` і ўсіх мясцовых баз дадзеных SQLite.
- Выкарыстоўвайце `.env.example` як шэму для вашага асяроддзя развіцця.

---

## 📋 Дакументацыя & Адлік праекта

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Падрабяжны журнал версій, новыя функцыянальнасці і выпраўленні памылак.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Карта маршруту будучых этапаў (Artistes, Cloud, Spotify, Дэдубліванне).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Хартия лаясі архітэктуры праграмнага забеспячэння і правілы якасці кода.

---

## 💖 Падтрымка праекта & Распыленне

AMSO з'яўляецца вольным і бясплатным праграмным забеспячэннем (open source). Калі вам спадабаецца праграма і вы хацелі падтрымаць яе распрацоўку:

- 🎮 **Загрузка & Аплаці па воўным:** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (прыгажоўны, спакампаляваны, гатовы для выкарыстання)
- ☕ **Зрабіць непасрэдны донацый:** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **Спонсары GitHub:** [Спонсаваць LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Ліцэнзія

Гэты праект пад ліцэнцыяй **GNU General Public License v3.0 (GPL-3.0)** — праглядзіце файл [LICENSE](../../LICENSE) для больш па세більных дэталяў.
