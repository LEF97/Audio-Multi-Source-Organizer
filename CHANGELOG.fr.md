# Journal des modifications (Changelog) — AMSO

<p align="right">
  <b>Français</b> • <a href="CHANGELOG.md">English</a> • <a href="CHANGELOG.es.md">Español</a> • <a href="CHANGELOG.de.md">Deutsch</a> • <a href="CHANGELOG.it.md">Italiano</a>
</p>

---

Toutes les modifications notables apportées au projet **Audio Multi-Source Organizer (AMSO)** sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/)
et ce projet adhère à la spécification [Semantic Versioning (SemVer)](https://semver.org/lang/fr/).

---

## [0.2.0-dev] - En cours de développement

### Fixed
- **Affichage du logo officiel dans l'exécutable Windows** : correction de la résolution multi-chemins des ressources embarquées PyInstaller (`sys._MEIPASS`) pour afficher le logo AMSO haute définition dans le bandeau latéral et la page À propos au lieu de l'icône de repli 🎵.

---

## [0.1.0] - 2026-10-17

### Added
- **Moteur de lecture audio intégré (python-vlc) :**
  - Prise en charge native des formats audio populaires : MP3, FLAC, WAV, AAC, OGG, M4A, WMA.
  - Détection et téléchargement automatique transparent d'un binaire VLC portable en cas d'absence de VLC sur le système utilisateur.
  - Contrôle complet de lecture : Play, Pause, Stop, Piste suivante, Piste précédente, barre de progression dynamique (Seekbar) et gestion du volume sonore.
  - Modes de lecture : lecture aléatoire (*Shuffle*) et modes de répétition (*Désactivé*, *Répéter la playlist*, *Répéter le titre en boucle*).
  - Effets visuels animés en temps réel synchronisés avec la lecture (particules, vagues, étoiles, distorsion spatiale, aurore boréale, barres de spectre).
- **Gestionnaire de Playlist & File d'attente :**
  - Vue dédiée avec table virtualisée supportant plusieurs dizaines de milliers de titres sans latence.
  - Réorganisation intuitive de la file d'attente par glisser-déposer (*Drag & Drop*).
  - Menus contextuels complets : « Lire », « Ajouter à la suite », « Supprimer de la file », « Propriétés ».
  - Sauvegarde automatique de la session de lecture (titre en cours, position temporelle en ms, playlist active).
- **Scanner local multithreadé haute performance :**
  - Parcours récursif asynchrone des répertoires locaux avec barre de progression et métriques en temps réel.
  - Extraction rapide des métadonnées (titre, artiste, album, année, genre, durée, bitrate, numéro de piste) via `mutagen`.
  - Extraction et mise en cache des pochettes d'albums intégrées avec rendu asynchrone pour éviter tout gel de l'interface.
  - Calcul d'empreintes de hachage de fichier pour identifier les doublons physiques.
- **Base de données SQLite optimisée :**
  - Architecture relationnelle sans ORM lourd pour une exécution quasi-instantanée des requêtes.
  - Gestion des sources, des morceaux scannés et de l'historique d'activité.
- **Interface Utilisateur Moderne (PySide6 / Dark Mode) :**
  - Thème sombre personnalisé haut de gamme avec palette de couleurs soignée et animations douces.
  - Tiroir latéral rétractable pour la navigation principale et les réglages.
  - Support multilingue complet (Français, Anglais, Espagnol, Allemand, Italien) avec changement de langue à chaud.
  - Page dédiée « À propos » dans les Paramètres : détails du projet, badge de version, technologies open-source, liens vers GitHub, Itch.io et plateformes de mécénat (Ko-fi, GitHub Sponsors).
  - Vérificateur manuel et automatique de mises à jour interrogeant l'API GitHub Releases (`/releases/latest`) avec bannière de notification interactive.
  - Raccourci clavier <kbd>F1</kbd> et clic direct sur le logo AMSO pour ouvrir la page « À propos ».

### Changed
- Remplacement du dialogue modal « À propos » par une sous-page intégrée et fluide dans les Paramètres.
- Réorganisation de la navigation des Paramètres en 5 sections : Général, Lecteur, Sources, Logs, À propos.
- Masquage de la barre de menus standard résiduelle au profit d'une interface épurée sans bouton « Aide » orphelin.

### Fixed
- **Démarrage à 00:00 :** Réinitialisation systématique de la position temporelle (`_pending_seek_ms = 0`) lors de la sélection d'une nouvelle musique depuis la bibliothèque ou la playlist, réservant la reprise de position uniquement au bouton « Play » de la session précédente restaurée.
- **Persistance immédiate du volume :** Sauvegarde instantanée dans `config.ini` dès la manipulation du slider de volume ou du bouton muet.
- **Verrouillage du volume VLC :** Resynchronisation automatique du volume audio lors du passage à l'état `Playing` dans la boucle d'horloge pour éviter toute perte de réglage lors du démarrage à froid du décodeur VLC.
