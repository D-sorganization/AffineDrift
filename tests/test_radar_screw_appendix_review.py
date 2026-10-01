"""Additional numerical and publication boundaries for appendix review #4717.

General Doppler rank/nullspace and SE(3) identities remain independently
covered by test_launch_monitor_estimation_rigor.py; do not duplicate them here.
"""

from pathlib import Path

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
APPENDIX = (
    ROOT / "articles/Launch_Monitor_Technology_Review/sections/appendix-e-screw-kinematics.tex"
)


@pytest.mark.parametrize(
    "transmitters,limit,resolution,duration_ms",
    [(1, 50.0, 0.78125, 3.2), (3, 50.0 / 3, 0.2604166667, 9.6)],
)
def test_same_transmitter_interval_controls_doppler_budget(
    transmitters: int, limit: float, resolution: float, duration_ms: float
) -> None:
    wavelength, chirp_interval, loops = 0.005, 25e-6, 128
    repeat_interval = transmitters * chirp_interval
    assert wavelength / (4 * repeat_interval) == pytest.approx(limit)
    assert wavelength / (2 * loops * repeat_interval) == pytest.approx(resolution)
    assert loops * repeat_interval * 1000 == pytest.approx(duration_ms)


def test_original_range_budget_does_not_freeze_target_in_one_bin() -> None:
    nominal_light_speed = 3e8
    range_bin = nominal_light_speed / (2 * 4e9)
    radial_travel = 50 * 128 * 25e-6
    assert range_bin == pytest.approx(0.0375)
    assert radial_travel == pytest.approx(0.16)
    assert radial_travel / range_bin == pytest.approx(4.2666666667)


def test_four_ghz_ramp_exceeds_three_tx_unaliased_fifty_mps_chirp_budget() -> None:
    bandwidth, max_slope = 4e9, 250e6 / 1e-6
    minimum_ramp = bandwidth / max_slope
    maximum_chirp_interval = 0.005 / (4 * 3 * 50)
    assert minimum_ramp == pytest.approx(16e-6)
    assert maximum_chirp_interval == pytest.approx(8.333333333e-6)
    assert minimum_ramp > maximum_chirp_interval


def test_face_azimuth_rate_is_not_a_shaft_axis_component() -> None:
    normal = np.array([0.8, 0.0, 0.6])
    omega, shaft = np.array([3.0, 4.0, 5.0]), np.array([0.0, 0.0, 1.0])
    derivative = np.cross(omega, normal)
    rate = (normal[0] * derivative[1] - normal[1] * derivative[0]) / (
        normal[0] ** 2 + normal[1] ** 2
    )
    step = 1e-7
    moved = Rotation.from_rotvec(omega * step).apply(normal)
    finite_difference = np.arctan2(moved[1], moved[0]) / step
    assert finite_difference == pytest.approx(rate, rel=1e-6)
    assert rate == pytest.approx(2.75)
    assert omega @ shaft == pytest.approx(5.0)


def test_smooth_single_origin_ambiguity_survives_time_variation() -> None:
    """Smoothness alone cannot select a global orientation about the radar."""
    rotation = Rotation.from_rotvec([0.2, -0.3, 0.5]).as_matrix()
    times = np.linspace(0.0, 0.03, 15)
    points = np.column_stack((2 + 4 * times, 0.1 + times**2, 0.3 - times))
    velocities = np.column_stack((np.full_like(times, 4), 2 * times, -np.ones_like(times)))
    radial = np.sum(points * velocities, axis=1) / np.linalg.norm(points, axis=1)
    transformed = points @ rotation.T
    transformed_velocities = velocities @ rotation.T
    alternate = np.sum(transformed * transformed_velocities, axis=1) / np.linalg.norm(
        transformed, axis=1
    )
    assert alternate == pytest.approx(radial)
    assert not np.allclose(transformed, points)
    # Angle or calibrated feature-position observations would distinguish these.


@pytest.mark.parametrize(
    "unsupported",
    [
        "the twist itself is frame-invariant",
        "The rank deficiency resolves \\emph{across} frames",
        "closure rate and a rigorous swing plane as free by-products",
        "path and attack angle move from \\emph{derived} to \\emph{measured}",
        "a covariance $(A^{\\mathsf T} W A)^{-1}\\sigma^2$ for free",
        "form $\\vect{p}_i = (R_i, \\theta_i, \\phi_i)$ in Cartesian",
    ],
)
def test_appendix_does_not_repeat_disproved_inference(unsupported: str) -> None:
    assert unsupported not in APPENDIX.read_text(encoding="utf-8")


def test_appendix_preserves_existing_equation_and_section_anchors() -> None:
    source = APPENDIX.read_text(encoding="utf-8")
    for label in [
        "app:screw",
        "sec:screw-context",
        "sec:screw-primer",
        "sec:screw-measurement",
        "sec:screw-ceiling",
        "sec:screw-recipe",
        "sec:screw-validation",
        "eq:screw-twist",
        "eq:screw-pointvel",
        "eq:screw-isa",
        "eq:screw-doppler",
        "eq:screw-ls",
    ]:
        assert source.count(r"\label{" + label + "}") == 1
