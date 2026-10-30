# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <b>Türkçe</b> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer), modern, reaktif ve çok platformlu bir masaüstü ses oynatıcısıdır (Windows, Linux, macOS). Audiophile'lara yerel müzik kütüphaneleri (MP3, FLAC, OGG…) üzerinde tam kontrol sağlamak üzere tasarlanmıştır; artık çalma listelerini (M3U, PLS, XSPF, WPL), CUE dosyalarını (parçalara ayrılmış tek dosyalık albümler) destekliyor ve yepyeni bir ses kör testi modu entegre ediyor! Proje, yerel diskler, bulut depolama (Google Drive) ve yayın hizmetleri (Spotify, Deezer, Amazon Music) arasında dağılmış hibrit müzik koleksiyonlarını düzenleyebilen, yinelenen öğeleri kaldırabilen ve senkronize edebilen birleşik bir komuta merkezine dönüşüyor.

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

## 📌 Özellikler & Proje Durumu

| Özellik | Açıklama | Durum |
| :--- | :---: | :---: |
| **Ses Çalma Motoru** | Hafif ve bağımsız ses oynatıcı (Windows altında otomatik yüklenen VLC portable). Seçenekli iki motor: doğrudan VLC çıkışı veya iki parça arasında akıcı geçiş için sürekli tampon motoru (Gapless 0 ms, eşit güce sahip geçiş, ses çıkışında kesinti yok) | 🟢 Uygulanmış |
| **Kütüphane Yönetimi** | Yerel klasörlerin özyinelemeli çok iş parçacıklı taraması (MP3, FLAC, AAC, OGG...), manuel, planlanmış veya gerçek zamanlı senkronizasyon, çöp kutusu ve kütüphane istatistikleri | 🟢 Uygulanmış |
| **Meta Veri Çıkarma** | ID3, Vorbis Comments okuma/yazma ve ses parmak izi hesaplama (`mutagen`) | 🟢 Uygulanmış |
| **Playlist Desteği (M3U, PLS, XSPF, WPL) & CUE dosyaları** | Ağaç yapısı indeksleme (🎶), sıralı dinleme sırası, eksik parçaların görsel tespiti; `.cue` dosyaları (💿) süresiyle birlikte sanal bir parça klasörü gibi açılır ve gerçek parçalar gibi çalınır | 🟢 Uygulanmış |
| **Çalma Listesi Yöneticisi & Sürükle-Bırak** | Sanallaştırılmış kuyruk, akıcı sürükle-bırak, geri alınabilir rastgele (shuffle) ve döngüler | 🟢 Uygulanmış |
| **Etkileşimli "🎲 Kör Test" Modu** | Animasyonlu sayaç, ses geçişi, yumuşak ortaya çıkarma ve otomatik sıralama içeren sürükleyici müzik oyunu | 🟢 Uygulanmış |
| **Uygulama içi güncellemeler** | GitHub Releases üzerinden otomatik/manuel sürüm kontrolü | 🟢 Uygulandı |
| **Linux ve macOS Sürümleri** | `.AppImage` / `.tar.gz` (Linux) ve imzalanmamış `.dmg` (macOS) paketleri, VLC gerekli | 🟡 Deneysel (test edilmedi) |
| **Sanatçı ve Diskografi Yönetimi** | Albümler, single'lar ve tam diskografi ile sanatçıya özel görünüm | 🟡 Planlanıyor |
| **Grafik Ekolayzır (EQ)** | Ses ön ayarları ve parametrik çok bantlı ekolayzır | 🟡 Planlanıyor |
| **Google Drive Bağlayıcısı** | OAuth 2.0 üzerinden uzaktaki ses koleksiyonlarının taranması ve senkronizasyonu | ⚪ Planlandı |
| **Amazon Music Bağlayıcısı** | OAuth 2.0 üzerinden uzaktaki koleksiyonların taranması ve senkronizasyonu | ⚪ Planlandı |
| **Spotify / Deezer Bağlayıcısı** | Çalma listelerinin içe aktarılması ve parça eşleştirme | ⚪ Planlandı |
| **Akıllı Yinelenme Kaldırma** | Dublikat algılama (başlık/sanatçı bulanık + akustik parmak izleri) | ⚪ Planlandı |

> 💡 *Planlanan kilometre taşları ve sürümlerin ayrıntılarını görmek için, [Yol Haritası (Roadmap)](../../ROADMAP.md)'e bakın.*

