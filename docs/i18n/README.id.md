# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <b>Bahasa Indonesia</b> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) adalah pemutar audio desktop modern, responsif, dan multiplatform (Windows, Linux, macOS). Dirancang untuk memberikan kontrol total kepada audiophile atas perpustakaan musik lokal mereka (MP3, FLAC, OGG…), kini ia mendukung daftar putar (M3U, PLS, XSPF, WPL), lembar CUE (album satu file yang dipotong menjadi trek) dan menyertakan mode blind test audio yang benar-benar baru! Proyek ini berkembang menjadi pusat kendali terpadu yang mampu mengatur, menghilangkan duplikasi, dan menyinkronkan koleksi musik hibrida yang tersebar antara disk lokal, penyimpanan cloud (Google Drive), dan layanan streaming (Spotify, Deezer, Amazon Music).

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

## 📌 Fitur & Status Proyek

| Fitur | Deskripsi | Status |
| :--- | :---: | :---: |
| **Mesin Pemutar Audio** | Pemutar audio ringan dan mandiri (VLC portable diinstal otomatis di Windows). Dua mesin pilihan: output langsung VLC, atau mesin buffer berkelanjutan untuk transisi mulus antar trek (Gapless 0 ms, fade out dengan kekuatan yang sama, tanpa gangguan output audio) | 🟢 Implémenté |
| **Manajemen Perpustakaan** | Pemindaian rekursif multithread dari folder lokal (MP3, FLAC, AAC, OGG...), sinkronisasi manual, terjadwal atau waktu nyata, tempat sampah, dan statistik perpustakaan | 🟢 Implémenté |
| **Ekstraksi Metadata** | Baca/tulis ID3, Vorbis Comments, dan perhitungan sidik jari audio (`mutagen`) | 🟢 Implémenté |
| **Dukungan Playlist (M3U, PLS, XSPF, WPL) & lembar CUE** | Pengindeksan pohon (🎶), urutan mendengarkan sekuensial, penandaan visual untuk potongan yang hilang; file `.cue` (💿) terbuka seperti folder trek virtual dengan durasinya dan diputar seperti trek nyata | 🟢 Implémenté |
| **Pengelola Playlist & Seret-Lepas** | Antrian virtual, drag & drop mulus, acak (shuffle) yang dapat dibalik, dan loop | 🟢 Implémenté |
| **Mode « 🎲 Blind Test » interaktif** | Permainan musik imersif dengan hitungan mundur animasi, fade suara, pengungkapan lembut, dan urutan otomatis | 🟢 Implémenté |
| **Pembaruan dalam aplikasi** | Pemeriksaan versi otomatis/manual melalui GitHub Releases | 🟢 Diimplementasikan |
| **Versi Linux & macOS** | Paket `.AppImage` / `.tar.gz` (Linux) dan `.dmg` tidak ditandatangani (macOS), VLC diperlukan | 🟡 Eksperimental (belum diuji) |
| **Manajemen Artis & Diskografi** | Tampilan khusus per artis dengan album, single, dan diskografi lengkap | 🟡 Direncanakan |
| **Equalizer Grafis (EQ)** | Preset audio dan equalizer multiband parametrik | 🟡 Direncanakan |
| **Konektor Google Drive** | Pemindaian dan sinkronisasi koleksi audio jarak jauh melalui OAuth 2.0 | ⚪ Direncanakan |
| **Konektor Amazon Music** | Pemindaian dan sinkronisasi koleksi jarak jauh melalui OAuth 2.0 | ⚪ Direncanakan |
| **Konektor Spotify / Deezer** | Impor playlist dan pencocokan trek | ⚪ Direncanakan |
| **Penghapusan Duplikat Cerdas** | Deteksi duplikat (judul/artis kabur + sidik jari akustik) | ⚪ Direncanakan |

> 💡 *Untuk melihat detail tonggak dan versi yang direncanakan, silakan merujuk ke [Feuille de route (Roadmap)](../../ROADMAP.md).*

