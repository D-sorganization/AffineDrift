"""Tests for code quality check pipeline (check.py, ast_analyzer.py, report_generator.py)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

import src.tools.code_quality_check as cq_shim  # noqa: F401 — covers shim imports
from src.tools.code_quality.ast_analyzer import check_ast_issues
from src.tools.code_quality.check import check_file, main
from src.tools.code_quality.pattern_checker import check_banned_patterns, check_magic_numbers
from src.tools.code_quality.report_generator import report_issues

# ---------------------------------------------------------------------------
# check_file tests
# ---------------------------------------------------------------------------


def test_check_file_returns_empty_for_clean_file(tmp_path: Path) -> None:
    """check_file should return no issues for a fully compliant file."""
    f = tmp_path / "clean.py"
    f.write_text(
        '"""Module docstring."""\n\n\ndef greet(name: str) -> str:\n    """Say hello."""\n    return f"hello {name}"\n',
        encoding="utf-8",
    )
    issues = check_file(f)
    assert isinstance(issues, list)
    # No banned patterns, no magic numbers, no missing docstrings
    assert not any("Error" in msg for _, msg, _ in issues)


def test_check_file_returns_error_tuple_on_oserror(tmp_path: Path) -> None:
    """check_file should return a synthetic error tuple when file is unreadable."""
    missing = tmp_path / "no_file.py"
    issues = check_file(missing)
    assert len(issues) == 1
    line_num, message, _ = issues[0]
    assert line_num == 0
    assert "Error reading file" in message


def test_check_file_detects_magic_number(tmp_path: Path) -> None:
    """check_file should flag known magic numbers (pi approximation) in source code."""
    f = tmp_path / "magic.py"
    f.write_text(
        '"""Module."""\n\n\ndef compute() -> float:\n    """Compute."""\n    return 3.14159\n',
        encoding="utf-8",
    )
    issues = check_file(f)
    assert any("math.pi" in msg or "3.14" in msg for _, msg, _ in issues)


# ---------------------------------------------------------------------------
# check_ast_issues tests
# ---------------------------------------------------------------------------


def test_check_ast_issues_detects_missing_docstring(tmp_path: Path) -> None:
    """check_ast_issues should flag functions without docstrings."""
    filepath = tmp_path / "nodoc.py"
    content = "def no_docstring():\n    pass\n"
    issues = check_ast_issues(content, filepath)
    assert any("missing docstring" in msg.lower() for _, msg, _ in issues)


def test_check_ast_issues_skips_quality_check_scripts(tmp_path: Path) -> None:
    """check_ast_issues should skip checks on quality check scripts."""
    filepath = tmp_path / "matlab_quality_check.py"
    content = "def no_docstring():\n    pass\n"
    issues = check_ast_issues(content, filepath)
    assert issues == []


def test_check_ast_issues_skips_tests_directory(tmp_path: Path) -> None:
    """check_ast_issues should skip docstring checks for files in tests/."""
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    filepath = tests_dir / "test_something.py"
    content = "def test_func():\n    pass\n"
    issues = check_ast_issues(content, filepath)
    assert not any("missing docstring" in msg.lower() for _, msg, _ in issues)


def test_check_ast_issues_skips_scripts_directory(tmp_path: Path) -> None:
    """check_ast_issues should skip docstring checks for files in scripts/."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    filepath = scripts_dir / "helper.py"
    content = "def helper():\n    pass\n"
    issues = check_ast_issues(content, filepath)
    assert not any("missing docstring" in msg.lower() for _, msg, _ in issues)


def test_check_ast_issues_skips_core_contracts_file() -> None:
    """check_ast_issues should skip docstring checks for src/core/contracts.py."""
    # Use the real contracts.py path
    from pathlib import Path as _Path

    filepath = _Path("src/core/contracts.py")
    content = "def enforce():\n    pass\n"
    issues = check_ast_issues(content, filepath)
    # Should not flag missing docstring for contracts.py
    assert not any("missing docstring" in msg.lower() for _, msg, _ in issues)


def test_check_ast_issues_detects_syntax_error(tmp_path: Path) -> None:
    """check_ast_issues should return a syntax-error tuple for invalid Python."""
    filepath = tmp_path / "broken.py"
    content = "def broken(\n"
    issues = check_ast_issues(content, filepath)
    assert any("syntax error" in msg.lower() for _, msg, _ in issues)


def test_check_ast_issues_ignores_stub_body(tmp_path: Path) -> None:
    """check_ast_issues should not flag functions whose body is just Ellipsis."""
    filepath = tmp_path / "proto.py"
    content = "def stub() -> None: ...\n"
    issues = check_ast_issues(content, filepath)
    # Stub-body functions (Ellipsis) should not trigger missing docstring
    assert not any("stub" in msg for _, msg, _ in issues)


