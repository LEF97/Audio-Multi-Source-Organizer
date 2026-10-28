# Journal des modifications (Changelog) — AMSO

<p align="right">
  <b>Français</b> • <a href="CHANGELOG.md">English</a> • <a href="docs/i18n/CHANGELOG.es.md">Español</a> • <a href="docs/i18n/CHANGELOG.de.md">Deutsch</a> • <a href="docs/i18n/CHANGELOG.it.md">Italiano</a>
</p>

---

Toutes les modifications notables apportées au projet **Audio Multi-Source Organizer (AMSO)** sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/)
et ce projet adhère à la spécification [Semantic Versioning (SemVer)](https://semver.org/lang/fr/).

---

## [0.4.1-dev] - À venir

### Added
- **Non-régression des transitions audio (TNR) :** `scripts/tnr_transitions.bat` rejoue la fin d'un titre puis le début du suivant (Sirius → Eye in the Sky par défaut) dans le vrai lecteur, avec une sortie audio factice, et compare l'enregistrement à une construction idéale (identique à l'échantillon près en gapless, fondu à puissance égale en crossfade, absence de coupure, session audio unique).
- **Journal de la TNR :** chaque exécution écrit `tests/tnr/log/tnr_AAAA-MM-JJ_HH-MM-SS.log` (version, commit, pistes, résultats détaillés, messages Qt et journaux du lecteur) ; le dossier est ignoré par git.
- **Journal de démarrage :** `startup.log` dans le dossier de données chronomètre chaque étape du lancement, la restauration de la session et les threads encore actifs à la fermeture.
- **Journal de plantage natif :** `crash.log` dans le dossier de données (`%APPDATA%/AMSO/`) reçoit la pile d'un plantage de LibVLC ou de Qt.

### Changed
- **Démarrage :** la table « Tous les morceaux » n'est plus chargée (jusqu'à 3 fois ~50 000 pistes) avant l'ouverture de sa page ; le compteur du bandeau reste exact via une requête `COUNT`.
- **Démarrage :** l'écran de chargement s'affiche avant l'import de la fenêtre principale et de la base, numpy n'est plus chargé qu'en arrière-plan une fois la fenêtre visible, l'icône et le logo sont mis en cache.

### Fixed
- **Démarrage sans réseau :** aucun sondage disque (`exists`, `isdir`) n'est plus fait sur un chemin réseau (UNC ou lecteur mappé) depuis le thread d'interface au démarrage (pochette, surveillance de dossier, restauration de la session) ; un partage injoignable ne fige plus la fenêtre. La pochette d'une piste réseau est revérifiée toutes les 30 s en arrière-plan.
- **Fermeture :** correction de « QThread: Destroyed while thread is still running » (signal `finished` du worker de pochettes qui masquait celui de `QThread`, threads de pochettes non attendus).
- **Moteur `buffer` — changement de mode de transition :** après un changement de mode dans les paramètres du lecteur, un seek puis Lecture ne démarrait plus rien (la réinitialisation laissait le moteur sans sortie audio, et le lecteur basculait à tort sur le chemin VLC). La session audio est désormais recréée immédiatement.
- **Moteur `buffer` — crossfade :** le fondu enchaîné est désormais mixé au fil du décodage (calculé sur toute la durée demandée, vectorisé). Il ne coupe plus la fin du titre sortant, ne raccourcit plus le fondu et ne provoque plus de saccades (l'ancien calcul échantillon par échantillon bloquait le thread de l'interface).
- **Blind Test avec le moteur `buffer` :** correction d'une récursion infinie (`track_changed` ↔ `seek_ratio`) qui fermait l'application ; les fondus de volume du Blind Test agissent maintenant aussi sur ce moteur.
- **Décodeur audio (`amem`) :** la fin de flux annoncée par VLC arrêtait un `QTimer` depuis le thread d'événements de VLC (`QObject::killTimer: Timers cannot be stopped from another thread`, comportement indéfini à chaque piste) ; elle est maintenant relayée au thread Qt.
- **Moteur `buffer` — mode « Pas de fondu » :** la session audio matérielle n'est plus fermée puis rouverte entre deux titres.

---

## [0.4.0] - 2026-10-25

### Added
- **Prise en charge des feuilles CUE (`.cue`) :**
  - Un fichier `.cue` apparaît dans l'arborescence comme un dossier virtuel (icône 💿) contenant ses pistes avec leur titre, leur artiste et leur durée ; le fichier audio d'origine reste lisible normalement.
  - Lecture d'une piste CUE en tant que portion du fichier (début `INDEX 01`, fin au début de la piste suivante, dernière piste jusqu'à la fin du fichier) avec position et durée propres à la piste, déplacement dans la piste et enchaînement gapless / crossfade entre portions (moteur à tampon continu uniquement ; le moteur `vlc_direct` affiche un message explicatif).
  - Tolérance aux feuilles mal formées (ligne `FILE` pointant vers le `.cue` lui-même : repli sur le fichier audio du même nom), plusieurs `FILE` par feuille, encodages UTF-8 / CP1252.
