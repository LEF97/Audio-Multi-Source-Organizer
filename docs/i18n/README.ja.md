# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <b>日本語</b> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
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

> **AMSO** (Audio Multi-Source Organizer) は、モダンで、反応性が高く、マルチプラットフォーム対応のデスクトップオーディオプレーヤーです（Windows、Linux、macOS）。オーディオファイル愛好家がローカルの音楽ライブラリ（MP3, FLAC, OGG…）を完全に管理できるように設計されており、現在ではプレイリスト（M3U, PLS, XSPF, WPL）、CUEシート（トラックに分割された単一ファイルのアルバム）をサポートし、全く新しいブラインドテストオーディオモードを組み込んでいます！このプロジェクトは、ローカルディスク、クラウドストレージ（Google Drive）、およびストリーミングサービス（Spotify, Deezer, Amazon Music）に分散したハイブリッドな音楽コレクションを整理、重複排除、同期できる統一されたコントロールセンターへと進化しています。

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

## 📌 機能とプロジェクトのステータス

| 機能 | 説明 | ステータス |
| :--- | :---: | :---: |
| **オーディオ再生エンジン** | 軽量で独立したオーディオプレーヤー（Windowsに自動インストールされるVLCポータブル）。選択可能な2つのエンジン：直接VLC出力、または2トラック間のスムーズな連続再生のためのバッファリングエンジン（Gapless 0 ms、等パワーフェード、オーディオ出力の途切れなし）。 | 🟢 実装済み |
| **ライブラリ管理** | ローカルフォルダのマルチスレッド再帰スキャン（MP3, FLAC, AAC, OGG...）、手動、スケジュール、またはリアルタイム同期、ゴミ箱、およびライブラリ統計。 | 🟢 実装済み |
| **メタデータ抽出** | ID3、Vorbis Commentsの読み書き、およびオーディオフィンガープリントの計算（`mutagen`）。 | 🟢 実装済み |
| **プレイリストサポート（M3U, PLS, XSPF, WPL）およびCUEシート** | ツリーインデックス化（🎶）、シーケンシャルな再生順序、欠落したトラックの視覚的な特定。`.cue`ファイル（💿）は、その長さとともに仮想トラックフォルダとして開き、実際のトラックのように再生されます。 | 🟢 実装済み |
| **プレイリスト管理＆ドラッグ＆ドロップ** | 仮想キュー、スムーズなドラッグ＆ドロップ、リバーシブルなシャッフル、およびループ。 | 🟢 実装済み |
| **対話型「🎲 ブラインドテスト」モード** | アニメーション付きのカウントダウン、サウンドフェード、穏やかな開示、および自動連続再生を備えた没入型の音楽ゲーム。 | 🟢 実装済み |
| **アプリ内アップデート** | GitHub Releases を介した自動/手動バージョン確認 | 🟢 実装済み |
| **Linux および macOS のバージョン** | パッケージ .AppImage / .tar.gz (Linux) および署名されていない .dmg (macOS)、VLC が必要 | 🟡 実験的 (未テスト) |
| **アーティストおよびディスコグラフィ管理** | アルバム、シングル、完全なディスコグラフィを含むアーティスト専用ビュー | 🟡 予定 |
| **グラフィックイコライザー (EQ)** | オーディオプリセットとパラメトリックマルチバンドイコライザー | 🟡 予定 |
| **Google Drive コネクタ** | OAuth 2.0 を介したリモートオーディオコレクションのスキャンと同期 | ⚪ 計画中 |
| **Amazon Music コネクタ** | OAuth 2.0 を介したリモートコレクションのスキャンと同期 | ⚪ 計画中 |
| **Spotify / Deezer コネクタ** | プレイリストのインポートとトラックのマッチング | ⚪ 計画中 |
| **スマート重複排除** | 重複検出 (タイトル/アーティストのぼかし + 音響指紋) | ⚪ 計画中 |

> 💡 *計画されているマイルストーンとバージョンの詳細を確認するには、[ロードマップ (Roadmap)](../../ROADMAP.md)を参照してください。*

