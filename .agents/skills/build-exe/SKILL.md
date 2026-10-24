---
name: build-exe
description: Compiler l'exécutable AMSO avec PyInstaller (scripts/build_exe.py), diagnostiquer un exécutable qui plante ou qui perd ses ressources (locales, icônes, VLC, plugins Qt). À utiliser pour tout build, problème de packaging ou ajout de ressource embarquée.
---

# Build de l'exécutable

## Commandes
- Build dossier (défaut) : `python scripts/build_exe.py` (ou `scripts\build_exe.bat`).
- Fichier unique portable : `python scripts/build_exe.py --onefile` (vérifier l'option dans `scripts/build_exe.py`).
- Sortie : `dist/` (travail dans `build/`). Ne jamais lire ni lister `dist/`, `build/`, `*.spec`.
- Le script ferme `AMSO.exe` s'il tourne (verrous de fichiers) ; fermer l'appli avant de compiler.

## Ressources embarquées
Le script passe `--add-data` pour `amso/locales` et `amso/resources` (dans `amso/…` et à la racine), plus l'icône selon l'OS (`icon.ico` Windows, `resources/icon.icns` macOS, `resources/icon.png` Linux). Une nouvelle ressource : l'ajouter au script **et** à `[tool.setuptools.package-data]` de `pyproject.toml`.

## Chemins à l'exécution
Code qui lit un fichier embarqué : résoudre via `sys._MEIPASS` si `getattr(sys, "frozen", False)`, sinon le dossier du package ; jamais de chemin relatif au répertoire courant.

## Diagnostic d'un exécutable défaillant
1. Lancer l'exe depuis un terminal pour lire la trace (le build est `--windowed`, sans console).
2. Module introuvable → `--hidden-import=<module>` (imports dynamiques) ; plugin Qt manquant → `--collect-all PySide6` en dernier recours (alourdit le build).
3. Textes non traduits ou clés brutes → dossier `locales` non embarqué.
4. VLC : `python-vlc` a besoin de VLC installé ou téléchargé (voir `amso/services/vlc_downloader.py`) ; ne pas embarquer VLC sans validation de licence.
5. Tester sur une machine/session propre avant publication (validation manuelle exigée par la release, skill `release`).

## Après build
Ne pas committer `dist/` ni `build/`. Pour la release : skill `release`.