- **Support étendu de 43 langues internationales :**
  - Intégration de 38 nouvelles langues avec leurs libellés natifs dans le sélecteur de langue (`amso/core/i18n.py`).
  - Traduction automatisée et parité intégrale (401 clés par langue) via l'IA locale Ollama (`mistral:latest`).
  - Script de synchronisation globale en un clic : `scripts/sync_all_languages_ollama.bat`.
- **Mode de diagnostic visuel des traductions (`⟦...⟧`) :**
  - Ajout de l'argument CLI `--debug-i18n` et du lanceur `run_debug_i18n.bat` encadrant chaque texte traduit de balises `⟦...⟧` pour repérer immédiatement à l'écran les textes dynamiques et isoler les éventuelles chaînes codées en dur.
- **Outil d'audit et d'intégrité i18n (`scripts/audit_translations.py`) :**
  - Détection automatique de la parité des 43 langues, détection des doublons de libellés à fusionner et identification des clés orphelines via `scripts/audit_translations.bat`.
- **Sélecteur d'architecture audio dans les Paramètres / Lecture parfaite en mode gapless 0 (reste certaines anomalies en mode cross fade) :**
  - Choix transparent dans `Paramètres > Lecteur` entre :
    - *Tampon continu en mémoire (QAudioSink / WASAPI)* : flux unique ininterrompu vers la carte son, transitions gapless 0 et fondu sans coupure matérielle.
    - *Sortie directe LibVLC (double lecteur matériel)* : moteur classique matériel piloté directement par LibVLC.
- **Harnais de validation qualité unifié (Quality Gate) :** Création du script `scripts/verify.py` et de son wrapper racine `verify.bat` exécutant consécutivement le formatage (Ruff), le linter (Ruff check), le typage strict (Mypy sans masquage), le contrôle des plafonds de taille de fichiers et les tests automatisés (Pytest).

### Fixed
- **Playlists et feuilles CUE découvertes : journal d'activité et rafraîchissement de l'arborescence :** un scan qui n'ajoutait que des playlists (M3U, PLS, XSPF, WPL, CUE) n'était mentionné nulle part et ne rafraîchissait pas l'arborescence des dossiers (le nouveau nœud n'apparaissait qu'après un redémarrage). Le journal indique désormais le nombre de playlists / feuilles CUE ajoutées, mises à jour ou supprimées (avec les premiers noms), et l'arborescence se met à jour à la fin du scan.
- **Moteur audio natif WASAPI & Résolution de la coupure prématurée de fin de piste :**
  - *Sortie audio native Windows WASAPI (`mmdevice`)* : suppression du forçage de `--aout=directsound` sous Windows. Le module DirectSound de VLC tronquait de manière anormale les 1,3 à 1,4 dernières secondes des fichiers audio (coupant la fin de *Sirius*). L'alignement sur `mmdevice` permet à LibVLC de diffuser l'intégralité du flux audio jusqu'à la dernière milliseconde en 32-bit float.
  - *Suppression des bops et artefacts de clics rapides* : élimination des coupures artificielles de volume à 0 lors des `seek` et `stop` qui provoquaient des discontinuités de phase et des collisions de timers asynchrones lors des clics rapides. Le repositionnement temporel (`set_time`) et l'arrêt s'exécutent désormais de manière native et fluide.
  - *Suppression des micro-glitches en fin de piste / passages calmes* : arrêt du polling permanent de volume dans la boucle de tick, évitant d'envoyer des ajustements de gain matériels répétitifs en continu pendant la lecture.
