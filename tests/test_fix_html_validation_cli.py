"""CLI contract tests for fix_html_validation tool."""

from __future__ import annotations

from pathlib import Path

from src.tools import fix_html_validation


def test_main_returns_2_for_missing_docs_dir(monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        ["fix_html_validation.py", "--docs-dir", "missing-directory"],
    )
    assert fix_html_validation.main() == 2


def test_main_uses_docs_dir_for_html_search(tmp_path: Path, monkeypatch) -> None:
    html_path = tmp_path / "index.html"
    html_path.write_text("<html></html>", encoding="utf-8")
    recorded: dict[str, object] = {}

    def fake_find_html_files(*, root_dir, docs_only, limit=None):  # type: ignore[no-untyped-def]
        recorded["root_dir"] = root_dir
        recorded["docs_only"] = docs_only
        recorded["limit"] = limit
        return [html_path]

    monkeypatch.setattr(
        "sys.argv",
        ["fix_html_validation.py", "--docs-dir", str(tmp_path), "--dry-run"],
    )
    monkeypatch.setattr(fix_html_validation, "find_html_files", fake_find_html_files)
    assert fix_html_validation.main() == 0
    assert Path(recorded["root_dir"]) == tmp_path
    assert recorded["docs_only"] is False
