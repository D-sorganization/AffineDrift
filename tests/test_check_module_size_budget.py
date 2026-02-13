"""Tests for module size budget helpers."""

from pathlib import Path

from scripts.check_module_size_budget import is_included, line_count


def test_line_count_counts_non_newline_terminated_files(tmp_path: Path) -> None:
    path = tmp_path / "sample.py"
    path.write_text("a\nb", encoding="utf-8")
    assert line_count(path) == 2


def test_is_included_applies_include_and_exclude_rules() -> None:
    assert is_included("src/core/x.py", ["src"], ["archive/"])
    assert not is_included("archive/src/core/x.py", ["src", "archive"], ["archive/"])
