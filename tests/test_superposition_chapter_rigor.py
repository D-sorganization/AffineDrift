"""Independent physical checks of the paired superposition chapter examples."""

import re
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles/The_Geometry_of_Motion/quarto/ch03_superposition.qmd"
PRINT = ROOT / "articles/The_Geometry_of_Motion/Volume_I/chapters/ch03_superposition.tex"
LENGTHS = np.array([0.8, 0.6])
MASSES = np.array([1.4, 0.5])
GRAVITY_M_S2 = 9.81


@pytest.fixture(scope="module")
def example() -> dict[str, Any]:
    """Run exactly the standalone example available to a reader."""
    text = ARTICLE.read_text(encoding="utf-8")
    block = re.search(r"```python\n(# Superposition chapter example\n.*?)\n```", text, re.S)
    assert block is not None, "Publish the reproducible chapter example"
    code = block.group(1)
    assert code in PRINT.read_text(encoding="utf-8"), "Keep print and web examples identical"
    namespace: dict[str, Any] = {}
    exec(compile(code, str(ARTICLE), "exec"), namespace)
    return namespace


def centers(q: np.ndarray) -> np.ndarray:
    """Locate uniform-rod centers using independent planar geometry."""
    angles = np.cumsum(q)
    rods = LENGTHS[:, None] * np.column_stack((np.cos(angles), np.sin(angles)))
    return np.array([rods[0] / 2, rods[0] + rods[1] / 2])


def cross2(a: np.ndarray, b: np.ndarray) -> float:
    """Return the signed planar moment."""
    return float(a[0] * b[1] - a[1] * b[0])


@pytest.mark.parametrize("q", [[0.4, -0.7], [0.0, 0.0], [0.2, np.pi]])
def test_uniform_rod_inertia_from_cartesian_energy(example: dict[str, Any], q: list[float]) -> None:
    state = np.array(q)
    velocity = np.array([2.1, -0.8])
    mass, _, _ = example["rod_arm"](state, velocity, LENGTHS, MASSES)
    step = 1e-5
    jac = np.stack(
        [(centers(state + step * e) - centers(state - step * e)) / (2 * step) for e in np.eye(2)],
        axis=-1,
    )
    omega_map = np.tril(np.ones((2, 2)))
    inertias = MASSES * LENGTHS**2 / 12
    expected = sum(MASSES[i] * jac[i].T @ jac[i] for i in range(2))
    expected += omega_map.T @ np.diag(inertias) @ omega_map
    np.testing.assert_allclose(mass, expected, atol=1e-10)
    assert np.linalg.eigvalsh(mass).min() > 0


@pytest.mark.parametrize("torque", [[0.0, 0.0], [2.0, -0.3], [-4.0, 1.2]])
def test_body_force_moments_recover_generalized_effort(
    example: dict[str, Any], torque: list[float]
) -> None:
    q = np.array([0.4, -0.7])
    v = np.array([2.1, -0.8])
    mass, c, gravity = example["rod_arm"](q, v, LENGTHS, MASSES)
    acceleration = np.linalg.solve(mass, np.array(torque) - c - gravity)
    step = 2e-5
    jac = np.stack(
        [(centers(q + step * e) - centers(q - step * e)) / (2 * step) for e in np.eye(2)], axis=-1
    )
    bias = (centers(q + step * v) - 2 * centers(q) + centers(q - step * v)) / step**2
    com_acceleration = jac @ acceleration + bias
    force12 = MASSES[1] * (com_acceleration[1] - np.array([0.0, -GRAVITY_M_S2]))
    force01 = MASSES[0] * (com_acceleration[0] - np.array([0.0, -GRAVITY_M_S2])) + force12
    points = centers(q)
    rho1 = points[0]
    rho2 = points[1] - 2 * rho1
    inertias = MASSES * LENGTHS**2 / 12
    distal = inertias[1] * acceleration.sum() + cross2(rho2, force12)
    proximal = inertias[0] * acceleration[0] + distal
    proximal += cross2(rho1, force01) + cross2(rho1, force12)
    np.testing.assert_allclose([proximal, distal], torque, atol=2e-6)


def test_velocity_products_cancel_mass_rate_power(example: dict[str, Any]) -> None:
    q = np.array([0.4, -0.7])
    v = np.array([2.1, -0.8])
    _, c, gravity = example["rod_arm"](q, v, LENGTHS, MASSES)
    step = 1e-6
    plus = example["rod_arm"](q + step * v, v, LENGTHS, MASSES)[0]
    minus = example["rod_arm"](q - step * v, v, LENGTHS, MASSES)[0]
    assert v @ c == pytest.approx(0.5 * v @ ((plus - minus) / (2 * step)) @ v, abs=1e-9)
    potential_rate = (
        GRAVITY_M_S2
        * MASSES
        @ (centers(q + step * v)[:, 1] - centers(q - step * v)[:, 1])
        / (2 * step)
    )
    assert v @ gravity == pytest.approx(potential_rate, abs=1e-8)
    assert abs(v @ c) > 0.1  # Velocity-product power is not generally zero.


