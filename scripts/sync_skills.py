"""Synchronisation bidirectionnelle des skills Gemini (.agents/skills) et Claude (.claude/skills).

Usage:
    python scripts/sync_skills.py [--dry-run] [--prefer {newest,agents,claude}] [--prune]

Principe (fusion à 3 voies) : l'état de la dernière synchro (hash par fichier) est mémorisé
dans .claude/.skills_sync.json. Pour chaque fichier :
- identique des deux côtés -> rien à faire ;
- modifié d'un seul côté depuis la dernière synchro -> copié vers l'autre côté ;
- modifié des DEUX côtés (conflit) -> rien n'est écrasé, sauf si --prefer est fourni
  (newest = date de modification la plus récente, agents = Gemini gagne, claude = Claude gagne) ;
- supprimé d'un côté -> signalé ; propagé seulement avec --prune.
Code de sortie 0 : OK ; 1 : conflits restants.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIDES = {"agents": ROOT / ".agents" / "skills", "claude": ROOT / ".claude" / "skills"}
STATE = ROOT / ".claude" / ".skills_sync.json"


def _hash(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def _relpaths() -> set[str]:
    return {
        p.relative_to(base).as_posix()
        for base in SIDES.values()
        if base.exists()
        for p in base.rglob("*")
        if p.is_file()
    }


def _copy(src: Path, dst: Path, dry: bool) -> None:
    if not dry:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def _remove(path: Path, dry: bool) -> None:
    if not dry:
        path.unlink()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="n'écrit rien, affiche seulement")
    ap.add_argument("--prefer", choices=["newest", "agents", "claude"], help="résolution des conflits")
    ap.add_argument("--prune", action="store_true", help="propage aussi les suppressions")
    args = ap.parse_args()

    state: dict[str, str] = json.loads(STATE.read_text("utf-8")) if STATE.exists() else {}
    new_state: dict[str, str] = {}
    conflicts = 0

    for rel in sorted(_relpaths()):
        a_path, c_path = SIDES["agents"] / rel, SIDES["claude"] / rel
        a, c, s = _hash(a_path), _hash(c_path), state.get(rel)
        if a == c:
            new_state[rel] = a  # type: ignore[assignment]
            continue
        action: tuple[Path, Path] | None = None
        label = ""
        if a is None or c is None:  # absent d'un côté
            src, dst = (c_path, a_path) if a is None else (a_path, c_path)
            present = c if a is None else a
            if s is None or s != present:  # nouveau fichier, ou modifié puis supprimé de l'autre côté
                action, label = (src, dst), "nouveau"
            elif args.prune:  # supprimé volontairement de l'autre côté, inchangé ici
                print(f"SUPPR  {src.relative_to(ROOT)}")
                _remove(src, args.dry_run)
                continue
            else:
                print(f"?      {rel} supprimé d'un côté (utiliser --prune pour propager)")
                new_state[rel] = present  # type: ignore[assignment]
                continue
        elif c == s:
            action, label = (a_path, c_path), "Gemini -> Claude"
        elif a == s:
            action, label = (c_path, a_path), "Claude -> Gemini"
        else:
            winner = args.prefer
            if winner == "newest":
                winner = "agents" if a_path.stat().st_mtime >= c_path.stat().st_mtime else "claude"
            if winner is None:
                print(f"CONFLIT {rel} (modifié des deux côtés, aucun écrasement)")
                conflicts += 1
                if s:
                    new_state[rel] = s
                continue
            action = (a_path, c_path) if winner == "agents" else (c_path, a_path)
            label = f"conflit résolu ({winner})"
        src, dst = action
        print(f"COPIE  {rel}  [{label}]")
        _copy(src, dst, args.dry_run)
        new_state[rel] = _hash(src)  # type: ignore[assignment]

    if not args.dry_run:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps(new_state, indent=1, sort_keys=True), "utf-8")
    print(f"Terminé : {conflicts} conflit(s).")
    return 1 if conflicts else 0


if __name__ == "__main__":
    sys.exit(main())
