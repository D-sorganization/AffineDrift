"""Regression tests pinning the RL-funnel dynamics de-duplication (issue #3180).

``rl_funnel_benchmark`` used to carry byte-identical copies of the double-pendulum
dynamics that already live in ``rl_funnel_dynamics``. The benchmark module now
re-exports the canonical implementations instead of redefining them. These tests
fail if a duplicate body is reintroduced, by asserting the benchmark symbols are
the *same object* as the canonical ones.
"""

from __future__ import annotations

import src.tools.rl_funnel_benchmark as benchmark
import src.tools.rl_funnel_dynamics as dynamics


def test_double_pendulum_drift_is_canonical() -> None:
    assert benchmark.double_pendulum_drift is dynamics.double_pendulum_drift


def test_double_pendulum_B_is_canonical() -> None:
    assert benchmark.double_pendulum_B is dynamics.double_pendulum_B


def test_generate_reference_trajectory_is_canonical() -> None:
    assert benchmark.generate_reference_trajectory is dynamics.generate_reference_trajectory


def test_benchmark_reexports_are_public() -> None:
    """The re-exported dynamics stay in the benchmark module's public surface."""
    for name in (
        "double_pendulum_drift",
        "double_pendulum_B",
        "generate_reference_trajectory",
    ):
        assert name in benchmark.__all__
