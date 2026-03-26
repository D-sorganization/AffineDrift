"""Additional tests for code_quality — pattern_checker, report_generator, async_utils."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from src.tools.code_quality.pattern_checker import (
    check_banned_patterns,
    check_magic_numbers,
    is_legitimate_pass_context,
)
from src.tools.code_quality.report_generator import report_issues


class TestIsLegitimatePasContext:
    """Tests for is_legitimate_pass_context()."""

    def test_pass_in_class_body_is_legitimate(self) -> None:
        """Should return True for pass inside a class definition."""
        lines = ["class Foo:", "    pass"]
        assert is_legitimate_pass_context(lines, 2) is True

    def test_pass_in_try_block_is_legitimate(self) -> None:
        """Should return True for pass inside try block."""
        lines = ["try:", "    pass"]
        assert is_legitimate_pass_context(lines, 2) is True

    def test_pass_in_except_block_is_legitimate(self) -> None:
        """Should return True for pass inside except block."""
        lines = ["try:", "    do_something()", "except ValueError:", "    pass"]
        assert is_legitimate_pass_context(lines, 4) is True

    def test_pass_in_function_body_not_legitimate(self) -> None:
        """Should return False for pass inside function body."""
        lines = ["def foo():", "    pass"]
        assert is_legitimate_pass_context(lines, 2) is False

    def test_invalid_line_num_returns_false(self) -> None:
        """Should return False for line_num out of range."""
        lines = ["x = 1"]
        assert is_legitimate_pass_context(lines, 0) is False
        assert is_legitimate_pass_context(lines, 10) is False

    def test_non_pass_line_returns_false(self) -> None:
        """Should return False when the line is not 'pass'."""
        lines = ["x = 1", "y = 2"]
        assert is_legitimate_pass_context(lines, 1) is False


class TestCheckBannedPatterns:
    """Tests for check_banned_patterns()."""

    def test_detects_todo(self, tmp_path: Path) -> None:
        """Should detect TRACKED_TASK patterns."""
        f = tmp_path / "module.py"
        lines = ["x = 1  # TRACKED_TASK: fix this\n"]
        result = check_banned_patterns(lines, f)
        assert any("TRACKED_TASK" in msg for _, msg, _ in result)

    def test_detects_fixme(self, tmp_path: Path) -> None:
        """Should detect TRACKED_DEFECT patterns."""
        f = tmp_path / "module.py"
        lines = ["# TRACKED_DEFECT: this is broken\n"]
        result = check_banned_patterns(lines, f)
        assert any("TRACKED_DEFECT" in msg for _, msg, _ in result)

    def test_skips_self_check_files(self, tmp_path: Path) -> None:
        """Should skip pattern_checker.py (self-check exclusion)."""
        f = tmp_path / "pattern_checker.py"
        lines = ["x = 1  # TRACKED_TASK: fix this\n"]
        result = check_banned_patterns(lines, f)
        assert result == []

    def test_detects_not_implemented_error(self, tmp_path: Path) -> None:
        """Should detect NotImplementedError in non-comment lines."""
        f = tmp_path / "module.py"
        lines = ["raise NotImplementedError()\n"]
        result = check_banned_patterns(lines, f)
        assert any("NotImplementedError" in msg for _, msg, _ in result)

    def test_ignores_not_implemented_in_comment(self, tmp_path: Path) -> None:
        """Should not flag NotImplementedError in comments."""
        f = tmp_path / "module.py"
        lines = ["# NotImplementedError - see issue\n"]
        result = check_banned_patterns(lines, f)
        # Should not flag it since it's in a comment
        assert not any("NotImplementedError" in msg for _, msg, _ in result)

    def test_detects_illegitimate_pass(self, tmp_path: Path) -> None:
        """Should detect illegitimate pass statements."""
        f = tmp_path / "module.py"
        lines = ["def foo():", "    pass"]
        result = check_banned_patterns(lines, f)
        assert any("pass" in msg.lower() for _, msg, _ in result)


class TestCheckMagicNumbers:
    """Tests for check_magic_numbers()."""

    def test_detects_pi_literal(self, tmp_path: Path) -> None:
        """Should detect raw pi value 3.141..."""
        f = tmp_path / "module.py"
        lines = ["radius_squared = 3.14159 * r**2\n"]
        result = check_magic_numbers(lines, f)
        assert any("pi" in msg.lower() for _, msg, _ in result)

    def test_detects_gravity_literal(self, tmp_path: Path) -> None:
        """Should detect raw gravity value 9.8."""
        f = tmp_path / "module.py"
        lines = ["force = mass * 9.81\n"]
        result = check_magic_numbers(lines, f)
        assert any("GRAVITY" in msg for _, msg, _ in result)

    def test_skips_constant_definition(self, tmp_path: Path) -> None:
        """Should not flag lines that define the constant."""
        f = tmp_path / "module.py"
        lines = ["GRAVITY_M_S2 = 9.81\n"]
        result = check_magic_numbers(lines, f)
        assert result == []

    def test_skips_self_check_files(self, tmp_path: Path) -> None:
        """Should skip self-check files."""
        f = tmp_path / "matlab_quality_check.py"
        lines = ["val = 3.14159\n"]
        result = check_magic_numbers(lines, f)
        assert result == []

    def test_ignores_magic_numbers_in_comments(self, tmp_path: Path) -> None:
        """Should not flag magic numbers after # comment marker."""
        f = tmp_path / "module.py"
        lines = ["x = 1  # 9.81 is gravity\n"]
        result = check_magic_numbers(lines, f)
        assert result == []


class TestReportIssues:
    """Tests for report_issues()."""

    def test_writes_to_stderr(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Should write output to stderr."""
        issues = [(Path("module.py"), [(1, "TRACKED_TASK found", "x  # TRACKED_TASK")])]
        report_issues(issues)
        captured = capsys.readouterr()
        assert "module.py" in captured.err or "FAILED" in captured.err

    def test_handles_zero_line_number(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Should handle issue with line_num=0 (file-level message)."""
        issues = [(Path("module.py"), [(0, "File-level error", "")])]
        report_issues(issues)
        captured = capsys.readouterr()
        assert "File-level error" in captured.err

    def test_handles_empty_issues(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Should handle empty issues list without raising."""
        report_issues([])
        captured = capsys.readouterr()
        assert "Total issues: 0" in captured.err

    def test_reports_total_issue_count(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Should report the total number of issues."""
        issues = [
            (Path("a.py"), [(1, "Issue 1", "code1"), (2, "Issue 2", "code2")]),
            (Path("b.py"), [(3, "Issue 3", "code3")]),
        ]
        report_issues(issues)
        captured = capsys.readouterr()
        assert "3" in captured.err


class TestAsyncUtils:
    """Tests for async_utils.run_async_task."""

    def test_run_async_task_returns_result(self) -> None:
        """run_async_task should run coroutine and return result."""
        from src.tools.utils.async_utils import run_async_task

        async def main() -> int:
            """Run coroutine."""
            return await run_async_task(_coro())

        async def _coro() -> int:
            """Return 42."""
            return 42

        result = asyncio.run(main())
        assert result == 42
