---
name: audio-pipeline
description: Architecture audio continue d'AMSO (ContinuousAudioEngine, QAudioSink push mode, Ring Buffer mémoire, décodeur amem). À consulter impérativement pour toute modification touchant la lecture, le streaming ou les transitions audio.
---

# Architecture Audio et Moteurs de Lecture

## Étanchéité stricte des deux moteurs audio (`vlc_direct` vs `buffer` / `QAudioSink`)
AMSO supporte deux moteurs audio distincts et hermétiques (sélectionnables via `get_audio_engine()` : `"vlc_direct"` ou `"buffer"`) :
1. **Mode `vlc_direct` (Sortie directe LibVLC — 100 % finalisé et figé)** :
   - Sortie audio directe gérée nativement par VLC (`python-vlc`).
   - 3 types de transitions validés à 100 % et figés : *Pas de fondu*, *Gapless 0 ms* (WASAPI `mmdevice`), et *Crossfade* (DirectSound pour isolation des volumes).
   - Indépendant de QAudioSink et du tampon mémoire PCM. Code figé, plus aucune modification de transport sur ce moteur.
2. **Mode `buffer` / `ContinuousAudioEngine` (moteur QAudioSink / phase 2 — en cours)** :
   - Sortie physique vers la carte son gérée exclusivement par un `QAudioSink` unique (mode Push) ouvert en continu.
   - Décodeur amem + Tampon mémoire continu (Ring Buffer PCM). Transitions 100% logicielles (gapless sample-accurate, crossfade cos/sin, silences numériques injectés).

**Règle d'étanchéité absolue :**
- Les deux moteurs sont **totalement étanches** : aucune modification de code, d'architecture, de paramétrage ou d'utilisation relative à un moteur ne doit avoir d'impact ou d'effet de bord sur le son ou le comportement de l'autre.
- Le mode **`vlc_direct`** est désormais figé. Le travail s'effectue exclusivement sur le mode **`buffer` / `QAudioSink`**.

---

## Règles du Mode Continu `buffer` (ContinuousAudioEngine - Phase 2)
1. **Flux unique vers la carte son (`QAudioSink`)** :
   - `QAudioSink` est initialisé une seule fois et reste actif en continu sur le périphérique audio.
   - La session audio matérielle (WASAPI sous Windows) ne doit JAMAIS être fermée, recréée, ni mise en pause entre deux morceaux.
   - En mode `buffer`, interdiction de réintroduire des doubles lecteurs matériels ou des alternances de volume sur l'OS.

2. **Tampon continu en mémoire (Ring Buffer)** :
   - Tout le mixage et les transitions s'opèrent au niveau des échantillons PCM dans `ContinuousAudioEngine` (`amso/services/audio_engine.py`).
   - `QAudioSink` lit le flux d'octets sans interruption en mode Push (`pump_audio`).

3. **Les 3 modes de transition dans le tampon** :
   - **Gapless 0** (`append_gapless`) : Les échantillons de la piste suivante sont concaténés directement à la suite du dernier échantillon de la piste courante. Décalage = 0.0 ms, aucun clic, aucun blanc.
   - **Crossfade** (`append_with_crossfade`) : Mixage mathématique à égale puissance (`gain_a = cos(t)`, `gain_b = sin(t)`) calculé directement sur les échantillons PCM dans la zone de chevauchement.
   - **Pas de fondu** (`append_with_silence`) : Injection d'un silence numérique (octets nuls `\x00`) dans le tampon pour marquer la pause entre pistes sans fermer la carte son.

4. **Décodage asynchrone** :
   - Le décodage extrait le PCM brut des fichiers locaux ou distants (NAS SMB) et l'injecte dans le tampon via `append_chunk` ou `play_track`.
   - Aucun son ne sort par le décodeur ; seule la sortie `QAudioSink` émet du son.
   - Les déclenchements temporels fixes (seuils en ms) pour simuler des enchaînements matériels ne concernent pas le mode buffer.

---

## Invariants de Transport & Anti-Déclenchement Intempestif (Communs aux deux moteurs)
Quel que soit le moteur audio sélectionné (`vlc_direct` ou `buffer`) :
1. **Piste précédente (`previous()`)** :
   - Si le lecteur est en pause, la commande doit charger la piste sans lancer la lecture (`load_index()`).
   - `play_index()` n'est invoqué que si le lecteur était déjà actif en lecture (`is_playing`).
2. **Déplacement temporel (`seek_ms`, `seek_ratio`) & Pause** :
   - Tout seek ou pause réinitialise immédiatement le préchargement standby (`_reset_standby_player()`) et annule les vidages matériels ou transitions en cours.
   - Sur une piste terminée (`State.Ended`), le seek ne doit jamais sauter à la piste suivante, mais replacer la tête de lecture sur le morceau actuel en respectant la pause.
3. **Changements de menus et modes exclusifs (Blind Test)** :
   - Quitter un écran exclusif (ex: Blind Test) vers un autre onglet impose la coupure immédiate de la lecture (`pause()`), l'arrêt des timers et la purge de tout préchargement en RAM/standby.
   - Aucun son ne doit se réveiller spontanément en arrière-plan après navigation.



---

## Pistes virtuelles CUE (moteur `buffer` uniquement)
- Une piste CUE est un `TrackRecord` avec `cue_start_ms` / `cue_end_ms` (portion de `source_path`, créé par `get_playlist_tracks`). `duration_seconds` est celle de la portion.
- Le moteur et l'UI travaillent dans le **temps relatif à la piste** (0 = début de la portion). Seul le décodage ajoute `cue_start_ms` (`:start-time`) et s'arrête à `cue_end_ms` (`:stop-time`) : toujours passer par `amso/services/player_cue.py` (`start_track_decode`, `stream_key`), jamais `decoder.start_decode(track.source_path, …)` directement.
- Le décodeur et le moteur identifient un flux par `stream_key(track)` (chemin + `#cue<début>`), pas par le chemin seul : deux portions d'un même fichier ne doivent jamais partager le même identifiant (sinon les blocs PCM de la piste suivante sont confondus avec ceux de la piste courante).
- `vlc_direct` reste figé : une piste CUE y est refusée avec un message (`play_index`), il ne lit jamais le fichier entier à sa place.
- Un test du décodage réel sur un `.cue` doit vérifier que la durée PCM obtenue égale celle de la portion (44100 Hz × 4 octets/s).
