"""Contracts for the content inventory and ownership map generator (#4602)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import generate_content_inventory as inventory
from tests.test_site_link_gate import write_page


def _record(records: list[dict[str, object]], route: str) -> dict[str, object]:
    matches = [record for record in records if record["route"] == route]
    assert matches, f"no record for route {route}"
    return matches[0]


@pytest.mark.unit
def test_short_page_without_planned_status_is_flagged(tmp_path: Path) -> None:
    write_page(tmp_path / "pages" / "short.qmd", "Just a few words here.\n", title="Short")
    records = inventory.build_inventory(tmp_path)
    record = _record(records, "/pages/short.html")
    assert record["status"] == "published"
    assert record["word_count"] < inventory.SHORT_PAGE_WORD_THRESHOLD
    assert record["flagged_short"] is True


@pytest.mark.unit
def test_short_page_with_planned_badge_is_not_flagged(tmp_path: Path) -> None:
    write_page(
        tmp_path / "pages" / "planned.qmd",
        '```{=html}\n<aside class="status-banner status-banner--warning">'
        '<p class="status-banner__title">Status: Planned</p></aside>\n```\n\nShort body.\n',
        title="Planned",
    )
    records = inventory.build_inventory(tmp_path)
    record = _record(records, "/pages/planned.html")
    assert record["status"] == "planned"
    assert record["word_count"] < inventory.SHORT_PAGE_WORD_THRESHOLD
    assert record["flagged_short"] is False


@pytest.mark.unit
def test_inbound_links_and_broken_outbound_links_are_tracked(tmp_path: Path) -> None:
    write_page(
        tmp_path / "articles" / "alpha.qmd",
        "See [beta](../pages/beta.html) and [gone](../pages/missing.html).\n",
        title="Alpha",
    )
    write_page(tmp_path / "pages" / "beta.qmd", "No outbound links here.\n", title="Beta")
    records = inventory.build_inventory(tmp_path)
    alpha = _record(records, "/articles/alpha.html")
    beta = _record(records, "/pages/beta.html")
    assert alpha["outbound_broken_links"] == ["../pages/missing.html"]
    assert beta["inbound_links"] == 1
    assert alpha["inbound_links"] == 0


@pytest.mark.unit
def test_canonical_defaults_to_route_and_honors_front_matter(tmp_path: Path) -> None:
    write_page(tmp_path / "pages" / "default.qmd", "Body text.\n", title="Default")
    write_page(
        tmp_path / "pages" / "aliased.qmd",
        "Body text.\n",
        title="Aliased",
        canonical="https://example.com/canonical-page",
    )
    records = inventory.build_inventory(tmp_path)
    default = _record(records, "/pages/default.html")
    aliased = _record(records, "/pages/aliased.html")
    assert default["canonical"] == "/pages/default.html"
    assert aliased["canonical"] == "https://example.com/canonical-page"


@pytest.mark.unit
def test_last_reviewed_from_date_front_matter(tmp_path: Path) -> None:
    write_page(tmp_path / "pages" / "dated.qmd", "Body text.\n", title="Dated", date="2026-01-15")
    write_page(tmp_path / "pages" / "undated.qmd", "Body text.\n", title="Undated")
    records = inventory.build_inventory(tmp_path)
    dated = _record(records, "/pages/dated.html")
    undated = _record(records, "/pages/undated.html")
    assert dated["last_reviewed"] == "2026-01-15"
    assert undated["last_reviewed"] is None


@pytest.mark.unit
def test_build_inventory_is_sorted_and_deterministic(tmp_path: Path) -> None:
    write_page(tmp_path / "pages" / "zeta.qmd", "Body.\n", title="Zeta")
    write_page(tmp_path / "pages" / "alpha.qmd", "Body.\n", title="Alpha")
    first = inventory.build_inventory(tmp_path)
    second = inventory.build_inventory(tmp_path)
    routes = [record["route"] for record in first]
    assert routes == sorted(routes, key=str.casefold)
    assert first == second


@pytest.mark.unit
def test_render_json_and_csv_are_deterministic_and_complete(tmp_path: Path) -> None:
    write_page(tmp_path / "pages" / "alpha.qmd", "Body.\n", title="Alpha")
    write_page(tmp_path / "pages" / "beta.qmd", "Body.\n", title="Beta")
    records = inventory.build_inventory(tmp_path)
    json_text = inventory.render_json(records)
    assert json_text == inventory.render_json(records)
    csv_text = inventory.render_csv(records)
    assert csv_text == inventory.render_csv(records)
    assert csv_text.strip().count("\n") == len(records)


@pytest.mark.unit
def test_render_dashboard_lists_flagged_pages(tmp_path: Path) -> None:
    write_page(tmp_path / "pages" / "short.qmd", "Just a few words.\n", title="Short")
    records = inventory.build_inventory(tmp_path)
    page = inventory.render_dashboard(records)
    assert page.startswith('---\ntitle: "Content Inventory and Ownership Map"')
    assert "/pages/short.html" in page
    assert "## Related Articles" in page


@pytest.mark.unit
def test_check_mode_detects_stale_output(tmp_path: Path) -> None:
    write_page(tmp_path / "pages" / "alpha.qmd", "Body.\n", title="Alpha")
    json_output = tmp_path / "out" / "inventory.json"
    csv_output = tmp_path / "out" / "inventory.csv"
    dashboard_output = tmp_path / "out" / "content-inventory.qmd"
    args = [
        "--root",
        str(tmp_path),
        "--json-output",
        str(json_output),
        "--csv-output",
        str(csv_output),
        "--dashboard-output",
        str(dashboard_output),
    ]
    assert inventory.main(args) == 0
    assert inventory.main([*args, "--check"]) == 0
    json_output.write_text(json_output.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    assert inventory.main([*args, "--check"]) == 1
