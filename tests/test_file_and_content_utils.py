"""Tests for file_utils and content_utils — coverage ratchet to 70%.

Covers the low-coverage utility modules:
  - src/tools/utils/file_utils.py  (was 16.9%)
  - src/tools/utils/content_utils.py (was 30.8%)
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from src.core.contracts.definitions import ContractViolationError
from src.tools.utils.content_utils import (
    collect_qmd_files,
    read_qmd_with_frontmatter,
)
from src.tools.utils.file_utils import (
    find_files_by_extension,
    find_markdown_files,
    find_qmd_files,
)

# ─────────────────────────────────────────────────────────────────────────────
# content_utils tests
# ─────────────────────────────────────────────────────────────────────────────


class TestCollectQmdFiles:
    def test_empty_dirs_returns_empty(self, tmp_path: Path) -> None:
        result = collect_qmd_files(content_dirs=[str(tmp_path / "nonexistent")])
        assert result == []

    def test_collects_qmd_files(self, tmp_path: Path) -> None:
        (tmp_path / "page.qmd").write_text("# Hello", encoding="utf-8")
        (tmp_path / "other.md").write_text("# Other", encoding="utf-8")
        result = collect_qmd_files(content_dirs=[str(tmp_path)])
        assert len(result) == 1
        assert result[0].name == "page.qmd"

    def test_excludes_underscore_prefixed(self, tmp_path: Path) -> None:
        (tmp_path / "_partial.qmd").write_text("# Partial", encoding="utf-8")
        (tmp_path / "normal.qmd").write_text("# Normal", encoding="utf-8")
        result = collect_qmd_files(content_dirs=[str(tmp_path)])
        names = [f.name for f in result]
        assert "normal.qmd" in names
        assert "_partial.qmd" not in names

    def test_returns_sorted(self, tmp_path: Path) -> None:
        for name in ["z.qmd", "a.qmd", "m.qmd"]:
            (tmp_path / name).write_text("", encoding="utf-8")
        result = collect_qmd_files(content_dirs=[str(tmp_path)])
        assert [f.name for f in result] == ["a.qmd", "m.qmd", "z.qmd"]

    def test_uses_default_dirs_when_none(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / "index.qmd").write_text("# Index", encoding="utf-8")
        result = collect_qmd_files()
        assert any(f.name == "index.qmd" for f in result)

    def test_multiple_dirs(self, tmp_path: Path) -> None:
        dir_a = tmp_path / "a"
        dir_b = tmp_path / "b"
        dir_a.mkdir()
        dir_b.mkdir()
        (dir_a / "page1.qmd").write_text("", encoding="utf-8")
        (dir_b / "page2.qmd").write_text("", encoding="utf-8")
        result = collect_qmd_files(content_dirs=[str(dir_a), str(dir_b)])
        names = {f.name for f in result}
        assert names == {"page1.qmd", "page2.qmd"}


class TestReadQmdWithFrontmatter:
    def test_reads_valid_frontmatter(self, tmp_path: Path) -> None:
        qmd = tmp_path / "test.qmd"
        qmd.write_text(
            textwrap.dedent(
                """\
                ---
                title: My Page
                date: 2026-01-01
                ---
                # Content
            """
            ),
            encoding="utf-8",
        )
        content, fm = read_qmd_with_frontmatter(qmd)
        assert "# Content" in content
        assert fm.get("title") == "My Page"

    def test_handles_missing_frontmatter(self, tmp_path: Path) -> None:
        qmd = tmp_path / "nofm.qmd"
        qmd.write_text("# Just content\n", encoding="utf-8")
        content, fm = read_qmd_with_frontmatter(qmd)
        assert "Just content" in content
        assert isinstance(fm, dict)

    def test_handles_malformed_frontmatter(self, tmp_path: Path) -> None:
        qmd = tmp_path / "bad.qmd"
        qmd.write_text("---\n: invalid: yaml:\n---\n# Content\n", encoding="utf-8")
        content, fm = read_qmd_with_frontmatter(qmd)
        assert isinstance(fm, dict)  # Falls back to empty dict

    def test_requires_existing_file(self, tmp_path: Path) -> None:
        with pytest.raises((ContractViolationError, FileNotFoundError, OSError)):
            read_qmd_with_frontmatter(tmp_path / "nonexistent.qmd")

    def test_requires_non_none_path(self) -> None:
        with pytest.raises((ContractViolationError, TypeError, AttributeError)):
            read_qmd_with_frontmatter(None)  # type: ignore[arg-type]


# ─────────────────────────────────────────────────────────────────────────────
# file_utils tests
# ─────────────────────────────────────────────────────────────────────────────


class TestFindQmdFiles:
    def test_finds_qmd_in_root(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / "index.qmd").write_text("", encoding="utf-8")
        result = find_qmd_files(root_dir=tmp_path)
        assert any(f.name == "index.qmd" for f in result)

    def test_excludes_site_dir(self, tmp_path: Path) -> None:
        site = tmp_path / "_site"
        site.mkdir()
        (site / "output.qmd").write_text("", encoding="utf-8")
        (tmp_path / "real.qmd").write_text("", encoding="utf-8")
        result = find_qmd_files(root_dir=tmp_path, exclude_dirs=["_site"])
        names = [f.name for f in result]
        assert "real.qmd" in names
        assert "output.qmd" not in names

    def test_include_root_false(self, tmp_path: Path) -> None:
        # When include_root=False, root-level files are not added in the iterdir block.
        # However rglob still traverses subdirs correctly.
        subdir = tmp_path / "articles"
        subdir.mkdir()
        (subdir / "article.qmd").write_text("", encoding="utf-8")
        result = find_qmd_files(root_dir=tmp_path, include_root=False, exclude_dirs=[])
        names = [f.name for f in result]
        # Subdirectory files ARE included
        assert "article.qmd" in names

    def test_empty_dir_returns_empty(self, tmp_path: Path) -> None:
        result = find_qmd_files(root_dir=tmp_path)
        assert isinstance(result, list)


class TestFindMarkdownFiles:
    def test_finds_md_files(self, tmp_path: Path) -> None:
        articles = tmp_path / "articles"
        articles.mkdir()
        (articles / "post.md").write_text("# Post", encoding="utf-8")
        result = find_markdown_files(root_dir=tmp_path, search_dirs=["articles"])
        assert any(f.name == "post.md" for f in result)

    def test_exclude_readme(self, tmp_path: Path) -> None:
        # Root-level README is excluded; regular files are included
        (tmp_path / "README.md").write_text("# Readme", encoding="utf-8")
        (tmp_path / "real.md").write_text("# Real", encoding="utf-8")
        result = find_markdown_files(root_dir=tmp_path, exclude_readme=True, search_dirs=[])
        names = [f.name for f in result]
        assert "real.md" in names
        assert "README.md" not in names

    def test_include_qmd(self, tmp_path: Path) -> None:
        articles = tmp_path / "articles"
        articles.mkdir()
        (articles / "page.qmd").write_text("# Page", encoding="utf-8")
        result = find_markdown_files(root_dir=tmp_path, include_qmd=True, search_dirs=["articles"])
        assert any(f.suffix == ".qmd" for f in result)

    def test_empty_result_when_no_dirs(self, tmp_path: Path) -> None:
        result = find_markdown_files(root_dir=tmp_path, search_dirs=["nonexistent"])
        assert result == []


class TestFindFilesByExtension:
    def test_finds_by_extension(self, tmp_path: Path) -> None:
        (tmp_path / "file.tex").write_text("content", encoding="utf-8")
        (tmp_path / "other.py").write_text("code", encoding="utf-8")
        result = find_files_by_extension([".tex"], root_dir=tmp_path)
        assert any(f.suffix == ".tex" for f in result)
        assert not any(f.suffix == ".py" for f in result)

    def test_multiple_extensions(self, tmp_path: Path) -> None:
        (tmp_path / "a.tex").write_text("", encoding="utf-8")
        (tmp_path / "b.bib").write_text("", encoding="utf-8")
        result = find_files_by_extension([".tex", ".bib"], root_dir=tmp_path)
        suffixes = {f.suffix for f in result}
        assert ".tex" in suffixes
        assert ".bib" in suffixes

    def test_returns_empty_on_no_match(self, tmp_path: Path) -> None:
        result = find_files_by_extension([".xyz"], root_dir=tmp_path)
        assert result == []

    def test_with_explicit_paths(self, tmp_path: Path) -> None:
        f = tmp_path / "file.tex"
        f.write_text("", encoding="utf-8")
        result = find_files_by_extension([".tex"], paths=[str(tmp_path)])
        assert any(fp.suffix == ".tex" for fp in result)

    def test_recursive_search(self, tmp_path: Path) -> None:
        subdir = tmp_path / "sub"
        subdir.mkdir()
        (subdir / "deep.tex").write_text("", encoding="utf-8")
        result = find_files_by_extension([".tex"], root_dir=tmp_path, recursive=True)
        assert any(f.name == "deep.tex" for f in result)

    def test_requires_non_empty_extensions(self) -> None:
        with pytest.raises(ContractViolationError):
            find_files_by_extension([])