---

## 📌 Mevcut diller

İngilizce, Fransızca, İspanyolca, Almanca, İtalyanca, Portekizce, Japonca, Rusça, Lehçe, Türkçe, Felemenkçe, İsveççe, Endonezyaca, Bulgarca, Sırpça, Beyaz Rusça, Yunanca, Katalanca, Baskça, Galicece, Çekçe, Slovakça, Macarca, Hırvatça, Slovençe, Bosna-Hersekçe, Estonca, Letonca, Litvanyaca, Norveççe, Danca, Fince, İzlandaca, Malayca, Tagalogca, Swahili, Esperanto, Basitleştirilmiş Çince, Geleneksel Çince, Korece, Arapça, İbranice, Vietnamca

---

## 🚀 Hızlı başlangıç

### Ön koşullar

- **Python 3.11** veya üzeri kurulu
- Git

### Kurulum

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

## 🐧🍎 Linux ve macOS: deneme sürümleri (test edilmemiş)

Linux paketleri (`.AppImage` / `.tar.gz`) ve macOS (`.dmg`) **test edilmemiş olarak** sağlanmıştır: AMSO yalnızca Windows altında doğrulanmıştır. Özellikle sürekli tamponlu (`buffer`) ses motoru bu sistemlerde kontrol edilmemiştir. Geri bildiriminiz değerlidir.

- **VLC gereklidir** (AMSO sadece Windows'ta indirir) :
  - Linux : `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) veya `sudo pacman -S vlc` (Arch).
  - macOS : Applications klasöründeki [videolan.org](https://www.videolan.org/vlc/) adresinden **VLC.app** kurun.
- **Linux, sistem kütüphaneleri** : Qt arayüzü özellikle `libpulse0` (ses), `libxcb-cursor0` ve `libxkbcommon-x11-0` talep eder (örneğin `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, imzalanmamış `.dmg`** : ilk çalıştırmada, AMSO üzerine sağ tıklayıp **Aç** yapın veya `xattr -dr com.apple.quarantine /Applications/AMSO.app` komutunu çalıştırın.
- **Linux, AppImage** : çalıştırılabilir yapmak için `chmod +x AMSO*.AppImage` kullanın.
- **Bir sorun olması durumunda**, lütfen veri klasöründe bulunan `startup.log` ve `crash.log` dosyalarını (varsa) gönderin: macOS'ta `~/Library/Application Support/AMSO/` altında, Linux'ta `~/.local/share/AMSO/` altında. Sisteminizi ve VLC sürümünüzü belirtin.

---

## 🧪 Testlerin başlatılması

Proje, birim ve entegrasyon testleri için `pytest` kullanır:

```bash
pytest -v
```

Testler otomatik olarak **Windows, macOS ve Ubuntu** üzerinde, GitHub Actions aracılığıyla her push'ta çalışır.

---

## 🔒 Güvenlik & API Anahtarları

- **API anahtarlarını veya gerçek kimlik doğrulama jetonlarını asla commit etmeyin.**
- `.gitignore` dosyası, `.env`, `credentials.json`, `token.json` ve tüm yerel SQLite veritabanlarını engellemek için önceden yapılandırılmıştır.
- Geliştirme ortamınız için şablon olarak `.env.example` kullanın.

---

## 📋 Dokümantasyon & Proje Takibi

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Sürümlerin, yeni özelliklerin ve hata düzeltmelerinin ayrıntılı günlüğü.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Gelecekteki kilometre taşlarının yol haritası (Artistes, Cloud, Spotify, Yinelenmeyi Kaldırma).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Yazılım mimarisi şartı ve kod kalitesi kuralları.

---

## 💖 Projeyi desteklemek & Dağıtım

AMSO ücretsiz ve açık kaynaklı bir yazılımdır (open source). Uygulamayı beğenirseniz ve geliştirilmesini desteklemek isterseniz:

- 🎮 **İndirme & İstediğin Kadar Öde :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (kullanıma hazır önceden derlenmiş çalıştırılabilir dosya)
- ☕ **Doğrudan bağış yapmak :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [LEF97'i Sponsor Yapmak](https://github.com/sponsors/LEF97)

---

## 📄 Lisans

Bu proje **GNU General Public License v3.0 (GPL-3.0)** lisansı altındadır — daha fazla ayrıntı için [LICENSE](../../LICENSE) dosyasına bakın.
