# Plan d'Architecture : Serveur Web Embarqué & Client Android pour AMSO

Date : 21 octobre 2026  
Statut : Proposition validée, à reprendre lors d'un prochain cycle de développement.

---

## 1. Vision et Objectifs

- **PC Maître (Inchangé)** : AMSO reste une application native PySide6 avec son moteur complet (lecture VLC, scan disque lourd, tagger Mutagen, SQLite local, drag-and-drop).
- **Serveur Web Local (Intégré)** : Un serveur HTTP/WebSocket léger tourne en arrière-plan dans AMSO pour exposer l'API et servir une interface web accessible depuis le réseau local (Wi-Fi).
- **Client Android** : Une application mobile (PWA ou packagée via Capacitor) qui découvre automatiquement le Maître sur le réseau local, permet de naviguer dans la bibliothèque, de lancer la lecture (en local ou en streaming) et de contrôler le lecteur du PC.

---

## 2. Découpage par Phases

### Phase 1 : Cœur du Serveur & API REST (Backend)
1. **Technologie** : `FastAPI` + `uvicorn` (ou `aiohttp`) exécuté dans un thread Python dédié (non bloquant pour l'UI PySide6).
2. **Endpoints prioritaires** :
   - `GET /api/status` : État d'AMSO (version, bibliothèque chargée, lecteur en cours).
   - `GET /api/tracks` : Recherche et pagination des pistes (filtres artiste, album, genre).
   - `GET /api/playlists` : Liste et contenu des playlists.
   - `GET /api/stream/{track_id}` : Streaming audio avec support HTTP Range (`206 Partial Content`) pour permettre l'avance/retour rapide dans les morceaux.
   - `POST /api/player/{action}` : Contrôle de lecture à distance (play, pause, next, volume).
3. **Sécurité locale** : Token d'accès optionnel ou code PIN généré dans les paramètres pour éviter les accès non désirés sur un réseau partagé.

---

### Phase 2 : Intégration dans l'interface PySide6 (PC)
1. **Préférence "Serveur Web"** (activée par défaut) :
   - Case à cocher "Activer l'accès distant / web".
   - Choix du port (ex: `8080` par défaut).
2. **Indicateur visuel (Barre d'état ou Page Paramètres)** :
   - Affichage de l'URL d'accès : `http://<IP_LOCALE>:8080`.
   - Bouton "Copier le lien" et bouton "Ouvrir dans le navigateur".
   - Affichage optionnel d'un QR code pour connexion instantanée depuis un smartphone.

---

### Phase 3 : Découverte automatique sur le réseau (mDNS / Zeroconf)
1. Intégration de la bibliothèque `zeroconf` côté Python.
2. Annonce du service sur le réseau local : `_amso._tcp.local.`.
3. Permet aux applications clientes (et à l'application Android) de trouver l'adresse IP et le port du PC sans que l'utilisateur n'ait à chercher son adresse IP manuellement.

---

### Phase 4 : Front Web Léger (Web UI)
1. **Technologie** : HTML5 / CSS vanilla moderne (ou composant Svelte/Vue léger) servi depuis `amso/server/static/`.
2. **Pages clés** :
   - Lecteur / Télécommande (pochette, titre, barre de progression, contrôles).
   - Explorateur de bibliothèque (recherche rapide, vue par artiste/album/playlist).
   - Mode Blind Test mobile (pour jouer depuis son téléphone connecté au salon).
3. **Responsive design** : Interface optimisée aussi bien pour navigateur PC que pour écran de smartphone.

---

### Phase 5 : Application Android
1. **Étape 1 (Rapide)** : PWA (Progressive Web App) installable directement depuis le navigateur du smartphone.
2. **Étape 2 (Complète)** : Wrapper mobile avec **Capacitor** (Ionic) :
   - Découverte automatique du PC via mDNS.
   - Intégration aux contrôles audio système d'Android (`MediaSession` : écran de verrouillage, boutons du casque Bluetooth).
   - Option de mise en cache / téléchargement hors-ligne de playlists sur le stockage du téléphone.

---

## 3. Dépendances prévues à intégrer au `pyproject.toml`

- `fastapi` & `uvicorn` (serveur API performant et asynchrone).
- `zeroconf` (découverte automatique réseau).
- (Optionnel) `qrcode` (génération de QR code dans l'UI Qt pour appairage rapide).

---

## 4. Comment reprendre ce plan le moment venu ?

Il suffira d'indiquer dans une prochaine session :
> *"On reprend le plan décrit dans `docs/plan_serveur_web_android.md` en commençant par la Phase 1."*
