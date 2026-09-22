"""Independent mechanics checks for the superposition reference article."""

from pathlib import Path

import numpy as np
import pytest

GRAVITY_M_S2 = 9.81
LENGTH_M = 0.8
MASSES = np.array([1.4, 0.5])
COM_DISTANCES = np.array([0.3, 0.2])
COM_INERTIAS = np.array([0.06, 0.02])


def test_affine_accelerations_require_one_baseline_subtraction() -> None:
    drift, first, second = 4.0, 2.0, -3.0
    assert drift + first + second == (drift + first) + (drift + second) - drift
    assert drift + first + second != (drift + first) + (drift + second)


def test_body_velocity_transport_recovers_spatial_acceleration() -> None:
    omega = np.array([0.0, 0.0, 2.0])
    body_velocity = np.array([3.0, 0.0, 0.0])
    body_rate = -np.cross(omega, body_velocity)
    assert body_rate + np.cross(omega, body_velocity) == pytest.approx(np.zeros(3))
    assert np.linalg.norm(body_rate) == pytest.approx(6.0)


def test_spatial_inertia_matches_center_of_mass_kinetic_energy() -> None:
    mass = 2.0
    offset = np.array([0.2, -0.1, 0.3])
    x, y, z = offset
    skew = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    center_inertia = np.diag([0.2, 0.3, 0.4])
    origin_inertia = center_inertia + mass * skew.T @ skew
    spatial = np.block([[origin_inertia, mass * skew], [-mass * skew, mass * np.eye(3)]])
    omega = np.array([1.0, -2.0, 0.5])
    velocity = np.array([2.0, 1.0, -1.0])
    twist = np.concatenate([omega, velocity])
    center_velocity = velocity + np.cross(omega, offset)
    assert spatial == pytest.approx(spatial.T)
    assert np.all(np.linalg.eigvalsh(spatial) > 0)
    assert twist @ spatial @ twist == pytest.approx(
        omega @ center_inertia @ omega + mass * center_velocity @ center_velocity
    )


def test_two_link_inertia_includes_both_center_of_mass_terms() -> None:
    # Two uniform unit rods, each with unit mass, at q2 = 0.
    center_inertia, center_distance = 1.0 / 12.0, 0.5
    first = 2 * center_inertia + center_distance**2 + 1 + center_distance**2
    coupling = center_distance
    last = center_inertia + center_distance**2
    mass = np.array([[first + 2 * coupling, last + coupling], [last + coupling, last]])
    expected = np.array([[8.0 / 3.0, 5.0 / 6.0], [5.0 / 6.0, 1.0 / 3.0]])
    assert mass == pytest.approx(expected)
    assert mass[1, 1] > center_inertia


def test_article_does_not_promote_affinity_to_causal_or_neural_identification() -> None:
    source = (Path(__file__).resolve().parents[1] / "articles/superposition.qmd").read_text(
        encoding="utf-8"
    )
    assert "activation dependence must be checked" in source.lower()
    assert "the acceleration increment, not a unique input" in source
    assert "Dominant Attractor" not in source
    assert "to accelerations is linear" not in source
    assert "except in special linear cases" not in source
    assert "m c^\\times \\\\ \nm c^\\times" not in source


def test_feasible_reference_is_translated_and_inputs_are_not_closed_under_addition() -> None:
    controls = np.array([1.0, 1.5, 2.0])
    reference = 1.5
    acceleration = 3 + 2 * controls
    np.testing.assert_allclose(acceleration - (3 + 2 * reference), [-1, 0, 1])
    np.testing.assert_allclose(acceleration[[0, -1]], [5, 7])
    assert reference + reference > controls.max()
    assert 0 < controls.min()  # Formal zero input is outside this physical envelope.


@pytest.mark.parametrize("force", [[0, 0], [10, 0], [-5, 4]])
def test_circular_guide_reaction_and_curvature_from_direct_kkt(force: list[float]) -> None:
    mass = 2 * np.eye(2)
    jacobian = np.array([[1.0, 0.0]])
    velocity = np.array([0.0, 3.0])
    gamma = velocity @ velocity
    kkt = np.block([[mass, -jacobian.T], [jacobian, np.zeros((1, 1))]])
    answer = np.linalg.solve(kkt, np.r_[force, -gamma])
    np.testing.assert_allclose(answer[:2], [-9, force[1] / 2])
    assert answer[2] == pytest.approx(-18 - force[0])
    assert (jacobian @ answer[:2]).item() == pytest.approx(-gamma)
    assert (jacobian @ velocity).item() == 0


