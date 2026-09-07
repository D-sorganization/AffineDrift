"""Independent energy, constraint and importer checks for the robot-model lesson."""

import importlib
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from defusedxml import ElementTree as ET


@pytest.fixture(scope="module")
def example() -> Any:
    return importlib.import_module("src.tools.robot_model_examples")


@pytest.mark.parametrize("angle", [-2.0, 0.0, 0.7, 2.9])
def test_mass_matrix_matches_cartesian_kinetic_energy(example: Any, angle: float) -> None:
    arm = example.TwoLinkArm()
    q = np.array([0.3, angle])
    velocity = np.array([1.2, -0.9])
    length1, length2 = arm.lengths
    mass1, mass2 = arm.masses
    normal1 = np.array([-np.sin(q[0]), np.cos(q[0])])
    normal2 = np.array([-np.sin(sum(q)), np.cos(sum(q))])
    speed1 = length1 / 2 * normal1 * velocity[0]
    speed2 = length1 * normal1 * velocity[0] + length2 / 2 * normal2 * sum(velocity)
    inertia = arm.centroidal_inertias()
    energy = (
        mass1 * speed1 @ speed1
        + mass2 * speed2 @ speed2
        + inertia[0, 2] * velocity[0] ** 2
        + inertia[1, 2] * sum(velocity) ** 2
    ) / 2
    matrix = arm.mass_matrix(q)
    assert velocity @ matrix @ velocity / 2 == pytest.approx(energy, abs=1e-13)
    assert np.linalg.eigvalsh(matrix).min() > 0


def test_gravity_is_potential_gradient(example: Any) -> None:
    arm = example.TwoLinkArm()
    q = np.array([0.3, 0.7])
    step = 1e-6
    gradient = np.array(
        [
            (arm.potential(q + step * direction) - arm.potential(q - step * direction)) / (2 * step)
            for direction in np.eye(2)
        ]
    )
    np.testing.assert_allclose(arm.gravity(q), gradient, atol=1e-9)


def test_dynamic_null_torque_preserves_task_acceleration(example: Any) -> None:
    mass = np.diag([2.0, 1.0])
    jacobian = np.array([[1.0, 1.0]])
    inverse = example.dynamic_inverse(mass, jacobian)
    np.testing.assert_allclose(inverse, [[1 / 3], [2 / 3]])
    projector = np.eye(2) - inverse @ jacobian
    np.testing.assert_allclose(jacobian @ projector, 0, atol=1e-15)
    np.testing.assert_allclose(jacobian @ np.linalg.solve(mass, projector.T), 0, atol=1e-15)
    # A velocity-null vector used as a torque is not acceleration-null.
    assert (jacobian @ np.linalg.solve(mass, [1.0, -1.0]))[0] == pytest.approx(-0.5)


def test_contact_mobility_matches_saddle_point_solution() -> None:
    mass = np.array([[2.0, 0.4, 0.2], [0.4, 1.5, 0.1], [0.2, 0.1, 1.0]])
    constraint = np.array([[1.0, 1.0, 0.0]])
    force = np.array([1.0, 2.0, 3.0])
    inverse = np.linalg.inv(mass)
    mobility = inverse - inverse @ constraint.T @ np.linalg.solve(
        constraint @ inverse @ constraint.T, constraint @ inverse
    )
    saddle = np.block([[mass, -constraint.T], [constraint, np.zeros((1, 1))]])
    acceleration = np.linalg.solve(saddle, np.r_[force, 0.0])[:3]
    np.testing.assert_allclose(mobility @ force, acceleration, atol=1e-14)
    np.testing.assert_allclose(constraint @ mobility, 0, atol=1e-14)


def test_elbow_circle_geometry_and_flexion() -> None:
    length1, length2, distance = 0.3, 0.25, 0.4
    axial = (length1**2 - length2**2 + distance**2) / (2 * distance)
    radius = np.sqrt(length1**2 - axial**2)
    angle = np.linspace(0, 2 * np.pi, 41)
    elbow = np.column_stack((np.full(41, axial), radius * np.cos(angle), radius * np.sin(angle)))
    wrist = np.array([distance, 0, 0])
    np.testing.assert_allclose(np.linalg.norm(elbow, axis=1), length1)
    np.testing.assert_allclose(np.linalg.norm(wrist - elbow, axis=1), length2)
    cosine = np.sum(elbow * (wrist - elbow), axis=1) / (length1 * length2)
    np.testing.assert_allclose(
        cosine, (distance**2 - length1**2 - length2**2) / (2 * length1 * length2)
    )


