"""Independent mechanical counterexamples for paired Chapter 29, issue #4295."""

from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "articles/The_Physics_of_Golf"
SOURCES = (
    BOOK / "quarto/ch29_joint_damping_friction.qmd",
    BOOK / "chapters/ch29_joint_damping_friction.tex",
)


@pytest.mark.parametrize("source", SOURCES, ids=("quarto", "latex"))
def test_paired_chapter_qualifies_grip_stability_and_units(source: Path) -> None:
    text = source.read_text(encoding="utf-8")
    for unsupported in (
        "7000",
        "17 times",
        "17 \\times",
        "approximately 17",
        "damping moves the eigenvalues into the left half-plane",
        "giving a constant friction torque of 5",
        "Modern drivers use relatively low-damping graphite shafts precisely",
        "Empirically, this derivative is approximately",
        "Most human joints are",
        "overkill for biomechanics",
    ):
        assert unsupported not in text
    for required in (
        "synthetic",
        "positive definite",
        "moving",
        "frequency",
        "negative stiffness",
        "moment arm",
        "sticking",
        "blinded",
        "chiementin2019grip",
        "bloch1994dissipation",
    ):
        assert required in text


def test_passive_damping_does_not_stabilize_negative_stiffness() -> None:
    # q'' + q' - q = 0: one growing real root remains despite positive damping.
    roots = np.roots([1, 1, -1])
    assert max(roots.real) == pytest.approx((np.sqrt(5) - 1) / 2)


def test_gyroscopic_stabilization_can_be_destroyed_by_positive_damping() -> None:
    # Dimensionless M=I, K=-I, G=[[0,-3],[3,0]]. Undamped roots are distinct
    # imaginary pairs; C=0.1 I creates two growing roots without negative loss.
    def generator(damping: float) -> np.ndarray:
        velocity = np.array([[damping, -3], [3, damping]])
        return np.block([[np.zeros((2, 2)), np.eye(2)], [np.eye(2), -velocity]])

    undamped = np.linalg.eigvals(generator(0))
    np.testing.assert_allclose(undamped.real, 0, atol=1e-14)
    np.testing.assert_allclose(
        np.sort(abs(undamped.imag)), np.repeat([(3 - np.sqrt(5)) / 2, (3 + np.sqrt(5)) / 2], 2)
    )
    damped = np.linalg.eigvals(generator(0.1))
    assert np.count_nonzero(damped.real > 0.017) == 2


def test_ideal_constraint_projection_preserves_loss_without_creating_it() -> None:
    basis = np.array([[1, 0], [0, 1], [1, 2]])
    constraint = np.array([[-1, -2, 1]])
    damping = np.diag([0.2, 0.4, 0.7])
    reduced_velocity = np.array([2, -0.3])
    velocity = basis @ reduced_velocity
    np.testing.assert_array_equal(constraint @ basis, 0)
    assert velocity @ constraint.T @ np.array([3.0]) == pytest.approx(0)
    reduced = basis.T @ damping @ basis
    assert reduced_velocity @ reduced @ reduced_velocity == pytest.approx(
        velocity @ damping @ velocity
    )
    assert np.min(np.linalg.eigvalsh(reduced)) > 0


def test_same_joint_damping_does_not_impose_a_proximal_power_order() -> None:
    coefficient = 0.2
    speed = np.array([10.0, 30.0])
    np.testing.assert_allclose(coefficient * speed**2, [20, 180])
    assert (7000 / 3000) ** 2 == pytest.approx(49 / 9)


def test_stribeck_sliding_limits_and_torque_units() -> None:
    static, kinetic, transition = 0.3, 0.1, 0.2
    speed = np.array([1e-9, 100])
    magnitude = kinetic + (static - kinetic) * np.exp(-((speed / transition) ** 2))
    np.testing.assert_allclose(magnitude, [static, kinetic])
    assert np.all((-magnitude * speed) <= 0)
    # mu*N is force; multiplying by the declared lever arm gives torque.
    torque = 0.1 * 50 * 0.02
    assert torque == pytest.approx(0.1)
    assert torque / 0.5 == pytest.approx(0.2)


def test_synthetic_speed_sensitivity_has_one_sign_and_correct_conversion() -> None:
    change = -0.02 * 5
    assert change == pytest.approx(-0.1)
    assert change / 0.44704 == pytest.approx(-0.2236936292)


def test_modal_decay_and_quality_factor_do_not_identify_shaft_material() -> None:
    frequency, damping_ratio = 100.0, 0.01
    angular = 2 * np.pi * frequency
    quality = 1 / (2 * damping_ratio)
    amplitude_time = 1 / (damping_ratio * angular)
    assert quality == 50
    assert amplitude_time == pytest.approx(0.1591549431)
    logarithmic_decrement = 2 * np.pi * damping_ratio / np.sqrt(1 - damping_ratio**2)
    assert 1 - np.exp(-2 * logarithmic_decrement) == pytest.approx(0.11809, abs=1e-5)


def test_exercise_power_and_oscillator_numbers_use_angular_units() -> None:
    power = 0.5 * 10**2 + 0.15 * 30**2
    assert power == 185
    assert power / 400 == pytest.approx(0.4625)
    inertia, stiffness, damping = 0.05, 5.0, 0.2
    frequency = np.sqrt(stiffness / inertia)
    ratio = damping / (2 * np.sqrt(stiffness * inertia))
    assert frequency == 10
    assert ratio == pytest.approx(0.2)
    assert 4 / (ratio * frequency) == pytest.approx(2)


def test_bristle_storage_requires_the_full_output_power_balance() -> None:
    # Positive coefficients alone do not make the proposed quadratic storage
    # certify the full bristle-damping output for every initialized state.
    stiffness, microdamping, viscosity = 1.0, 1.0, 0.0
    state, velocity, friction_level = 0.2, 1.0, 0.1
    rate = velocity - stiffness * abs(velocity) * state / friction_level
    effort = stiffness * state + microdamping * rate + viscosity * velocity
    storage_rate = stiffness * state * rate
    supplied_minus_stored = effort * velocity - storage_rate
    expected = (
        stiffness**2 * abs(velocity) * state**2 / friction_level
        + microdamping * rate * velocity
        + viscosity * velocity**2
    )
    assert supplied_minus_stored == pytest.approx(expected)
    assert supplied_minus_stored == pytest.approx(-0.6)
    for source in SOURCES:
        assert r"\sigma_0^2" in source.read_text(encoding="utf-8")
