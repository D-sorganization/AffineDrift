"""Tests Extracting and Validating Continuous LQR from Chapter 10 Listings.

This module extracts Python listings from LaTeX source, executes them in a
controlled namespace, and verifies the mathematical properties of the continuous
infinite-horizon Linear Quadratic Regulator (LQR) problem.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from scipy.integrate import quad


def extract_listing_code(tex_path: Path) -> str:
    """Read all Python listings at the required canonical source path."""
    assert tex_path.is_file(), f"Missing source: {tex_path}"
    blocks = re.findall(
        r"\\begin\{lstlisting\}\[language=Python[^\]]*\](.*?)\\end\{lstlisting\}",
        tex_path.read_text(encoding="utf-8"),
        re.DOTALL,
    )
    assert blocks, "Missing Python listings"
    return "\n\n".join(blocks)


@pytest.fixture(scope="module")
def lqr_module() -> dict[str, Any]:
    """Compile and Execute Extracted Chapter Code into a Test Namespace.

    nosemgrep: python.lang.security.audit.exec-detected
    Exec is strictly constrained to extracted textbook listings from the repo's
    fixed LaTeX source path to verify executable mathematical correctness.
    """
    root_dir = Path(__file__).resolve().parents[1]
    tex_path = (
        root_dir
        / "articles"
        / "The_Geometry_of_Motion"
        / "Volume_IV"
        / "chapters"
        / "ch10_computational_models.tex"
    )
    code_str = extract_listing_code(tex_path)
    namespace: dict[str, Any] = {"__name__": "listing_tests"}
    compiled = compile(code_str, filename=str(tex_path), mode="exec", dont_inherit=True)
    # Repository-owned listings at a fixed path, with no external input.
    # nosemgrep: python.lang.security.audit.exec-detected.exec-detected
    exec(compiled, namespace)

    assert "LQRProblem" in namespace, "Extracted listing did not define 'LQRProblem'"
    return namespace


def test_scalar_problem_solution(lqr_module: dict[str, Any]) -> None:
    """Verify Scalar System Riccati and Gain Closed-Form Solution."""
    lqr_cls = lqr_module["LQRProblem"]
    prob = lqr_cls(A=[[0.0]], B=[[1.0]], Q=[[4.0]], R=[[1.0]])
    k, p = prob.solve()
    assert np.allclose(p, [[2.0]], atol=1e-7)
    assert np.allclose(k, [[2.0]], atol=1e-7)


def test_undetectable_unstable_cost_free_mode_is_rejected(lqr_module: dict[str, Any]) -> None:
    """CARE's stabilizing branch need not minimize cost without detectability."""
    problem = lqr_module["LQRProblem"](A=[[1.0]], B=[[1.0]], Q=[[0.0]], R=[[1.0]])
    with pytest.raises(ValueError):
        problem.solve()


def test_scalar_asymptotic_energy_independent_oracle(lqr_module: dict[str, Any]) -> None:
    """Verify Asymptotic Quadratic Cost Matches Independent Integration."""
    lqr_cls = lqr_module["LQRProblem"]
    prob = lqr_cls(A=[[0.0]], B=[[1.0]], Q=[[4.0]], R=[[1.0]])
    k, p = prob.solve()

    x0 = np.array([3.0])
    analytic_cost = float(x0.T @ p @ x0)
    a_cl = -float(k[0, 0])

    def integrand(t: float) -> float:
        xt = float(x0[0] * np.exp(a_cl * t))
        ut = float(-k[0, 0] * xt)
        return float(xt * 4.0 * xt + ut * 1.0 * ut)

    oracle_cost, _ = quad(integrand, 0.0, np.inf)
    assert np.isclose(analytic_cost, oracle_cost, rtol=1e-5)


