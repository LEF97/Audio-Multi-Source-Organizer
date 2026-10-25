# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <b>עברית</b> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) הוא נגן אודיו שולחני מודרני, מגיב ורב-פלטפורמה (Windows, Linux, macOS). שתוכנן להעניק לאודיופילים שליטה מוחלטת בספריית המוזיקה המקומית שלהם (MP3, FLAC, OGG...), הוא תומך כעת ברשימות השמעה (M3U, PLS, XSPF, WPL), דפי CUE (אלבומים מקובצים בקובץ אחד ומפורקים למסלולים), ומשלב מצב בדיקה עיוורת (blind test) חדש לחלוטין לאודיו! הפרויקט מתפתח להפוך למרכז בקרה מאוחד המסוגל לארגן, להסיר כפילויות ולסנכרן אוספי מוזיקה היברידיות המפוזרות בין כוננים מקומיים, אחסון ענן (Google Drive), ושירותי סטרימינג (Spotify, Deezer, Amazon Music).

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

## 📌 תכונות & סטטוס הפרויקט

| תכונה | תיאור | סטטוס |
| :--- | :---: | :---: |
| **מנוע נגן VLC משולב** | נגן אודיו קל ועצמאי עם התקנה אוטומטית של VLC נייד וניהול תצורה חלק של הווליום | 🟢 מיושם |
| **סורק מקומי מרובה-משול threads** | גילוי רקורסיבי ומהיר של קבצי אודיו מקומיים (MP3, FLAC, AAC, OGG...) | 🟢 מיושם |
| **חילוץ מטא-דאטה** | קריאה/כתיבה של ID3, Vorbis Comments וחישוב טביעת אצבע אודיו (`mutagen`) | 🟢 מיושם |
| **תמיכה ברשימות השמעה (M3U, PLS, XSPF, WPL) ודפי CUE** | אינדקס עצי (🎶), סדר האזנה סדרתי, איתור ויזואלי של קטעים חסרים; קבצי `.cue` (💿) נפתחים כתיקייה של מסלולים וירטואליים עם משך הזמן שלהם ומושמעים כמסלולים אמיתיים | 🟢 מיושם |
| **מנהל רשימת השמעה וגרירה-שחרור** | תור המתנה וירטואלי, גרירה ושחרור חלק, אקראי (shuffle) הפיך ולולאות | 🟢 מיושם |
| **מצב "🎲 מבחן עיוור" אינטראקטיבי** | משחק מוזיקלי סוחף עם ספירה לאחור מונפשת, מעבר צלילי, גילוי עדין והמשך אוטומטי | 🟢 מיושם |
| **עדכונים בתוך האפליקציה** | בדיקה אוטומטית/ידנית של גרסאות דרך GitHub Releases | 🟢 ממומש |
| **ניהול אמנים ודיסקוגרפיה** | תצוגה ייעודית לכל אמן עם אלבומים, סינגלים ודיסקוגרפיה מלאה | 🟡 מתוכנן |
| **אקוולייזר גרפי (EQ)** | פריסטים אודיו ומעגל אקולייזר רב-פס פרמטרי | 🟡 מתוכנן |
| **מחבר Google Drive** | סריקה וסנכרון של אוספים אודיו מרחוק דרך OAuth 2.0 | ⚪ מתוכנן |
| **מחבר Amazon Music** | סריקה וסנכרון של אוספים מרחוק דרך OAuth 2.0 | ⚪ מתוכנן |
| **מחבר Spotify / Deezer** | ייבוא פלייליסטים ומציאת שירים | ⚪ מתוכנן |
| **הסרת כפילויות חכמה** | זיהוי כפילויות (שם/אמן מטושטשים + טביעות אקוסטיות) | ⚪ מתוכנן |

> 💡 *כדי לצפות בפרטים של אבני הדרך והגרסאות המתוכננות, עיינו ב־[מפת דרכים (Roadmap)](../../ROADMAP.md).*

---

## 📌 שפות זמינות

אנגלית, צרפתית, ספרדית, גרמנית, איטלקית, פורטוגזית, יפנית, רוסית, פולנית, טורקית, הולנדית, שוודית, אינדונזית, בולגרית, סרבית, בלארוסית, יוונית, קטלאנית, באסكية, גליסיאנית, צ'כית, סלובקית, הונגרית, קרואטית, סלובנית, בוסנית, אסטונית, לאטבית, ליטאית, נורווגית, דנית, פינית, איסלנדית, מאלאית, טאגאלית, סוואהילית, אספרנטו, סינית מפושטת, סינית מסורתית, קוריאנית, ערבית, עברית, וייטנאמית

---

## 🚀 התחלה מהירה

### דרישות קדם

- **Python 3.11** או גבוה יותר מותקן
- Git

### התקנה

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

## 🧪 השקת המבחנים

הפרויקט משתמש ב`pytest` עם חבילת בדיקות יחידה ושילוב:

```bash
pytest -v
```

הבדיקות רצות אוטומטית על **Windows, macOS et Ubuntu** בכל דחיפה דרך GitHub Actions.

---

## 🔒 אבטחה וּמפתחות API

- **לעולם אל תגלחו מפתחות API או אסימוני אימות אמיתיים.**
- הקובץ `.gitignore` מוגדר מראש כדי לחסום את `.env`, `credentials.json`, `token.json` וכל מסדי הנתונים המקומיים של SQLite.
- השתמשו ב-`.env.example` כתבנית לסביבת הפיתוח שלכם.

---

## 📋 תיעוד & מעקב אחר הפרויקט

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : יומן מפורט של גרסאות, תכונות חדשות ותיקוני באגים.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : מפת דרכים של אבני דרך עתידיות (אמנים, ענן, Spotify, ניקוי כפילויות).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : המגדיר של ארכיטקטורת תוכנה וכללי איכות קוד.

---

## 💖 תמיכה בפרויקט & הפצה

AMSO הוא תוכנה חופשית וחינמית (open source). אם אתם מעריכים את האפליקציה ורוצים לתמוך בפיתוחה:

- 🎮 **הורדה ותשלום לפי הרצון :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (קובץ הרצה מוקדם-מגובש ומוכן לשימוש)
- ☕ **תרומה ישירה :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [לתרום ל-LEF97](https://github.com/sponsors/LEF97)

---

## 📄 רישיון

הפרויקט הזה נמצא תחת רישיון **GNU General Public License v3.0 (GPL-3.0)** — עיין בקובץ [LICENSE](../../LICENSE) לפרטים נוספים.
