"""Independent benchmarks and contracts for three replacement pedagogical listings."""

import math
import re
from pathlib import Path
from typing import Any

import numpy as np
import pytest

CHAPTERS = (
    Path(__file__).resolve().parents[1] / "articles/The_Geometry_of_Motion/Volume_IV/chapters"
)


@pytest.fixture
def listings() -> dict[str, Any]:
    namespace: dict[str, Any] = {"__name__": "textbook_listing"}
    for name in (
        "ch02_curse_of_dimensionality.tex",
        "ch03_neural_architecture.tex",
        "ch11_neural_to_robot.tex",
    ):
        source = (CHAPTERS / name).read_text(encoding="utf-8")
        blocks = re.findall(r"\\begin\{lstlisting\}[^\n]*\n(.*?)\\end\{lstlisting\}", source, re.S)
        # Repository-owned listings at fixed paths, with no external input.
        # nosemgrep: python.lang.security.audit.exec-detected.exec-detected
        exec("\n".join(blocks), namespace)
    return namespace


# (1) planning_costs


def test_planning_costs_analytic_scaling(listings: dict[str, Any]) -> None:
    func = listings["planning_costs"]
    # Analytic check with n_x=4, n_u=2, horizon=10, grid_points=100
    res = func(n_state=4, n_control=2, horizon=10, grid_points=100)
    # log10_grid = 4 * log10(100) = 8.0
    assert math.isclose(res["log10_grid"], 8.0)
    # value_hessian_entries = 10 * 4^2 = 160
    assert res["value_hessian_entries"] == 160
    # dense_proxy: 10 * (4^3 + 4^2*2 + 4*2^2 + 2^3) = 10 * (64 + 32 + 16 + 8) = 1200
    assert res["dense_proxy"] == 1200

    res_synergy = func(n_state=4, n_control=1, horizon=10, grid_points=100)
    assert res_synergy["value_hessian_entries"] == res["value_hessian_entries"]
    # 10 * (64 + 16 + 4 + 1) = 850 < 1200
    assert res_synergy["dense_proxy"] == 850


@pytest.mark.parametrize(
    "case",
    [
        (0, 2, 100, 10),
        (-1, 2, 100, 10),
        (2, 0, 100, 10),
        (2, 2, 0, 10),
        (2, 2, 100, 1),
        (2.5, 2, 100, 10),
    ],
)
def test_planning_costs_contracts(listings: dict[str, Any], case: tuple[Any, ...]) -> None:
    with pytest.raises((ValueError, TypeError)):
        listings["planning_costs"](*case)


# (2) population_vector


def test_population_vector_analytic_uniform(listings: dict[str, Any]) -> None:
    func = listings["population_vector"]
    angles = np.linspace(0, 2 * np.pi, 8, endpoint=False)
    theta = np.pi / 3
    baseline = 5.0
    gain = 2.5
    # Analytic tuning: rates = baseline + gain * cos(theta - angles)
    rates = baseline + gain * np.cos(theta - angles)
    vec = func(angles, rates, baseline)

    expected = 4.0 * gain * np.array([np.cos(theta), np.sin(theta)])
    np.testing.assert_allclose(vec, expected, atol=1e-12)


def test_population_vector_zero_and_nonuniform_gram(listings: dict[str, Any]) -> None:
    func = listings["population_vector"]
    angles = np.array([0.0, np.pi])
    rates = np.array([3.0, 3.0])
    # Symmetric opposing rates yield exact zero vector (legitimate output)
    np.testing.assert_allclose(func(angles, rates, 1.0), [0.0, 0.0], atol=1e-14)

    # Non-uniform angles [0, 0, pi/2] -> directional matrix P = [[1, 1, 0], [0, 0, 1]]
    # Gram matrix P @ P.T = [[2, 0], [0, 1]]
    nonuniform_angles = np.array([0.0, 0.0, np.pi / 2])
    p_mat = np.column_stack([np.cos(nonuniform_angles), np.sin(nonuniform_angles)]).T
    gram = p_mat @ p_mat.T
    np.testing.assert_allclose(gram, np.diag([2.0, 1.0]), atol=1e-14)

    # Contrast population vector response under rates [1, 1, 1] - baseline 0
    pv = func(nonuniform_angles, np.array([1.0, 1.0, 1.0]), 0.0)
    np.testing.assert_allclose(pv, [2.0, 1.0], atol=1e-14)


