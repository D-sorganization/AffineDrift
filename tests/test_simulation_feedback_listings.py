"""Verify the published simulation and regulation examples against mechanics."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest

CHAPTERS = Path(__file__).resolve().parents[1] / "articles/The_Geometry_of_Motion/Volume_V/chapters"


def _listing(name: str) -> ModuleType:
    """Execute a fixed repository-owned listing, with no external input."""
    path = CHAPTERS / name
    blocks = re.findall(
        r"\\begin\{lstlisting\}\[language=Python[^\n]*\]\n(.*?)\\end\{lstlisting\}",
        path.read_text(encoding="utf-8"),
        re.DOTALL,
    )
    assert blocks
    module = ModuleType(f"_feedback_listing_{path.stem}")
    sys.modules[module.__name__] = module
    # Repository-owned listing at a fixed path, with no external input.
    # nosemgrep: python.lang.security.audit.exec-detected.exec-detected
    exec(compile("\n".join(blocks), str(path), "exec", dont_inherit=True), module.__dict__)
    return module


@pytest.fixture(scope="module")
def simulation() -> ModuleType:
    """Load the chapter's actual forward and inverse dynamics functions."""
    return _listing("ch04_simulation.tex")


@pytest.fixture(scope="module")
def feedback() -> ModuleType:
    """Load the chapter's actual gravity-compensated regulation function."""
    return _listing("ch06_controller_design.tex")


def _zero_torque(time: float, state: np.ndarray) -> np.ndarray:
    """Torque-free input used to test the unforced initial-value problem."""
    return np.zeros(3)


def test_forward_inverse_round_trip(simulation: ModuleType) -> None:
    """Same-state algebra is consistent without claiming an independent validation."""
    state = np.array([0.4, -0.7, 0.3, 1.2, -0.8, 0.2])
    torque = np.array([2.0, -0.4, 0.6])
    acceleration = simulation.forward_dynamics(state, torque)
    np.testing.assert_allclose(simulation.inverse_dynamics(state, acceleration), torque, atol=1e-12)


def test_horizontal_gravity_matches_rod_moments(simulation: ModuleType) -> None:
    """Independent lever arms fix the sign and uniform-rod mass convention."""
    model = simulation.RIGID_MODEL
    m1, m2, m3 = model.masses
    l1, l2, l3 = model.lengths
    expected = 9.81 * np.array(
        [
            m1 * l1 / 2 + m2 * (l1 + l2 / 2) + m3 * (l1 + l2 + l3 / 2),
            m2 * l2 / 2 + m3 * (l2 + l3 / 2),
            m3 * l3 / 2,
        ]
    )
    np.testing.assert_allclose(
        simulation.inverse_dynamics(np.zeros(6), np.zeros(3)), expected, rtol=1e-8
    )


def test_downward_rest_stays_at_rest(simulation: ModuleType) -> None:
    """The downward straight chain is a gravity equilibrium, not the horizontal chain."""
    initial = np.array([-np.pi / 2, 0, 0, 0, 0, 0])
    times = np.array([0.0, 0.007, 0.023])
    result = simulation.simulate(initial, times, _zero_torque)
    np.testing.assert_array_equal(result["time"], times)
    np.testing.assert_allclose(result["state"], np.broadcast_to(initial, (3, 6)), atol=2e-8)


def test_forced_trajectory_energy_balance(simulation: ModuleType) -> None:
    """Check independent energy change against integrated torque power."""
    initial = np.array([0.2, -0.4, 0.1, 0.3, -0.2, 0.1])
    times = np.linspace(0.0, 0.04, 161)
    torque = np.array([0.4, -0.3, 0.1])

    def control(time: float, state: np.ndarray) -> np.ndarray:
        """Apply a constant generalized torque, without an actuator model."""
        return torque

    states = simulation.simulate(initial, times, control)["state"]
    model = simulation.RIGID_MODEL

    def energy(state: np.ndarray) -> float:
        """Evaluate mechanical energy separately from the integrator."""
        position, velocity = state[:3], state[3:]
        return float(
            0.5 * velocity @ model.rigid_mass_matrix(position) @ velocity
            + model.potential_energy(position)
        )

    delta = energy(states[-1]) - energy(states[0])
    work = np.trapezoid(states[:, 3:] @ torque, times)
    assert abs(delta - work) < 2e-7


@pytest.mark.parametrize("state", [np.zeros(4), np.zeros((2, 3)), np.full(6, np.nan)])
def test_state_contract(simulation: ModuleType, state: np.ndarray) -> None:
    """Unsupported state dimensions cannot silently return zero accelerations."""
    with pytest.raises(ValueError):
        simulation.forward_dynamics(state, np.zeros(3))


