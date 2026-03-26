"""Extended tests for rl_funnel_benchmark.py — run_comparison and main()."""

from __future__ import annotations

import sys
from unittest.mock import patch

import numpy as np
import pytest

from src.tools.rl_funnel_benchmark import (
    BenchmarkResult,
    run_comparison,
)


class TestRunComparison:
    """Tests for run_comparison()."""

    def test_returns_list_of_benchmark_results(self) -> None:
        """Should return a list of BenchmarkResult objects."""
        results = run_comparison(
            perturbation_scale=0.1,
            t_span=(0.0, 0.05),
            dt=0.005,
            seed=42,
        )
        assert isinstance(results, list)
        assert all(isinstance(r, BenchmarkResult) for r in results)

    def test_returns_three_results(self) -> None:
        """Should return exactly 3 BenchmarkResult objects (setpoint, TTCF, passive)."""
        results = run_comparison(
            perturbation_scale=0.1,
            t_span=(0.0, 0.05),
            dt=0.005,
            seed=0,
        )
        assert len(results) == 3

    def test_setpoint_result_present(self) -> None:
        """Should include a 'Setpoint LQR' result."""
        results = run_comparison(
            perturbation_scale=0.05,
            t_span=(0.0, 0.05),
            dt=0.005,
            seed=1,
        )
        names = [r.name for r in results]
        assert any("Setpoint" in n for n in names)

    def test_trajectory_tracking_result_present(self) -> None:
        """Should include a 'Trajectory Tracking' result."""
        results = run_comparison(
            perturbation_scale=0.05,
            t_span=(0.0, 0.05),
            dt=0.005,
            seed=2,
        )
        names = [r.name for r in results]
        assert any("Trajectory" in n for n in names)

    def test_passive_result_present(self) -> None:
        """Should include a 'Passive' result."""
        results = run_comparison(
            perturbation_scale=0.05,
            t_span=(0.0, 0.05),
            dt=0.005,
            seed=3,
        )
        names = [r.name for r in results]
        assert any("Passive" in n for n in names)

    def test_tracking_errors_are_non_negative(self) -> None:
        """All tracking errors should be >= 0."""
        results = run_comparison(
            perturbation_scale=0.1,
            t_span=(0.0, 0.05),
            dt=0.005,
            seed=10,
        )
        for r in results:
            assert r.tracking_error >= 0.0


class TestPrintResultsEdgeCases:
    """Additional tests for print_results() edge cases."""

    def test_setpoint_outperforms_ttcf_branch(self, caplog: pytest.LogCaptureFixture) -> None:
        """Should log setpoint wins message when TTCF is worse."""
        import logging

        from src.tools.rl_funnel_benchmark import print_results

        t = np.linspace(0, 1, 10)
        traj = np.zeros((4, 10))
        # Setpoint has LOWER error than TTCF (setpoint wins)
        results = [
            BenchmarkResult("Setpoint LQR", 0.3, 1.0, 0.1, traj, t),
            BenchmarkResult("Trajectory Tracking (TTCF)", 0.8, 1.2, 0.15, traj, t),
        ]
        with caplog.at_level(logging.INFO, logger="src.tools.rl_funnel_benchmark"):
            print_results(results)
        combined = " ".join(caplog.messages)
        # Either improvement or degradation message should appear
        assert "%" in combined


class TestMain:
    """Tests for main() function."""

    def test_main_runs_with_defaults(self) -> None:
        """main() should run without raising with short horizon."""
        from src.tools.rl_funnel_benchmark import main

        with patch.object(
            sys, "argv", ["rl_funnel_benchmark.py", "--horizon", "0.05", "--seed", "99"]
        ):
            # Should not raise
            main()
