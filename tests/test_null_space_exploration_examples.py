"""Property and counterexample tests for the null-space exploration companion (#5094).

Each proposition P1-P5 and P7 of the article "After One Solution: Exploring Dynamically
Equivalent Force Allocations" has at least one Hypothesis property test and one explicit
counterexample test.  The module under test is self-contained (numpy and scipy only), so these
tests compare it against independent constructions (SVD factories, full KKT solves, brute-force
sampling) rather than against its own helpers.
"""

import json
import math
from pathlib import Path
from typing import cast

import numpy as np
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st
from numpy.typing import NDArray

from scripts import build_null_space_exploration_examples as builder
from src.tools.null_space_exploration_examples import (
    ForceFrame,
    affine_fibre,
    framewise_vs_coupled_envelope,
    functional_interval,
    functional_invariance,
    grip_example,
    kkt_minimiser,
    leakage_bound,
    linear_section,
    reduced_quadratic,
    rescaled_representative,
    three_muscle_example,
    weighted_representative,
)

type Array = NDArray[np.float64]

SEEDS = st.integers(min_value=0, max_value=2**32 - 1)
DIMS = st.integers(min_value=1, max_value=6)
PROPERTY = settings(max_examples=60, deadline=None)


def _orthogonal(rng: np.random.Generator, rows: int, cols: int) -> Array:
    """Return a matrix with orthonormal columns (rows >= cols)."""
    factor, _ = np.linalg.qr(rng.standard_normal((rows, max(rows, cols))))
    return np.asarray(factor[:rows, :cols])


def _system(seed: int, m: int, n: int, rank: int) -> Array:
    """Build a well-conditioned m-by-n matrix of exactly the requested rank."""
    rng = np.random.default_rng(seed)
    if rank == 0:
        return np.zeros((m, n))
    values = rng.uniform(1.0, 10.0, size=rank)
    return np.asarray(_orthogonal(rng, m, rank) @ np.diag(values) @ _orthogonal(rng, n, rank).T)


@st.composite
def consistent_systems(draw: st.DrawFn, full_row_rank: bool = False) -> tuple[Array, Array, Array]:
    """Draw (A, b, u0) with A u0 = b; rank is 0..min(m, n) or, if requested, exactly m."""
    n = draw(DIMS)
    m = draw(st.integers(1, n)) if full_row_rank else draw(DIMS)
    rank = m if full_row_rank else draw(st.integers(min_value=0, max_value=min(m, n)))
    matrix = _system(draw(SEEDS), m, n, rank)
    u0 = np.random.default_rng(draw(SEEDS)).standard_normal(n)
    return matrix, matrix @ u0, u0


def _spd(seed: int, n: int) -> Array:
    rng = np.random.default_rng(seed)
    factor = rng.standard_normal((n, n))
    return np.asarray(factor @ factor.T + np.eye(n))


# ----------------------------------------------------------------------------------- P1


@PROPERTY
@given(consistent_systems())
def test_p1_fibre_is_complete_and_dimension_counts(
    system: tuple[Array, Array, Array],
) -> None:
    matrix, b, u0 = system
    fibre = affine_fibre(matrix, b, rtol=1e-10)
    n = matrix.shape[1]
    assert fibre.consistent
    assert fibre.rank == np.linalg.matrix_rank(matrix)
    assert fibre.kernel.shape == (n, n - fibre.rank)
    np.testing.assert_allclose(matrix @ fibre.particular, b, atol=1e-9)
    np.testing.assert_allclose(matrix @ fibre.kernel, 0.0, atol=1e-9)
    np.testing.assert_allclose(
        fibre.kernel.T @ fibre.kernel, np.eye(fibre.kernel.shape[1]), atol=1e-9
    )
    # Completeness: every solution differs from u_p by a kernel element.
    gap = u0 - fibre.particular
    np.testing.assert_allclose(fibre.kernel @ (fibre.kernel.T @ gap), gap, atol=1e-8)


@PROPERTY
@given(consistent_systems(), SEEDS)
def test_p1_every_kernel_step_stays_on_the_fibre(
    system: tuple[Array, Array, Array], seed: int
) -> None:
    matrix, b, _ = system
    fibre = affine_fibre(matrix, b, rtol=1e-10)
    z = 100.0 * np.random.default_rng(seed).standard_normal(fibre.kernel.shape[1])
    np.testing.assert_allclose(
        matrix @ (fibre.particular + fibre.kernel @ z), b, atol=1e-6, rtol=1e-9
    )


