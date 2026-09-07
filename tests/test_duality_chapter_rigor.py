"""Check the published duality examples against independent dynamics."""

import re
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from scipy.linalg import expm, solve_discrete_are

from scripts.generate_worked_examples import CH06_A, CH06_B, CH06_Q, CH06_R, build

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "articles/The_Geometry_of_Motion"
WEB = BOOK / "quarto/ch06_duality.qmd"
PRINT = BOOK / "Volume_I/chapters/ch06_duality.tex"


@pytest.fixture(scope="module")
def example() -> dict[str, Any]:
    text = WEB.read_text(encoding="utf-8")
    match = re.search(r"```python\n(# Duality chapter checks\n.*?)\n```", text, re.S)
    assert match is not None, "Publish the independently checkable duality cases"
    assert match[1] in PRINT.read_text(encoding="utf-8")
    namespace: dict[str, Any] = {}
    exec(compile(match[1], str(WEB), "exec"), namespace)
    return namespace["duality_cases"]()


def test_web_example_is_generated_and_matches_independent_dare() -> None:
    path = BOOK / "quarto/_includes/ch06_lqr_example.qmd"
    artifacts = build()
    assert path in artifacts, "Both editions need the same generated numerical authority"
    fragment = artifacts[path]
    assert path.read_text(encoding="utf-8") == fragment
    assert "{{< include _includes/ch06_lqr_example.qmd >}}" in WEB.read_text(encoding="utf-8")
    riccati = solve_discrete_are(CH06_A, CH06_B, CH06_Q, CH06_R)
    gain = np.linalg.solve(CH06_R + CH06_B.T @ riccati @ CH06_B, CH06_B.T @ riccati @ CH06_A)
    for value in np.concatenate((riccati.ravel(), gain.ravel())):
        assert f"{value:.4f}" in fragment
    state = np.array([1.0, 0.0])
    previous = None
    for step in range(11):
        value = float(state @ riccati @ state)
        match = re.search(rf"^\| {step} \| ([^\n]+)", fragment, re.M)
        assert match is not None
        cells = [cell.strip() for cell in match[1].split("|")]
        assert float(cells[0]) == pytest.approx(value, abs=5.1e-5)
        assert float(cells[1]) == pytest.approx(np.linalg.norm(state), abs=5.1e-5)
        if previous is not None:
            assert float(cells[2]) == pytest.approx(value / previous, abs=5.1e-5)
        previous = value
        state = (CH06_A - CH06_B @ gain) @ state


def test_continuous_decay_uses_half_the_value_rate(example: dict[str, Any]) -> None:
    rate = example["scalar_norm_rate"]
    assert rate == pytest.approx(np.sqrt(2.0))
    assert example["scalar_value_rate"] == pytest.approx(2 * rate)
    assert example["scalar_transition"] == pytest.approx(np.exp(-np.sqrt(2.0) * 0.7))


def test_discrete_norm_rate_is_square_root(example: dict[str, Any]) -> None:
    multiplier = example["discrete_closed_loop"]
    assert abs(multiplier) == pytest.approx(example["discrete_norm_factor"])
    assert multiplier**2 == pytest.approx(example["discrete_value_factor"])


def test_uncontrollable_stable_system_has_regular_metric(example: dict[str, Any]) -> None:
    np.testing.assert_allclose(example["uncontrolled_riccati"], 0.5 * np.eye(2), atol=1e-12)
    assert np.linalg.cond(example["uncontrolled_riccati"]) == pytest.approx(1.0)


def test_lqr_path_is_not_constant_metric_geodesic(example: dict[str, Any]) -> None:
    velocity, acceleration = example["path_velocity"], example["path_acceleration"]
    assert abs(np.linalg.det(np.column_stack((velocity, acceleration)))) > 0.5


def test_observer_cascade_does_not_inherit_exact_minimum_rate(example: dict[str, Any]) -> None:
    terminal = 4.0
    expected = expm(np.array([[-1.0, 1.0], [0.0, -1.0]]) * terminal)
    np.testing.assert_allclose(example["cascade_transition"], expected, atol=1e-13)
    assert np.linalg.norm(expected, 2) > np.exp(-terminal)
    assert expected[0, 1] == pytest.approx(terminal * np.exp(-terminal))


def test_disturbance_can_increase_storage_while_gain_bound_holds(example: dict[str, Any]) -> None:
    assert example["disturbed_storage_rate"] > 0.0
    assert example["hinf_balance"] <= 1e-12


def test_state_dependent_observer_gain_needs_innovation_derivative(example: dict[str, Any]) -> None:
    state, command, measurement, step = 0.3, 0.7, 1.2, 1e-5

    def observer(value: float) -> float:
        return value**2 + (1 + value) * command + value**2 * (measurement - value)

    actual = (observer(state + step) - observer(state - step)) / (2 * step)
    assert example["observer_jacobian"] == pytest.approx(actual, abs=2e-9)


def test_saturation_can_break_unconstrained_stability(example: dict[str, Any]) -> None:
    assert example["saturated_state_rate"] > 0.0
    assert example["unsaturated_state_rate"] < 0.0
