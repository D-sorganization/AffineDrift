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


# ---------------------------------------------------------------------------
# check_matlab_files_exist tests
# ---------------------------------------------------------------------------


def test_check_matlab_files_exist_returns_false_when_no_matlab_dir(tmp_path: Path) -> None:
    """check_matlab_files_exist should return False when matlab dir is absent."""
    checker = MATLABQualityChecker(tmp_path)
    assert checker.check_matlab_files_exist() is False


def test_check_matlab_files_exist_returns_false_for_empty_matlab_dir(tmp_path: Path) -> None:
    """check_matlab_files_exist should return False when matlab dir has no .m files."""
    matlab_dir = tmp_path / "matlab"
    matlab_dir.mkdir()
    checker = MATLABQualityChecker(tmp_path)
    assert checker.check_matlab_files_exist() is False


def test_check_matlab_files_exist_returns_true_when_m_files_present(tmp_path: Path) -> None:
    """check_matlab_files_exist should return True when at least one .m file exists."""
    matlab_dir = tmp_path / "matlab"
    matlab_dir.mkdir()
    (matlab_dir / "script.m").write_text("x = 1;", encoding="utf-8")
    checker = MATLABQualityChecker(tmp_path)
    assert checker.check_matlab_files_exist() is True


def test_check_matlab_files_exist_sets_total_files_count(tmp_path: Path) -> None:
    """check_matlab_files_exist should update results total_files count."""
    matlab_dir = tmp_path / "matlab"
    matlab_dir.mkdir()
    (matlab_dir / "a.m").write_text("x = 1;", encoding="utf-8")
    (matlab_dir / "b.m").write_text("y = 2;", encoding="utf-8")
    checker = MATLABQualityChecker(tmp_path)
    checker.check_matlab_files_exist()
    assert checker.results["total_files"] == 2


# ---------------------------------------------------------------------------
# run_matlab_quality_checks tests
# ---------------------------------------------------------------------------


def test_run_matlab_quality_checks_falls_back_to_static_when_no_config(tmp_path: Path) -> None:
    """run_matlab_quality_checks should use static analysis when config script absent."""
    matlab_dir = tmp_path / "matlab"
    matlab_dir.mkdir()
    (matlab_dir / "clean.m").write_text(
        "\n".join(
            [
                "function y = clean(x)",
                "% Clean function doc",
                "arguments",
                "  x",
                "end",
                "y = x;",
                "end",
            ]
        ),
        encoding="utf-8",
    )
    checker = MATLABQualityChecker(tmp_path)
    result = checker.run_matlab_quality_checks()
    assert result.get("method") == "static_analysis"


# ---------------------------------------------------------------------------
# _static_matlab_analysis tests
# ---------------------------------------------------------------------------


def test_static_matlab_analysis_passes_for_clean_file(tmp_path: Path) -> None:
    """_static_matlab_analysis should report passed=True for clean MATLAB files."""
    matlab_dir = tmp_path / "matlab"
    matlab_dir.mkdir()
    (matlab_dir / "clean.m").write_text(
        "\n".join(
            [
                "function y = clean(x)",
                "% Doc",
                "arguments",
                "  x",
                "end",
                "y = x;",
                "end",
            ]
        ),
        encoding="utf-8",
    )
    checker = MATLABQualityChecker(tmp_path)
    result = checker._static_matlab_analysis()
    assert result["passed"] is True


def test_static_matlab_analysis_fails_for_problematic_file(tmp_path: Path) -> None:
    """_static_matlab_analysis should report passed=False when issues are found."""
    matlab_dir = tmp_path / "matlab"
    matlab_dir.mkdir()
    (matlab_dir / "bad.m").write_text("eval('x')\n", encoding="utf-8")
    checker = MATLABQualityChecker(tmp_path)
    result = checker._static_matlab_analysis()
    assert result["passed"] is False
    assert len(result["issues"]) > 0


# ---------------------------------------------------------------------------
# run_all_checks tests
# ---------------------------------------------------------------------------


def test_run_all_checks_passes_when_no_matlab_dir(tmp_path: Path) -> None:
    """run_all_checks should skip gracefully and pass when no matlab directory."""
    checker = MATLABQualityChecker(tmp_path)
    results = checker.run_all_checks()
    assert results["passed"] is True
    assert "SKIP" in results["summary"]


def test_run_all_checks_passes_for_clean_matlab_files(tmp_path: Path) -> None:
    """run_all_checks should pass when MATLAB files have no issues."""
    matlab_dir = tmp_path / "matlab"
    matlab_dir.mkdir()
    (matlab_dir / "clean.m").write_text(
        "\n".join(
            [
                "function y = clean(x)",
                "% Doc",
                "arguments",
                "  x",
                "end",
                "y = x;",
                "end",
            ]
        ),
        encoding="utf-8",
    )
    checker = MATLABQualityChecker(tmp_path)
    results = checker.run_all_checks()
    assert results["passed"] is True


def test_run_all_checks_fails_for_problematic_matlab_files(tmp_path: Path) -> None:
    """run_all_checks should fail when MATLAB files have issues."""
    matlab_dir = tmp_path / "matlab"
    matlab_dir.mkdir()
    (matlab_dir / "bad.m").write_text("eval('x')\n", encoding="utf-8")
    checker = MATLABQualityChecker(tmp_path)
    results = checker.run_all_checks()
    assert results["passed"] is False
