"""Unit tests for scripts/post_render_sri_audit.py (issue #5252)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.post_render_sri_audit import (
    ExternalAssetRecord,
    audit_html_directory,
    audit_html_file,
    collect_repo_third_party_inventory,
    main,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_post_render_check_fails_fixture_page_with_external_script_without_integrity(
    tmp_path: Path,
) -> None:
    """Fixture page containing an external script without integrity must fail the check."""
    site_dir = tmp_path / "_site"
    site_dir.mkdir(parents=True)
    fixture_page = site_dir / "widget.html"
    fixture_page.write_text(
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head>\n"
        '  <script src="https://cdn.jsdelivr.net/npm/three@0.147.0/build/three.min.js"></script>\n'
        '  <script src="/js/main.js"></script>\n'
        "</head>\n"
        "<body></body>\n"
        "</html>\n",
        encoding="utf-8",
    )

    records = audit_html_file(fixture_page, base_dir=site_dir)
    assert len(records) == 1
    rec: ExternalAssetRecord = records[0]
    assert rec.host == "cdn.jsdelivr.net"
    assert rec.asset_type == "script"
    assert rec.has_sri is False

    rc = main(["--site-dir", str(site_dir)])
    assert rc == 1


def test_post_render_check_passes_fixture_page_with_valid_sri_and_local_scripts(
    tmp_path: Path,
) -> None:
    """External script with valid sha384 integrity and crossorigin passes the check."""
    site_dir = tmp_path / "_site"
    site_dir.mkdir(parents=True)
    fixture_page = site_dir / "math.html"
    fixture_page.write_text(
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head>\n"
        '  <script src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js"\n'
        '          integrity="sha384-Wuix6BuhrWbjDBs24bXrjf4ZQ5aFeFWBuKkFekO2t8xFU0iNaLQfp2K6/1Nxveei"\n'
        '          crossorigin="anonymous"></script>\n'
        '  <script src="/js/local.js"></script>\n'
        "</head>\n"
        "<body></body>\n"
        "</html>\n",
        encoding="utf-8",
    )

    records = audit_html_directory(site_dir)
    assert len(records) == 1
    assert records[0].has_sri is True
    assert records[0].sri_value.startswith("sha384-")

    rc = main(["--site-dir", str(site_dir)])
    assert rc == 0


def test_audit_html_directory_rejects_missing_dir(tmp_path: Path) -> None:
    """Boundary check raises ValueError when site_dir does not exist."""
    with pytest.raises(ValueError, match="Site directory does not exist"):
        audit_html_directory(tmp_path / "missing")


def test_repo_inventory_covers_mathjax_three_and_plotly_and_matches_audit_doc() -> None:
    """Repo inventory captures MathJax, Three.js, and Plotly with accurate SRI status."""
    inventory = collect_repo_third_party_inventory(REPO_ROOT)
    by_url = {item.url: item for item in inventory}

    assert "https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js" in by_url
    assert by_url["https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js"].has_sri is True

    assert "https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js" in by_url
    assert by_url["https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js"].has_sri is True

    assert "https://cdn.jsdelivr.net/npm/three@0.147.0/build/three.min.js" in by_url
    assert by_url["https://cdn.jsdelivr.net/npm/three@0.147.0/build/three.min.js"].has_sri is False

    assert "https://cdn.plot.ly/plotly-2.26.0.min.js" in by_url
    assert by_url["https://cdn.plot.ly/plotly-2.26.0.min.js"].has_sri is False

    audit_doc = (REPO_ROOT / "docs" / "audits" / "sri-csp-adr0002-5252.md").read_text(
        encoding="utf-8"
    )
    for url in by_url:
        assert url in audit_doc
