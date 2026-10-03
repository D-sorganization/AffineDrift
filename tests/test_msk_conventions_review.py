"""Tests reviewing musculoskeletal conventions and spatial inertia from chapter 2."""

import re
from collections.abc import Callable
from pathlib import Path
from typing import cast

import numpy as np
import pytest
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

from src.affine_control.dynamics import spatial_inertia

Array = NDArray[np.float64]
JointAngles = Callable[[Array, Array], tuple[float, float, float]]

CHAPTER_REL_PATH = Path(
    "articles/The_Geometry_of_Motion/Volume_III/chapters/ch02_musculoskeletal_conventions.tex"
)


def _load_chapter_text() -> str:
    """Read chapter LaTeX source from repository root or active parent worktree."""
    return (Path(__file__).resolve().parents[1] / CHAPTER_REL_PATH).read_text(encoding="utf-8")


def _extract_and_exec_joint_fn() -> JointAngles:
    """Extract first lstlisting with def, exec in clean namespace, and return angle fn."""
    text = _load_chapter_text()
    pattern = re.compile(r"\\begin\{lstlisting\}(?:\[.*?\])?(.*?)\\end\{lstlisting\}", re.DOTALL)
    for match in pattern.finditer(text):
        code = match.group(1)
        if "def " in code:
            ns: dict[str, object] = {}
            exec(code, ns)
            for name in ("segment_zxy_angles", "grood_suntay_knee_angles"):
                if name in ns and callable(ns[name]):
                    return cast(JointAngles, ns[name])
            raise KeyError("Neither segment_zxy_angles nor grood_suntay_knee_angles found in code")
    raise ValueError("No lstlisting containing 'def ' found in chapter source")


def _eval_inertia_cell(
    cell: str,
    mass: float,
    com: Array,
    origin_inertia: Array,
) -> Array:
    """Evaluate single 3x3 block from supported spatial inertia LaTeX expressions."""
    cleaned = re.sub(r"\s+", "", cell)
    if cleaned in ("I_i", "I_{i}"):
        return origin_inertia
    if cleaned in ("m_i\\mathbb{I}_3", "m_i\\mathbb{I}_{3}"):
        return mass * np.eye(3)
    if cleaned in ("m_i[\\bm{c}_i]_\\times", "m_i[\\bm{c}_i]_{times}", "m_i[\\bm{c}_i]_{\\times}"):
        cx, cy, cz = com
        c_cross = np.array([[0.0, -cz, cy], [cz, 0.0, -cx], [-cy, cx, 0.0]])
        return mass * c_cross
    if cleaned in (
        "m_i[\\bm{c}_i]_\\times^T",
        "m_i[\\bm{c}_i]_{times}^T",
        "m_i[\\bm{c}_i]_{\\times}^T",
    ):
        cx, cy, cz = com
        c_cross = np.array([[0.0, -cz, cy], [cz, 0.0, -cx], [-cy, cx, 0.0]])
        return mass * c_cross.T
    raise ValueError(f"Unsupported LaTeX spatial inertia cell: {cell!r}")


def _extract_and_eval_printed_inertia(mass: float, com: Array, origin_inertia: Array) -> Array:
    """Parse exact bmatrix immediately preceding eq:ch2:spatial-inertia and construct 6x6."""
    text = _load_chapter_text()
    equation = text.split(r"\label{eq:ch2:spatial-inertia}", 1)[0].rsplit(r"\begin{equation}", 1)[1]
    match = re.search(r"\\begin\{bmatrix\}(.*?)\\end\{bmatrix\}", equation, re.DOTALL)
    if not match:
        raise ValueError("Could not locate bmatrix preceding eq:ch2:spatial-inertia")

    rows = [r.strip() for r in match.group(1).strip().split(r"\\") if r.strip()]
    if len(rows) != 2:
        raise ValueError(f"Expected 2 matrix rows, got {len(rows)}")

    cells: list[list[Array]] = []
    for row in rows:
        parts = [c.strip() for c in row.split("&")]
        if len(parts) != 2:
            raise ValueError(f"Expected 2 cells per row, got {len(parts)} in row {row!r}")
        cells.append([_eval_inertia_cell(c, mass, com, origin_inertia) for c in parts])

    return np.block(cells)


@pytest.mark.parametrize(
    ("z_deg", "x_deg", "y_deg"),
    [(60.0, 5.0, 10.0), (-30.0, -20.0, 40.0), (120.0, 30.0, -150.0)],
)
def test_segment_zxy_angles_reconstruction(z_deg: float, x_deg: float, y_deg: float) -> None:
    """Validate extracted angle function matches scipy Rotation.from_euler uppercase ZXY."""
    angle_fn = _extract_and_exec_joint_fn()
    expected = (z_deg, x_deg, y_deg)
    r_rel = Rotation.from_euler("ZXY", expected, degrees=True).as_matrix()

    r_femur = Rotation.identity().as_matrix()
    r_tibia = r_femur @ r_rel
    computed = angle_fn(r_femur, r_tibia)
    np.testing.assert_allclose(computed, expected, atol=1e-6)

    # Invariance under arbitrary common global rotation
    r_rand = Rotation.from_euler("xyz", [17.0, -42.0, 68.0], degrees=True).as_matrix()
    computed_rotated = angle_fn(r_rand @ r_femur, r_rand @ r_tibia)
    np.testing.assert_allclose(computed_rotated, expected, atol=1e-6)


