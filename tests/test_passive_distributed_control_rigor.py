"""Independent mechanics checks for the paired passive-control treatment."""

from pathlib import Path

import numpy as np
import pytest
import sympy as sp
from scipy.integrate import quad, solve_ivp
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = (
    ROOT / "articles/The_Physics_of_Golf/chapters/ch27_passive_distributed_control.tex",
    ROOT / "articles/The_Physics_of_Golf/quarto/ch27_passive_distributed_control.qmd",
)


def test_additive_impedance_does_not_double_kinematic_velocity() -> None:
    mass = np.array([[2.0, 0.3], [0.3, 1.0]])
    velocity = np.array([0.7, -0.2])
    load = np.array([3.0, -1.0])
    impedance = np.array([-0.4, 0.6])
    bare = np.r_[velocity, np.linalg.solve(mass, load)]
    addition = np.r_[np.zeros(2), np.linalg.solve(mass, impedance)]
    np.testing.assert_allclose(
        bare + addition, np.r_[velocity, np.linalg.solve(mass, load + impedance)]
    )


def test_variable_inertia_energy_uses_coriolis_cancellation() -> None:
    q, v, k, d, g, u, q0 = sp.symbols("q v k d g u q0", real=True)
    mass = 1 + q**2
    storage = mass * v**2 / 2 + g * q**2 / 2 + k * (q - q0) ** 2 / 2
    acceleration = (u - q * v**2 - g * q - k * (q - q0) - d * v) / mass
    derivative = sp.diff(storage, q) * v + sp.diff(storage, v) * acceleration
    assert sp.simplify(derivative - (u * v - d * v**2)) == 0


def test_moving_reference_and_stiffness_supply_power() -> None:
    t = sp.symbols("t", real=True)
    q, reference, stiffness = (sp.Function(name)(t) for name in ("q", "reference", "stiffness"))
    error = q - reference
    derivative = sp.diff(stiffness * error**2 / 2, t)
    expected = (
        stiffness * error * sp.diff(q, t)
        - stiffness * error * sp.diff(reference, t)
        + sp.diff(stiffness, t) * error**2 / 2
    )
    assert sp.simplify(derivative - expected) == 0


def test_error_tracking_solution_and_work_identity() -> None:
    inertia, damping, stiffness = 1.0, 5.0, 100.0
    matrix = np.array([[0.0, 1.0], [-stiffness / inertia, -damping / inertia]])
    initial = np.array([0.1, 0.0])
    result = solve_ivp(
        lambda t, x: matrix @ x, (0, 1), initial, rtol=1e-11, atol=1e-13, dense_output=True
    )
    assert result.success
    for time in (0.1, 0.4, 1.0):
        np.testing.assert_allclose(result.sol(time), expm(matrix * time) @ initial, atol=1e-11)
    final = result.sol(1)
    loss = quad(lambda t: damping * result.sol(t)[1] ** 2, 0, 1, epsabs=1e-11)[0]
    assert 0.5 * (inertia * final[1] ** 2 + stiffness * final[0] ** 2) + loss == pytest.approx(
        0.5, abs=1e-10
    )


def test_damping_regimes_and_slow_overdamped_pole() -> None:
    under = np.roots([1, 5, 100])
    critical = np.roots([1, 20, 100])
    over = np.roots([1, 50, 100])
    assert np.all(np.abs(under.imag) > 0)
    np.testing.assert_allclose(critical.real, [-10, -10])
    np.testing.assert_allclose(critical.imag, 0)
    assert np.all(over.imag == 0)
    assert max(over.real) == pytest.approx(-2.0871215252208)
    assert max(over.real) > max(critical.real)


def test_dissipation_is_semidefinite_at_zero_velocity() -> None:
    position, velocity, stiffness, damping = 0.1, 0.0, 100.0, 5.0
    assert 0.5 * stiffness * position**2 > 0
    assert -damping * velocity**2 == 0
    assert -stiffness * position != 0


def test_delayed_restoring_feedback_can_supply_positive_mean_power() -> None:
    amplitude, frequency, delay, gain = 0.01, 20.0, 0.05, 10.0
    period = 2 * np.pi / frequency
    actual = (
        quad(
            lambda t: (-gain * amplitude * np.cos(frequency * (t - delay)))
            * (-amplitude * frequency * np.sin(frequency * t)),
            0,
            period,
        )[0]
        / period
    )
    expected = 0.5 * gain * amplitude**2 * frequency * np.sin(frequency * delay)
    assert actual == pytest.approx(expected)
    assert actual > 0


def test_dynamic_stiffness_and_impedance_use_different_ports() -> None:
    inertia, damping, stiffness = 1.0, 5.0, 100.0
    for frequency in (1.0, 10.0, 25.0):
        s = 1j * frequency
        impedance = inertia * s + damping + stiffness / s
        dynamic_stiffness = inertia * s**2 + damping * s + stiffness
        assert s * impedance == pytest.approx(dynamic_stiffness)
        assert impedance.real == pytest.approx(damping)


def test_preload_changes_joint_tangent_stiffness() -> None:
    q = sp.symbols("q", real=True)
    endpoint = sp.cos(q)
    rest, stiffness = sp.Rational(1, 2), sp.Integer(10)
    potential = stiffness * (endpoint - rest) ** 2 / 2
    tangent = sp.diff(potential, q, 2)
    jacobian_term = stiffness * sp.diff(endpoint, q) ** 2
    preload_term = stiffness * (endpoint - rest) * sp.diff(endpoint, q, 2)
    assert sp.simplify(tangent - jacobian_term - preload_term) == 0
    assert tangent.subs(q, 0) == -5
    assert jacobian_term.subs(q, 0) == 0


def test_single_frequency_cannot_separate_unknown_inertia_and_stiffness() -> None:
    time = np.linspace(0, 2 * np.pi, 400)
    angle = np.cos(time)
    speed = -np.sin(time)
    acceleration = -angle
    design = np.column_stack([acceleration, speed, angle])
    assert np.linalg.matrix_rank(design) == 2
    assert np.linalg.matrix_rank(design[:, 1:]) == 2


@pytest.mark.parametrize("path", CHAPTERS, ids=("print", "web"))
def test_paired_publication_retains_corrected_proof_and_counterfactual(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert "dynamic stiffness" in text.lower()
    assert "negative semidefinite" in text.lower()
    assert "120--180" in text
    assert "parameter power" in text.lower()
    assert "cannot identify" in text.lower()
    assert "20,000 decisions" not in text
    assert "40--50" not in text
    assert "Have a partner apply" not in text
    assert r"\begin{bmatrix}0" in text


def test_web_prose_and_exercise_labels_are_not_raw_latex() -> None:
    text = CHAPTERS[1].read_text(encoding="utf-8")
    assert r"\emph{" not in text
    assert r"\textbf{" not in text
    assert "*negative semidefinite*" in text
    assert text.count("**Answer.**") == 12
