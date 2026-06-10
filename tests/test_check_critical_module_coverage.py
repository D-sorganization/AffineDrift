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
