"""Independent particle, planar and tree checks for the paired chapter (#4318)."""

from pathlib import Path

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from src.affine_control.dynamics import force_cross, motion_cross, skew, spatial_inertia
from src.tools.articulated_body_examples import PreparedTree
from src.tools.screw_examples import adjoint

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "articles/The_Geometry_of_Motion"


def _particle_inertia(points: np.ndarray, masses: np.ndarray) -> np.ndarray:
    """Accumulate kinetic energy directly from each point's velocity map."""
    maps = np.concatenate(
        (-np.array([skew(p) for p in points]), np.tile(np.eye(3), (len(points), 1, 1))), axis=2
    )
    return np.einsum("n,nai,naj->ij", masses, maps, maps)


def test_force_motion_duality_has_opposite_sign() -> None:
    velocity = np.array([0, 0, 1, 1, 0, 0], dtype=float)
    wrench = np.array([0.1, 0.2, 0.3, 1, 2, 3])
    other = np.array([0.5, 0.5, 0.5, 0.1, 0.1, 0.1])
    assert wrench @ motion_cross(velocity) @ other == pytest.approx(0.65)
    assert (force_cross(velocity) @ wrench) @ other == pytest.approx(-0.65)


def test_point_mass_is_rank_three_and_has_zero_energy_rotations() -> None:
    center = np.array([0.3, -0.2, 0.1])
    inertia = spatial_inertia(2, center, np.zeros((3, 3)))
    null_motion = np.vstack((np.eye(3), skew(center)))
    assert np.linalg.matrix_rank(inertia) == 3
    assert inertia @ null_motion == pytest.approx(np.zeros((6, 3)), abs=1e-15)


def test_inertia_matches_direct_particle_energy() -> None:
    rng = np.random.default_rng(4318)
    points = rng.normal(size=(12, 3))
    masses = rng.uniform(0.1, 2, size=12)
    center = np.average(points, axis=0, weights=masses)
    relative = points - center
    central = _particle_inertia(relative, masses)[:3, :3]
    inertia = spatial_inertia(float(masses.sum()), center, central)
    assert inertia == pytest.approx(_particle_inertia(points, masses))
    velocity = rng.normal(size=6)
    particle_velocity = velocity[3:] + np.cross(velocity[:3], points)
    energy = np.sum(masses * np.sum(particle_velocity**2, axis=1)) / 2
    assert velocity @ inertia @ velocity / 2 == pytest.approx(energy)


def test_planar_embedding_exposes_both_original_sign_errors() -> None:
    embed = np.eye(6)[:, [2, 3, 4]]
    velocity = np.array([2, 3, 5], dtype=float)
    cross = embed.T @ motion_cross(embed @ velocity) @ embed
    assert cross == pytest.approx(np.array([[0, 0, 0], [5, 0, -2], [-3, 2, 0]]))
    inertia = embed.T @ spatial_inertia(2, np.array([0.3, 0.4, 0]), np.eye(3) * 0.1) @ embed
    assert inertia == pytest.approx(np.array([[0.6, -0.8, 0.6], [-0.8, 2, 0], [0.6, 0, 2]]))


def test_transform_inertia_matches_relocated_particles_and_power() -> None:
    from src.tools.spatial_inertia_examples import reexpress_inertia

    points = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [-1, -1, -1]], dtype=float)
    masses = np.array([1, 2, 3, 4], dtype=float)
    pose = np.eye(4)
    pose[:3, :3] = Rotation.from_rotvec([0.2, -0.4, 0.7]).as_matrix()
    pose[:3, 3] = [0.8, -0.6, 0.5]
    source = _particle_inertia(points, masses)
    relocated = points @ pose[:3, :3].T + pose[:3, 3]
    result = reexpress_inertia(pose, source)
    assert result == pytest.approx(_particle_inertia(relocated, masses), abs=1e-13)
    velocity = np.array([1, 2, 3, -1, 0.4, 2])
    change = adjoint(pose)
    assert (change @ velocity) @ result @ (change @ velocity) == pytest.approx(
        velocity @ source @ velocity
    )


def _branched_tree() -> PreparedTree:
    """Use distinct offsets and rotations so reversed transforms cannot pass."""
    poses = np.tile(np.eye(4), (4, 1, 1))
    poses[1:, :3, 3] = [[0.7, 0, 0], [0, 0.5, 0], [0.2, 0.1, 0]]
    poses[1:, :3, :3] = Rotation.from_euler("z", [[0.4], [-0.7], [0.2]]).as_matrix()
    transforms = np.array([adjoint(np.linalg.inv(pose)) for pose in poses])
    inertia = spatial_inertia(2, np.array([0.2, 0.1, 0]), np.diag([0.1, 0.12, 0.15]))
    return PreparedTree(
        (-1, 0, 0, 1), transforms, np.tile([0, 0, 1, 0, 0, 0], (4, 1)), np.tile(inertia, (4, 1, 1))
    )


