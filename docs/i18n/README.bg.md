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
| **Вграден VLC медиа плейър** | Лека и автономна аудио програма с автоматична инсталация на преносим VLC и гладко управление на силата на гласа | 🟢 Имплементиран |
| **Многопоточен локален сканер** | Рекурсивно и бързо откриване на локални аудио файлове (MP3, FLAC, AAC, OGG...) | 🟢 Имплементиран |
| **Извличане на метаданни** | Четене/записване на ID3, Vorbis Comments и изчисляване на аудио отпечатък (`mutagen`) | 🟢 Имплементиран |
| **Поддръжка на плейлисти (M3U, PLS, XSPF, WPL) & CUE файлове** | Дърбовидна индексация (🎶), последователен ред на слушане, визуално идентифициране на липсващи части; файловете .cue (💿) се отварят като директория с виртуални части с тяхната продължителност и се възпроизвеждат като истински части | 🟢 Имплементиран |
| **Мениджър на плейлисти и Претегляне/Пускане** | Виртуална опашка, гладко drag & drop, обратимо случайно (shuffle) и цикли | 🟢 Имплементиран |
| **Интерактивен режим „🎲 Слепи тест“** | Имативна музикална игра с анимационен брой, звуково затихване, меко разкриване и автоматично свързване | 🟢 Имплементиран |
| **Актуалнизации в приложението** | Автоматична/ръчна проверка на версиите чрез GitHub Releases | 🟢 Внедрено |
| **Управление на изтори и дискография** | Специална папка по изтори с албуми, сингли и пълна дискография | 🟡 Планирано |
| **Графичен еквалайзер (EQ)** | Аудио пресетс и параметричен мултибанд еквалайзер | 🟡 Планирано |
| **Connecteur Google Drive** | Сканиране и синхронизиране на отдалечени аудио колекции чрез OAuth 2.0 | ⚪ Планирано |
| **Connecteur Amazon Music** | Сканиране и синхронизиране на отдалечени колекции чрез OAuth 2.0 | ⚪ Планирано |
| **Connecteur Spotify / Deezer** | Импортиране на плейлисти и съпоставяне на пръчки | ⚪ Планирано |
| **Интелигентно дедуплиране** | Обнаружение на дубликати (заглавие/източник + акустични отпечатъци) | ⚪ Планирано |

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
