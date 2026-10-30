"""Non-régression des transitions sur deux pistes réelles (Sirius -> Eye in the Sky), moteur `buffer`.

Lent (~40 s par mode) et dépendant de VLC et des fichiers : ignoré s'ils sont absents. Lancer à la demande avec
`pytest -m tnr` ou, plus simplement, `scripts/tnr_transitions.bat`.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from amso.services.player_service import vlc

LOCAL_DIR = Path(__file__).resolve().parents[1] / "_work" / "tnr"
NAS_DIR = Path("//NASLEF97/Audio/Par artiste/Alan Parsons Project/1982 - Eye In The Sky")
DEFAULT_DIR = LOCAL_DIR if (LOCAL_DIR / "01 - Sirius.flac").is_file() else NAS_DIR
TRACK_A = Path(os.environ.get("AMSO_TNR_TRACK_A", DEFAULT_DIR / "01 - Sirius.flac"))
TRACK_B = Path(os.environ.get("AMSO_TNR_TRACK_B", DEFAULT_DIR / "02 - Eye In The Sky.flac"))

pytestmark = [
    pytest.mark.tnr,
    pytest.mark.skipif(not vlc.available, reason="VLC indisponible"),
    pytest.mark.skipif(not (TRACK_A.is_file() and TRACK_B.is_file()), reason="pistes de référence absentes"),
]


@pytest.mark.parametrize("mode", ["gapless", "crossfade"])
def test_tnr_real_tracks_transition_matches_ideal(mode: str) -> None:
    from tests.tnr.analysis import evaluate
    from tests.tnr.reference import load_reference
    from tests.tnr.scenario import run_transition

    result = run_transition(TRACK_A, TRACK_B, mode, fade_s=10)
    failed = [
        f"{c.name} : {c.detail}" for c in evaluate(result, load_reference(TRACK_A), load_reference(TRACK_B)) if not c.ok
    ]
    assert not failed, "\n".join(failed)
