"""Navbar information-architecture contract (EPIC #3140 D1).

The site's top-level navigation exposes four focused dropdowns
(Read / Technology / Build / Connect) plus the Home link, with the legacy
Learn and Explore labels removed. Each dropdown is capped at 11 items (including
separators) so the proximal--distal reader and its model workbench can remain
discoverable without allowing unbounded menu growth.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
QUARTO_YML = REPO_ROOT / "_quarto.yml"

# Hard limits — the IA contract.
EXPECTED_DROPDOWNS: frozenset[str] = frozenset({"Read", "Technology", "Build", "Connect"})
MAX_ITEMS_PER_DROPDOWN: int = 11
FORBIDDEN_TOP_LEVEL_LABELS: frozenset[str] = frozenset({"Learn", "Explore"})


@pytest.fixture(scope="module")
def navbar() -> dict:
    data = yaml.safe_load(QUARTO_YML.read_text(encoding="utf-8"))
    return data["website"]["navbar"]


def test_page_footer_links_publication_and_executable_companions() -> None:
    website = yaml.safe_load(QUARTO_YML.read_text(encoding="utf-8"))["website"]
    footer = website["page-footer"]

    assert "independent open research" in footer["left"].casefold()
    links = {item["text"]: item["href"] for item in footer["right"]}
    assert links["AffineDrift Source"].endswith("/AffineDrift")
    assert links["UpstreamDrift Programs"].endswith("/UpstreamDrift")
    assert links["About & Authority"] == "pages/about.html"


def _left_entries(navbar: dict) -> list[dict]:
    """Return the navbar 'left' array as a list of dicts (LOD helper)."""
    return list(navbar.get("left", []))


def _dropdown_labels(navbar: dict) -> list[str]:
    return [e["text"] for e in _left_entries(navbar) if "menu" in e]


def _entry_with_label(navbar: dict, label: str) -> dict:
    for entry in _left_entries(navbar):
        if entry.get("text") == label:
            return entry
    raise AssertionError(f"navbar entry with text={label!r} not found")


class TestTopLevelStructure:
    def test_home_link_present(self, navbar: dict) -> None:
        labels = [e["text"] for e in _left_entries(navbar)]
        assert "Home" in labels

    def test_expected_number_of_dropdowns(self, navbar: dict) -> None:
        expected = len(EXPECTED_DROPDOWNS)
        labels = _dropdown_labels(navbar)
        assert (
            len(labels) == expected
        ), f"Expected {expected} dropdowns, got {len(labels)}: {labels}"

    def test_dropdowns_match_the_ia_contract(self, navbar: dict) -> None:
        assert set(_dropdown_labels(navbar)) == EXPECTED_DROPDOWNS

    @pytest.mark.parametrize("label", sorted(FORBIDDEN_TOP_LEVEL_LABELS))
    def test_forbidden_label_absent(self, navbar: dict, label: str) -> None:
        assert label not in _dropdown_labels(
            navbar
        ), f"Forbidden top-level label still present: {label}"


class TestDropdownContent:
    @pytest.mark.parametrize("label", sorted(EXPECTED_DROPDOWNS))
    def test_dropdown_has_menu(self, navbar: dict, label: str) -> None:
        entry = _entry_with_label(navbar, label)
        assert "menu" in entry, f"{label} is not a dropdown"

    @pytest.mark.parametrize("label", sorted(EXPECTED_DROPDOWNS))
    def test_dropdown_within_item_budget(self, navbar: dict, label: str) -> None:
        entry = _entry_with_label(navbar, label)
        count = len(entry["menu"])
        assert (
            count <= MAX_ITEMS_PER_DROPDOWN
        ), f"{label} dropdown has {count} items; budget is {MAX_ITEMS_PER_DROPDOWN}"


class TestReadDropdownContent:
    """The 'Read' dropdown is the primary content path — keep it focused."""

    def test_includes_physics_of_golf(self, navbar: dict) -> None:
        menu = _entry_with_label(navbar, "Read")["menu"]
        hrefs = [item.get("href", "") for item in menu]
        assert any("The_Physics_of_Golf" in h for h in hrefs)

    def test_includes_geometry_of_motion(self, navbar: dict) -> None:
        menu = _entry_with_label(navbar, "Read")["menu"]
        hrefs = [item.get("href", "") for item in menu]
        assert any("The_Geometry_of_Motion" in h for h in hrefs)

    def test_includes_bibliography(self, navbar: dict) -> None:
        menu = _entry_with_label(navbar, "Read")["menu"]
        hrefs = [item.get("href", "") for item in menu]
        assert any("bibliography" in h for h in hrefs)

    def test_includes_learning_paths(self, navbar: dict) -> None:
        """IA cleanup (#3222): surface the buried learning-paths feature."""
        menu = _entry_with_label(navbar, "Read")["menu"]
        hrefs = [item.get("href", "") for item in menu]
        assert any("learning-paths" in h for h in hrefs)


class TestBuildDropdownContent:
    """Build points to curated hubs; engine leaves belong on the model hub."""

    def test_build_menu_is_hub_first(self, navbar: dict) -> None:
        menu = _entry_with_label(navbar, "Build")["menu"]
        labels = {item.get("text", "") for item in menu}

        assert {
            "Golf Modeling Suite",
            "Repositories",
            "Datasets",
            "Software Catalog",
            "Interactive Tools",
        }.issubset(labels)
        assert not {"MuJoCo", "Drake", "Pinocchio", "OpenSim", "MyoSim", "Simulink"}.intersection(
            labels
        )