@PROPERTY
@given(SEEDS, st.integers(2, 6), st.integers(2, 6))
def test_p1_inconsistent_system_is_flagged_empty(seed: int, m: int, n: int) -> None:
    rank = min(m, n) - 1
    matrix = _system(seed, m, n, rank)
    left_null = np.linalg.svd(matrix)[0][:, rank:]
    assume(left_null.shape[1] > 0)
    b = matrix @ np.ones(n) + left_null[:, 0]  # off-range component of unit size
    fibre = affine_fibre(matrix, b, rtol=1e-10)
    assert not fibre.consistent
    assert fibre.residual == pytest.approx(1.0, rel=1e-8)


def test_p1_counterexample_duplicate_rows_with_conflicting_rhs() -> None:
    matrix = np.array([[1.0, 1.0], [1.0, 1.0]])
    assert not affine_fibre(matrix, np.array([1.0, 2.0]), rtol=1e-10).consistent
    consistent = affine_fibre(matrix, np.array([1.0, 1.0]), rtol=1e-10)
    assert consistent.consistent and consistent.rank == 1
    assert consistent.kernel.shape == (2, 1)


def test_p1_zero_nullity_fibre_is_a_single_point() -> None:
    fibre = affine_fibre(np.array([[2.0, 0.0], [0.0, 4.0]]), np.array([2.0, 4.0]), rtol=1e-10)
    assert fibre.kernel.shape == (2, 0)
    np.testing.assert_allclose(fibre.particular, [1.0, 1.0])


# ----------------------------------------------------------------------------------- P2


@PROPERTY
@given(consistent_systems(), SEEDS)
def test_p2_weighted_representative_and_self_adjoint_projector(
    system: tuple[Array, Array, Array], seed: int
) -> None:
    matrix, b, _ = system
    n = matrix.shape[1]
    weight = _spd(seed, n)
    rep = weighted_representative(matrix, b, weight)
    np.testing.assert_allclose(matrix @ rep.u_w, b, atol=1e-8)
    np.testing.assert_allclose(rep.projector @ rep.projector, rep.projector, atol=1e-8)
    np.testing.assert_allclose(weight @ rep.projector, rep.projector.T @ weight, atol=1e-8)
    np.testing.assert_allclose(matrix @ rep.projector, 0.0, atol=1e-8)
    np.testing.assert_allclose(rep.projector @ rep.u_w, 0.0, atol=1e-8)  # W-orthogonal to kernel


@PROPERTY
@given(consistent_systems())
def test_p2_identity_weight_gives_minimum_norm_solution(
    system: tuple[Array, Array, Array],
) -> None:
    matrix, b, _ = system
    rep = weighted_representative(matrix, b, np.eye(matrix.shape[1]))
    np.testing.assert_allclose(rep.u_w, np.linalg.pinv(matrix) @ b, atol=1e-8)


@PROPERTY
@given(consistent_systems(), SEEDS)
def test_p2_unit_rescaling_moves_within_the_fibre_never_off(
    system: tuple[Array, Array, Array], seed: int
) -> None:
    matrix, b, _ = system
    fibre = affine_fibre(matrix, b, rtol=1e-10)
    scale = np.exp(np.random.default_rng(seed).uniform(-3.0, 3.0, size=matrix.shape[1]))
    moved = rescaled_representative(matrix, b, scale)
    np.testing.assert_allclose(matrix @ moved, b, atol=1e-7, rtol=1e-9)
    gap = moved - fibre.particular
    np.testing.assert_allclose(fibre.kernel @ (fibre.kernel.T @ gap), gap, atol=1e-6)


def test_p2_counterexample_weighted_and_euclidean_representatives_differ() -> None:
    matrix, b = np.array([[1.0, 1.0]]), np.array([2.0])
    rep = weighted_representative(matrix, b, np.diag([1.0, 4.0]))
    np.testing.assert_allclose(rep.u_w, [1.6, 0.4])
    euclid = weighted_representative(matrix, b, np.eye(2)).u_w
    np.testing.assert_allclose(euclid, [1.0, 1.0])
    for point in (rep.u_w, euclid, rescaled_representative(matrix, b, np.array([1.0, 0.5]))):
        assert float((matrix @ point)[0]) == pytest.approx(2.0)
    # Rescaling changes the representative (that is the point) but not the fibre.
    assert not np.allclose(rescaled_representative(matrix, b, np.array([1.0, 0.5])), euclid)


