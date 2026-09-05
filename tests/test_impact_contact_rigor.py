"""Independent momentum, contact, and reference-frame checks for impact articles."""

from math import atan, atan2, atanh, degrees, pi, sin, sqrt, tanh
from pathlib import Path

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

ARTICLES = Path(__file__).resolve().parents[1] / "articles"
BALL_MASS_KG = 0.04593
BALL_RADIUS_M = 0.021335
INERTIA_RATIO = 0.4


def skew(vector: np.ndarray) -> np.ndarray:
    """Return the cross-product operator in one world frame."""
    x, y, z = vector
    return np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])


def contact_matrix(
    head_lever: np.ndarray, head_inertia: np.ndarray, head_mass: float = 0.2
) -> np.ndarray:
    ball_lever = np.array([-BALL_RADIUS_M, 0.0, 0.0])
    ball_inertia = INERTIA_RATIO * BALL_MASS_KG * BALL_RADIUS_M**2
    return (
        (1 / BALL_MASS_KG + 1 / head_mass) * np.eye(3)
        - skew(ball_lever) @ skew(ball_lever) / ball_inertia
        - skew(head_lever) @ np.linalg.solve(head_inertia, skew(head_lever))
    )


def test_contact_matrix_matches_four_independent_momentum_updates() -> None:
    lever = np.array([0.04, 0.012, -0.018])
    inertia = np.diag([0.0003, 0.0004, 0.0005])
    impulse = np.array([2.8, -0.04, 0.08])
    ball_lever = np.array([-BALL_RADIUS_M, 0.0, 0.0])
    ball_inertia = INERTIA_RATIO * BALL_MASS_KG * BALL_RADIUS_M**2
    ball_velocity = impulse / BALL_MASS_KG
    ball_spin = np.cross(ball_lever, impulse) / ball_inertia
    head_velocity = -impulse / 0.2
    head_spin = np.linalg.solve(inertia, -np.cross(lever, impulse))
    relative_change = (
        ball_velocity + np.cross(ball_spin, ball_lever) - head_velocity - np.cross(head_spin, lever)
    )
    matrix = contact_matrix(lever, inertia)
    assert matrix @ impulse == pytest.approx(relative_change)
    assert matrix == pytest.approx(matrix.T)
    assert np.linalg.eigvalsh(matrix).min() > 0


def test_impulse_energy_identity_matches_full_body_kinetic_energy() -> None:
    lever = np.array([0.04, 0.012, -0.018])
    inertia = np.diag([0.0003, 0.0004, 0.0005])
    ball_lever = np.array([-BALL_RADIUS_M, 0.0, 0.0])
    ball_inertia = INERTIA_RATIO * BALL_MASS_KG * BALL_RADIUS_M**2
    head_velocity = np.array([48.0, 1.0, -2.0])
    head_spin = np.array([3.0, 30.0, -10.0])
    relative = -head_velocity - np.cross(head_spin, lever)
    matrix = contact_matrix(lever, inertia)
    restitution = 0.8
    impulse = np.linalg.solve(matrix, -(1 + restitution) * relative)
    new_head_velocity = head_velocity - impulse / 0.2
    new_head_spin = head_spin - np.linalg.solve(inertia, np.cross(lever, impulse))
    new_ball_spin = np.cross(ball_lever, impulse) / ball_inertia
    before = 0.1 * head_velocity @ head_velocity + 0.5 * head_spin @ inertia @ head_spin
    after = (
        0.1 * new_head_velocity @ new_head_velocity
        + 0.5 * new_head_spin @ inertia @ new_head_spin
        + 0.5 * impulse @ impulse / BALL_MASS_KG
        + 0.5 * ball_inertia * new_ball_spin @ new_ball_spin
    )
    identity = relative @ impulse + 0.5 * impulse @ matrix @ impulse
    assert after - before == pytest.approx(identity)
    assert identity == pytest.approx(
        -0.5 * (1 - restitution**2) * relative @ np.linalg.solve(matrix, relative)
    )
    assert identity < 0


