"""Tests verifying Gymnasium Pendulum-v1 policy analysis listings.

Extracts executable Python listings directly from Chapter 8 of Volume V,
validating rollout mechanics, state transitions, physics conformity,
random seed isolation, observation isolation, and Bellman targets.
"""

from __future__ import annotations

import math
import re
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

import numpy as np
import pytest

pytest.importorskip("gymnasium")


def _load_ch08_module() -> ModuleType:
    """Extract and compile Python listings from the Ch08 LaTeX source.

    Returns:
        ModuleType: Executed module namespace containing extracted listings.

    Raises:
        FileNotFoundError: If the TeX source file cannot be found.
        RuntimeError: If no Python listings are found in the chapter source.
    """
    tex_path = (
        Path(__file__).resolve().parents[1]
        / "articles"
        / "The_Geometry_of_Motion"
        / "Volume_V"
        / "chapters"
        / "ch08_reinforcement_learning.tex"
    )
    if not tex_path.is_file():
        pytest.fail(f"TeX file not found at: {tex_path}")

    content = tex_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"\\begin\{lstlisting\}\[[^\]]*language=Python[^\]]*\](?:\s*%.*?)?\n(.*?)\\end\{lstlisting\}",
        re.DOTALL | re.IGNORECASE,
    )
    matches = pattern.findall(content)
    if not matches:
        pytest.fail(f"No Python lstlisting blocks discovered in {tex_path}")

    combined_code = "\n\n".join(matches)
    mod = ModuleType("ch08_reinforcement_learning_extracted")
    compiled = compile(
        combined_code,
        str(tex_path),
        "exec",
        dont_inherit=True,
    )
    # Repository-owned listing at a fixed path, with no external input.
    # nosemgrep: python.lang.security.audit.exec-detected.exec-detected
    exec(compiled, mod.__dict__)
    return mod


@pytest.fixture(scope="module")
def ch08() -> ModuleType:
    """Provide dynamically compiled Chapter 8 listings module."""
    return _load_ch08_module()


def _predict_pendulum_step(obs: np.ndarray, action: float) -> tuple[np.ndarray, float]:
    """Compute independent ground-truth Euler integration for Pendulum-v1.

    Args:
        obs: Array containing [cos(theta), sin(theta), theta_dot].
        action: Scalar applied torque in [-2.0, 2.0].

    Returns:
        Tuple of (next_observation, reward).
    """
    dt, g, m, length = 0.05, 10.0, 1.0, 1.0
    cos_th, sin_th, thdot = float(obs[0]), float(obs[1]), float(obs[2])
    theta = math.atan2(sin_th, cos_th)
    torque = float(np.clip(action, -2.0, 2.0))
    # Pre-step state reward
    costheta_norm = ((theta + math.pi) % (2.0 * math.pi)) - math.pi
    reward = -(costheta_norm**2 + 0.1 * (thdot**2) + 0.001 * (torque**2))
    # Semi-implicit Euler integration
    angular_acc = (3.0 * g / (2.0 * length)) * sin_th + (3.0 / (m * length**2)) * torque
    next_thdot = float(np.clip(thdot + angular_acc * dt, -8.0, 8.0))
    next_theta = theta + next_thdot * dt
    next_obs = np.array(
        [math.cos(next_theta), math.sin(next_theta), next_thdot],
        dtype=np.float32,
    )
    return next_obs, reward


def test_run_pendulum_physics_and_reward(ch08: ModuleType) -> None:
    """Verify first-step physics, reward calculation, and transition shape."""
    run_pendulum = ch08.run_pendulum
    seed, test_torque = 42, 0.4

    def applied_policy(_: np.ndarray) -> np.ndarray:
        """Apply a constant torque."""
        return np.array([test_torque], dtype=np.float32)

    rollout = run_pendulum(policy=applied_policy, seed=seed, steps=1)

    assert rollout["observations"].shape == (2, 3)
    assert rollout["actions"].shape == (1, 1)
    assert len(rollout["rewards"]) == 1
    assert not rollout["terminated"][0]

    obs0 = rollout["observations"][0]
    expected_obs1, expected_r0 = _predict_pendulum_step(obs0, test_torque)

    np.testing.assert_allclose(rollout["observations"][1], expected_obs1, atol=1e-5)
    assert math.isclose(rollout["rewards"][0], expected_r0, abs_tol=1e-5)