# ----------------------------------------------------------------------------------- P3


@PROPERTY
@given(consistent_systems(full_row_rank=True), SEEDS, SEEDS)
def test_p3_reduced_minimiser_matches_full_kkt_solve(
    system: tuple[Array, Array, Array], hseed: int, gseed: int
) -> None:
    matrix, b, _ = system
    n = matrix.shape[1]
    hessian = _spd(hseed, n)
    gradient = np.random.default_rng(gseed).standard_normal(n)
    fibre = affine_fibre(matrix, b, rtol=1e-10)
    reduced = reduced_quadratic(hessian, gradient, fibre.particular, fibre.kernel)
    np.testing.assert_allclose(
        reduced.u_star, kkt_minimiser(hessian, gradient, matrix, b), atol=1e-7
    )
    np.testing.assert_allclose(reduced.hessian, fibre.kernel.T @ hessian @ fibre.kernel, atol=1e-10)


@PROPERTY
@given(consistent_systems(), SEEDS, SEEDS, SEEDS)
def test_p3_minimiser_independent_of_particular_solution_and_basis(
    system: tuple[Array, Array, Array], hseed: int, gseed: int, qseed: int
) -> None:
    matrix, b, u0 = system
    n = matrix.shape[1]
    hessian = _spd(hseed, n)
    gradient = np.random.default_rng(gseed).standard_normal(n)
    fibre = affine_fibre(matrix, b, rtol=1e-10)
    k = fibre.kernel.shape[1]
    rotation = _orthogonal(np.random.default_rng(qseed), k, k) if k else np.zeros((0, 0))
    first = reduced_quadratic(hessian, gradient, fibre.particular, fibre.kernel)
    second = reduced_quadratic(hessian, gradient, u0, fibre.kernel @ rotation)
    np.testing.assert_allclose(first.u_star, second.u_star, atol=1e-7)


def test_p3_counterexample_dropping_particular_solution_gives_wrong_minimiser() -> None:
    hessian, gradient = np.diag([2.0, 6.0]), np.array([0.0, 0.0])
    matrix, b = np.array([[1.0, 1.0]]), np.array([2.0])
    fibre = affine_fibre(matrix, b, rtol=1e-10)
    right = reduced_quadratic(hessian, gradient, fibre.particular, fibre.kernel).u_star
    np.testing.assert_allclose(right, [1.5, 0.5], atol=1e-12)
    wrong_z = -np.linalg.solve(
        fibre.kernel.T @ hessian @ fibre.kernel, fibre.kernel.T @ gradient
    )  # forgets H u_p
    wrong = fibre.particular + fibre.kernel @ wrong_z
    assert float(wrong @ hessian @ wrong) > float(right @ hessian @ right) + 1.0


def test_p3_indefinite_full_hessian_with_positive_reduced_hessian() -> None:
    hessian, gradient = np.diag([1.0, -1.0]), np.array([-1.0, 0.0])
    matrix, b = np.array([[0.0, 1.0]]), np.array([3.0])
    fibre = affine_fibre(matrix, b, rtol=1e-10)
    reduced = reduced_quadratic(hessian, gradient, fibre.particular, fibre.kernel)
    np.testing.assert_allclose(reduced.hessian, [[1.0]])
    np.testing.assert_allclose(reduced.u_star, [1.0, 3.0], atol=1e-12)
    np.testing.assert_allclose(reduced.u_star, kkt_minimiser(hessian, gradient, matrix, b))


def test_p3_non_positive_reduced_hessian_is_rejected() -> None:
    with pytest.raises(ValueError, match="positive definite"):
        reduced_quadratic(np.diag([1.0, -1.0]), np.zeros(2), np.zeros(2), np.array([[0.0], [1.0]]))


# ----------------------------------------------------------------------------------- P4


