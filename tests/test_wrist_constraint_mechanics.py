"""Independent kinematic and reaction checks for the wrist review (#4299)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from src.tools.wrist_universal_joint.torque_calculator import universal_joint_transmission_ratio


@pytest.mark.parametrize("bend", [0.2, 0.6, 1.0])
@pytest.mark.parametrize("phase", [-1.2, -0.3, 0.4, np.pi / 2])
def test_cardan_ratio_differentiates_geometric_angle_relation(bend: float, phase: float) -> None:
    """An angle derivative detects errors hidden by reciprocal-product tests."""
    step = 1e-6

    def output_angle(angle: float) -> float:
        return float(np.arctan2(np.cos(bend) * np.sin(angle), np.cos(angle)))

    numerical = (output_angle(phase + step) - output_angle(phase - step)) / (2 * step)
    speed_ratio, _ = universal_joint_transmission_ratio(phase, bend)
    assert speed_ratio == pytest.approx(numerical, rel=2e-8)


def test_cardan_completes_one_output_turn_per_input_turn() -> None:
    """The original square-root formula fails the integral winding constraint."""
    phase = np.linspace(0, 2 * np.pi, 4001)
    speed = np.array([universal_joint_transmission_ratio(float(p), 0.7)[0] for p in phase])
    assert np.trapezoid(speed, phase) == pytest.approx(2 * np.pi, rel=1e-10)


@pytest.mark.parametrize("phase,bend", [(np.nan, 0.2), (0.2, np.inf), (-np.inf, 0.3)])
def test_cardan_rejects_nonfinite_angles(phase: float, bend: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        universal_joint_transmission_ratio(phase, bend)


def test_streamlit_sweep_uses_phase_and_bend_in_the_same_order_as_current_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Only the cache decorator is optional here; the actual numerical helper
    # remains unmocked. Keep this test runnable without other tests' UI stubs.
    if "streamlit" not in sys.modules and importlib.util.find_spec("streamlit") is None:
        monkeypatch.setitem(
            sys.modules, "streamlit", SimpleNamespace(cache_resource=lambda **_: lambda fn: fn)
        )
    from src.tools.wrist_universal_joint.plots import _compute_transmission_sweep

    phases = np.array([-35.0, 0.0, 20.0, 55.0])
    bend = 0.4
    torque, speed, _, _ = _compute_transmission_sweep(phases, bend, 0.2, 0.1)
    expected = np.array(
        [universal_joint_transmission_ratio(float(p), bend) for p in np.radians(phases)]
    )
    np.testing.assert_allclose(speed, expected[:, 0])
    np.testing.assert_allclose(torque, expected[:, 1])


def test_transmission_plot_separates_units_and_marks_exact_phase(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Other legacy tests install a MagicMock decorator at collection time.
    # Load the production source with only caching disabled, without reloading
    # or changing the module that those callers already imported.
    monkeypatch.setitem(
        sys.modules, "streamlit", SimpleNamespace(cache_resource=lambda **_: lambda fn: fn)
    )
    spec = importlib.util.spec_from_file_location(
        "src.tools.wrist_universal_joint._review_plots",
        Path(__file__).parents[1] / "src/tools/wrist_universal_joint/plots.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    figure = module.plot_transmission_sweep(40, 17.3, 0.2, 0.1, True, True, True, True)
    assert len(figure.axes) == 2
    ratio_axis, gain_axis = figure.axes
    assert "Dimensionless" in ratio_axis.get_ylabel()
    assert "(rad/s²)/(N·m)" in gain_axis.get_ylabel()
    assert len(gain_axis.lines) == 2
    expected = universal_joint_transmission_ratio(np.radians(17.3), np.radians(40))[1]
    marker = next(line for line in ratio_axis.lines if line.get_marker() == "o")
    assert marker.get_ydata()[0] == pytest.approx(expected, rel=1e-12)


def test_wrist_reaction_annihilates_actual_relative_rotation() -> None:
    """Differentiate the rotation matrix, rather than treating Euler rates as omega."""
    from scipy.spatial.transform import Rotation

    phi, psi = np.radians([30, 20])
    rates = np.array([1.3, -0.7])

    def orientation(time: float) -> np.ndarray:
        return (
            Rotation.from_rotvec([phi + rates[0] * time, 0, 0]).as_matrix()
            @ Rotation.from_rotvec([0, psi + rates[1] * time, 0]).as_matrix()
        )

    rotation = orientation(0)
    step = 1e-6
    omega_matrix = (orientation(step) - orientation(-step)) / (2 * step) @ rotation.T
    omega = np.array([omega_matrix[2, 1], omega_matrix[0, 2], omega_matrix[1, 0]])
    reaction = np.array([0, -0.5, np.sqrt(3) / 2])
    assert reaction @ omega == pytest.approx(0, abs=1e-10)
    assert abs(omega[2]) > 0.3  # Permitted motion need not have zero forearm z component.
    np.testing.assert_allclose(rotation.T @ reaction, [-np.sin(psi), 0, np.cos(psi)], atol=1e-12)


def test_reaction_changes_with_input_in_full_saddle_point_solve() -> None:
    """Solve the unreduced equations to verify the article's counterexample."""
    inertia = np.array([[2, 0, 0.5], [0, 2, 0], [0.5, 0, 2]])
    constraint = np.array([[0, 0, 1]])
    system = np.block([[inertia, -constraint.T], [constraint, np.zeros((1, 1))]])
    for torque in [-4.0, 0.0, 7.0]:
        solution = np.linalg.solve(system, [torque, 0, 0, 0])
        np.testing.assert_allclose(solution, [torque / 2, 0, 0, torque / 4], atol=1e-12)


