"""Tests for visualization dynamics and kinematic mappings extracted from LaTeX."""

import re
import types
from pathlib import Path
from typing import Any

import numpy as np
import pytest


def _load_tex_module() -> types.ModuleType:
    """Extract and compile Python listings from chapter 9 LaTeX source."""
    tex_path = (
        Path(__file__).resolve().parents[1]
        / "articles"
        / "The_Geometry_of_Motion"
        / "Volume_V"
        / "chapters"
        / "ch09_visualization.tex"
    )
    content = tex_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"\\begin\{lstlisting\}\[language=Python[^\]]*\](.*?)\\end\{lstlisting\}",
        re.DOTALL,
    )
    blocks = pattern.findall(content)
    combined = "\n\n".join(b.strip() for b in blocks)

    mod = types.ModuleType("ch09_visualization")
    code_obj = compile(combined, str(tex_path), "exec", dont_inherit=True)
    # Repository-owned listing at a fixed path, with no external input.
    # nosemgrep: python.lang.security.audit.exec-detected.exec-detected
    exec(code_obj, mod.__dict__)
    return mod


_MOD = _load_tex_module()
compute_joint_positions_2d = _MOD.compute_joint_positions_2d
phase_portrait = _MOD.phase_portrait


def velocity_ellipsoid(jacobian: np.ndarray, scales: np.ndarray) -> tuple:
    """Call the actual listing; preserve RED tests of existing other functions."""
    return _MOD.velocity_ellipsoid(jacobian, scales)


def test_compute_joint_positions_2d_known_geometries() -> None:
    """Verify base origin, right-angle elbow, and full folded configurations."""
    q_right = np.array([0.0, np.pi / 2.0], dtype=float)
    lens_right = np.array([1.0, 1.0], dtype=float)
    pos_right = compute_joint_positions_2d(q_right, lens_right)

    assert pos_right.shape == (3, 2)
    np.testing.assert_allclose(pos_right[0], [0.0, 0.0], atol=1e-12)
    np.testing.assert_allclose(pos_right[1], [1.0, 0.0], atol=1e-12)
    np.testing.assert_allclose(pos_right[2], [1.0, 1.0], atol=1e-12)

    q_fold = np.array([0.0, np.pi], dtype=float)
    pos_fold = compute_joint_positions_2d(q_fold, lens_right)
    np.testing.assert_allclose(pos_fold[2], [0.0, 0.0], atol=1e-12)


def test_joint_fk_finite_difference_jacobian_two_link() -> None:
    """Verify endpoint kinematics match the analytic 2-link Jacobian."""
    q = np.array([np.pi / 6.0, np.pi / 4.0], dtype=float)
    lens = np.array([1.5, 0.8], dtype=float)
    eps = 1e-7

    theta1 = q[0]
    theta12 = q[0] + q[1]
    j_hand = np.array(
        [
            [-lens[0] * np.sin(theta1) - lens[1] * np.sin(theta12), -lens[1] * np.sin(theta12)],
            [lens[0] * np.cos(theta1) + lens[1] * np.cos(theta12), lens[1] * np.cos(theta12)],
        ],
        dtype=float,
    )

    def centered_column(column: int) -> np.ndarray:
        delta = eps * np.eye(2)[column]
        return (
            compute_joint_positions_2d(q + delta, lens)[-1]
            - compute_joint_positions_2d(q - delta, lens)[-1]
        ) / (2 * eps)

    j_num = np.vectorize(centered_column, signature="()->(n)")(np.arange(2)).T

    np.testing.assert_allclose(j_num, j_hand, rtol=1e-5, atol=1e-5)


@pytest.mark.parametrize(
    ("q_bad", "lens_bad"),
    [
        (np.array([], dtype=float), np.array([], dtype=float)),
        (np.array([0.0], dtype=float), np.array([1.0, 1.0], dtype=float)),
        (np.array([np.nan, 0.0]), np.array([1.0, 1.0], dtype=float)),
        (np.array([0.0, 0.0]), np.array([1.0, -0.5], dtype=float)),
        (np.array([0.0, 0.0]), np.array([1.0, 0.0], dtype=float)),
        (np.zeros((2, 2)), np.array([1.0, 1.0], dtype=float)),
    ],
)
def test_compute_joint_positions_2d_invalid_inputs(q_bad: np.ndarray, lens_bad: np.ndarray) -> None:
    """Ensure invalid q or lengths dimensions/values raise ValueError."""
    with pytest.raises(ValueError):
        compute_joint_positions_2d(q_bad, lens_bad)


