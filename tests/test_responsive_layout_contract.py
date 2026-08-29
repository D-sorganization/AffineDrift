"""Responsive source contracts for public-facing full-layout pages."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_models_mobile_layout_prioritizes_primary_content() -> None:
    """The compact Models view must not spend its first fold on a duplicate TOC."""
    source = (REPO_ROOT / "models" / "models.qmd").read_text(encoding="utf-8")
    stylesheet = (REPO_ROOT / "styles.css").read_text(encoding="utf-8")

    modifier = "standard-page-layout--content-first-compact"
    assert modifier in source
    assert f".{modifier} > .left-sidebar" in stylesheet
    assert (
        "display: none"
        in stylesheet.split(f".{modifier} > .left-sidebar", maxsplit=1)[1].split("}", maxsplit=1)[0]
    )


def test_full_layout_grid_placement_overrides_quarto_page_columns() -> None:
    """Quarto annotates authored grid children; the site grid remains authoritative."""
    stylesheet = (REPO_ROOT / "styles.css").read_text(encoding="utf-8")

    for child in ("left-sidebar", "main-content-area", "right-sidebar"):
        assert f"#quarto-content .standard-page-layout > .{child}" in stylesheet
    assert ".page-columns.page-full:not(.standard-page-layout)" in stylesheet


def test_all_authored_full_layouts_are_content_first_on_phones() -> None:
    """Section navigation must not displace a detail page title below the phone fold."""
    stylesheet = (REPO_ROOT / "styles.css").read_text(encoding="utf-8")

    phone_contract = stylesheet.split(
        "/* Phone full-layout contract: primary content precedes section navigation. */",
        maxsplit=1,
    )[1]
    sidebar_rule = phone_contract.split(
        "#quarto-content .standard-page-layout > .left-sidebar", maxsplit=1
    )[1].split("}", maxsplit=1)[0]
    main_rule = phone_contract.split(
        "#quarto-content .standard-page-layout > .main-content-area", maxsplit=1
    )[1].split("}", maxsplit=1)[0]

    assert "@media (width < 768px)" in phone_contract
    assert "display: none !important" in sidebar_rule
    assert "grid-column: 1 !important" in main_rule
