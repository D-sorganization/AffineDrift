"""Regression tests for MATLAB quality checker decomposition."""

from pathlib import Path

from src.tools.matlab_utilities.scripts.matlab_quality_check import MATLABQualityChecker


def test_analyze_matlab_file_reports_all_key_issue_categories(tmp_path: Path) -> None:
    """Analyzer should keep parity across extracted check categories."""
    checker = MATLABQualityChecker(tmp_path)
    matlab_file = tmp_path / "example.m"
    matlab_file.write_text(
        "\n".join(
            [
                "function y = example(x)",
                "% function doc",
                "arguments",
                "  x",
                "end",
                "% <PLACEHOLDER>",
                "eval('x')",
                "assignin('base', 'x', 1)",
                "evalin('base', 'x')",
                "global G",
                "x = 42",
                "clear all",
                "clc",
                "close all",
                "addpath('foo')",
                "if exist('x', 'var')",
                "end",
                "load data.mat",
                "y = x",
                "end",
            ]
        ),
        encoding="utf-8",
    )

    issues = checker._analyze_matlab_file(matlab_file)

    assert any("Angle bracket placeholder found" in issue for issue in issues)
    assert any("Avoid using eval()" in issue for issue in issues)
    assert any("Avoid using assignin()" in issue for issue in issues)
    assert any("Avoid using evalin()" in issue for issue in issues)
    assert any("Magic number 42" in issue for issue in issues)
    assert any("Avoid 'clear all'" in issue for issue in issues)
    assert any("Avoid 'clc'" in issue for issue in issues)
    assert any("Avoid 'close all'" in issue for issue in issues)
    assert any("Avoid addpath in functions" in issue for issue in issues)
    assert any("instead of exist()" in issue for issue in issues)
    assert any("load without output variable" in issue for issue in issues)


def test_analyze_matlab_file_reports_missing_function_contracts(tmp_path: Path) -> None:
    """Function definitions without contracts should still be flagged."""
    checker = MATLABQualityChecker(tmp_path)
    matlab_file = tmp_path / "missing_contracts.m"
    matlab_file.write_text(
        "\n".join(
            [
                "function y = missing_contracts(x)",
                "y = x",
                "end",
            ]
        ),
        encoding="utf-8",
    )

    issues = checker._analyze_matlab_file(matlab_file)

    assert any("Missing function docstring" in issue for issue in issues)
    assert any("Missing arguments validation block" in issue for issue in issues)