@pytest.mark.parametrize("values", [(0.0, 0.2), (-0.1, 0.2), (np.nan, 0.2), (0.1,), (0.1, np.inf)])
def test_invalid_segment_dimensions_rejected(example: Any, values: tuple[float, ...]) -> None:
    with pytest.raises(ValueError):
        example.TwoLinkArm(lengths=values)
    with pytest.raises(ValueError):
        example.TwoLinkArm(masses=values)


@pytest.mark.parametrize("radius", [0.0, -0.1, np.nan])
def test_invalid_radius_rejected(example: Any, radius: float) -> None:
    with pytest.raises(ValueError):
        example.TwoLinkArm(radius=radius)


@pytest.mark.parametrize("q", [np.array([1.0]), np.array([np.nan, 0]), np.zeros((2, 1))])
def test_invalid_configuration_rejected(example: Any, q: Any) -> None:
    with pytest.raises(ValueError):
        example.TwoLinkArm().mass_matrix(q)


@pytest.mark.parametrize(
    "mass,jacobian",
    [
        (np.diag([1.0, -1.0]), np.ones((1, 2))),
        (np.array([[1.0, 1.0], [0.0, 1.0]]), np.ones((1, 2))),
        (np.eye(2), np.ones((2, 2))),
        (np.eye(2), np.ones((1, 3))),
        (np.eye(2), np.array([[np.nan, 1.0]])),
        (np.ones((2, 3)), np.ones((1, 2))),
        (np.empty((0, 0)), np.empty((0, 0))),
        (np.eye(2), np.empty((0, 2))),
    ],
)
def test_invalid_dynamic_inverse_rejected(example: Any, mass: Any, jacobian: Any) -> None:
    with pytest.raises(ValueError):
        example.dynamic_inverse(mass, jacobian)


def test_dynamic_inverse_minimizes_kinetic_energy(example: Any) -> None:
    mass = np.array([[3.0, 0.4, 0.1], [0.4, 2.0, 0.2], [0.1, 0.2, 1.0]])
    jacobian = np.array([[1.0, 0.5, 1.0], [0.2, 1.0, 0.0]])
    inverse = example.dynamic_inverse(mass, jacobian)
    speed = np.array([0.4, -0.2])
    minimum = inverse @ speed
    _, _, vectors = np.linalg.svd(jacobian)
    null = vectors[-1]
    np.testing.assert_allclose(jacobian @ minimum, speed, atol=1e-14)
    assert minimum @ mass @ null == pytest.approx(0.0, abs=1e-14)
    for coefficient in (-2.0, -0.3, 0.5, 2.0):
        alternative = minimum + coefficient * null
        assert alternative @ mass @ alternative > minimum @ mass @ minimum


def test_published_urdf_matches_example_and_tree(example: Any) -> None:
    path = Path(__file__).parents[1] / "articles/The_Physics_of_Golf/models/teaching_arm.urdf"
    assert path.read_text(encoding="utf-8") == example.TwoLinkArm().urdf()
    robot = ET.fromstring(path.read_text(encoding="utf-8"))
    assert len(robot.findall("link")) == 3
    assert len(robot.findall("joint")) == 2
    assert {joint.find("child").attrib["link"] for joint in robot.findall("joint")} == {
        "link1",
        "link2",
    }


@pytest.mark.integration
def test_mujoco_import_matches_independent_dynamics(example: Any) -> None:
    mujoco = pytest.importorskip("mujoco")
    arm = example.TwoLinkArm()
    model = mujoco.MjModel.from_xml_string(arm.urdf())
    assert (model.nq, model.nv, model.nu) == (2, 2, 0)
    model.opt.gravity[:] = [0, -9.81, 0]
    data = mujoco.MjData(model)
    data.qpos[:] = [0.3, 0.7]
    mujoco.mj_forward(model, data)
    dense = np.empty((2, 2))
    mujoco.mj_fullM(model, dense, data.qM)
    np.testing.assert_allclose(dense, arm.mass_matrix(data.qpos), atol=1e-12)
    np.testing.assert_allclose(data.qfrc_bias, arm.gravity(data.qpos), atol=1e-12)
    data.qfrc_applied[:] = [1.0, 0.0]
    mujoco.mj_forward(model, data)
    expected = np.linalg.solve(dense, data.qfrc_applied - arm.gravity(data.qpos))
    np.testing.assert_allclose(data.qacc, expected, atol=1e-10)
