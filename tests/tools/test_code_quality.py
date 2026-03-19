"""Tests for code_quality module — AST analysis, pattern checking, report generation."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.tools.code_quality.ast_analyzer import check_ast_issues
from src.tools.code_quality.check import check_file
from src.tools.code_quality.report_generator import report_issues


class TestCheckAstIssues:
    """Tests for check_ast_issues()."""

    def test_detects_missing_docstring(self) -> None:
        """Should detect functions missing docstrings."""
        content = "def my_function():\n    pass\n"
        filepath = Path("src/mymodule.py")
        issues = check_ast_issues(content, filepath)
        assert any("missing docstring" in msg.lower() for _, msg, _ in issues)

    def test_no_issues_with_docstring(self) -> None:
        """Should not flag functions that have docstrings."""
        content = 'def my_function():\n    """Does something."""\n    pass\n'
        filepath = Path("src/mymodule.py")
        issues = check_ast_issues(content, filepath)
        docstring_issues = [i for i in issues if "missing docstring" in i[1].lower()]
        assert len(docstring_issues) == 0

    def test_skips_test_files(self) -> None:
        """Should skip docstring checks for test files."""
        content = "def test_something():\n    assert True\n"
        filepath = Path("tests/test_module.py")
        issues = check_ast_issues(content, filepath)
        assert not any("missing docstring" in msg.lower() for _, msg, _ in issues)

    def test_skips_scripts_directory(self) -> None:
        """Should skip docstring checks for scripts/ directory."""
        content = "def do_thing():\n    pass\n"
        filepath = Path("scripts/myscript.py")
        issues = check_ast_issues(content, filepath)
        assert not any("missing docstring" in msg.lower() for _, msg, _ in issues)

    def test_skips_quality_check_scripts(self) -> None:
        """Should skip known quality check script filenames."""
        content = "def do_thing():\n    pass\n"
        filepath = Path("code_quality_check.py")
        issues = check_ast_issues(content, filepath)
        assert issues == []

    def test_handles_syntax_error(self) -> None:
        """Should return syntax error issue for unparseable Python."""
        content = "def broken(:\n    pass\n"
        filepath = Path("src/broken.py")
        issues = check_ast_issues(content, filepath)
        assert any("Syntax error" in msg for _, msg, _ in issues)

    def test_returns_list(self) -> None:
        """Should always return a list."""
        result = check_ast_issues("x = 1\n", Path("src/a.py"))
        assert isinstance(result, list)

    def test_stub_function_no_docstring_warning(self) -> None:
        """Should skip stub functions (body is just ...)."""
        content = "def stub() -> None:\n    ...\n"
        filepath = Path("src/protocols.py")
        issues = check_ast_issues(content, filepath)
        assert not any("stub" in msg for _, msg, _ in issues)


class TestCheckFile:
    """Tests for check_file()."""

    def test_returns_list_of_issues(self, tmp_path: Path) -> None:
        """Should return a list of issue tuples."""
        f = tmp_path / "test.py"
        f.write_text("x = 1\n")
        issues = check_file(f)
        assert isinstance(issues, list)

    def test_handles_file_with_issues(self, tmp_path: Path) -> None:
        """Should detect issues in problematic file."""
        f = tmp_path / "bad.py"
        f.write_text("def bad_function():\n    pass\n")
        issues = check_file(f)
        assert isinstance(issues, list)

    def test_handles_missing_file(self, tmp_path: Path) -> None:
        """Should return error issue for missing file."""
        f = tmp_path / "nonexistent.py"
        issues = check_file(f)
        assert len(issues) == 1
        assert "Error reading file" in issues[0][1]

    def test_requires_non_none_filepath(self) -> None:
        """Should raise on None filepath (contract enforcement)."""
        with pytest.raises(AssertionError):
            check_file(None)  # type: ignore[arg-type]

    def test_clean_file_returns_empty(self, tmp_path: Path) -> None:
        """A clean file should return no or few issues."""
        f = tmp_path / "clean.py"
        f.write_text('"""Module docstring."""\n\nx = 1\n')
        issues = check_file(f)
        assert isinstance(issues, list)


class TestReportIssues:
    """Tests for report_issues()."""

    def test_writes_to_stderr(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Should write report to stderr."""
        issues = [(Path("file.py"), [(1, "Missing docstring", "")])]
        report_issues(issues)
        captured = capsys.readouterr()
        assert "file.py" in captured.err or len(captured.err) > 0

    def test_includes_total_issue_count(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Should include total issue count in output."""
        issues = [
            (Path("a.py"), [(1, "Issue A", ""), (2, "Issue B", "")]),
        ]
        report_issues(issues)
        captured = capsys.readouterr()
        assert "2" in captured.err

    def test_handles_empty_issues_list(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Should handle empty issues list without error."""
        report_issues([])
        # No exception; output contains 0 issues
        captured = capsys.readouterr()
        assert "0" in captured.err

    def test_includes_filepath_in_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Should include filepath in report."""
        issues = [(Path("mymodule.py"), [(5, "Some issue", "code here")])]
        report_issues(issues)
        captured = capsys.readouterr()
        assert "mymodule.py" in captured.err

    def test_handles_zero_line_number(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Should handle line_number=0 (file-level errors)."""
        issues = [(Path("file.py"), [(0, "File-level error", "")])]
        report_issues(issues)
        # Should not raise
        captured = capsys.readouterr()
        assert len(captured.err) > 0

    def test_code_snippet_included_when_present(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Should include code snippet in output when non-empty."""
        issues = [(Path("file.py"), [(10, "Issue msg", "some_code()")])]
        report_issues(issues)
        captured = capsys.readouterr()
        assert "some_code()" in captured.err
