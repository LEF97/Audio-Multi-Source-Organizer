# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <b>Bahasa Melayu</b> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) ialah pemain audio desktop moden, responsif, dan pelbagai platform (Windows, Linux, macOS). Direka untuk memberikan audiophile kawalan total ke atas perpustakaan muzik tempatan mereka (MP3, FLAC, OGG…), ia kini menyokong senarai main (M3U, PLS, XSPF, WPL), helaian CUE (album fail tunggal yang dipotong kepada trek) dan menyepadukan mod ujian buta audio yang baharu! Projek ini berkembang menjadi pusat kawalan bersepadu yang mampu mengatur, menghilangkan duplikasi, dan menyegerakkan koleksi muzik hibrid yang diedarkan antara cakera tempatan, storan awan (Google Drive) dan perkhidmatan penstriman (Spotify, Deezer, Amazon Music).

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

## 📌 Ciri-ciri & Status Projek

| Ciri | Penerangan | Status |
| :--- | :---: | :---: |
| **Enjin pemain VLC bersepadu** | Pemain audio ringan dan mandiri dengan pemasangan auto VLC portable dan pengurusan volume yang lancar | 🟢 Implémenté |
| **Pengimbas tempatan multithread** | Penemuan rekursif dan pantas fail audio tempatan (MP3, FLAC, AAC, OGG...) | 🟢 Implémenté |
| **Ekstraksi metadata** | Baca/tulis ID3, Vorbis Comments dan pengiraan cap jari audio (`mutagen`) | 🟢 Implémenté |
| **Sokongan Senarai Main (M3U, PLS, XSPF, WPL) & lembaran CUE** | Pengindeksan pokok (🎶), susunan mendengar berurutan, pengenalpastian visual trek yang hilang; fail `.cue` (💿) dibuka seperti folder trek maya dengan tempohnya dan dimainkan seperti trek sebenar | 🟢 Implémenté |
| **Pengurus Senarai Main & Seret-Lepas** | Barisan menunggu yang divirtualkan, seret & lepas yang lancar, rawak (shuffle) boleh diterbalikkan dan gelung | 🟢 Implémenté |
| **Mod "🎲 Blind Test" interaktif** | Permainan muzik imersif dengan kira detik animasi, pudar bunyi, pendedahan lembut dan penyambungan automatik | 🟢 Implémenté |
| **Kemas kini dalam aplikasi** | Pengesahan versi automatik/manual melalui GitHub Releases | 🟢 Dilaksanakan |
| **Pengurusan artis & Diskografi** | Paparan khusus mengikut artis dengan album, single, dan diskografi lengkap | 🟡 Dirancang |
| **Equalizer grafik (EQ)** | Preset audio dan equalizer multiband parametrik | 🟡 Dirancang |
| **Penyambung Google Drive** | Imbasan dan penyegerakan koleksi audio jarak jauh melalui OAuth 2.0 | ⚪ Dirancang |
| **Penyambung Amazon Music** | Imbasan dan penyegerakan koleksi jarak jauh melalui OAuth 2.0 | ⚪ Dirancang |
| **Penyambung Spotify / Deezer** | Import senarai main dan padanan trek | ⚪ Dirancang |
| **Penghapusan duplikat pintar** | Pengesanan duplikat (tajuk/artis kabur + cap jari akustik) | ⚪ Dirancang |

> 💡 *Untuk melihat perincian pencapaian dan versi yang dirancang, sila rujuk kepada [Feuille de route (Roadmap)](../../ROADMAP.md).*

---

## 📌 Bahasa yang tersedia

Inggeris, Perancis, Sepanyol, Jerman, Itali, Portugis, Jepun, Rusia, Poland, Turki, Belanda, Sweden, Indonesia, Bulgaria, Serbia, Belarus, Greek, Catalan, Basque, Galisia, Czech, Slovakia, Hungary, Croatia, Slovenia, Bosnia, Estonia, Latvia, Lithuania, Norway, Denmark, Finland, Iceland, Melayu, Tagalog, Swahili, Esperanto, Cina Ringkas, Cina Tradisional, Korea, Arab, Ibrani, Vietnam

---

## 🚀 Permulaan pantas

### Prasyarat

- **Python 3.11** atau lebih tinggi dipasang
- Git

### Pemasangan

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

## 🧪 Pelancaran ujian

Projek ini menggunakan `pytest` dengan set ujian unit dan integrasi :

```bash
pytest -v
```

Ujian dijalankan secara automatik pada **Windows, macOS et Ubuntu** pada setiap tolak melalui GitHub Actions.

---

## 🔒 Keselamatan & Kunci API

- **Jangan pernah commit kunci API atau token pengesahan sebenar.**
- Fail `.gitignore` telah dikonfigurasi awal untuk menyekat `.env`, `credentials.json`, `token.json` dan semua pangkalan data SQLite tempatan.
- Gunakan `.env.example` sebagai templat untuk persekitaran pembangunan anda.

---

## 📋 Dokumentasi & Pemantauan Projek

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Log terperinci versi, ciri baharu, dan pembetulan pepijat.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Pelan jalan untuk pencapaian masa depan (Artis, Cloud, Spotify, Penghapusan Duplikat).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Piagam seni bina perisian dan peraturan kualiti kod.

---

## 💖 Menyokong projek & Pengedaran

AMSO adalah perisian bebas dan percuma (open source). Jika anda menghargai aplikasi ini dan ingin menyokong perkembangannya:

- 🎮 **Muat Turun & Bayar Apa Yang Anda Mahu :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (executable pra-kompilasi sedia untuk digunakan)
- ☕ **Derma terus :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **Penaja GitHub :** [Sponsor LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Lesen

Projek ini di bawah lesen **GNU General Public License v3.0 (GPL-3.0)** — rujuk fail [LICENSE](../../LICENSE) untuk butiran lanjut.
