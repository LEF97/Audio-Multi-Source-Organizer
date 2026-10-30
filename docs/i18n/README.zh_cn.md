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

## 📌 功能与项目状态

| 功能 | 描述 | 状态 |
| :--- | :--- | :---: |
| **音频播放引擎** | 轻量级独立音频播放器 (VLC portable 自动安装于 Windows)。可选两种引擎：VLC 直接输出，或连续缓冲区引擎，用于两曲之间流畅衔接 (Gapless 0 ms, 等功率淡入淡出，无音频输出中断) | 🟢 已实现 |
| **库管理** | 本地文件夹多线程递归扫描 (MP3, FLAC, AAC, OGG...)，手动、计划或实时同步，垃圾箱和库统计 | 🟢 已实现 |
| **元数据提取** | 读取/写入 ID3, Vorbis Comments 并计算音频指纹 (`mutagen`) | 🟢 已实现 |
| **播放列表支持 (M3U, PLS, XSPF, WPL) & CUE 文件** | 树形索引 (🎶)，顺序播放，缺失曲目可视化定位；`.cue` 文件 (💿) 像一个包含其持续时间和可作为真实曲目播放的虚拟曲目文件夹打开 | 🟢 已实现 |
| **播放列表管理器和拖放** | 虚拟播放队列，流畅的 drag & drop，可逆随机播放 (shuffle) 和循环 | 🟢 已实现 |
| **互动模式 « 🎲 Blind Test »** | 沉浸式音乐游戏，包含动画倒计时、音频淡出、平滑揭示和自动衔接 | 🟢 已实现 |
| **应用内更新** | 通过 GitHub Releases 进行自动/手动版本检查 | 🟢 已实现 |
| **Linux 和 macOS 版本** | Paquets `.AppImage` / `.tar.gz` (Linux) et `.dmg` non signé (macOS), VLC requis | 🟡 实验性 (未测试) |
| **艺术家和唱片目录管理** | 艺术家专用视图，包含专辑、单曲和完整唱片目录 | 🟡 计划中 |
| **图形均衡器 (EQ)** | 音频预设和参数多频带均衡器 | 🟡 计划中 |
| **Google Drive 连接器** | 通过 OAuth 2.0 扫描和同步远程音频收藏 | ⚪ 已计划 |
| **Amazon Music 连接器** | 通过 OAuth 2.0 扫描和同步远程收藏 | ⚪ 已计划 |
| **Spotify / Deezer 连接器** | 导入播放列表和匹配曲目 | ⚪ 已计划 |
| **智能去重** | 重复内容检测（模糊标题/艺术家 + 声学指纹） | ⚪ 已计划 |

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

## 🐧🍎 Linux 和 macOS：实验版本（未测试）

Linux 包 (`.AppImage` / `.tar.gz`) 和 macOS (`.dmg`) 包提供的 **未经测试**：AMSO 仅在 Windows 上进行了验证。特别是连续缓冲区音频引擎 (`buffer`) 在这些系统上尚未经过测试。您的反馈对我们非常宝贵。

- **需要 VLC** (AMSO 仅在 Windows 下下载)：
  - Linux：`sudo apt install vlc` (Debian / Ubuntu)，`sudo dnf install vlc` (Fedora) 或 `sudo pacman -S vlc` (Arch)。
  - macOS：从 [videolan.org](https://www.videolan.org/vlc/) 下载 **VLC.app** 并将其放入 Applications 文件夹。
- **Linux，系统库**：Qt 界面尤其需要 `libpulse0` (音频)，`libxcb-cursor0` 和 `libxkbcommon-x11-0` (例如 `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`)。
- **macOS，未签名的 .dmg**：首次启动时，右键单击 AMSO，然后选择 **打开**，或运行 `xattr -dr com.apple.quarantine /Applications/AMSO.app`。
- **Linux，AppImage**：使用 `chmod +x AMSO*.AppImage` 使其可执行。
- **如果遇到问题**，请发送位于数据文件夹中的 `startup.log` 和 `crash.log` 文件（如果存在）：macOS 下的 `~/Library/Application Support/AMSO/`，Linux 下的 `~/.local/share/AMSO/`。请注明您的系统和 VLC 版本。

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
