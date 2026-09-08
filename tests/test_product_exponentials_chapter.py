"""Check the published 3R example against independent link geometry."""

import ast
import re
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from scipy.linalg import expm, logm
from scipy.spatial.transform import Rotation

CHAPTER = (
    Path(__file__).resolve().parents[1]
    / "articles/The_Geometry_of_Motion/Volume_0/chapters/ch09_product_of_exponentials.tex"
)


def _robot() -> Any:
    """Execute only the locally authored class, excluding demonstration commands."""
    source = CHAPTER.read_text(encoding="utf-8")
    match = re.search(r"\\begin\{lstlisting\}[^\n]*\n(.*?)\\end\{lstlisting\}", source, re.S)
    assert match is not None
    parsed = ast.parse(match.group(1))
    classes = [node for node in parsed.body if isinstance(node, ast.ClassDef)]
    assert len(classes) == 1
    namespace: dict[str, Any] = {"np": np, "expm": expm}
    exec(
        compile(ast.Module(body=classes, type_ignores=[]), str(CHAPTER), "exec"), namespace
    )  # nosec B102
    return namespace["SpatialRobot3R"]()


def _link_geometry(q: np.ndarray) -> np.ndarray:
    """Compose rotations and link offsets directly, without screw exponentials."""
    rz = Rotation.from_rotvec([0, 0, q[0]]).as_matrix()
    ry = Rotation.from_rotvec([0, q[1], 0]).as_matrix()
    rx = Rotation.from_rotvec([q[2], 0, 0]).as_matrix()
    result = np.eye(4)
    result[:3, :3] = rz @ ry @ rx
    result[:3, 3] = rz @ (np.array([0.5, 0, 0]) + ry @ np.array([0.5, 0, 0]))
    return result


@pytest.mark.parametrize("q", [np.array([0.7, 0.4, -0.9]), np.array([-0.3, 0.8, 0.2])])
def test_published_forward_kinematics_matches_link_geometry(q: np.ndarray) -> None:
    np.testing.assert_allclose(_robot().forward_kinematics(q), _link_geometry(q), atol=1e-12)


def test_spatial_jacobian_uses_angular_then_linear_order() -> None:
    """At home each column is the known axis velocity, including its moment."""
    expected = np.array([[0, 0, 1], [0, 1, 0], [1, 0, 0], [0, 0, 0], [0, 0, 0.0], [0, 0.5, 0]])
    np.testing.assert_allclose(_robot().spatial_jacobian(np.zeros(3)), expected, atol=1e-8)


def test_spatial_jacobian_predicts_point_velocity() -> None:
    """The spatial linear component is not itself the tool-origin velocity."""
    q = np.array([0.7, 0.4, -0.9])
    rates = np.array([0.8, -0.3, 0.5])
    h = 1e-6
    expected = (_link_geometry(q + h * rates) - _link_geometry(q - h * rates)) / (2 * h)
    twist = _robot().spatial_jacobian(q) @ rates
    position = _link_geometry(q)[:3, 3]
    predicted = np.cross(twist[:3], position) + twist[3:]
    np.testing.assert_allclose(predicted, expected[:3, 3], atol=1e-8)


def _vee(generator: np.ndarray) -> np.ndarray:
    rotation = (generator[:3, :3] - generator[:3, :3].T) / 2
    return np.r_[rotation[2, 1], rotation[0, 2], rotation[1, 0], generator[:3, 3]]


def test_spatial_columns_match_independent_pose_derivatives() -> None:
    q = np.array([0.6, -0.35, 0.8])
    inverse = np.linalg.inv(_link_geometry(q))
    step = 1e-6 * np.eye(3)
    expected = np.column_stack(
        [_vee((_link_geometry(q + dq) - _link_geometry(q - dq)) @ inverse / 2e-6) for dq in step]
    )
    np.testing.assert_allclose(_robot().spatial_jacobian(q), expected, atol=1e-9)


def test_home_tool_conversion_retains_body_product_order() -> None:
    robot = _robot()
    q = np.array([0.6, -0.35, 0.8])
    inverse_home = np.linalg.inv(robot.M)
    factors = [
        expm(inverse_home @ robot.screw_to_matrix(axis) @ robot.M * angle)
        for axis, angle in zip(robot.axes, q, strict=True)
    ]
    body_pose = robot.M @ factors[0] @ factors[1] @ factors[2]
    np.testing.assert_allclose(body_pose, _link_geometry(q), atol=1e-12)
    reversed_pose = robot.M @ factors[2] @ factors[1] @ factors[0]
    assert np.linalg.norm(reversed_pose - body_pose) > 0.1


def test_reported_spatial_example_pose() -> None:
    reported = np.array(
        [
            [0.612372, -0.659740, -0.435596, 0.659740],
            [0.612372, 0.047367, 0.789149, 0.659740],
            [-0.5, -0.75, 0.433013, -0.25],
            [0, 0, 0, 1],
        ]
    )
    actual = _robot().forward_kinematics(np.array([np.pi / 4, np.pi / 6, -np.pi / 3]))
    np.testing.assert_allclose(actual, reported, atol=5e-7, rtol=0)