---

## 📌 Bahasa yang tersedia

Inggris, Prancis, Spanyol, Jerman, Italia, Portugis, Jepang, Rusia, Polandia, Turki, Belanda, Swedia, Indonesia, Bulgaria, Serbia, Belarusia, Yunani, Katalan, Basque, Galisia, Ceko, Slovakia, Hongaria, Kroasia, Slovenia, Bosnia, Estonia, Latvia, Lituania, Norwegia, Denmark, Finlandia, Islandia, Melayu, Tagalog, Swahili, Esperanto, Mandarin Sederhana, Mandarin Tradisional, Korea, Arab, Ibrani, Vietnam

---

## 🚀 Memulai cepat

### Prasyarat

- **Python 3.11** atau yang lebih tinggi terinstal
- Git

### Instalasi

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

## 🐧🍎 Linux dan macOS: versi eksperimental (tidak diuji)

Paket Linux (`.AppImage` / `.tar.gz`) dan macOS (`.dmg`) disediakan **tanpa diuji**: AMSO hanya divalidasi di Windows. Mesin audio buffer berkelanjutan (`buffer`) khususnya belum diverifikasi pada sistem ini. Masukan Anda sangat berharga.

- **VLC diperlukan** (AMSO hanya mengunduhnya di Windows):
  - Linux : `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) atau `sudo pacman -S vlc` (Arch).
  - macOS : instal **VLC.app** dari [videolan.org](https://www.videolan.org/vlc/) di folder Applications.
- **Linux, pustaka sistem** : antarmuka Qt memerlukan terutama `libpulse0` (suara), `libxcb-cursor0` dan `libxkbcommon-x11-0` (misalnya `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, `.dmg` tidak ditandatangani** : pada peluncuran pertama, klik kanan pada AMSO lalu **Buka**, atau jalankan `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage** : membuatnya dapat dieksekusi dengan `chmod +x AMSO*.AppImage`.
- **Jika ada masalah**, mohon kirimkan file `startup.log` dan `crash.log` (jika ada) yang terletak di folder data: `~/Library/Application Support/AMSO/` di macOS, `~/.local/share/AMSO/` di Linux. Sebutkan sistem dan versi VLC Anda.

---

## 🧪 Peluncuran tes

Proyek ini menggunakan `pytest` dengan rangkaian tes unit dan integrasi :

```bash
pytest -v
```

Pengujian berjalan secara otomatis pada **Windows, macOS dan Ubuntu** setiap kali ada *push* melalui GitHub Actions.

---

## 🔒 Keamanan & Kunci API

- **Jangan pernah memasukkan kunci API atau token otentikasi nyata.**
- File `.gitignore` sudah dikonfigurasi sebelumnya untuk memblokir `.env`, `credentials.json`, `token.json`, dan semua basis data SQLite lokal.
- Gunakan `.env.example` sebagai model untuk lingkungan pengembangan Anda.

---

## 📋 Dokumentasi & Pemantauan proyek

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Catatan rinci versi, fitur baru, dan perbaikan bug.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Peta jalan tonggak masa depan (Artis, Cloud, Spotify, Penghapusan Duplikasi).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Piagam arsitektur perangkat lunak dan aturan kualitas kode.

---

## 💖 Mendukung proyek & Distribusi

AMSO adalah perangkat lunak bebas dan gratis (open source). Jika Anda menyukai aplikasi ini dan ingin mendukung pengembangannya:

- 🎮 **Unduhan & Pay What You Want :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (aplikasi yang sudah dikompilasi dan siap digunakan)
- ☕ **Donasi langsung :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [Sponsor LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Lisensi

Proyek ini berada di bawah lisensi **GNU General Public License v3.0 (GPL-3.0)** — silakan lihat berkas [LICENSE](../../LICENSE) untuk detail lebih lanjut.
