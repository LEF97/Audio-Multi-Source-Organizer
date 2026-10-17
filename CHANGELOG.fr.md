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
- **Autonomie et perfectionnement ergonomique de la page Blind Test** :
  - **Démarrage manuel sous contrôle (aucun autoplay à l'ouverture)** : la musique ne démarre plus automatiquement à l'affichage de la page Blind Test. Le joueur se place en attente (statut *En pause*) sur la piste en cours calée à 0 seconde, le jeu attendant le clic sur le bouton Play.
  - **Repositionnement du volume dans la barre supérieure** : la réglette de volume, l'icône muet et l'affichage du pourcentage sont relogés tout en haut de l'écran, à droite du titre « 🎭 Blind Test », calqués sur l'ergonomie de la page Lecteur et épurant la carte de jeu.
  - **Lecture systématique à 0 seconde** : chaque extrait joué dans le Blind Test démarre impérativement à 0:00 (ne reprenant plus la position en cours du lecteur).
  - **Autonomie complète du Blind Test & Restauration fidèle du Lecteur** : distinction stricte entre la progression de manche du Blind Test (0 à 30 secondes d'extrait) et la position du lecteur audio. Lorsque l'utilisateur quitte la page Blind Test, la piste choisie avant le jeu ainsi que sa position exacte en millisecondes et son état de lecture sont fidèlement restaurés.
  - **Animation de zoom dynamique sur le décompte** : effet de zoom vectoriel fluide (redimensionnement dynamique de 1.45 vers 1.0 avec lissage OutCubic) synchronisé avec le fondu d'opacité sur chaque seconde du décompte.
  - **Bouton « ⏮️ Morceau précédent » interactif** : ajout de la commande dans la rangée de contrôle (`btn_prev`). Si la manche est entamée (> 2 s) ou déjà révélée, le bouton remet à zéro la manche en cours à 0:00 (décompte et pochette mystère réinitialisés). Si la manche est au tout début (<= 2 s), il recule réellement vers la piste précédente de la playlist.
  - **Durée complète de découverte lors de la révélation** : un clic sur « 👁️ Révéler » bascule directement au début de la phase de découverte, garantissant toujours les 10 secondes complètes restantes (ou la durée configurée) avant le titre suivant, avec application du fondu sonore de fin de manche.
  - **Affichage du nom de fichier sous l'artiste** : ajout du libellé de fichier sous l'artiste/album, affichant « 📁 Fichier mystère... » pendant la recherche et le nom réel du fichier audio lors de la révélation (avec infobulle complète).
  - **Indicateur de session globale « Extrait x / y — reste z minutes »** : affichage d'un badge épuré centré directement sous la barre supérieure informant en direct du numéro d'extrait courant, du total et de la durée restante estimée de la session.
  - **Préchargement transparent du fichier suivant** : préchargement en tâche de fond sur le lecteur secondaire LibVLC dès le début de la manche pour une transition instantanée et sans à-coups à l'extrait suivant.
  - **Fondu entrant doux (Fade-in 0% à 100% en 2 secondes)** : la piste suivante démarre désormais dans le silence (0%) et gagne progressivement son volume nominal sur 2.0 secondes via une courbe de lissage à 50 ms.
  - **Extinction acoustique propre en fin de manche** : éradication du retour brutal de volume à 100% à la fin des 30 secondes, garantissant que le morceau s'éteint totalement dans le silence à 0% avant de basculer vers l'extrait suivant.

### Fixed
- **Résolution du blocage/gel critique de l'interface (écran blanc / « Ne répond pas »)** :
  - **Éradication du deadlock LibVLC C-Thread / GIL** : identification via inspection de pile mémoire d'un interblocage (*deadlock*) fatal où un callback d'événement VLC (`MediaPlayerPlaying`) tentait d'appeler `libvlc_audio_set_volume` depuis le thread interne de VLC pendant que le thread principal Qt appelait simultanément VLC avec le verrou GIL. Le rappel d'événement a été supprimé et remplacé par une application sécurisée sur l'event loop Qt.
  - **Dissociation et non-ingérence des volumes temporaires** : ajout d'un drapeau `_is_temporary_volume` dans `PlayerService` pour empêcher la boucle de contrôle principale (100 ms) d'écraser et de combattre l'atténuation sonore du Blind Test (50 ms).
  - **Élimination des rafales d'appels DirectSound** : mise en cache du dernier volume appliqué (`_last_set_volume`) et suppression des multiples `QTimer.singleShot` concurrents sur l'initialisation du périphérique audio DirectSound.
  - **Suppression des appels dupliqués lors des enchaînements de manche** : clarification de la transition de fin de manche dans le Blind Test, évitant les déclenchements multiples et simultanés de `next()`, `seek_ratio(0.0)` et `_start_round_for_track()`.
- **Optimisations et corrections ergonomiques du Lecteur et du Blind Test** :
  - **Intégration du volume en haut du Lecteur audio** : déplacement du curseur de volume, de l'icône muet et du pourcentage sonore dans la barre supérieure de la page, directement à côté du titre « Lecteur audio », libérant ainsi l'espace visuel sous la carte principale.
  - **Épuration de la page Lecteur** : retrait complet du bloc de configuration du Blind Test qui n'apparaît plus sous le lecteur audio.
  - **Délocalisation des paramètres Blind Test dans Paramètres > Lecteur** :
    - Nouvelle carte dédiée « 🎭 Paramètres du Blind Test » ajoutée à la fin de la page `Paramètres > Lecteur`.
    - Configuration de la durée du décompte (5 à 120 s, 20 s par défaut) et de la durée de découverte (3 à 60 s, 10 s par défaut).
    - **Nouveau paramètre : Durée du fondu sonore (*Fade-out*)** : réglable de 0 à 10 secondes (2 secondes par défaut, plafonné dynamiquement à la durée de découverte).
    - Calcul et résumé en direct de la manche : `Durée d'une manche : {total}s ({countdown}s recherche + {reveal}s découverte dont {fade}s de fondu)`.
  - **Gestion acoustique du fondu de découverte** :
    - La durée totale de découverte reste inchangée (ex: 10 s par défaut).
    - La lecture audio s'effectue à 100 % du volume nominal défini pendant `découverte - fondu` (ex: 10 - 2 = 8 secondes), puis s'atténue de manière fluide et progressive jusqu'à 0 pendant les 2 dernières secondes.
    - Dès le passage au morceau suivant (nouvelle manche), le volume sonore est instantanément et automatiquement rétabli à 100 % dès la première milliseconde.
    - Rétablissement immédiat du volume nominal en cas de clic manuel sur « Morceau suivant », pause ou changement de vue.
  - **Internationalisation intégrale** : libellés et textes d'explication traduits et synchronisés en 5 langues (FR, EN, ES, DE, IT).
- **Refonte et perfectionnement du mode Aléatoire (Shuffle)** :
  - **Mélange intégral de la playlist** : lorsque l'icône Shuffle passe de désactivé à activé, l'ensemble complet de la file d'attente/tableau est mélangé aléatoirement (et non plus uniquement les titres en dessous). La piste en cours de lecture est elle-même redistribuée aléatoirement (pouvant se retrouver en première comme en dernière position) tout en poursuivant sa lecture sans coupure.
  - **Restauration fidèle de l'ordre initial** : dès que le mode Shuffle est désactivé, la playlist reprend instantanément son ordre de titres d'origine (avant le mélange), l'index de lecture étant automatiquement recalé sur la position d'origine du morceau actif.
  - **Bouton et menu contextuel « 🎲 Mélanger les titres »** :
    - Renommage de « Mélanger la suite » en « 🎲 Mélanger les titres » (`playlist.btn_shuffle_tracks` et `playlist.menu_shuffle_tracks`).
    - État contextuel strict : le bouton et l'action du menu clic droit ne sont désormais activables que lorsque le mode Shuffle est actif (affichés en grisé/désactivé sinon).
    - Re-mélange dynamique : un clic sur ce bouton re-mélange l'ensemble des titres avec redistribution fluide de la piste en cours.
  - **Localisation complète** : traductions synchronisées dans les 5 langues officielles de l'application (FR, EN, ES, DE, IT).
- **Refonte visuelle et interactive de la page À propos** :
  - **Bannière supérieure unifiée et alignée** :
    - Alignement parfait du titre « Audio Multi-Source Organizer » et du badge de version tout en haut du cadre avec le sommet du logo officiel AMSO.
    - Égaliseur de spectre audio rétro intégré directement **sous le texte descriptif** : barres calées sur le bord gauche du texte (ne touchant pas l'icône) et s'étirant jusqu'au bord droit du cadre, réagissant en temps réel à la musique jouée.
  - **Section Soutien & Financement restructurée** :
    - Carte dédiée avec sous-titre `💖 Soutenir le projet (Faire un don)`.
    - Bouton Ko-fi aux couleurs officielles (`☕ Faire un don sur Ko-fi`) pointant vers `https://ko-fi.com/arnaudlef97`.
    - Bouton GitHub Sponsors (`💖 GitHub Sponsors`) pointant vers l'URL officielle corrigée `https://github.com/sponsors/lef97`.
  - **Section Pages officielles distincte** :
    - Carte dédiée avec sous-titre `🌐 Pages officielles` séparée par un espacement naturel (sans trait horizontal de séparation).
    - Boutons d'accès direct au Dépôt GitHub (`⭐ Dépôt GitHub`) et à la page Itch.io (`🎮 Page Itch.io` : `https://arnaudlef97.itch.io/amso`).
  - **Section Remerciements repositionnée en clôture** :
    - Carte dédiée `👍 Remerciements & Technologies Open Source` positionnée après les Pages officielles pour une hiérarchie d'information optimale.
- **Mode « 🎭 Blind Test » interactif avec animations et enchaînement automatique** :
  - **Nouvelle vue dédiée « 🎭 Blind Test »** insérée dans le tiroir Lecteur de la barre latérale, entre les pages Lecteur et Playlist.
  - **Affichage mystère immersif** : effets visuels en haut synchronisés avec le moteur graphique, cadre central au format vinyle avec pochette masquée et métadonnées cachées (titre et artiste affichés sous forme de mystère).
  - **Décompte dynamique animé par pulsation (Zoom & Fade)** : affichage d'un décompte géant au centre de la pochette qui effectue un zoom et un fondu doux à chaque seconde.
  - **Révélation progressive et douce** : à 0 seconde (ou par clic anticipé sur le bouton « 👁️ Révéler »), la pochette émerge en fondu doux (*fade-in* progressif), le titre, l'artiste et l'album s'affichent clairement tout en dissimulant les données techniques (bitrate, format, chemin de fichier).
  - **Enchaînement automatique et calage parfait** : la piste reste révélée pendant la durée de découverte configurée, puis passe automatiquement à la piste suivante en repartant systématiquement de 00:00.
  - **Section de réglages intégrée dans la page Lecteur** : deux commandes configurables (*spinboxes*) avec calcul dynamique en direct de la durée totale d'une manche :
    - *Durée du décompte* : 20 secondes par défaut (ajustable de 5 à 120 s).
    - *Durée de la découverte* : 10 secondes par défaut (ajustable de 3 à 60 s).
    - Durée totale par défaut : 30 secondes par manche.
  - **Contrôles du jeu** : boutons Lecture/Pause, Révéler manuellement et Suivant, ainsi que maintien actif de l'écran (inhibition de mise en veille) pendant la session de jeu.
  - **Internationalisation complète** : 100 % des libellés et textes d'états traduits et synchronisés en 5 langues (FR, EN, ES, DE, IT).
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
- **Refonte de l'arborescence des dossiers et harmonisation des menus contextuels** :
  - **Distinction visuelle des sources et dossiers** : les racines de sources affichent désormais une icône dédiée (`💾` pour le stockage local/NAS, `☁️` pour le cloud) les différenciant immédiatement des sous-dossiers (`📁`).
  - **Arborescence repliée par défaut** : au démarrage de l'application, l'arborescence des sources sur le panneau de gauche est désormais réduite pour une vue propre et dégagée.
  - **Harmonisation des menus contextuels** : ajout des actions « ⏭️ Suivant » et « ➕ Ajouter à la liste de lecture » par clic-droit sur les dossiers de l'arborescence de gauche, ordonnées de manière identique au tableau des morceaux.
- **Suppression intelligente de morceau & intégration de la Corbeille Windows** :
  - Boîte de dialogue de confirmation moderne proposant deux choix clairs lors d'une demande de suppression :
    1. *Retirer de la bibliothèque (et ignorer lors des futurs scans)* : le fichier est préservé sur le disque mais enregistré dans la table `ignored_tracks` pour ne plus jamais réapparaître lors des synchronisations automatiques ou manuelles.
    2. *Mettre également le fichier à la corbeille Windows* : déplacement physique direct du fichier dans la corbeille système Windows (`ctypes.windll.shell32.SHFileOperationW`) avec possibilité de restauration ultérieure.
  - Retrait dynamique et instantané du morceau supprimé de la file d'attente du lecteur audio si celui-ci y figurait.
- **Vue dédiée Corbeille AMSO & Restauration dans la bibliothèque** :
  - Ajout d'une entrée racine permanente **« 🗑️ Corbeille »** en dessous des sources dans l'arborescence de gauche, avec décompte dynamique des morceaux.
  - Interface dédiée listant les morceaux retirés de la bibliothèque avec leur nom de fichier, leur emplacement d'origine, leur date de retrait et leur statut physique sur disque (*✅ Présent* ou *❌ Absent / Corbeille Windows*).
  - Actions de restauration en un clic : bouton d'en-tête « ♻️ Restaurer la sélection », double-clic sur une ligne ou menu contextuel pour retirer l'exclusion et relancer la synchronisation de la source parente afin de réintégrer instantanément les morceaux dans la bibliothèque.
  - Possibilité de vider la corbeille d'un clic pour réinitialiser les exclusions.
- **Ajout en file d'attente sans lecture forcée (*No Autoplay*)** :
  - Les commandes « Suivant » et « Ajouter à la liste de lecture » n'imposent plus de lecture automatique lorsque le lecteur est arrêté ou la file d'attente vide. Seuls le double-clic sur un morceau ou le clic sur « Play » démarrent la restitution sonore.

### Fixed
- **Résolution des erreurs `disk I/O error` (SQLite sous Windows)** : configuration du mode WAL une seule fois à l'initialisation du fichier de base de données, ajout de `PRAGMA busy_timeout = 30000`, stockage temporaire en mémoire RAM (`PRAGMA temp_store = MEMORY`) et mécanisme de réessais automatiques avec backoff exponentiel pour éliminer les conflits de verrouillage de fichiers lors des scans multithreadés.
- **Suppression des alertes modales bloquantes en arrière-plan** : les synchronisations automatiques en tâche de fond n'affichent plus de boîte de dialogue modale intrusive en cas d'erreur transitoire, mais consignent proprement l'alerte dans le journal d'activité et la barre d'état cliquable.
- **Volume audio trop faible au démarrage** : élimination d'une condition de course lors de l'initialisation du moteur de lecture VLC et neutralisation de l'atténuation automatique (*ducking*) du mixeur audio de Windows.
- **Affichage du logo officiel dans l'exécutable Windows** : correction de la résolution multi-chemins des ressources embarquées PyInstaller (`sys._MEIPASS`) pour afficher le logo AMSO haute définition dans le bandeau latéral et la page À propos au lieu de l'icône de repli 🎵.
- **Restauration de la playlist et isolation hermétique des tests** : élimination d'une pollution du profil utilisateur où l'exécution des tests automatisés pouvait écraser `saved_playlist.json` avec des pistes factices (*Track 1, Track 2, Track 3*) et une position temporelle erronée (14:10 sur un morceau de 3:00). Isolation complète de `AMSO_DATA_DIR`, `AMSO_PLAYLIST_PATH` et `AMSO_DB_PATH` dans l'environnement de test, filtrage automatique des pistes locales fantômes ou introuvables lors du chargement de la playlist, et sécurisation de la position initiale pour ne jamais dépasser la durée du titre.
- **Optimisation du temps de démarrage avec de grandes playlists (suppression du gel à 85 %)** : élimination d'un goulot d'étranglement bloquant sur le thread principal lors de la restauration de la session de lecture. La validation de la playlist exécutait des milliers d'appels disques synchrones `Path.exists()` (~40 secondes pour 12 000 morceaux). Elle privilégie désormais une vérification instantanée en mémoire O(1) (< 1 ms) pour toutes les pistes issues de la base SQLite active, rendant le lancement de l'application instantané.
- **Progression fluide pas-à-pas et élimination du recul visuel du Splash Screen** : refonte du suivi de progression au démarrage avec animation fluide pas-à-pas de 1 % en 1 % (10 ms par incrément) pour une transition continue et soignée entre les paliers réguliers (15 % préférences, 25 % thème, 35 % SQLite, 45 % moteur audio, 60 % interface, 75 % bibliothèque, 90 % restauration de session, 100 % finalisation). Résolution d'un conflit de style CSS global où l'application du thème sombre imposait un `max-width: 220px` sur toutes les barres de progression, divisant soudainement la largeur du splash screen par deux et donnant l'illusion visuelle d'un retour en arrière de la jauge bleue. Sanctuarisation de la largeur (`#splashProgressBar`), verrouillage de la progression strictement monotone et suppression de la mention superflue à droite du pied de page.
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
