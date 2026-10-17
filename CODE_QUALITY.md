# Stack d'Aide au Coding & Audit Qualité de Code - AMSO

Ce document recense l'ensemble de la boîte à outils mise en place sur **Audio Multi-Source Organizer (AMSO)** pour garantir la robustesse, la propreté, la maintenabilité et les performances du code.

Il sert de référence pour **reproduire et réinstaller à l'identique cet environnement sur une nouvelle machine**.

---

## 1. Vue d'Ensemble de la Stack

La stack combine des outils d'analyse statique ultra-rapides en ligne de commande (exécutables par vous ou par l'agent IA) et des extensions d'assistance visuelle directement intégrées à l'IDE (VS Code / Antigravity IDE).

| Outil | Type | Rôle principal | Configuration / Commande |
| :--- | :--- | :--- | :--- |
| **[SonarLint](https://www.sonarsource.com/products/sonarlint/)** | Extension IDE | Détection en temps réel des *Code Smells*, failles de sécurité, régressions et complexités sans nécessiter de serveur SonarQube | ID extension : `SonarSource.sonarlint-vscode` |
| **[Ruff](https://astral.sh/ruff)** | Extension IDE + CLI (Rust) | Linter et formateur moderne ultra-rapide (remplace Flake8, Black, isort, Bandit). Traque les imports orphelins, syntaxe obsolète, bugs et variables inutilisées | `ruff check amso/`<br>`ruff format amso/` |
| **[Mypy](https://mypy-lang.org/)** | Extension IDE + CLI | Vérificateur statique de typage. Prévient les erreurs de type à l'exécution (`AttributeError`, `NoneType`, mauvais arguments) | `mypy amso/` |
| **[Radon](https://radon.readthedocs.io/)** | CLI Python | Analyse de la complexité cyclomatique des fonctions et classes (notes de A à F) pour cibler le refactoring | `radon cc amso/ -s -a -n C` |
| **pytest-cov** | CLI Python | Mesure et rapport de couverture de tests ligne par ligne | `pytest --cov=amso --cov-report=term-missing` |

---

## 2. Procédure de Réinstallation sur une Nouvelle Machine

En cas de changement de poste ou de réinstallation complète, suivez ces étapes :

### Étape A : Cloner le dépôt et initialiser l'environnement virtuel Python
```bash
git clone <URL_DU_DEPOT>
cd "02 Audio Multi-Source Organizer"

# Création du venv Python (Python 3.11 ou 3.13 recommandé)
python -m venv .venv

# Activation du venv
# Sous Windows (PowerShell) :
.venv\Scripts\Activate.ps1
# Sous Windows (CMD) :
.venv\Scripts\activate.bat
# Sous Linux / macOS :
source .venv/bin/activate
```

### Étape B : Installer les dépendances du projet et la stack qualité
Une seule commande suffit grâce au fichier `requirements-dev.txt` :
```bash
pip install -r requirements-dev.txt
```
*(Alternative si vous utilisez le paquet éditable : `pip install -e .[dev]`)*.

### Étape C : Installer les extensions IDE recommandées
Le fichier `.vscode/extensions.json` suggère automatiquement les extensions nécessaires à l'ouverture du dossier. 

Vous pouvez également les installer en une seule ligne de commande :
```bash
# Pour VS Code :
code --install-extension SonarSource.sonarlint-vscode
code --install-extension charliermarsh.ruff
code --install-extension ms-python.mypy-type-checker

# (Ou sous Antigravity IDE, installez ces 3 IDs depuis le panneau Extensions)
```

---

## 3. Configuration & Fichiers Associés

* **[pyproject.toml](file:///x:/Projets/05%20Mes%20projets%20Outils%20et%20Sites/02%20Audio%20Multi-Source%20Organizer/pyproject.toml)** :
  * `[tool.ruff]` : configuration du linter (longueur de ligne max 120, exclusions automatiques pour `_work/` et répertoires temporaires).
  * `[tool.mypy]` : options de typage statique (`ignore_missing_imports = true`, etc.).
  * `[tool.pytest.ini_options]` : chemins et filtres de tests.
* **[.vscode/extensions.json](file:///x:/Projets/05%20Mes%20projets%20Outils%20et%20Sites/02%20Audio%20Multi-Source%20Organizer/.vscode/extensions.json)** : liste des identifiants d'extensions partagés pour l'équipe / le projet.
* **[scripts/audit_code_quality.bat](file:///x:/Projets/05%20Mes%20projets%20Outils%20et%20Sites/02%20Audio%20Multi-Source%20Organizer/scripts/audit_code_quality.bat)** : script Windows automatisant les 4 étapes de l'audit complet.

---

## 4. Commandes d'Analyse et Raccourcis Usuels

### Lancer l'audit complet en 1 clic
Exécutez simplement :
```cmd
scripts\audit_code_quality.bat
```

### Commandes individuelles

| Action souhaitée | Commande à exécuter |
| :--- | :--- |
| **Vérifier le linting** | `.venv\Scripts\ruff.exe check amso/` |
| **Corriger automatiquement le code (safe fixes)** | `.venv\Scripts\ruff.exe check --fix amso/` |
| **Formater tout le code source** | `.venv\Scripts\ruff.exe format amso/` |
| **Vérifier les types** | `.venv\Scripts\mypy.exe amso/` |
| **Voir les fonctions les plus complexes (rang C, D, E, F)** | `.venv\Scripts\radon.exe cc amso/ -s -a -n C` |
| **Calculer l'indice de maintenabilité (MI)** | `.venv\Scripts\radon.exe mi amso/ -s` |
| **Lancer tous les tests avec rapport de couverture** | `.venv\Scripts\pytest.exe --cov=amso --cov-report=term-missing` |
