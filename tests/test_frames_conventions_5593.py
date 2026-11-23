"""Content contracts for frame pinning remainder (Refs #5593)."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.content_lint

ROOT = Path(__file__).resolve().parents[1]
NOTATION = ROOT / "NOTATION.md"
POG_INDEX = ROOT / "articles" / "The_Physics_of_Golf" / "quarto" / "index.qmd"
GOM_INDEX = ROOT / "articles" / "The_Geometry_of_Motion" / "quarto" / "index.qmd"
PDE_INDEX = ROOT / "articles" / "proximal_distal_energy_transfer" / "index.qmd"
LM_INTRO = (
    ROOT / "articles" / "Launch_Monitor_Technology_Review" / "sections" / "01-introduction.tex"
)
LM_VENDOR = ROOT / "articles" / "launch-monitor-vendor-reference.qmd"
LM_TECH = ROOT / "articles" / "technology-launch-monitors.qmd"
CLUB_FITTING = ROOT / "articles" / "technology-club-fitting.qmd"
POG_CH28 = ROOT / "articles" / "The_Physics_of_Golf" / "quarto" / "ch28_impact_collision.qmd"


def test_notation_defines_club_and_ball_frames() -> None:
    text = NOTATION.read_text(encoding="utf-8")
    assert "**Club frame" in text
    assert "**Ball frame" in text


@pytest.mark.parametrize(
    "path",
    [POG_INDEX, GOM_INDEX, PDE_INDEX],
    ids=["pog", "gom", "pde"],
)
def test_book_index_declares_frame_conventions(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert "Frames and Site Notation" in text
    assert "coordinate-frame-conventions" in text or "NOTATION.md" in text


def test_launch_monitor_monograph_intro_points_at_site_frames() -> None:
    text = LM_INTRO.read_text(encoding="utf-8")
    assert "coordinate-frame-conventions" in text or "Site default" in text
    assert "ch:params" in text or "cref{ch:params}" in text


def test_launch_monitor_articles_map_to_site_default_frame() -> None:
    vendor = LM_VENDOR.read_text(encoding="utf-8")
    assert "coordinate-frame-conventions" in vendor or "site default" in vendor.lower()

    tech = LM_TECH.read_text(encoding="utf-8")
    assert "coordinate-frame-conventions" in tech

    fitting = CLUB_FITTING.read_text(encoding="utf-8")
    assert "coordinate-frame-conventions" in fitting or "site default" in fitting.lower()


def test_pog_ch28_declares_y_up_departure_from_site_default() -> None:
    text = POG_CH28.read_text(encoding="utf-8")
    assert "forward/up/right" in text
    assert "coordinate-frame-conventions" in text


def test_vendor_coordinates_map_to_left_positive_site_axis() -> None:
    """Require an explicit sign reversal when changing the lateral axis."""
    text = LM_VENDOR.read_text(encoding="utf-8")
    assert r"=(y_{\mathrm{page}},-x_{\mathrm{page}},z_{\mathrm{page}})" in text


def test_equipment_example_declares_head_body_frame() -> None:
    """Keep the equipment body frame distinct from the site target frame."""
    text = CLUB_FITTING.read_text(encoding="utf-8")
    introduction = text.split("A future equipment contract", 1)[1].split("```json", 1)[0]
    assert "head body frame" in introduction
    assert "face-normal" in introduction
    assert "body-to-site rotation" in introduction
    assert r"x_{\mathrm{site}}" not in introduction


@pytest.mark.parametrize("path", [POG_INDEX, GOM_INDEX, POG_CH28])
def test_nested_book_frame_links_resolve_to_site_pages(path: Path) -> None:
    """Resolve nested book links from their source directory."""
    import re

    text = path.read_text(encoding="utf-8")
    links = re.findall(r"\]\(([^)]+pages/[^)]+)\)", text)
    assert links
    for link in links:
        target = link.split("#", 1)[0].replace(".html", ".qmd")
        assert (path.parent / target).is_file(), link


@pytest.mark.parametrize(
    "path",
    [
        ROOT / "articles" / "forward_dynamics_matching" / "index.qmd",
        ROOT / "books" / "tangent-space-methods.qmd",
    ],
    ids=["forward-dynamics", "tangent-space"],
)
def test_remaining_book_landings_link_frame_conventions(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert "coordinate-frame-conventions" in text
    assert "angular-first" in text
