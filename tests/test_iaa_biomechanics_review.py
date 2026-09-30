"""Independent counterexamples for the paired biomechanics literature chapter."""

from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "articles/The_Geometry_of_Motion"
SOURCES = (
    BOOK / "quarto/ch03b_induced_acceleration_biomechanics.qmd",
    BOOK / "Volume_I/chapters/ch03b_induced_acceleration_biomechanics.tex",
)


def test_coupling_ratio_is_not_equal_torque_mobility_or_muscle_action() -> None:
    mass = np.array([[4.0, 1.0], [1.0, 1.0]])
    first, second = np.linalg.solve(mass, 3 * np.eye(2)).T
    assert first == pytest.approx([1, -1])
    assert second == pytest.approx([-1, 4])
    assert first[1] == pytest.approx(second[0])
    assert abs(first[1] / first[0]) == pytest.approx(1)
    assert abs(second[0] / second[1]) == pytest.approx(0.25)
    routed = np.linalg.solve(mass, [1, 2])
    assert routed == pytest.approx([-1 / 3, 7 / 3])


def test_constrained_ledger_counts_baseline_once_against_kkt_solve() -> None:
    mass = np.array([[4.0, 1.0], [1.0, 1.0]])
    constraint = np.array([[1.0, 1.0]])
    kkt = np.block([[mass, -constraint.T], [constraint, np.zeros((1, 1))]])
    total = np.linalg.solve(kkt, [3, 3, 2])
    first = np.linalg.solve(kkt, [3, 0, 0])
    second = np.linalg.solve(kkt, [0, 3, 0])
    baseline = np.linalg.solve(kkt, [0, 0, 2])
    assert total[:2] == pytest.approx([0, 2])
    assert first + second + baseline == pytest.approx(total)
    assert first[:2] == pytest.approx([1, -1])
    assert second[:2] == pytest.approx([-1, 1])
    assert baseline[:2] == pytest.approx([0, 2])
    assert first + second + 2 * baseline != pytest.approx(total)


def test_excitation_change_has_no_instantaneous_force_jump_with_activation_state() -> None:
    # Unit-mass actuator model: q''=a; a'=(u-a)/T, with a(0)=0.
    duration, time_constant = 0.1, 0.05
    response = solve_ivp(
        lambda _time, state: [state[1], state[2], (1 - state[2]) / time_constant],
        (0, duration),
        [0, 0, 0],
        rtol=1e-10,
        atol=1e-12,
    )
    assert response.y[2, 0] == 0
    assert response.y[2, -1] == pytest.approx(1 - np.exp(-duration / time_constant))
    assert response.y[1, -1] == pytest.approx(
        duration - time_constant * (1 - np.exp(-duration / time_constant))
    )


def test_small_force_error_can_survive_perfect_closure_and_amplify() -> None:
    mass = np.diag([1.0, 0.001])
    nominal_force, force_error = np.array([1.0, 0.0]), np.array([0.0, 0.001])
    fitted = np.linalg.solve(mass, nominal_force + force_error)
    assert mass @ fitted == pytest.approx(nominal_force + force_error)
    assert fitted - np.linalg.solve(mass, nominal_force) == pytest.approx([0, 1])


def test_fixed_mode_increment_can_require_unilateral_contact_release() -> None:
    # Upward-positive unit mass at a stationary horizontal floor: a=F-g+lambda.
    gravity = 9.81
    for upward_force in (0.0, 12.0):
        reaction = gravity - upward_force
        assert upward_force - gravity + reaction == pytest.approx(0)
    assert gravity - 12.0 < 0  # Algebraic sticking solution would require adhesion.
    free_acceleration = 12.0 - gravity
    assert free_acceleration > 0


@pytest.mark.parametrize("path", SOURCES, ids=lambda path: path.suffix)
@pytest.mark.parametrize(
    "required, forbidden",
    [
        ("Q_g=-g", "now represents the gravitational contribution"),
        ("kinematic block", "The correspondence is exact"),
        ("baseline once", "ground reaction force is itself a constraint force"),
        ("equal-torque", "IAI}_{j \\to k} ="),
        ("nominal trajectory", "The cumulative effect is the drift field"),
        ("nonorthogonal torque decomposition", "extended induced acceleration analysis to"),
        ("ten stroke participants", "informed individualized rehabilitation protocols"),
    ],
)
def test_both_editions_state_the_essential_interpretation_boundaries(
    path: Path, required: str, forbidden: str
) -> None:
    source = " ".join(path.read_text(encoding="utf-8").split())
    assert required in source
    assert forbidden not in source
