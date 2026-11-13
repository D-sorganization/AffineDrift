"""Keep phase-zero artifact reviews explicit and prevent accidental approval."""

import re
from pathlib import Path

import pytest

LEDGER = Path(__file__).resolve().parents[1] / "docs/humanoid/rights-licence-ledger.md"
pytestmark = pytest.mark.integration


def ledger_rows() -> dict[str, list[str]]:
    """Read the six-column artifact table, excluding its header and separator."""
    lines = LEDGER.read_text(encoding="utf-8").splitlines()
    rows = [line.strip("| ").split("|") for line in lines if line.startswith("|")]
    return {cells[0].strip(): [cell.strip() for cell in cells] for cells in rows[2:]}


@pytest.mark.parametrize(
    "artifact",
    [
        "MuJoCo Menagerie models",
        "Unitree robot models (URDF/MJCF)",
        "Open X-Embodiment",
        "LeRobot datasets/models",
    ],
)
def test_artifact_review_is_pending(artifact: str) -> None:
    row = ledger_rows()[artifact]
    assert len(row) == 6
    assert all(row)
    assert row[-1] == "PENDING"


def test_rights_ledger_amass_is_on_hold() -> None:
    assert ledger_rows()["AMASS"][-1] == "ON-HOLD"


def test_rights_ledger_amass_has_no_licence_reading() -> None:
    assert ledger_rows()["AMASS"][2] == "Terms not reviewed; no licence interpretation recorded"


def test_ledger_template_has_required_columns() -> None:
    header = next(line for line in LEDGER.read_text().splitlines() if line.startswith("|"))
    assert [cell.strip().lower() for cell in header.strip("| ").split("|")] == [
        "artifact",
        "version",
        "licence",
        "intended use",
        "reviewer",
        "decision",
    ]


@pytest.mark.parametrize("outline", sorted((LEDGER.parent / "outlines").glob("series-*.md")))
def test_outline_candidates_resolve_to_distinct_ledger_rows(outline: Path) -> None:
    """Every declared outline candidate needs an explicit, uncleared planning row."""
    rows = ledger_rows()
    section = outline.read_text(encoding="utf-8").split("## Engines and Datasets\n", 1)[1]
    section = section.split("\n## ", 1)[0]
    candidates = [
        line.split("|")[1].strip() for line in section.splitlines() if line.startswith("|")
    ][2:]
    assert candidates, f"No candidate table found in {outline.name}"
    for candidate in candidates:
        engines = re.findall(r"\b(?:MuJoCo|Drake|Pinocchio|MJX)\b", candidate)
        artifacts = [f"{engine} engine" for engine in engines] or [candidate]
        for artifact in artifacts:
            assert artifact in rows, f"{outline.name}: missing ledger row for {artifact}"
            assert len(rows[artifact]) == 6 and all(rows[artifact])
            assert rows[artifact][-1] == ("ON-HOLD" if artifact == "AMASS" else "PENDING")
            assert rows[artifact][-2] == "Unassigned"
