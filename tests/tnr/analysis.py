"""Contrôles objectifs d'une transition enregistrée, comparée à la construction idéale issue de PCM de référence.

Pour deux pistes A (fin jouée depuis `start`) et B, la sortie attendue est :
- gapless : fin de A suivie de B, identiques à l'échantillon près ;
- standard : fin de A, un silence court, puis B intégral ;
- crossfade : A jusqu'à `durée - fondu`, mixage à puissance égale de la fin de A et du début de B, puis B.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from amso.core.pcm_mixer import SAMPLE_RATE, equal_power_mix
from tests.tnr.scenario import ScenarioResult

NEEDLE_FRAMES = 2048
EXACT_TOLERANCE = 2  # LSB : écart toléré entre deux décodages du même fichier
WINDOW_FRAMES = SAMPLE_RATE // 50  # 20 ms
MAX_STANDARD_GAP_MS = 400.0  # le décodeur doit livrer 200 ms d'audio en temps réel avant de démarrer
MAX_SEEK_ERROR_MS = 300.0
MAX_CROSSFADE_ONSET_ERROR_MS = 150.0
MAX_PLACEMENT_ERROR_MS = 20.0
MAX_ENVELOPE_DEVIATION_DB = 2.0


@dataclass(slots=True)
class Check:
    name: str
    ok: bool
    detail: str


def _ms(frames: float) -> float:
    return frames * 1000.0 / SAMPLE_RATE


def _frames(ms: float) -> int:
    return int(ms * SAMPLE_RATE / 1000.0)


def locate(haystack: np.ndarray, needle: np.ndarray, start: int = 0) -> int | None:
    """Position (en frames) de `needle` dans `haystack` à partir de `start`, ou None. Recherche exacte."""
    raw = np.ascontiguousarray(haystack).tobytes()
    target = np.ascontiguousarray(needle).tobytes()
    index = raw.find(target, start * 4)
    while index != -1 and index % 4:
        index = raw.find(target, index + 1)
    return None if index == -1 else index // 4


def pick_needle(frames: np.ndarray, start: int) -> tuple[int, np.ndarray] | None:
    """Premier bloc non silencieux de `frames` à partir de `start`, utilisable comme repère de recherche."""
    for pos in range(start, max(start, len(frames) - NEEDLE_FRAMES), NEEDLE_FRAMES // 2):
        block = frames[pos : pos + NEEDLE_FRAMES]
        if len(block) == NEEDLE_FRAMES and int(np.abs(block).max()) > 500:
            return pos, block
    return None


def window_deviation(actual: np.ndarray, ideal: np.ndarray) -> tuple[float, int | None]:
    """Part des fenêtres de 20 ms dont l'écart maximal dépasse la tolérance, et position (ms) de la première."""
    count = min(len(actual), len(ideal)) // WINDOW_FRAMES * WINDOW_FRAMES
    if count == 0:
        return 1.0, 0
    diff = np.abs(actual[:count].astype(np.int32) - ideal[:count].astype(np.int32)).max(axis=1)
    bad = diff.reshape(-1, WINDOW_FRAMES).max(axis=1) > EXACT_TOLERANCE
    first = int(np.argmax(bad)) * WINDOW_FRAMES if bad.any() else None
    return float(bad.mean()), None if first is None else round(_ms(first))


