# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <b>Русский</b> • <a href="README.ar.md">العربية</a>
</p>
<details>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) — это современный, отзывчивый и кроссплатформенный настольный аудиопроигрыватель (Windows, Linux, macOS). Созданный для того, чтобы предоставить аудиофилам полный контроль над их локальной музыкальной библиотекой (MP3, FLAC, OGG…), он теперь поддерживает плейлисты (M3U, PLS, XSPF, WPL), файлы CUE (альбомы в одном файле, разделенные на треки) и включает совершенно новый режим аудио-тестирования вслепую (blind test)! Проект развивается, чтобы стать унифицированным центром управления, способным организовывать, устранять дубликаты и синхронизировать гибридные музыкальные коллекции, распределенные между локальными дисками, облачным хранилищем (Google Drive) и стриминговыми сервисами (Spotify, Deezer, Amazon Music).

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

## 📌 Функционал и статус проекта

| Функционал | Описание | Статус |
| :--- | :--- | :---: |
| **Аудиоплеер** | Легкий автономный аудиоплеер (VLC portable автоматически установлен под Windows). Два движка на выбор: прямая выход VLC или непрерывный буферный движок для плавного переключения между треками (Gapless 0 ms, плавное затухание с равной мощностью, без обрыва аудиовыхода) | 🟢 Реализовано |
| **Управление библиотекой** | Многопоточный рекурсивный сканирование локальных папок (MP3, FLAC, AAC, OGG...), ручная, запланированная или в реальном времени синхронизация, корзина и статистика библиотеки | 🟢 Реализовано |
| **Извлечение метаданных** | Чтение/запись ID3, Vorbis Comments и расчет аудиоотпечатка (`mutagen`) | 🟢 Реализовано |
| **Поддержка плейлистов (M3U, PLS, XSPF, WPL) и файлов CUE** | Древовидная индексация (🎶), последовательный порядок прослушивания, визуальное указание отсутствующих треков; файлы `.cue` (💿) открываются как папка виртуальных треков с их длительностью и воспроизводятся как настоящие треки | 🟢 Реализовано |
| **Менеджер плейлистов и перетаскивание** | Виртуальная очередь, плавное перетаскивание (drag & drop), обратный порядок (shuffle) и циклы | 🟢 Реализовано |
| **Интерактивный режим « 🎲 Blind Test »** | Иммерсивная музыкальная игра с анимационным отсчетом, звуковым затуханием, мягким раскрытием и автоматическим переключением | 🟢 Реализовано |
| **Обновления в приложении** | Автоматическая/ручная проверка версий через GitHub Releases | 🟢 Реализовано |
| **Версии для Linux и macOS** | Пакеты `.AppImage` / `.tar.gz` (Linux) и не подписанный `.dmg` (macOS), требуется VLC | 🟡 Экспериментально (не протестировано) |
| **Управление артистами и дискографией** | Специальный просмотр по артисту с альбомами, синглами и полной дискографией | 🟡 Планируется |
| **Графический эквалайзер (EQ)** | Аудиопресеты и параметрический многополосный эквалайзер | 🟡 Планируется |
| **Коннектор Google Drive** | Сканирование и синхронизация удаленных аудиоколлекций через OAuth 2.0 | ⚪ Запланировано |
| **Коннектор Amazon Music** | Сканирование и синхронизация удаленных коллекций через OAuth 2.0 | ⚪ Запланировано |
| **Коннектор Spotify / Deezer** | Импорт плейлистов и сопоставление треков | ⚪ Запланировано |
| **Интеллектуальное удаление дубликатов** | Обнаружение дубликатов (размытые название/артист + акустические отпечатки) | ⚪ Запланировано |

> 💡 *Чтобы ознакомиться с деталями запланированных этапов и версий, обратитесь к [Feuille de route (Roadmap)](../../ROADMAP.md).*

---

## 📌 Доступные языки

Английский, Французский, Испанский, Немецкий, Итальянский, Португальский, Японский, Русский, Польский, Турецкий, Нидерландский, Шведский, Индонезийский, Болгарский, Сербский, Белорусский, Греческий, Каталанский, Баскский, Галисийский, Чешский, Словацкий, Венгерский, Хорватский, Словенский, Боснийский, Эстонский, Латвийский, Литовский, Норвежский, Датский, Финский, Исландский, Малайский, Тагальский, Суахили, Эсперанто, Китайский (упрощенный), Китайский (традиционный), Корейский, Арабский, Еврейский, Вьетнамский

---

## 🚀 Быстрый старт

### Предварительные требования

- Установлен **Python 3.11** или выше
- Git

### Установка

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

## 🐧🍎 Linux и macOS: экспериментальные версии (не протестированы)

Пакеты Linux (`.AppImage` / `.tar.gz`) и macOS (`.dmg`) предоставляются **без тестирования**: AMSO был проверен только под Windows. Аудиодвижок с непрерывным буфером (`buffer`), в частности, не был проверен на этих системах. Ваш отзыв очень ценен.

- **Требуется VLC** (AMSO загружает его только под Windows):
  - Linux: `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) или `sudo pacman -S vlc` (Arch).
  - macOS: установить **VLC.app** из [videolan.org](https://www.videolan.org/vlc/) в папку Applications.
- **Linux, системные библиотеки**: интерфейс Qt требует, в частности, `libpulse0` (звук), `libxcb-cursor0` и `libxkbcommon-x11-0` (например, `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, не подписанный `.dmg`**: при первом запуске щелкните правой кнопкой мыши по AMSO и выберите **Открыть** или выполните `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage**: сделайте его исполняемым с помощью `chmod +x AMSO*.AppImage`.
- **В случае проблем**, пожалуйста, отправьте файлы `startup.log` и `crash.log` (если они существуют), расположенные в папке данных: `~/Library/Application Support/AMSO/` под macOS, `~/.local/share/AMSO/` под Linux. Укажите вашу систему и версию VLC.

---

## 🧪 Запуск тестов

Проект использует `pytest` с набором модульных и интеграционных тестов:

```bash
pytest -v
```

Тесты автоматически запускаются на **Windows, macOS и Ubuntu** при каждом пуше через GitHub Actions.

---

## 🔒 Безопасность & Ключи API

- **Никогда не коммитьте реальные ключи API или токены аутентификации.**
- Файл `.gitignore` предварительно настроен для блокировки `.env`, `credentials.json`, `token.json` и всех локальных баз данных SQLite.
- Используйте `.env.example` в качестве шаблона для вашей среды разработки.

---

## 📋 Документация и Отслеживание проекта

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Подробный журнал версий, новых функций и исправлений ошибок.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Дорожная карта будущих этапов (Артисты, Облако, Spotify, Дедупликация).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Хартия архитектуры программного обеспечения и правила качества кода.

---

## 💖 Поддержать проект & Дистрибуция

AMSO это бесплатное и свободное программное обеспечение (open source). Если вам нравится приложение и вы хотите поддержать его разработку:

- 🎮 **Скачивание и Pay What You Want :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (предварительно скомпилированный исполняемый файл, готовый к использованию)
- ☕ **Прямое пожертвование :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [Спонсировать LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Лицензия

Этот проект находится под лицензией **GNU General Public License v3.0 (GPL-3.0)** — ознакомьтесь с файлом [LICENSE](../../LICENSE) для получения более подробной информации.
