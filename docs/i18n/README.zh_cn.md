# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <b>简体中文</b> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
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

> **AMSO** (Audio Multi-Source Organizer) 是一款现代、响应式、多平台的桌面音频播放器（Windows、Linux、macOS）。它旨在为发烧友提供对本地音乐库（MP3、FLAC、OGG…）的完全控制，现在支持播放列表（M3U、PLS、XSPF、WPL）、CUE 文件（拆分成轨道的单文件专辑）并集成了全新的音频盲测模式！该项目正在发展为一个统一的控制中心，能够组织、去重和同步分布在本地磁盘、云存储（Google Drive）和流媒体服务（Spotify、Deezer、Amazon Music）之间的混合音乐收藏。

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

## 📌 功能与项目状态

| 功能 | 描述 | 状态 |
| :--- | :--- | :---: |
| **集成 VLC 播放引擎** | 轻量级、独立的音频播放器，支持 VLC 便携版自动安装和流畅音量管理 | 🟢 已实现 |
| **多线程本地扫描** | 快速递归发现本地音频文件 (MP3, FLAC, AAC, OGG...) | 🟢 已实现 |
| **元数据提取** | 读取/写入 ID3、Vorbis Comments 并计算音频指纹 (`mutagen`) | 🟢 已实现 |
| **支持播放列表 (M3U, PLS, XSPF, WPL) 和 CUE 文件** | 树状索引 (🎶)，顺序播放，可视化缺失曲目定位；`.cue` 文件 (💿) 像一个包含时长和可播放的虚拟曲目文件夹一样打开 | 🟢 已实现 |
| **播放列表管理器和拖放** | 虚拟播放队列，流畅拖放，可逆随机播放 (shuffle) 和循环 | 🟢 已实现 |
| **交互式“🎲 盲测”模式** | 沉浸式音乐游戏，带有动画倒计时、音效淡入淡出、平滑揭示和自动衔接 | 🟢 已实现 |
| **应用内更新** | 通过 GitHub Releases 的自动/手动版本检查 | 🟢 已实现 |
| **艺人与唱片管理** | 艺术家专用视图，包含专辑、单曲和完整唱片目录 | 🟡 计划中 |
| **图形均衡器 (EQ)** | 音频预设和参数多频带均衡器 | 🟡 计划中 |
| **Google Drive 连接器** | 通过 OAuth 2.0 扫描和同步远程音频收藏 | ⚪ 待规划 |
| **Amazon Music 连接器** | 通过 OAuth 2.0 扫描和同步远程收藏 | ⚪ 待规划 |
| **Spotify / Deezer 连接器** | 导入播放列表和匹配曲目 | ⚪ 待规划 |
| **智能去重** | 重复检测（模糊标题/艺术家 + 声学指纹） | ⚪ 待规划 |

> 💡 *要查看计划的里程碑和版本详情，请参阅 [路线图 (Roadmap)](../../ROADMAP.md)。*

---

## 📌 可用语言

英语, 法语, 西班牙语, 德语, 意大利语, 葡萄牙语, 日语, 俄语, 波兰语, 土耳其语, 荷兰语, 瑞典语, 印度尼西亚语, 保加利亚语, 塞尔维亚语, 白俄罗斯语, 希腊语, 加泰罗尼亚语, 巴斯克语, 加利西亚语, 捷克语, 斯洛伐克语, 匈牙利语, 克罗地亚语, 斯洛文尼亚语, 波斯尼亚语, 爱沙尼亚语, 拉脱维亚语, 立陶宛语, 挪威语, 丹麦语, 芬兰语, 冰岛语, 马来语, 塔加洛语, 斯瓦希里语, 斯佩尔兰语, 简体中文, 繁体中文, 韩语, 阿拉伯语, 希伯来语, 越南语

---

## 🚀 快速入门

### 前提条件

- **Python 3.11** 或更高版本已安装
- Git

### 安装

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

## 🧪 测试启动

该项目使用`pytest`，并包含单元测试和集成测试套件：

```bash
pytest -v
```

测试会在每次推送时，通过 GitHub Actions 自动运行在 **Windows, macOS 和 Ubuntu** 上。

---

## 🔒 安全与 API 密钥

- **永远不要提交真实的 API 密钥或身份验证令牌。**
- `.gitignore` 文件已预配置为阻止 `.env`、`credentials.json`、`token.json` 和所有本地 SQLite 数据库。
- 使用 `.env.example` 作为开发环境的模板。

---

## 📋 文档 & 项目跟踪

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : 版本、新功能和错误修复的详细日志。
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : 未来里程碑（艺术家、Cloud、Spotify、去重）路线图。
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : 软件架构规范和代码质量规则。

---

## 💖 支持项目 & 分发

AMSO 是一个免费的开源软件 (open source)。如果您喜欢这个应用程序并希望支持其开发：

- 🎮 **下载和按需付费：** [AMSO 的 itch.io 页面](https://lef97.itch.io/audio-multi-source-organizer) (即用型预编译可执行文件)
- ☕ **直接捐赠：** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub 赞助：** [赞助 LEF97](https://github.com/sponsors/LEF97)

---

## 📄 许可证

本项目采用 **GNU General Public License v3.0 (GPL-3.0)** 许可 — 请查阅 [LICENSE](../../LICENSE) 文件了解更多详细信息。
