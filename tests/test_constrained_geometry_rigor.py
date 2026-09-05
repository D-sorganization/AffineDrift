"""Counterexamples for the constrained-mechanics chapter's repaired identities."""

from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_mass_metric_projection_preserves_tangency_and_is_self_adjoint() -> None:
    mass = np.diag([2.0, 1.0])
    jacobian = np.array([[1.0, 1.0]])
    normal = np.linalg.solve(mass, jacobian.T)
    projector = np.eye(2) - normal @ np.linalg.solve(jacobian @ normal, jacobian)
    assert jacobian @ projector == pytest.approx(np.zeros((1, 2)))
    assert projector @ projector == pytest.approx(projector)
    assert projector.T @ mass == pytest.approx(mass @ projector)
    tangent = np.array([1.0, -1.0])
    assert tangent @ mass @ normal[:, 0] == pytest.approx(0.0)
    assert tangent @ mass @ jacobian[0] != pytest.approx(0.0)


def test_circle_acceleration_requires_normal_offset() -> None:
    position = np.array([1.0, 0.0])
    velocity = np.array([0.0, 2.0])
    jacobian = position.reshape(1, 2)
    curvature = velocity @ velocity
    tangent_only = (np.eye(2) - jacobian.T @ jacobian) @ np.array([3.0, 1.0])
    acceleration = tangent_only - position * curvature
    assert jacobian @ acceleration + curvature == pytest.approx([0.0])
    assert jacobian @ tangent_only + curvature != pytest.approx([0.0])


def test_coriolis_load_obeys_kinetic_energy_identity() -> None:
    angle, first_rate, second_rate = 0.7, 1.3, -2.0
    mass_scale = 3.0
    derivative = -mass_scale * np.sin(angle)
    mass_dot = np.array([[0.0, derivative], [derivative, 0.0]]) * second_rate
    velocity = np.array([first_rate, second_rate])
    load = np.array([derivative * second_rate**2, 0.0])
    assert velocity @ load == pytest.approx(0.5 * velocity @ mass_dot @ velocity)
    assert velocity @ (mass_dot @ velocity) != pytest.approx(velocity @ load)


def test_weighted_input_allocation_is_feasible_and_minimal() -> None:
    actuation = np.array([[1.0, 1.0]])
    weight = np.diag([1.0, 4.0])
    inverse_weight_columns = np.linalg.solve(weight, actuation.T)
    solution = inverse_weight_columns @ np.linalg.solve(
        actuation @ inverse_weight_columns, np.array([1.0])
    )
    assert solution == pytest.approx([0.8, 0.2])
    for amplitude in (-1.0, -0.2, 0.3, 2.0):
        alternative = solution + amplitude * np.array([1.0, -1.0])
        assert actuation @ alternative == pytest.approx([1.0])
        assert alternative @ weight @ alternative > solution @ weight @ solution


def test_force_plate_signs_and_stationary_contact_power() -> None:
    cop = np.array([0.2, -0.1, 0.0])
    force = np.array([10.0, 20.0, 500.0])
    moment = np.cross(cop, force) + np.array([0.0, 0.0, 3.0])
    assert [-moment[1] / force[2], moment[0] / force[2]] == pytest.approx(cop[:2])
    assert force @ np.zeros(3) + moment @ np.zeros(3) == 0.0


def test_paired_chapter_removes_false_mechanical_claims() -> None:
    for relative in (
        "Volume_I/chapters/ch09_parallel_mechanisms_constrained_dynamics.tex",
        "quarto/ch09_parallel_mechanisms_constrained_dynamics.qmd",
    ):
        source = (ROOT / "articles/The_Geometry_of_Motion" / relative).read_text(encoding="utf-8")
        assert "These projectors act on different spaces" in source
        assert "A stationary rigid foot has zero twist" in source
        assert "the total angular momentum\nis conserved" not in source
        assert "This identifiability problem is resolved via" not in source
        assert "the system is \\textbf{redundant}" not in source
