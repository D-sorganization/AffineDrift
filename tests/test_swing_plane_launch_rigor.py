"""Independent geometric, impact and optimization checks for Physics chapter 31."""

import re
from pathlib import Path

import numpy as np
import pytest
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
GRAVITY = 9.80665


def test_both_editions_preserve_all_display_equations() -> None:
    """A delimiter surviving as a paragraph is a missing equation, not valid math."""
    book = ROOT / "articles/The_Physics_of_Golf"
    tex = (book / "chapters/ch31_swing_plane_launch.tex").read_text(encoding="utf-8")
    web = (book / "quarto/ch31_swing_plane_launch.qmd").read_text(encoding="utf-8")
    print_math = re.findall(r"\\\[(.*?)\\\]|\\begin\{equation\}(.*?)\\end\{equation\}", tex, re.S)
    web_math = re.findall(r"(?m)^ *\$\$ *\n(.*?)\n *\$\$", web, re.S)
    expected = [re.sub(r"\\label\{[^}]+\}", "", a or b) for a, b in print_math]
    assert len(web_math) == len(expected)
    for actual, equation in zip(web_math, expected, strict=True):
        assert actual.splitlines()[0].strip()
        assert actual.splitlines()[-1].strip()
        assert not re.search(r"\n\s*\n", actual)
        assert " ".join(actual.split()) == " ".join(equation.split())


@pytest.mark.parametrize(
    "suffix", ["chapters/ch31_swing_plane_launch.tex", "quarto/ch31_swing_plane_launch.qmd"]
)
def test_publication_replaces_dimensionally_invalid_attack_and_optimum_claims(suffix: str) -> None:
    source = (ROOT / "articles/The_Physics_of_Golf" / suffix).read_text(encoding="utf-8")
    assert "component of acceleration in vertical direction" not in source
    assert "near the optimal launch angle, it is maximal" not in source
    assert "smooth interior optimum" in source


def test_velocity_and_vertical_span_a_vertical_plane() -> None:
    velocity = np.array([40.0, 2.0, -3.0])
    vertical = np.array([0.0, 0.0, 1.0])
    normal = np.cross(velocity, vertical)
    assert np.dot(normal, vertical) == 0.0
    assert np.dot(normal, velocity) == 0.0


@pytest.mark.parametrize("phase", [-20.0, -5.0, 0.0, 15.0])
def test_inclined_plane_attack_and_path_identity(phase: float) -> None:
    heading, tilt, phase_radians = np.radians([12.0, 60.0, phase])
    base = np.array([np.cos(heading), np.sin(heading), 0.0])
    uphill = np.array(
        [-np.sin(heading) * np.cos(tilt), np.cos(heading) * np.cos(tilt), np.sin(tilt)]
    )
    tangent = np.cos(phase_radians) * base + np.sin(phase_radians) * uphill
    attack = np.arctan2(tangent[2], np.linalg.norm(tangent[:2]))
    path = np.arctan2(tangent[1], tangent[0])
    assert np.linalg.norm(tangent) == pytest.approx(1.0)
    assert np.dot(tangent, np.cross(base, uphill)) == pytest.approx(0.0, abs=1e-15)
    assert np.tan(attack) == pytest.approx(np.tan(tilt) * np.sin(path - heading), abs=1e-15)


def test_sixty_degree_plane_five_degree_descent_has_nonzero_path_offset() -> None:
    offset = np.degrees(np.arcsin(np.tan(np.radians(-5.0)) / np.tan(np.radians(60.0))))
    assert offset == pytest.approx(-2.8953, abs=5e-5)


@pytest.mark.parametrize("axis", np.eye(3))
def test_face_azimuth_sensitivity_matches_finite_rotation(axis: np.ndarray) -> None:
    loft, face = np.radians([15.0, 20.0])
    normal = np.array([np.cos(loft) * np.cos(face), np.cos(loft) * np.sin(face), np.sin(loft)])
    step = 1e-6
    plus = Rotation.from_rotvec(step * axis).apply(normal)
    minus = Rotation.from_rotvec(-step * axis).apply(normal)
    numerical = (np.arctan2(plus[1], plus[0]) - np.arctan2(minus[1], minus[0])) / (2 * step)
    analytic = axis[2] - np.tan(loft) * (axis[0] * np.cos(face) + axis[1] * np.sin(face))
    assert numerical == pytest.approx(analytic, abs=1e-9)


def test_finite_rotations_do_not_add_as_scalar_face_angles() -> None:
    normal = np.array([1.0, 0.0, 0.0])
    rx = Rotation.from_euler("x", 90.0, degrees=True)
    ry = Rotation.from_euler("y", 90.0, degrees=True)
    assert (rx * ry).apply(normal) == pytest.approx([0.0, 1.0, 0.0], abs=1e-15)
    assert (ry * rx).apply(normal) == pytest.approx([0.0, 0.0, -1.0], abs=1e-15)


