"""Tests for single-purpose navbar menus in _quarto.yml (#4497).

Enforces the 6 top-level single-purpose menus (Start, Library, Evidence, Tools,
Resources, About) and ensures zero duplicate links appear across the navbar.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
QUARTO_YML = REPO_ROOT / "_quarto.yml"

EXPECTED_MENUS: tuple[str, ...] = (
    "Start",
    "Library",
    "Evidence",
    "Tools",
    "Resources",
    "About",
)

EXPECTED_MENU_ITEMS: dict[str, list[tuple[str, str]]] = {
    "Start": [
        ("Start Here", "pages/start-here.html"),
        ("The Big Idea", "pages/big-idea.html"),
        ("Learning Paths", "resources/learning-paths.html"),
        ("Glossary", "pages/glossary.html"),
        ("Home", "index.html"),
    ],
    "Library": [
        ("Books & Textbooks", "books/index.html"),
        ("The Physics of Golf", "articles/The_Physics_of_Golf/quarto/index.html"),
        ("The Geometry of Motion", "articles/The_Geometry_of_Motion/quarto/index.html"),
        (
            "Proximal-to-Distal Monograph",
            "articles/proximal_distal_energy_transfer/index.html",
        ),
        ("Theory Series", "pages/drifter-manifesto.html"),
        ("Tangent-Space Series", "pages/tangent-hyperplanes.html"),
        ("Article Index", "resources/articles.html"),
        (
            "How a Golf Swing Carries Energy",
            "articles/proximal-distal-a-journey-through-the-swing.html",
        ),
    ],
    "Evidence": [
        ("Critiques & Responses", "critiques/index.html"),
        ("Core Theses Registry", "articles/core-theses-registry.html"),
        ("Falsification Atlas", "pages/falsification-atlas.html"),
        ("Validation Roadmap", "pages/validation-roadmap.html"),
        ("Technology Overview", "pages/technology.html"),
        ("Force Measurement", "articles/technology-force-measurement.html"),
        ("Motion Capture", "articles/technology-motion-capture.html"),
        ("Launch Monitors", "articles/technology-launch-monitors.html"),
        ("The Reference-Point Problem", "articles/reference-point-problem.html"),
    ],
    "Tools": [
        ("Programs & Tools", "pages/tools.html"),
        ("Programming Companion", "models/models.html"),
        ("Fixture and Dataset Explorer", "models/dataset-explorer.html"),
        ("Datasets", "resources/resources-datasets.html"),
        ("Software", "resources/resources-software.html"),
        ("Repositories", "repositories/repositories.html"),
        ("Club Fitting Simulation", "articles/technology-club-fitting.html"),
        (
            "Multibody Impact Coupling",
            "articles/technology-heavy-hit-impact-coupling.html",
        ),
    ],
    "Resources": [
        ("Resources & Links", "resources/resources.html"),
        ("Bibliography", "resources/bibliography.html"),
        ("Researchers", "resources/resources-researchers.html"),
        ("Papers", "resources/resources-papers.html"),
        ("Videos", "resources/resources-videos.html"),
        ("Websites", "resources/resources-websites.html"),
        ("NotebookLM Notebooks", "resources/resources-notebooklm.html"),
        (
            "Markerless Mocap Camera Selection",
            "articles/markerless-mocap-camera-selection.html",
        ),
    ],
    "About": [
        ("About", "pages/about.html"),
        ("Contact", "pages/contact.html"),
        ("Collaborate", "pages/collaborate.html"),
    ],
}


@pytest.fixture(scope="module")
def navbar_config() -> dict[str, Any]:
    """Load the navbar configuration dictionary from _quarto.yml."""
    raw = yaml.safe_load(QUARTO_YML.read_text(encoding="utf-8"))
    return raw["website"]["navbar"]


def _extract_all_navbar_hrefs(node: Any) -> list[str]:
    """Recursively collect all non-empty href strings across the navbar tree."""
    hrefs: list[str] = []
    if isinstance(node, dict):
        if "href" in node and isinstance(node["href"], str):
            hrefs.append(node["href"].strip())
        for val in node.values():
            hrefs.extend(_extract_all_navbar_hrefs(val))
    elif isinstance(node, list):
        for item in node:
            hrefs.extend(_extract_all_navbar_hrefs(item))
    return hrefs


class TestNavbarSinglePurposeMenus:
    """Test suite asserting single-purpose navbar structure and invariants."""

    def test_navbar_left_has_six_single_purpose_menus(self, navbar_config: dict[str, Any]) -> None:
        """Navbar left must contain exactly the 6 single-purpose menus in order."""
        left = navbar_config.get("left", [])
        actual_menus = tuple(item.get("text") for item in left if "menu" in item)
        assert (
            actual_menus == EXPECTED_MENUS
        ), f"Navbar left menus mismatch. Expected: {EXPECTED_MENUS}, Got: {actual_menus}"

    def test_navbar_left_entries_are_only_the_six_menus(
        self, navbar_config: dict[str, Any]
    ) -> None:
        """Navbar left must contain no rogue items outside the 6 menus."""
        left = navbar_config.get("left", [])
        assert len(left) == len(
            EXPECTED_MENUS
        ), f"Expected {len(EXPECTED_MENUS)} entries in navbar.left, found {len(left)}"

    @pytest.mark.parametrize("menu_title", EXPECTED_MENUS)
    def test_each_menu_matches_item_specification(
        self, navbar_config: dict[str, Any], menu_title: str
    ) -> None:
        """Each menu must contain its specified text and href pairs."""
        left = navbar_config.get("left", [])
        target = next((item for item in left if item.get("text") == menu_title), None)
        assert target is not None, f"Menu {menu_title} not found in navbar.left"

        actual_items = [
            (sub.get("text"), sub.get("href"))
            for sub in target.get("menu", [])
            if isinstance(sub, dict) and "href" in sub
        ]
        expected = EXPECTED_MENU_ITEMS[menu_title]
        assert (
            actual_items == expected
        ), f"Menu {menu_title} items mismatch.\nExpected: {expected}\nGot: {actual_items}"

    def test_no_duplicate_href_across_entire_navbar(self, navbar_config: dict[str, Any]) -> None:
        """No href may appear more than once across the entire navbar."""
        hrefs = _extract_all_navbar_hrefs(navbar_config)
        counts = Counter(hrefs)
        duplicates = {href: count for href, count in counts.items() if count > 1}
        assert not duplicates, f"Duplicate href(s) found in navbar: {duplicates}"
