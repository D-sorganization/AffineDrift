"""Manufactured counterfactual identities, not provider or human validation."""

from pathlib import Path

import numpy as np
import pytest


def test_finite_nonlinear_removal_is_neither_additive_nor_a_derivative() -> None:
    """Two dimensionless inputs share a quadratic torque law on a fixed rotor."""
    inertia, torque_scale = 2.0, 3.0  # kg m^2, N m
    inputs = np.array([[1.0, 1.0], [0.0, 1.0], [1.0, 0.0], [0.0, 0.0]])
    acceleration = torque_scale * inputs.sum(axis=1) ** 2 / inertia
    np.testing.assert_allclose(acceleration, [6.0, 1.5, 1.5, 0.0])  # rad/s^2
    separate_reductions = acceleration[0] - acceleration[1:3]
    combined_reduction = acceleration[0] - acceleration[3]
    np.testing.assert_allclose(separate_reductions, [4.5, 4.5])
    assert separate_reductions.sum() == pytest.approx(9.0)
    assert combined_reduction == pytest.approx(6.0)
    total_input = 2.0
    derivative = 2 * torque_scale * total_input / inertia
    assert derivative * total_input == pytest.approx(12.0)  # Linearized reduction.
    assert not np.isclose(derivative * total_input, combined_reduction)


def test_coincident_contacts_remove_differential_not_every_moment() -> None:
    """Check reference transport, direct couples and a bounded-force estimate."""
    midpoint = np.array([0.4, 0.0, 0.0])  # m from the chosen origin.
    separation = np.array([0.1, 0.0, 0.0])  # m
    forces = np.array([[0.0, 30.0, 0.0], [0.0, 10.0, 0.0]])  # N
    points = midpoint + np.array([0.5, -0.5])[:, None] * separation
    moment = np.cross(points, forces).sum(axis=0)
    differential = np.cross(separation / 2, forces[0] - forces[1])
    offset = np.cross(midpoint, forces.sum(axis=0))
    np.testing.assert_allclose(differential, [0.0, 0.0, 1.0])  # N m
    np.testing.assert_allclose(offset, [0.0, 0.0, 16.0])
    np.testing.assert_allclose(moment, differential + offset)
    np.testing.assert_allclose(moment, [0.0, 0.0, 17.0])
    bound = 0.5 * np.linalg.norm(separation) * np.linalg.norm(forces, axis=1).sum()
    assert bound == pytest.approx(2.0)
    assert np.linalg.norm(differential) <= bound
    coincident = np.cross(np.broadcast_to(midpoint, forces.shape), forces).sum(axis=0)
    np.testing.assert_allclose(coincident, offset)
    np.testing.assert_allclose(coincident + [0.0, 0.0, 2.0], [0.0, 0.0, 18.0])
    reversed_points = midpoint - (points - midpoint)
    reversed_moment = np.cross(reversed_points, forces).sum(axis=0)
    np.testing.assert_allclose(reversed_moment, offset - differential)


def test_component_sign_can_flip_while_physical_projection_is_invariant() -> None:
    """Passive proper-axis rotation preserves a consistently mapped scalar."""
    rotation = np.diag([1.0, -1.0, -1.0])
    moment = np.array([0.0, 0.0, 1.0])  # N m
    normal = np.array([0.0, 0.0, 1.0])  # Declared physical unit normal.
    omega = np.array([0.0, 0.0, 3.0])  # rad/s
    np.testing.assert_allclose(rotation.T @ rotation, np.eye(3))
    assert np.linalg.det(rotation) == pytest.approx(1.0)
    assert (rotation @ moment)[2] == pytest.approx(-1.0)
    assert (rotation @ normal) @ (rotation @ moment) == pytest.approx(normal @ moment)
    assert normal @ moment == pytest.approx(1.0)
    assert (rotation @ moment) @ (rotation @ omega) == pytest.approx(3.0)  # W


@pytest.mark.integration
def test_counterfactual_provider_links_pin_the_reviewed_revision() -> None:
    """Connect the three explanatory provider claims to the reviewed Git blobs."""
    source = Path(
        "articles/proximal_distal_companion/chapters/ch11_counterfactual_scissors.qmd"
    ).read_text(encoding="utf-8")
    prefix = (
        "https://github.com/D-sorganization/UpstreamDrift/blob/"
        "85cce4d3307bb7ad3953d9fc6e583e370803515c/"
        "docs/research/proximal_distal_energy_transfer/chapters/"
    )
    for name in (
        "_ch04_counterfactual_ensemble.qmd",
        "_ch06cc_spatial_forward_contact.qmd",
        "_ch06e_experimental_protocol.qmd",
    ):
        assert prefix + name in source
