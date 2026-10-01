"""Independent boundary-port checks for the existing impact article (#4720)."""

from pathlib import Path

import numpy as np
import pytest

ARTICLE = Path(__file__).resolve().parents[1] / "articles/technology-heavy-hit-impact-coupling.qmd"


@pytest.mark.parametrize("omega", [7.0, 17.0, 61.0])
def test_condensed_hand_boundary_matches_full_two_mass_system(omega: float) -> None:
    """Compare the eliminated boundary with the original coupled balance."""
    club_mass, hand_mass = 0.2, 0.3
    grip = 800.0 + 3.0j * omega
    support = 1200.0 + 4.0j * omega
    hand_dynamic = grip + support - hand_mass * omega**2
    load, base = 2.0 - 0.3j, 0.001 + 0.0004j
    matrix = np.array([[grip - club_mass * omega**2, -grip], [-grip, hand_dynamic]])
    full = np.linalg.solve(matrix, [load, support * base])
    driving = grip * (1 - grip / hand_dynamic)
    base_transfer = -grip * support / hand_dynamic
    reduced = (load - base_transfer * base) / (driving - club_mass * omega**2)
    assert reduced == pytest.approx(full[0])
    boundary_force = grip * (full[0] - full[1])
    assert boundary_force == pytest.approx(driving * full[0] + base_transfer * base)
    assert (driving / (1j * omega)).real >= 0
    # Accelerating both ends is not a rigid translation with zero inertial force.
    assert abs(driving + base_transfer) > 1e-3


def test_moving_boundary_power_includes_both_driven_ports() -> None:
    mass, grip_stiffness, base_stiffness = 0.3, 800.0, 1200.0
    grip_damping, base_damping = 3.0, 4.0
    club, hand, base = 0.003, -0.001, 0.002
    club_rate, hand_rate, base_rate = 0.2, -0.1, 0.3
    grip_force = grip_stiffness * (club - hand) + grip_damping * (club_rate - hand_rate)
    base_force = base_stiffness * (base - hand) + base_damping * (base_rate - hand_rate)
    acceleration = (grip_force + base_force) / mass
    energy_rate = (
        mass * hand_rate * acceleration
        + grip_stiffness * (club - hand) * (club_rate - hand_rate)
        + base_stiffness * (hand - base) * (hand_rate - base_rate)
    )
    dissipation = (
        grip_damping * (club_rate - hand_rate) ** 2 + base_damping * (hand_rate - base_rate) ** 2
    )
    input_power = grip_force * club_rate + base_force * base_rate
    assert energy_rate + dissipation == pytest.approx(input_power)
    assert energy_rate + dissipation != pytest.approx(grip_force * club_rate)


@pytest.mark.parametrize(
    "unsupported",
    [
        "the two-stage decoupled architecture implements",
        "the decoupling law connects",
        "can act only before the collision window opens",
        "this decoupling law justifies fitting against",
    ],
)
def test_related_concepts_do_not_reintroduce_retracted_isolation(unsupported: str) -> None:
    assert unsupported not in ARTICLE.read_text(encoding="utf-8")