def test_check_ast_issues_clean_file_no_issues(tmp_path: Path) -> None:
    """check_ast_issues should return empty list for a fully documented file."""
    filepath = tmp_path / "good.py"
    content = (
        '"""Module."""\n\n\ndef greet(name: str) -> str:\n    """Say hello."""\n    return name\n'
    )
    issues = check_ast_issues(content, filepath)
    assert issues == []


# ---------------------------------------------------------------------------
# report_issues tests
# ---------------------------------------------------------------------------


def test_report_issues_writes_to_stderr(capsys: pytest.CaptureFixture[str]) -> None:
    """report_issues should write a formatted report to stderr."""
    all_issues: list[tuple[Path, list[tuple[int, str, str]]]] = [
        (Path("src/tools/foo.py"), [(10, "Magic number 99", "x = 99")]),
    ]
    report_issues(all_issues)
    captured = capsys.readouterr()
    assert "foo.py" in captured.err
    assert "Magic number 99" in captured.err


def test_report_issues_handles_zero_line_number(capsys: pytest.CaptureFixture[str]) -> None:
    """report_issues should handle issues at line 0 (file-level errors)."""
    all_issues: list[tuple[Path, list[tuple[int, str, str]]]] = [
        (Path("src/tools/broken.py"), [(0, "Syntax error: unexpected EOF", "")]),
    ]
    report_issues(all_issues)
    captured = capsys.readouterr()
    assert "Syntax error" in captured.err


def test_report_issues_shows_code_snippet_when_present(capsys: pytest.CaptureFixture[str]) -> None:
    """report_issues should print code snippets for issues that have them."""
    all_issues: list[tuple[Path, list[tuple[int, str, str]]]] = [
        (Path("src/tools/mod.py"), [(5, "Banned pattern: eval", "eval('x')")]),
    ]
    report_issues(all_issues)
    captured = capsys.readouterr()
    assert "eval" in captured.err


def test_report_issues_shows_total_count(capsys: pytest.CaptureFixture[str]) -> None:
    """report_issues should include total issue count at the end."""
    all_issues: list[tuple[Path, list[tuple[int, str, str]]]] = [
        (
            Path("src/tools/a.py"),
            [(1, "issue one", ""), (2, "issue two", "")],
        ),
    ]
    report_issues(all_issues)
    captured = capsys.readouterr()
    assert "2" in captured.err


# ---------------------------------------------------------------------------
# pattern_checker tests
# ---------------------------------------------------------------------------


def test_check_banned_patterns_skips_self_check_files(tmp_path: Path) -> None:
    """check_banned_patterns should return empty for self-check files."""
    filepath = tmp_path / "pattern_checker.py"
    lines = ["TRACKED_TASK: fix this\n"]
    issues = check_banned_patterns(lines, filepath)
    assert issues == []


def test_check_banned_patterns_ignores_not_implemented_in_comment(tmp_path: Path) -> None:
    """check_banned_patterns should skip NotImplementedError when in a comment."""
    filepath = tmp_path / "mymod.py"
    lines = ["# NotImplementedError is not raised here\n"]
    issues = check_banned_patterns(lines, filepath)
    assert not any("NotImplementedError" in msg for _, msg, _ in issues)


def test_check_banned_patterns_flags_template_placeholder(tmp_path: Path) -> None:
    """check_banned_patterns should flag 'your code here' template patterns."""
    filepath = tmp_path / "template.py"
    lines = ["x = 'your value here'\n"]
    issues = check_banned_patterns(lines, filepath)
    assert any("placeholder" in msg.lower() for _, msg, _ in issues)


def test_check_magic_numbers_skips_self_check_files(tmp_path: Path) -> None:
    """check_magic_numbers should return empty for self-check files."""
    filepath = tmp_path / "matlab_quality_check.py"
    lines = ["g = 9.81\n"]
    issues = check_magic_numbers(lines, filepath)
    assert issues == []


def test_check_magic_numbers_skips_allowed_constants(tmp_path: Path) -> None:
    """check_magic_numbers should skip lines that define GRAVITY_M_S2."""
    filepath = tmp_path / "constants.py"
    lines = ["GRAVITY_M_S2 = 9.81\n"]
    issues = check_magic_numbers(lines, filepath)
    assert issues == []


# ---------------------------------------------------------------------------
# check.main() tests
# ---------------------------------------------------------------------------


def test_main_exits_zero_with_clean_file(tmp_path: Path) -> None:
    """main() should exit 0 when all scanned files are clean."""
    clean = tmp_path / "clean.py"
    clean.write_text(
        '"""Module."""\n\n\ndef greet() -> None:\n    """Say hi."""\n', encoding="utf-8"
    )
    with patch.object(sys, "argv", ["check.py", str(clean)]):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 0


def test_main_exits_one_with_issues(tmp_path: Path) -> None:
    """main() should exit 1 when issues are found."""
    bad = tmp_path / "bad.py"
    bad.write_text("x = 3.14159\n", encoding="utf-8")
    with patch.object(sys, "argv", ["check.py", str(bad)]):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1
