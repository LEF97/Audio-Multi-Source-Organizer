# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <a href="README.el.md">Ελληνικά</a> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <b>한국어</b> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer)는 현대적이고 반응성이 뛰어나며 다중 플랫폼(Windows, Linux, macOS)을 지원하는 데스크톱 오디오 플레이어입니다. 오디오 애호가들에게 로컬 음악 라이브러리(MP3, FLAC, OGG…)에 대한 완벽한 제어를 제공하도록 설계되었으며, 이제는 재생 목록(M3U, PLS, XSPF, WPL), CUE 시트(트랙으로 분할된 단일 파일 앨범)를 지원하고 완전히 새로운 블라인드 테스트 오디오 모드를 통합했습니다! 이 프로젝트는 로컬 디스크, 클라우드 스토리지 (Google Drive), 스트리밍 서비스 (Spotify, Deezer, Amazon Music)에 분산된 하이브리드 음악 컬렉션을 정리하고, 중복을 제거하며, 동기화할 수 있는 통합 제어 센터로 발전하고 있습니다.

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

## 📌 기능 및 프로젝트 상태

| 기능 | 설명 | 상태 |
| :--- | :---: | :---: |
| **통합 VLC 플레이어** | 휴대용 VLC 자동 설치 및 부드러운 볼륨 관리가 가능한 가볍고 독립적인 오디오 플레이어 | 🟢 구현됨 |
| **멀티스레드 로컬 스캐너** | 로컬 오디오 파일(MP3, FLAC, AAC, OGG...)의 빠르고 재귀적인 검색 | 🟢 구현됨 |
| **메타데이터 추출** | ID3, Vorbis Comments 읽기/쓰기 및 오디오 지문 계산 (`mutagen`) | 🟢 구현됨 |
| **플레이리스트 지원 (M3U, PLS, XSPF, WPL) 및 CUE 시트** | 트리 인덱싱 (🎶), 순차적 청취 순서, 누락된 트랙 시각적 식별; `.cue` 파일 (💿)은 길이와 함께 가상 트랙 폴더처럼 열리고 실제 트랙처럼 재생됩니다 | 🟢 구현됨 |
| **플레이리스트 관리자 및 드래그 앤 드롭** | 가상 대기열, 부드러운 드래그 앤 드롭, 되돌릴 수 있는 무작위 재생(shuffle) 및 루프 | 🟢 구현됨 |
| **« 🎲 블라인드 테스트 » 인터랙티브 모드** | 애니메이션 카운트다운, 사운드 페이드, 부드러운 공개 및 자동 연결이 있는 몰입형 음악 게임 | 🟢 구현됨 |
| **인앱 업데이트** | GitHub Releases를 통한 자동/수동 버전 확인 | 🟢 구현됨 |
| **아티스트 및 디스코그래피 관리** | 앨범, 싱글 및 전체 디스코그래피가 포함된 아티스트 전용 보기 | 🟡 예정 |
| **그래픽 이퀄라이저 (EQ)** | 오디오 프리셋 및 파라메트릭 멀티밴드 이퀄라이저 | 🟡 예정 |
| **Google Drive 커넥터** | OAuth 2.0을 통한 원격 오디오 컬렉션 스캔 및 동기화 | ⚪ 계획 |
| **Amazon Music 커넥터** | OAuth 2.0을 통한 원격 컬렉션 스캔 및 동기화 | ⚪ 계획 |
| **Spotify / Deezer 커넥터** | 플레이리스트 가져오기 및 트랙 매칭 | ⚪ 계획 |
| **스마트 중복 제거** | 중복 감지 (퍼지 제목/아티스트 + 음향 지문) | ⚪ 계획 |

> 💡 *계획된 마일스톤 및 버전에 대한 자세한 내용은 [로드맵 (Roadmap)](../../ROADMAP.md)을 참조하십시오.*

---

## 📌 지원 언어

영어, 프랑스어, 스페인어, 독일어, 이탈리아어, 포르투갈어, 일본어, 러시아어, 폴란드어, 터키어, 네덜란드어, 스웨덴어, 인도네시아어, 불가리아어, 세르비아어, 벨라루스어, 그리스어, 카탈루냐어, 바스크어, 갈리시아어, 체코어, 슬로바키아어, 헝가리어, 크로아티아어, 슬로베니아어, 보스니아어, 에스토니아어, 라트비아어, 리투아니아어, 노르웨이어, 덴마크어, 핀란드어, 아이슬란드어, 말레이어, 타갈로그어, 스와힐리어, 에스페란토어, 중국어(간체), 중국어(번체), 한국어, 아랍어, 히브리어, 베트남어

---

## 🚀 빠른 시작

### 필수 준비물

- **Python 3.11** 이상 설치
- Git

### 설치

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

## 🧪 테스트 시작

이 프로젝트는 단위 및 통합 테스트 스위트로 `pytest`를 사용합니다:

```bash
pytest -v
```

테스트는 GitHub Actions를 통해 푸시할 때마다 **Windows, macOS 및 Ubuntu**에서 자동으로 실행됩니다.

---

## 🔒 보안 및 API 키

- **실제 API 키나 인증 토큰을 절대 커밋하지 마세요.**
- `.gitignore` 파일은 `.env`, `credentials.json`, `token.json` 및 모든 로컬 SQLite 데이터베이스를 차단하도록 사전 구성되어 있습니다.
- 개발 환경의 템플릿으로 `.env.example`을 사용하세요.

---

## 📋 문서 및 프로젝트 진행 상황

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : 버전, 새로운 기능 및 버그 수정에 대한 상세한 기록.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : 향후 마일스톤(아티스트, 클라우드, Spotify, 중복 제거) 로드맵.
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : 소프트웨어 아키텍처 헌장 및 코드 품질 규칙.

---

## 💖 프로젝트 지원 및 배포

AMSO는 자유롭고 무료인 소프트웨어입니다 (open source). 이 애플리케이션이 마음에 드시고 개발을 지원하고 싶으시다면:

- 🎮 **다운로드 및 원하는 만큼 지불 :** [AMSO의 Itch.io 페이지](https://lef97.itch.io/audio-multi-source-organizer) (바로 사용 가능한 미리 컴파일된 실행 파일)
- ☕ **직접 기부하기 :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub 후원 :** [LEF97 후원하기](https://github.com/sponsors/LEF97)

---

## 📄 라이선스

이 프로젝트는 **GNU General Public License v3.0 (GPL-3.0)** 라이선스 하에 있습니다. — 자세한 내용은 [LICENSE](../../LICENSE) 파일을 참조하십시오.