@PROPERTY
@given(consistent_systems(), SEEDS)
def test_p4_range_of_transpose_functionals_are_invariant(
    system: tuple[Array, Array, Array], seed: int
) -> None:
    matrix, b, u0 = system
    fibre = affine_fibre(matrix, b, rtol=1e-10)
    rng = np.random.default_rng(seed)
    c = matrix.T @ rng.standard_normal(matrix.shape[0])
    report = functional_invariance(fibre.kernel, c, tol=1e-9)
    assert report.invariant
    assert float(c @ u0) == pytest.approx(float(c @ fibre.particular), abs=1e-8)


@PROPERTY
@given(consistent_systems(), SEEDS)
def test_p4_kernel_component_makes_functional_vary(
    system: tuple[Array, Array, Array], seed: int
) -> None:
    matrix, b, _ = system
    fibre = affine_fibre(matrix, b, rtol=1e-10)
    assume(fibre.kernel.shape[1] > 0)
    c = fibre.kernel[:, 0] + matrix.T @ np.random.default_rng(seed).standard_normal(matrix.shape[0])
    report = functional_invariance(fibre.kernel, c, tol=1e-9)
    assert not report.invariant and report.residual > 1e-3
    varied = fibre.particular + fibre.kernel[:, 0]
    assert abs(float(c @ varied) - float(c @ fibre.particular)) > 1e-3


@PROPERTY
@given(consistent_systems(), SEEDS)
def test_p4_invariance_iff_functional_lies_in_row_space(
    system: tuple[Array, Array, Array], seed: int
) -> None:
    matrix, b, _ = system
    fibre = affine_fibre(matrix, b, rtol=1e-10)
    c = np.random.default_rng(seed).standard_normal(matrix.shape[1])
    in_row_space = np.linalg.norm(c - np.linalg.pinv(matrix) @ (matrix @ c)) < 1e-8
    assert functional_invariance(fibre.kernel, c, tol=1e-8).invariant == in_row_space


@PROPERTY
@given(consistent_systems(), SEEDS)
def test_p4_interval_on_box_contains_samples_and_collapses_when_box_is_a_point(
    system: tuple[Array, Array, Array], seed: int
) -> None:
    matrix, b, u0 = system
    fibre = affine_fibre(matrix, b, rtol=1e-10)
    n = matrix.shape[1]
    rng = np.random.default_rng(seed)
    c = rng.standard_normal(n)
    box, margin = np.vstack([np.eye(n), -np.eye(n)]), rng.uniform(0.0, 2.0, size=2 * n)
    bound = np.concatenate([u0 + margin[:n], -(u0 - margin[n:])])
    result = functional_interval(c, fibre.particular, fibre.kernel, box, bound)
    assert result.feasible and result.bounded
    assert result.lower - 1e-7 <= float(c @ u0) <= result.upper + 1e-7
    point = functional_interval(
        c, fibre.particular, fibre.kernel, box, np.concatenate([u0, -u0]), tol=1e-7
    )
    assert point.feasible
    assert point.lower == pytest.approx(float(c @ u0), abs=1e-6)
    assert point.upper == pytest.approx(float(c @ u0), abs=1e-6)


def test_p4_counterexample_marginal_is_an_interval_net_is_a_point() -> None:
    matrix, b = np.array([[1.0, 1.0]]), np.array([1.0])
    fibre = affine_fibre(matrix, b, rtol=1e-10)
    box, bound = np.vstack([np.eye(2), -np.eye(2)]), np.array([1.0, 1.0, 0.0, 0.0])
    split = functional_interval(np.array([1.0, 0.0]), fibre.particular, fibre.kernel, box, bound)
    net = functional_interval(np.array([1.0, 1.0]), fibre.particular, fibre.kernel, box, bound)
    assert split.lower == pytest.approx(0.0) and split.upper == pytest.approx(1.0)
    assert net.lower == pytest.approx(1.0) and net.upper == pytest.approx(1.0)
    assert functional_invariance(fibre.kernel, np.array([1.0, 1.0]), tol=1e-12).invariant
    assert not functional_invariance(fibre.kernel, np.array([1.0, 0.0]), tol=1e-12).invariant