@pytest.mark.parametrize("vector", [np.zeros(2), np.full(3, np.inf), np.zeros((3, 1))])
def test_torque_and_acceleration_contract(simulation: ModuleType, vector: np.ndarray) -> None:
    """Both directions require finite three-component generalized quantities."""
    with pytest.raises(ValueError):
        simulation.forward_dynamics(np.zeros(6), vector)
    with pytest.raises(ValueError):
        simulation.inverse_dynamics(np.zeros(6), vector)


@pytest.mark.parametrize("times", [[0], [1, 2], [0, 0], [0, -1], [0, np.nan], [[0, 1]]])
def test_time_contract(simulation: ModuleType, times: list) -> None:
    """Output grid is finite, increasing, one-dimensional and includes initial time zero."""
    with pytest.raises(ValueError):
        simulation.simulate(np.zeros(6), np.asarray(times), _zero_torque)


def test_solver_failure_is_not_a_trajectory(
    simulation: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failed numerical solver raises rather than publishing incomplete output."""
    monkeypatch.setattr(simulation, "solve_ivp", lambda *a, **kw: SimpleNamespace(success=False))
    with pytest.raises(RuntimeError):
        simulation.simulate(np.zeros(6), np.array([0.0, 0.1]), _zero_torque)


def test_regulation_torque_and_equilibrium(feedback: ModuleType) -> None:
    """At a constant target only the supplied gravity torque remains."""
    gains = feedback.PDGains(np.diag([4.0, 9.0]), np.diag([2.0, 3.0]))
    state = np.array([[0.4, -0.2], [0.1, -0.3]])
    target = np.array([0.2, 0.1])
    gravity = np.array([1.2, 0.4])
    np.testing.assert_allclose(
        feedback.regulation_torque(gains, state, target, gravity), [0.2, 4.0], atol=1e-12
    )
    np.testing.assert_allclose(
        feedback.regulation_torque(gains, np.stack([target, np.zeros(2)]), target, gravity),
        gravity,
    )


def test_moving_target_counterexample(feedback: ModuleType) -> None:
    """At perfect sinusoidal tracking, static PD lacks the required acceleration."""
    gains = feedback.PDGains(np.array([[4.0]]), np.array([[2.0]]))
    torque = feedback.regulation_torque(gains, np.array([[1.0], [0.0]]), np.ones(1), np.zeros(1))
    assert torque[0] == 0
    required_acceleration = -1.0  # Unit mass, r=sin(t) at t=pi/2.
    assert torque[0] - required_acceleration == 1.0


@pytest.mark.parametrize(
    "gain",
    [
        np.array([1.0]),
        np.zeros((0, 0)),
        np.zeros((2, 2)),
        np.diag([1.0, -1.0]),
        np.full((2, 2), np.nan),
        np.array([[2.0, 1.0], [0.0, 2.0]]),
    ],
)
def test_gain_contract(feedback: ModuleType, gain: np.ndarray) -> None:
    """The theorem requires nonempty finite symmetric positive-definite gains."""
    with pytest.raises(ValueError):
        feedback.PDGains(gain, np.eye(2))
    with pytest.raises(ValueError):
        feedback.PDGains(np.eye(2), gain)


def test_gain_dimensions_and_defensive_copy(feedback: ModuleType) -> None:
    """A valid gain pair has equal dimensions and cannot be changed through the input."""
    with pytest.raises(ValueError):
        feedback.PDGains(np.eye(2), np.eye(3))
    original = np.eye(2)
    gains = feedback.PDGains(original, original)
    original[0, 0] = -1
    np.testing.assert_array_equal(gains.proportional, np.eye(2))
    assert not gains.proportional.flags.writeable


@pytest.mark.parametrize(
    "state,target,gravity",
    [
        (np.zeros(4), np.zeros(2), np.zeros(2)),
        (np.zeros((2, 2)), np.zeros(3), np.zeros(2)),
        (np.zeros((2, 2)), np.zeros(2), np.zeros(3)),
        (np.full((2, 2), np.nan), np.zeros(2), np.zeros(2)),
        (np.zeros((2, 2)), np.full(2, np.inf), np.zeros(2)),
        (np.zeros((2, 2)), np.zeros(2), np.full(2, np.nan)),
    ],
)
def test_regulation_boundary(
    feedback: ModuleType, state: np.ndarray, target: np.ndarray, gravity: np.ndarray
) -> None:
    """Malformed or nonfinite controller data cannot broadcast silently."""
    gains = feedback.PDGains(np.eye(2), np.eye(2))
    with pytest.raises(ValueError):
        feedback.regulation_torque(gains, state, target, gravity)
