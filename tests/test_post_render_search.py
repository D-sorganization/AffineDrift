from __future__ import annotations

import gzip
import json
from pathlib import Path

import pytest

from scripts import post_render_search as search


def entry(href: str, text: str = "Article body") -> dict[str, str]:
    return dict(objectID=href, href=href, title="Article title", section="A section", text=text)


def test_index_keeps_article_book_sections_but_drops_utility_and_skip_text() -> None:
    rows = [
        entry("articles/chapter.html#intro", "Skip to main content\n" + "x" * 1_201 + "tailmarker"),
        entry("/books/volume/chapter.html#model"),
        entry("resources/articles.html"),
        entry("critiques/generated-assessment.html"),
        entry("../articles/outside.html"),
    ]
    result = search.bound_search_index(rows)
    assert [row["href"] for row in result] == [rows[0]["href"], rows[1]["href"]]
    assert all("Skip to main content" not in row["text"] for row in result)
    assert len(result[0]["text"]) <= search.MAX_SEARCH_TEXT_CHARS
    assert "tailmarker" in result[0]["text"]


def test_index_rejects_malformed_entries() -> None:
    with pytest.raises(ValueError, match="search entry"):
        search.bound_search_index([{"href": "articles/a.html"}])


def test_post_render_bounds_index_and_removes_eager_libraries(tmp_path: Path) -> None:
    site = tmp_path / "_site"
    site.mkdir()
    rows = [
        entry(f"articles/chapter-{i}.html#section", "double pendulum " * 300) for i in range(12)
    ]
    rows += [entry(f"critiques/generated-{i}.html", "assessment " * 300) for i in range(12)]
    (site / "search.json").write_text(json.dumps(rows), encoding="utf-8")
    libs = "".join(
        f'<script src="site_libs/quarto-search/{name}" defer></script>'
        for name in search.SEARCH_LIBRARIES
    )
    page = site / "index.html"
    page.write_text(
        f"<script src='/js/search-lazy-loader.js'></script>{libs}<script src='/js/main.js'></script>",
        encoding="utf-8",
    )

    assert search.process_site(site) is True
    bounded = (site / "search.json").read_bytes()
    assert len(json.loads(bounded)) == 12
    assert len(gzip.compress(bounded, mtime=0)) < search.MAX_GZIP_BYTES
    assert all(name not in page.read_text(encoding="utf-8") for name in search.SEARCH_LIBRARIES)
    assert search.process_site(site) is False


def test_post_render_fails_closed_on_partial_assets_or_over_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(ValueError, match="partial Quarto search library set"):
        search.process_html('<script src="site_libs/quarto-search/fuse.min.js"></script>')
    site = tmp_path / "_site"
    site.mkdir()
    (site / "search.json").write_text(json.dumps([entry("articles/a.html")]), encoding="utf-8")
    monkeypatch.setattr(search, "MAX_GZIP_BYTES", 1)
    with pytest.raises(ValueError, match="gzip bytes; budget is 1"):
        search.process_site(site)
