# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <b>Tiếng Việt</b>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) là một trình phát âm thanh máy tính để bàn hiện đại, phản hồi nhanh và đa nền tảng (Windows, Linux, macOS). Được thiết kế để mang lại cho những người yêu âm thanh khả năng kiểm soát hoàn toàn thư viện âm nhạc cục bộ của họ (MP3, FLAC, OGG…), nó hiện hỗ trợ các danh sách phát (M3U, PLS, XSPF, WPL), các tệp CUE (album một tệp được cắt thành các bản nhạc) và tích hợp một chế độ thử âm thanh mù hoàn toàn mới! Dự án đang phát triển để trở thành một trung tâm điều khiển hợp nhất có khả năng tổ chức, loại bỏ trùng lặp và đồng bộ hóa các bộ sưu tập âm nhạc lai được phân tán giữa ổ đĩa cục bộ, lưu trữ đám mây (Google Drive) và các dịch vụ streaming (Spotify, Deezer, Amazon Music).

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

## 📌 Tính năng & Trạng thái dự án

| Tính năng | Mô tả | Trạng thái |
| :--- | :---: | :---: |
| **Công cụ phát âm thanh** | Trình phát âm thanh nhẹ và độc lập (VLC portable được cài đặt tự động trên Windows). Hai công cụ lựa chọn: xuất trực tiếp VLC, hoặc công cụ bộ đệm liên tục để chuyển tiếp mượt mà giữa hai bản nhạc (Gapless 0 ms, fade bằng công suất bằng nhau, không gián đoạn đầu ra âm thanh) | 🟢 Đã triển khai |
| **Quản lý thư viện** | Quét đệ quy đa luồng các thư mục cục bộ (MP3, FLAC, AAC, OGG...), đồng bộ hóa thủ công, theo lịch hoặc thời gian thực, thùng rác và thống kê thư viện | 🟢 Đã triển khai |
| **Trích xuất siêu dữ liệu** | Đọc/ghi ID3, Vorbis Comments và tính toán dấu vân tay âm thanh (`mutagen`) | 🟢 Đã triển khai |
| **Hỗ trợ Playlist (M3U, PLS, XSPF, WPL) & sheet CUE** | Lập chỉ mục cây (🎶), thứ tự nghe tuần tự, định vị trực quan các bài hát bị thiếu; các tệp `.cue` (💿) mở như một thư mục các bản nhạc ảo với thời lượng của chúng và phát như các bản nhạc thực tế | 🟢 Đã triển khai |
| **Trình quản lý Playlist & Kéo-Thả** | Hàng đợi ảo, kéo & thả mượt mà, ngẫu nhiên (shuffle) có thể đảo ngược và vòng lặp | 🟢 Đã triển khai |
| **Chế độ tương tác « 🎲 Blind Test »** | Trò chơi âm nhạc nhập vai với bộ đếm thời gian hoạt hình, fade âm thanh, tiết lộ nhẹ nhàng và chuyển tiếp tự động | 🟢 Đã triển khai |
| **Cập nhật trong ứng dụng** | Kiểm tra phiên bản tự động/thủ công qua GitHub Releases | 🟢 Đã triển khai |
| **Phiên bản Linux & macOS** | Gói `.AppImage` / `.tar.gz` (Linux) và `.dmg` không ký (macOS), yêu cầu VLC | 🟡 Thử nghiệm (chưa kiểm tra) |
| **Quản lý nghệ sĩ & Discography** | Chế độ xem dành riêng cho nghệ sĩ với album, single và discography đầy đủ | 🟡 Dự kiến |
| **Bộ cân bằng đồ họa (EQ)** | Thiết lập âm thanh và bộ cân bằng đa băng tần tham số | 🟡 Dự kiến |
| **Kết nối Google Drive** | Quét và đồng bộ hóa các bộ sưu tập âm thanh từ xa qua OAuth 2.0 | ⚪ Lên kế hoạch |
| **Kết nối Amazon Music** | Quét và đồng bộ hóa các bộ sưu tập từ xa qua OAuth 2.0 | ⚪ Lên kế hoạch |
| **Kết nối Spotify / Deezer** | Nhập danh sách phát và khớp bài hát | ⚪ Lên kế hoạch |
| **Loại bỏ trùng lặp thông minh** | Phát hiện bản sao (tiêu đề/nghệ sĩ mờ + dấu vân âm thanh) | ⚪ Lên kế hoạch |

> 💡 *Để xem chi tiết các cột mốc và phiên bản dự kiến, vui lòng tham khảo [Feuille de route (Roadmap)](../../ROADMAP.md).*

---

## 📌 Các ngôn ngữ có sẵn

