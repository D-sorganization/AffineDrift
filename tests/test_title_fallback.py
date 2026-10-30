"""Tests for the title-fallback Lua filter (#5168).

Enforces:
1. A page with no `title:` front matter gets its `.title` heading populated
   from the document's first level-1 heading, instead of rendering empty
   (axe `empty-heading`).
2. A page that already sets `title:` is left untouched.
3. The promoted heading is removed from the body, so the page renders
   exactly one visible H1 (not two).
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FILTER = ROOT / "scripts/filters/title-fallback.lua"


def _render_html(frontmatter_extra: str, body: str) -> str:
    quarto = shutil.which("quarto")
    if quarto is None:
        pytest.skip("Quarto is required for the title-fallback integration check")
    with tempfile.TemporaryDirectory() as tmp_dir:
        qmd = Path(tmp_dir) / "test.qmd"
        content = (
            "---\n"
            "description: Test article description\n"
            f"{frontmatter_extra}\n"
            f"filters:\n  - {FILTER.resolve().as_posix()}\n"
            "format:\n  html:\n    title-block-style: default\n"
            "---\n\n"
            f"{body}\n"
        )
        qmd.write_text(content, encoding="utf-8")
        result = subprocess.run(
            [quarto, "render", str(qmd), "--to", "html"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        assert result.returncode == 0, result.stderr
        return (Path(tmp_dir) / "test.html").read_text(encoding="utf-8")


def test_missing_title_falls_back_to_first_heading() -> None:
    html = _render_html("", "# A Derived Title From The Body\n\nBody paragraph.\n")
    assert '<h1 class="title">' in html
    assert "A Derived Title From The Body" in html
    assert '<h1 class="title"></h1>' not in html


def test_promoted_heading_is_not_duplicated_in_body() -> None:
    html = _render_html("", "# A Derived Title From The Body\n\nBody paragraph.\n")
    assert html.count("<h1") == 1


def test_explicit_title_is_left_untouched() -> None:
    html = _render_html(
        'title: "Explicit Title Wins"',
        "# A Different Heading\n\nBody paragraph.\n",
    )
    assert "Explicit Title Wins" in html
    assert '<h1 class="title">Explicit Title Wins</h1>' in html