def test_double_integrator_velocity_penalty(lqr_module: dict[str, Any]) -> None:
    """Verify Double Integrator Yields Damping Despite Zero Velocity Weight."""
    lqr_cls = lqr_module["LQRProblem"]
    a_mat = np.array([[0.0, 1.0], [0.0, 0.0]])
    b_mat = np.array([[0.0], [1.0]])
    q_mat = np.diag([1.0, 0.0])
    r_mat = np.array([[1.0]])

    prob = lqr_cls(A=a_mat, B=b_mat, Q=q_mat, R=r_mat)
    k, p = prob.solve()

    sqrt2 = np.sqrt(2.0)
    expected_p = np.array([[sqrt2, 1.0], [1.0, sqrt2]])
    expected_k = np.array([[1.0, sqrt2]])

    assert np.allclose(p, expected_p, atol=1e-6)
    assert np.allclose(k, expected_k, atol=1e-6)
    assert k[0, 1] > 0.0, "Velocity feedback must be strictly non-zero"


def test_stable_decoupled_free_coordinate(lqr_module: dict[str, Any]) -> None:
    """Verify Stable Decoupled Coordinate with Zero Cost Yields Zero Gain."""
    lqr_cls = lqr_module["LQRProblem"]
    a_mat = np.diag([-1.0, -2.0])
    b_mat = np.eye(2)
    q_mat = np.diag([1.0, 0.0])
    r_mat = np.eye(2)

    prob = lqr_cls(A=a_mat, B=b_mat, Q=q_mat, R=r_mat)
    k, p = prob.solve()

    expected_p00 = np.sqrt(2.0) - 1.0
    expected_p = np.diag([expected_p00, 0.0])
    expected_k = np.diag([expected_p00, 0.0])

    assert np.allclose(p, expected_p, atol=1e-6)
    assert np.allclose(k, expected_k, atol=1e-6)


def test_stabilizable_not_controllable_system(lqr_module: dict[str, Any]) -> None:
    """Verify LQR Solves Successfully for Stabilizable Uncontrollable System."""
    lqr_cls = lqr_module["LQRProblem"]
    a_mat = np.diag([1.0, -1.0])
    b_mat = np.array([[1.0], [0.0]])
    q_mat = np.eye(2)
    r_mat = np.array([[1.0]])

    prob = lqr_cls(A=a_mat, B=b_mat, Q=q_mat, R=r_mat)
    k, p = prob.solve()

    assert p.shape == (2, 2)
    assert k.shape == (1, 2)
    a_cl = a_mat - b_mat @ k
    eigenvalues = np.linalg.eigvals(a_cl)
    assert np.all(eigenvalues.real < 0.0)


def test_unstabilizable_system_raises_value_error(lqr_module: dict[str, Any]) -> None:
    """Verify Unstabilizable Uncontrollable System Fails CARE Solution."""
    lqr_cls = lqr_module["LQRProblem"]
    a_mat = np.diag([1.0, 1.0])
    b_mat = np.array([[1.0], [0.0]])
    q_mat = np.eye(2)
    r_mat = np.array([[1.0]])

    prob = lqr_cls(A=a_mat, B=b_mat, Q=q_mat, R=r_mat)
    with pytest.raises(ValueError) as excinfo:
        prob.solve()
    assert len(str(excinfo.value)) > 0


def test_care_algebraic_residual(lqr_module: dict[str, Any]) -> None:
    """Verify Solution Satisfies Continuous Algebraic Riccati Equation."""
    lqr_cls = lqr_module["LQRProblem"]
    a_mat = np.array([[0.0, 1.0], [-2.0, -3.0]])
    b_mat = np.array([[0.0], [1.0]])
    q_mat = np.diag([3.0, 2.0])
    r_mat = np.array([[0.5]])

    prob = lqr_cls(A=a_mat, B=b_mat, Q=q_mat, R=r_mat)
    k, p = prob.solve()

    sinv_term = p @ b_mat @ np.linalg.solve(r_mat, b_mat.T @ p)
    residual = a_mat.T @ p + p @ a_mat - sinv_term + q_mat
    assert np.allclose(residual, 0.0, atol=1e-7)
    assert np.allclose(k, np.linalg.solve(r_mat, b_mat.T @ p), atol=1e-7)


def test_closed_loop_strictly_stable_spectrum(lqr_module: dict[str, Any]) -> None:
    """Verify Closed Loop Matrix Has Strictly Negative Real Eigenvalues."""
    lqr_cls = lqr_module["LQRProblem"]
    a_mat = np.array([[1.0, 2.0], [0.0, 1.0]])
    b_mat = np.array([[0.0], [1.0]])
    q_mat = np.eye(2)
    r_mat = np.array([[1.0]])

    prob = lqr_cls(A=a_mat, B=b_mat, Q=q_mat, R=r_mat)
    k, _ = prob.solve()

    a_cl = a_mat - b_mat @ k
    eigs = np.linalg.eigvals(a_cl)
    assert np.all(np.real(eigs) < -1e-5)