Tiếng Anh, Tiếng Pháp, Tiếng Tây Ban Nha, Tiếng Đức, Tiếng Ý, Tiếng Bồ Đào Nha, Tiếng Nhật, Tiếng Nga, Tiếng Ba Lan, Tiếng Thổ Nhĩ Kỳ, Tiếng Hà Lan, Tiếng Thụy Điển, Tiếng Indonesia, Tiếng Bulgaria, Tiếng Serbia, Tiếng Belarus, Tiếng Hy Lạp, Tiếng Catalan, Tiếng Basque, Tiếng Galician, Tiếng Séc, Tiếng Slovak, Tiếng Hungary, Tiếng Croatia, Tiếng Slovenia, Tiếng Bosnia, Tiếng Estonia, Tiếng Latvia, Tiếng Lithuania, Tiếng Na Uy, Tiếng Đan Mạch, Tiếng Phần Lan, Tiếng Iceland, Tiếng Mã Lai, Tiếng Tagalog, Tiếng Swahili, Tiếng Esperanto, Tiếng Trung giản thể, Tiếng Trung phồn thể, Tiếng Hàn, Tiếng Ả Rập, Tiếng Hebrew, Tiếng Việt

---

## 🚀 Khởi động nhanh

### Yêu cầu

- **Python 3.11** hoặc phiên bản cao hơn đã cài đặt
- Git

### Cài đặt

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

## 🐧🍎 Linux và macOS: phiên bản thử nghiệm (chưa được kiểm tra)

Các gói Linux (`.AppImage` / `.tar.gz`) và macOS (`.dmg`) được cung cấp **mà chưa được kiểm tra**: AMSO chỉ được xác nhận trên Windows. Đặc biệt, công cụ âm thanh bộ đệm liên tục (`buffer`) chưa được kiểm tra trên các hệ thống này. Phản hồi của bạn rất quý giá.

- **VLC là bắt buộc** (AMSO chỉ tải xuống trên Windows) :
  - Linux : `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) hoặc `sudo pacman -S vlc` (Arch).
  - macOS : cài đặt **VLC.app** từ [videolan.org](https://www.videolan.org/vlc/) vào thư mục Applications.
- **Linux, thư viện hệ thống** : giao diện Qt yêu cầu đặc biệt `libpulse0` (âm thanh), `libxcb-cursor0` và `libxkbcommon-x11-0` (ví dụ: `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, `.dmg` chưa được ký** : lần khởi chạy đầu tiên, hãy nhấp chuột phải vào AMSO rồi **Mở**, hoặc chạy `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage** : làm cho nó có thể thực thi bằng `chmod +x AMSO*.AppImage`.
- **Trong trường hợp gặp sự cố**, vui lòng gửi các tệp `startup.log` và `crash.log` (nếu có) nằm trong thư mục dữ liệu: `~/Library/Application Support/AMSO/` trên macOS, `~/.local/share/AMSO/` trên Linux. Vui lòng nêu rõ hệ điều hành và phiên bản VLC của bạn.

---

## 🧪 Khởi động các bài kiểm tra

Dự án sử dụng `pytest` với một bộ kiểm thử đơn vị và tích hợp:

```bash
pytest -v
```

Các bài kiểm tra được chạy tự động trên **Windows, macOS và Ubuntu** mỗi khi push qua GitHub Actions.

---

## 🔒 Bảo mật & Khóa API

- **Không bao giờ commit các khóa API hoặc token xác thực thực tế.**
- Tệp `.gitignore` được cấu hình sẵn để chặn `.env`, `credentials.json`, `token.json` và tất cả các cơ sở dữ liệu SQLite cục bộ.
- Sử dụng `.env.example` làm mẫu cho môi trường phát triển của bạn.

---

## 📋 Tài liệu & Theo dõi dự án

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Nhật ký chi tiết các phiên bản, tính năng mới và sửa lỗi.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Lộ trình các cột mốc tương lai (Artistes, Cloud, Spotify, Dédoublonnage).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Quy tắc kiến trúc phần mềm và các quy tắc chất lượng mã.

---

## 💖 Hỗ trợ dự án & Phân phối

AMSO là một phần mềm tự do và miễn phí (open source). Nếu bạn thích ứng dụng và muốn khuyến khích phát triển nó:

- 🎮 **Tải xuống & Pay What You Want :** [Trang Itch.io của AMSO](https://lef97.itch.io/audio-multi-source-organizer) (tệp thực thi được biên dịch sẵn, sẵn sàng sử dụng)
- ☕ **Ủng hộ trực tiếp :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **Nhà tài trợ GitHub :** [Tài trợ cho LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Giấy phép

Dự án này được cấp phép theo **GNU General Public License v3.0 (GPL-3.0)** — hãy xem tệp [LICENSE](../../LICENSE) để biết thêm chi tiết.
