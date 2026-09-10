"""Independent controls for the DCR article's scaling and coordinate claims."""

import json
from pathlib import Path

import numpy as np
import pytest
import sympy as sp

ARTICLE = Path(__file__).resolve().parents[1] / "articles/controllability-drift-ratio.qmd"


def test_lagrangian_example_has_potential_velocity_cancellation() -> None:
    """A valid scalar mechanical model need not have monotone drift magnitude."""
    q, velocity, acceleration, torque = sp.symbols("q v a tau", real=True)
    inertia = sp.exp(2 * q)
    kinetic = inertia * velocity**2 / 2
    potential = -inertia / 2
    momentum = sp.diff(kinetic, velocity)
    lhs = sp.diff(momentum, q) * velocity + sp.diff(momentum, velocity) * acceleration
    lhs -= sp.diff(kinetic - potential, q)
    actual = sp.solve(lhs - torque, acceleration)[0]
    assert sp.simplify(actual - (1 - velocity**2 + sp.exp(-2 * q) * torque)) == 0
    drift = [abs(float(actual.subs({q: 0, velocity: v, torque: 0}))) for v in (0, 1, 2, 3)]
    assert drift == [1, 0, 3, 8]


def test_constant_inertia_does_not_create_quadratic_drift() -> None:
    q, velocity, inertia = sp.symbols("q v I", positive=True)
    kinetic = inertia * velocity**2 / 2
    assert sp.diff(sp.diff(kinetic, velocity), q) == 0
    assert sp.diff(kinetic, q) == 0


def test_nonlinear_chart_adds_acceleration_even_when_original_drift_is_zero() -> None:
    q, velocity, control = sp.symbols("q v u", real=True)
    coordinate = q**2
    transformed = sp.diff(coordinate, q, 2) * velocity**2 + sp.diff(coordinate, q) * control
    assert sp.expand(transformed) == 2 * q * control + 2 * velocity**2
    assert transformed.subs({q: 1, velocity: 1, control: 0}) == 2
    assert sp.diff(transformed, control).subs(q, 1) == 2


def test_cartesian_acceleration_keeps_curvature_term() -> None:
    time = sp.symbols("t", real=True)
    position = sp.Matrix([sp.cos(time), sp.sin(time)])
    actual = sp.diff(position, time, 2)
    assert actual.subs(time, 0) == sp.Matrix([-1, 0])
    assert sp.diff(time, time, 2) == 0


def test_force_ratio_requires_transporting_acceleration_metric() -> None:
    mass = np.diag([1.0, 10.0])
    force = np.array([1.0, 1.0])
    input_force = np.array([1.0, 0.0])
    acceleration = np.linalg.solve(mass, force)
    capacity = np.linalg.norm(np.linalg.solve(mass, input_force))
    force_ratio = np.linalg.norm(force) / np.linalg.norm(input_force)
    acceleration_ratio = np.linalg.norm(acceleration) / capacity
    inverse = np.linalg.inv(mass)
    metric = inverse.T @ inverse
    transported = np.sqrt(force @ metric @ force) / np.sqrt(input_force @ metric @ input_force)
    assert force_ratio == pytest.approx(np.sqrt(2))
    assert acceleration_ratio == pytest.approx(np.sqrt(1.01))
    assert transported == pytest.approx(acceleration_ratio)


def test_reported_norm_examples_use_one_common_state_and_capacity() -> None:
    drift = np.array([3.0, 4.0])
    extreme_input = np.array([2.0, 0.0])
    assert np.linalg.norm(drift) / np.linalg.norm(extreme_input) == 2.5
    assert np.linalg.norm(drift, np.inf) / np.linalg.norm(extreme_input, np.inf) == 2
    inertia = np.diag([1.0, 9.0])
    weighted = np.sqrt(drift @ inertia @ drift) / np.sqrt(extreme_input @ inertia @ extreme_input)
    assert weighted == pytest.approx(np.sqrt(153) / 2)


