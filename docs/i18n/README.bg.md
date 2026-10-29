# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <b>Български</b> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) е модерен, реактивен и кросплатформен аудио плейър за десктоп (Windows, Linux, macOS). Създаден да предложи на аудиофилите пълен контрол върху локалната им музикална библиотека (MP3, FLAC, OGG…), той вече поддържа плейлисти (M3U, PLS, XSPF, WPL), CUE файлове (албуми от един файл, разделени на пръчки) и интегрира напълно нов режим „слеп аудио тест“! Проектът се развива, за да стане унифициран контролен център, способен да организира, дедупликира и синхронизира хибридни музикални колекции, разпределени между локални дискове, облачно съхранение (Google Drive) и стрийминг услуги (Spotify, Deezer, Amazon Music).

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

## 📌 Функционалности & Статус на проекта

| Функционалност | Описание | Статус |
| :--- | :---: | :---: |
| **Аудио възпроиздоjavъчен двигател** | Лека и автономна аудио програма (VLC portable, автоматично инсталиран под Windows). Две опции за двигател: директен изход VLC или буферизиран двигател за плавен преход между две пръстни (Gapless 0 ms, плавен преход с еднаква мощност, без прекъсване на аудио изхода) | 🟢 Внедрен |
| **Управление на библиотеката** | Рекурсивно многопоточно сканиране на локални директории (MP3, FLAC, AAC, OGG...), ръчна, планирана или в реално време синхронизация, кошница и статистика на библиотеката | 🟢 Внедрен |
| **Извличане на метаданни** | Четене/запис на ID3, Vorbis Comments и изчисляване на аудио отпечатък (`mutagen`) | 🟢 Внедрен |
| **Поддръжка на плейлисти (M3U, PLS, XSPF, WPL) и CUE листа** | Дърбовидна индексация (🎶), последователен ред на слушане, визуално откриване на липсващи части; файловете `.cue` (💿) се отварят като директория с виртуални пръстни с тяхната продължителност и се възпроизвеждат като истински пръстни | 🟢 Внедрен |
| **Мениджър на плейлисти и Drag & Drop** | Виртуализиран списък с очакване, плавен drag & drop, обръщащ се случаен ред (shuffle) и цикли | 🟢 Внедрен |
| **Интерактивен режим „🎲 Blind Test“** | Иммерсивен музикален тест с анимиран броиш, звуков преход, нежна разкритие и автоматично свързване | 🟢 Внедрен |
| **Актуалнизации в приложението** | Автоматична/ръчна проверка на версиите чрез GitHub Releases | 🟢 Внедрено |
| **Версии за Linux и macOS** | Пакети .AppImage / .tar.gz (Linux) и не подписан .dmg (macOS), изисква се VLC | 🟡 Експериментално (не тествано) |
| **Управление на изкустители и дискография** | Специална гледка по изкустител с албуми, сингли и пълна дискография | 🟡 Планирано |
| **Графичен еквалайзер (EQ)** | Аудио пресетс и параметричен мултибанд еквалайзер | 🟡 Планирано |
| **Конектор Google Drive** | Сканиране и синхронизиране на отдалечени аудио колекции чрез OAuth 2.0 | ⚪ Планирано |
| **Конектор Amazon Music** | Сканиране и синхронизиране на отдалечени колекции чрез OAuth 2.0 | ⚪ Планирано |
| **Конектор Spotify / Deezer** | Импортиране на плейлисти и съпоставяне на пръчки | ⚪ Планирано |
| **Интелигентно дедуплиране** | Обнаружение на дубликати (заглавие/изкустител + акустични отпечатъци) | ⚪ Планирано |

> 💡 *За да видите подробностите по етапите и планираните версии, реферетирайте се към [Дорожна карта (Roadmap)](../../ROADMAP.md).*

---

## 📌 Налични езици

Английски, Френски, Испански, Германски, Италиански, Португалски, Японски, Руски, Полски, Турски, Нидерландски, Шведски, Индонезийски, Български, Сръбски, Беларуски, Гръцки, Каталански, Баскски, Галисийски, Чешки, Словашки, Унгарски, Хърватски, Словешки, Босански, Естонски, Латвийски, Литовски, Норвежки, Дънски, Фински, Исландски, Малайски, Тагалог, Свахили, Есперански, Китайски (упростени), Китайски (традиционни), Корейски, Арабски, Еврейски, Виетнамски

---

## 🚀 Бързо започване

### Предварителни изисквания

- **Python 3.11** или по-висока версия инсталирана
- Git

### Инсталация

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

## 🐧🍎 Linux и macOS : експериментални версии (нетествани)

Пакетните файлове за Linux (`.AppImage` / `.tar.gz`) и macOS (`.dmg`) са предоставени **без да са тествани**: AMSO е валидиран само под Windows. Аудио двигателя с непрекъснат буфер (`buffer`) в частност не е проверен на тези системи. Вашето мнение е ценно.

- **VLC е необходим** (AMSO го изтегля само под Windows):
  - Linux : `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) или `sudo pacman -S vlc` (Arch).
  - macOS : инсталирайте **VLC.app** от [videolan.org](https://www.videolan.org/vlc/) в папката Applications.
- **Linux, системни библиотеки** : интерфейсът Qt изисква, в между другото, `libpulse0` (звук), `libxcb-cursor0` и `libxkbcommon-x11-0` (например `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, не подписан `.dmg`** : при първото стартиране, кликнете с десен бутон върху AMSO и след това **Отворете**, или изпълнете `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage** : направете го изпълним с `chmod +x AMSO*.AppImage`.
- **В случай на проблем**, моля изпратете файловете `startup.log` и `crash.log` (ако съществуват), намиращи се в директорията за данни: `~/Library/Application Support/AMSO/` под macOS, `~/.local/share/AMSO/` под Linux. Уточнете вашата система и версия на VLC.

---

## 🧪 Стартиране на тестовете

Проектът използва `pytest` с набор от модулни и интеграционни тестове:

```bash
pytest -v
```

Тестовете се изпълняват автоматично на **Windows, macOS и Ubuntu** при всеки push чрез GitHub Actions.

---

## 🔒 Сигурност и API Ключове

- **Никога не коммитвайте реални API ключове или токени за автентикация.**
- Файлът `.gitignore` е предварително конфигуриран да блокира `.env`, `credentials.json`, `token.json` и всички локални SQLite бази данни.
- Използвайте `.env.example` като шаблон за вашата среда за разработка.

---

## 📋 Документация & Проследяване на проекта

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Подробен журнал на версиите, нови функции и корекции на грешки.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Карта на бъдещи етапи (Изкустители, Cloud, Spotify, Дедупликация).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Хартия за софтуерна архитектура и правила за качество на кода.

---

## 💖 Подкрепа на проекта & Дистрибуция

AMSO е безплатен и свободен софтуер (open source). Ако харесвате приложението и искате да подкрепите развитието му:

- 🎮 **Изтегляне & Плати каквото искаш :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (прекомпилируем изпълним файл, готов за употреба)
- ☕ **Директно донориране :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Спонсори :** [Спонсорирайте LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Лиценз

Този проект е под лиценз **GNU General Public License v3.0 (GPL-3.0)** — вижте файла [LICENSE](../../LICENSE) за повече подробности.
