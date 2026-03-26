"""Tests for file discovery and path utilities."""

from __future__ import annotations

from pathlib import Path

from src.tools.utils import file_utils


def test_imports():
    assert file_utils


def test_get_python_files():
    files = file_utils.get_python_files(".")
    assert isinstance(files, list)
    # Ensure it returns Path objects
    if files:
        assert isinstance(files[0], Path)


def test_find_qmd_files_finds_qmd_files(tmp_path: Path) -> None:
    """find_qmd_files should discover .qmd files in subdirectories."""
    sub = tmp_path / "chapters"
    sub.mkdir()
    (sub / "intro.qmd").write_text("# Intro", encoding="utf-8")
    (sub / "notes.md").write_text("notes", encoding="utf-8")

    result = file_utils.find_qmd_files(tmp_path, exclude_dirs=[], include_root=False)
    assert any(f.name == "intro.qmd" for f in result)
    assert not any(f.name == "notes.md" for f in result)


def test_find_qmd_files_includes_root_files(tmp_path: Path) -> None:
    """find_qmd_files with include_root=True should find root-level .qmd files."""
    (tmp_path / "index.qmd").write_text("# Index", encoding="utf-8")
    result = file_utils.find_qmd_files(tmp_path, exclude_dirs=[], include_root=True)
    assert any(f.name == "index.qmd" for f in result)


def test_find_qmd_files_respects_exclude_dirs(tmp_path: Path) -> None:
    """find_qmd_files should skip excluded directories."""
    excluded = tmp_path / "docs"
    excluded.mkdir()
    (excluded / "hidden.qmd").write_text("# Hidden", encoding="utf-8")

    result = file_utils.find_qmd_files(tmp_path, exclude_dirs=["docs"], include_root=False)
    assert not any(f.name == "hidden.qmd" for f in result)


def test_find_markdown_files_finds_md_files(tmp_path: Path) -> None:
    """find_markdown_files should discover .md files in root directory."""
    (tmp_path / "readme.md").write_text("notes", encoding="utf-8")
    result = file_utils.find_markdown_files(tmp_path, search_dirs=[])
    assert any(f.name == "readme.md" for f in result)


def test_find_markdown_files_excludes_readme_when_flagged(tmp_path: Path) -> None:
    """find_markdown_files with exclude_readme=True should skip README files."""
    (tmp_path / "README.md").write_text("readme", encoding="utf-8")
    (tmp_path / "notes.md").write_text("notes", encoding="utf-8")
    result = file_utils.find_markdown_files(tmp_path, exclude_readme=True, search_dirs=[])
    names = [f.name for f in result]
    assert "README.md" not in names
    assert "notes.md" in names


def test_find_markdown_files_includes_qmd_when_flagged(tmp_path: Path) -> None:
    """find_markdown_files with include_qmd=True should include .qmd files."""
    (tmp_path / "doc.qmd").write_text("# Doc", encoding="utf-8")
    result = file_utils.find_markdown_files(tmp_path, include_qmd=True, search_dirs=[])
    assert any(f.name == "doc.qmd" for f in result)


def test_find_markdown_files_searches_specified_dirs(tmp_path: Path) -> None:
    """find_markdown_files should search specified subdirectories."""
    articles = tmp_path / "articles"
    articles.mkdir()
    (articles / "post.md").write_text("post", encoding="utf-8")
    result = file_utils.find_markdown_files(tmp_path, search_dirs=["articles"])
    assert any(f.name == "post.md" for f in result)


def test_find_files_by_extension_in_root(tmp_path: Path) -> None:
    """find_files_by_extension without paths should scan root_dir."""
    (tmp_path / "module.py").write_text("x=1", encoding="utf-8")
    result = file_utils.find_files_by_extension([".py"], root_dir=tmp_path)
    assert any(f.name == "module.py" for f in result)


def test_find_files_by_extension_recursive(tmp_path: Path) -> None:
    """find_files_by_extension with recursive=True searches subdirectories."""
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "nested.py").write_text("x=1", encoding="utf-8")
    result = file_utils.find_files_by_extension([".py"], root_dir=tmp_path, recursive=True)
    assert any(f.name == "nested.py" for f in result)


