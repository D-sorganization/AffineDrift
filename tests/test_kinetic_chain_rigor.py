"""Independently verify the kinetic-chain chapter's mechanical counterexamples."""

import re
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "articles/The_Physics_of_Golf"
WEB = BOOK / "quarto/ch30_kinetic_chain.qmd"
PRINT = BOOK / "chapters/ch30_kinetic_chain.tex"
GRAVITY_M_S2 = 9.81


@pytest.fixture(scope="module")
def example() -> dict[str, Any]:
    text = WEB.read_text(encoding="utf-8")
    match = re.search(r"```python\n(# Kinetic-chain mechanical checks\n.*?)\n```", text, re.S)
    assert match is not None, "Publish reproducible mechanical cases in both editions"
    assert match[1] in PRINT.read_text(encoding="utf-8")
    namespace: dict[str, Any] = {}
    exec(compile(match[1], str(WEB), "exec"), namespace)
    return namespace


def test_rotor_response_matches_independent_initial_value_problem(example: dict[str, Any]) -> None:
    def dynamics(time: float, state: np.ndarray) -> list[float]:
        del time
        displacement = state[0] - state[1]
        return [state[2], state[3], (50 - 100 * displacement) / 2, 200 * displacement]

    times = np.linspace(0, 1, 501)
    solution = solve_ivp(dynamics, (0, 1), np.zeros(4), t_eval=times, rtol=1e-10, atol=1e-12)
    assert solution.success
    result = example["rotor_case"](times)
    np.testing.assert_allclose(result["state"], solution.y, atol=2e-8)
    np.testing.assert_allclose(result["energy"], 50 * solution.y[0], atol=2e-7)
    assert np.all(result["acceleration"][0] >= 15 - 1e-12)
    assert np.argmax(solution.y[2]) == len(times) - 1


def test_modes_satisfy_generalized_eigenproblem_with_rigid_mode(example: dict[str, Any]) -> None:
    result = example["mode_case"]()
    mass = np.diag([2, 1.2, 0.4])
    stiffness = np.array([[120, -120, 0], [-120, 220, -100], [0, -100, 100]])
    modes, squared = result["modes"], result["squared_frequencies"]
    np.testing.assert_allclose(stiffness @ modes, mass @ modes @ np.diag(squared), atol=1e-10)
    np.testing.assert_allclose(modes.T @ mass @ modes, np.eye(3), atol=1e-12)
    assert squared[0] == pytest.approx(0, abs=1e-12)
    assert np.all(squared[1:] > 0)


@pytest.mark.parametrize("acceleration", [(0.0, -20.0), (0.0, -GRAVITY_M_S2), (0.0, 0.0)])
def test_moving_grip_obeys_force_moment_and_work_balances(
    example: dict[str, Any], acceleration: tuple[float, float]
) -> None:
    result = example["grip_case"](acceleration)
    mass, length, central_inertia = 0.2, 1.0, 0.02
    alpha = result["alpha"]
    gravity = np.array([0, -GRAVITY_M_S2])
    center_acceleration = np.array(acceleration) + length * np.array([-4, alpha])
    np.testing.assert_allclose(result["force"] + mass * gravity, mass * center_acceleration)
    assert central_inertia * alpha == pytest.approx(-length * result["force"][1])
    center_velocity = np.array([0, -1])
    kinetic_rate = mass * center_velocity @ center_acceleration + central_inertia * 2 * alpha
    assert kinetic_rate == pytest.approx(result["grip_power"] + mass * gravity @ center_velocity)
    assert result["energy_rate"] == pytest.approx(result["grip_power"])
    if acceleration == (0.0, -GRAVITY_M_S2):
        assert alpha == pytest.approx(0)


def test_ground_wrench_separates_yaw_from_vertical_force(example: dict[str, Any]) -> None:
    cases = example["ground_case"]()
    np.testing.assert_allclose(cases["vertical_moment"], [235.44, -470.88, 0])
    np.testing.assert_allclose(cases["full_moment"], [435.44, -570.88, 70])
    assert cases["yaw_impulse"] == pytest.approx(3.5)


def test_joint_spring_power_retains_storage_and_dissipation(example: dict[str, Any]) -> None:
    result = example["joint_case"]()
    assert result["proximal_power"] + result["distal_power"] == pytest.approx(
        -result["storage_rate"] - result["dissipation"]
    )
    assert result["storage_rate"] > 0
    assert result["dissipation"] > 0
