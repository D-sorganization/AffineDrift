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


def test_mobile_publication_shell_contains_wide_content_without_page_scroll() -> None:
    """Tables and equations may scroll locally but must not widen the phone viewport."""
    stylesheet = (REPO_ROOT / "styles.css").read_text(encoding="utf-8")

    contract = stylesheet.split("/* Mobile publication overflow containment. */", maxsplit=1)[1]
    table_rule = contract.split("#quarto-document-content .table-wrapper", maxsplit=1)[1].split(
        "}", maxsplit=1
    )[0]
    shell_rule = contract.split("#quarto-content,", maxsplit=1)[1].split("}", maxsplit=1)[0]

    assert "@media (max-width: 575.98px)" in contract
    assert "overflow-x: clip" in contract
    assert "min-width: 0" in shell_rule
    assert "max-width: 100%" in shell_rule
    assert "width: 100%" in table_rule
    assert "contain: inline-size" in table_rule


def test_notation_tables_scroll_locally_and_keep_well_formed_norm_rows() -> None:
    """The normative notation reference must remain complete on narrow screens."""
    page = (REPO_ROOT / "pages" / "notation.qmd").read_text(encoding="utf-8")
    notation = (REPO_ROOT / "NOTATION.md").read_text(encoding="utf-8")
    stylesheet = (REPO_ROOT / "styles.css").read_text(encoding="utf-8")

    assert "::: {.notation-reference}" in page
    table_rule = stylesheet.split(".notation-reference table", maxsplit=1)[1].split(
        "}", maxsplit=1
    )[0]
    assert "display: block" in table_rule
    assert "overflow-x: auto" in table_rule
    assert "max-width: 100%" in table_rule

    assert "| **$\\lVert q \\rVert = 1$** | Unit quaternion constraint" in notation
    assert "| **$\\lVert v \\rVert$** | Magnitude/norm" in notation
    assert "| --- | ------- | -------------------------- |" not in notation


def test_roadmap_state_contract_table_scrolls_locally() -> None:
    """The high-value state key must not be clipped by the mobile page shell."""
    roadmap = (REPO_ROOT / "pages" / "development-roadmap.qmd").read_text(encoding="utf-8")

    state_section = roadmap.split("## State Contract", maxsplit=1)[1].split(
        "## Public Content Workstreams", maxsplit=1
    )[0]
    assert "::: {.table-wrapper}" in state_section
