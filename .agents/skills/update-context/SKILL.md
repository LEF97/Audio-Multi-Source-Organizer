---
name: update-context
description: Mettre à jour context.md (référence unique d'architecture et d'état du projet AMSO). À utiliser dès qu'un module/dossier est créé, déplacé, renommé ou supprimé, qu'une version change d'état, ou quand `check_context.py` signale des éléments absents.
---

# Maintenir context.md

`context.md` est lu par tous les assistants au démarrage : une information fausse ici est pire qu'une information absente.

## Quand
- Module ou dossier créé / déplacé / renommé / supprimé dans `amso/core`, `amso/core/db`, `amso/services` ou `amso/ui` (typiquement après `split-module` ou `add-source-connector`).
- Nouveau script dans `scripts/`, changement de stack, de moteur audio, de langues supportées.
- Début ou clôture d'une version (étapes 2 et 4 du skill `release`) : tableau « Vision & état ».
- Sortie en échec de `python scripts/check_context.py` (aussi exécuté par `scripts/verify.py`).

## Procédure
1. `python scripts/check_context.py` : liste ce qui manque.
2. Éditer uniquement la section concernée de `context.md` (§3 Architecture : une ligne par module, 5 à 10 mots de rôle ; §1 état des versions ; §7 points d'attention).
3. Retirer les points d'attention résolus (§7) ; ne jamais y noter d'état de travail éphémère (cela relève du CHANGELOG).
4. Garder le fichier court (< 150 lignes) : pas de détail d'implémentation, renvoyer vers le skill ou le fichier concerné.
5. Relancer `python scripts/check_context.py` jusqu'à succès.

## À ne pas faire
- Ne pas dupliquer les règles de `GEMINI.md` ni les procédures des skills : y renvoyer.
- Ne pas modifier les docs multilingues (skill `docs-sync`).
