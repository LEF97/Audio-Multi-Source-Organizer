"""Non-régression des transitions audio (moteur `buffer`) sur deux pistes réelles.

Rejoue la fin de la piste A puis le début de la piste B dans le vrai `PlayerService`, avec une sortie audio factice
qui enregistre ce qui serait joué, et compare à une construction idéale issue d'un décodage de référence.
Par défaut : Sirius -> Eye in the Sky (Alan Parsons Project, 1982), copie `_work/tnr/` sinon NAS ; remplaçable par `--a` / `--b`
ou par les variables AMSO_TNR_TRACK_A / AMSO_TNR_TRACK_B.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
# Copie locale (dossier ignoré par git) : indépendante du NAS, dont les micro-coupures faussent la mesure
LOCAL_DIR = REPO_ROOT / "_work" / "tnr"
NAS_DIR = Path("//NASLEF97/Audio/Par artiste/Alan Parsons Project/1982 - Eye In The Sky")
DEFAULT_DIR = LOCAL_DIR if (LOCAL_DIR / "01 - Sirius.flac").is_file() else NAS_DIR
DEFAULT_A = DEFAULT_DIR / "01 - Sirius.flac"
DEFAULT_B = DEFAULT_DIR / "02 - Eye In The Sky.flac"
MODES = ("standard", "gapless", "crossfade")


def _isolate_environment() -> None:
    """Config et base jetables : la TNR ne doit jamais toucher %APPDATA%/AMSO de l'utilisateur."""
    data_dir = Path(tempfile.mkdtemp(prefix="amso_tnr_"))
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["AMSO_DATA_DIR"] = str(data_dir)
    os.environ["AMSO_CONFIG_PATH"] = str(data_dir / "config.ini")
    os.environ["AMSO_PLAYLIST_PATH"] = str(data_dir / "saved_playlist.json")
    os.environ["AMSO_DB_PATH"] = str(data_dir / "amso_library.db")
    sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--a", type=Path, default=Path(os.environ.get("AMSO_TNR_TRACK_A", DEFAULT_A)))
    parser.add_argument("--b", type=Path, default=Path(os.environ.get("AMSO_TNR_TRACK_B", DEFAULT_B)))
    parser.add_argument("--modes", nargs="+", choices=MODES, default=list(MODES))
    parser.add_argument("--fade", type=int, default=10, help="durée du crossfade en secondes")
    args = parser.parse_args()

    for path in (args.a, args.b):
        if not path.is_file():
            print(f"Fichier introuvable : {path}")
            return 2
    _isolate_environment()

    from amso.services.player_service import vlc
    from tests.tnr.analysis import evaluate
    from tests.tnr.reference import load_reference
    from tests.tnr.report import TnrReport
    from tests.tnr.scenario import run_transition

    if not vlc.available:
        print("VLC indisponible : la TNR utilise le décodeur LibVLC du moteur à tampon.")
        return 2
    report = TnrReport()
    try:
        report.capture_diagnostics()
        report.header(sys.argv, (args.a, args.b), args.modes, args.fade)
        report.line("\nDécodage de référence (mis en cache)...")
        ref_a, ref_b = load_reference(args.a), load_reference(args.b)

        failures = 0
        for mode in args.modes:
            report.line(f"\n=== {mode} (fondu {args.fade} s) ===")
            result = run_transition(args.a, args.b, mode, fade_s=args.fade)
            report.scenario(result)
            for check in evaluate(result, ref_a, ref_b):
                report.line(f"  [{'OK' if check.ok else 'ECHEC'}] {check.name} : {check.detail}")
                failures += not check.ok
        report.line(f"\n{'TOUT EST CONFORME' if not failures else f'{failures} contrôle(s) en échec'}")
        report.line(f"Journal : {report.path}")
    except Exception:
        report.line(traceback.format_exc())
        raise
    finally:
        report.close()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