@pytest.mark.parametrize("torque", [5.0, -5.0, 2.5, 7.5])
def test_pendulum_trace_against_independent_solver_and_work_energy(
    example: dict[str, Any], torque: float
) -> None:
    times = np.array([0.0, 0.25, 0.5, 1.0, 1.5, 2.0])
    coarse = example["pendulum_trace"](torque, times, max_step=0.001)
    fine = example["pendulum_trace"](torque, times, max_step=0.0005)

    def rhs(_time: float, state: np.ndarray) -> list[float]:
        return [state[1], torque - GRAVITY_M_S2 * np.sin(state[0])]

    reference = solve_ivp(
        rhs, (0, 2), [0, 0], method="DOP853", t_eval=times, rtol=1e-12, atol=1e-13
    )
    assert reference.success
    np.testing.assert_allclose(coarse[:, :2], reference.y.T, atol=2e-10, rtol=0)
    np.testing.assert_allclose(coarse, fine, atol=2e-10, rtol=0)
    q, v, a = coarse.T
    np.testing.assert_allclose(a, torque - GRAVITY_M_S2 * np.sin(q), atol=1e-12)
    np.testing.assert_allclose(
        0.5 * v**2 + GRAVITY_M_S2 * (1 - np.cos(q)) - torque * q, 0, atol=2e-10
    )


def test_symmetric_exception_and_nonsymmetric_trajectory_defect(example: dict[str, Any]) -> None:
    times = np.array([0.0, 0.5, 1.0, 2.0])
    traces = {u: example["pendulum_trace"](u, times) for u in [0, 2.5, 5, -5, 7.5]}
    np.testing.assert_allclose(traces[5], -traces[-5], atol=1e-12)
    defect = traces[7.5] - traces[5] - traces[2.5] + traces[0]
    assert abs(defect[-1, 0]) > 1
    # At one shared state the affine identity remains exact.
    baseline = -GRAVITY_M_S2 * np.sin(0.5)
    assert (baseline + 7.5) == pytest.approx((baseline + 5) + (baseline + 2.5) - baseline)


def test_passivity_does_not_imply_contraction_or_bounded_motion() -> None:
    upright_jacobian = np.array([[0.0, 1.0], [GRAVITY_M_S2, -0.4]])
    assert np.linalg.eigvals(upright_jacobian).max() > 0
    amplitude = np.array([0.1, 0.01, 0.001])
    storage = amplitude**4 / 4
    decay = amplitude**6
    np.testing.assert_allclose(decay / storage, 4 * amplitude**2)
    # Unit mass, constant unit force: a passive lossless port still admits unbounded energy.
    time = np.array([1.0, 10.0, 100.0])
    energy = time**2 / 2
    work = time**2 / 2
    np.testing.assert_allclose(energy, work)
    assert energy[-1] > 1000 * energy[0]


@pytest.mark.parametrize("path", [ARTICLE, PRINT])
def test_published_tables_match_the_reproducible_trajectories(
    example: dict[str, Any], path: Path
) -> None:
    text = path.read_text(encoding="utf-8")
    if path == ARTICLE:
        rows = [
            line.strip(" |").split(" | ")
            for line in text.splitlines()
            if re.match(r"\| \d\.\d\d \|", line)
        ]
    else:
        rows = [
            line.rstrip(" \\").split(" & ")
            for line in text.splitlines()
            if re.match(r"\d\.\d\d &", line)
        ]
    assert len(rows) == 12
    state_rows = np.array(rows[:6], dtype=float)
    defect_rows = np.array(rows[6:], dtype=float)
    times = state_rows[:, 0]
    traces = {u: example["pendulum_trace"](u, times) for u in (0, 2.5, 5, 7.5)}
    np.testing.assert_allclose(state_rows[:, 1:], traces[5], atol=5.01e-7, rtol=0)
    expected = np.column_stack(
        [
            traces[5][:, 0],
            traces[2.5][:, 0],
            traces[7.5][:, 0],
            (traces[7.5] - traces[5] - traces[2.5] + traces[0])[:, 0],
        ]
    )
    np.testing.assert_allclose(defect_rows[:, 1:], expected, atol=5.01e-7, rtol=0)


def test_first_kind_christoffel_contraction_recovers_rod_force(example: dict[str, Any]) -> None:
    q = np.array([0.4, -0.7])
    v = np.array([2.1, -0.8])
    step = 1e-6
    derivative = np.stack(
        [
            (
                example["rod_arm"](q + step * e, v, LENGTHS, MASSES)[0]
                - example["rod_arm"](q - step * e, v, LENGTHS, MASSES)[0]
            )
            / (2 * step)
            for e in np.eye(2)
        ]
    )
    force = np.zeros(2)
    for i in range(2):
        for j in range(2):
            for k in range(2):
                gamma = (derivative[j, i, k] + derivative[k, i, j] - derivative[i, j, k]) / 2
                force[i] += gamma * v[j] * v[k]
    mass, expected, _ = example["rod_arm"](q, v, LENGTHS, MASSES)
    np.testing.assert_allclose(force, expected, atol=1e-9)
    connection_acceleration = np.linalg.solve(mass, force)
    assert not np.allclose(connection_acceleration, force)