def test_p4_unbounded_infeasible_and_singleton_are_explicit() -> None:
    matrix, b = np.array([[1.0, 1.0]]), np.array([0.0])
    fibre = affine_fibre(matrix, b, rtol=1e-10)
    c = np.array([1.0, 0.0])
    free = functional_interval(c, fibre.particular, fibre.kernel, np.zeros((0, 2)), np.zeros(0))
    assert free.feasible and not free.bounded
    assert free.lower == -math.inf and free.upper == math.inf
    nonneg, zero = -np.eye(2), np.zeros(2)  # u >= 0 and u1 + u2 = 0  ->  only the origin
    single = functional_interval(c, fibre.particular, fibre.kernel, nonneg, zero)
    assert single.feasible and single.lower == pytest.approx(0.0, abs=1e-9)
    assert single.upper == pytest.approx(0.0, abs=1e-9)
    shifted = functional_interval(c, fibre.particular, fibre.kernel, nonneg, zero - 1.0)
    assert not shifted.feasible and math.isnan(shifted.lower) and math.isnan(shifted.upper)


def test_p4_zero_nullity_interval_is_the_particular_value() -> None:
    fibre = affine_fibre(np.eye(2), np.array([1.0, 2.0]), rtol=1e-10)
    inside = functional_interval(
        np.array([1.0, 1.0]), fibre.particular, fibre.kernel, np.eye(2), np.array([5.0, 5.0])
    )
    assert inside.feasible and inside.lower == inside.upper == pytest.approx(3.0)
    outside = functional_interval(
        np.array([1.0, 1.0]), fibre.particular, fibre.kernel, np.eye(2), np.array([0.5, 5.0])
    )
    assert not outside.feasible


def test_p4_invariance_report_states_tolerance_and_is_not_the_exact_theorem() -> None:
    kernel = np.array([[1.0], [-1.0]]) / math.sqrt(2.0)
    nearly = np.array([1.0, 1.0 + 1e-8])
    loose = functional_invariance(kernel, nearly, tol=1e-6)
    tight = functional_invariance(kernel, nearly, tol=1e-12)
    assert loose.invariant and not tight.invariant  # verdict depends on the declared tolerance
    assert loose.tol == 1e-6 and loose.residual == pytest.approx(tight.residual)
    assert "tolerance" in (functional_invariance.__doc__ or "").lower()


# ----------------------------------------------------------------------------------- P5


@PROPERTY
@given(consistent_systems(), SEEDS, SEEDS, st.floats(0.0, 1e4))
def test_p5_leakage_bound_holds_for_large_steps(
    system: tuple[Array, Array, Array], seed: int, zseed: int, radius: float
) -> None:
    matrix, b, _ = system
    n = matrix.shape[1]
    rng = np.random.default_rng(seed)
    k = int(rng.integers(0, n + 1))
    basis = rng.standard_normal((n, k))  # generic, NOT a true null basis
    particular = rng.standard_normal(n)
    z = np.random.default_rng(zseed).standard_normal(k) * radius
    result = leakage_bound(matrix, basis, particular, b, z)
    assert result.actual <= result.bound * (1 + 1e-12) + 1e-9
    assert result.slack >= -1e-9


@PROPERTY
@given(consistent_systems(), SEEDS)
def test_p5_exact_null_basis_has_zero_leakage_growth(
    system: tuple[Array, Array, Array], seed: int
) -> None:
    matrix, b, _ = system
    fibre = affine_fibre(matrix, b, rtol=1e-10)
    z = 1e3 * np.random.default_rng(seed).standard_normal(fibre.kernel.shape[1])
    result = leakage_bound(matrix, fibre.kernel, fibre.particular, b, z)
    assert result.actual == pytest.approx(0.0, abs=1e-6)


def test_p5_counterexample_bound_is_tight_and_leakage_grows_linearly() -> None:
    eps = 1e-3
    matrix, basis = np.array([[eps]]), np.array([[1.0]])
    for step in (1.0, 1e3, 1e6):
        result = leakage_bound(matrix, basis, np.zeros(1), np.zeros(1), np.array([step]))
        assert result.actual == pytest.approx(eps * step)
        assert result.bound == pytest.approx(eps * step)  # equality: the bound cannot be improved
    assert leakage_bound(matrix, basis, np.zeros(1), np.zeros(1), np.array([1e6])).actual > 100.0


# ----------------------------------------------------------------------------------- P7


def _box_frame(lower: float, upper: float, n: int = 2, total: float | None = None) -> ForceFrame:
    box = np.vstack([np.eye(n), -np.eye(n)])
    bound = np.concatenate([np.full(n, upper), np.full(n, -lower)])
    rows = np.ones((1, n)) if total is not None else np.zeros((0, n))
    rhs = np.array([total]) if total is not None else np.zeros(0)
    return ForceFrame(rows, rhs, box, bound)