def test_weighted_direction_needs_normalization() -> None:
    normal = np.array([np.cos(np.pi / 6), 0.0, np.sin(np.pi / 6)])
    path = np.array([1.0, 0.0, 0.0])
    weighted = 0.76 * normal + 0.24 * path
    assert np.linalg.norm(weighted) < 1.0
    assert np.linalg.norm(weighted / np.linalg.norm(weighted)) == pytest.approx(1.0)


def test_tangential_impulse_sets_spin_magnitude_and_lift_sign() -> None:
    mass, radius = 0.04593, 0.02135
    inertia = 0.4 * mass * radius**2  # Declared homogeneous-sphere illustration.
    normal = np.array([np.cos(np.pi / 12), 0.0, np.sin(np.pi / 12)])
    path = np.array([1.0, 0.0, 0.0])
    tangent = path - np.dot(path, normal) * normal
    tangent /= np.linalg.norm(tangent)
    impulse = 2.0 * normal + 0.1 * tangent
    omega = np.cross(-radius * normal, impulse) / inertia
    assert np.linalg.norm(omega) == pytest.approx(radius * 0.1 / inertia)
    assert omega[1] < 0.0
    assert np.cross(omega, path)[2] > 0.0
    assert np.dot(omega, normal) == pytest.approx(0.0, abs=1e-12)


def test_frictionless_central_impulse_produces_no_ball_spin() -> None:
    normal = np.array([0.8, 0.0, 0.6])
    assert np.cross(-0.02135 * normal, 2.0 * normal) == pytest.approx(np.zeros(3), abs=1e-15)


def test_off_center_head_impulse_reduces_normal_effective_mass() -> None:
    head_mass, ball_mass, head_inertia, offset = 0.2, 0.04593, 0.0004, 0.02
    centered_inverse_mass = 1 / head_mass + 1 / ball_mass
    offset_inverse_mass = centered_inverse_mass + offset**2 / head_inertia
    centered_impulse = 1.8 * 40 / centered_inverse_mass
    offset_impulse = 1.8 * 40 / offset_inverse_mass
    assert offset_impulse < centered_impulse
    assert offset_impulse / centered_impulse == pytest.approx(1.22965 / 1.27558)


def test_vacuum_carry_has_zero_first_derivative_at_its_optimum() -> None:
    speed, angle, step = 60.0, np.pi / 4, 1e-5

    def carry(theta: float) -> float:
        return float(speed**2 / GRAVITY * np.sin(2 * theta))

    derivative = (carry(angle + step) - carry(angle - step)) / (2 * step)
    assert derivative == pytest.approx(0.0, abs=1e-8)
    assert carry(angle - 0.1) < carry(angle)
    assert carry(angle + 0.1) < carry(angle)


def test_positive_spin_optimum_is_absent_from_old_polynomial() -> None:
    spin = np.linspace(0.0, 6000.0, 31)
    carry = 300.0 - 0.01 * spin - 1e-6 * spin**2
    assert np.all(np.diff(carry) < 0)


def test_declared_quadratic_launch_surface_and_conditional_optimum() -> None:
    curvature = np.array([[0.8, 0.002], [0.002, 0.00002]])
    assert np.all(np.linalg.eigvalsh(curvature) > 0)

    def loss(delta: list[float]) -> float:
        return float(0.5 * np.asarray(delta) @ curvature @ np.asarray(delta))

    assert 230.0 - loss([2.0, -200.0]) == pytest.approx(228.8)
    assert 230.0 - loss([-1.0, -200.0]) == pytest.approx(228.8)
    fit = minimize(lambda delta: loss([float(delta[0]), -200.0]), [0.0])
    assert fit.success
    assert fit.x[0] == pytest.approx(0.5, abs=1e-5)
    assert 230.0 - fit.fun == pytest.approx(229.7)


@pytest.mark.parametrize("correlation, expected_loss", [(0.5, 1.0), (-0.5, 0.6)])
def test_launch_covariance_changes_expected_quadratic_loss(
    correlation: float, expected_loss: float
) -> None:
    curvature = np.array([[0.8, 0.002], [0.002, 0.00002]])
    covariance = np.array([[1.0, correlation * 200.0], [correlation * 200.0, 40000.0]])
    assert 0.5 * np.trace(curvature @ covariance) == pytest.approx(expected_loss)


def test_smash_standard_deviation_is_not_variance() -> None:
    assert 100.0 * 0.05 == 5.0
    assert 100.0 * np.sqrt(0.05) == pytest.approx(22.360679775)


def test_smash_product_variance_includes_both_factors() -> None:
    speed = np.array([98.0, 102.0])
    smash = np.array([1.43, 1.53])
    ball_speed = np.outer(speed, smash)
    exact = (
        np.mean(speed) ** 2 * np.var(smash)
        + np.mean(smash) ** 2 * np.var(speed)
        + np.var(speed) * np.var(smash)
    )
    assert np.var(ball_speed) == pytest.approx(exact)