def test_constrained_inverse_mass_and_task_differences_match_kkt() -> None:
    rng = np.random.default_rng(4418)
    factor = rng.normal(size=(4, 4))
    mass = factor.T @ factor + np.eye(4)
    jacobian = rng.normal(size=(2, 4))
    input_map = rng.normal(size=(4, 3))
    inverse = np.linalg.solve(mass, np.eye(4))
    schur = jacobian @ inverse @ jacobian.T
    constrained = inverse - inverse @ jacobian.T @ np.linalg.solve(schur, jacobian @ inverse)
    h, gamma = rng.normal(size=4), rng.normal(size=2)
    baseline = -constrained @ h - inverse @ jacobian.T @ np.linalg.solve(schur, gamma)
    kkt = np.block([[mass, -jacobian.T], [jacobian, np.zeros((2, 2))]])
    control, reference = rng.normal(size=(2, 3))
    direct = np.linalg.solve(kkt, np.r_[input_map @ control - h, -gamma])[:4]
    anchor = np.linalg.solve(kkt, np.r_[input_map @ reference - h, -gamma])[:4]
    np.testing.assert_allclose(direct, baseline + constrained @ input_map @ control, atol=1e-12)
    np.testing.assert_allclose(jacobian @ constrained, 0, atol=1e-12)
    np.testing.assert_allclose(constrained @ jacobian.T, 0, atol=1e-12)
    np.testing.assert_allclose(jacobian @ (direct - anchor), 0, atol=1e-12)
    task, bias = rng.normal(size=(2, 4)), rng.normal(size=2)
    np.testing.assert_allclose(
        (task @ direct + bias) - (task @ anchor + bias),
        task @ constrained @ input_map @ (control - reference),
        atol=1e-12,
    )
    assert not np.allclose(constrained @ constrained, constrained)


def _two_link_terms(q: np.ndarray, velocity: np.ndarray) -> tuple[np.ndarray, ...]:
    """Evaluate the article's mass, velocity-product and gravity formulas."""
    masses, centers, inertias = MASSES, COM_DISTANCES, COM_INERTIAS
    length, gravity = LENGTH_M, GRAVITY_M_S2
    angles = np.cumsum(q)
    last = inertias[1] + masses[1] * centers[1] ** 2
    first = inertias[0] + masses[0] * centers[0] ** 2 + masses[1] * length**2 + last
    coupling = masses[1] * length * centers[1]
    mass = np.array(
        [
            [first + 2 * coupling * np.cos(q[1]), last + coupling * np.cos(q[1])],
            [last + coupling * np.cos(q[1]), last],
        ]
    )
    convective = (
        coupling
        * np.sin(q[1])
        * np.array([-2 * velocity[0] * velocity[1] - velocity[1] ** 2, velocity[0] ** 2])
    )
    potential_gradient = gravity * np.array(
        [
            (masses[0] * centers[0] + masses[1] * length) * np.cos(q[0])
            + masses[1] * centers[1] * np.cos(angles[1]),
            masses[1] * centers[1] * np.cos(angles[1]),
        ]
    )
    return mass, convective, potential_gradient


def test_two_link_equations_match_independent_body_moments_and_energy() -> None:
    # Unequal COM offsets and inertias exercise the article's general 2R formulas.
    q, velocity, acceleration = np.array([0.4, -0.7]), np.array([2.1, -0.8]), np.array([1.2, -2.3])
    masses, centers, inertias = MASSES, COM_DISTANCES, COM_INERTIAS
    length, gravity = LENGTH_M, GRAVITY_M_S2
    angles = np.cumsum(q)
    directions = np.column_stack((np.cos(angles), np.sin(angles)))
    normals = np.column_stack((-np.sin(angles), np.cos(angles)))
    center_rates = centers[:, None] * normals * np.cumsum(velocity)[:, None]
    center_rates[1] += length * normals[0] * velocity[0]
    center_acc = centers[:, None] * (
        normals * np.cumsum(acceleration)[:, None] - directions * np.cumsum(velocity)[:, None] ** 2
    )
    center_acc[1] += length * (normals[0] * acceleration[0] - directions[0] * velocity[0] ** 2)
    distal_force = masses[1] * (center_acc[1] - [0, -gravity])
    base_force = masses[0] * (center_acc[0] - [0, -gravity]) + distal_force
    distal_torque = inertias[1] * acceleration.sum() + centers[1] * normals[1] @ distal_force
    base_torque = inertias[0] * acceleration[0] + distal_torque
    base_torque += centers[0] * normals[0] @ base_force
    base_torque += (length - centers[0]) * normals[0] @ distal_force
    mass, convective, potential_gradient = _two_link_terms(q, velocity)
    np.testing.assert_allclose(
        mass @ acceleration + convective + potential_gradient,
        [base_torque, distal_torque],
        atol=1e-12,
    )
    kinetic = (masses @ np.sum(center_rates**2, axis=1) + inertias @ np.cumsum(velocity) ** 2) / 2
    assert velocity @ mass @ velocity / 2 == pytest.approx(kinetic)
    assert velocity @ potential_gradient == pytest.approx(gravity * masses @ center_rates[:, 1])
