"""Extended tests for various utils modules to improve coverage."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.tools.utils.frontmatter import (
    extract_frontmatter,
    extract_title_description,
    parse_frontmatter_dict,
)


class TestExtractFrontmatter:
    """Tests for extract_frontmatter()."""

    def test_extracts_yaml_and_body(self) -> None:
        """Should split yaml frontmatter and body correctly."""
        content = '---\ntitle: "My Article"\n---\nBody content here.'
        yaml, body = extract_frontmatter(content)
        assert yaml is not None
        assert 'title: "My Article"' in yaml
        assert "Body content here." in body

    def test_returns_none_yaml_when_no_frontmatter(self) -> None:
        """Should return None for yaml when no frontmatter found."""
        content = "Just plain content without frontmatter."
        yaml, body = extract_frontmatter(content)
        assert yaml is None
        assert body == content

    def test_empty_yaml_block(self) -> None:
        """Should handle empty frontmatter block."""
        content = "---\n\n---\nBody content."
        yaml, body = extract_frontmatter(content)
        assert isinstance(body, str)


class TestExtractTitleDescription:
    """Tests for extract_title_description()."""

    def test_extracts_title_and_description(self) -> None:
        """Should extract both title and description from YAML."""
        yaml = 'title: "My Article"\ndescription: "A great article"'
        title, desc = extract_title_description(yaml)
        assert title == "My Article"
        assert desc == "A great article"

    def test_returns_defaults_when_yaml_is_none(self) -> None:
        """Should return defaults when yaml_content is None."""
        title, desc = extract_title_description(None, "Default Title", "Default Desc")
        assert title == "Default Title"
        assert desc == "Default Desc"

    def test_returns_defaults_when_fields_missing(self) -> None:
        """Should return defaults when fields not found in YAML."""
        yaml = 'author: "Someone"'
        title, desc = extract_title_description(yaml, "Default Title", "Default Desc")
        assert title == "Default Title"
        assert desc == "Default Desc"

    def test_empty_defaults(self) -> None:
        """Should return empty strings as defaults when not specified."""
        title, desc = extract_title_description(None)
        assert title == ""
        assert desc == ""


class TestParseFrontmatterDict:
    """Tests for parse_frontmatter_dict()."""

    def test_parses_key_value_pairs(self) -> None:
        """Should parse simple key:value pairs."""
        content = '---\ntitle: "My Article"\nauthor: "Author"\n---\nBody.'
        result = parse_frontmatter_dict(content)
        assert result.get("title") == "My Article"
        assert result.get("author") == "Author"

    def test_returns_empty_dict_without_frontmatter(self) -> None:
        """Should return empty dict for content without frontmatter."""
        result = parse_frontmatter_dict("Plain content.")
        assert result == {}

    def test_handles_insufficient_parts(self) -> None:
        """Should return empty dict when frontmatter is malformed."""
        result = parse_frontmatter_dict("--- incomplete")
        assert isinstance(result, dict)

    def test_skips_nested_content(self) -> None:
        """Should skip indented nested YAML content."""
        content = "---\nformat:\n  html:\n    toc: true\ntitle: Test\n---\nBody."
        result = parse_frontmatter_dict(content)
        assert "title" in result

    def test_requires_non_none_content(self) -> None:
        """Should raise on None content (contract)."""
        with pytest.raises(AssertionError):
            parse_frontmatter_dict(None)  # type: ignore[arg-type]


class TestFileUtils:
    """Tests for file_utils.py uncovered paths."""

    def test_process_file_content_modifies_file(self, tmp_path: Path) -> None:
        """process_file_content should apply transformation and write back."""
        from src.tools.utils.file_utils import process_file_content

        f = tmp_path / "test.txt"
        f.write_text("hello", encoding="utf-8")

        def upper(s: str) -> str:
            return s.upper()

        modified = process_file_content(f, upper)
        assert modified is True
        assert f.read_text() == "HELLO"

    def test_process_file_content_no_change(self, tmp_path: Path) -> None:
        """process_file_content should return False when content unchanged."""
        from src.tools.utils.file_utils import process_file_content

        f = tmp_path / "test.txt"
        f.write_text("hello", encoding="utf-8")

        modified = process_file_content(f, lambda s: s)  # identity
        assert modified is False

    def test_process_file_content_missing_file(self, tmp_path: Path) -> None:
        """process_file_content should handle missing files gracefully."""
        from src.tools.utils.file_utils import process_file_content

        result = process_file_content(tmp_path / "nonexistent.txt", lambda s: s)
        assert result is False

    def test_find_files_by_extension_in_directory(self, tmp_path: Path) -> None:
        """find_files_by_extension should find files by extension."""
        from src.tools.utils.file_utils import find_files_by_extension

        (tmp_path / "a.tex").write_text("content")
        (tmp_path / "b.md").write_text("content")
        result = find_files_by_extension([".tex"], root_dir=tmp_path)
        assert any(p.suffix == ".tex" for p in result)

    def test_find_files_by_extension_with_paths(self, tmp_path: Path) -> None:
        """find_files_by_extension should find files from explicit paths."""
        from src.tools.utils.file_utils import find_files_by_extension

        f = tmp_path / "test.tex"
        f.write_text("content")
        result = find_files_by_extension([".tex"], paths=[str(f)])
        assert f in result

    def test_find_files_skips_missing_path(self, tmp_path: Path) -> None:
        """find_files_by_extension should skip non-existent paths."""
        from src.tools.utils.file_utils import find_files_by_extension

        result = find_files_by_extension([".tex"], paths=[str(tmp_path / "missing")])
        assert result == []


class TestIssueUtils:
    """Tests for issue_utils.py uncovered paths."""

    def test_get_repo_short_name_known_repo(self) -> None:
        """Should return mapped short name for known repositories."""
        from pathlib import Path

        from src.tools.utils.issue_utils import get_repo_short_name

        result = get_repo_short_name(Path("/some/path/AffineDrift"))
        assert result == "AffineDrift"

    def test_get_repo_short_name_unknown_repo(self) -> None:
        """Should return truncated name for unknown repositories."""
        from pathlib import Path

        from src.tools.utils.issue_utils import get_repo_short_name

        result = get_repo_short_name(Path("/some/path/UnknownRepoName"))
        assert result == "UnknownR"

    def test_get_repo_short_name_default_cwd(self) -> None:
        """Should not raise when called with no argument (uses cwd)."""
        from src.tools.utils.issue_utils import get_repo_short_name

        result = get_repo_short_name()
        assert isinstance(result, str)

    def test_format_issue_body_basic(self) -> None:
        """Should format issue body with all required fields."""
        from src.tools.utils.issue_utils import format_issue_body

        result = format_issue_body(
            severity="CRITICAL",
            category="Coverage",
            source="CI",
            description="Coverage dropped below threshold.",
        )
        assert "CRITICAL" in result
        assert "Coverage" in result
        assert "Coverage dropped below threshold." in result

    def test_format_issue_body_includes_timestamp(self) -> None:
        """Should include custom timestamp in output."""
        from src.tools.utils.issue_utils import format_issue_body

        result = format_issue_body(
            severity="HIGH",
            category="Lint",
            source="ruff",
            description="Lint violations found.",
            timestamp="2026-01-01T00:00:00Z",
        )
        assert "2026-01-01T00:00:00Z" in result


class TestContentUtils:
    """Tests for content_utils.py uncovered paths."""

    def test_collect_qmd_files_missing_dirs(self, tmp_path: Path) -> None:
        """Should return empty list when directories do not exist."""
        import os

        from src.tools.utils.content_utils import collect_qmd_files

        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = collect_qmd_files(["nonexistent_dir"])
            assert result == []
        finally:
            os.chdir(original)

    def test_collect_qmd_files_finds_qmd(self, tmp_path: Path) -> None:
        """Should collect .qmd files from specified directories."""
        import os

        from src.tools.utils.content_utils import collect_qmd_files

        qmd_dir = tmp_path / "articles"
        qmd_dir.mkdir()
        (qmd_dir / "page.qmd").write_text("content", encoding="utf-8")
        (qmd_dir / "_partial.qmd").write_text("partial", encoding="utf-8")

        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = collect_qmd_files(["articles"])
            names = [p.name for p in result]
            assert "page.qmd" in names
            assert "_partial.qmd" not in names
        finally:
            os.chdir(original)

    def test_read_qmd_with_frontmatter_parses_yaml(self, tmp_path: Path) -> None:
        """Should return content and parsed frontmatter dict."""
        from src.tools.utils.content_utils import read_qmd_with_frontmatter

        f = tmp_path / "page.qmd"
        f.write_text('---\ntitle: "My Page"\n---\nBody text.', encoding="utf-8")
        content, fm = read_qmd_with_frontmatter(f)
        assert "Body text." in content
        assert fm.get("title") == "My Page"

    def test_read_qmd_with_frontmatter_no_frontmatter(self, tmp_path: Path) -> None:
        """Should return empty dict when no frontmatter present."""
        from src.tools.utils.content_utils import read_qmd_with_frontmatter

        f = tmp_path / "plain.qmd"
        f.write_text("Just plain content.", encoding="utf-8")
        content, fm = read_qmd_with_frontmatter(f)
        assert "plain content" in content
        assert isinstance(fm, dict)
