"""Verify the nonlinearity article against independent mechanics and limiting cases."""

import re
from pathlib import Path
from typing import Any

import numpy as np
import pytest

SOURCE = Path(__file__).resolve().parents[1] / "articles/sources-of-nonlinearity.qmd"
GRAVITY_M_S2 = 9.81


@pytest.fixture(scope="module")
def example() -> dict[str, Any]:
    match = re.search(
        r"```python\n(# Nonlinearity mechanical checks\n.*?)\n```",
        SOURCE.read_text(encoding="utf-8"),
        re.S,
    )
    assert match is not None, "Publish independently checkable nonlinearity examples"
    namespace: dict[str, Any] = {}
    exec(compile(match[1], str(SOURCE), "exec"), namespace)
    return namespace


@pytest.mark.parametrize("q", [(0.0, 0.0), (0.6, -0.9), (2.0, 1.7)])
def test_two_link_equations_match_com_geometry(example: dict[str, Any], q: tuple) -> None:
    q = np.array(q)
    velocity = np.array([1.3, -0.7])
    torque = np.array([2.0, -1.0])
    result = example["two_link"](q, velocity, torque)

    def geometric_mass(position: np.ndarray) -> np.ndarray:
        first, total = position[0], sum(position)
        jacobian_one = np.array([[0.5 * np.cos(first), 0], [0.5 * np.sin(first), 0]])
        jacobian_two = np.array(
            [
                [np.cos(first) + 0.4 * np.cos(total), 0.4 * np.cos(total)],
                [np.sin(first) + 0.4 * np.sin(total), 0.4 * np.sin(total)],
            ]
        )
        return (
            2 * jacobian_one.T @ jacobian_one
            + jacobian_two.T @ jacobian_two
            + 0.15 * np.diag([1, 0])
            + 0.05 * np.ones((2, 2))
        )

    mass = geometric_mass(q)
    np.testing.assert_allclose(result["mass"], mass, atol=1e-12)
    assert np.linalg.eigvalsh(mass).min() > 0
    step = 1e-5
    derivatives = [
        (geometric_mass(q + step * axis) - geometric_mass(q - step * axis)) / (2 * step)
        for axis in np.eye(2)
    ]
    coriolis = np.array(
        [
            sum(
                0.5
                * (derivatives[k][i, j] + derivatives[j][i, k] - derivatives[i][j, k])
                * velocity[j]
                * velocity[k]
                for j in range(2)
                for k in range(2)
            )
            for i in range(2)
        ]
    )
    np.testing.assert_allclose(result["coriolis"], coriolis, atol=1e-10)
    gravity = GRAVITY_M_S2 * np.array(
        [2 * np.sin(q[0]) + 0.4 * np.sin(sum(q)), 0.4 * np.sin(sum(q))]
    )
    np.testing.assert_allclose(mass @ result["acceleration"] + coriolis + gravity, torque)
    mass_rate = sum(derivatives[i] * velocity[i] for i in range(2))
    energy_rate = velocity @ mass @ result["acceleration"]
    energy_rate += 0.5 * velocity @ mass_rate @ velocity + gravity @ velocity
    assert energy_rate == pytest.approx(velocity @ torque, abs=1e-10)


def test_fixed_state_acceleration_increments_add(example: dict[str, Any]) -> None:
    q, velocity = np.array([0.7, -0.8]), np.array([2.0, 1.0])
    first, second = np.array([3.0, 0]), np.array([0, -2.0])
    solve = example["two_link"]
    baseline = solve(q, velocity, np.zeros(2))["acceleration"]
    combined = solve(q, velocity, first + second)["acceleration"]
    separate = (
        solve(q, velocity, first)["acceleration"] + solve(q, velocity, second)["acceleration"]
    )
    np.testing.assert_allclose(combined - baseline, separate - 2 * baseline, atol=1e-12)
    assert not np.allclose(combined, separate)


def test_stiction_uses_all_applied_loads_and_balances_force(example: dict[str, Any]) -> None:
    solve = example["rest_friction"]
    for drive, load in [(3, 0), (6, 0), (-6, 0), (-4, 4), (3, 4)]:
        acceleration, friction = solve(drive, load)
        assert acceleration == pytest.approx(drive + load + friction)
    assert solve(3, 0)[0] == 0
    assert solve(6, 0)[0] == 2
    assert solve(-6, 0)[0] == -2
    assert solve(-4, 4)[0] == 0
    assert solve(3, 4)[0] == 3


def test_play_operator_remembers_engagement(example: dict[str, Any]) -> None:
    result = example["play"](np.array([0, 0.4, 1, 0.4, -0.4, 0]), half_gap=0.5)
    np.testing.assert_allclose(result, [0, 0, 0.5, 0.5, 0.1, 0.1], atol=1e-12)
    assert result[1] != result[3]  # Same command, different retained state.


def test_hill_curve_has_correct_limits_and_curvature(example: dict[str, Any]) -> None:
    force = example["hill_shortening"](np.array([0, 1, 4]), 100.0, 25.0, 1.0)
    np.testing.assert_allclose(force, [100, 37.5, 0], atol=1e-12)
    np.testing.assert_allclose((force + 25) * (np.array([0, 1, 4]) + 1), 125)


def test_zero_excitation_retains_activation_and_force(example: dict[str, Any]) -> None:
    activation, force = example["deactivation"](np.array([0, 0.02, 0.04]))
    assert activation[0] == pytest.approx(0.6)
    np.testing.assert_allclose(activation / activation[0], [1, np.exp(-0.5), np.exp(-1)])
    np.testing.assert_allclose(force, 40 * activation)
    assert force[-1] > 0