def test_composite_recursion_matches_independent_body_jacobians() -> None:
    from src.tools.spatial_inertia_examples import composite_inertias, joint_mass_matrix

    tree = _branched_tree()
    original = tree.inertia.copy()
    jacobians = np.zeros((4, 6, 4))
    for body, parent in enumerate(tree.parents):
        if parent >= 0:
            jacobians[body] = tree.transform[body] @ jacobians[parent]
        jacobians[body, :, body] = tree.subspace[body]
    expected = np.einsum("nai,nab,nbj->ij", jacobians, tree.inertia, jacobians)
    mass = joint_mass_matrix(tree)
    assert mass == pytest.approx(expected)
    assert mass[1, 2] == pytest.approx(0)
    assert mass[2, 3] == pytest.approx(0)
    assert np.linalg.eigvalsh(mass).min() > 0
    assert composite_inertias(tree)[0] @ tree.subspace[0] @ tree.subspace[0] == pytest.approx(
        mass[0, 0]
    )
    assert np.array_equal(tree.inertia, original)


def test_two_link_worked_mass_matrix_matches_point_velocities() -> None:
    from src.tools.spatial_inertia_examples import joint_mass_matrix

    inertia = np.array(
        [
            spatial_inertia(2, np.array([0.3, 0, 0]), np.diag([0.05, 0.05, 0.01])),
            spatial_inertia(1, np.array([0.25, 0, 0]), np.diag([0.02, 0.02, 0.005])),
        ]
    )
    for angle in (0, np.pi / 2, -0.7):
        pose = np.eye(4)
        pose[:3, :3] = Rotation.from_rotvec([0, 0, angle]).as_matrix()
        pose[0, 3] = 0.6
        tree = PreparedTree(
            (-1, 0),
            np.array([np.eye(6), adjoint(np.linalg.inv(pose))]),
            np.tile([0, 0, 1, 0, 0, 0], (2, 1)),
            inertia,
        )
        expected = np.array(
            [
                [0.6175 + 0.3 * np.cos(angle), 0.0675 + 0.15 * np.cos(angle)],
                [0.0675 + 0.15 * np.cos(angle), 0.0675],
            ]
        )
        assert joint_mass_matrix(tree) == pytest.approx(expected)
        rates = np.array([1, -2])
        center2 = pose[:3, :3] @ np.array([0.25, 0, 0])
        velocity2 = np.cross([0, 0, rates[0]], pose[:3, 3] + center2) + np.cross(
            [0, 0, rates[1]], center2
        )
        energy = (0.19 * rates[0] ** 2 + 0.005 * rates.sum() ** 2 + velocity2 @ velocity2) / 2
        assert rates @ expected @ rates / 2 == pytest.approx(energy)
        if angle == 0:
            assert energy == pytest.approx(0.15875)


def test_rotated_wrench_keeps_power_with_shifted_twist_origin() -> None:
    from src.tools.screw_examples import reexpress_wrench

    pose = np.eye(4)
    pose[0, 3] = 0.2
    velocity = np.array([0, 0, 3, 1, 2, 0])
    force = np.array([0, 0, 0, 0, 10, 0])
    transformed = reexpress_wrench(pose, force)
    assert transformed == pytest.approx([0, 0, 2, 0, 10, 0])
    assert adjoint(pose) @ velocity == pytest.approx([0, 0, 3, 1, 1.4, 0])
    assert transformed @ adjoint(pose) @ velocity == pytest.approx(20)


def test_positive_definite_central_tensor_can_be_nonphysical() -> None:
    tensor = np.diag([1, 1, 3])
    assert np.linalg.eigvalsh(tensor).min() > 0
    second_moment = np.trace(tensor) / 2 * np.eye(3) - tensor
    assert np.linalg.eigvalsh(second_moment).min() == pytest.approx(-0.5)


def test_constraint_projection_preserves_physical_acceleration_under_scaling() -> None:
    mass = np.diag([2, 3])
    force = np.array([1, 0])
    for scale in (1, 1 / np.sqrt(2), 3):
        basis = np.array([1, -1]) * scale
        reduced = basis @ mass @ basis
        acceleration = basis * (basis @ force / reduced)
        assert acceleration == pytest.approx([0.2, -0.2])
        reaction = mass @ acceleration - force
        assert reaction == pytest.approx([-0.6, -0.6])
        assert reaction @ basis == pytest.approx(0, abs=1e-15)


@pytest.mark.parametrize("bad", [np.full((6, 6), np.nan), np.eye(3)])
def test_reexpress_inertia_rejects_invalid_array(bad: np.ndarray) -> None:
    from src.tools.spatial_inertia_examples import reexpress_inertia

    with pytest.raises(ValueError, match="finite 6 by 6"):
        reexpress_inertia(np.eye(4), bad)


@pytest.mark.parametrize(
    "relative",
    ["Volume_0/chapters/ch08_spatial_algebra.tex", "quarto/vol0_ch08_spatial_algebra.qmd"],
)
def test_both_editions_include_the_complete_rigorous_treatment(relative: str) -> None:
    text = (BOOK / relative).read_text(encoding="utf-8")
    for topic in (
        "rank three",
        "triangle inequalities",
        "body-fixed",
        "fifteen",
        "kinetic energy",
        "joint_mass_matrix",
    ):
        assert topic.casefold() in text.casefold(), topic
    for wrong in (
        "should be equal",
        "forward-dynamics calculations (solving for accelerations given forces) are $O(N)$ via matrix multiplication",
        "verify it is positive definite",
    ):
        assert wrong not in text
