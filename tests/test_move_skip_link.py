"""Contracts for the skip-link post-render step (#4566)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import move_skip_link as step

LINK = '<a href="#quarto-document-content" class="skip-to-content">Skip to main content</a>'
INCLUDE = Path(__file__).resolve().parents[1] / "_includes" / "skip-link.html"


def _page(before_link: str = "") -> str:
    return (
        '<html><body class="nav-fixed">\n<header id="quarto-header"><nav>'
        '<a href="index.html">Home</a></nav></header>\n'
        f'<main id="quarto-document-content">\n{before_link}{LINK}\n<p>Body</p></main>'
        "</body></html>"
    )


@pytest.mark.unit
def test_link_moves_ahead_of_navbar() -> None:
    result = step.move_skip_link(_page())
    body_end = result.index(">", result.index("<body")) + 1
    assert result[body_end:].lstrip().startswith(LINK)
    assert result.count("skip-to-content") == 1
    assert result.index(LINK) < result.index('id="quarto-header"')


@pytest.mark.unit
def test_include_comment_travels_out_with_the_link() -> None:
    comment = "<!-- Static skip link (issue #4566): see scripts/move_skip_link.py -->\n"
    result = step.move_skip_link(_page(before_link=comment))
    assert "Static skip link" not in result
    assert result.count("skip-to-content") == 1


@pytest.mark.unit
def test_step_is_idempotent() -> None:
    once = step.move_skip_link(_page())
    assert step.move_skip_link(once) == once


@pytest.mark.unit
def test_pages_without_a_link_are_unchanged() -> None:
    html = "<html><body><p>No link</p></body></html>"
    assert step.move_skip_link(html) == html


@pytest.mark.unit
def test_duplicate_links_are_rejected() -> None:
    with pytest.raises(ValueError, match="expected one skip link"):
        step.move_skip_link(_page(before_link=LINK + "\n"))


@pytest.mark.unit
def test_include_markup_matches_the_step() -> None:
    assert step.SKIP_LINK.search(INCLUDE.read_text(encoding="utf-8"))


@pytest.mark.unit
def test_main_rewrites_listed_files_in_place(tmp_path: Path) -> None:
    page = tmp_path / "index.html"
    page.write_text(_page(), encoding="utf-8")
    other = tmp_path / "data.json"
    other.write_text("{}", encoding="utf-8")
    assert step.main([str(page), str(other), str(tmp_path / "missing.html")]) == 0
    assert page.read_text(encoding="utf-8").index(LINK) < page.read_text(encoding="utf-8").index(
        "quarto-header"
    )
    assert other.read_text(encoding="utf-8") == "{}"


@pytest.mark.unit
def test_quarto_output_env_is_used(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    page = tmp_path / "a.html"
    monkeypatch.setenv("QUARTO_PROJECT_OUTPUT_FILES", f"{page}\n{tmp_path / 'b.css'}\n")
    assert step.rendered_html_files([]) == [page]
