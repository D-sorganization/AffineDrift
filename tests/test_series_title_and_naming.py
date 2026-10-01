"""Regression test enforcing Theory Series single naming and title patterns (#4499).

Ensures that:
1. One series name ('Theory Series') is used across navbar, sidebar, titles,
   Article Index, and home page.
2. Front matter 'series:' and 'series-part:' metadata enforce the standardized
   title pattern: f"{series}, Part {series_part}: {subtitle}".
3. affine-nature-golf-swing.qmd is retitled as the Consolidated Edition.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
QUARTO_YML = REPO_ROOT / "_quarto.yml"


def _extract_frontmatter(file_path: Path) -> dict[str, object]:
    """Extract and parse YAML frontmatter from a Quarto markdown document."""
    content = file_path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, flags=re.DOTALL)
    assert match is not None, f"No YAML frontmatter found in {file_path}"
    parsed = yaml.safe_load(match.group(1))
    assert isinstance(parsed, dict), f"Frontmatter in {file_path} did not parse as a dict"
    return parsed


def test_theory_series_frontmatter_and_title_pattern() -> None:
    """Enforce series metadata and title pattern across Theory Series parts."""
    parts = [
        (1, "Control-Affine Foundations"),
        (2, "Counterfactual Diagnostics"),
        (3, "Drift Invariance and Force Taxonomy"),
        (4, "Worked Pendulum Dynamics"),
        (5, "Numerical Consistency"),
    ]

    for part_num, expected_subtitle in parts:
        qmd_file = REPO_ROOT / "articles" / f"theory-part{part_num}.qmd"
        assert qmd_file.exists(), f"Missing {qmd_file}"
        fm = _extract_frontmatter(qmd_file)

        assert (
            fm.get("series") == "Theory Series"
        ), f"{qmd_file.name} must declare 'series: \"Theory Series\"'"
        assert (
            fm.get("series-part") == part_num
        ), f"{qmd_file.name} must declare 'series-part: {part_num}'"

        expected_title = f"Theory Series, Part {part_num}: {expected_subtitle}"
        assert (
            fm.get("title") == expected_title
        ), f"{qmd_file.name} title '{fm.get('title')}' does not match expected '{expected_title}'"


def test_consolidated_edition_frontmatter_and_title() -> None:
    """affine-nature-golf-swing.qmd must be retitled as the Consolidated Edition."""
    qmd_file = REPO_ROOT / "articles" / "affine-nature-golf-swing.qmd"
    assert qmd_file.exists(), f"Missing {qmd_file}"
    fm = _extract_frontmatter(qmd_file)

    assert (
        fm.get("series") == "Theory Series"
    ), "affine-nature-golf-swing.qmd must declare 'series: \"Theory Series\"'"
    assert (
        fm.get("series-edition") == "Consolidated Edition"
    ), "affine-nature-golf-swing.qmd must declare 'series-edition: \"Consolidated Edition\"'"
    assert (
        fm.get("title") == "Theory Series: Consolidated Edition"
    ), f"affine-nature-golf-swing.qmd title must be 'Theory Series: Consolidated Edition', got '{fm.get('title')}'"


def test_single_series_name_in_navbar_and_sidebar() -> None:
    """Navbar and sidebar in _quarto.yml must consistently use 'Theory Series'."""
    data = yaml.safe_load(QUARTO_YML.read_text(encoding="utf-8"))
    website = data["website"]

    # Navbar check
    read_menu = None
    for item in website.get("navbar", {}).get("left", []):
        if item.get("text") == "Read":
            read_menu = item.get("menu", [])
            break
    assert read_menu is not None, "Could not find 'Read' menu in navbar"

    navbar_texts = [item.get("text") for item in read_menu if isinstance(item, dict)]
    assert (
        "Theory Series" in navbar_texts
    ), f"Navbar 'Read' menu must contain 'Theory Series', found: {navbar_texts}"
    assert (
        "Drifter Manifesto & Theory" not in navbar_texts
    ), "Navbar must not use legacy 'Drifter Manifesto & Theory'"

    # Sidebar check
    sidebars = website.get("sidebar", [])
    theory_sidebar = next((s for s in sidebars if s.get("id") == "theory-nav"), None)
    assert theory_sidebar is not None, "Missing theory-nav sidebar in _quarto.yml"
    assert theory_sidebar.get("title") == "Theory Series"

    # Sidebar section title and consolidated edition text
    contents = theory_sidebar.get("contents", [])
    assert len(contents) > 0
    section = contents[0]
    assert section.get("section") == "Theory Series"

    section_texts = [
        item.get("text") for item in section.get("contents", []) if isinstance(item, dict)
    ]
    assert (
        "Consolidated Edition" in section_texts
    ), f"Sidebar must label affine-nature-golf-swing.html as 'Consolidated Edition', found: {section_texts}"
    assert "Foundations Monograph" not in section_texts


def test_single_series_name_in_article_index_and_home() -> None:
    """Article Index and Home page must use 'Theory Series' consistently."""
    articles_index = (REPO_ROOT / "resources" / "articles.qmd").read_text(encoding="utf-8")
    assert (
        "## Theory Series" in articles_index
    ), "resources/articles.qmd must have a '## Theory Series' section"
    assert "Theory Series: Consolidated Edition" in articles_index

    home_page = (REPO_ROOT / "index.qmd").read_text(encoding="utf-8")
    assert "Theory Series, Part 1" in home_page, "index.qmd must reference 'Theory Series, Part 1'"
