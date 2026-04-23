"""Tests for the Quarto render coverage checker."""

from __future__ import annotations

from pathlib import Path

from scripts.check_quarto_render_coverage import (
    find_missing_sitemap_sources,
    load_sitemap_paths,
    sitemap_loc_to_source_path,
)


def test_sitemap_loc_to_source_path_maps_root_and_html_pages(tmp_path):
    repo_root = tmp_path

    assert sitemap_loc_to_source_path("https://affinedrift.com/", repo_root) == (
        repo_root / "index.qmd"
    )
    assert sitemap_loc_to_source_path(
        "https://affinedrift.com/articles/theory-part1.html",
        repo_root,
    ) == (repo_root / "articles" / "theory-part1.qmd")


def test_load_sitemap_paths_reads_all_locs(tmp_path):
    sitemap = tmp_path / "sitemap.xml"
    sitemap.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://affinedrift.com/</loc></url>
  <url><loc>https://affinedrift.com/articles/theory-part1.html</loc></url>
</urlset>
""",
        encoding="utf-8",
    )

    assert load_sitemap_paths(sitemap) == [
        "https://affinedrift.com/",
        "https://affinedrift.com/articles/theory-part1.html",
    ]


def test_find_missing_sitemap_sources_reports_unbacked_urls(tmp_path):
    repo_root = tmp_path
    (repo_root / "articles").mkdir()
    (repo_root / "index.qmd").write_text("---\ntitle: Home\n---\n", encoding="utf-8")

    missing = find_missing_sitemap_sources(
        [
            "https://affinedrift.com/",
            "https://affinedrift.com/articles/theory-part1.html",
        ],
        repo_root,
    )

    assert missing == [
        (
            "https://affinedrift.com/articles/theory-part1.html",
            Path(repo_root / "articles" / "theory-part1.qmd"),
        )
    ]
