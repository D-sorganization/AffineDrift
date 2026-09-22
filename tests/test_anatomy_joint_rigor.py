"""Independent kinematic and work checks for the Chapter 22 idealizations."""

import re
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


@pytest.mark.parametrize("source", SOURCES, ids=("web", "print"))
def test_anatomical_models_separate_motion_work_and_clinical_inference(source: Path) -> None:
    """Keep both editions free of specific scientific errors found in review."""
    text = source.read_text(encoding="utf-8")
    assert "from radial extension toward ulnar flexion" in text
    for equation in (r"R_{PF}=R_P^T R_F", r"R_C=R_H R_{HC}", r"d=35-\operatorname{rank}J_c"):
        assert equation in text
    assert "five male collegiate golfers" in text
    assert "Lim2012LumbarLoads" in text
    for rejected in (
        "It would be accurate.",
        "the knee has one input: the flexion angle",
        "13$ DOF per arm",
        "the system is on autopilot",
        "extension + ulnar deviation) is stronger",
    ):
        assert rejected not in text


def test_relative_hip_rotation_is_invariant_to_common_laboratory_rotation() -> None:
    pelvis = Rotation.from_euler("xyz", [0.2, -0.4, 0.8]).as_matrix()
    femur = Rotation.from_euler("xyz", [-0.3, 0.1, 0.5]).as_matrix()
    common = Rotation.from_rotvec([0.7, -0.2, 0.4]).as_matrix()
    np.testing.assert_allclose((common @ pelvis).T @ (common @ femur), pelvis.T @ femur)
    assert not np.allclose((common @ pelvis).T @ femur, pelvis.T @ femur)


def test_shoulder_center_translation_survives_a_correct_orientation_fit() -> None:
    """Differentiate a moving center plus rotation without using its Jacobian."""
    angle, speed, radius = 0.4, 1.3, 0.08
    offset = np.array([0.3, -0.1, 0.0])

    def point(q: float) -> np.ndarray:
        center = radius * np.array([np.cos(q), np.sin(q), 0.0])
        return center + Rotation.from_euler("z", 2 * q).apply(offset)

    step = 1e-6
    numerical = (point(angle + step * speed) - point(angle - step * speed)) / (2 * step)
    rotation_only = np.cross([0, 0, 2 * speed], Rotation.from_euler("z", 2 * angle).apply(offset))
    center_speed = radius * speed * np.array([-np.sin(angle), np.cos(angle), 0.0])
    np.testing.assert_allclose(numerical, rotation_only + center_speed, atol=1e-9)
    assert np.linalg.norm(numerical - rotation_only) == pytest.approx(radius * speed)


def test_prescribed_shoulder_coupling_requires_force_pullback() -> None:
    """A force on a dependent coordinate contributes to the independent moment."""
    q, qdot = 0.6, -1.2
    full_force = np.array([2.0, -3.0])
    derivative = np.array([1.0, 2 * q])  # q_s = q_g**2
    full_velocity = derivative * qdot
    reduced_force = derivative @ full_force
    assert reduced_force * qdot == pytest.approx(full_force @ full_velocity)
    assert reduced_force != pytest.approx(full_force[0])


def test_coupled_wrist_energy_and_rigid_grip_roll() -> None:
    stiffness = np.array([[2.0, -1.0], [-1.0, 2.0]])
    np.testing.assert_allclose(np.linalg.eigvalsh(stiffness), [1, 3])
    for displacement, energy in (([0.1, 0.1], 0.01), ([0.1, -0.1], 0.03)):
        q = np.array(displacement)
        assert 0.5 * q @ stiffness @ q == pytest.approx(energy)
    fixed_grip = Rotation.from_euler("y", 0.7)
    hand = Rotation.from_euler("x", 0.4)
    club = hand * fixed_grip
    step = 1e-6
    advanced_hand = Rotation.from_euler("x", 0.4 + 2 * step)
    advanced_club = advanced_hand * fixed_grip
    rate = (advanced_club * club.inv()).as_rotvec() / step
    np.testing.assert_allclose(rate, [2, 0, 0], atol=1e-9)
    assert abs(rate @ club.apply([0, 0, 1])) > 0.5
    np.testing.assert_allclose((hand.inv() * club).as_matrix(), fixed_grip.as_matrix(), atol=1e-14)


def test_arch_energy_ledger_and_explicit_body_counts() -> None:
    stiffness, damping, angle, speed = 8.0, 0.3, 0.2, -0.7
    moment = -stiffness * angle - damping * speed
    step = 1e-6
    energy_rate = (
        0.5 * stiffness * (angle + step * speed) ** 2
        - 0.5 * stiffness * (angle - step * speed) ** 2
    ) / (2 * step)
    assert moment * speed == pytest.approx(-energy_rate - damping * speed**2)
    freedoms = [3, 3, 3, 1, 2, 3, 1, 2, 0]
    bodies = len(freedoms) + 1
    assert bodies == 10
    assert 6 * (bodies - 1) - sum(6 - value for value in freedoms) == 18
    assert 6 + 3 + 2 * (3 + 1 + 2) + 2 * (3 + 2 + 2) == 35


def test_print_labels_do_not_collide_with_other_chapters() -> None:
    """An isolated chapter build cannot expose duplicate labels in the full book."""
    own_labels = set(re.findall(r"\\label\{([^}]+)\}", SOURCES[1].read_text(encoding="utf-8")))
    for chapter in (BOOK / "chapters").glob("*.tex"):
        if chapter == SOURCES[1]:
            continue
        labels = set(re.findall(r"\\label\{([^}]+)\}", chapter.read_text(encoding="utf-8")))
        assert not own_labels.intersection(labels), chapter.name
