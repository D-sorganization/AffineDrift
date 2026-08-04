"""Behavioral tests for ``scripts/build-html.py`` (issue #3230).

The script file is hyphenated, so it is loaded via importlib. Tests cover the
pure ``extract_html_from_qmd`` extractor: the happy path (frontmatter + html
block), the no-frontmatter path, the no-html-block path, and title/description
defaulting from the filename stem.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "build-html.py"


@pytest.fixture(scope="module")
def build_html():
    spec = importlib.util.spec_from_file_location("build_html_under_test", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _qmd(tmp_path: Path, name: str, body: str) -> Path:
    f = tmp_path / name
    f.write_text(body, encoding="utf-8")
    return f


def test_extract_full_page(build_html, tmp_path) -> None:
    qmd = _qmd(
        tmp_path,
        "page.qmd",
        '---\ntitle: "My Title"\ndescription: "My Desc"\n---\n\n```{=html}\n<p>Hello</p>\n```\n',
    )
    title, description, html = build_html.extract_html_from_qmd(qmd)
    assert title == "My Title"
    assert description == "My Desc"
    assert html == "<p>Hello</p>"


def test_no_frontmatter_returns_all_none(build_html, tmp_path) -> None:
    qmd = _qmd(tmp_path, "nofm.qmd", "Just body text with no frontmatter.\n")
    title, description, html = build_html.extract_html_from_qmd(qmd)
    assert (title, description, html) == (None, None, None)


def test_frontmatter_but_no_html_block(build_html, tmp_path) -> None:
    qmd = _qmd(tmp_path, "noblock.qmd", '---\ntitle: "T"\n---\n\nSome markdown only.\n')
    title, _description, html = build_html.extract_html_from_qmd(qmd)
    assert title == "T"
    assert html is None


def test_title_defaults_to_stem_when_absent(build_html, tmp_path) -> None:
    qmd = _qmd(
        tmp_path,
        "fallback.qmd",
        "---\nauthor: nobody\n---\n\n```{=html}\n<div/>\n```\n",
    )
    title, _description, html = build_html.extract_html_from_qmd(qmd)
    assert title == "fallback"
    assert html == "<div/>"
