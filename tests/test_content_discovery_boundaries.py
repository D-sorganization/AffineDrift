"""Regression coverage for content scan selection and file boundaries."""

from pathlib import Path

import pytest

from src.tools.utils.content_utils import collect_qmd_files


def test_empty_content_selection_does_not_scan_defaults(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An explicit empty selection must not silently scan the current directory."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "root.qmd").write_text("Root", encoding="utf-8")
    assert collect_qmd_files([]) == []
    assert collect_qmd_files(None) == [Path("root.qmd")]


@pytest.mark.parametrize("directory", [".", "articles", "critiques"])
def test_content_scan_returns_only_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, directory: str
) -> None:
    """Matching directory names cannot be passed to consumers as text files."""
    monkeypatch.chdir(tmp_path)
    root = tmp_path / directory
    root.mkdir(exist_ok=True)
    (root / "folder.qmd").mkdir()
    (root / "folder.md").mkdir()
    (root / "real.qmd").write_text("Content", encoding="utf-8")
    if directory == "critiques":
        (root / "review.md").write_text("Review", encoding="utf-8")
    result = collect_qmd_files([directory])
    expected = [Path(directory) / "real.qmd"]
    if directory == "critiques":
        expected.append(Path(directory) / "review.md")
    assert result == sorted(expected)
    assert all(path.is_file() for path in result)
