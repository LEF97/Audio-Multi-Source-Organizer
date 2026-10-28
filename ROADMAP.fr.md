# Feuille de route (Roadmap) — AMSO

<p align="right">
  <b>Français</b> • <a href="ROADMAP.md">English</a> • <a href="docs/i18n/ROADMAP.es.md">Español</a> • <a href="docs/i18n/ROADMAP.de.md">Deutsch</a> • <a href="docs/i18n/ROADMAP.it.md">Italiano</a>
</p>

---

Ce document détaille les orientations stratégiques, les fonctionnalités planifiées et les jalons futurs du projet **Audio Multi-Source Organizer (AMSO)**.

---

## 🎯 Vision du projet

AMSO a pour vocation de devenir le **hub musical universel et décentralisé** de référence : une application rapide, légère, élégante et sans compromis sur la vie privée, permettant à chacun de maîtriser sa collection audio qu'elle soit stockée sur disque dur, archivée dans le cloud ou consultée sur les services de streaming.

---

## 🗺️ Jalons et Versions

### 🟢 Version 0.1.0 — Le Socle Local Robuste
- [x] Scanner local multithreadé avec extraction des métadonnées (ID3, Vorbis Comments, FLAC).
- [x] Moteur de lecture audio intégré (python-vlc) avec auto-installation VLC portable.
- [x] Vue Playlist complète avec réorganisation glisser-déposer, lecture aléatoire et boucles.
- [x] Sauvegarde automatique de la session de lecture (position, volume, liste).
- [x] Interface moderne en Dark Mode avec effets visuels réactifs.
- [x] Internationalisation complète (FR, EN, ES, DE, IT).
- [x] Système de notification et vérification de mises à jour via GitHub Releases.

---

