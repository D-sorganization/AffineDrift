"""Independent counterexamples and executable evidence for the lay contraction article."""

import re
from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import expm

from src.tools.contraction_examples import local_contraction_rate

SOURCE = (
    Path(__file__).resolve().parents[1]
    / "articles/tangent-hyperplane-articles/Advanced/Contraction_Tangent_LAYMAN.qmd"
)


@pytest.mark.parametrize(
    "unsupported",
    [
        "The friction makes the system contracting",
        "contraction and optimality coincide",
        "It **bends spacetime**",
        "28.7 units³",
        "1.94 Hz (target: 2.0 Hz)",
        "https://github.com/AffineDrift/contraction-tangent-unification",
        "Preserved optimality (can still reach targets)",
        "λ = (1/2) λ_min(S B R^(-1) B^T S)",
    ],
)
def test_lay_article_does_not_republish_rejected_claims(unsupported: str) -> None:
    """Guard specific false claims, not a vocabulary proxy for full scientific review."""
    assert unsupported not in SOURCE.read_text(encoding="utf-8")


def test_published_scalar_certificate_matches_closed_loop_solution() -> None:
    """Execute the actual article example and compare with the analytic trajectory."""
    examples = re.findall(r"```python\n(.*?)\n```", SOURCE.read_text(encoding="utf-8"), re.S)
    assert len(examples) == 1
    namespace: dict[str, object] = {}
    exec(compile(examples[0], str(SOURCE), "exec"), namespace)
    assert namespace["gain"] == pytest.approx(3.0)
    assert namespace["rate"] == pytest.approx(2.0)
    assert np.exp(-2 * 0.5) == pytest.approx(0.36787944117)


@pytest.mark.parametrize("scale", [0.1, 1.0, 7.0])
def test_cost_rescaling_preserves_controller_and_normalized_rate(scale: float) -> None:
    """Rescaling the declared objective cannot change the same physical closed loop."""
    state_cost, effort_cost, value = 3 * scale, scale, 3 * scale
    gain = value / effort_cost
    closed = np.array([[1 - gain]])
    metric = np.array([[value]])
    assert gain == pytest.approx(3)
    assert state_cost + gain**2 * effort_cost == pytest.approx(4 * value)
    assert local_contraction_rate(closed, metric, np.zeros((1, 1))) == pytest.approx(2)
    # The retired unnormalized formula wrongly changes with the cost units.
    assert value**2 / (2 * effort_cost) == pytest.approx(4.5 * scale)


def test_damped_pendulum_keeps_an_unstable_upright_equilibrium() -> None:
    """Dissipated energy does not imply a global incremental certificate."""
    upright_jacobian = np.array([[0.0, 1.0], [1.0, -0.2]])
    assert np.linalg.eigvals(upright_jacobian).max() > 0.9
    # Both resting configurations remain stationary, so their separation persists.
    assert np.sin(0.0) == 0
    assert np.sin(np.pi) == pytest.approx(0, abs=1e-15)


def test_spring_without_damping_preserves_error_energy() -> None:
    dynamics = np.array([[0.0, 1.0], [-4.0, 0.0]])
    energy_metric = np.diag([4.0, 1.0])
    transition = expm(dynamics * 0.7)
    assert transition.T @ energy_metric @ transition == pytest.approx(energy_metric)
    assert local_contraction_rate(dynamics, energy_metric, np.zeros((2, 2))) == 0


def test_more_stiffness_does_not_raise_underdamped_spectral_decay() -> None:
    """With fixed inertia/damping, stiffness can alter frequency without the envelope."""
    for stiffness in (1.0, 4.0):
        dynamics = np.array([[0.0, 1.0], [-stiffness, -0.2]])
        assert np.linalg.eigvals(dynamics).real == pytest.approx([-0.1, -0.1])


def test_closed_loop_eigenvalues_miss_transient_error_growth() -> None:
    dynamics = np.array([[-1.0, 4.0], [0.0, -1.0]])
    assert np.linalg.eigvals(dynamics) == pytest.approx([-1.0, -1.0])
    assert local_contraction_rate(dynamics, np.eye(2), np.zeros((2, 2))) == -1
    assert np.linalg.norm(expm(dynamics * 0.25) @ [0.0, 1.0]) > 1


def test_persistent_disturbance_prevents_exact_recovery() -> None:
    # de/dt = -2e + 0.2, e(0)=0, has the exact comparison-bound solution.
    time = 5.0
    error = 0.1 * (1 - np.exp(-2 * time))
    assert error == pytest.approx(0.1, rel=1e-4)
    assert error > 0.09


def test_sampled_feedback_uses_the_implemented_update() -> None:
    # de/dt=u, u_k=-2e_k held over a sampling interval h.
    continuous = np.array([[-2.0]])
    assert local_contraction_rate(continuous, np.eye(1), np.zeros((1, 1))) == 2
    assert abs(1 - 2 * 0.25) < 1
    assert abs(1 - 2 * 1.25) > 1


def test_phase_shift_can_preserve_event_output_despite_clock_time_error() -> None:
    """Same path and speed, different arrival time: equality at impact is a new map."""
    speed, phase_shift = 2.0, 0.1
    nominal_event = 1 / speed
    perturbed_event = (1 - phase_shift) / speed
    assert speed * nominal_event + phase_shift != 1
    assert speed * perturbed_event + phase_shift == pytest.approx(1)
    assert perturbed_event != nominal_event


def test_fast_contraction_does_not_guarantee_smaller_task_error() -> None:
    # The same final norm can hide very different errors in an observed component.
    task_map = np.array([[1.0, 0.0]])
    harmless = np.array([0.0, 1.0])
    damaging = np.array([0.1, 0.0])
    assert np.linalg.norm(damaging) < np.linalg.norm(harmless)
    assert np.linalg.norm(task_map @ damaging) > np.linalg.norm(task_map @ harmless)