- **Précision millimétrique des transitions & Enchaînements fluides (Gapless & Pas de fondu) :**
  - *Élimination des craquements et pops au lancement du titre suivant* : suppression du forçage de volume à 0 sur le second lecteur en veille, qui provoquait une coupure globale de session sous WASAPI puis un transitoire impulsif (« craquement ») au déblocage de la pause. Le second lecteur est préchargé en pause (`:start-paused`) au volume nominal sans altérer le titre en cours.
  - *Enchaînement sans blanc (Gapless 0)* : prise en compte exacte de la latence de pipeline LibVLC (`vlc_gapless_latency_ms`, 250 ms par défaut) pour débloquer le lecteur suivant avant la fin exacte de la piste en cours, assurant une continuité musicale ininterrompue sans aucun trou de silence entre morceaux enchaînés (*Sirius* -> *Eye In The Sky*).
  - *Enchaînement naturel en mode Pas de fondu* : suppression du délai artificiel de 400 ms après `State.Ended`, permettant une transition immédiate et propre dès la fin de lecture du titre précédent.
- **Suppression des déclenchements de lecture audio intempestifs :**
  - *Retour en arrière (`previous` / `seek`)* : la commande piste précédente (`previous()`) respecte strictement l'état de pause du lecteur et utilise `load_index()` pour charger le titre sans démarrer la lecture si le lecteur était en pause. De même, un déplacement temporel (`seek_ms`) annule tout préchargement standby ou vidage de transition en attente, et repositionne la piste sans lecture forcée si le lecteur était en pause ou en fin de morceau (`State.Ended`).
  - *Navigation entre menus (sortie du Blind Test vers d'autres onglets)* : centralisation de la navigation d'onglets (`_switch_to_page`), arrêt forcé du Blind Test et réinitialisation de tout standby actif dès la sortie de la page pour interdire tout redémarrage autonome de la musique en arrière-plan.
- **Fondu enchaîné sans saccades (Crossfade Equal-Power) :**
  - *Isolation matérielle des volumes sous Windows* : affectation dynamique de la sortie audio `directsound` pour le mode fondu enchaîné (les modes standard et gapless demeurent sur `mmdevice` natif sans troncature). Contrairement à WASAPI (`mmdevice`) dont le réglage de volume affecte la session de processus globale et générait un conflit violent (hachage / saccades à 40 Hz entre le titre sortant et le titre entrant), DirectSound isole le volume propre à chaque mémoire tampon secondaire (`IDirectSoundBuffer::SetVolume`).
  - *Courbes de fondu parfaitement lisses* : transition en puissance égale continue (cosinus pour le titre sortant, sinus pour le titre entrant) sans aucun creux acoustique ni saccade au déclenchement du fondu.
- **Fiabilisation du Moteur Tampon Continu en Mémoire (Phase 2 - QAudioSink / Ring Buffer) :**
  - *Respect absolu de la pause sur retour arrière (`previous()`)* : `previous()` préserve désormais fidèlement l'état de pause, charge le morceau précédent sans déclencher la lecture, et suspend le flux audio sans micro-coupure ni redémarrage impromptu.
  - *Enchaînement naturel en mode Pas de fondu* : suppression du préchargement standby inutile en mode standard, transition directe via le cycle de chargement standard avec mise à jour immédiate du titre, de la pochette et de la durée exacte.
  - *Résolution des collisions et saccades en mode Gapless 0* : cycle de vie hermétique du décodeur standby, déconnexions/reconnexions complètes des signaux (`ready_to_play`, `chunk_decoded`), rétablissement du seek après raccord, et rejet strict des paquets PCM non appariés au titre courant dans le tampon mémoire.
  - *Fondu croisé en mémoire à puissance égale (Mode Crossfade)* :
    - Mixage PCM mathématique des échantillons 16-bit (courbes cos/sin à puissance égale) à partir de la tête de lecture courante (`_play_offset`), avec clamping anti-écrêtage.
    - Séparation stricte entre le déclenchement audio du fondu et la bascule de l'interface graphique : l'UI reste affichée sur le titre sortant pendant son estompage progressif, et bascule sur le titre entrant exactement à l'extinction naturelle du morceau, éliminant la coupure visuelle et sonore prématurée.
    - Synchronisation et calage temporel continus : purge instantanée des données PCM consommées de la piste sortante à l'extinction (`finish_crossfade`), recalage précis de l'offset de lecture (`_base_offset_ms`) sur la durée exacte du fondu, garantissant un défilement continu du curseur sans téléportation, ainsi qu'un repositionnement temporel (`seek_ms`) parfaitement aligné.
    - Découpage modulaire : extraction de `amso/services/player_vlc_transitions.py` (transitions directes LibVLC) permettant de maintenir tous les fichiers du lecteur sous les 450 lignes.
  - *Réinitialisation intégrale à chaud du lecteur (`reset_playback`)* :
    - Toute modification dans les Paramètres du moteur audio (*VLC direct* vs *Tampon continu*) ou du mode de transition (*Pas de fondu*, *Gapless 0*, *Crossfade*) coupe immédiatement la lecture en cours et réinitialise de fond en comble les flux (destruction propre du `QAudioSink`, vidage des tampons PCM mémoire, arrêt des décodeurs, détachement des médias LibVLC, annulation de tous les timers de transition/fondu).
    - La piste active reste sélectionnée en pause à 00:00 prête à être lancée sous la nouvelle configuration sans nécessiter de redémarrer l'application.


### Changed
- **Découpage modulaire complet de l'architecture (< 500 lignes par fichier) :**
  - Objectif atteint à 100 % : **0 fichier > 500 lignes** sur l'ensemble de la base de code AMSO (contre 8 fichiers au-dessus du seuil initialement).
  - Allègement de `main_window.py` (~1 500 -> 357 lignes) via des mixins spécialisés dans `amso/ui/pages/`.
  - Décomposition de `player_service.py` (~1 400 -> 329 lignes) avec l'extraction de `player_transport.py`, `player_queue.py`, `player_transitions.py` et `windows_audio.py`.
  - Scission de `blind_test_view.py` (864 -> 447 lignes) vers `round_controller.py` et `compat.py`.
  - Scission de `player_view.py` (693 -> 316 lignes) vers `player_ui_builder.py`.
  - Scission de `settings_player.py` (668 -> 345 lignes) vers `settings_player_effects.py`.
  - Scission de `theme.py` (633 -> 20 lignes) vers `resources.py`, `qss_base.py` et `qss_components.py`.
  - Scission de `models.py` (631 -> 118 lignes) vers `models_base.py`, `folder_track_model.py` et `playlist_table_model.py`.
  - Scission de `metadata.py` (621 -> 420 lignes) vers `cover_art.py`.
  - Scission de `playlist_view.py` (603 -> 284 lignes) vers `playlist_ui_builder.py` et `playlist_table_view.py`.
  - Scission de `logs_view.py` (512 -> 426 lignes) vers `log_detail_dialog.py`.
  - Scission de `folders_page.py` (~970 -> 406 lignes) vers `folders_tree.py` et `folders_trash.py`.
- **Rationalisation et fusion des doublons :**
  - Centralisation des composants partagés (`ClickableSlider`, `EffectContainer`, `EffectsViewMixin`).
  - Factorisation des libellés UI génériques sous le préfixe partagé `common.*` (`common.cancel`, `common.close`, `common.refresh`, `common.later`, `common.open_explorer`, `table.col_filename`, `table.col_source`, `table.col_folder_name`).
  - Normalisation obligatoire des fins de ligne Windows CRLF (`\r\n`) sur l'ensemble des fichiers `.bat`.

### Fixed
- **Harmonisation et élimination des résidus de traduction dans les 41 langues :**
  - Éradication de plus de 1 400 clés restées en français ou en anglais par défaut via le nouvel outil `scripts/fix_residual_translations.py` (`scripts/fix_residual_translations.bat`).
  - Correction des libellés d'ambiance visuelle et des effets graphiques (`player.visual_effect`, `effects.*`), traduits désormais nativement dans toutes les langues.
  - Résolution des placeholders de recherche hybrides (`topbar.search_placeholder`) mélangeant langue cible et anglais sur les écrans Doublons, Sources et Navigation.
  - Traduction fidèle des titres de paramétrage des sources (`settings.page_sources_title`, `settings.section_sources_title`) et de configuration générale (`settings.page_title`).
  - Traduction intégrale du bouton partagé d'actualisation (`common.refresh` : « 🔄 刷新 » en chinois, etc.) au lieu d'un « Actualiser » francophone résiduel dans les logs.
  - Localisation complète des sections de soutien, dons et liens officiels de la page À propos (`dialog.about_*`, `update.btn_support`).

---

## [0.3.0] - 2026-10-18

### Added
- **Prise en charge complète des fichiers de playlist** :
  - Indexation automatique des formats de listes de lecture : `.m3u`, `.m3u8`, `.pls`, `.xspf` et `.wpl`.
  - Intégration dans l'arborescence « Par dossier » sous forme de nœuds dédiés arborant l'icône **`🎶`**.
  - Respect de l'ordre séquentiel d'écoute défini dans la playlist (colonne `#` avec l'ordre 1, 2, 3...) sans tri alphabétique automatique forcé.
  - Gestion et détection visuelle des morceaux manquants ou déplacés : indication par un préfixe **`⚠️`**, coloration d'avertissement douce et infobulle descriptive, sans bloquer la lecture des autres pistes.
  - Menu contextuel enrichi sur les nœuds de playlist : lecture directe, ajout en file d'attente et ouverture de l'emplacement du fichier playlist dans l'Explorateur Windows.
- **Fondu sonore entrant doux (*Fade-in*)** :
  - Transition progressive du volume de 0% au volume défini sur 1 seconde lors du démarrage ou de la reprise d'une lecture audio (hors mode Blind Test).
- **Stabilité et fluidité de la synchronisation** :
  - Suppression de la boîte de dialogue bloquante « Scan already running » au profit d'un enchaînement silencieux en file d'attente.
  - Préservation de la sélection et non-rechargement inutile de l'arborescence des dossiers si aucun changement de dossier n'est détecté.
- **Affichage dynamique des pochettes** :
  - Correction du redimensionnement et du repositionnement de la pochette lors du passage plein écran / fenêtré ou du redimensionnement libre de la fenêtre.

---

## [0.2.0] - 2026-10-18

### Added

### Mode Blind Test & Section Jeux
- **Nouveau tiroir « 🎲 Jeux »** : Catégorie dédiée repliable dans la barre latérale accueillant la vue Blind Test (localisée en 5 langues).
- **Expérience de jeu immersive** : Décompte visuel dynamique au centre de la pochette masquée, révélation progressive en fondu doux et enchaînement automatique des manches.
- **Gestion acoustique avancée** : Réglage précis des temps de recherche, de découverte et du fondu sonore sortant (*fade-out*).
- **Configuration dédiée** : Délocalisation des réglages du Blind Test dans `Paramètres > Lecteur`.

### Ergonomie & Gestion de Playlist
- **Refonte du mode Aléatoire (Shuffle)** : Mélange visuel intégral de la file d'attente préservant la piste active, bouton d'action directe « 🎲 Mélanger les titres » et restauration fidèle de l'ordre d'origine dès désactivation.
- **Réorganisation par Glisser-Déposer** : Réordonnancement fluide des morceaux à la souris dans le tableau sans interrompre la lecture.
- **Sauvegarde asynchrone v2** : Format compact par identifiants SQLite réduisant l'empreinte disque de 99 % (accès non-bloquants, 60 FPS constants).
- **Comportement « No Autoplay »** : L'ajout de morceaux en file d'attente ne force plus le démarrage intempestif de la lecture.

### Gestion de bibliothèque & Corbeille intelligente
- **Suppression à double niveau** : Choix entre le simple retrait de la bibliothèque (avec exclusion mémorisée pour les futurs scans) et la suppression physique vers la Corbeille Windows.
- **Vue dédiée « 🗑️ Corbeille »** : Consultation des pistes exclues et restauration en un clic avec réintégration automatique dans la base de données.
- **Arborescence clarifiée** : Distinction visuelle entre sources locales et cloud, arborescence repliée par défaut au démarrage et menus contextuels uniformisés.

### Stabilité du moteur audio (LibVLC) & Performances
- **Éradication des blocages critiques** : Suppression du deadlock entre le thread C interne de LibVLC et la boucle d'événements Qt (fin des gels d'interface et écrans blancs).
- **Robustesse des transitions** : Verrou anti-réentrance sur les changements rapides de pistes et résolution des blocages lors des retours arrière successifs (« Morceau précédent »).
- **Contrôles de volume fiabilisés** : Intégration du curseur de volume dans la barre supérieure du lecteur et suppression des conflits d'atténuation sonore DirectSound.

### Interface & Liens officiels
- **Modernisation de la page « À propos »** : En-tête réaligné, analyseur de spectre rétro interactif intégré sous le texte et ajout des boutons officiels (Ko-fi, GitHub Sponsors, GitHub, Itch.io).
- **Internationalisation intégrale** : Synchronisation complète de l'ensemble des libellés et options en 5 langues (FR, EN, ES, DE, IT).

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