def rms_db(frames: np.ndarray, window: int = SAMPLE_RATE // 10) -> np.ndarray:
    count = len(frames) // window * window
    blocks = frames[:count].astype(np.float64).reshape(-1, window, 2)
    return 10.0 * np.log10(np.maximum((blocks**2).mean(axis=(1, 2)), 1e-3))


def _common_checks(result: ScenarioResult) -> list[Check]:
    underruns = result.underruns if result.mode != "standard" else []  # le silence de « pas de fondu » est borné à part
    longest = max((u.duration_ms for u in underruns), default=0.0)
    first = f", premier à {underruns[0].output_ms:.0f} ms" if underruns else ""
    return [
        Check(
            "transition atteinte", result.reached_second_track, f"piste suivante lue : {result.reached_second_track}"
        ),
        Check(
            "aucune coupure de sortie",
            not underruns,
            f"{len(underruns)} trou(s), plus long {longest:.0f} ms{first}",
        ),
        Check(
            "session matérielle unique",
            result.sink_starts == 1 and result.sink_stops == 0,
            f"{result.sink_starts} ouverture(s), {result.sink_stops} fermeture(s)",
        ),
    ]


def evaluate(result: ScenarioResult, ref_a: np.ndarray, ref_b: np.ndarray) -> list[Check]:
    checks = _common_checks(result)
    out = result.output
    needle = pick_needle(out, 0)
    a0 = locate(ref_a, needle[1]) if needle else None
    if needle is None or a0 is None:
        checks.append(Check("alignement sur A", False, "début de sortie introuvable dans la référence de A"))
        return checks
    a_start = a0 - needle[0]
    # LibVLC se place sur un bloc FLAC, pas à la milliseconde demandée : le moteur croit lire à `start_ms`
    seek_error = a_start - _frames(result.start_ms)
    checks.append(
        Check(
            "précision du positionnement après seek",
            abs(_ms(seek_error)) <= MAX_SEEK_ERROR_MS,
            f"démarrage à {_ms(a_start) / 1000:.2f} s au lieu de {result.start_ms / 1000:.2f} s ({_ms(seek_error):+.0f} ms)",
        )
    )
    tail_a = ref_a[a_start:]
    if result.mode == "crossfade":
        checks += _crossfade_checks(result, out, tail_a, ref_b, seek_error)
    elif result.mode == "gapless":
        checks += _gapless_checks(out, tail_a, ref_b)
    else:
        checks += _standard_checks(out, tail_a, ref_b)
    return checks


def _verdict(ratio: float, first: int | None) -> str:
    return "conforme" if ratio == 0.0 else f"{ratio:.1%} des fenêtres de 20 ms diffèrent, première à {first} ms"


def describe_shift(out: np.ndarray, ideal: np.ndarray, first_ms: int | None) -> str:
    """Après une divergence, cherche où la sortie reprend dans la référence : un décalage = audio perdu ou répété."""
    if first_ms is None:
        return ""
    probe = pick_needle(out, _frames(first_ms) + SAMPLE_RATE // 2)
    if probe is None:
        return ""
    found = locate(ideal, probe[1], max(0, probe[0] - 10 * SAMPLE_RATE))
    if found is None:
        return " ; contenu altéré (aucune reprise retrouvée)"
    shift = _ms(found - probe[0])
    return (
        f" ; la sortie reprend avec un décalage de {shift:+.1f} ms ({'audio perdu' if shift > 0 else 'audio répété'})"
    )


def _gapless_checks(out: np.ndarray, tail_a: np.ndarray, ref_b: np.ndarray) -> list[Check]:
    ideal = np.concatenate([tail_a, ref_b])
    ratio, first = window_deviation(out, ideal)
    detail = _verdict(ratio, first) + describe_shift(out, ideal, first)
    return [Check("enchaînement identique à l'échantillon près", ratio == 0.0, detail)]


def _standard_checks(out: np.ndarray, tail_a: np.ndarray, ref_b: np.ndarray) -> list[Check]:
    ratio_a, first_a = window_deviation(out[: len(tail_a)], tail_a)
    checks = [Check("fin de A intacte", ratio_a == 0.0, _verdict(ratio_a, first_a))]
    needle = pick_needle(ref_b, 0)
    b0 = locate(out, needle[1], max(0, len(tail_a) - SAMPLE_RATE)) if needle else None
    if needle is None or b0 is None:
        return [*checks, Check("début de B retrouvé", False, "début de B introuvable dans la sortie")]
    b_start = b0 - needle[0]
    gap = _ms(b_start - len(tail_a))
    checks.append(Check("silence entre pistes borné", 0 <= gap <= MAX_STANDARD_GAP_MS, f"{gap:.0f} ms"))
    ratio_b, first_b = window_deviation(out[b_start:], ref_b)
    checks.append(
        Check("B intact", ratio_b == 0.0, _verdict(ratio_b, first_b) + describe_shift(out[b_start:], ref_b, first_b))
    )
    return checks


def _fade_onset_check(out: np.ndarray, tail_a: np.ndarray, zone: int) -> Check:
    """Le fondu ne doit altérer A qu'à partir de `zone` (début de la dernière `fade` secondes de A)."""
    head = min(len(out), zone)
    diff = np.abs(out[:head].astype(np.int32) - tail_a[:head].astype(np.int32)).max(axis=1)
    bad = np.nonzero(diff > EXACT_TOLERANCE)[0]
    early_ms = _ms(head - int(bad[0])) if bad.size else 0.0
    detail = (
        "conforme" if not early_ms else f"A altéré {early_ms:.0f} ms avant l'instant prévu ({_ms(zone) / 1000:.2f} s)"
    )
    return Check("début du fondu à l'instant prévu", early_ms <= MAX_CROSSFADE_ONSET_ERROR_MS, detail)


def _ideal_crossfade(tail_a: np.ndarray, ref_b: np.ndarray, fade: int, zone: int) -> np.ndarray:
    """Sortie attendue : A jusqu'à `zone`, fondu sur la fin de A (au plus `fade` frames), puis B."""
    mixed_frames = min(fade, len(tail_a) - zone)
    mixed = equal_power_mix(tail_a[zone:].tobytes(), ref_b[:mixed_frames].tobytes(), 0, fade)
    return np.concatenate([tail_a[:zone], np.frombuffer(mixed, "<i2").reshape(-1, 2), ref_b[mixed_frames:]])


def _crossfade_checks(
    result: ScenarioResult, out: np.ndarray, tail_a: np.ndarray, ref_b: np.ndarray, seek_error: int
) -> list[Check]:
    fade = _frames(result.fade_s * 1000)
    # Le moteur place la zone d'après la position qu'il croit lire ; elle se termine avec A, donc raccourcie de l'erreur
    zone = len(tail_a) - fade + seek_error
    ideal = _ideal_crossfade(tail_a, ref_b, fade, zone)
    checks = [_fade_onset_check(out, tail_a, zone)]
    needle = pick_needle(ref_b, fade + SAMPLE_RATE)
    b0 = locate(out, needle[1], max(0, zone)) if needle else None
    if needle is None or b0 is None:
        checks.append(Check("placement de B", False, "B introuvable dans la sortie"))
    else:
        placement = _ms(b0 - (zone + needle[0]))
        checks.append(
            Check("placement de B", abs(placement) <= MAX_PLACEMENT_ERROR_MS, f"écart de {placement:+.1f} ms")
        )
    mixed_frames = min(fade, len(tail_a) - zone)
    ratio, first = window_deviation(out[zone + mixed_frames :], ref_b[mixed_frames:])
    after_fade, expected = out[zone + mixed_frames :], ref_b[mixed_frames:]
    checks.append(
        Check(
            "B intact après le fondu",
            ratio == 0.0,
            _verdict(ratio, first) + describe_shift(after_fade, expected, first),
        )
    )
    count = min(len(out), len(ideal))
    deviation = np.abs(rms_db(out[:count]) - rms_db(ideal[:count]))
    worst = float(deviation.max()) if deviation.size else 0.0
    at = int(deviation.argmax()) * 100 if deviation.size else 0
    checks.append(
        Check(
            "niveau conforme au fondu idéal",
            worst <= MAX_ENVELOPE_DEVIATION_DB,
            f"écart maximal {worst:.1f} dB à {at} ms de la sortie",
        )
    )
    return checks
