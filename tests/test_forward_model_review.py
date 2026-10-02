"""Manufactured solver identities and source provenance, not golfer validation."""

from pathlib import Path

import numpy as np
import pytest

PROVIDER_REVISION = "85cce4d3307bb7ad3953d9fc6e583e370803515c"


@pytest.mark.integration
def test_forward_model_provider_links_pin_the_reviewed_revision() -> None:
    """Keep the explanatory claims connected to the inspected provider revision."""
    path = Path("articles/proximal_distal_companion/chapters/ch18_forward_model.qmd")
    source = path.read_text(encoding="utf-8")
    prefix = (
        "https://github.com/D-sorganization/UpstreamDrift/blob/"
        f"{PROVIDER_REVISION}/docs/research/proximal_distal_energy_transfer/"
    )
    for suffix in (
        "chapters/_ch05b_forward_two_hand.qmd",
        "chapters/_ch06_methods.qmd",
        "OPEN_RELEASE_QUALIFICATION.md",
    ):
        assert prefix + suffix in source


def test_mass_metric_projection_has_a_separate_energy_change() -> None:
    """Check a fixed-configuration velocity correction and its kinetic-energy loss."""
    mass = np.diag([2.0, 1.0])  # kg; both coordinates are translations.
    jacobian = np.array([[1.0, 1.0]])
    velocity = np.array([3.0, -1.0])  # m/s; violates stationary Jv = 0.
    inverse_jacobian = np.linalg.solve(mass, jacobian.T)
    schur = jacobian @ inverse_jacobian
    defect = jacobian @ velocity
    projected = velocity - inverse_jacobian @ np.linalg.solve(schur, defect)
    energy_before = 0.5 * velocity @ mass @ velocity
    energy_after = 0.5 * projected @ mass @ projected
    np.testing.assert_allclose(projected, [7 / 3, -7 / 3])
    np.testing.assert_allclose(jacobian @ projected, 0, atol=1e-14)
    assert energy_before == pytest.approx(9.5)
    assert energy_after == pytest.approx(49 / 6)
    assert energy_after - energy_before == pytest.approx(-4 / 3)
    predicted_loss = -0.5 * defect @ np.linalg.solve(schur, defect)
    assert energy_after - energy_before == pytest.approx(predicted_loss)


def test_moving_constraint_can_supply_whole_system_power() -> None:
    """Check two translating masses constrained by q1 - q2 = s(t)."""
    mass = np.diag([2.0, 3.0])  # kg
    jacobian = np.array([[1.0, -1.0]])
    velocity = np.array([2.0, 1.5])  # m/s
    boundary_speed, boundary_acceleration = 0.5, 0.2  # m/s, m/s^2
    kkt = np.block([[mass, -jacobian.T], [jacobian, np.zeros((1, 1))]])
    solution = np.linalg.solve(kkt, [0, 0, boundary_acceleration])
    acceleration, multiplier = solution[:2], solution[2]  # m/s^2, N
    np.testing.assert_allclose(acceleration, [0.12, -0.08])
    assert multiplier == pytest.approx(0.24)
    assert (jacobian @ velocity).item() == pytest.approx(boundary_speed)
    reaction = jacobian.T[:, 0] * multiplier
    assert reaction @ velocity == pytest.approx(0.12)  # W
    assert velocity @ mass @ acceleration == pytest.approx(reaction @ velocity)
    assert not np.isclose((jacobian @ np.zeros(2)).item(), boundary_speed)


def test_constraint_row_scaling_changes_multiplier_not_physical_reaction() -> None:
    """Rescale the same constraint equation without changing its physical model."""
    mass = np.diag([2.0, 3.0])  # kg
    jacobian = np.array([[1.0, -1.0]])
    rhs = np.array([0.0, 0.0, 0.2])  # N, N, m/s^2
    kkt = np.block([[mass, -jacobian.T], [jacobian, np.zeros((1, 1))]])
    original = np.linalg.solve(kkt, rhs)
    scale = 7.0  # Dimensionless row rescaling.
    scaled_jacobian = scale * jacobian
    scaled_kkt = np.block([[mass, -scaled_jacobian.T], [scaled_jacobian, np.zeros((1, 1))]])
    scaled = np.linalg.solve(scaled_kkt, rhs * [1, 1, scale])
    np.testing.assert_allclose(scaled[:2], original[:2])
    assert scaled[2] == pytest.approx(original[2] / scale)
    np.testing.assert_allclose(scaled_jacobian.T * scaled[2], jacobian.T * original[2])


def test_finite_applied_torque_step_has_continuous_velocity_and_balanced_work() -> None:
    """Integrate a manufactured constant-inertia rotor after a finite torque step."""
    inertia, torque, initial_speed = 2.0, 3.0, 0.4  # kg m^2, N m, rad/s
    times = np.array([0.0, 0.1])  # s after the step; no impulsive torque.
    acceleration = torque / inertia
    speed = initial_speed + acceleration * times
    angle_change = initial_speed * times + 0.5 * acceleration * times**2
    energy_change = 0.5 * inertia * (speed**2 - initial_speed**2)
    assert acceleration == pytest.approx(1.5)
    np.testing.assert_allclose(speed, [0.4, 0.55])
    np.testing.assert_allclose(energy_change, torque * angle_change, atol=1e-14)