def test_normal_restitution_is_coupled_to_tangential_impulse_off_center() -> None:
    matrix = contact_matrix(np.array([0.04, 0.0, 0.02]), np.eye(3) * 0.0004)
    relative = np.array([-48.0, 0.0, -2.0])
    target = -np.diag([0.8, 0.0, 0.0]) @ relative
    impulse = np.linalg.solve(matrix, target - relative)
    scalar_normal = -(1 + 0.8) * relative[0] / matrix[0, 0]
    assert impulse[0] != pytest.approx(scalar_normal, rel=1e-5)
    assert relative + matrix @ impulse == pytest.approx(target)
    assert matrix[0, 2] != 0


def test_centered_normal_impact_recovers_mass_ratio_formula() -> None:
    matrix = contact_matrix(np.array([0.04, 0.0, 0.0]), np.eye(3) * 0.0004)
    speed, restitution, head_mass = 48.0, 0.8, 0.2
    impulse = (1 + restitution) * speed / matrix[0, 0]
    assert impulse / BALL_MASS_KG == pytest.approx(
        (1 + restitution) * head_mass / (head_mass + BALL_MASS_KG) * speed
    )


def test_a_reference_change_leaves_contact_velocity_and_impulse_invariant() -> None:
    head_velocity = np.array([48.0, 1.0, -2.0])
    head_spin = np.array([3.0, 30.0, -10.0])
    lever = np.array([0.04, 0.012, -0.018])
    offset = np.array([0.01, -0.02, 0.03])
    shifted_velocity = head_velocity + np.cross(head_spin, offset)
    direct = head_velocity + np.cross(head_spin, lever)
    shifted = shifted_velocity + np.cross(head_spin, lever - offset)
    assert direct == pytest.approx(shifted)
    matrix = contact_matrix(lever, np.eye(3) * 0.0004)
    assert np.linalg.solve(matrix, direct) == pytest.approx(np.linalg.solve(matrix, shifted))


def test_fixed_contact_velocity_rotation_comparison_has_no_extra_spin_term() -> None:
    lever = np.array([0.04, 0.0, 0.0])
    contact_velocity = np.array([48.0, 0.0, -1.0])
    matrix = contact_matrix(lever, np.eye(3) * 0.0004)
    impulses = []
    for head_spin in [np.zeros(3), np.array([0.0, 30.0, 0.0])]:
        center_velocity = contact_velocity - np.cross(head_spin, lever)
        relative = -center_velocity - np.cross(head_spin, lever)
        impulses.append(np.linalg.solve(matrix, -(np.eye(3) + np.diag([0.8, 0, 0])) @ relative))
    assert impulses[0] == pytest.approx(impulses[1])


def test_fixed_center_velocity_uses_head_depth_and_inertia() -> None:
    omega = 30.0
    spins = []
    for depth, inertia_scalar in [(0.02, 0.0004), (0.04, 0.0004), (0.04, 0.0008)]:
        matrix = contact_matrix(np.array([depth, 0.0, 0.0]), np.eye(3) * inertia_scalar)
        impulse_magnitude = depth * omega / matrix[2, 2]
        spin_magnitude = impulse_magnitude / (INERTIA_RATIO * BALL_MASS_KG * BALL_RADIUS_M)
        expected = (
            depth
            * omega
            / (
                INERTIA_RATIO
                * BALL_RADIUS_M
                * (
                    1
                    + 1 / INERTIA_RATIO
                    + BALL_MASS_KG / 0.2
                    + BALL_MASS_KG * depth**2 / inertia_scalar
                )
            )
        )
        assert spin_magnitude == pytest.approx(expected)
        spins.append(spin_magnitude)
    assert spins[0] < spins[1] < spins[2]


def test_five_sevenths_is_a_prescribed_surface_velocity_special_case() -> None:
    imposed_sweep, head_rate = 0.8, 30.0
    ball_spin = imposed_sweep / ((1 + INERTIA_RATIO) * BALL_RADIUS_M)
    assert ball_spin != pytest.approx(5 * head_rate / 7)
    special_sweep = BALL_RADIUS_M * head_rate
    assert special_sweep / ((1 + INERTIA_RATIO) * BALL_RADIUS_M) == pytest.approx(5 * head_rate / 7)
    assert 1.1 * ball_spin > ball_spin  # Positive tangential restitution exceeds zero slip.


