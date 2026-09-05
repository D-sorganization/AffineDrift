"""Counterexamples for control-theory publication corrections in #4149."""

from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_cross_cost_riccati_identity_keeps_both_cross_terms() -> None:
    """A nonzero cross cost must survive policy substitution."""
    gain = -0.75
    schur_value = 2 - 1.5**2 / 2
    substituted_value = 1 + 2 * gain * 0.5 + gain**2 + (1 + gain) ** 2
    assert schur_value == substituted_value == 0.875


def test_analytic_pendulum_balance_solution_satisfies_care() -> None:
    """Check the printed solution independently against the CARE and stability."""
    p12 = 1 + np.sqrt(11)
    p22 = (-0.2 + np.sqrt(0.04 + 40 * (2 * p12 + 10))) / 20
    p11 = 0.1 * p12 - 10 * p22 + 10 * p12 * p22
    value = np.array([[p11, p12], [p12, p22]])
    system = np.array([[0, 1], [10, -0.1]])
    input_map = np.array([[0], [1]])
    cost = np.diag([100, 10])
    gain = 10 * input_map.T @ value
    residual = system.T @ value + value @ system - value @ input_map @ gain + cost
    np.testing.assert_allclose(residual, 0, atol=1e-10)
    assert (np.linalg.eigvalsh(value) > 0).all()
    assert (np.linalg.eigvals(system - input_map @ gain).real < 0).all()
    np.testing.assert_allclose(gain, [[43.166, 13.551]], atol=0.001)


def test_finite_horizon_lqr_is_finite_with_no_control_authority() -> None:
    """For x'=x, B=0, terminal cost zero, S(t)=(exp(2(T-t))-1)/2."""
    horizon = 1.0
    times = np.linspace(0, horizon, 20)
    value_curvature = np.expm1(2 * (horizon - times)) / 2
    derivative = -np.exp(2 * (horizon - times))
    np.testing.assert_allclose(-derivative, 2 * value_curvature + 1)
    assert np.isfinite(value_curvature).all()
    assert value_curvature[-1] == 0


def test_larger_stiffness_does_not_change_kinematic_jacobian_rank() -> None:
    """Task displacement y=q1+q2 has rank one for every finite spring stiffness."""
    jacobian = np.array([[1.0, 1.0]])
    stiffness = np.diag([2.0, 3.0])
    compliance = jacobian @ np.linalg.solve(stiffness, jacobian.T)
    stiffer_compliance = jacobian @ np.linalg.solve(10 * stiffness, jacobian.T)
    assert np.linalg.matrix_rank(jacobian) == 1
    np.testing.assert_allclose(stiffer_compliance, compliance / 10)


@pytest.mark.content_lint
@pytest.mark.parametrize(
    "relative_path",
    (
        "articles/The_Geometry_of_Motion/Volume_I/chapters/ch05_optimal_control.tex",
        "articles/The_Geometry_of_Motion/quarto/ch05_optimal_control.qmd",
    ),
)
def test_optimal_control_editions_use_cost_gradient_and_conditional_convergence(
    relative_path: str,
) -> None:
    source = (ROOT / relative_path).read_text(encoding="utf-8")
    assert "control maximizes the Hamiltonian" not in source
    assert "the re-linearization\nis exact" not in source
    assert "the cost and dynamics are\nquadratic" not in source
    assert "costate trajectory" not in source or "gradient of" in source


@pytest.mark.content_lint
def test_tangent_lqr_does_not_require_controllability_for_finite_horizon() -> None:
    source = (
        ROOT / "articles/tangent-hyperplane-contraction/chapters/03-local-optimal-control.qmd"
    ).read_text(encoding="utf-8")
    assert "the Riccati equation becomes singular and the LQR framework breaks" not in source
