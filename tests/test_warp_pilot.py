from __future__ import annotations

import math

import pytest

from amso.ui.views.effects.warp_pilot import Maneuver, WarpPilot


def _run(pilot: WarpPilot, seconds: float, dt: float = 0.033):
    steps = []
    for _ in range(int(seconds / dt) + 2):
        steps.append(pilot.advance(dt))
    return steps


def test_pilot_cruise_at_start_goes_straight() -> None:
    pilot = WarpPilot()
    step = pilot.advance(0.033)
    assert (step.yaw, step.pitch, step.roll) == (0.0, 0.0, 0.0)
    assert pilot.maneuver is None


@pytest.mark.parametrize("maneuver", list(Maneuver))
def test_pilot_maneuver_ends_and_returns_to_cruise(maneuver: Maneuver) -> None:
    pilot = WarpPilot()
    pilot.start(maneuver)
    _run(pilot, 5.0)
    assert pilot.maneuver is None


def test_pilot_turn_reaches_total_angle_without_roll_drift() -> None:
    pilot = WarpPilot()
    pilot.start(Maneuver.TURN)
    total_yaw = pilot._yaw_total
    steps = []
    while pilot.maneuver is not None:
        steps.append(pilot.advance(0.033))
    assert sum(s.yaw for s in steps) == pytest.approx(total_yaw, abs=1e-9)
    # Après la manœuvre la caméra est redressée.
    assert pilot.advance(0.033).roll == pytest.approx(0.0, abs=1e-9)


def test_pilot_barrel_roll_makes_full_revolution() -> None:
    pilot = WarpPilot()
    pilot.start(Maneuver.BARREL_ROLL)
    steps = []
    while pilot.maneuver is not None:
        steps.append(pilot.advance(0.033))
    assert all(s.yaw == 0.0 and s.pitch == 0.0 for s in steps)
    assert abs(pilot._roll_base) < 1e-9 or abs(pilot._roll_base - 2 * math.pi) < 1e-9
