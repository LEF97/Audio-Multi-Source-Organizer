---
name: docs-sync
description: Mise à jour de la documentation multilingue AMSO (README, CHANGELOG, ROADMAP, RELEASE_PROCESS en FR/EN/ES/DE/IT, soit 15 fichiers). À utiliser uniquement pour une release ou sur demande explicite de modifier la doc.
---

# Synchronisation de la documentation multilingue

Fichiers : `README.fr.md` et `README.md` (racine), `docs/i18n/README.<code>.md` (41 langues, dont es/de/it), `CHANGELOG.fr.md`, `CHANGELOG.md`, `ROADMAP.fr.md`, `ROADMAP.md` (racine) et `docs/i18n/CHANGELOG.{es,de,it}.md`, `docs/i18n/ROADMAP.{es,de,it}.md` (+ `RELEASE_PROCESS.fr.md`, français seul).

## Qui traduit quoi (règle stricte)
- `fr` : source de vérité, rédigée au fil de l'eau.
- `en` : SEULE langue traduite par un assistant IA (Claude), depuis `*.fr.md`, à la release (README, CHANGELOG, ROADMAP).
- **Toutes les autres langues, Ollama uniquement** : `python scripts/translate_docs.py --ollama` (ou `scripts\translate_docs.bat`, modèle par défaut `gemma4:latest`) traduit README (41 langues), CHANGELOG et ROADMAP (es, de, it). Jamais de traduction manuelle par Claude ou Gemini pour ces langues, et jamais d'édition à la main des fichiers générés. Options : `--docs README`, `--lang ja`, `--force`, `--nav-only` (régénère seulement les sélecteurs de langue, bloc entre `<!-- lang-nav:start -->` et `<!-- lang-nav:end -->`, à ne pas modifier à la main).
- Chaque bloc traduit est validé (liens, versions/dates, structure) ; les blocs invalides restent en français et le script signale `fragment(s) laissé(s) en français` : relancer (le cache évite de tout retraduire) ou signaler à l'utilisateur.

- **Au fil de l'eau :** Les versions françaises (`*.fr.md`) sont la source de vérité et sont mises à jour au fur et à mesure des développements.
- **À la release uniquement :** `en` (assistant) puis les autres langues (Ollama) sont traduites et synchronisées lors de la préparation de la release.

## Procédure
1. Éditer d'abord la version française (`*.fr.md`), qui sert de référence.
2. Ne lire que les sections concernées (grep sur le titre `## [`, ou le badge/numéro de ligne), pas les 15 fichiers entiers.
3. Ne rien reporter à la main dans les autres langues : à la release, traduire `en` depuis `fr`, puis lancer `translate_docs.py --ollama --lang es de it` (Ollama démarré). **Attendre la validation de l'utilisateur sur les 5 langues (fr, en, es, de, it)** avant de lancer `translate_docs.py --ollama` pour les 38 autres langues.
4. Lancer `python scripts/check_docs_sync.py` (`--release` à la release : exige les 43 README) : il détecte les écarts de structure et un sélecteur de langue obsolète. Corriger jusqu'à succès (bloquant en CI).
5. Si le script échoue 2 fois avec la même erreur, arrêter et expliquer.

## Conventions
- CHANGELOG : `## [X.Y.Z-dev] - AAAA-MM-JJ` en tête pendant le développement ; clôturé en `## [X.Y.Z]` à la release.
- README : liens relatifs (`../../` dans `docs/i18n/`), 13 lignes de fonctionnalités, captures selon `screenshots/*vX.Y.Z*.png` et `screenshots/Global*.png`.
- ROADMAP : cocher les objectifs atteints, réajuster les jalons.
- Les textes d'interface se traduisent via le skill `add-i18n-key`, pas ici.