@PROPERTY
@given(
    st.floats(0.0, 2.0),
    st.floats(0.5, 3.0),
    st.floats(0.0, 2.0),
    st.floats(0.5, 3.0),
    st.floats(0.0, 3.0),
    st.sampled_from([[1.0, 0.0], [0.0, 1.0], [1.0, -1.0]]),
)
def test_p7_coupling_never_widens_envelopes(
    lo1: float, w1: float, lo2: float, w2: float, delta: float, direction: list[float]
) -> None:
    frames = (_box_frame(lo1, lo1 + w1), _box_frame(lo2, lo2 + w2))
    c = np.array(direction)
    try:
        result = framewise_vs_coupled_envelope(frames, c, delta)
    except ValueError:
        assume(False)
    assert result.contained
    for free, tied in zip(result.framewise, result.coupled, strict=True):
        assert free[0] - 1e-6 <= tied[0] <= tied[1] <= free[1] + 1e-6


@PROPERTY
@given(st.floats(0.0, 2.0), st.floats(0.5, 3.0), st.floats(0.0, 2.0), st.floats(0.5, 3.0))
def test_p7_without_coupling_the_envelopes_are_equal(
    lo1: float, w1: float, lo2: float, w2: float
) -> None:
    frames = (_box_frame(lo1, lo1 + w1), _box_frame(lo2, lo2 + w2))
    result = framewise_vs_coupled_envelope(frames, np.array([1.0, 0.0]), math.inf)
    for free, tied in zip(result.framewise, result.coupled, strict=True):
        assert free == pytest.approx(tied, abs=1e-6)


def test_p7_counterexample_rate_bound_strictly_shrinks_both_frames() -> None:
    frames = (_box_frame(0.0, 1.0, n=1), _box_frame(0.5, 2.0, n=1))
    result = framewise_vs_coupled_envelope(frames, np.array([1.0]), 0.2)
    assert result.framewise[0] == pytest.approx((0.0, 1.0))
    assert result.framewise[1] == pytest.approx((0.5, 2.0))
    assert result.coupled[0] == pytest.approx((0.3, 1.0))
    assert result.coupled[1] == pytest.approx((0.5, 1.2))
    assert result.contained


def test_p7_infeasible_coupling_and_bad_delta_are_rejected() -> None:
    far = (_box_frame(0.0, 1.0, n=1), _box_frame(5.0, 6.0, n=1))
    with pytest.raises(ValueError, match="infeasible"):
        framewise_vs_coupled_envelope(far, np.array([1.0]), 0.1)
    with pytest.raises(ValueError, match="delta"):
        framewise_vs_coupled_envelope(far, np.array([1.0]), -0.1)


# --------------------------------------------------------------------------- worked examples


def test_three_muscle_toy_matches_hand_derivation_and_collapses_when_disabled() -> None:
    result = three_muscle_example()
    assert result["nullity"] == 1
    assert result["muscle_3_interval"] == pytest.approx([0.0, 3.0])
    assert result["muscle_1_interval"] == pytest.approx([0.0, 3.0])
    assert result["net_invariant"] is True
    assert result["muscle_3_disabled_interval"] == pytest.approx([0.0, 0.0])
    assert result["muscle_1_disabled_interval"] == pytest.approx([3.0, 3.0])
    for t in (0.0, 1.0, 3.0):  # u = (3 - t, 3 - t, t) solves the declared constraints
        u = np.array([3 - t, 3 - t, t])
        np.testing.assert_allclose(
            np.asarray(result["A"], dtype=float) @ u,
            np.asarray(result["b"], dtype=float),
            atol=1e-12,
        )


def test_grip_toy_net_wrench_invariant_and_lead_trail_split_is_an_interval() -> None:
    result = grip_example()
    assert result["nullity"] == 1
    assert result["net_wrench_invariant"] is True
    assert result["lead_squeeze_interval"] == pytest.approx([-10.0, 10.0])
    assert result["lead_squeeze_invariant"] is False
    assert result["net_wrench"] == pytest.approx([0.0, 40.0, 0.0])


# ------------------------------------------------------------------------- design by contract


