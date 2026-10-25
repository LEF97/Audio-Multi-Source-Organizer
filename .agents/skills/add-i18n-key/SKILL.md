---
name: add-i18n-key
description: Ajouter ou modifier un texte d'interface traduit dans AMSO (clés tr() dans amso/locales/*.json, 43 langues, `fr` = source). À utiliser dès qu'un nouveau libellé, message ou tooltip est créé.
---

# Ajouter une clé i18n

Fichiers : `amso/locales/<code>.json` (43 langues : fr, en, es, de, it, ja, ru…). **`fr.json` = source de vérité.**
Fonction : `from amso.core.i18n import tr` → `tr("section.cle", default="...", nom=valeur)`.

## Procédure
0. **Anti-duplication :** Lancer `scripts/audit_translations.bat` ou faire un `grep_search` dans `amso/locales/fr.json` pour vérifier si le libellé exact ou équivalent n'existe pas déjà (ex. actions réutilisables `common.cancel`, `common.refresh`, `common.close`, en-têtes de colonnes `table.col_*`). Réutiliser la clé existante si possible.
1. Choisir une clé hiérarchique cohérente avec l'existant (ex. `table.col_source_type`) : `grep_search` sur le préfixe dans `amso/locales/fr.json` pour reprendre la convention.
2. **Ajouter la clé EXCLUSIVEMENT dans `fr.json`** (à la bonne place thématique). En cours de développement au fil de l'eau, **ne pas modifier les autres fichiers de langues (`en`, `es`, `de`, `it`...) ni lancer de synchronisation**.
3. Dans le code : `tr("ma.cle")` — jamais de texte en dur visible par l'utilisateur. Les textes déjà affichés doivent être rafraîchis au changement de langue (voir `amso/ui/pages/retranslate.py`).
4. Test : si le comportement est nouveau, ajouter un test dans `tests/`.

## Traduction des autres langues (Pré-release ou demande explicite uniquement)
Ne JAMAIS traduire ni synchroniser au fil de l'eau sur chaque petite tâche. Lors d'une release ou sur demande explicite de l'utilisateur :
- **Mode IA locale (Ollama) :** `python scripts/sync_translations.py --ollama [MODELE]` (ou `scripts/sync_all_languages_ollama.bat`).
- **Mode classique (alignement) :** `python scripts/sync_translations.py`.
- Option `--check-only` pour vérifier l'alignement sans écrire.

## Règles
- En développement courant : **SEUL `fr.json` est modifié**.
- Ne pas toucher aux fichiers `*.md` multilingues (voir skill `docs-sync`).
