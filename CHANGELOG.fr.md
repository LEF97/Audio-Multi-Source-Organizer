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

### Added
- **Sauvegarde automatique et ultra-compacte de la playlist en temps réel** :
  - Sauvegarde automatique en tâche de fond déclenchée à chaque changement de morceau ou modification de la file d'attente, temporisée par un anti-rebond (*debounce* de 2 secondes) pour éviter les accès disques inutiles lors des sauts rapides.
  - Format compact v2 stockant uniquement les identifiants SQLite ordonnés (`track_ids`), réduisant l'empreinte disque de plus de 99 % (ex. ~78 Ko au lieu de 8,5 Mo pour une bibliothèque de 13 000 titres) et accélérant l'écriture à moins de 4 ms.
  - Écriture asynchrone non-bloquante via un thread d'arrière-plan dédié (`PlaylistSaveThread`) pour garantir une fluidité totale de l'interface utilisateur (60 FPS constants).
  - Découpage par lots de 900 variables dans `get_tracks_by_ids` pour respecter les plafonds SQLite et restaurer instantanément les très grandes playlists tout en maintenant la rétrocompatibilité avec les fichiers de format v1.
- **Mode Aléatoire physique (Option A — Mélange visible de la playlist sous le titre actif)** :
  - L'activation du mode aléatoire ou un clic sur le bouton de mélange réorganise physiquement les pistes situées sous le morceau actuellement joué dans la table de la playlist.
  - Le morceau en cours de lecture reste actif et à sa position, tandis que toute la file d'attente à venir est visible dans son ordre de diffusion réel.
  - Le bouton « Suivant » avance séquentiellement et de manière infaillible dans la table, supprimant définitivement les arrêts inopinés ou les sauts imprévisibles.
  - Ajout d'un bouton d'action directe **🎲 Mélanger la suite** dans l'en-tête de la page Playlist et dans le menu contextuel clic-droit du tableau.
- **Réorganisation intuitive de la playlist par Glisser-Déposer (Drag & Drop)** :
  - Prise en charge native du réordonnancement par glisser-déposer sur les lignes du tableau de playlist (`PlaylistTableView`).
  - Déplacement fluide mono ou multi-sélection avec mise à jour automatique de l'index de lecture pour que la piste en cours reste surlignée et continue de jouer sans interruption, peu importe les mouvements effectués autour d'elle.
  - Persistance asynchrone instantanée du nouvel ordre défini par l'utilisateur.

### Fixed
- **Résolution des erreurs `disk I/O error` (SQLite sous Windows)** : configuration du mode WAL une seule fois à l'initialisation du fichier de base de données, ajout de `PRAGMA busy_timeout = 30000`, stockage temporaire en mémoire RAM (`PRAGMA temp_store = MEMORY`) et mécanisme de réessais automatiques avec backoff exponentiel pour éliminer les conflits de verrouillage de fichiers lors des scans multithreadés.
- **Suppression des alertes modales bloquantes en arrière-plan** : les synchronisations automatiques en tâche de fond n'affichent plus de boîte de dialogue modale intrusive en cas d'erreur transitoire, mais consignent proprement l'alerte dans le journal d'activité et la barre d'état cliquable.
- **Volume audio trop faible au démarrage** : élimination d'une condition de course lors de l'initialisation du moteur de lecture VLC et neutralisation de l'atténuation automatique (*ducking*) du mixeur audio de Windows.
- **Affichage du logo officiel dans l'exécutable Windows** : correction de la résolution multi-chemins des ressources embarquées PyInstaller (`sys._MEIPASS`) pour afficher le logo AMSO haute définition dans le bandeau latéral et la page À propos au lieu de l'icône de repli 🎵.
- **Restauration de la playlist et isolation hermétique des tests** : élimination d'une pollution du profil utilisateur où l'exécution des tests automatisés pouvait écraser `saved_playlist.json` avec des pistes factices (*Track 1, Track 2, Track 3*) et une position temporelle erronée (14:10 sur un morceau de 3:00). Isolation complète de `AMSO_DATA_DIR`, `AMSO_PLAYLIST_PATH` et `AMSO_DB_PATH` dans l'environnement de test, filtrage automatique des pistes locales fantômes ou introuvables lors du chargement de la playlist, et sécurisation de la position initiale pour ne jamais dépasser la durée du titre.
- **Optimisation du temps de démarrage avec de grandes playlists (suppression du gel à 85 %)** : élimination d'un goulot d'étranglement bloquant sur le thread principal lors de la restauration de la session de lecture. La validation de la playlist exécutait des milliers d'appels disques synchrones `Path.exists()` (~40 secondes pour 12 000 morceaux). Elle privilégie désormais une vérification instantanée en mémoire O(1) (< 1 ms) pour toutes les pistes issues de la base SQLite active, rendant le lancement de l'application instantané.
- **Progression linéaire et épuration visuelle du Splash Screen** : refonte du suivi de progression au démarrage pour refléter fidèlement les opérations par paliers réguliers (15 % préférences, 25 % thème, 35 % SQLite, 45 % moteur audio, 60 % interface, 75 % bibliothèque, 90 % restauration de session, 100 % finalisation). Suppression de la mention superflue à droite du pied de page pour ne conserver que le numéro de version.
- **Rendu visuel de la pochette par défaut (vinyle & note)** : suppression du rognage vertical sur le bord droit de l'icône de note de musique au centre du vinyle, causé par l'application d'un faux-gras synthétique (*synthetic bold*) par le moteur de police DirectWrite sur l'emoji sous Windows.
- **Détection stricte des pochettes de dossier (*folder cover*)** : fiabilisation de l'algorithme de recherche d'images dans le répertoire pour n'accepter que les noms de pochettes légitimes (`folder`, `cover`, `front`, nom du morceau, `album`, `artwork`) et rejeter les images arbitraires ou préfixées (ex. `exfolder.webp`). Invalidation immédiate du cache lors de tout renommage ou suppression dans le dossier pour basculer fidèlement vers le visuel vinyle par défaut (« pochette intégrée > image folder > vinyle musique »).

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