@pytest.mark.parametrize(
    ("call", "error"),
    [
        (lambda: affine_fibre([[1.0]], np.ones(1), rtol=1e-10), TypeError),
        (lambda: affine_fibre(np.ones((2, 2)), np.ones(3), rtol=1e-10), ValueError),
        (lambda: affine_fibre(np.array([[np.nan]]), np.ones(1), rtol=1e-10), ValueError),
        (lambda: affine_fibre(np.ones((1, 1)), np.ones(1), rtol=0.0), ValueError),
        (lambda: weighted_representative(np.eye(2), np.ones(2), -np.eye(2)), ValueError),
        (
            lambda: weighted_representative(
                np.ones((1, 2)), np.ones(1), np.array([[1.0, 2.0], [0.0, 1.0]])
            ),
            ValueError,
        ),
        (
            lambda: weighted_representative(
                np.array([[1.0, 1.0], [1.0, 1.0]]), np.array([1.0, 2.0]), np.eye(2)
            ),
            ValueError,
        ),
        (lambda: rescaled_representative(np.eye(2), np.ones(2), np.array([1.0, 0.0])), ValueError),
        (lambda: functional_invariance(np.ones((2, 1)), np.ones(3), tol=1e-9), ValueError),
        (lambda: functional_invariance(np.ones((2, 1)), np.ones(2), tol=-1.0), ValueError),
        (
            lambda: leakage_bound(np.eye(2), np.ones((2, 1)), np.zeros(2), np.zeros(2), np.ones(2)),
            ValueError,
        ),
        (
            lambda: ForceFrame(np.zeros((0, 2)), np.zeros(0), np.zeros((1, 3)), np.zeros(1)),
            ValueError,
        ),
    ],
)
def test_contract_violations_raise_typed_errors(call: object, error: type[Exception]) -> None:
    with pytest.raises(error):
        call()  # type: ignore[operator]


# -------------------------------------------------------------------- JSON registry and file

DATA_FILE = Path(__file__).resolve().parents[1] / "data/null_space_exploration/examples.json"


def _assert_close(saved: object, fresh: object, path: str = "$") -> None:
    if isinstance(saved, dict) and isinstance(fresh, dict):
        assert saved.keys() == fresh.keys(), path
        for key in saved:
            _assert_close(saved[key], fresh[key], f"{path}.{key}")
    elif isinstance(saved, list) and isinstance(fresh, list):
        assert len(saved) == len(fresh), path
        for index, (left, right) in enumerate(zip(saved, fresh, strict=True)):
            _assert_close(left, right, f"{path}[{index}]")
    elif isinstance(saved, float) and isinstance(fresh, float):
        assert saved == pytest.approx(fresh, rel=1e-8, abs=1e-10), path
    else:
        assert saved == fresh, path


def test_generated_json_is_current() -> None:
    saved = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    _assert_close(saved, builder.build_document())


def test_generated_json_is_lf_only_and_rendering_is_deterministic() -> None:
    raw = DATA_FILE.read_bytes()
    assert b"\r" not in raw and raw.endswith(b"}\n")
    assert builder.render_document(builder.build_document()) == builder.render_document(
        builder.build_document()
    )


def _stub_section() -> dict[str, object]:
    return {"value": 1.0}


def test_document_layout_and_section_registry_are_extensible() -> None:
    document = builder.build_document()
    assert set(document) == {"schema_version", "sections"}
    sections = cast(dict[str, object], document["sections"])
    assert "linear" in sections and "linear" in builder.SECTION_BUILDERS
    extended = builder.build_document({**builder.SECTION_BUILDERS, "stub": _stub_section})
    extended_sections = cast(dict[str, object], extended["sections"])
    assert extended_sections["stub"] == {"value": 1.0}
    assert extended_sections["linear"] == sections["linear"]
    assert builder.build_document({"only": _stub_section})["sections"] == {"only": {"value": 1.0}}


def test_linear_section_is_seeded_and_json_clean() -> None:
    first, second = linear_section(), linear_section()
    assert first == second
    assert json.loads(json.dumps(first)) is not None
    assert {"p1", "p2", "p3", "p4", "p5", "p7"} <= set(first)


def test_write_document_uses_lf_even_on_windows(tmp_path: Path) -> None:
    target = tmp_path / "out" / "examples.json"
    builder.write_document(target)
    assert b"\r" not in target.read_bytes()
    assert target.read_bytes() == builder.render_document(builder.build_document()).encode("utf-8")
