"""Tests for Volume Title Consistency and Volume Page Requirements (WEB-02.2 / #4498).

Acceptance criteria:
- Each volume number maps to exactly one title everywhere; a pytest checks
  _quarto.yml, books/*.qmd, and the Geometry of Motion index.
- No rendered volume page has fewer than 200 words unless it is marked Planned.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
QUARTO_YML = REPO_ROOT / "_quarto.yml"
BOOKS_DIR = REPO_ROOT / "books"
GEOM_QUARTO_DIR = REPO_ROOT / "articles" / "The_Geometry_of_Motion" / "quarto"
GEOM_INDEX = GEOM_QUARTO_DIR / "index.qmd"

CANONICAL_VOLUME_TITLES: dict[str, str] = {
    "Volume 0": "Volume 0: The Mathematical Primer",
    "Volume I": "Volume I: Tangent-Space Methods for Nonlinear Control",
    "Volume II": "Volume II: Control Is Motion",
    "Volume III": "Volume III: Biomechanics - Biology to Systems",
    "Volume IV": "Volume IV: Human Motor Control",
    "Volume V": "Volume V: Practical Application",
}

VOLUME_PAGE_PATHS: list[Path] = [
    GEOM_QUARTO_DIR / "volume0.qmd",
    GEOM_QUARTO_DIR / "volume1.qmd",
    GEOM_QUARTO_DIR / "volume2.qmd",
    BOOKS_DIR / "tangent-space-methods.qmd",
    BOOKS_DIR / "control-is-motion.qmd",
    BOOKS_DIR / "biomechanics-biology-to-systems.qmd",
    BOOKS_DIR / "human-motor-control.qmd",
]


def _extract_sidebar_volume_titles(quarto_yml_path: Path) -> dict[str, str]:
    """Extract volume labels from the geometry-motion-nav sidebar in _quarto.yml."""
    config = yaml.safe_load(quarto_yml_path.read_text(encoding="utf-8"))
    sidebars = config.get("website", {}).get("sidebar", [])
    geom_sidebar = next((s for s in sidebars if s.get("id") == "geometry-motion-nav"), None)
    assert geom_sidebar is not None, "Missing geometry-motion-nav sidebar in _quarto.yml"

    titles: dict[str, str] = {}
    for section in geom_sidebar.get("contents", []):
        for item in section.get("contents", []):
            text = item.get("text", "")
            for vol_key in CANONICAL_VOLUME_TITLES:
                if text.startswith(f"{vol_key}:") or text == vol_key:
                    titles[vol_key] = text
    return titles


def _extract_books_volume_titles(books_dir: Path) -> dict[str, str]:
    """Extract titles starting with 'Volume ' from books/*.qmd front matter."""
    titles: dict[str, str] = {}
    for qmd in sorted(books_dir.glob("*.qmd")):
        content = qmd.read_text(encoding="utf-8")
        match = re.search(
            r'^title:\s*["\']?(Volume [0-9IVXLCDM]+:[^"\']+)["\']?', content, re.MULTILINE
        )
        if match:
            full_title = match.group(1).strip()
            vol_key = full_title.split(":")[0].strip()
            titles[vol_key] = full_title
    return titles


def _extract_geom_index_volume_titles(geom_index_path: Path) -> dict[str, str]:
    """Extract volume titles from headings and list items in the Geometry of Motion index."""
    content = geom_index_path.read_text(encoding="utf-8")
    titles: dict[str, str] = {}

    # Check headings e.g. '### Volume 0: The Mathematical Primer'
    for heading in re.findall(r"^###\s+(Volume [0-9IVXLCDM]+:[^\n]+)", content, re.MULTILINE):
        heading = heading.strip()
        vol_key = heading.split(":")[0].strip()
        titles[vol_key] = heading

    # Check bullet items e.g. '- **Volume III: Biomechanics - Biology to Systems**'
    for item in re.findall(r"\*\*(Volume [0-9IVXLCDM]+:[^*]+)\*\*", content):
        item = item.strip()
        vol_key = item.split(":")[0].strip()
        titles[vol_key] = item

    return titles


def test_quarto_yml_volume_titles_match_canonical() -> None:
    """_quarto.yml sidebar items must strictly match canonical volume titles."""
    sidebar_titles = _extract_sidebar_volume_titles(QUARTO_YML)
    assert (
        len(sidebar_titles) >= 3
    ), f"Expected at least Volumes 0-II in sidebar, found {sidebar_titles}"
    for vol_key, actual_title in sidebar_titles.items():
        expected_title = CANONICAL_VOLUME_TITLES[vol_key]
        assert (
            actual_title == expected_title
        ), f"Sidebar mismatch for {vol_key}: got '{actual_title}', expected '{expected_title}'"


def test_books_qmd_volume_titles_match_canonical() -> None:
    """books/*.qmd front matter titles must strictly match canonical volume titles."""
    books_titles = _extract_books_volume_titles(BOOKS_DIR)
    assert len(books_titles) >= 4, f"Expected at least Volumes I-IV in books/, found {books_titles}"
    for vol_key, actual_title in books_titles.items():
        expected_title = CANONICAL_VOLUME_TITLES[vol_key]
        assert (
            actual_title == expected_title
        ), f"Books page mismatch for {vol_key}: got '{actual_title}', expected '{expected_title}'"


def test_geom_index_volume_titles_match_canonical() -> None:
    """Geometry of Motion index.qmd must strictly match canonical volume titles for all Volumes 0-V."""
    index_titles = _extract_geom_index_volume_titles(GEOM_INDEX)
    assert (
        len(index_titles) == 6
    ), f"Expected all 6 volumes (0-V) in Geometry of Motion index, found {index_titles}"
    for vol_key, actual_title in index_titles.items():
        expected_title = CANONICAL_VOLUME_TITLES[vol_key]
        assert (
            actual_title == expected_title
        ), f"Geometry of Motion index mismatch for {vol_key}: got '{actual_title}', expected '{expected_title}'"


def test_each_volume_maps_to_exactly_one_title_everywhere() -> None:
    """Every volume number must map to exactly one unified title across all surfaces."""
    sidebar_titles = _extract_sidebar_volume_titles(QUARTO_YML)
    books_titles = _extract_books_volume_titles(BOOKS_DIR)
    index_titles = _extract_geom_index_volume_titles(GEOM_INDEX)

    all_keys = set(sidebar_titles) | set(books_titles) | set(index_titles)
    for vol_key in sorted(all_keys):
        distinct_titles = {
            t
            for titles_dict in (sidebar_titles, books_titles, index_titles)
            if (t := titles_dict.get(vol_key)) is not None
        }
        assert (
            len(distinct_titles) == 1
        ), f"Multiple conflicting titles found for {vol_key}: {distinct_titles}"
        assert distinct_titles.pop() == CANONICAL_VOLUME_TITLES[vol_key]


def test_no_rendered_volume_page_has_fewer_than_200_words_unless_planned() -> None:
    """No rendered volume page has fewer than 200 words unless explicitly marked Planned."""
    for path in VOLUME_PAGE_PATHS:
        assert path.exists(), f"Volume page not found: {path}"
        content = path.read_text(encoding="utf-8")

        # Exclude frontmatter from word count
        body = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                body = parts[2]

        # Word count of raw body (or if it includes content, words of body)
        word_count = len(body.split())
        is_planned = (
            "status: planned" in content.lower()
            or "planned" in content.lower()
            and word_count < 200
        )

        assert word_count >= 200 or is_planned, (
            f"Volume page '{path.relative_to(REPO_ROOT)}' has only {word_count} words (< 200) "
            f"and is not marked Planned"
        )


def test_books_hub_publishes_concordance_table() -> None:
    """books/index.qmd must publish the volume concordance table covering Volumes 0-V."""
    hub_content = (BOOKS_DIR / "index.qmd").read_text(encoding="utf-8")
    assert "Volume Concordance and Mapping Table" in hub_content
    for vol_key, canonical_title in CANONICAL_VOLUME_TITLES.items():
        assert vol_key in hub_content, f"Missing {vol_key} in books/index.qmd"
        assert canonical_title in hub_content, f"Missing '{canonical_title}' in books/index.qmd"
