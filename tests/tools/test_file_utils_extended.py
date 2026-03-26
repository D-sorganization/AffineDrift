"""Additional tests for src.tools.utils.file_utils — covering remaining gaps."""

from __future__ import annotations

from pathlib import Path


class TestFindQmdFiles:
    """Tests for find_qmd_files()."""

    def test_finds_qmd_in_root(self, tmp_path: Path) -> None:
        """Should find .qmd files in root directory."""
        from src.tools.utils.file_utils import find_qmd_files

        (tmp_path / "article.qmd").write_text("content", encoding="utf-8")
        result = find_qmd_files(root_dir=tmp_path)
        names = [p.name for p in result]
        assert "article.qmd" in names

    def test_excludes_configured_dirs(self, tmp_path: Path) -> None:
        """Should exclude directories matching exclude_dirs."""
        from src.tools.utils.file_utils import find_qmd_files

        excluded = tmp_path / "_site"
        excluded.mkdir()
        (excluded / "page.qmd").write_text("content", encoding="utf-8")
        result = find_qmd_files(root_dir=tmp_path, exclude_dirs=["_site"])
        paths_str = [str(p) for p in result]
        assert all("_site" not in s for s in paths_str)

    def test_subdirectory_files_always_included(self, tmp_path: Path) -> None:
        """Should always include files from subdirectories regardless of include_root."""
        from src.tools.utils.file_utils import find_qmd_files

        sub = tmp_path / "content"
        sub.mkdir()
        (sub / "sub.qmd").write_text("content", encoding="utf-8")
        result = find_qmd_files(root_dir=tmp_path, include_root=False)
        names = [p.name for p in result]
        assert "sub.qmd" in names


class TestFindMarkdownFiles:
    """Tests for find_markdown_files()."""

    def test_finds_md_files_in_root(self, tmp_path: Path) -> None:
        """Should find .md files in root directory."""
        from src.tools.utils.file_utils import find_markdown_files

        (tmp_path / "notes.md").write_text("content", encoding="utf-8")
        result = find_markdown_files(root_dir=tmp_path)
        names = [p.name for p in result]
        assert "notes.md" in names

    def test_excludes_readme_by_default(self, tmp_path: Path) -> None:
        """Should exclude README files by default."""
        from src.tools.utils.file_utils import find_markdown_files

        (tmp_path / "README.md").write_text("readme", encoding="utf-8")
        (tmp_path / "notes.md").write_text("notes", encoding="utf-8")
        result = find_markdown_files(root_dir=tmp_path, exclude_readme=True)
        names = [p.name for p in result]
        assert "README.md" not in names
        assert "notes.md" in names

    def test_include_qmd_true(self, tmp_path: Path) -> None:
        """Should include .qmd files when include_qmd=True."""
        from src.tools.utils.file_utils import find_markdown_files

        (tmp_path / "article.qmd").write_text("content", encoding="utf-8")
        result = find_markdown_files(root_dir=tmp_path, include_qmd=True)
        names = [p.name for p in result]
        assert "article.qmd" in names

    def test_searches_specified_subdirs(self, tmp_path: Path) -> None:
        """Should search specified subdirectories."""
        from src.tools.utils.file_utils import find_markdown_files

        articles = tmp_path / "articles"
        articles.mkdir()
        (articles / "story.md").write_text("content", encoding="utf-8")
        result = find_markdown_files(root_dir=tmp_path, search_dirs=["articles"])
        names = [p.name for p in result]
        assert "story.md" in names