### 🟢 Version 0.2.0 — Mode Blind Test, Corbeille & Ergonomie
- [x] **Mode « 🎲 Jeux / Blind Test » immersif :** Décompte avec pulsation animée, révélation progressive en fondu doux, enchaînement automatique et paramètres dédiés.
- [x] **Gestion de la Corbeille & Restauration :** Exclusion de morceaux, envoi vers la corbeille Windows et vue dédiée Corbeille AMSO avec restauration instantanée dans la bibliothèque.
- [x] **Refonte du mode Aléatoire (Shuffle) & Glisser-Déposer :** Mélange visuel intégral, ordre réversible et réorganisation de la playlist à la souris.
- [x] **Optimisations de performances et persistance :** Format de sauvegarde compact asynchrone (-99 % d'espace disque) et élimination des latences au démarrage.
- [x] **Ergonomie du Lecteur & Navigation :** Nouveau tiroir « Jeux », curseur de volume intégré dans l'en-tête du Lecteur, démarrage par défaut sur le Lecteur.

---

### 🟢 Version 0.3.0 — Support des Playlists, Fondu Audio & Robustesse
- [x] **Prise en charge intégrale des playlists :** Indexation automatique des formats `.m3u`, `.m3u8`, `.pls`, `.xspf`, `.wpl` dans la vue par dossier avec l'icône `🎶`.
- [x] **Ordre séquentiel et gestion des morceaux manquants :** Respect de l'ordre d'origine de la playlist et détection visuelle des fichiers manquants (`⚠️`) sans interruption de lecture.
- [x] **Fondu sonore acoustique (*Fade-in*) :** Montée progressive du volume sur 1 seconde au démarrage et à la reprise d'une lecture audio.
- [x] **Fluidité de la synchronisation :** File d'attente continue en arrière-plan sans pop-up intrusive et préservation de l'arbre des dossiers.
- [x] **Ajustement dynamique des pochettes :** Recentrage et dimensionnement fluide lors du passage plein écran / fenêtré.

---

### 🟢 Version 0.4.0 — Expérience Audio Avancée & Feuilles CUE *(Actuel)*
- [x] **Refonte modulaire de l'architecture & Quality Gate :** Découpage de l'application en modules cohésifs (< 500 lignes), modularisation de MainWindow en mixins dédiés (amso/ui/pages/), décomposition du service audio en sous-systèmes indépendants (player_transport, player_queue, player_transitions) et mise en place d'un harnais de validation automatisé (scripts/verify.py & .bat : ruff, mypy, pytest, contrôle des tailles).
- [x] **Intégration Windows Shell & barre des tâches :** Épinglage natif direct depuis l'icône active (AppUserModelID explicite LEF97.AMSO.AudioPlayer) dès le point d'entrée main.py et persistance du raccourci lors des mises à jour.
- [x] **Ecoute parfaite Gapless 0 entre deux pistes :** 2 moteurs sont désormais disponibles, un basé sur VLC_direct, l'autre fonctionnant en mode buffer (fonctionnement privilégié). Ces modes permettent une écoute fluide sur les albums avec pistes liés (Alan Parsons, Pink Floyd, Mike Oldfield, etc...)
- [x] **Prise en charge des feuilles CUE (`.cue`) :** Un fichier `.cue` s'affiche comme un dossier de pistes virtuelles (💿) avec leur durée et se lit comme de vraies pistes (moteur à tampon continu).

---

### 🔵 Version 0.4.1 — Packaging Linux & macOS
- [ ] **Déploiement multiplateforme automatisé (Linux & macOS) :** Compilation native et packaging automatisé via GitHub Actions pour Linux (.AppImage / .tar.gz) et macOS Apple Silicon ARM & Intel (.dmg), en complément de l'exécutable Windows.

---

### 🔵 Version 0.4.2 — Compatibilité réseau Linux & macOS
- [ ] **Détection des montages réseau (Linux & macOS) :** `amso/core/network_paths.py` ne reconnaît aujourd'hui que les chemins UNC et les lecteurs mappés Windows ; reconnaître les montages NFS / SMB / AFP (`/proc/self/mountinfo`, `statfs`) pour éviter tout sondage disque bloquant au démarrage sur ces systèmes.

---

### 🌟 Version x.0.0 — Dédoublonnage Intelligent & Version Stable
- [ ] **Détection acoustique d'empreinte (Audio Fingerprinting) :** Identification des doublons même en cas de tags erronés ou de fichiers ré-encodés.
- [ ] **Assistant de résolution des doublons :** Comparaison intelligente de qualité (sélection automatique du meilleur bitrate / lossless) avec archivage sécurisé.
- [ ] **Packaging multiplateforme officiel :** Exécutables signés pour Windows (`.exe` / portable), macOS (`.dmg` Apple Silicon & Intel) et Linux (`AppImage` / `.deb`).
- [ ] **Documentation utilisateur complète :** Guide pas-à-pas illustré et site vitrine GitHub Pages.
- [ ] **Connecteur Spotify (Web API) :** Connexion du compte utilisateur et récupération des playlists et favoris.
- [ ] **Connecteur Amazon Music :** Scan, streaming et synchronisation de collections musicales distantes (OAuth 2.0).
- [ ] **Matching hybride intelligent :** Correspondance entre les titres d'une playlist distante et les fichiers déjà présents en local (haute fidélité).
- [ ] **Vue unifiée :** Affichage côte à côte des pistes disponibles en local et de celles disponibles uniquement en streaming.
- [ ] **Authentification sécurisée OAuth 2.0 :** Connexion simplifiée via le navigateur sans stocker de secrets en clair.
- [ ] **Scan distant des dossiers Google Drive :** Indexation des fichiers audio présents dans les dossiers configurés.
- [ ] **Lecture directe en streaming cloud :** Écoute des morceaux distants avec mise en cache locale transparente.
- [ ] **Synchronisation bidirectionnelle sélective :** Téléchargement local de pistes du cloud ou sauvegarde de pistes locales vers Drive.
- [ ] **Gestion des artistes et discographie associée :** Vue dédiée par artiste avec albums, singles et discographie complète.
- [ ] **Égaliseur graphique (EQ) :** Presets (Rock, Pop, Jazz, Bass Boost) et égaliseur paramétrique multibandes.
- [ ] **Éditeur de métadonnées in-app :** Modification directe des tags ID3 / Vorbis sur un ou plusieurs fichiers sélectionnés.
- [ ] **Téléchargement automatique de pochettes :** Recherche en ligne (MusicBrainz / Cover Art Archive) des jaquettes manquantes.
- [ ] **Filtres de recherche avancés :** Filtrage combiné par genre, année, débit binaire (bitrate) et format sans perte (Lossless).
- [x] **Crossfade paramétrable & Enchaînements audio avancés :** Prise en charge des transitions sans coupure (Gapless 0 ms), du fondu enchaîné haute précision (Crossfade Equal-Power) et du mode standard sans blanc.

---

## 💡 Proposer une fonctionnalité

Une idée ou un besoin spécifique ?
- Ouvrez une discussion ou un ticket sur [GitHub Issues](https://github.com/LEF97/Audio-Multi-Source-Organizer/issues) en utilisant le modèle *Feature Request*.
- Participez aux votes communautaires pour prioriser les développements !
