"""Independent kinematic and work checks for the Chapter 22 idealizations."""

from pathlib import Path

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "articles/The_Physics_of_Golf"
SOURCES = (
    BOOK / "quarto/ch22_anatomy_joint_modeling.qmd",
    BOOK / "chapters/ch22_anatomy_joint_modeling.tex",
)


@pytest.mark.parametrize("source", SOURCES, ids=("web", "print"))
def test_joint_constraints_declare_frames_and_independent_rank(source: Path) -> None:
    """Both published editions must carry the corrected, checkable equations."""
    text = source.read_text(encoding="utf-8")
    for equation in (
        r"R u_B=u_A",
        r"u_A^T R u_B=0",
        r"W(\alpha)^T W(\alpha)=I_2",
        r"Q=W^T m",
        r"6(4-1)-3(6-1)=3",
    ):
        assert equation in text
    assert "When the two rotation axes align" not in text
    assert r"\bm{R}_{AB}(:, 1) \cdot \bm{u} &= \bm{u}" not in text


@pytest.mark.parametrize("angles", [(0.0, 0.0), (0.7, -1.1), (np.pi / 2, np.pi / 2)])
def test_universal_axes_stay_orthogonal_and_rate_map_matches_finite_rotation(angles) -> None:
    """Differentiate orientation independently; the rejected fixed-normal rule fails."""
    alpha, beta = angles
    first = Rotation.from_rotvec([alpha, 0, 0]).as_matrix()
    second = Rotation.from_rotvec([0, beta, 0]).as_matrix()
    orientation = first @ second
    axes = np.column_stack((np.eye(3)[:, 0], first[:, 1]))
    np.testing.assert_allclose(axes.T @ axes, np.eye(2), atol=1e-14)
    assert orientation[0, 1] == pytest.approx(0, abs=1e-14)
    step = 1e-6
    speed = np.array([0.8, -1.7])
    advanced = Rotation.from_rotvec([alpha + step * speed[0], 0, 0]).as_matrix()
    advanced = advanced @ Rotation.from_rotvec([0, beta + step * speed[1], 0]).as_matrix()
    angular_velocity = Rotation.from_matrix(advanced @ orientation.T).as_rotvec() / step
    np.testing.assert_allclose(angular_velocity, axes @ speed, atol=8e-7)
    moment = np.array([1.3, -2.4, 0.7])
    assert (axes.T @ moment) @ speed == pytest.approx(moment @ (axes @ speed))
    if alpha != 0:
        assert not np.allclose(orientation[:, 2], np.eye(3)[:, 2])


def test_joint_constraint_differentials_have_expected_rank() -> None:
    """Redundant vector notation gives two axis constraints, not three."""
    axis = np.array([0.0, 0.0, 1.0])
    step = 1e-6
    columns = [
        (Rotation.from_rotvec(step * direction).apply(axis) - axis) / step
        for direction in np.eye(3)
    ]
    assert np.linalg.matrix_rank(np.column_stack(columns), tol=1e-5) == 2
    orientation = Rotation.from_euler("XY", [0.7, -1.1]).as_matrix()
    scalar_gradient = np.array(
        [
            ((Rotation.from_rotvec(step * direction).as_matrix() @ orientation)[0, 1]) / step
            for direction in np.eye(3)
        ]
    )
    assert np.linalg.norm(scalar_gradient) == pytest.approx(1, abs=1e-6)


def test_euler_chart_singularity_does_not_remove_spherical_joint_freedom() -> None:
    """ZYX loses chart rank at pitch 90 degrees; SO(3) still has three tangents."""
    pitch = np.pi / 2
    chart = np.column_stack(([0, 0, 1], [0, 1, 0], [np.cos(pitch), 0, -np.sin(pitch)]))
    assert np.linalg.matrix_rank(chart) == 2
    orientation = Rotation.from_euler("y", pitch)
    step = 1e-6
    tangents = np.column_stack(
        [
            ((Rotation.from_rotvec(step * direction) * orientation) * orientation.inv()).as_rotvec()
            / step
            for direction in np.eye(3)
        ]
    )
    np.testing.assert_allclose(tangents, np.eye(3), atol=1e-10)


def test_base_accounting_and_axial_rotation_displacement() -> None:
    """A missing base weld adds six freedoms; axial error depends on radial offset."""
    assert 6 * (4 - 1) - 3 * (6 - 1) == 3
    assert 6 * (5 - 1) - (6 + 3 * (6 - 1)) == 3
    assert 6 * (5 - 1) - 3 * (6 - 1) == 9
    rotation = Rotation.from_euler("z", 10, degrees=True)
    for radius in (0.0, 0.05):
        point = np.array([radius, 0, -0.4])
        displacement = np.linalg.norm(rotation.apply(point) - point)
        assert displacement == pytest.approx(2 * radius * np.sin(np.deg2rad(5)))
