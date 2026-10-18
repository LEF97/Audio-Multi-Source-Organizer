"""Script de vérification de synchronisation de la documentation multilingue (5 langues).

Langues prises en charge :
- Français (fr) : README.fr.md, CHANGELOG.fr.md, ROADMAP.fr.md
- Anglais (en / base) : README.md, CHANGELOG.md, ROADMAP.md
- Espagnol (es) : README.es.md, CHANGELOG.es.md, ROADMAP.es.md
- Allemand (de) : README.de.md, CHANGELOG.de.md, ROADMAP.de.md
- Italien (it) : README.it.md, CHANGELOG.it.md, ROADMAP.it.md

Usage:
    python scripts/check_docs_sync.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# UTF-8 stdout pour éviter les erreurs charmap cp1252 sous Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

LANGUAGES = ["fr", "en", "es", "de", "it"]

DOC_PATTERNS = {
    "README": {
        "fr": "README.fr.md",
        "en": "README.md",
        "es": "README.es.md",
        "de": "README.de.md",
        "it": "README.it.md",
    },
    "CHANGELOG": {
        "fr": "CHANGELOG.fr.md",
        "en": "CHANGELOG.md",
        "es": "CHANGELOG.es.md",
        "de": "CHANGELOG.de.md",
        "it": "CHANGELOG.it.md",
    },
    "ROADMAP": {
        "fr": "ROADMAP.fr.md",
        "en": "ROADMAP.md",
        "es": "ROADMAP.es.md",
        "de": "ROADMAP.de.md",
        "it": "ROADMAP.it.md",
    },
}

EXPECTED_ROADMAP_MILESTONES = [
    "0.1.0",
    "0.2.0",
    "0.3.0",
    "0.4.0",
    "0.5.0",
    "0.6.0",
    "1.0.0",
]


def check_docs(project_root: Path | None = None) -> list[str]:
    """Vérifie l'existence et la synchronisation de tous les fichiers de documentation.

    Retourne une liste d'erreurs (vide si tout est valide).
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.resolve()

    errors: list[str] = []

    # 1. Vérification de l'existence des 15 fichiers
    for doc_type, lang_map in DOC_PATTERNS.items():
        for lang, filename in lang_map.items():
            filepath = project_root / filename
            if not filepath.exists():
                errors.append(f"[{doc_type}] Fichier manquant pour la langue '{lang}' : {filename}")

    if errors:
        return errors

    # Récupérer la version courante depuis amso/__init__.py
    init_file = project_root / "amso" / "__init__.py"
    current_version = "0.0.0"
    if init_file.exists():
        content = init_file.read_text(encoding="utf-8")
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            current_version = match.group(1)

    # 2. Vérification des CHANGELOG
    for filename in DOC_PATTERNS["CHANGELOG"].values():
        filepath = project_root / filename
        text = filepath.read_text(encoding="utf-8")

        # Vérifier la présence du header de navigation des 5 langues
        if not all(code in text for code in ["Français", "English", "Español", "Deutsch", "Italiano"]):
            errors.append(f"[{filename}] La barre de navigation multilingue est incomplète.")

        # Vérifier la version courante (ou dev)
        if "-dev" in current_version:
            if f"[{current_version}]" not in text:
                errors.append(f"[{filename}] Section de développement [{current_version}] manquante.")
        else:
            if f"[{current_version}]" not in text:
                errors.append(f"[{filename}] Section de release [{current_version}] manquante.")

        # Vérifier que les versions publiées antérieures majeures sont présentes
        for released in ["0.1.0", "0.2.0", "0.3.0"]:
            if f"[{released}]" not in text:
                errors.append(f"[{filename}] Version publiée [{released}] manquante dans le changelog.")

    # 3. Vérification des ROADMAP
    for filename in DOC_PATTERNS["ROADMAP"].values():
        filepath = project_root / filename
        text = filepath.read_text(encoding="utf-8")

        # Vérifier la navigation
        if not all(code in text for code in ["Français", "English", "Español", "Deutsch", "Italiano"]):
            errors.append(f"[{filename}] La barre de navigation multilingue est incomplète.")

        # Vérifier que tous les jalons sont mentionnés
        for milestone in EXPECTED_ROADMAP_MILESTONES:
            if milestone not in text:
                errors.append(f"[{filename}] Jalon {milestone} introuvable dans la feuille de route.")

        # Vérifier le format à cases à cocher (- [x] et - [ ])
        if "- [x]" not in text or "- [ ]" not in text:
            errors.append(f"[{filename}] Format incohérent : cases à cocher markdown (- [x] / - [ ]) manquantes.")

    # 4. Vérification des README
    for filename in DOC_PATTERNS["README"].values():
        filepath = project_root / filename
        text = filepath.read_text(encoding="utf-8")

        # Navigation
        if not all(code in text for code in ["Français", "English", "Español", "Deutsch", "Italiano"]):
            errors.append(f"[{filename}] La barre de navigation multilingue est incomplète.")

        # Vérification des screenshots v0.3.0
        expected_screenshots = [
            "screenshots/2026-10-18%20v0.3.0%2002.png",
            "screenshots/2026-10-18%20v0.3.0.png",
            "screenshots/2026-10-18%20v0.3.0%20blind%20test.png",
        ]
        for shot in expected_screenshots:
            if shot not in text:
                errors.append(f"[{filename}] Capture d'écran attendue absente : {shot}")

        # Vérification des liens de documentation
        if "CHANGELOG" not in text or "ROADMAP" not in text or "CODE_QUALITY" not in text:
            errors.append(f"[{filename}] Liens de documentation essentiels manquants (CHANGELOG/ROADMAP/CODE_QUALITY).")

    return errors


def main() -> int:
    project_root = Path(__file__).parent.parent.resolve()
    print("=" * 65)
    print("  AMSO — Vérification de la synchronisation de la documentation")
    print(f"  Répertoire : {project_root}")
    print("  Langues    : FR, EN, ES, DE, IT (15 fichiers)")
    print("=" * 65)

    errors = check_docs(project_root)

    if errors:
        print("\n❌ DES ERREURS DE SYNCHRONISATION ONT ÉTÉ DÉTECTÉES :\n")
        for err in errors:
            print(f"  • {err}")
        print("\n" + "!" * 65)
        print("  ÉCHEC : Veuillez corriger les fichiers avant de continuer.")
        print("!" * 65)
        return 1

    print("\n✅ SUCCÈS : Tous les fichiers de documentation (README, CHANGELOG,")
    print("            ROADMAP) sont parfaitement synchronisés en 5 langues !")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())
