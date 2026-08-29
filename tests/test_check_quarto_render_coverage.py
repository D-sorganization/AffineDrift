"""Tests for the Quarto render coverage checker."""

from __future__ import annotations

from pathlib import Path

import pytest
from defusedxml.common import DefusedXmlException

from scripts import check_quarto_render_coverage as render_coverage
from scripts.check_quarto_render_coverage import (
    find_missing_sitemap_sources,
    find_unindexed_sources,
    load_sitemap_paths,
    sitemap_loc_to_source_path,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_required_render_rules_publish_only_the_claim_audit_report_from_reports():
    """The public audit link must not expose the repository's broader report tree."""
    assert "reports/scientific-claim-audit.md" in render_coverage.REQUIRED_RENDER_RULES
    assert "reports/**/*.md" not in render_coverage.REQUIRED_RENDER_RULES


def test_repository_render_config_covers_every_required_target():
    """The checked-in Quarto project must satisfy the executable render contract."""
    render_rules = render_coverage.load_render_rules(REPO_ROOT / "_quarto.yml")

    assert render_coverage.REQUIRED_RENDER_RULES.issubset(render_rules)


def test_sitemap_loc_to_source_path_maps_root_and_html_pages(tmp_path):
    repo_root = tmp_path

    assert sitemap_loc_to_source_path("https://affinedrift.com/", repo_root) == (
        repo_root / "index.qmd"
    )
    assert sitemap_loc_to_source_path(
        "https://affinedrift.com/articles/theory-part1.html",
        repo_root,
    ) == (repo_root / "articles" / "theory-part1.qmd")


def test_sitemap_loc_to_source_path_maps_md_when_present(tmp_path):
    repo_root = tmp_path
    critiques_dir = repo_root / "critiques"
    critiques_dir.mkdir()
    md_file = critiques_dir / "review.md"
    md_file.write_text("# Review\n", encoding="utf-8")

    assert (
        sitemap_loc_to_source_path(
            "https://affinedrift.com/critiques/review.html",
            repo_root,
        )
        == md_file
    )


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


def test_load_sitemap_paths_rejects_entity_expansion(tmp_path):
    sitemap = tmp_path / "sitemap.xml"
    sitemap.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE urlset [
  <!ENTITY unsafe "https://affinedrift.com/">
]>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>&unsafe;</loc></url>
</urlset>
""",
        encoding="utf-8",
    )

    with pytest.raises(DefusedXmlException):
        load_sitemap_paths(sitemap)


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


def test_find_unindexed_sources_reports_missing_from_sitemap(tmp_path, monkeypatch):
    repo_root = tmp_path
    (repo_root / "index.qmd").write_text("---\ntitle: Home\n---\n", encoding="utf-8")
    (repo_root / "articles").mkdir()
    p1 = repo_root / "articles" / "page1.qmd"
    p1.write_text("---\ntitle: Page 1\n---\n", encoding="utf-8")

    import src.tools.utils.content_utils as cu

    monkeypatch.setattr(cu, "DEFAULT_CONTENT_DIRS", [str(repo_root / "articles")])
    monkeypatch.setattr(
        cu, "collect_qmd_files", lambda *args, **kwargs: [Path("articles/page1.qmd")]
    )

    unindexed = find_unindexed_sources(
        ["https://affinedrift.com/"],
        repo_root,
    )
    assert unindexed == [Path("articles/page1.qmd")]
