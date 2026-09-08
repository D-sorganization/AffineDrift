"""Independent checks of finite-angle, interpolation and delivery claims."""

import re
from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import expm, logm
from scipy.spatial.transform import Rotation, Slerp

from src.affine_control.dynamics import skew

BOOK = Path(__file__).resolve().parents[1] / "articles/The_Geometry_of_Motion"


@pytest.mark.parametrize("web", [False, True], ids=["print", "web"])
def test_published_code_remains_executable_and_checks_the_pose(web: bool) -> None:
    """Execute each actual code block so prose conversion cannot destroy the example."""
    path = BOOK / (
        "quarto/vol0_ch06_exponential_coordinates.qmd"
        if web
        else "Volume_0/chapters/ch06_exponential_coordinates.tex"
    )
    pattern = (
        r"```python\n(.*?)```"
        if web
        else r"\\begin\{lstlisting\}\[[^\]]+\]\n(.*?)\\end\{lstlisting\}"
    )
    blocks = re.findall(pattern, path.read_text(encoding="utf-8"), re.S)
    assert len(blocks) == 1
    namespace: dict = {}
    exec(compile(blocks[0], str(path), "exec"), namespace)
    np.testing.assert_allclose(namespace["pose"][:3, 3], [np.sin(1), 1 - np.cos(1), 0], atol=1e-14)


def test_bch_truncations_have_the_claimed_error_orders() -> None:
    """Halving small amplitudes exposes the omitted quadratic/cubic/quartic terms."""
    first, second = skew(np.array([1.0, 0.2, -0.1])), skew(np.array([-0.3, 1.0, 0.4]))
    bracket = first @ second - second @ first
    cubic = first @ bracket - bracket @ first - second @ bracket + bracket @ second
    errors = []
    for amplitude in (0.08, 0.04):
        exact = logm(expm(amplitude * first) @ expm(amplitude * second))
        linear = amplitude * (first + second)
        quadratic = linear + amplitude**2 * bracket / 2
        third = quadratic + amplitude**3 * cubic / 12
        errors.append([np.linalg.norm(exact - term) for term in (linear, quadratic, third)])
    np.testing.assert_allclose(np.array(errors[0]) / errors[1], [4, 8, 16], rtol=0.03)


def test_quarter_turn_order_reversal_is_a_diagonal_third_turn() -> None:
    """Exact integer matrices fix the order and axis convention independently."""
    first = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
    second = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]])
    relative = second @ first @ (first @ second).T
    expected = 2 * np.pi / (3 * np.sqrt(3)) * np.array([-1, 1, -1])
    np.testing.assert_allclose(Rotation.from_matrix(relative).as_rotvec(), expected, atol=1e-14)


@pytest.mark.parametrize("fraction", [0.0, 0.3, 0.7, 1.0])
def test_matrix_and_quaternion_interpolations_agree_in_both_frames(fraction: float) -> None:
    """Independent Slerp and expm paths have the same angle and spatial/body rate."""
    initial = Rotation.from_euler("xyz", [0.4, -0.5, 0.8]).as_matrix()
    final = Rotation.from_euler("xyz", [-0.7, 0.9, 0.2]).as_matrix()
    body_vector = Rotation.from_matrix(initial.T @ final).as_rotvec()
    body_path = initial @ expm(fraction * skew(body_vector))
    space_path = expm(fraction * skew(initial @ body_vector)) @ initial
    quaternion_path = Slerp([0, 1], Rotation.from_matrix([initial, final]))(fraction).as_matrix()
    np.testing.assert_allclose(body_path, space_path, atol=1e-14)
    np.testing.assert_allclose(body_path, quaternion_path, atol=1e-14)
    distance = Rotation.from_matrix(initial.T @ body_path).magnitude()
    assert distance == pytest.approx(fraction * np.linalg.norm(body_vector), abs=1e-14)


def test_linear_rotation_error_and_chordal_metric() -> None:
    """Check the stated norm and the second-order error coefficient."""
    angle = 0.001
    cross = skew(np.array([0.0, 0.0, 1.0]))
    exact = expm(angle * cross)
    error = np.linalg.norm(exact - np.eye(3) - angle * cross, "fro")
    assert error == pytest.approx(angle**2 / np.sqrt(2), rel=1e-7)
    assert np.linalg.norm(exact - np.eye(3), "fro") ** 2 == pytest.approx(
        8 * np.sin(angle / 2) ** 2
    )


def test_delivery_point_and_normal_sensitivity() -> None:
    """Finite-difference material geometry verifies the spatial perturbation sign."""
    rotation = Rotation.from_euler("xyz", [0.4, -0.7, 0.1]).as_matrix()
    offset, normal_body = np.array([0.1, 0.2, -1.1]), np.array([1.0, 0.0, 0.0])
    delta_rotation, delta_translation = np.array([0.3, -0.2, 0.1]), np.array([0.2, 0.4, -0.1])
    step = 1e-6
    plus = expm(step * skew(delta_rotation)) @ rotation
    minus = expm(-step * skew(delta_rotation)) @ rotation
    point_derivative = (plus @ offset - minus @ offset) / (2 * step) + delta_translation
    normal_derivative = (plus @ normal_body - minus @ normal_body) / (2 * step)
    np.testing.assert_allclose(
        point_derivative, delta_translation - skew(rotation @ offset) @ delta_rotation, atol=1e-10
    )
    np.testing.assert_allclose(
        normal_derivative, -skew(rotation @ normal_body) @ delta_rotation, atol=1e-10
    )