def test_planar_standard_dh_includes_terminal_link() -> None:
    lengths = [1.0, 0.8, 0.6]
    q = np.deg2rad([45, -30, 60])
    dh_pose = np.eye(4)
    for length, angle in zip(lengths, q, strict=True):
        factor = np.eye(4)
        factor[:3, :3] = Rotation.from_rotvec([0, 0, angle]).as_matrix()
        factor[:3, 3] = factor[:3, :3] @ np.array([length, 0, 0])
        dh_pose = dh_pose @ factor
    np.testing.assert_allclose(dh_pose[:3, 3], [1.635139, 1.493718, 0], atol=5e-7, rtol=0)
    np.testing.assert_allclose(
        dh_pose[:3, :3], Rotation.from_rotvec([0, 0, np.deg2rad(75)]).as_matrix(), atol=1e-12
    )


def _planar_position_jacobian(q: np.ndarray, lengths: np.ndarray) -> np.ndarray:
    angles = np.cumsum(q)
    endpoint_derivatives = lengths * np.array([-np.sin(angles), np.cos(angles)])
    return np.cumsum(endpoint_derivatives[:, ::-1], axis=1)[:, ::-1]


@pytest.mark.parametrize("elbow", [0.0, np.pi])
def test_position_singularity_does_not_imply_pose_rank_loss(elbow: float) -> None:
    q = np.array([0.7, elbow])
    jp = _planar_position_jacobian(q, np.array([1.5, 1.0]))
    pose_jacobian = np.vstack([jp, [1, 1]])
    assert np.linalg.matrix_rank(jp) == 1
    assert np.linalg.matrix_rank(pose_jacobian) == 2


@pytest.mark.parametrize(
    ("elbow", "singular_values"),
    [(np.pi / 4, [2.07313218, 0.34108138]), (0.1, [2.23338537, 0.04470049])],
)
def test_ellipse_numbers_and_static_force_duality(
    elbow: float, singular_values: list[float]
) -> None:
    jacobian = _planar_position_jacobian(np.array([0, elbow]), np.ones(2))
    directions, values, _ = np.linalg.svd(jacobian)
    np.testing.assert_allclose(values, singular_values, atol=5e-9, rtol=0)
    np.testing.assert_allclose(np.prod(values), np.sin(elbow), atol=1e-12)
    # Each reciprocal velocity semiaxis consumes one unit of joint torque.
    for direction, value in zip(directions.T, values, strict=True):
        np.testing.assert_allclose(np.linalg.norm(jacobian.T @ (direction / value)), 1.0)


def test_null_step_preserves_only_the_first_order_task() -> None:
    q = np.array([0.4, -0.7, 0.9])
    lengths = np.array([1.0, 0.8, 0.6])
    jacobian = _planar_position_jacobian(q, lengths)
    null = np.linalg.svd(jacobian, full_matrices=True)[2][-1]

    def position(coordinates: np.ndarray) -> np.ndarray:
        angles = np.cumsum(coordinates)
        return (lengths * np.array([np.cos(angles), np.sin(angles)])).sum(axis=1)

    np.testing.assert_allclose(jacobian @ null, 0, atol=1e-14)
    drift = np.linalg.norm(position(q + 0.02 * null) - position(q))
    half_drift = np.linalg.norm(position(q + 0.01 * null) - position(q))
    assert drift > 1e-6
    assert 3.9 < drift / half_drift < 4.1


def test_body_log_error_differential_includes_logarithm_factor() -> None:
    robot = _robot()
    q = np.array([0.5, -0.2, 0.4])
    desired = _link_geometry(np.array([-0.2, 0.6, -0.3]))
    current = _link_geometry(q)
    error_transform = np.linalg.solve(current, desired)
    step = 1e-6
    direction = np.array([0.3, -0.4, 0.2])
    body_generator = np.linalg.solve(
        current, robot.screw_to_matrix(robot.spatial_jacobian(q) @ direction) @ current
    )
    # Differentiate log(exp(-h V_b) E), without replacing d log by identity.
    predicted = _vee(
        (
            logm(expm(-step * body_generator) @ error_transform)
            - logm(expm(step * body_generator) @ error_transform)
        )
        / (2 * step)
    )
    actual = _vee(
        (
            logm(np.linalg.solve(_link_geometry(q + step * direction), desired))
            - logm(np.linalg.solve(_link_geometry(q - step * direction), desired))
        )
        / (2 * step)
    )
    np.testing.assert_allclose(predicted, actual, atol=1e-8)
    assert np.linalg.norm(actual + _vee(body_generator)) > 0.01


@pytest.mark.parametrize("coordinates", [np.zeros(2), np.array([0, np.inf, 0])])
def test_published_example_rejects_invalid_joint_coordinates(coordinates: np.ndarray) -> None:
    with pytest.raises(ValueError, match="three finite"):
        _robot().forward_kinematics(coordinates)


def test_web_edition_preserves_executable_example_and_unbroken_math_blocks() -> None:
    web = (CHAPTER.parents[2] / "quarto/vol0_ch09_product_of_exponentials.qmd").read_text(
        encoding="utf-8"
    )
    tex = CHAPTER.read_text(encoding="utf-8")
    web_program = re.search(r"```python\n(.*?)```", web, re.S)
    tex_program = re.search(r"\\begin\{lstlisting\}[^\n]*\n(.*?)\\end\{lstlisting\}", tex, re.S)
    assert web_program is not None and tex_program is not None
    assert web_program[1].strip() == tex_program[1].strip()
    equations = re.findall(r"\$\$(.*?)\$\$", web, re.S)
    assert len(equations) == tex.count(r"\begin{equation}")
    assert all(not re.search(r"\n\s*\n", equation) for equation in equations)