---

## 📌 利用可能な言語

英語, フランス語, スペイン語, ドイツ語, イタリア語, ポルトガル語, 日本語, ロシア語, ポーランド語, トルコ語, オランダ語, スウェーデン語, インドネシア語, ブルガリア語, セルビア語, ベラルーシ語, ギリシャ語, カタルーニャ語, バスク語, ガリシア語, チェコ語, スロバキア語, ハンガリー語, クロアチア語, スロベニア語, ボスニア語, エストニア語, ラトビア語, リトアニア語, ノルウェー語, デンマーク語, フィンランド語, アイスランド語, マレー語, タガログ語, スワヒリ語, エスペラント語, 簡体字中国語, 繁体字中国語, 韓国語, アラビア語, ヘブライ語, ベトナム語

---

## 🚀 クイックスタート

### 前提条件

- **Python 3.11** 以上がインストールされている
- Git

### インストール

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

## 🐧🍎 LinuxとmacOS：実験版（未テスト）

Linuxパッケージ（`.AppImage` / `.tar.gz`）およびmacOSパッケージ（`.dmg`）は、**テストされていない状態で**提供されます。AMSOはWindowsでのみ検証されています。特に、連続バッファオーディオエンジン（`buffer`）は、これらのシステムでは確認されていません。皆様からのフィードバックは貴重です。

- **VLCが必要です** (AMSOはWindowsでのみダウンロードします) :
  - Linux : `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) または `sudo pacman -S vlc` (Arch)。
  - macOS : アプリケーションフォルダから [videolan.org](https://www.videolan.org/vlc/) で **VLC.app** をインストールしてください。
- **Linux、システムライブラリ** : Qtインターフェースは、特に `libpulse0` (サウンド)、`libxcb-cursor0`、および `libxkbcommon-x11-0` を要求します (例: `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`)。
- **macOS、署名されていない.dmg** : 初回起動時には、AMSOを右クリックし **開く** を選択するか、`xattr -dr com.apple.quarantine /Applications/AMSO.app` を実行してください。
- **Linux、AppImage** : `chmod +x AMSO*.AppImage` で実行可能にしてください。
- **問題が発生した場合**、データフォルダ内にある `startup.log` および `crash.log` (存在する場合) ファイルを送信してください：macOSでは `~/Library/Application Support/AMSO/`、Linuxでは `~/.local/share/AMSO/` です。お使いのシステムとVLCのバージョンを明記してください。

---

## 🧪 テストの開始

プロジェクトは、ユニットテストと統合テストのスイートとして`pytest`を使用します：

```bash
pytest -v
```

テストは、GitHub Actions を介したプッシュのたびに、**Windows, macOS, および Ubuntu** で自動的に実行されます。

---

## 🔒 セキュリティとAPIキー

- **実際のAPIキーや認証トークンをコミットしないでください。**
- `.gitignore`ファイルは、`.env`、`credentials.json`、`token.json`、およびすべてのローカルSQLiteデータベースをブロックするように事前設定されています。
- 開発環境のテンプレートとして`.env.example`を使用してください。

---

## 📋 ドキュメントとプロジェクトの進捗管理

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : バージョン、新機能、バグ修正の詳細なログ。
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : 今後のマイルストーン（アーティスト、クラウド、Spotify、重複排除）のロードマップ。
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : ソフトウェアアーキテクチャの憲章とコード品質のルール。

---

## 💖 プロジェクトの支援と配布

AMSOは、自由で無料のソフトウェアです（open source）。もしこのアプリケーションを気に入っていただき、その開発を支援したい場合は：

- 🎮 **ダウンロード＆好きな金額で支払う :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (すぐに使える事前コンパイルされた実行ファイル)
- ☕ **直接寄付をする :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [LEF97をスポンサーする](https://github.com/sponsors/LEF97)

---

## 📄 ライセンス

このプロジェクトは **GNU General Public License v3.0 (GPL-3.0)** ライセンスの下で提供されています。詳細については、[LICENSE](../../LICENSE) ファイルを参照してください。
