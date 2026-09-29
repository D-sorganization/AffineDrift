"""Independent mathematical checks for the Volume I reference appendices (#4469)."""

import re
import runpy
from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray
from scipy.linalg import eig, expm
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "articles/The_Geometry_of_Motion/Volume_I/main.tex"


def _hat(vector: NDArray[np.float64]) -> NDArray[np.float64]:
    x, y, z = vector
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])


@pytest.mark.parametrize("angle", [0.0, 1e-9, 0.7, np.pi])
def test_rotation_vector_exponential_and_branch_safe_roundtrip(angle: float) -> None:
    axis = np.array([2.0, -1.0, 3.0]) / np.sqrt(14.0)
    vector = angle * axis
    skew = _hat(vector)
    # sinc-based coefficients include the removable zero-angle limits.
    matrix = np.eye(3) + np.sinc(angle / np.pi) * skew
    matrix += 0.5 * np.sinc(angle / (2 * np.pi)) ** 2 * skew @ skew
    assert matrix == pytest.approx(expm(skew), abs=1e-14)
    recovered = Rotation.from_matrix(matrix).as_rotvec()
    assert expm(_hat(recovered)) == pytest.approx(matrix, abs=1e-14)
    if angle < np.pi:
        assert recovered == pytest.approx(vector, abs=1e-14)
    else:
        assert np.linalg.norm(recovered) == pytest.approx(np.pi)


def test_nominal_input_enters_the_state_jacobian() -> None:
    step = 1e-6
    state, command = 1.0, 2.0
    derivative = (-1 + command) * (state + step) - (-1 + command) * (state - step)
    derivative /= 2 * step
    assert derivative == pytest.approx(1.0)
    assert derivative != pytest.approx(-1.0)  # Drift-only derivative reverses stability.


def test_twists_and_wrenches_use_dual_frame_maps() -> None:
    rotation = Rotation.from_rotvec([0.2, -0.3, 0.4]).as_matrix()
    offset = np.array([0.1, 0.3, -0.2])
    adjoint = np.block([[rotation, np.zeros((3, 3))], [_hat(offset) @ rotation, rotation]])
    twist = np.array([1.0, 2.0, -1.0, 0.3, -0.2, 0.5])
    wrench = np.array([0.2, -0.1, 0.3, 2.0, -4.0, 1.0])
    transformed = np.linalg.solve(adjoint.T, wrench)
    direct = np.r_[
        rotation @ wrench[:3] + np.cross(offset, rotation @ wrench[3:]), rotation @ wrench[3:]
    ]
    assert transformed == pytest.approx(direct)
    assert transformed @ (adjoint @ twist) == pytest.approx(wrench @ twist)
    assert (adjoint @ wrench) @ (adjoint @ twist) != pytest.approx(wrench @ twist)


def test_flat_geometry_does_not_determine_flow_stability() -> None:
    vector = np.array([1.0, 0.0])
    transition = expm(np.diag([2.0, -1.0]) * 0.5)
    assert np.linalg.norm(transition @ vector) == pytest.approx(np.e)
    assert np.linalg.norm(vector) == 1.0  # Euclidean parallel transport preserves norm.


def test_ltv_order_matters_but_endpoint_equality_does_not_imply_commutation() -> None:
    first = np.array([[0.0, 1.0], [0.0, 0.0]])
    second = first.T
    assert not np.allclose(first @ second, second @ first)
    assert not np.allclose(expm(second) @ expm(first), expm(first + second))
    # Four unit intervals: A, B, -B, -A. The reversals cancel exactly.
    loop = expm(-first) @ expm(-second) @ expm(second) @ expm(first)
    assert loop == pytest.approx(np.eye(2))
    assert expm(first + second - second - first) == pytest.approx(loop)


