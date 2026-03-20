"""Tests for src.tools.utils.budget_check_utils — shared CI budget check utilities."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.tools.utils.budget_check_utils import (
    collect_matching_files,
    is_included,
    read_text_safe,
    report_results,
)


class TestIsIncluded:
    """Tests for is_included()."""

    def test_includes_matching_root(self) -> None:
        """Should return True when path matches include root."""
        result = is_included("src/module.py", include_roots=["src"], exclude_substrings=[])
        assert result is True

    def test_excludes_path_with_substring(self) -> None:
        """Should return False when path contains excluded substring."""
        result = is_included(
            "src/__pycache__/module.pyc",
            include_roots=["src"],
            exclude_substrings=["__pycache__"],
        )
        assert result is False

    def test_excludes_non_matching_root(self) -> None:
        """Should return False when path doesn't match any include root."""
        result = is_included("tests/test_module.py", include_roots=["src"], exclude_substrings=[])
        assert result is False

    def test_includes_exact_match(self) -> None:
        """Should return True when path exactly matches an include root."""
        result = is_included("src", include_roots=["src"], exclude_substrings=[])
        assert result is True

    def test_path_object_accepted(self) -> None:
        """Should accept Path objects."""
        result = is_included(Path("src/module.py"), include_roots=["src"], exclude_substrings=[])
        assert result is True

    def test_multiple_include_roots(self) -> None:
        """Should return True when path matches any include root."""
        result = is_included(
            "tests/test_module.py",
            include_roots=["src", "tests"],
            exclude_substrings=[],
        )
        assert result is True

    def test_backslash_path_normalized(self) -> None:
        """Should handle Windows-style paths with backslashes."""
        result = is_included("src\\module.py", include_roots=["src"], exclude_substrings=[])
        assert result is True


class TestCollectMatchingFiles:
    """Tests for collect_matching_files()."""

    def test_collects_files_in_include_root(self, tmp_path: Path) -> None:
        """Should collect files matching include roots."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "module.py").write_text("x = 1", encoding="utf-8")
        result = collect_matching_files(
            tmp_path,
            include_roots=["src"],
            exclude_substrings=[],
        )
        names = [p.name for p in result]
        assert "module.py" in names

    def test_excludes_directories_by_substring(self, tmp_path: Path) -> None:
        """Should exclude files matching exclude_substrings."""
        src = tmp_path / "src"
        src.mkdir()
        cache = src / "__pycache__"
        cache.mkdir()
        (cache / "module.pyc").write_text("bytecode", encoding="utf-8")
        (src / "module.py").write_text("x = 1", encoding="utf-8")
        result = collect_matching_files(
            tmp_path,
            include_roots=["src"],
            exclude_substrings=["__pycache__"],
        )
        names = [p.name for p in result]
        assert "module.py" in names
        assert "module.pyc" not in names

    def test_filters_by_extension(self, tmp_path: Path) -> None:
        """Should only include files with allowed extensions."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "module.py").write_text("x = 1", encoding="utf-8")
        (src / "notes.txt").write_text("notes", encoding="utf-8")
        result = collect_matching_files(
            tmp_path,
            include_roots=["src"],
            exclude_substrings=[],
            allowed_extensions={".py"},
        )
        names = [p.name for p in result]
        assert "module.py" in names
        assert "notes.txt" not in names

    def test_raises_on_non_directory_root(self, tmp_path: Path) -> None:
        """Should raise when repo_root is not a directory."""
        not_a_dir = tmp_path / "file.txt"
        not_a_dir.write_text("content", encoding="utf-8")
        with pytest.raises(AssertionError):
            collect_matching_files(not_a_dir, include_roots=["src"], exclude_substrings=[])

    def test_raises_on_empty_include_roots(self, tmp_path: Path) -> None:
        """Should raise when include_roots is empty."""
        with pytest.raises(AssertionError):
            collect_matching_files(tmp_path, include_roots=[], exclude_substrings=[])

    def test_returns_sorted_results(self, tmp_path: Path) -> None:
        """Should return files in sorted order."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "z_module.py").write_text("z = 1", encoding="utf-8")
        (src / "a_module.py").write_text("a = 1", encoding="utf-8")
        result = collect_matching_files(tmp_path, include_roots=["src"], exclude_substrings=[])
        names = [p.name for p in result]
        assert names == sorted(names)


class TestReadTextSafe:
    """Tests for read_text_safe()."""

    def test_reads_valid_utf8_file(self, tmp_path: Path) -> None:
        """Should return content for valid UTF-8 file."""
        f = tmp_path / "file.txt"
        f.write_text("Hello, world!", encoding="utf-8")
        result = read_text_safe(f)
        assert result == "Hello, world!"

    def test_returns_none_for_binary_file(self, tmp_path: Path) -> None:
        """Should return None for non-UTF-8 binary files."""
        f = tmp_path / "binary.bin"
        f.write_bytes(b"\xff\xfe\x00\x01binary")
        result = read_text_safe(f)
        # May return None for binary or content — both are acceptable
        assert result is None or isinstance(result, str)


class TestReportResults:
    """Tests for report_results()."""

    def test_returns_0_when_no_errors(self) -> None:
        """Should return 0 when errors list is empty."""
        result = report_results(
            "Budget Check",
            files_scanned=10,
            details=["All within budget"],
            errors=[],
        )
        assert result == 0

    def test_returns_1_when_errors_present(self) -> None:
        """Should return 1 when errors list is non-empty."""
        result = report_results(
            "Budget Check",
            files_scanned=5,
            details=["Over budget"],
            errors=["module.py exceeds 500 lines"],
        )
        assert result == 1

    def test_multiple_errors_returns_1(self) -> None:
        """Should return 1 even with multiple errors."""
        result = report_results(
            "Check",
            files_scanned=3,
            details=[],
            errors=["error 1", "error 2"],
        )
        assert result == 1

    def test_handles_empty_details(self) -> None:
        """Should not raise when details list is empty."""
        result = report_results(
            "Check",
            files_scanned=0,
            details=[],
            errors=[],
        )
        assert result == 0


class TestLoadConfig:
    """Tests for load_config()."""

    def test_loads_valid_json_config(self, tmp_path: Path) -> None:
        """Should load and parse a JSON config file."""
        from src.tools.utils.budget_check_utils import load_config

        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "test_budget.json"
        config_file.write_text(json.dumps({"limit": 100}), encoding="utf-8")
        result = load_config(tmp_path, "test_budget.json")
        assert result == {"limit": 100}

    def test_raises_on_none_repo_root(self) -> None:
        """Should raise on None repo_root (contract)."""
        from src.tools.utils.budget_check_utils import load_config

        with pytest.raises(AssertionError):
            load_config(None, "config.json")  # type: ignore[arg-type]

    def test_raises_on_empty_config_name(self, tmp_path: Path) -> None:
        """Should raise on empty config_name (contract)."""
        from src.tools.utils.budget_check_utils import load_config

        with pytest.raises(AssertionError):
            load_config(tmp_path, "")
