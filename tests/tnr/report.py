"""Journal horodaté d'une exécution de la TNR : console + fichier `tests/tnr/log/tnr_AAAA-MM-JJ_HH-MM-SS.log`.

Le fichier reçoit aussi les messages Qt (avertissements natifs du type « Timers cannot be stopped from another
thread ») et les journaux Python du lecteur, qui n'apparaissent sinon que dans la console, ou nulle part.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import TextIO

from PySide6.QtCore import QMessageLogContext, QtMsgType, qInstallMessageHandler

from tests.tnr.scenario import ScenarioResult

LOG_DIR = Path(__file__).resolve().parent / "log"
MAX_LISTED_EVENTS = 10


class TnrReport:
    def __init__(self) -> None:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.path = LOG_DIR / f"tnr_{datetime.now():%Y-%m-%d_%H-%M-%S}.log"
        self._file: TextIO = self.path.open("w", encoding="utf-8", buffering=1)

    def line(self, text: str = "") -> None:
        print(text, flush=True)
        self._file.write(f"{text}\n")

    def capture_diagnostics(self) -> None:
        """Dirige vers le journal les messages Qt et les logs Python (niveau INFO) émis pendant la TNR."""
        handler = logging.StreamHandler(self._file)
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s : %(message)s", "%H:%M:%S"))
        root = logging.getLogger()
        root.addHandler(handler)
        root.setLevel(logging.INFO)
        qInstallMessageHandler(self._on_qt_message)

    def _on_qt_message(self, kind: QtMsgType, _context: QMessageLogContext, message: str) -> None:
        self.line(f"[Qt {kind.name}] {message}")

    def header(self, argv: list[str], tracks: tuple[Path, Path], modes: list[str], fade_s: int) -> None:
        from amso import __version__
        from amso.services.player_service import vlc

        self.line(f"TNR des transitions audio - {datetime.now():%Y-%m-%d %H:%M:%S}")
        self.line(f"commande : {' '.join(argv)}")
        self.line(f"AMSO {__version__}, commit {_git_state()}, Python {sys.version.split()[0]}")
        self.line(f"LibVLC {vlc.libvlc_get_version().decode(errors='replace')}")
        for label, track in zip(("A", "B"), tracks, strict=True):
            self.line(f"piste {label} : {track} ({track.stat().st_size / 1_048_576:.1f} Mo)")
        self.line(f"modes : {', '.join(modes)} ; fondu {fade_s} s")

    def scenario(self, result: ScenarioResult) -> None:
        self.line(f"durée {result.wall_seconds:.0f} s, intervalle de pompage max {result.max_pump_gap_ms:.0f} ms")
        self.line(
            f"  lecture de A depuis {result.start_ms / 1000:.2f} s demandée ; sortie enregistrée "
            f"{len(result.output) / 44100:.2f} s ; sortie matérielle : {result.sink_starts} ouverture(s), "
            f"{result.sink_stops} fermeture(s) pendant la lecture"
        )
        for index, position_ms in result.track_changes:
            self.line(f"  piste {index} annoncée à {position_ms / 1000:.2f} s de sortie")
        for underrun in result.underruns[:MAX_LISTED_EVENTS]:
            self.line(f"  coupure de {underrun.duration_ms:.0f} ms à {underrun.output_ms / 1000:.2f} s de sortie")
        if len(result.underruns) > MAX_LISTED_EVENTS:
            self.line(f"  ... {len(result.underruns) - MAX_LISTED_EVENTS} autre(s) coupure(s)")

    def close(self) -> None:
        self._file.close()


def _git_state() -> str:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=10, check=True
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10, check=True
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "inconnu"
    return f"{commit}{' (modifications non commitées)' if dirty else ''}"