def test_seed_isolation_and_reproducibility(ch08: ModuleType) -> None:
    """Verify deterministic trajectories without polluting global NumPy RNG state."""
    run_pendulum = ch08.run_pendulum

    def zero_policy(_: np.ndarray) -> np.ndarray:
        """Apply zero torque."""
        return np.array([0.0], dtype=np.float32)

    state_before = np.random.get_state()
    rollout_a = run_pendulum(zero_policy, seed=101, steps=3)
    state_after = np.random.get_state()
    rollout_b = run_pendulum(zero_policy, seed=101, steps=3)

    np.testing.assert_array_equal(rollout_a["observations"], rollout_b["observations"])
    assert state_before[0] == state_after[0]
    assert state_before[2:] == state_after[2:]
    np.testing.assert_array_equal(state_before[1], state_after[1])


def test_observation_mutation_isolation(ch08: ModuleType) -> None:
    """Ensure in-place mutation of observation in policy does not corrupt recorded states."""
    run_pendulum = ch08.run_pendulum

    def malicious_policy(obs: np.ndarray) -> np.ndarray:
        """Mutate only the defensive observation copy."""
        obs[:] = 999.0
        return np.array([0.0], dtype=np.float32)

    def clean_policy(_: np.ndarray) -> np.ndarray:
        """Apply the same torque without mutating the observation."""
        return np.array([0.0], dtype=np.float32)

    rollout_corrupting = run_pendulum(malicious_policy, seed=2026, steps=4)
    rollout_baseline = run_pendulum(clean_policy, seed=2026, steps=4)

    assert not np.any(np.isclose(rollout_corrupting["observations"], 999.0))
    np.testing.assert_allclose(
        rollout_corrupting["observations"],
        rollout_baseline["observations"],
        rtol=1e-6,
    )


def test_truncation_boundary_and_no_post_done_stepping(ch08: ModuleType) -> None:
    """Confirm episode strictly terminates at step limit without post-done stepping."""
    run_pendulum = ch08.run_pendulum
    steps = 4

    def policy(_: np.ndarray) -> np.ndarray:
        """Apply a fixed valid action."""
        return np.array([0.5], dtype=np.float32)

    rollout = run_pendulum(policy=policy, seed=7, steps=steps)

    assert rollout["observations"].shape == (steps + 1, 3)
    assert rollout["actions"].shape == (steps, 1)
    assert len(rollout["rewards"]) == steps
    assert len(rollout["terminated"]) == steps
    assert len(rollout["truncated"]) == steps
    assert not any(rollout["terminated"])
    np.testing.assert_array_equal(rollout["truncated"], [False, False, False, True])


@pytest.mark.parametrize(
    ("bad_policy", "seed", "steps"),
    [
        (lambda _: np.array([3.5], dtype=np.float32), 1, 5),
        (lambda _: np.array([-2.01], dtype=np.float32), 1, 5),
        (lambda _: np.array([np.nan], dtype=np.float32), 1, 5),
        (lambda _: np.array([0.0, 1.0], dtype=np.float32), 1, 5),
        (lambda _: np.array([0.0], dtype=np.float32), -1, 5),
        (lambda _: np.array([0.0], dtype=np.float32), True, 5),
        (lambda _: np.array([0.0], dtype=np.float32), 1, 0),
        (lambda _: np.array([0.0], dtype=np.float32), 1, False),
    ],
)
def test_run_pendulum_strict_input_validation(
    ch08: ModuleType,
    bad_policy: Callable[[np.ndarray], Any],
    seed: Any,
    steps: Any,
) -> None:
    """Validate strict rejection of out-of-bound/malformed inputs, actions, seeds, and steps."""
    run_pendulum = ch08.run_pendulum
    with pytest.raises((ValueError, TypeError)):
        run_pendulum(policy=bad_policy, seed=seed, steps=steps)


