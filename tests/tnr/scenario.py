"""Rejoue une transition entre deux pistes réelles dans le vrai `PlayerService`, avec une sortie audio factice."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

import mutagen
import numpy as np
from PySide6.QtCore import QCoreApplication

from amso.core.config import get_config_manager
from amso.core.database import TrackRecord
from amso.core.pcm_mixer import SAMPLE_RATE
from amso.services.player_service import PlayerService
from tests.tnr.capture_sink import CaptureSink, Underrun

PUMP_GAP_REPORT_MS = 150.0


@dataclass(slots=True)
class ScenarioResult:
    mode: str
    fade_s: int
    start_ms: int
    output: np.ndarray
    underruns: list[Underrun]
    sink_starts: int
    sink_stops: int
    max_pump_gap_ms: float
    reached_second_track: bool
    wall_seconds: float
    track_changes: list[tuple[int, float]] = field(default_factory=list)  # (index, position de sortie en ms)


def make_track(path: Path) -> TrackRecord:
    info = mutagen.File(path)
    if info is None:
        raise ValueError(f"Fichier audio illisible : {path}")
    length = float(info.info.length)
    return TrackRecord(source_ref=str(path), source_path=str(path), title=path.stem, duration_seconds=length)


def _install_pump_probe(player: PlayerService, gaps: list[float]) -> None:
    original = player._engine.pump_audio
    last = [0.0]

    def probed() -> None:
        now = time.monotonic()
        if last[0]:
            gaps.append((now - last[0]) * 1000.0)
        last[0] = now
        original()

    player._engine.pump_audio = probed


def run_transition(
    path_a: Path, path_b: Path, mode: str, fade_s: int = 10, lead_s: float = 25.0, post_s: float = 14.0
) -> ScenarioResult:
    """Lit la fin de A (`lead_s` avant la fin) puis le début de B, et enregistre la sortie audio."""
    app = QCoreApplication.instance() or QCoreApplication([])
    cfg = get_config_manager()
    cfg.set_audio_engine("buffer")
    cfg.set_transition_mode(mode)
    cfg.set_crossfade_duration(fade_s)

    track_a, track_b = make_track(path_a), make_track(path_b)
    player = PlayerService()
    sink = CaptureSink()
    player._engine._sink = sink
    gaps: list[float] = []
    _install_pump_probe(player, gaps)
    changes: list[tuple[int, float]] = []
    player.track_changed.connect(lambda _t: changes.append((player.current_index, sink.output_ms)))

    start_ms = max(0, int((track_a.duration_seconds or 0) * 1000 - lead_s * 1000))
    player._playlist = [track_a, track_b]
    player._shuffle_order = [0, 1]
    player._pending_seek_ms = start_ms
    t0 = time.monotonic()
    player.play_index(0, resume_pending=True)

    goal_ms = lead_s * 1000 + post_s * 1000
    deadline = t0 + lead_s + post_s + 40.0
    while time.monotonic() < deadline and sink.output_ms < goal_ms:
        app.processEvents()
        time.sleep(0.001)
    reached = player.current_index == 1
    stops_during_playback = sink.stop_count
    player.reset_playback()
    player.deleteLater()
    app.processEvents()

    frames = np.frombuffer(bytes(sink.output), dtype="<i2").reshape(-1, 2).copy()
    return ScenarioResult(
        mode=mode,
        fade_s=fade_s,
        start_ms=start_ms,
        output=frames,
        underruns=[u for u in sink.underruns if u.duration_ms >= 5.0],
        sink_starts=sink.start_count,
        sink_stops=stops_during_playback,
        max_pump_gap_ms=max(gaps, default=0.0),
        reached_second_track=reached,
        wall_seconds=time.monotonic() - t0,
        track_changes=changes,
    )


def start_frame(result: ScenarioResult) -> int:
    return result.start_ms * SAMPLE_RATE // 1000