class TestFindHtmlFiles:
    """Tests for find_html_files()."""

    def test_finds_html_in_docs_by_default(self, tmp_path: Path) -> None:
        """Should find HTML files in docs/ directory by default."""
        from src.tools.utils.file_utils import find_html_files

        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "page.html").write_text("<html></html>", encoding="utf-8")
        result = find_html_files(root_dir=tmp_path, docs_only=True)
        names = [p.name for p in result]
        assert "page.html" in names

    def test_returns_empty_when_docs_missing(self, tmp_path: Path) -> None:
        """Should return empty list when docs/ directory doesn't exist."""
        from src.tools.utils.file_utils import find_html_files

        result = find_html_files(root_dir=tmp_path, docs_only=True)
        assert result == []

    def test_docs_only_false_searches_root(self, tmp_path: Path) -> None:
        """Should search entire root when docs_only=False."""
        from src.tools.utils.file_utils import find_html_files

        (tmp_path / "index.html").write_text("<html></html>", encoding="utf-8")
        result = find_html_files(root_dir=tmp_path, docs_only=False)
        names = [p.name for p in result]
        assert "index.html" in names

    def test_limit_parameter(self, tmp_path: Path) -> None:
        """Should respect the limit parameter."""
        from src.tools.utils.file_utils import find_html_files

        docs = tmp_path / "docs"
        docs.mkdir()
        for i in range(5):
            (docs / f"page{i}.html").write_text("<html></html>", encoding="utf-8")
        result = find_html_files(root_dir=tmp_path, docs_only=True, limit=2)
        assert len(result) <= 2


class TestGetPythonFiles:
    """Tests for get_python_files()."""

    def test_finds_python_files(self, tmp_path: Path) -> None:
        """Should find .py files in root directory."""
        from src.tools.utils.file_utils import get_python_files

        (tmp_path / "module.py").write_text("x = 1", encoding="utf-8")
        result = get_python_files(root_dir=tmp_path)
        names = [p.name for p in result]
        assert "module.py" in names

    def test_excludes_git_dir(self, tmp_path: Path) -> None:
        """Should exclude .git directory."""
        from src.tools.utils.file_utils import get_python_files

        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "config.py").write_text("x = 1", encoding="utf-8")
        (tmp_path / "module.py").write_text("x = 1", encoding="utf-8")
        result = get_python_files(root_dir=tmp_path)
        paths_str = [str(p) for p in result]
        assert all(".git" not in s for s in paths_str)


class TestFindFilesByExtensionRecursive:
    """Tests for find_files_by_extension() recursive mode."""

    def test_recursive_finds_nested_files(self, tmp_path: Path) -> None:
        """Should find files in nested directories when recursive=True."""
        from src.tools.utils.file_utils import find_files_by_extension

        nested = tmp_path / "sub" / "deep"
        nested.mkdir(parents=True)
        (nested / "file.tex").write_text("content", encoding="utf-8")
        result = find_files_by_extension([".tex"], root_dir=tmp_path, recursive=True)
        assert any("file.tex" in str(p) for p in result)

    def test_non_recursive_skips_subdirs(self, tmp_path: Path) -> None:
        """Should not find files in subdirectories when recursive=False."""
        from src.tools.utils.file_utils import find_files_by_extension

        nested = tmp_path / "sub"
        nested.mkdir()
        (nested / "file.tex").write_text("content", encoding="utf-8")
        result = find_files_by_extension([".tex"], root_dir=tmp_path, recursive=False)
        assert not any("file.tex" in str(p) for p in result)

    def test_recursive_dir_in_paths(self, tmp_path: Path) -> None:
        """Should recursively search a directory given in paths."""
        from src.tools.utils.file_utils import find_files_by_extension

        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "file.tex").write_text("content", encoding="utf-8")
        result = find_files_by_extension([".tex"], paths=[str(sub)], recursive=True)
        assert any("file.tex" in str(p) for p in result)

    def test_non_recursive_dir_in_paths(self, tmp_path: Path) -> None:
        """Should search non-recursively when recursive=False with dir in paths."""
        from src.tools.utils.file_utils import find_files_by_extension

        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "file.tex").write_text("content", encoding="utf-8")
        result = find_files_by_extension([".tex"], paths=[str(sub)], recursive=False)
        assert any("file.tex" in str(p) for p in result)

    def test_extension_without_dot_normalized(self, tmp_path: Path) -> None:
        """Should normalize extensions without leading dot."""
        from src.tools.utils.file_utils import find_files_by_extension

        (tmp_path / "article.tex").write_text("content", encoding="utf-8")
        result = find_files_by_extension(["tex"], root_dir=tmp_path)
        assert any("article.tex" in str(p) for p in result)