def test_bootstrap_target_truncation_vs_terminal(ch08: ModuleType) -> None:
    """Verify Bellman target calculation respects truncation vs termination semantics."""
    bootstrap_target = ch08.bootstrap_target

    # Truncation: terminated is False -> continues bootstrapping (2.0 + 0.9 * 5.0 = 6.5)
    target_truncated = bootstrap_target(reward=2.0, discount=0.9, next_value=5.0, terminated=False)
    assert math.isclose(target_truncated, 6.5, rel_tol=1e-6)

    # Termination: terminated is True -> drops future value (2.0 + 0.9 * 0.0 = 2.0)
    target_terminal = bootstrap_target(reward=2.0, discount=0.9, next_value=5.0, terminated=True)
    assert math.isclose(target_terminal, 2.0, rel_tol=1e-6)
    assert bootstrap_target(2.0, 0.9, 5.0, np.bool_(False)) == 6.5
    assert bootstrap_target(2.0, 0.9, 5.0, np.bool_(True)) == 2.0


@pytest.mark.parametrize(("torque", "seed"), [(-2.0, 11), (2.0, 42)])
def test_full_rollout_wrap_and_speed_cap(ch08: ModuleType, torque: float, seed: int) -> None:
    """Check every transition and reward, including wrap and speed saturation."""

    def policy(_: np.ndarray) -> np.ndarray:
        """Drive the benchmark with a bounded constant torque."""
        return np.array([torque], dtype=np.float32)

    record = ch08.run_pendulum(policy, seed=seed, steps=200)
    before, after = record["observations"][:-1], record["observations"][1:]
    angle = np.arctan2(before[:, 1].astype(float), before[:, 0].astype(float))
    velocity = before[:, 2].astype(float)
    expected_rate = np.clip(velocity + 0.05 * (15 * np.sin(angle) + 3 * torque), -8, 8)
    expected_angle = angle + 0.05 * expected_rate
    expected_observation = np.column_stack(
        (np.cos(expected_angle), np.sin(expected_angle), expected_rate)
    )
    np.testing.assert_allclose(after, expected_observation, atol=2e-6)
    np.testing.assert_allclose(
        record["rewards"],
        -(angle**2 + 0.1 * velocity**2 + 0.001 * torque**2),
        atol=2e-6,
    )
    # The positive-drive case saturates; the negative-drive case oscillates.
    # Constant bounded torque does not guarantee circulation or saturation.
    if torque > 0:
        assert np.any(np.abs(after[:, 2]) == 8.0)
    assert np.any(np.abs(np.diff(angle)) > np.pi)


@pytest.mark.parametrize(
    "case",
    [
        (float("nan"), 0.9, 1.0, False),
        (1.0, -0.01, 1.0, False),
        (1.0, 1.01, 1.0, False),
        (1.0, 0.9, float("inf"), False),
        (1.0, 0.9, 1.0, "not_a_bool"),
        (1.0, 0.9, 1.0, 1),
    ],
)
def test_bootstrap_target_invalid_domains(ch08: ModuleType, case: tuple[Any, ...]) -> None:
    """Validate boundary checks for scalar finiteness, discount [0, 1], and bool type."""
    reward, discount, next_val, terminated = case
    bootstrap_target = ch08.bootstrap_target
    with pytest.raises((ValueError, TypeError)):
        bootstrap_target(
            reward=reward,
            discount=discount,
            next_value=next_val,
            terminated=terminated,
        )
