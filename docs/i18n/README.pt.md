# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <b>Português</b> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
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

> **AMSO** (Audio Multi-Source Organizer) é um reprodutor de áudio de desktop moderno, responsivo e multiplataforma (Windows, Linux, macOS). Projetado para oferecer aos audiófilos um controle total sobre sua biblioteca musical local (MP3, FLAC, OGG…), ele agora suporta playlists (M3U, PLS, XSPF, WPL), arquivos CUE (álbuns de um único arquivo divididos em faixas) e integra um modo de teste cego de áudio totalmente novo! O projeto está evoluindo para se tornar um centro de comando unificado capaz de organizar, desduplicar e sincronizar coleções musicais híbridas distribuídas entre discos locais, armazenamento em nuvem (Google Drive) e serviços de streaming (Spotify, Deezer, Amazon Music).

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

## 📌 Funcionalidades & Status do projeto

| Funcionalidade | Descrição | Status |
| :--- | :---: | :---: |
| **Motor de reprodução de áudio** | Player de áudio leve e autônomo (VLC portátil instalado automaticamente sob Windows). Dois motores à escolha: saída direta VLC, ou motor de buffer contínuo para uma transição suave entre duas faixas (Gapless 0 ms, fade de potência igual, sem interrupção da saída de áudio) | 🟢 Implementado |
| **Gerenciamento de biblioteca** | Scan recursivo multithread de pastas locais (MP3, FLAC, AAC, OGG...), sincronização manual, agendada ou em tempo real, lixeira e estatísticas da biblioteca | 🟢 Implementado |
| **Extração de metadados** | Leitura/escrita ID3, Vorbis Comments e cálculo de impressão digital de áudio (`mutagen`) | 🟢 Implementado |
| **Suporte a Playlists (M3U, PLS, XSPF, WPL) & folhas CUE** | Indexação em árvore (🎶), ordem de escuta sequencial, localização visual de faixas ausentes; os arquivos `.cue` (💿) abrem como uma pasta de faixas virtuais com sua duração e são reproduzidos como faixas reais | 🟢 Implementado |
| **Gerenciador de Playlist & Arrastar-Soltar** | Fila de reprodução virtualizada, drag & drop fluido, aleatório (shuffle) reversível e loops | 🟢 Implementado |
| **Modo interativo « 🎲 Blind Test »** | Jogo musical imersivo com contagem regressiva animada, fade sonoro, revelação suave e sequência automática | 🟢 Implementado |
| **Atualizações no aplicativo** | Verificação automática/manual de versões via GitHub Releases | 🟢 Implementado |
| **Versões Linux & macOS** | Pacotes `.AppImage` / `.tar.gz` (Linux) e `.dmg` não assinado (macOS), VLC necessário | 🟡 Experimental (não testado) |
| **Gerenciamento de artistas & Discografia** | Visualização dedicada por artista com álbuns, singles e discografia completa | 🟡 Planejado |
| **Equalizador gráfico (EQ)** | Presets de áudio e equalizador multibanda paramétrico | 🟡 Planejado |
| **Conector Google Drive** | Scan e sincronização de coleções de áudio remotas via OAuth 2.0 | ⚪ Planejado |
| **Conector Amazon Music** | Scan e sincronização de coleções remotas via OAuth 2.0 | ⚪ Planejado |
| **Conector Spotify / Deezer** | Importação de playlists e correspondência de faixas | ⚪ Planejado |
| **Desduplicação inteligente** | Detecção de duplicatas (título/artista desfocados + impressões acústicas) | ⚪ Planejado |

> 💡 *Para consultar o detalhe dos marcos e versões previstas, consulte [Roteiro (Roadmap)](../../ROADMAP.md).*

---

## 📌 Idiomas disponíveis

Inglês, Francês, Espanhol, Alemão, Italiano, Português, Japonês, Russo, Polonês, Turco, Neerlandês, Sueco, Indonésio, Búlgaro, Sérvio, Bielorrusso, Grego, Catalão, Basco, Galego, Tcheco, Eslovaco, Húngaro, Croata, Esloveno, Bósnio, Estoniano, Letão, Lituano, Norueguês, Dinamarquês, Finlandês, Islandês, Malaio, Tagalo, Swahili, Esperanto, Chinês simplificado, Chinês tradicional, Coreano, Árabe, Hebraico, Vietnamita

---

## 🚀 Início rápido

### Pré-requisitos

- **Python 3.11** ou superior instalado
- Git

### Instalação

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

## 🐧🍎 Linux e macOS : versões experimentais (não testadas)

Os pacotes Linux (`.AppImage` / `.tar.gz`) e macOS (`.dmg`) são fornecidos **sem terem sido testados**: AMSO foi validado apenas no Windows. O motor de áudio de buffer contínuo (`buffer`) em particular não foi verificado nestes sistemas. Seu feedback é valioso.

- **VLC é necessário** (AMSO só o baixa sob Windows) :
  - Linux : `sudo apt install vlc` (Debian / Ubuntu), `sudo dnf install vlc` (Fedora) ou `sudo pacman -S vlc` (Arch).
  - macOS : instalar **VLC.app** desde [videolan.org](https://www.videolan.org/vlc/) no diretório Applications.
- **Linux, bibliotecas do sistema** : a interface Qt exige, em particular, `libpulse0` (som), `libxcb-cursor0` e `libxkbcommon-x11-0` (por exemplo `sudo apt install libpulse0 libxcb-cursor0 libxkbcommon-x11-0`).
- **macOS, `.dmg` não assinado** : no primeiro lançamento, clique com o botão direito em AMSO e depois **Abrir**, ou execute `xattr -dr com.apple.quarantine /Applications/AMSO.app`.
- **Linux, AppImage** : torná-lo executável com `chmod +x AMSO*.AppImage`.
- **Em caso de problema**, por favor, envie os arquivos `startup.log` e `crash.log` (se existirem) localizados no diretório de dados: `~/Library/Application Support/AMSO/` no macOS, `~/.local/share/AMSO/` no Linux. Especifique seu sistema e a versão do VLC.

---

## 🧪 Lançamento dos testes

O projeto utiliza `pytest` com um conjunto de testes unitários e de integração:

```bash
pytest -v
```

Os testes são executados automaticamente em **Windows, macOS e Ubuntu** a cada push via GitHub Actions.

---

## 🔒 Segurança & Chaves de API

- **Nunca commitem chaves de API nem tokens de autenticação reais.**
- O arquivo `.gitignore` está pré-configurado para bloquear `.env`, `credentials.json`, `token.json` e todos os bancos de dados SQLite locais.
- Use `.env.example` como modelo para seu ambiente de desenvolvimento.

---

## 📋 Documentação & Acompanhamento do projeto

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Diário detalhado das versões, novos recursos e correções de bugs.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Roteiro dos futuros marcos (Artistas, Cloud, Spotify, Desduplicação).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Carta de arquitetura de software e regras de qualidade de código.

---

## 💖 Apoiar o projeto & Distribuição

AMSO é um software livre e gratuito (open source). Se você aprecia o aplicativo e deseja incentivar seu desenvolvimento:

- 🎮 **Download & Pay What You Want :** [Página Itch.io do AMSO](https://lef97.itch.io/audio-multi-source-organizer) (executável pré-compilado pronto para uso)
- ☕ **Fazer uma doação direta :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [Patrocinar LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Licença

Este projeto está sob licença **GNU General Public License v3.0 (GPL-3.0)** — consulte o arquivo [LICENSE](../../LICENSE) para mais detalhes.
