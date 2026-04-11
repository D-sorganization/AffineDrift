"""Regression tests for local developer test commands."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_make_test_runs_python_and_javascript_suites() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "python3 -m pytest tests/ --cov=src --cov-fail-under=50" in makefile
    assert "npm test -- --coverage" in makefile


def test_coverage_report_does_not_exclude_bare_pass() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    report_section = pyproject.split("[tool.coverage.report]", maxsplit=1)[1]

    assert '"pass"' not in report_section
