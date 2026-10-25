# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <b>العربية</b>
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

> **AMSO** (Audio Multi-Source Organizer) هو مشغل صوتي مكتبي حديث، ومتجاوب ومتعدد المنصات (Windows, Linux, macOS). تم تصميمه لتقديم تحكم كامل لعشاق الصوتيات في مكتبتهم الموسيقية المحلية (MP3, FLAC, OGG…)، وهو يدعم الآن قوائم التشغيل (M3U, PLS, XSPF, WPL)، وأوراق CUE (الألبومات ذات الملف الواحد المقسمة إلى مقاطع)، ويتضمن وضع اختبار الصوت الأعمى (blind test audio) الجديد كلياً! يتطور المشروع ليصبح مركز تحكم موحد قادر على تنظيم وتزيل التكرارات ومزامنة المجموعات الموسيقية الهجينة الموزعة بين الأقراص المحلية، والتخزين السحابي (Google Drive)، وخدمات البث (Spotify, Deezer, Amazon Music).

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

## 📌 الميزات وحالة المشروع

| الميزة | الوصف | الحالة |
| :--- | :---: | :---: |
| **محرك تشغيل VLC المدمج** | مشغل صوتي خفيف ومستقل مع التثبيت التلقائي لـ VLC المحمول وإدارة سلسة للصوت | 🟢 مُنفَّذ |
| **الماسح المحلي متعدد الخيوط** | الاكتشاف التكراري والسريع للملفات الصوتية المحلية (MP3, FLAC, AAC, OGG...) | 🟢 مُنفَّذ |
| **استخراج البيانات الوصفية** | قراءة/كتابة ID3، Vorbis Comments وحساب البصمة الصوتية (`mutagen`) | 🟢 مُنفَّذ |
| **دعم قوائم التشغيل (M3U, PLS, XSPF, WPL) وأوراق CUE** | الفهرسة الشجرية (🎶)، الترتيب التسلسلي للاستماع، تحديد مرئي للمقاطع المفقودة؛ ملفات `.cue` (💿) تفتح كمجلد مسارات افتراضية مع مدتها وتُشغَّل كمسارات حقيقية | 🟢 مُنفَّذ |
| **مدير قائمة التشغيل والسحب والإفلات** | قائمة الانتظار الافتراضية، سحب وإفلات سلس، عشوائي (shuffle) قابل للعكس والحلقات | 🟢 مُنفَّذ |
| **وضع « 🎲 اختبار التعمية » التفاعلي** | لعبة موسيقية غامرة مع عد تنازلي متحرك، وتلاشي صوتي، وكشف ناعم، وتسلسل تلقائي | 🟢 مُنفَّذ |
| **تحديثات داخل التطبيق** | التحقق التلقائي/اليدوي من الإصدارات عبر GitHub Releases | 🟢 مُنفَّذ |
| **إدارة الفنانين والتسجيلات الغنائية** | عرض مخصص لكل فنان يتضمن الألبومات والأغاني المنفردة والتسجيلات الغنائية الكاملة | 🟡 مُخطَّط |
| **المعادل الصوتي الرسومي (EQ)** | الإعدادات المسبقة للصوت والمعادل متعدد النطاقات البارامتري | 🟡 مُخطَّط |
| **موصل Google Drive** | مسح ومزامنة مجموعات صوتية عن بُعد عبر OAuth 2.0 | ⚪ مُخطَّط |
| **موصل Amazon Music** | مسح ومزامنة مجموعات عن بُعد عبر OAuth 2.0 | ⚪ مُخطَّط |
| **موصل Spotify / Deezer** | استيراد قوائم التشغيل ومطابقة المقاطع | ⚪ مُخطَّط |
| **إزالة التكرار الذكية** | اكتشاف التكرارات (العنوان/الفنان الغامض + البصمات الصوتية) | ⚪ مُخطَّط |

> 💡 *للاطلاع على تفاصيل المراحل والإصدارات المخطط لها، يرجى الرجوع إلى [Feuille de route (Roadmap)](../../ROADMAP.md).*

---

## 📌 اللغات المتاحة

الإنجليزية، الفرنسية، الإسبانية، الألمانية، الإيطالية، البرتغالية، اليابانية، الروسية، البولندية، التركية، الهولندية، السويدية، الإندونيسية، البلغارية، الصربية، البيلاروسية، اليونانية، الكاتالونية، الباسكية، الغاليسية، التشيكية، السلوفاكية، المجرية، الكرواتية، السلوفينية، البوسنية، الإستونية، اللاتفية، الليتوانية، النرويجية، الدنماركية، الفنلندية، الأيسلندية، الملايو، التاغالوغ، السواحيلية، الإسبيرانتو، الصينية المبسطة، الصينية التقليدية، الكورية، العربية، العبرية، الفيتنامية

---

## 🚀 البدء السريع

### المتطلبات

- **Python 3.11** أو أعلى إصدار مُثبَّت
- Git

### التثبيت

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

## 🧪 إطلاق الاختبارات

يستخدم المشروع `pytest` مع مجموعة من اختبارات الوحدة والتكامل:

```bash
pytest -v
```

تُشغَّل الاختبارات تلقائيًا على **Windows, macOS et Ubuntu** عند كل عملية دفع عبر GitHub Actions.

---

## 🔒 الأمان ومفاتيح API

- **لا تقم أبدًا بتضمين مفاتيح API أو رموز مصادقة حقيقية.**
- تم إعداد ملف `.gitignore` مسبقًا لحظر `.env`، و `credentials.json`، و `token.json`، وجميع قواعد بيانات SQLite المحلية.
- استخدم `.env.example` كنموذج لبيئة التطوير الخاصة بك.

---

## 📋 التوثيق ومتابعة المشروع

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : سجل مفصل للإصدارات والميزات الجديدة وتصحيحات الأخطاء.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : خريطة الطريق للمعالم المستقبلية (الفنانون، Cloud، Spotify، إزالة التكرار).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : ميثاق هندسة البرمجيات وقواعد جودة الكود.

---

## 💖 دعم المشروع و التوزيع

AMSO هو برنامج مجاني ومفتوح المصدر (open source). إذا أعجبك التطبيق وترغب في تشجيع تطويره:

- 🎮 **التحميل وادفع ما تريد :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (ملف تنفيذي مُجمَّع مسبقًا وجاهز للاستخدام)
- ☕ **التبرع المباشر :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [Sponsoriser LEF97](https://github.com/sponsors/LEF97)

---

## 📄 الترخيص

هذا المشروع مرخص بموجب **GNU General Public License v3.0 (GPL-3.0)** — يرجى الاطلاع على الملف [LICENSE](../../LICENSE) لمزيد من التفاصيل.