def test_moving_point_torque_matches_particle_force_sum() -> None:
    """Check transport against particle accelerations with nonzero support acceleration."""
    positions = np.array([[0.2, 0.1, 0.3], [-0.1, 0.2, 0.4], [0.3, -0.2, 0.5]])
    masses = np.array([0.2, 0.3, 0.1])
    omega, acceleration, support = np.array([[2, -1, 3], [0.5, 2, -0.4], [4, -2, 1]])
    particle_acceleration = (
        support + np.cross(acceleration, positions) + np.cross(omega, np.cross(omega, positions))
    )
    actual_torque = np.cross(positions, masses[:, None] * particle_acceleration).sum(axis=0)
    inertia = sum(
        mass * ((position @ position) * np.eye(3) - np.outer(position, position))
        for mass, position in zip(masses, positions, strict=True)
    )
    first_moment = (masses[:, None] * positions).sum(axis=0)
    predicted = (
        inertia @ acceleration + np.cross(omega, inertia @ omega) + np.cross(first_moment, support)
    )
    np.testing.assert_allclose(predicted, actual_torque, atol=1e-12)
    assert np.linalg.norm(np.cross(first_moment, support)) > 0.1


@pytest.mark.parametrize("loft", [0.0, 0.2, 0.6])
def test_face_yaw_jacobian_matches_rotated_face_normal(loft: float) -> None:
    from scipy.spatial.transform import Rotation

    normal = np.array([np.cos(loft), 0, np.sin(loft)])
    gradient = np.array([-np.tan(loft), 0, 1])
    step = 1e-6
    for axis in np.eye(3):
        plus = Rotation.from_rotvec(step * axis).apply(normal)
        minus = Rotation.from_rotvec(-step * axis).apply(normal)
        derivative = (np.arctan2(plus[1], plus[0]) - np.arctan2(minus[1], minus[0])) / (2 * step)
        assert derivative == pytest.approx(gradient @ axis, abs=1e-10)


def test_torque_covariance_integration_has_correct_time_and_unit_scaling() -> None:
    duration, torque_sd = 0.01, 0.15
    time = np.linspace(0, duration, 10001)
    for inertia, angle in [(0.005, 0.0015), (0.00015, 0.05)]:
        kernel = (duration - time) / inertia
        frozen_sd = torque_sd * np.trapezoid(kernel, time)
        assert frozen_sd == pytest.approx(angle, rel=1e-12)
        intensity = 0.002  # N² m² s, not a pointwise variance.
        white_variance = intensity * np.trapezoid(kernel**2, time)
        assert white_variance == pytest.approx(intensity * duration**3 / (3 * inertia**2), rel=1e-8)
