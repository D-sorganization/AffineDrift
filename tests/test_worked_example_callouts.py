"""Recompute the numbers in each `.callout-example` worked example from src/.

Issue #4511 adopts a `.callout-example` convention (given data, steps, result)
and requires at least eight worked examples -- one in each theory part, plus
DCR, ZTCF and superposition -- whose numbers are reproducible from src/. Each
test below recomputes one callout's result independently of the qmd source.
"""

from pathlib import Path

import numpy as np
import pytest

from src.affine_control.dynamics import (
    constrained_affine_fields,
    double_pendulum_coriolis,
    double_pendulum_mass_matrix,
    spatial_inertia,
)
from src.affine_control.golf_model import SEGMENTS, GolfModel
from src.affine_control.reachability import constant_additive_drift_interval
from src.tangent_models.examples import SimplePendulum

ARTICLES_DIR = Path(__file__).resolve().parent.parent / "articles"

WORKED_EXAMPLE_PAGES = (
    "theory-part1.qmd",
    "theory-part2.qmd",
    "theory-part3.qmd",
    "theory-part4.qmd",
    "theory-part5.qmd",
    "controllability-drift-ratio.qmd",
    "zero-torque-counterfactual.qmd",
    "superposition.qmd",
)


def test_at_least_eight_worked_example_callouts_are_published():
    pages_with_callout = [
        page
        for page in WORKED_EXAMPLE_PAGES
        if "{.callout-example}" in (ARTICLES_DIR / page).read_text(encoding="utf-8")
    ]
    assert len(pages_with_callout) >= 8


def test_theory_part1_spatial_inertia():
    spatial = spatial_inertia(2.0, np.array([0.3, 0.0, 0.0]), np.diag([0.05, 0.05, 0.01]))
    np.testing.assert_allclose(np.diag(spatial[:3, :3]), [0.05, 0.23, 0.19], atol=1e-9)


def test_theory_part2_pointwise_ztcf_sample():
    q = np.deg2rad(np.array([60.0, -30.0, -20.0]))
    qd = np.array([12.0, -18.0, -25.0])
    result = SEGMENTS.drift_acceleration(q, qd)
    np.testing.assert_allclose(result, [-118.58020078, 70.46844681, 134.82714903], atol=1e-6)


def test_theory_part3_constrained_acceleration_map():
    drift, field = constrained_affine_fields(
        mass_matrix=np.diag([2.0, 1.0]),
        bias=np.array([0.0, 0.0]),
        input_matrix=np.eye(2),
        constraint_jacobian=np.array([[1.0, 1.0]]),
        constraint_bias=np.array([0.0]),
    )
    np.testing.assert_allclose(drift, [0.0, 0.0], atol=1e-12)
    delta_a = field @ np.array([1.0, 0.0])
    np.testing.assert_allclose(delta_a, [1 / 3, -1 / 3], atol=1e-9)


def test_theory_part4_rigid_pendulum():
    pendulum = SimplePendulum(m=1.0, L=1.0, g=9.81)
    state = np.array([0.5, 0.0])
    control = np.array([0.0])
    np.testing.assert_allclose(pendulum.dynamics(state, control), [0.0, -4.70316453], atol=1e-6)
    a_matrix, b_matrix = pendulum.linearize(state, control)
    np.testing.assert_allclose(a_matrix, [[0.0, 1.0], [-8.60908493, 0.0]], atol=1e-6)
    np.testing.assert_allclose(b_matrix, [[0.0], [1.0]], atol=1e-12)


def test_theory_part5_forward_ztcf_trajectory():
    q0 = np.deg2rad(np.array([60.0, -30.0, -20.0]))
    qd0 = np.array([12.0, -18.0, -25.0])
    trajectory = SEGMENTS.ztcf_trajectory(q0, qd0, duration=0.10, steps=400)
    start_speed = trajectory[0][3]
    end_speed = trajectory[-1][3]
    assert start_speed == pytest.approx(35.368172816116925, abs=1e-6)
    assert end_speed == pytest.approx(21.65613999178662, abs=1e-6)
    assert 100.0 * (end_speed / start_speed - 1.0) == pytest.approx(-38.76941253261992, abs=1e-4)


def test_dcr_reachable_width_independent_of_drift():
    zero_drift = constant_additive_drift_interval(0.0, 0.0, 1.0, 1.0)
    high_drift = constant_additive_drift_interval(0.0, 100.0, 1.0, 1.0)
    assert zero_drift == pytest.approx((-1.0, 1.0))
    assert high_drift == pytest.approx((99.0, 101.0))
    zero_width = zero_drift[1] - zero_drift[0]
    high_width = high_drift[1] - high_drift[0]
    assert zero_width == pytest.approx(high_width)
    assert zero_width == pytest.approx(2.0)


def test_ztcf_pointwise_sample_at_rest():
    model = GolfModel()
    zero = np.zeros(3)
    result = model.drift_acceleration(zero, zero)
    np.testing.assert_allclose(result, [-31.40452157, 29.97923538, 1.56914225], atol=1e-6)


def test_superposition_theorem_double_pendulum():
    q = np.array([0.5, -0.3])
    qd = np.array([1.0, 0.5])
    mass_matrix = double_pendulum_mass_matrix(q, 1.0, 1.0, 1.0, 1.0)
    bias = double_pendulum_coriolis(q, qd, 1.0, 1.0, 1.0) @ qd

    def phi(tau: list[float]) -> np.ndarray:
        return np.linalg.solve(mass_matrix, np.asarray(tau, dtype=float) - bias)

    baseline = phi([0.0, 0.0])
    tau1 = phi([2.0, 0.0])
    tau2 = phi([0.0, 1.0])
    combined = phi([2.0, 1.0])
    np.testing.assert_allclose(tau1 + tau2 - baseline, combined, atol=1e-9)
    np.testing.assert_allclose(combined, [0.02240423, 5.40349383], atol=1e-6)
