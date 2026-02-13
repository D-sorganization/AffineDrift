"""Tests for the shared budget_check_utils module (DRY consolidation).

Validates the core shared utilities used by all check_* budget scripts.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.tools.utils.budget_check_utils import (
    collect_matching_files,
    is_included,
    load_config,
    read_text_safe,
    report_results,
)

# ─── is_included ─────────────────────────────────────────────────


class TestIsIncluded:
    """Tests for the is_included path filter."""

    def test_included_when_prefix_matches(self) -> None:
        assert is_included("src/tools/foo.py", ["src"], [])

    def test_excluded_when_substring_matches(self) -> None:
        assert not is_included("src/tools/__pycache__/foo.pyc", ["src"], ["__pycache__"])

    def test_not_included_without_matching_root(self) -> None:
        assert not is_included("docs/readme.md", ["src"], [])

    def test_exact_root_match(self) -> None:
        assert is_included("src", ["src"], [])

    def test_path_object(self) -> None:
        assert is_included(Path("src/tools/foo.py"), ["src"], [])

    def test_backslash_normalization(self) -> None:
        assert is_included(Path("src\\tools\\foo.py"), ["src"], [])


# ─── load_config ─────────────────────────────────────────────────


class TestLoadConfig:
    """Tests for load_config."""

    def test_loads_json(self, tmp_path: Path) -> None:
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "test.json").write_text('{"key": "value"}', encoding="utf-8")
        result = load_config(tmp_path, "test.json")
        assert result == {"key": "value"}

    def test_missing_config_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_config(tmp_path, "nonexistent.json")


# ─── collect_matching_files ──────────────────────────────────────


class TestCollectMatchingFiles:
    """Tests for collect_matching_files."""

    def test_filters_by_include_root(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        (src / "a.py").write_text("pass", encoding="utf-8")
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "b.py").write_text("pass", encoding="utf-8")

        files = collect_matching_files(tmp_path, ["src"], [])
        assert len(files) == 1
        assert files[0].name == "a.py"

    def test_filters_by_extension(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        (src / "a.py").write_text("pass", encoding="utf-8")
        (src / "b.txt").write_text("hello", encoding="utf-8")

        files = collect_matching_files(tmp_path, ["src"], [], {".py"})
        assert len(files) == 1
        assert files[0].suffix == ".py"

    def test_excludes_substrings(self, tmp_path: Path) -> None:
        src = tmp_path / "src" / "__pycache__"
        src.mkdir(parents=True)
        (src / "cached.pyc").write_text("", encoding="utf-8")

        files = collect_matching_files(tmp_path, ["src"], ["__pycache__"])
        assert len(files) == 0


# ─── read_text_safe ──────────────────────────────────────────────


class TestReadTextSafe:
    """Tests for read_text_safe."""

    def test_reads_text(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("hello", encoding="utf-8")
        assert read_text_safe(f) == "hello"

    def test_returns_none_for_binary(self, tmp_path: Path) -> None:
        f = tmp_path / "test.bin"
        f.write_bytes(b"\x00\x01\x02\xff")
        assert read_text_safe(f) is None


# ─── report_results ──────────────────────────────────────────────


class TestReportResults:
    """Tests for report_results."""

    def test_returns_zero_on_no_errors(self, capsys: pytest.CaptureFixture[str]) -> None:
        code = report_results("Test check", 5, ["detail1"], [])
        assert code == 0
        assert "Test check" in capsys.readouterr().out

    def test_returns_one_on_errors(self, capsys: pytest.CaptureFixture[str]) -> None:
        code = report_results("Test check", 5, [], ["boom"])
        assert code == 1
        assert "ERROR: boom" in capsys.readouterr().out
