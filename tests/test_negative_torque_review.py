"""Manufactured power examples and publication contracts, not human validation."""

import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure

from scripts import make_proximal_distal_companion_figures as figures


@pytest.mark.integration
def test_negative_torque_provider_links_are_revision_bound() -> None:
    text = Path("articles/proximal_distal_companion/chapters/ch13_negative_torque.qmd").read_text(
        encoding="utf-8"
    )
    links = re.findall(r"https://github\.com/D-sorganization/UpstreamDrift/[^)\s]+", text)
    assert links
    assert all("/blob/85cce4d3307bb7ad3953d9fc6e583e370803515c/" in link for link in links)


@pytest.mark.integration
def test_quadrants_specify_power_conjugate_rate(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[Figure] = []
    monkeypatch.setattr(figures, "_save", lambda figure, _stem: captured.append(figure))
    figures.make_sign_quadrants()
    figure = captured[0]
    try:
        axis = figure.axes[0]
        assert "Conjugate" in axis.get_xlabel()
        labels = {tuple(text.get_position()): text.get_text() for text in axis.texts}
        for location in [(0.5, 0.5), (-0.5, -0.5), (-0.5, 0.5), (0.5, -0.5)]:
            expected = "Positive Power" if np.prod(location) > 0 else "Negative Power"
            assert labels[location] == expected
        assert any("Relative Rate" in text for text in labels.values())
    finally:
        plt.close(figure)


def test_negative_moment_can_have_positive_total_club_power() -> None:
    # SI example: H-to-C displacement, absolute club rate and hand wrench.
    radius = np.array([0.0, 1.0, 0.0])
    omega = np.array([0.0, 0.0, 3.0])
    velocity_hand = np.array([2.0, 0.0, 0.0])
    force = np.array([10.0, 0.0, 0.0])
    moment_hand = np.array([0.0, 0.0, -2.0])
    velocity_center = velocity_hand + np.cross(omega, radius)
    moment_center = moment_hand - np.cross(radius, force)
    np.testing.assert_allclose(velocity_center, [-1.0, 0.0, 0.0])
    np.testing.assert_allclose(moment_center, [0.0, 0.0, 8.0])
    assert moment_hand @ omega == pytest.approx(-6.0)
    assert force @ velocity_hand + moment_hand @ omega == pytest.approx(14.0)
    assert force @ velocity_center + moment_center @ omega == pytest.approx(14.0)
    # The sign claim depends on the reference point; total wrench power does not.
    assert moment_center @ omega == pytest.approx(24.0)


def test_random_wrench_transport_preserves_complete_power() -> None:
    radius, omega, velocity, force, moment = np.random.default_rng(4811).normal(size=(5, 32, 3))
    center_velocity = velocity + np.cross(omega, radius)
    center_moment = moment - np.cross(radius, force)
    original_power = np.sum(force * velocity + moment * omega, axis=1)
    transported_power = np.sum(force * center_velocity + center_moment * omega, axis=1)
    np.testing.assert_allclose(original_power, transported_power, atol=1e-12, rtol=1e-12)


def test_joint_power_uses_relative_rate_and_preserves_coordinate_mapping() -> None:
    torque = -2.0  # N m on club; reaction on arm is +2 N m.
    absolute_rates = np.array([5.0, 3.0])  # Arm, club in rad/s.
    relative_rates = np.array([5.0, -2.0])  # Arm, club-minus-arm.
    absolute_forces = np.array([-torque, torque])
    relative_forces = np.array([0.0, torque])
    body_powers = absolute_forces * absolute_rates
    np.testing.assert_allclose(body_powers, [10.0, -6.0])
    assert absolute_forces @ absolute_rates == pytest.approx(4.0)
    assert relative_forces @ relative_rates == pytest.approx(4.0)
    assert (-relative_forces) @ (-relative_rates) == pytest.approx(4.0)


def test_fixed_force_geometry_reversal_and_surviving_free_moment() -> None:
    separation = np.array([0.2, 0.0, 0.0])
    lead_force = np.array([0.0, 10.0, 0.0])
    trail_force = -lead_force
    normal = np.array([0.0, 0.0, 1.0])
    midpoint_moment = np.cross(-separation / 2, lead_force) + np.cross(separation / 2, trail_force)
    assert midpoint_moment @ normal == pytest.approx(-2.0)
    assert np.cross(-separation, trail_force) @ normal == pytest.approx(2.0)
    free_moment = np.array([0.0, 0.0, 1.0])
    np.testing.assert_allclose(np.cross(np.zeros(3), trail_force) + free_moment, free_moment)
    # A proper cyclic axis rotation; rotate the measuring normal with the system.
    rotation = np.array([[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    assert np.linalg.det(rotation) == pytest.approx(1.0)
    rotated = np.cross(rotation @ separation, rotation @ trail_force)
    assert rotated @ (rotation @ normal) == pytest.approx(-2.0)


def test_ideal_contact_zero_net_power_allows_nonzero_internal_transfer() -> None:
    jacobian = np.array([[1.0, -1.0]])
    velocities = np.array([3.0, 3.0])
    multiplier = np.array([2.0])
    contact_forces = jacobian.T @ multiplier
    np.testing.assert_allclose(contact_forces * velocities, [6.0, -6.0])
    assert multiplier @ (jacobian @ velocities) == pytest.approx(0.0)
