# Feuille de route (Roadmap) — AMSO

<p align="right">
  <b>Français</b> • <a href="ROADMAP.md">English</a> • <a href="ROADMAP.es.md">Español</a> • <a href="ROADMAP.de.md">Deutsch</a> • <a href="ROADMAP.it.md">Italiano</a>
</p>

---

Ce document détaille les orientations stratégiques, les fonctionnalités planifiées et les jalons futurs du projet **Audio Multi-Source Organizer (AMSO)**.

---

## 🎯 Vision du projet

AMSO a pour vocation de devenir le **hub musical universel et décentralisé** de référence : une application rapide, légère, élégante et sans compromis sur la vie privée, permettant à chacun de maîtriser sa collection audio qu'elle soit stockée sur disque dur, archivée dans le cloud ou consultée sur les services de streaming.

---

## 🗺️ Jalons et Versions

### 🟢 Version 0.1.0 — Le Socle Local Robuste *(Actuel)*
- [x] Scanner local multithreadé avec extraction des métadonnées (ID3, Vorbis Comments, FLAC).
- [x] Moteur de lecture audio intégré (python-vlc) avec auto-installation VLC portable.
- [x] Vue Playlist complète avec réorganisation glisser-déposer, lecture aléatoire et boucles.
- [x] Sauvegarde automatique de la session de lecture (position, volume, liste).
- [x] Interface moderne en Dark Mode avec effets visuels réactifs.
- [x] Internationalisation complète (FR, EN, ES, DE, IT).
- [x] Système de notification et vérification de mises à jour via GitHub Releases.

---

### 🟡 Version 0.2.0 — Expérience Audio Avancée, Artistes & Discographie
- [ ] **Gestion des artistes et discographie associée :** Vue dédiée par artiste avec albums, singles et discographie complète.
- [ ] **Égaliseur graphique (EQ) :** Presets (Rock, Pop, Jazz, Bass Boost) et égaliseur paramétrique multibandes.
- [ ] **Éditeur de métadonnées in-app :** Modification directe des tags ID3 / Vorbis sur un ou plusieurs fichiers sélectionnés.
- [ ] **Téléchargement automatique de pochettes :** Recherche en ligne (MusicBrainz / Cover Art Archive) des jaquettes manquantes.
- [ ] **Filtres de recherche avancés :** Filtrage combiné par genre, année, débit binaire (bitrate) et format de compression sans perte (Lossless).
- [ ] **Crossfade paramétrable :** Transition en fondu enchaîné personnalisable entre les morceaux.

---

### 🔵 Version 0.3.0 — Connecteur Cloud Google Drive
- [ ] **Authentification sécurisée OAuth 2.0 :** Connexion simplifiée via le navigateur sans stocker de secrets en clair.
- [ ] **Scan distant des dossiers Google Drive :** Indexation des fichiers audio présents dans les dossiers configurés.
- [ ] **Lecture directe en streaming cloud :** Écoute des morceaux distants avec mise en cache locale transparente.
- [ ] **Synchronisation bidirectionnelle sélective :** Téléchargement local de pistes du cloud ou sauvegarde de pistes locales vers Drive.

---

### 🟣 Version 0.4.0 — Intégrations Streaming (Spotify, Deezer & Amazon Music)
- [ ] **Connecteur Spotify (Web API) :** Connexion du compte utilisateur et récupération des playlists et favoris.
- [ ] **Connecteur Amazon Music :** Scan, streaming et synchronisation de collections musicales distantes (OAuth 2.0).
- [ ] **Matching hybride intelligent :** Correspondance entre les titres d'une playlist distante et les fichiers déjà présents en local (haute fidélité).
- [ ] **Vue unifiée :** Affichage côte à côte des pistes disponibles en local et de celles disponibles uniquement en streaming.

---

### 🌟 Version 1.0.0 — Dédoublonnage Intelligent & Version Stable
- [ ] **Détection acoustique d'empreinte (Audio Fingerprinting) :** Identification des doublons même en cas de tags erronés ou de fichiers ré-encodés.
- [ ] **Assistant de résolution des doublons :** Comparaison intelligente de qualité (sélection automatique du meilleur bitrate / lossless) avec archivage sécurisé.
- [ ] **Packaging multiplateforme officiel :** Exécutables signés pour Windows (`.exe` / portable), macOS (`.dmg` Apple Silicon & Intel) et Linux (`AppImage` / `.deb`).
- [ ] **Documentation utilisateur complète :** Guide pas-à-pas illustré et site vitrine GitHub Pages.

---

## 💡 Proposer une fonctionnalité

Une idée ou un besoin spécifique ?
- Ouvrez une discussion ou un ticket sur [GitHub Issues](https://github.com/LEF97/Audio-Multi-Source-Organizer/issues) en utilisant le modèle *Feature Request*.
- Participez aux votes communautaires pour prioriser les développements !