def test_uniform_cost_scaling_homogeneity(lqr_module: dict[str, Any]) -> None:
    """Verify Scaling Q and R Scales Riccati Matrix P while Invariantizing K."""
    lqr_cls = lqr_module["LQRProblem"]
    a_mat = np.array([[0.0, 1.0], [0.0, 0.0]])
    b_mat = np.array([[0.0], [1.0]])
    q_mat = np.diag([2.0, 1.0])
    r_mat = np.array([[1.0]])

    base_prob = lqr_cls(A=a_mat, B=b_mat, Q=q_mat, R=r_mat)
    k_base, p_base = base_prob.solve()

    scale = 2.0
    scaled_prob = lqr_cls(A=a_mat, B=b_mat, Q=scale * q_mat, R=scale * r_mat)
    k_scaled, p_scaled = scaled_prob.solve()

    assert np.allclose(p_scaled, scale * p_base, atol=1e-7)
    assert np.allclose(k_scaled, k_base, atol=1e-7)


@pytest.mark.parametrize(
    "matrices",
    [
        (np.nan * np.eye(2), np.ones((2, 1)), np.eye(2), np.eye(1)),
        (np.ones((2, 3)), np.ones((2, 1)), np.eye(2), np.eye(1)),
        (np.eye(2), np.ones((3, 1)), np.eye(2), np.eye(1)),
        (np.eye(2), np.ones((2, 1)), np.eye(3), np.eye(1)),
        (np.eye(2), np.ones((2, 1)), np.eye(2), np.eye(2)),
    ],
)
def test_invalid_dimension_and_nonfinite_inputs(
    lqr_module: dict[str, Any],
    matrices: tuple[np.ndarray, ...],
) -> None:
    """Verify Shape Mismatches and Non-Finite Matrices Raise ValueError."""
    lqr_cls = lqr_module["LQRProblem"]
    with pytest.raises(ValueError):
        lqr_cls(*matrices)


def test_asymmetric_weighting_matrices(lqr_module: dict[str, Any]) -> None:
    """Verify Non-Symmetric Q or R Matrices Raise ValueError."""
    lqr_cls = lqr_module["LQRProblem"]
    a_mat = np.eye(2)
    b_mat = np.ones((2, 1))

    q_asym = np.array([[1.0, 2.0], [0.0, 1.0]])
    with pytest.raises(ValueError):
        lqr_cls(A=a_mat, B=b_mat, Q=q_asym, R=np.eye(1))

    r_asym = np.array([[1.0, 2.0], [0.0, 1.0]])
    with pytest.raises(ValueError):
        lqr_cls(A=a_mat, B=np.eye(2), Q=np.eye(2), R=r_asym)


def test_indefinite_q_matrix_rejection(lqr_module: dict[str, Any]) -> None:
    """Verify Negative Definite or Indefinite Q Raises ValueError."""
    lqr_cls = lqr_module["LQRProblem"]
    a_mat = np.eye(2)
    b_mat = np.ones((2, 1))
    q_neg = np.diag([1.0, -0.5])
    with pytest.raises(ValueError):
        lqr_cls(A=a_mat, B=b_mat, Q=q_neg, R=np.eye(1))


def test_singular_and_indefinite_r_matrix_rejection(lqr_module: dict[str, Any]) -> None:
    """Verify Non-Positive-Definite or Singular R Raises ValueError."""
    lqr_cls = lqr_module["LQRProblem"]
    a_mat = np.eye(2)
    b_mat = np.eye(2)
    q_mat = np.eye(2)

    r_singular = np.diag([1.0, 0.0])
    with pytest.raises(ValueError):
        lqr_cls(A=a_mat, B=b_mat, Q=q_mat, R=r_singular)

    r_neg = np.diag([1.0, -1.0])
    with pytest.raises(ValueError):
        lqr_cls(A=a_mat, B=b_mat, Q=q_mat, R=r_neg)