def test_mass_metric_singular_values_survive_coordinate_rescaling() -> None:
    transition = np.array([[1.0, 2.0], [0.0, 1.0]])
    scale = np.diag([1000.0, 1.0])
    changed = np.linalg.solve(scale, transition @ scale)
    assert np.linalg.norm(changed, 2) != pytest.approx(np.linalg.norm(transition, 2))
    # G_z = scale.T @ scale; its square root restores the original physical norm.
    weighted = scale @ changed @ np.linalg.inv(scale)
    assert np.linalg.svd(weighted, compute_uv=False) == pytest.approx(
        np.linalg.svd(transition, compute_uv=False)
    )


def test_column_vectorization_matches_lyapunov_operator() -> None:
    matrix = np.array([[-1.0, 2.0], [0.0, -3.0]])
    metric = np.array([[2.0, 0.3], [0.3, 1.0]])
    operator = np.kron(np.eye(2), matrix.T) + np.kron(matrix.T, np.eye(2))
    direct = matrix.T @ metric + metric @ matrix
    assert operator @ metric.ravel(order="F") == pytest.approx(direct.ravel(order="F"))


def test_schur_complement_preserves_block_quadratic_form() -> None:
    coupling, lower = 0.8, 2.0
    schur = 0.3
    upper = schur + coupling**2 / lower
    block = np.array([[upper, coupling], [coupling, lower]])
    x, y = 0.4, -0.7
    assert np.array([x, y]) @ block @ np.array([x, y]) == pytest.approx(
        schur * x**2 + lower * (y + coupling * x / lower) ** 2
    )
    assert np.linalg.eigvalsh(block).min() > 0


def test_regular_descriptor_pencil_can_have_an_infinite_eigenvalue() -> None:
    pairs = eig(np.eye(2), np.diag([1.0, 0.0]), homogeneous_eigvals=True, right=False)
    assert np.count_nonzero(np.isclose(pairs[1], 0)) == 1
    finite = np.flatnonzero(~np.isclose(pairs[1], 0))
    assert pairs[0, finite] / pairs[1, finite] == pytest.approx([1.0])


def test_pseudospectrum_contains_spectrum_and_nonnormal_sensitivity() -> None:
    matrix = np.array([[0.0, 10.0], [0.0, 0.0]])
    assert np.linalg.svd(matrix, compute_uv=False)[-1] == 0.0
    shifted = 0.1 * np.eye(2) - matrix
    assert np.linalg.svd(shifted, compute_uv=False)[-1] < 0.0011
    perturbed = matrix + np.array([[0.0, 0.0], [0.001, 0.0]])
    assert np.sort(np.linalg.eigvals(perturbed)) == pytest.approx([-0.1, 0.1])


@pytest.mark.parametrize("index", [0, 1])
def test_published_python_examples_execute_and_verify_results(tmp_path: Path, index: int) -> None:
    text = SOURCE.read_text(encoding="utf-8")
    snippets = re.findall(
        r"\\begin\{lstlisting\}\[language=Python\]\s*(.*?)\\end\{lstlisting\}", text, re.S
    )
    example = tmp_path / "reference_example.py"
    example.write_text(snippets[index], encoding="utf-8")
    values = runpy.run_path(str(example))
    if index == 0:
        assert values["w_recovered"] == pytest.approx(values["w"])
    else:
        assert values["info"] == 0
        assert values["x"] == pytest.approx([1.0, 2.0, 3.0])
        assert np.linalg.norm(values["A"] @ values["x"] - values["b"]) < 1e-10


@pytest.mark.parametrize(
    "obsolete",
    [
        "State Jacobian $\\partial f/\\partial x$",
        "Adjoint operators transport twists and wrenches across frames",
        "is the right way to carry perturbations",
        "Equality holds only when",
        "Tools like cvxpy and SciPy can solve LMI",
        "w_hat = logm(R).real",
    ],
)
def test_reference_removes_identified_false_generalizations(obsolete: str) -> None:
    assert obsolete not in SOURCE.read_text(encoding="utf-8")
