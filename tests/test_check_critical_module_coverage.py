"""Tests for the critical-module coverage gate (issue #3230).

The gate shells out to pytest per target module. We mock ``subprocess.run`` so
the pass/fail aggregation logic is exercised without spawning real test runs.
"""

from __future__ import annotations

import subprocess

import scripts.check_critical_module_coverage as gate


class _FakeResult:
    def __init__(self, returncode: int) -> None:
        self.returncode = returncode


def test_run_coverage_builds_expected_pytest_command(monkeypatch):
    captured = {}

    def fake_run(cmd, check):
        captured["cmd"] = cmd
        return _FakeResult(0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    rc = gate._run_coverage("src.tools.foo", ["tests/test_foo.py"], 80)
    assert rc == 0
    assert "pytest" in captured["cmd"]
    assert "--cov=src.tools.foo" in captured["cmd"]
    assert "--cov-fail-under=80" in captured["cmd"]
    assert "tests/test_foo.py" in captured["cmd"]


def test_main_returns_zero_when_all_targets_pass(monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _FakeResult(0))
    assert gate.main() == 0


def test_main_returns_one_when_any_target_fails(monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _FakeResult(1))
    assert gate.main() == 1


def test_main_counts_partial_failures(monkeypatch):
    # Fail only the first target; main() must still report failure.
    calls = {"n": 0}

    def fake_run(*a, **k):
        calls["n"] += 1
        return _FakeResult(1 if calls["n"] == 1 else 0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert gate.main() == 1
    assert calls["n"] == len(gate.CRITICAL_COVERAGE_TARGETS)


def test_targets_are_well_formed():
    for module, tests, threshold in gate.CRITICAL_COVERAGE_TARGETS:
        assert isinstance(module, str) and module
        assert isinstance(tests, list) and tests
        assert 0 < threshold <= 100


def test_gate_covers_physics_and_control_modules():
    """The gate must include the numerically critical physics/control modules."""
    modules = {module for module, _tests, _threshold in gate.CRITICAL_COVERAGE_TARGETS}
    required = {
        "src.golf_simulation.ball_flight",
        "src.golf_simulation.round_simulator",
        "src.golf_simulation.putting",
        "src.golf_simulation.clubs",
        "src.core.optimizers.ilqr_solver",
        "src.affine_control.swing_optimizer",
    }
    assert required <= modules


def test_physics_targets_reference_existing_test_files():
    """Each critical-module target must list real test files on disk."""
    from pathlib import Path

    repo_root = Path(gate.__file__).resolve().parents[1]
    for _module, tests, _threshold in gate.CRITICAL_COVERAGE_TARGETS:
        for test_path in tests:
            assert (repo_root / test_path).exists(), f"missing test file: {test_path}"
