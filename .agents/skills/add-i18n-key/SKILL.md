---
name: add-i18n-key
description: Ajouter ou modifier un texte d'interface traduit dans AMSO (clés tr() dans amso/locales/*.json, 5 langues fr/en/es/de/it). À utiliser dès qu'un nouveau libellé, message ou tooltip est créé.
---

# Ajouter une clé i18n

Fichiers : `amso/locales/{fr,en,es,de,it}.json`. **`fr.json` = source de vérité.**
Fonction : `from amso.core.i18n import tr` → `tr("section.cle", default="...", nom=valeur)`.

## Procédure
1. Choisir une clé hiérarchique cohérente avec l'existant (ex. `table.col_source_type`) : `grep_search` sur le préfixe dans `amso/locales/fr.json` pour reprendre la convention.
2. Ajouter la clé dans `fr.json` (à la bonne place thématique).
3. Ajouter la traduction dans `en.json`, `es.json`, `de.json`, `it.json`. Placeholders identiques dans toutes les langues (`{nom}`).
4. Synchronisation des traductions (au choix) :
   - **Mode classique (instantané) :** `python scripts/sync_translations.py` (ou `sync_translations.bat`).
   - **Mode IA locale (Ollama) :** `python scripts/sync_translations.py --ollama [MODELE]` (ou `sync_translations_ollama.bat` avec `mistral:latest`, `qwen3.8:latest`, etc.). Traduit automatiquement les clés manquantes en local.
   - Option `--check-only` pour vérifier l'alignement sans écrire.
5. Dans le code : `tr("ma.cle")` — jamais de texte en dur visible par l'utilisateur. Les textes déjà affichés doivent être rafraîchis au changement de langue (voir `amso/ui/pages/retranslate.py`).
6. Test : si le comportement est nouveau, ajouter un test dans `tests/`.

## Règles
- Ne pas modifier le JSON à la main au-delà des ajouts : laisser le script le reformater (UTF-8, indentation 2).
- Supprimer une clé = la retirer de `fr.json` puis lancer le script.
- Ne pas toucher aux fichiers `*.md` multilingues (voir skill `docs-sync`).
