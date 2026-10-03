"""Distal power identities and regression contracts for article review #4855."""

from importlib import import_module
from pathlib import Path

import numpy as np
import pytest

MODEL = import_module("docs.development.technical-review.build_affine_structure_figures")
SOURCE = (
    Path(__file__).resolve().parents[1] / "articles/drift-components-wrench-double-pendulum.qmd"
)
GRAVITY = np.array([0.0, -MODEL.GRAVITY_M_S2])


def radial(angle: float) -> np.ndarray:
    """Unit direction counterclockwise from the downward vertical."""
    return np.array([np.sin(angle), -np.cos(angle)])


def tangent(angle: float) -> np.ndarray:
    """Derivative of the radial direction with respect to angle."""
    return np.array([np.cos(angle), np.sin(angle)])


def kinematics(q: np.ndarray, rates: np.ndarray, acceleration: np.ndarray) -> tuple:
    """Differentiate COM geometry in the upward-positive inertial frame."""
    joint_velocity = MODEL.LENGTH_FIRST * rates[0] * tangent(q[0])
    com_velocity = joint_velocity + MODEL.COM_SECOND * rates.sum() * tangent(q.sum())
    joint_acceleration = MODEL.LENGTH_FIRST * (
        acceleration[0] * tangent(q[0]) - rates[0] ** 2 * radial(q[0])
    )
    com_acceleration = joint_acceleration + MODEL.COM_SECOND * (
        acceleration.sum() * tangent(q.sum()) - rates.sum() ** 2 * radial(q.sum())
    )
    return joint_velocity, com_velocity, com_acceleration


def distal_energy(q: np.ndarray, rates: np.ndarray) -> float:
    """Compute energy directly from COM motion, not the joint-force power formula."""
    speed = kinematics(q, rates, np.zeros(2))[1]
    height = -MODEL.LENGTH_FIRST * np.cos(q[0]) - MODEL.COM_SECOND * np.cos(q.sum())
    return float(
        0.5 * MODEL.MASS_SECOND * speed @ speed
        + 0.5 * MODEL.INERTIA_SECOND * rates.sum() ** 2
        + MODEL.MASS_SECOND * MODEL.GRAVITY_M_S2 * height
    )


def response(q: np.ndarray, rates: np.ndarray, torque: np.ndarray) -> tuple:
    """Recover acceleration and actual link-1-on-link-2 force from Newton's law."""
    mass, bias, gravity = MODEL.operators(q, rates)
    acceleration = np.linalg.solve(mass, torque - bias - gravity)
    joint_velocity, _, com_acceleration = kinematics(q, rates, acceleration)
    force = MODEL.MASS_SECOND * (com_acceleration - GRAVITY)
    return acceleration, force, joint_velocity


@pytest.mark.parametrize("torque", [[0.0, 0.0], [2.0, 0.0], [0.0, 2.0]])
@pytest.mark.parametrize(
    "state", [([0.6, -0.8], [1.7, -2.3]), ([0.2, 0.4], [0.8, -0.5]), ([0.5, -0.3], [1.2, 0.0])]
)
def test_distal_energy_and_com_moment_balances(state: tuple, torque: list) -> None:
    """Check the same article balance by energy differentiation and COM moments."""
    q, rates = np.asarray(state[0]), np.asarray(state[1])
    applied = np.asarray(torque)
    acceleration, force, joint_velocity = response(q, rates, applied)
    step = 1e-6  # Directional energy derivative; truncation and roundoff allowance below.
    derivative = (
        distal_energy(q + step * rates, rates + step * acceleration)
        - distal_energy(q - step * rates, rates - step * acceleration)
    ) / (2 * step)
    power = force @ joint_velocity + applied[1] * rates.sum()
    assert derivative == pytest.approx(power, abs=2e-8, rel=0)
    lever = -MODEL.COM_SECOND * radial(q.sum())  # COM to force-application point.
    moment = lever[0] * force[1] - lever[1] * force[0] + applied[1]
    assert moment == pytest.approx(MODEL.INERTIA_SECOND * acceleration.sum(), abs=1e-12, rel=0)


def test_proximal_input_changes_distal_force_power_with_zero_distal_torque() -> None:
    """The manufactured example disproves identification of pulling with drift."""
    q, rates = np.array([0.6, -0.8]), np.array([1.7, -2.3])
    _, drift_force, joint_velocity = response(q, rates, np.zeros(2))
    _, driven_force, _ = response(q, rates, np.array([2.0, 0.0]))
    assert drift_force @ joint_velocity == pytest.approx(0.34148300592885, abs=1e-12, rel=0)
    assert driven_force @ joint_velocity == pytest.approx(1.13075298847874, abs=1e-12, rel=0)
    mass = MODEL.operators(q, rates)[0]
    input_acceleration = np.linalg.solve(mass, [2.0, 0.0])
    jacobian = np.column_stack(
        (
            MODEL.LENGTH_FIRST * tangent(q[0]) + MODEL.COM_SECOND * tangent(q.sum()),
            MODEL.COM_SECOND * tangent(q.sum()),
        )
    )
    np.testing.assert_allclose(
        driven_force - drift_force,
        MODEL.MASS_SECOND * jacobian @ input_acceleration,
        atol=1e-12,
        rtol=0,
    )


@pytest.mark.parametrize("relative_rate", [-2.3, 0.0])
def test_segment_moment_power_differs_from_motor_pair_power(relative_rate: float) -> None:
    """Equal/opposite couples use different segment rates, including at zero joint rate."""
    q, rates, torque = np.array([0.6, -0.8]), np.array([1.7, relative_rate]), np.array([0.0, 2.0])
    acceleration, force, joint_velocity = response(q, rates, torque)
    distal = torque[1] * rates.sum()
    proximal = -torque[1] * rates[0]
    assert distal + proximal == pytest.approx(torque[1] * relative_rate, abs=1e-12, rel=0)
    assert force @ joint_velocity + (-force) @ joint_velocity == pytest.approx(0.0)
    if relative_rate == 0:
        assert abs(acceleration[1]) > 1e-3  # An instantaneous zero rate is not a joint lock.
        assert distal != 0
    else:
        assert distal == pytest.approx(-1.2)
        assert distal + proximal == pytest.approx(-4.6)


@pytest.mark.content_lint
@pytest.mark.parametrize(
    "unsupported",
    [
        "active (you consciously pushing)",
        'We find that in the late downswing, the "Natural" power transfer',
        "Every movement has two sources of power",
        "underestimates the _capacity_ for delayed release",
        "From (2.3) and (2.6)",
        "ready to be wrapped in Streamlit",
        'gyroscopic coupling ("Beta axis")',
    ],
)
def test_article_removes_identified_unsupported_claims(unsupported: str) -> None:
    """Prevent the opening from reinstating inferences contradicted by the derivation."""
    assert unsupported not in SOURCE.read_text(encoding="utf-8")


@pytest.mark.content_lint
def test_published_force_powers_match_the_com_calculation() -> None:
    """Bind the displayed six-decimal power results to the reproducible example."""
    article = SOURCE.read_text(encoding="utf-8")
    q, rates = np.array([0.6, -0.8]), np.array([1.7, -2.3])
    _, drift_force, joint_velocity = response(q, rates, np.zeros(2))
    _, driven_force, _ = response(q, rates, np.array([2.0, 0.0]))
    for force in (drift_force, driven_force, driven_force - drift_force):
        assert f"{force @ joint_velocity:.6f}" in article
