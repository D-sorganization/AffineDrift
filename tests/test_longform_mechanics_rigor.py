"""Counterexamples and publication contracts for technical-review issue #4148."""

from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.content_lint
@pytest.mark.parametrize(
    "false_statement",
    (
        "mass matrix is augmented by neuromuscular stiffness",
        "constraint torques** that reside in the null space of the actuation map",
        "calcium dynamics are fast enough to be quasi-static",
        "only by computing ZVCF can we isolate each category with precision",
        "all rigid–flexible coupling remains in the drift term",
        "M(q,\\eta)\\,\\ddot{v}",
    ),
)
def test_foundational_editions_remove_identified_false_statements(false_statement: str) -> None:
    """A correction must reach the long monograph and maintained series editions."""
    sources = [ROOT / "articles" / f"theory-part{i}.qmd" for i in range(1, 6)]
    sources += [
        ROOT / "articles/affine-nature-golf-swing.qmd",
        ROOT / "articles/drifter-manifesto.qmd",
    ]
    for source in sources:
        assert false_statement not in source.read_text(encoding="utf-8"), source.name


def test_zero_input_inverse_dynamics_is_zero_despite_nonzero_bias_load() -> None:
    """Coupled modal inertia must be included; a rigid diagonal block is insufficient."""
    mass = np.array([[3.0, 0.7], [0.7, 1.2]])
    bias = np.array([4.0, -2.0])
    drift = np.linalg.solve(mass, -bias)
    np.testing.assert_allclose(mass @ drift + bias, 0.0, atol=1e-14)
    assert not np.isclose(mass[0, 0] * drift[0], -bias[0])
    applied = np.array([1.5, 0.0])
    actual = np.linalg.solve(mass, applied - bias)
    np.testing.assert_allclose(mass @ (actual - drift), applied, atol=1e-14)


def test_constraint_reaction_is_workless_but_need_not_be_unactuated() -> None:
    """A fully actuated constrained example disproves the actuation-nullspace claim."""
    mass = np.diag([2.0, 3.0])
    jacobian = np.array([[1.0, 1.0]])
    actuation = np.eye(2)
    velocity = np.array([1.0, -1.0])
    mobility = np.linalg.inv(mass)
    reaction = jacobian.T[:, 0] * 4.0
    assert reaction @ velocity == pytest.approx(0.0)
    assert np.linalg.norm(actuation.T @ reaction) > 0
    constrained = mobility - mobility @ jacobian.T @ np.linalg.solve(
        jacobian @ mobility @ jacobian.T, jacobian @ mobility
    )
    np.testing.assert_allclose(jacobian @ constrained, 0, atol=1e-14)


def test_stiffness_changes_response_without_changing_instantaneous_input_gain() -> None:
    """The scalar mass-spring example distinguishes inertia from dynamic stiffness."""
    mass, force, time = 2.0, 1.0, 0.1
    stiffnesses = np.array([20.0, 200.0])
    omega = np.sqrt(stiffnesses / mass)
    response = force / stiffnesses * (1 - np.cos(omega * time))
    assert response[0] != pytest.approx(response[1])
    initial_accelerations = force / stiffnesses * omega**2
    np.testing.assert_allclose(initial_accelerations, force / mass)


def test_point_mass_pendulum_cannot_use_full_spatial_inertia_inverse() -> None:
    """A spherical pendulum has no axial inertia in the ideal point-mass limit."""
    position = np.array([0.0, 0.0, -1.2])
    inertia = 0.2 * (position @ position * np.eye(3) - np.outer(position, position))
    assert np.linalg.matrix_rank(inertia) == 2
    assert np.linalg.det(inertia) == 0


def test_wrench_translation_preserves_power_with_matching_point_velocity() -> None:
    """The force moment changes sign when moving the reporting point."""
    force = np.array([0.0, 4.0, 0.0])
    moment_at_origin = np.array([0.0, 0.0, 2.0])
    displacement = np.array([0.5, 0.0, 0.0])
    angular_velocity = np.array([0.0, 0.0, 3.0])
    origin_velocity = np.array([1.0, 2.0, 0.0])
    moment_at_point = moment_at_origin - np.cross(displacement, force)
    point_velocity = origin_velocity + np.cross(angular_velocity, displacement)
    assert moment_at_point[2] == pytest.approx(0.0)
    assert force @ origin_velocity + moment_at_origin @ angular_velocity == pytest.approx(
        force @ point_velocity + moment_at_point @ angular_velocity
    )


@pytest.mark.content_lint
def test_inverse_inference_does_not_subtract_bias_twice_or_claim_to_measure_effort() -> None:
    """A model-perfect ID load is already the declared generalized input."""
    source = (ROOT / "articles/inverse-dynamics-inference.qmd").read_text(encoding="utf-8")
    assert r"Bu = \tau_{\mathrm{ID}} - \tau_{\mathrm{drift}}" not in source
    assert "To measure just your muscular effort" not in source