def test_nonzero_friction_during_full_sliding_generates_spin() -> None:
    friction, normal_impulse = 0.1, 2.0
    tangential_impulse = friction * normal_impulse
    spin = tangential_impulse / (INERTIA_RATIO * BALL_MASS_KG * BALL_RADIUS_M)
    assert spin > 0


def test_shared_friction_cone_cannot_be_checked_one_component_at_a_time() -> None:
    friction, normal_impulse = 0.4, 3.0
    tangent = np.array([1.19, 0.2])
    assert np.all(np.abs(tangent) < friction * normal_impulse)
    assert np.linalg.norm(tangent) > friction * normal_impulse


def test_sliding_threshold_uses_complementary_angle_conventions() -> None:
    restitution = 0.9
    thresholds = [
        degrees(atan(1 / (mu * (1 + restitution) * (1 + 1 / INERTIA_RATIO)))) for mu in [0.18, 0.4]
    ]
    assert thresholds[0] == pytest.approx(39.8764, abs=0.01)
    assert thresholds[1] < thresholds[0]  # Angle measured from the surface.
    assert 90 - thresholds[1] > 90 - thresholds[0]  # Spin loft from its normal.


def test_face_azimuth_rate_is_not_total_angular_speed() -> None:
    normal = np.array([sqrt(0.5), sqrt(0.5), 0.0])
    omega = np.array([2.0, 3.0, 4.0])
    derivative = np.cross(omega, normal)
    rate = (normal[0] * derivative[2] - normal[2] * derivative[0]) / (
        normal[0] ** 2 + normal[2] ** 2
    )
    step = 1e-6
    rotated = Rotation.from_rotvec(step * omega).apply(normal)
    numerical = (atan2(rotated[2], rotated[0]) - atan2(normal[2], normal[0])) / step
    assert rate == pytest.approx(numerical, abs=1e-5)
    assert rate != pytest.approx(np.linalg.norm(omega))


def test_screw_radius_excludes_velocity_parallel_to_axis() -> None:
    angular_speed, radius, axial_speed = 20.0, 0.7, 8.0
    speed = sqrt((angular_speed * radius) ** 2 + axial_speed**2)
    assert speed / angular_speed > radius
    assert sqrt(speed**2 - axial_speed**2) / angular_speed == pytest.approx(radius)


def test_transverse_reference_shift_changes_speed_by_point_zero_three_mph() -> None:
    velocity = 120 * 0.44704
    transverse = 0.035 * 2000 * pi / 180
    increment_mph = (sqrt(velocity**2 + transverse**2) - velocity) / 0.44704
    assert increment_mph == pytest.approx(0.0311168, abs=1e-5)
    assert degrees(atan(transverse / velocity)) == pytest.approx(1.30475, abs=0.001)


def test_published_coupled_example_reverses_the_isolated_slip_prediction() -> None:
    lever = np.array([0.04, 0.0, 0.02])
    matrix = contact_matrix(lever, np.eye(3) * 0.0004)
    incoming = -np.array([48.0, 0.0, 0.0]) - np.cross([0.0, 30.0, 0.0], lever)
    impulse = np.linalg.solve(matrix, -(np.eye(3) + np.diag([0.8, 0, 0])) @ incoming)
    assert impulse == pytest.approx([3.15422316, 0, 0.05995624], abs=1e-8)
    assert impulse / BALL_MASS_KG == pytest.approx([68.67457351, 0, 1.30538291], abs=1e-8)
    ball_spin = np.cross([-BALL_RADIUS_M, 0, 0], impulse) / (
        INERTIA_RATIO * BALL_MASS_KG * BALL_RADIUS_M**2
    )
    assert ball_spin == pytest.approx([0, 152.96260968, 0], abs=1e-8)
    assert incoming @ impulse + 0.5 * impulse @ matrix @ impulse == pytest.approx(-15.2935508211)
    assert incoming[2] > 0 and impulse[2] > 0
    assert np.linalg.norm(impulse[1:]) / impulse[0] < 0.1