@pytest.mark.parametrize("singular_x_deg", [90.0, -90.0, 90.0 - 1e-9, -90.0 + 1e-9])
def test_segment_zxy_angles_singularities(singular_x_deg: float) -> None:
    """Singular middle angle (+/-90 deg) must trigger ValueError."""
    angle_fn = _extract_and_exec_joint_fn()
    r_rel = Rotation.from_euler("ZXY", [15.0, singular_x_deg, 30.0], degrees=True).as_matrix()
    with pytest.raises(ValueError):
        angle_fn(np.eye(3), r_rel)


@pytest.mark.parametrize(
    "invalid_frame",
    [
        np.diag([1.0, 1.0, -1.0]),  # reflected
        np.eye(3) * 2.0,  # scaled
        np.array([[np.nan, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]),  # non-finite
        np.zeros((3, 3)),  # zero
        np.eye(2),  # wrong shape
        np.full((3, 3), np.inf),
        np.eye(3, dtype=complex) * 1j,
    ],
)
def test_segment_zxy_angles_invalid_frames(invalid_frame: Array) -> None:
    """Invalid, reflected, scaled, or non-finite frames must raise ValueError."""
    angle_fn = _extract_and_exec_joint_fn()
    with pytest.raises(ValueError):
        angle_fn(invalid_frame, np.eye(3))
    with pytest.raises(ValueError):
        angle_fn(np.eye(3), invalid_frame)


def test_spatial_inertia_symbolic_and_energy_consistency() -> None:
    """Validate printed inertia extraction, kinetic energy equivalence, and affine_control."""
    mass = 2.0
    com = np.array([0.1, 0.2, -0.1], dtype=float)
    i_c = np.diag([0.03, 0.04, 0.05])
    omega = np.array([1.0, -2.0, 3.0], dtype=float)
    v_o = np.array([0.3, -0.2, 0.4], dtype=float)

    i_origin = i_c + mass * (float(np.dot(com, com)) * np.eye(3) - np.outer(com, com))
    g_printed = _extract_and_eval_printed_inertia(mass, com, i_origin)
    g_canonical = np.asarray(spatial_inertia(mass, com, i_c))

    v_c = v_o + np.cross(omega, com)
    kinetic_energy_direct = 0.5 * float(omega @ i_c @ omega) + 0.5 * mass * float(np.dot(v_c, v_c))
    spatial_twist = np.concatenate([omega, v_o])
    kinetic_energy_matrix = 0.5 * float(spatial_twist @ g_printed @ spatial_twist)

    assert abs(float(v_o @ np.cross(omega, com))) > 0.01
    np.testing.assert_allclose(kinetic_energy_matrix, kinetic_energy_direct, atol=1e-12)
    np.testing.assert_allclose(g_printed, g_canonical, atol=1e-12)


def test_printed_inertia_matches_point_momenta_and_origin_transport() -> None:
    """Independent point velocities expose cross-block sign and origin mistakes."""
    points = np.array([[0.2, 0.0, 0.1], [0.0, 0.4, -0.1], [-0.1, 0.1, 0.3]])
    masses = np.array([0.7, 1.1, 0.5])
    mass = float(masses.sum())
    com = masses @ points / mass
    origin_inertia = sum(
        m * ((point @ point) * np.eye(3) - np.outer(point, point))
        for m, point in zip(masses, points, strict=True)
    )
    omega, velocity = np.array([1.0, -2.0, 3.0]), np.array([0.3, -0.2, 0.4])
    point_velocities = velocity + np.cross(omega, points)
    momenta = masses[:, None] * point_velocities
    direct_momentum = np.concatenate([np.cross(points, momenta).sum(axis=0), momenta.sum(axis=0)])
    inertia = _extract_and_eval_printed_inertia(mass, com, np.asarray(origin_inertia))
    twist = np.concatenate([omega, velocity])
    np.testing.assert_allclose(inertia @ twist, direct_momentum, atol=1e-12)
    direct_energy = 0.5 * float(np.sum(masses * np.sum(point_velocities**2, axis=1)))
    assert float(twist @ inertia @ twist) / 2 == pytest.approx(direct_energy)

    offset = np.array([0.15, -0.07, 0.05])
    shifted_points = points - offset
    shifted_inertia = sum(
        m * ((point @ point) * np.eye(3) - np.outer(point, point))
        for m, point in zip(masses, shifted_points, strict=True)
    )
    shifted = _extract_and_eval_printed_inertia(mass, com - offset, np.asarray(shifted_inertia))
    shifted_twist = np.concatenate([omega, velocity + np.cross(omega, offset)])
    assert float(shifted_twist @ shifted @ shifted_twist) / 2 == pytest.approx(direct_energy)