def test_phase_portrait_projection_no_aliasing_and_unwrapped() -> None:
    """Ensure multi-turn angles preserve unwrapped trajectories and isolate coordinates."""
    steps = 100
    q_history = np.zeros((steps, 3), dtype=float)
    qd_history = np.zeros((steps, 3), dtype=float)

    # Angle spans 0 to 4*pi (unwrapped); velocity is constant
    q_history[:, 1] = np.linspace(0.0, 4.0 * np.pi, steps)
    qd_history[:, 1] = np.full(steps, 2.5)

    data = phase_portrait(q_history, qd_history, joint_idx=1, label="Elbow")
    x, y, label = data["x"], data["y"], data["label"]

    assert label == "Elbow"
    assert x[0] == pytest.approx(0.0)
    assert x[-1] == pytest.approx(4.0 * np.pi)
    np.testing.assert_allclose(y, 2.5)

    # Validate output isolation (no aliases/views)
    x[0] = 999.0
    assert q_history[0, 1] != 999.0


@pytest.mark.parametrize(
    ("q_h", "qd_h", "idx"),
    [
        (np.ones((10, 2)), np.ones((5, 2)), 0),
        (np.ones((10, 2)), np.ones((10, 3)), 0),
        (np.array([]), np.array([]), 0),
        (np.ones((10, 2)), np.ones((10, 2)), 2),
        (np.ones((10, 2)), np.ones((10, 2)), -1),
        (np.ones((10, 2)), np.ones((10, 2)), True),
        (np.full((10, 2), np.nan), np.ones((10, 2)), 0),
    ],
)
def test_phase_portrait_invalid_inputs(q_h: Any, qd_h: Any, idx: Any) -> None:
    """Reject mismatched, non-2D, invalid indexing, or non-finite inputs."""
    with pytest.raises((ValueError, IndexError, TypeError)):
        phase_portrait(q_h, qd_h, joint_idx=idx)


@pytest.mark.parametrize(
    ("J", "scales"),
    [
        (np.array([[2.0, -1.0], [0.5, 1.5]]), np.array([1.0, 2.0])),
        (np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]), np.array([0.5, 1.5])),
        (np.array([[1.0, 2.0, 0.5], [-1.0, 0.0, 1.0]]), np.array([1.0, 1.0, 2.0])),
    ],
)
def test_velocity_ellipsoid_reconstruction_tall_and_wide(J: np.ndarray, scales: np.ndarray) -> None:
    """Reconstruct the mapped rate-ball shape for rectangular Jacobians."""
    A = J @ np.diag(scales)
    axes, radii, rank = velocity_ellipsoid(J, scales)
    m = J.shape[0]

    assert axes.shape == (m, m)
    assert len(radii) == m
    assert rank == np.linalg.matrix_rank(A)
    assert np.all(np.diff(radii) <= 1e-12)  # descending order

    # Orthonormal basis check
    np.testing.assert_allclose(axes @ axes.T, np.eye(m), atol=1e-12)

    # Spectral reconstruction invariant to eigenvector sign choices
    cov_expected = A @ A.T
    cov_reconstructed = axes @ np.diag(radii**2) @ axes.T
    np.testing.assert_allclose(cov_reconstructed, cov_expected, atol=1e-12)


def test_velocity_ellipsoid_singular_collapse_and_scale_rotation() -> None:
    """Verify rank collapse under singular J and principal axes rotation with scales."""
    # Zero Jacobian: complete collapse
    J_zero = np.zeros((2, 3), dtype=float)
    scales_zero = np.array([1.0, 2.0, 3.0], dtype=float)
    _, radii_zero, rank_zero = velocity_ellipsoid(J_zero, scales_zero)
    assert rank_zero == 0
    np.testing.assert_allclose(radii_zero, [0.0, 0.0], atol=1e-12)

    # Diagonal Jacobian with non-uniform scaling alters principal semi-axes lengths
    J_diag = np.eye(2, dtype=float)
    scales_aniso = np.array([0.2, 5.0], dtype=float)
    _, radii_aniso, rank_aniso = velocity_ellipsoid(J_diag, scales_aniso)
    assert rank_aniso == 2
    np.testing.assert_allclose(radii_aniso, [5.0, 0.2], atol=1e-12)


@pytest.mark.parametrize(
    ("J_bad", "scales_bad"),
    [
        (np.ones((2, 2)), np.array([1.0, -0.5])),
        (np.ones((2, 2)), np.array([1.0, 0.0])),
        (np.ones((2, 2)), np.array([1.0])),
        (np.full((2, 2), np.inf), np.array([1.0, 1.0])),
        (np.empty((0, 2)), np.array([1.0, 1.0])),
        (np.ones((2, 2, 1)), np.array([1.0, 1.0])),
    ],
)
def test_velocity_ellipsoid_invalid_inputs(J_bad: np.ndarray, scales_bad: np.ndarray) -> None:
    """Validate dimensionality, positivity, and finiteness error enforcement."""
    with pytest.raises(ValueError):
        velocity_ellipsoid(J_bad, scales_bad)
