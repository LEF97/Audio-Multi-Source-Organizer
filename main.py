"""Audio Multi-Source Organizer (AMSO) — Point d'entrée principal."""

import sys
from pathlib import Path

# S'assurer que le package amso est importable
sys.path.insert(0, str(Path(__file__).parent.resolve()))


def main() -> int:
    """Point d'entrée de l'application AMSO."""
    print("=" * 60)
    print("  Audio Multi-Source Organizer (AMSO) - v0.1.0")
    print("  Unificateur et organisateur de bibliothèques audio")
    print("=" * 60)
    print("\nInitialisation en cours...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
