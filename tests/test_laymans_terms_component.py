"""Tests for the shared "In Layman's Terms" component (#4494).

Enforces:
1. No ``.qmd`` page carries an inline copy of the lay-block HTML; pages use
   the ``::: {.laymans-terms}`` fenced div rendered by
   ``scripts/filters/laymans-terms.lua``.
2. The filter is registered for HTML output, after the summary-takeaways
   filter so that filter's legacy-lay-block suppression still applies.
3. Rendered through Quarto, the block is open by default and sits above the
   page's Abstract heading (skipped when Quarto is not installed).
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
FILTER = ROOT / "scripts/filters/laymans-terms.lua"
SUMMARY_FILTER = "scripts/filters/summary-takeaways.lua"

_INLINE_BLOCK_RE = re.compile(r"<section[^>]*class=[\"'][^\"']*laymans-terms|laymans-terms-header")
_EXCLUDED_DIRS = {"node_modules", "_site", ".quarto", ".git"}


def _qmd_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*.qmd")
        if not _EXCLUDED_DIRS.intersection(path.relative_to(ROOT).parts)
    ]


def test_no_qmd_contains_inline_laymans_terms_html() -> None:
    offenders = [
        path.relative_to(ROOT).as_posix()
        for path in _qmd_files()
        if _INLINE_BLOCK_RE.search(path.read_text(encoding="utf-8"))
    ]
    assert offenders == [], (
        "Inline 'In Layman's Terms' HTML found; use the ::: {.laymans-terms} "
        f"fenced div instead: {offenders}"
    )


def test_pages_use_the_shared_component() -> None:
    users = [p for p in _qmd_files() if "::: {.laymans-terms}" in p.read_text(encoding="utf-8")]
    assert users, "expected at least one page to use the shared lay-block component"


def test_filter_registered_after_summary_takeaways() -> None:
    config = yaml.safe_load((ROOT / "_quarto.yml").read_text(encoding="utf-8"))
    filters = config["format"]["html"]["filters"]
    assert "scripts/filters/laymans-terms.lua" in filters
    assert filters.index("scripts/filters/laymans-terms.lua") > filters.index(SUMMARY_FILTER)


def _render_html(body: str) -> str:
    quarto = shutil.which("quarto")
    if quarto is None:
        pytest.skip("Quarto is required for the laymans-terms integration check")
    with tempfile.TemporaryDirectory() as tmp_dir:
        qmd = Path(tmp_dir) / "test.qmd"
        qmd.write_text(
            "---\n"
            "title: Test Article\n"
            f"filters:\n  - {FILTER.resolve().as_posix()}\n"
            "format: html\n"
            "---\n\n"
            f"{body}\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [quarto, "render", str(qmd), "--to", "html"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert result.returncode == 0, f"quarto render failed:\n{result.stderr}"
        return qmd.with_suffix(".html").read_text(encoding="utf-8")


_LAY_BODY = (
    "::: {.laymans-terms}\n"
    "```{=html}\n"
    '<p class="laymans-terms-intro">Plain words stay exactly as written.</p>\n'
    "```\n"
    ":::\n"
)


@pytest.mark.integration
def test_rendered_block_is_open_by_default() -> None:
    html = _render_html(_LAY_BODY)
    assert 'aria-expanded="true"' in html
    assert 'aria-expanded="false"' not in html
    assert "Plain words stay exactly as written." in html


@pytest.mark.integration
def test_rendered_block_is_moved_above_the_abstract() -> None:
    html = _render_html("## Abstract\n\nAbstract text.\n\n" + _LAY_BODY)
    assert html.index('class="laymans-terms"') < html.index("Abstract text.")
