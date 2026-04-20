"""Tests for scripts/check_logging_consistency — print() enforcement in src/.

Verifies that the checker:
- Detects actual print() call statements
- Does NOT flag string literals containing 'print(' (false-positive guard)
- Does NOT flag print() inside non-statement contexts
- Returns exit code 0 for a clean codebase
"""

from __future__ import annotations

from pathlib import Path

from scripts.check_logging_consistency import check_file, find_print_calls, main


class TestFindPrintCalls:
    """Unit tests for the AST-based print() detector."""

    def test_detects_bare_print_call(self) -> None:
        """Should detect a simple print() statement."""
        source = 'print("hello")\n'
        result = find_print_calls(source)
        assert result == [1]

    def test_detects_print_with_f_string(self) -> None:
        """Should detect print(f'...')."""
        source = 'x = 1\nprint(f"value={x}")\n'
        result = find_print_calls(source)
        assert result == [2]

    def test_does_not_flag_string_literal(self) -> None:
        """String 'print(' inside a value must NOT be reported."""
        source = 'usage = 1 if "print(" in content else 0\n'
        result = find_print_calls(source)
        assert result == []

    def test_does_not_flag_comment(self) -> None:
        """Comments containing print( must NOT be flagged."""
        source = "# print(x) -- do not use\nx = 1\n"
        result = find_print_calls(source)
        assert result == []

    def test_does_not_flag_docstring(self) -> None:
        """Docstrings mentioning print() must NOT be flagged."""
        source = '"""Use logging, not print(x)."""\nlogger.info("ok")\n'
        result = find_print_calls(source)
        assert result == []

    def test_multiple_print_calls(self) -> None:
        """Should return all line numbers when multiple print() calls exist."""
        source = 'print("a")\nx = 1\nprint("b")\n'
        result = find_print_calls(source)
        assert result == [1, 3]

    def test_syntax_error_returns_empty(self) -> None:
        """Unparseable source should return empty list (graceful skip)."""
        result = find_print_calls("def broken(\n")
        assert result == []

    def test_empty_file_returns_empty(self) -> None:
        """Empty source should return empty list."""
        result = find_print_calls("")
        assert result == []

    def test_logging_call_not_flagged(self) -> None:
        """Logging calls must NOT be flagged."""
        source = 'import logging\nlogger = logging.getLogger(__name__)\nlogger.info("ok")\n'
        result = find_print_calls(source)
        assert result == []


class TestCheckFile:
    """Integration tests for check_file()."""

    def test_clean_file_returns_empty(self, tmp_path: Path) -> None:
        """A file with no print() calls should return no violations."""
        f = tmp_path / "clean.py"
        f.write_text(
            "import logging\nlogger = logging.getLogger(__name__)\nlogger.info('hi')\n",
            encoding="utf-8",
        )
        result = check_file(f)
        assert result == []

    def test_file_with_print_returns_violation(self, tmp_path: Path) -> None:
        """A file with a print() call should return a violation string."""
        f = tmp_path / "bad.py"
        f.write_text('print("oops")\n', encoding="utf-8")
        result = check_file(f)
        assert len(result) == 1
        assert "print() call found" in result[0]
        assert "line 1" in result[0]

    def test_false_positive_string_literal_not_flagged(self, tmp_path: Path) -> None:
        """String literal containing print( must not be flagged."""
        f = tmp_path / "analysis_utils.py"
        f.write_text(
            'print_usage = 1 if "print(" in content else 0\n',
            encoding="utf-8",
        )
        result = check_file(f)
        assert result == []

    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        """Non-existent file should return empty list (graceful)."""
        result = check_file(tmp_path / "nonexistent.py")
        assert result == []


class TestMain:
    """End-to-end tests for the main() entry point."""

    def test_clean_src_exits_zero(self) -> None:
        """Running against the real src/ (which has no print() calls) must exit 0."""
        result = main()
        assert result == 0