def test_directional_restitution_bounds_do_not_guarantee_coupled_passivity() -> None:
    matrix = np.array([[1.0, 0.9], [0.9, 1.0]])
    restitution = np.diag([1.0, 0.0])
    incoming = np.array([-1.0, -1.0])
    impulse = np.linalg.solve(matrix, -(np.eye(2) + restitution) @ incoming)
    assert impulse[0] > 0
    assert abs(impulse[1]) < impulse[0]  # Even an integrated mu=1 cone passes.
    assert incoming + matrix @ impulse == pytest.approx([1.0, 0.0])
    energy = incoming @ impulse + 0.5 * impulse @ matrix @ impulse
    assert energy == pytest.approx(40 / 19)
    assert energy > 0


def test_fisher_interval_does_not_establish_correlation_equivalence() -> None:
    interval = [tanh(atanh(-0.14) + sign * 1.96 / sqrt(70 - 3)) for sign in [-1, 1]]
    assert interval == pytest.approx([-0.3630354224, 0.0982089533])


def test_contact_event_correction_matches_a_perturbed_straight_trajectory() -> None:
    initial = np.array([0.0, 0.05, 2.0, 0.1])
    perturbation = np.array([0.02, -0.03, 0.04, 0.01])
    duration = (1 - initial[0]) / initial[2]
    fixed_time_change = perturbation[:2] + duration * perturbation[2:]
    event_time_change = -fixed_time_change[0] / initial[2]
    contact_change = fixed_time_change + initial[2:] * event_time_change

    def contact(state: np.ndarray) -> np.ndarray:
        time = (1 - state[0]) / state[2]
        return state[:2] + time * state[2:]

    step = 1e-5
    numerical = (
        contact(initial + step * perturbation) - contact(initial - step * perturbation)
    ) / (2 * step)
    assert contact_change == pytest.approx(numerical, abs=1e-10)
    assert contact_change[0] == pytest.approx(0.0)


def test_sliding_spin_normalized_by_total_speed_uses_sine() -> None:
    speed, angle, friction, restitution = 10.0, pi / 6, 0.18, 0.9
    normal_impulse = BALL_MASS_KG * (1 + restitution) * speed * sin(angle)
    spin = friction * normal_impulse / (INERTIA_RATIO * BALL_MASS_KG * BALL_RADIUS_M)
    assert BALL_RADIUS_M * spin / speed == pytest.approx(
        friction * (1 + restitution) * sin(angle) / INERTIA_RATIO
    )


@pytest.mark.parametrize("name", ["rotation-induced-spin", "reference-point-problem"])
def test_companions_state_what_is_held_fixed(name: str) -> None:
    source = (ARTICLES / f"{name}.qmd").read_text(encoding="utf-8")
    assert "held fixed" in source
    assert "tour-median" not in source.lower()


def test_rotation_companion_removes_universal_rotation_spin_prediction() -> None:
    source = (ARTICLES / "rotation-induced-spin.qmd").read_text(encoding="utf-8")
    assert "finite head" in source.lower()
    assert "MOI cancels entirely" not in source
    assert "What Would Distinguish the Models" in source


def test_reference_companion_separates_geometry_and_accuracy_evidence() -> None:
    source = (ARTICLES / "reference-point-problem.qmd").read_text(encoding="utf-8")
    assert "Bias, Variability, and Adaptation" in source
    assert "axial velocity" in source
    assert "neither is a fit to the other" not in source


def test_main_reference_defines_coupled_contact_and_evidence_limits() -> None:
    source = (ARTICLES / "impact-mechanics-and-ball-flight.qmd").read_text(encoding="utf-8")
    assert "One Coupled Impulse" in source
    assert "Contact-Point Effective Inverse Mass" in source
    assert "season" in source
    assert "95% confidence intervals" in source