def test_regularizer_changes_the_meaning_of_a_numeric_threshold() -> None:
    drift, capacity, epsilon = 11.0, 1.0, 0.1
    assert drift / (capacity + epsilon) == pytest.approx(10)
    assert drift / capacity == 11
    scale = 1e-6
    assert drift * scale / ((capacity + epsilon) * scale) == pytest.approx(10)
    assert drift * scale / (capacity * scale + epsilon) != pytest.approx(10)


def test_double_integrator_rank_and_horizon_are_not_given_by_dcr() -> None:
    horizon = sp.symbols("T", positive=True)
    generator = sp.Matrix([[0, 1], [0, 0]])
    input_map = sp.Matrix([0, 1])
    assert input_map.rank() == 1
    assert input_map.row_join(generator * input_map).rank() == 2
    gramian = sp.Matrix([[horizon**3 / 3, horizon**2 / 2], [horizon**2 / 2, horizon]])
    assert sp.simplify(gramian.det() - horizon**4 / 12) == 0


def test_nonconvex_instantaneous_inputs_have_convexified_short_time_endpoints() -> None:
    """For x_dot in {-1,1}, switching can produce zero net displacement."""
    horizon = 0.2
    endpoint = -1 * horizon / 2 + 1 * horizon / 2
    assert endpoint == 0
    assert endpoint / horizon not in (-1, 1)


def test_task_event_time_response_matches_an_exact_contact_solution() -> None:
    height, initial_speed, downward_acceleration = 1.0, -1.0, -8.0
    event_speed = -np.sqrt(initial_speed**2 - 2 * downward_acceleration * height)
    assert event_speed == pytest.approx(-np.sqrt(17))
    derivative = height / np.sqrt(initial_speed**2 - 2 * downward_acceleration * height)
    perturbation = 1e-5
    plus = -np.sqrt(initial_speed**2 - 2 * (downward_acceleration + perturbation) * height)
    minus = -np.sqrt(initial_speed**2 - 2 * (downward_acceleration - perturbation) * height)
    assert (plus - minus) / (2 * perturbation) == pytest.approx(derivative, rel=1e-8)


def test_article_publishes_coordinate_regularization_and_evidence_limits() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    assert "100\\times-300\\times" not in text
    assert "dynamic fiber" not in text
    assert "convex" in text
    assert "Hessian" in text
    assert "zero capacity" in text
    assert "No calibrated golf-swing growth factor" in text
    assert "\\dot J" in text


def test_article_does_not_drop_visible_prose_in_raw_tex_or_html() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    assert r"\textbf{" not in text
    assert r"\emph{" not in text
    assert "Critics citing" not in text
    assert "10:48 (Global Phase Portrait)" not in text


def test_readiness_evidence_names_the_actual_route_reviewer() -> None:
    """A new article digest must not inherit an unrelated historical review label."""
    from src.affine_control.research_readiness.fixtures import build_manufactured_library

    root = ARTICLE.parents[1]
    inventory = json.loads((root / "data/trust/claim_audit_inventory.json").read_text("utf-8"))
    route = next(
        item
        for item in inventory["routes"]
        if item["route"] == "/articles/controllability-drift-ratio.html"
    )
    library = build_manufactured_library(root)
    protocol = next(
        item
        for item in library["protocols"]
        if item["protocol_id"] == "ad-protocol-dcr-perturbation-001"
    )
    evidence = next(item for item in protocol["evidence"] if item["kind"] == "evidence-review")
    assert evidence["reviewed_by"] == route["review"]["reviewer"]
    assert evidence["reviewed_on"] == route["review"]["reviewed_on"]
    assert all(event["on"] >= evidence["reviewed_on"] for event in protocol["history"])
    assert protocol["state"] == "simulation-ready"
    assert protocol["promotion_attempts"][0]["outcome"] == "rejected"
