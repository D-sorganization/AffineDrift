"""Tests for the critical-module coverage gate (issues #3230, #3294).

The gate shells out to pytest per target and reads the resulting coverage JSON
report. We mock ``subprocess.run`` (and, where needed, the report parsing) so
the pass/fail aggregation logic is exercised without spawning real test runs.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import scripts.check_critical_module_coverage as gate


class _FakeResult:
    def __init__(self, returncode: int) -> None:
        self.returncode = returncode


def test_run_coverage_builds_whole_tree_pytest_command(monkeypatch):
    """The gate measures the whole ``src`` tree (not a single submodule)."""
    captured = {}

    def fake_run(cmd, check):
        captured["cmd"] = cmd
        return _FakeResult(0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    # Report says the module is above its floor.
    monkeypatch.setattr(gate, "_coverage_percent_for", lambda report, module: 95.0)
    # Avoid touching the (mock-skipped) JSON file on disk.
    monkeypatch.setattr(gate.Path, "exists", lambda self: True)
    monkeypatch.setattr(gate.Path, "read_text", lambda self, encoding="utf-8": "{}")

    rc = gate._run_coverage("src.tools.foo", ["tests/test_foo.py"], 80)
    assert rc == 0
    assert "pytest" in captured["cmd"]
    assert "--cov=src" in captured["cmd"]
    assert "tests/test_foo.py" in captured["cmd"]
    # The per-submodule --cov flag must NOT be used (it double-imports numpy).
    assert "--cov=src.tools.foo" not in captured["cmd"]


def test_run_coverage_fails_when_below_floor(monkeypatch):
    """A module below its floor returns non-zero."""
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _FakeResult(0))
    monkeypatch.setattr(gate, "_coverage_percent_for", lambda report, module: 50.0)
    monkeypatch.setattr(gate.Path, "exists", lambda self: True)
    monkeypatch.setattr(gate.Path, "read_text", lambda self, encoding="utf-8": "{}")

    assert gate._run_coverage("src.tools.foo", ["tests/test_foo.py"], 80) == 1


def test_run_coverage_propagates_real_test_failure(monkeypatch):
    """A real pytest failure (rc not in {0, 5}) is propagated."""
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _FakeResult(2))
    assert gate._run_coverage("src.tools.foo", ["tests/test_foo.py"], 80) == 2


def _pass_all(monkeypatch) -> None:
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _FakeResult(0))
    monkeypatch.setattr(gate, "_coverage_percent_for", lambda report, module: 99.0)
    monkeypatch.setattr(gate.Path, "exists", lambda self: True)
    monkeypatch.setattr(gate.Path, "read_text", lambda self, encoding="utf-8": "{}")


def test_main_returns_zero_when_all_targets_pass(monkeypatch):
    _pass_all(monkeypatch)
    assert gate.main() == 0


def test_main_returns_one_when_any_target_fails(monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _FakeResult(0))
    monkeypatch.setattr(gate, "_coverage_percent_for", lambda report, module: 0.0)
    monkeypatch.setattr(gate.Path, "exists", lambda self: True)
    monkeypatch.setattr(gate.Path, "read_text", lambda self, encoding="utf-8": "{}")
    assert gate.main() == 1


def test_coverage_percent_for_matches_module_path():
    """_coverage_percent_for resolves a dotted module to its report entry."""
    report = {
        "files": {
            "src/golf_simulation/ball_flight.py": {"summary": {"percent_covered": 93.1}},
            "src/golf_simulation/clubs.py": {"summary": {"percent_covered": 80.0}},
        }
    }
    assert gate._coverage_percent_for(report, "src.golf_simulation.ball_flight") == 93.1
    assert gate._coverage_percent_for(report, "src.golf_simulation.missing") is None


def test_coverage_percent_for_handles_windows_paths():
    """Backslash paths in the report are normalized before matching."""
    report = {
        "files": {
            "src\\golf_simulation\\putting.py": {"summary": {"percent_covered": 83.3}},
        }
    }
    assert gate._coverage_percent_for(report, "src.golf_simulation.putting") == 83.3


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
    repo_root = Path(gate.__file__).resolve().parents[1]
    for _module, tests, _threshold in gate.CRITICAL_COVERAGE_TARGETS:
        for test_path in tests:
            assert (repo_root / test_path).exists(), f"missing test file: {test_path}"
