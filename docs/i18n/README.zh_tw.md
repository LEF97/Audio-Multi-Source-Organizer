# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <b>繁體中文</b> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) 是一款現代、響應迅速且跨平台的桌面音訊播放器 (Windows, Linux, macOS)。它旨在為發燒友提供對本地音樂庫 (MP3, FLAC, OGG…) 的完全控制，現已支援播放列表 (M3U, PLS, XSPF, WPL)、CUE 文件 (單一檔案的專輯，分割成曲目) 並整合了全新的盲測音訊模式！該專案正在發展成為一個統一的控制中心，能夠組織、去重並同步分散在本地磁碟、雲端儲存 (Google Drive) 和串流服務 (Spotify, Deezer, Amazon Music) 中的混合音樂收藏。

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

## 📌 功能 & 專案狀態

| 功能性 | 描述 | 狀態 |
| :--- | :--- | :---: |
| **音訊播放引擎** | 輕量且獨立的音訊播放器 (Windows 下自動安裝 VLC portable)。可選兩種引擎：直接 VLC 輸出，或連續緩衝引擎，以實現兩曲之間流暢的銜接 (Gapless 0 ms, 等功率淡入淡出，音訊輸出無斷層) | 🟢 已實作 |
| **媒體庫管理** | 本地資料夾的多執行緒遞迴掃描 (MP3, FLAC, AAC, OGG...)，手動、排程或即時同步，垃圾桶與媒體庫統計數據 | 🟢 已實作 |
| **中繼資料提取** | ID3、Vorbis Comments 的讀寫，以及音訊指紋計算 (`mutagen`) | 🟢 已實作 |
| **支援播放清單 (M3U, PLS, XSPF, WPL) & CUE 檔案** | 樹狀索引 (🎶)，順序播放，視覺化標記缺失曲目；`.cue` 檔案 (💿) 會像一個虛擬曲目資料夾一樣打開，顯示其時長，並像真實曲目一樣播放 | 🟢 已實作 |
| **播放清單管理器與拖放** | 虛擬佇列，流暢的拖放，可反轉的隨機播放 (shuffle) 和循環播放 | 🟢 已實作 |
| **互動式「🎲 盲測」模式** | 沉浸式的音樂遊戲，配有動畫計時器、音效淡入淡出、柔和揭示和自動銜接 | 🟢 已實作 |
| **應用程式內更新** | 透過 GitHub Releases 的自動/手動版本檢查 | 🟢 已實作 |
| **Linux 和 macOS 版本** | `.AppImage` / `.tar.gz` 套件 (Linux) 和未簽署的 `.dmg` (macOS)，需要 VLC | 🟡 實驗性 (未測試) |
| **藝人與唱片目錄管理** | 每個藝人專屬頁面，包含專輯、單曲和完整的唱片目錄 | 🟡 規劃中 |
| **圖形均衡器 (EQ)** | 音訊預設和參數化多頻帶均衡器 | 🟡 規劃中 |
| **Google Drive 連接器** | 透過 OAuth 2.0 掃描和同步遠端音訊收藏 | ⚪ 計劃中 |
| **Amazon Music 連接器** | 透過 OAuth 2.0 掃描和同步遠端收藏 | ⚪ 計劃中 |
| **Spotify / Deezer 連接器** | 匯入播放清單和曲目匹配 | ⚪ 計劃中 |
| **智慧去重** | 偵測重複（模糊的標題/藝人 + 音訊指紋） | ⚪ 計劃中 |

> 💡 *如需查閱預計的里程碑和版本詳情，請參閱 [路線圖 (Roadmap)](../../ROADMAP.md)。*

---

## 📌 可用語言

英語, 法語, 西班牙語, 德語, 義大利語, 葡萄牙語, 日語, 俄語, 波蘭語, 土耳其語, 荷蘭語, 瑞典語, 印尼語, 保加利亞語, 塞爾維亞語, 白俄語, 希臘語, 加泰隆語, 巴斯克語, 加利西亞語, 捷克語, 正格爾語, 匈牙利語, 克羅地亞語, 斯洛維尼亞語, 波斯尼亞語, 愛沙尼亞語, 拉脫維亞語, 立陶宛語, 挪威語, 丹麥語, 芬蘭語, 冰島語, 馬來語, 塔加洛語, 斯瓦希里語, 費斯蘭語, 簡體中文, 繁體中文, 韓語, 阿拉伯語, 希伯來語, 越南語

---

## 🚀 快速入門

### 前置條件

- **Python 3.11** 或更高版本已安裝
- Git

### 安裝

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

## 🐧🍎 Linux 和 macOS：實驗版本（未測試）

Linux 套件（`.AppImage` / `.tar.gz`）和 macOS（`.dmg`）是**未經測試**提供的：AMSO 僅在 Windows 上經過驗證。特別是連續緩衝區（`buffer`）音訊引擎，尚未在這些系統上檢查。您的回饋非常寶貴。

- **需要 VLC** (AMSO 僅在 Windows 下下載)：
  - Linux：`sudo apt install vlc` (Debian / Ubuntu)，`sudo dnf install vlc` (Fedora) 或 `sudo pacman -S vlc` (Arch)。
  - macOS：從 [videolan.org](https://www.videolan.org/vlc/) 將 **VLC.app** 安裝到 Applications 資料夾中。
- **Linux，系統函式庫**：Qt 介面特別需要 `libpulse0` (音訊)、`libxcb-cursor0` 和 `libxkbcommon-x11-0` (例如 `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`)。
- **macOS，未簽署的 `.dmg`**：首次啟動時，請對 AMSO 點擊右鍵然後選擇 **開啟**，或執行 `xattr -dr com.apple.quarantine /Applications/AMSO.app`。
- **Linux，AppImage**：使用 `chmod +x AMSO*.AppImage` 使其可執行。
- **若有問題**，請將位於資料夾中的 `startup.log` 和 `crash.log` (如果存在) 檔案發送給我們：macOS 下為 `~/Library/Application Support/AMSO/`，Linux 下為 `~/.local/share/AMSO/`。請同時說明您的系統和 VLC 版本。

---

## 🧪 測試啟動

該專案使用 `pytest`，並包含單元測試和整合測試的套件：

```bash
pytest -v
```

測試會在每次透過 GitHub Actions 推送時，自動在 **Windows, macOS 和 Ubuntu** 上執行。

---

## 🔒 安全 & API 金鑰

- **切勿提交真實的 API 金鑰或身份驗證令牌。**
- `.gitignore` 檔案預先配置了排除 `.env`、`credentials.json`、`token.json` 和所有本地 SQLite 資料庫。
- 請使用 `.env.example` 作為您的開發環境範本。

---

## 📋 文件記錄與專案追蹤

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : 版本的詳細日誌、新功能和錯誤修復。
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : 未來里程碑的路線圖（藝術家、Cloud、Spotify、去重）。
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : 軟體架構章程和程式碼品質規則。

---

## 💖 支持專案 & 發行

AMSO 是一個免費且開源的軟體 (open source)。如果您喜歡這個應用程式並希望支持其開發：

- 🎮 **下載與隨心支付：** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (即用型預編譯執行檔)
- ☕ **直接捐款：** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub 贊助人：** [贊助 LEF97](https://github.com/sponsors/LEF97)

---

## 📄 授權

本專案採用授權 **GNU General Public License v3.0 (GPL-3.0)** — 請參閱檔案 [LICENSE](../../LICENSE) 以了解更多詳情。