@pytest.mark.parametrize(
    ("angles", "rates", "baseline"),
    [
        (np.array([]), np.array([]), 0.0),  # empty
        (np.array([0.0, 1.0]), np.array([1.0]), 0.0),  # mismatched shape
        (np.array([[0.0], [1.0]]), np.array([[1.0], [2.0]]), 0.0),  # 2D
        (np.array([0.0, np.nan]), np.array([1.0, 2.0]), 0.0),  # non-finite angle
        (np.array([0.0, 1.0]), np.array([1.0, -0.1]), 0.0),  # negative rate
        (np.array([0.0, 1.0]), np.array([1.0, 2.0]), -1.0),  # negative baseline
        (np.array([0.0, 1.0]), np.array([1.0, 2.0]), np.array([0.0, 0.0])),  # non-scalar
    ],
)
def test_population_vector_contracts(
    listings: dict[str, Any], angles: Any, rates: Any, baseline: Any
) -> None:
    with pytest.raises((ValueError, TypeError)):
        listings["population_vector"](angles, rates, baseline)


# (3) RhythmicPolicy


def test_rhythmic_policy_analytic_and_subspace(listings: dict[str, Any]) -> None:
    policy_cls = listings["RhythmicPolicy"]
    weights = np.array([[1.0, 0.0], [0.0, 1.0]])  # n=2, k=2
    feedback = np.array([[0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]])  # n=2, 2n=4
    phases = np.array([0.0, np.pi / 2])
    freq = 1.0
    pol = policy_cls(weights=weights, feedback=feedback, phases=phases, frequency_hz=freq)

    # At t=0: sin(phases) = [0, 1] => feedforward = weights @ [0.5, 1.0] = [0.5, 1.0]
    error = np.array([1.0, 2.0, 3.0, 4.0])
    # feedback @ error = [2.0, 3.0]
    # command = [0.5, 1.0] - [2.0, 3.0] = [-1.5, -2.0]
    cmd = pol.command(time=0.0, error=error)
    np.testing.assert_allclose(cmd, [-1.5, -2.0], atol=1e-12)

    # Subspace verification: feedback need not lie in range(weights)
    rank_restricted_weights = np.array([[1.0], [0.0]])  # rank 1 range
    pol_subspace = policy_cls(
        weights=rank_restricted_weights,
        feedback=np.array([[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]]),
        phases=np.array([0.0]),
        frequency_hz=1.0,
    )
    cmd_sub = pol_subspace.command(time=0.0, error=error)
    # y-component is purely from feedback (-3.0), orthogonal to range(weights)
    assert cmd_sub[1] == -3.0


def test_rhythmic_policy_trajectory_rank(listings: dict[str, Any]) -> None:
    policy_cls = listings["RhythmicPolicy"]
    k = 8
    n = 6
    rng = np.random.default_rng(4908)
    pol = policy_cls(
        weights=rng.standard_normal((n, k)),
        feedback=np.zeros((n, 2 * n)),
        phases=rng.uniform(0, 2 * np.pi, size=k),
        frequency_hz=2.0,
    )
    times = np.linspace(0.0, 1.0, 50)
    traj = np.array([pol.command(t, np.zeros(2 * n)) for t in times])  # shape (50, n)

    # Shared frequency centered trajectory has rank <= 2 (spanned by sin(wt) and cos(wt))
    centered = traj - np.mean(traj, axis=0)
    assert np.linalg.matrix_rank(centered, tol=1e-10) <= 2
    # Uncentered trajectory includes constant offset vector, rank <= 3
    assert np.linalg.matrix_rank(traj, tol=1e-10) <= 3


@pytest.mark.parametrize(
    "case",
    [
        (np.ones((2, 2)), np.ones((2, 4)), np.ones(2), -1.0, 0.0, np.zeros(4)),  # negative freq
        (np.ones((2, 2)), np.ones((2, 3)), np.ones(2), 1.0, 0.0, np.zeros(3)),  # feedback != 2n
        (np.ones((2, 2)), np.ones((2, 4)), np.ones(3), 1.0, 0.0, np.zeros(4)),  # phase != k
        (np.ones((2, 2)), np.ones((2, 4)), np.ones(2), 1.0, np.nan, np.zeros(4)),  # non-finite time
        (np.ones((2, 2)), np.ones((2, 4)), np.ones(2), 1.0, 0.0, np.zeros(5)),  # error != 2n
    ],
)
def test_rhythmic_policy_contracts(listings: dict[str, Any], case: tuple[Any, ...]) -> None:
    weights, feedback, phases, freq, time, error = case
    with pytest.raises((ValueError, TypeError)):
        pol = listings["RhythmicPolicy"](weights, feedback, phases, freq)
        pol.command(time=time, error=error)