def test_find_files_by_extension_with_paths_skips_nonexistent(tmp_path: Path) -> None:
    """find_files_by_extension should skip paths that don't exist."""
    missing = tmp_path / "no_such_dir"
    result = file_utils.find_files_by_extension([".py"], paths=[str(missing)])
    assert result == []


def test_find_files_by_extension_with_specific_file(tmp_path: Path) -> None:
    """find_files_by_extension should include matching files passed directly."""
    f = tmp_path / "example.py"
    f.write_text("x=1", encoding="utf-8")
    result = file_utils.find_files_by_extension([".py"], paths=[str(f)])
    assert f in result


def test_find_files_by_extension_with_directory_recursive(tmp_path: Path) -> None:
    """find_files_by_extension with a dir path and recursive=True."""
    sub = tmp_path / "pkg"
    sub.mkdir()
    (sub / "a.py").write_text("x=1", encoding="utf-8")
    result = file_utils.find_files_by_extension([".py"], paths=[str(sub)], recursive=True)
    assert any(f.name == "a.py" for f in result)


def test_process_file_content_returns_true_when_changed(tmp_path: Path) -> None:
    """process_file_content should return True when the transform changed content."""
    f = tmp_path / "file.txt"
    f.write_text("hello", encoding="utf-8")
    changed = file_utils.process_file_content(f, lambda c: c + " world")
    assert changed is True
    assert f.read_text(encoding="utf-8") == "hello world"


def test_process_file_content_returns_false_when_unchanged(tmp_path: Path) -> None:
    """process_file_content should return False when content is unchanged."""
    f = tmp_path / "file.txt"
    f.write_text("hello", encoding="utf-8")
    changed = file_utils.process_file_content(f, lambda c: c)
    assert changed is False


def test_process_file_content_returns_false_on_unicode_error(tmp_path: Path) -> None:
    """process_file_content should return False for non-UTF-8 files."""
    f = tmp_path / "binary.bin"
    f.write_bytes(bytes([0xFF, 0xFE, 0x00]))
    changed = file_utils.process_file_content(f, lambda c: c + "x")
    assert changed is False


def test_process_file_content_returns_false_when_file_not_found(tmp_path: Path) -> None:
    """process_file_content should return False when file doesn't exist."""
    missing = tmp_path / "ghost.txt"
    changed = file_utils.process_file_content(missing, lambda c: c)
    assert changed is False


def test_find_html_files_returns_empty_when_no_docs_dir(tmp_path: Path) -> None:
    """find_html_files with docs_only=True returns [] when docs/ doesn't exist."""
    result = file_utils.find_html_files(root_dir=tmp_path, docs_only=True)
    assert result == []


def test_find_html_files_finds_html_in_docs(tmp_path: Path) -> None:
    """find_html_files should discover .html files inside docs/."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "page.html").write_text("<html/>", encoding="utf-8")
    result = file_utils.find_html_files(root_dir=tmp_path, docs_only=True)
    assert any(f.name == "page.html" for f in result)


def test_find_html_files_respects_limit(tmp_path: Path) -> None:
    """find_html_files should honor the limit parameter."""
    docs = tmp_path / "docs"
    docs.mkdir()
    for i in range(5):
        (docs / f"p{i}.html").write_text("<html/>", encoding="utf-8")
    result = file_utils.find_html_files(root_dir=tmp_path, docs_only=True, limit=2)
    assert len(result) == 2


def test_find_html_files_docs_only_false(tmp_path: Path) -> None:
    """find_html_files with docs_only=False should search root directory."""
    (tmp_path / "root.html").write_text("<html/>", encoding="utf-8")
    result = file_utils.find_html_files(root_dir=tmp_path, docs_only=False)
    assert any(f.name == "root.html" for f in result)


def test_find_markdown_files_uses_default_search_dirs(tmp_path: Path) -> None:
    """find_markdown_files with search_dirs=None should use default dirs."""
    # Just verify it doesn't raise and returns a list
    result = file_utils.find_markdown_files(tmp_path, search_dirs=None)
    assert isinstance(result, list)
