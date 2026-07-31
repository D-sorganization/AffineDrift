"""Property tests for the discrete LQR solver and the ch06 worked example.

Issue #3518 found that the published ch06 example asserted stability for a closed
loop whose spectral radius was 1.043, from an ``S`` that was not a Riccati
solution at all. These tests assert the properties the chapter *claims*, so the
same class of error cannot reach the page again.
"""

from __future__ import annotations

import numpy as np
import pytest

from scripts.generate_worked_examples import CH06_A, CH06_B, CH06_Q, CH06_R, build
from src.affine_control.lqr import discrete_lqr

SYSTEMS = [
    # (name, A, B, Q, R) -- the ch06 pendulum plus unrelated stabilisable pairs.
    ("ch06_pendulum", CH06_A, CH06_B, CH06_Q, CH06_R),
    (
        "double_integrator",
        np.array([[1.0, 0.05], [0.0, 1.0]]),
        np.array([[0.00125], [0.05]]),
        np.diag([1.0, 0.1]),
        np.array([[0.5]]),
    ),
    (
        "unstable_scalar",
        np.array([[1.4]]),
        np.array([[1.0]]),
        np.array([[2.0]]),
        np.array([[1.0]]),
    ),
    (
        "coupled_3state",
        np.array([[1.0, 0.1, 0.0], [0.0, 1.0, 0.1], [0.2, 0.0, 0.9]]),
        np.array([[0.0], [0.0], [0.1]]),
        np.eye(3),
        np.array([[0.25]]),
    ),
]


@pytest.mark.parametrize(("name", "a", "b", "q", "r"), SYSTEMS)
def test_solution_satisfies_the_riccati_equation(
    name: str, a: np.ndarray, b: np.ndarray, q: np.ndarray, r: np.ndarray
) -> None:
    """The defining property. The published ch06 S had residual norm 16.25."""
    solution = discrete_lqr(a, b, q, r)
    assert solution.residual(a, b, q, r) < 1e-8, name


@pytest.mark.parametrize(("name", "a", "b", "q", "r"), SYSTEMS)
def test_riccati_solution_is_symmetric_positive_definite(
    name: str, a: np.ndarray, b: np.ndarray, q: np.ndarray, r: np.ndarray
) -> None:
    solution = discrete_lqr(a, b, q, r)
    np.testing.assert_allclose(solution.riccati, solution.riccati.T, atol=1e-12)
    assert np.min(np.linalg.eigvalsh(solution.riccati)) > 0.0, name


@pytest.mark.parametrize(("name", "a", "b", "q", "r"), SYSTEMS)
def test_closed_loop_is_stable(
    name: str, a: np.ndarray, b: np.ndarray, q: np.ndarray, r: np.ndarray
) -> None:
    """Spectral radius strictly inside the unit circle, for every system."""
    assert discrete_lqr(a, b, q, r).spectral_radius() < 1.0, name


@pytest.mark.parametrize(("name", "a", "b", "q", "r"), SYSTEMS)
def test_value_function_decreases_monotonically(
    name: str, a: np.ndarray, b: np.ndarray, q: np.ndarray, r: np.ndarray
) -> None:
    """V_k = x'Sx is a Lyapunov function for the closed loop."""
    solution = discrete_lqr(a, b, q, r)
    rng = np.random.default_rng(7)
    x0 = rng.normal(size=a.shape[0])
    values = [row[1] for row in solution.value_trajectory(x0, 25)]
    assert all(later < earlier for earlier, later in zip(values, values[1:], strict=False)), name


@pytest.mark.parametrize(("name", "a", "b", "q", "r"), SYSTEMS)
def test_contraction_rate_is_a_valid_bound(
    name: str, a: np.ndarray, b: np.ndarray, q: np.ndarray, r: np.ndarray
) -> None:
    """V_k <= rho^k V_0 must actually hold -- it is quoted as a guarantee."""
    solution = discrete_lqr(a, b, q, r)
    rho = solution.contraction_rate(q, r)
    assert 0.0 < rho < 1.0, name
    rng = np.random.default_rng(11)
    for _ in range(5):
        x0 = rng.normal(size=a.shape[0])
        rows = solution.value_trajectory(x0, 20)
        v0 = rows[0][1]
        for k, value, _norm in rows:
            assert value <= rho**k * v0 + 1e-9, f"{name}: bound violated at k={k}"


def test_ch06_gain_matches_the_defining_formula() -> None:
    """K = (R + B'SB)^-1 B'SA, recomputed from S rather than carried along."""
    solution = discrete_lqr(CH06_A, CH06_B, CH06_Q, CH06_R)
    expected = np.linalg.solve(
        CH06_R + CH06_B.T @ solution.riccati @ CH06_B,
        CH06_B.T @ solution.riccati @ CH06_A,
    )
    np.testing.assert_allclose(solution.gain, expected, atol=1e-12)


def test_ch06_published_values_are_the_solved_ones() -> None:
    """The generated fragment must carry the solver's numbers, not stale ones.

    Guards the specific regression: the fragment claiming stability while the
    matrix beside it is unstable.
    """
    fragment = next(iter(build().values()))
    solution = discrete_lqr(CH06_A, CH06_B, CH06_Q, CH06_R)

    assert f"{solution.spectral_radius():.4f}" in fragment
    assert solution.spectral_radius() < 1.0
    # The defect this replaces: spectral radius 1.043 presented as stable.
    assert "1.0434" not in fragment
    assert "\\newcommand{\\chsixSpectralRadius}{0.7298}" in fragment


def test_ch06_table_is_a_simulation_not_the_bound() -> None:
    """The decay-ratio column must vary; a constant column means rho^k was tabulated."""
    solution = discrete_lqr(CH06_A, CH06_B, CH06_Q, CH06_R)
    rows = solution.value_trajectory(np.array([1.0, 0.0]), 10)
    ratios = [later[1] / earlier[1] for earlier, later in zip(rows, rows[1:], strict=False)]
    assert max(ratios) - min(ratios) > 0.01, "decay ratios are suspiciously constant"
    # And the bound must be strictly looser than the trajectory it bounds.
    rho = solution.contraction_rate(CH06_Q, CH06_R)
    assert rows[-1][1] / rows[0][1] < rho**10


def test_non_stabilisable_pair_raises() -> None:
    """An uncontrollable unstable mode has no stabilising solution."""
    a = np.array([[1.5, 0.0], [0.0, 1.2]])
    b = np.array([[1.0], [0.0]])  # second mode unreachable and unstable
    with pytest.raises(ValueError, match="not stabilisable"):
        discrete_lqr(a, b, np.eye(2), np.array([[1.0]]))
