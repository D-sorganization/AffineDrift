"""Tests for scripts.mypy_io - file I/O, path safety, and mypy output parsing."""

import textwrap

from scripts.mypy_io import (
    is_safe_path,
    parse_mypy_output,
    read_file_lines,
    write_file_lines,
)


class TestParseMyPyOutput:
    def test_parses_single_error(self):
        raw = "src/foo.py:10:5: error: Name 'X' is not defined  [name-defined]\n"
        errors = parse_mypy_output(raw)
        assert len(errors) == 1
        e = errors[0]
        assert e.file == "src/foo.py"
        assert e.line == 10
        assert e.column == 5
        assert e.code == "name-defined"
        assert "X" in e.message

    def test_skips_notes(self):
        raw = "src/foo.py:3:1: note: See declaration  [misc]\n"
        assert parse_mypy_output(raw) == []

    def test_skips_errors_without_code(self):
        raw = "src/foo.py:3:1: error: Some problem\n"
        assert parse_mypy_output(raw) == []

    def test_multiple_errors(self):
        raw = textwrap.dedent("""\
            src/a.py:1:1: error: Msg A  [arg-type]
            src/b.py:2:2: error: Msg B  [return-value]
            """)
        errors = parse_mypy_output(raw)
        assert len(errors) == 2
        assert errors[0].file == "src/a.py"
        assert errors[1].file == "src/b.py"

    def test_empty_output(self):
        assert parse_mypy_output("") == []


class TestIsSafePath:
    def test_src_py_is_safe(self):
        assert is_safe_path("src/mymodule/foo.py")

    def test_tests_py_is_safe(self):
        assert is_safe_path("tests/test_foo.py")

    def test_scripts_not_safe(self):
        assert not is_safe_path("scripts/something.py")

    def test_hidden_dir_not_safe(self):
        assert not is_safe_path("src/.hidden/foo.py")

    def test_pycache_not_safe(self):
        assert not is_safe_path("src/__pycache__/foo.py")

    def test_vendor_not_safe(self):
        assert not is_safe_path("src/vendor/lib.py")

    def test_non_py_not_safe(self):
        assert not is_safe_path("src/module/data.json")


class TestReadWriteFileLines:
    def test_round_trip(self, tmp_path):
        p = tmp_path / "test.py"
        p.write_text("line1\nline2\n", encoding="utf-8")
        lines = read_file_lines(str(p))
        assert lines == ["line1\n", "line2\n"]
        lines.append("line3\n")
        write_file_lines(str(p), lines)
        assert p.read_text(encoding="utf-8") == "line1\nline2\nline3\n"

    def test_missing_file_returns_empty(self):
        assert read_file_lines("/nonexistent/path/file.py") == []

    def test_write_creates_file(self, tmp_path):
        p = tmp_path / "new.py"
        write_file_lines(str(p), ["x = 1\n"])
        assert p.read_text(encoding="utf-8") == "x = 1\n"
