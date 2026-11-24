"""Contract validation tests for the humanoid UpstreamDrift reuse map and phase 0 index."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs" / "humanoid"
REUSE_MAP_PATH = DOCS_DIR / "upstream-reuse-map.md"

pytestmark = pytest.mark.integration

SCOPED_COMPONENTS = [
    "1. Cross-Engine Parity Harness and Benchmarks",
    "2. Screw / Wrench Math Utilities",
    "3. Optimizer Backend Registry (UD ADR-0050)",
    "4. Replay Benchmarks",
]

REQUIRED_FIELDS = [
    "Provides",
    "Where in UD",
    "Contract",
    "Existing evidence",
    "Gaps",
]


def _get_component_section(component_title: str) -> str:
    """Extract section markdown for a scoped component from the reuse map."""
    text = REUSE_MAP_PATH.read_text(encoding="utf-8")
    heading = f"### {component_title}"
    assert heading in text, f"Missing component heading: {heading}"
    start = text.index(heading) + len(heading)
    rest = text[start:]
    next_idx = len(rest)
    for marker in ("\n### ", "\n## "):
        idx = rest.find(marker)
        if idx != -1 and idx < next_idx:
            next_idx = idx
    return rest[:next_idx]


def _parse_table_fields(section_text: str) -> dict[str, str]:
    """Parse markdown key-value table rows (| Field | Entry |) in section."""
    fields: dict[str, str] = {}
    for line in section_text.splitlines():
        trimmed = line.strip()
        if trimmed.startswith("|") and not trimmed.startswith("| ---"):
            cells = [c.strip() for c in trimmed.strip("|").split("|")]
            if len(cells) == 2 and cells[0] != "Field":
                fields[cells[0]] = cells[1]
    return fields


@pytest.mark.parametrize(
    "artifact_link",
    [
        "../adr/0003-humanoid-expansion-scope-and-phase-gates.md",
        "upstream-reuse-map.md",
        "rights-licence-ledger.md",
        "audience-brief.md",
        "content-metadata-schema.md",
        "outlines/",
    ],
)
def test_humanoid_readme_indexes_phase0_artifacts(artifact_link: str) -> None:
    """Verify docs/humanoid/README.md exists and indexes all Phase-0 artifacts."""
    readme_path = DOCS_DIR / "README.md"
    assert readme_path.exists(), "docs/humanoid/README.md does not exist"
    content = readme_path.read_text(encoding="utf-8")
    assert artifact_link in content, f"Missing link to {artifact_link} in README.md"


@pytest.mark.parametrize("component_title", SCOPED_COMPONENTS)
def test_upstream_reuse_map_covers_all_four_scoped_components(
    component_title: str,
) -> None:
    """Assert each component defines all required fields and an unticked checklist."""
    section = _get_component_section(component_title)
    fields = _parse_table_fields(section)

    for required_field in REQUIRED_FIELDS:
        assert (
            required_field in fields
        ), f"Component '{component_title}' missing field '{required_field}'"
        assert fields[
            required_field
        ], f"Component '{component_title}' field '{required_field}' is empty"

    checklist_items = [
        line.strip() for line in section.splitlines() if line.strip().startswith("- [")
    ]
    assert len(checklist_items) >= 1, f"Component '{component_title}' has no checklist items"
    assert all(
        item.startswith("- [ ]") for item in checklist_items
    ), f"Component '{component_title}' checklist must be unticked"
    assert not any(
        "- [x]" in item.lower() for item in checklist_items
    ), f"Component '{component_title}' checklist contains ticked items"


def test_upstream_reuse_map_marks_unvalidated_gaps_explicitly() -> None:
    """Verify gaps explicitly state unvalidated humanoid applicability and prerequisite citations."""
    text = REUSE_MAP_PATH.read_text(encoding="utf-8")

    # Prerequisites citations without asserting parity is complete
    assert "UD#13789" in text, "Missing citation of epic UD#13789"
    assert "UD#13786" in text, "Missing citation of UD#13786"
    assert "ADR-0050" in text, "Missing citation of ADR-0050"
    assert (
        "No row asserts that UD#13789 or the MJX benchmark work is complete." in text
    ), "Reuse map must confirm UD#13789 and MJX benchmarks are not asserted complete"

    for component_title in SCOPED_COMPONENTS:
        section = _get_component_section(component_title)
        fields = _parse_table_fields(section)
        gaps = fields.get("Gaps", "")
        has_unvalidated_flag = any(
            phrase in gaps.lower()
            for phrase in (
                "not validated",
                "not yet validated",
                "no evidence found for humanoid",
            )
        )
        assert (
            has_unvalidated_flag
        ), f"Component '{component_title}' Gaps does not explicitly mark unvalidated: '{gaps}'"


def test_upstream_reuse_map_enforces_presentation_only_boundary() -> None:
    """Verify boundary enforces AffineDrift presentation-only and links ADRs 0003 and 0001."""
    text = REUSE_MAP_PATH.read_text(encoding="utf-8")

    assert (
        "../adr/0003-humanoid-expansion-scope-and-phase-gates.md" in text
    ), "Reuse map must link ADR 0003"
    assert (
        "../adr/0001-markerless-mocap-publication-boundary.md" in text
    ), "Reuse map must link ADR 0001"
    assert (
        "presentation-only" in text
    ), "Reuse map must explicitly declare presentation-only boundary"
    assert "Heavy dynamics" in text, "Reuse map must declare heavy dynamics stay in UD"
    assert (
        "consumes UD outputs" in text or "consumes outputs only" in text
    ), "Reuse map must declare AffineDrift consumes outputs only"
