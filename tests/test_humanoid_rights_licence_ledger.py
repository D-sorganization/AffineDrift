"""Keep phase-zero artifact reviews explicit and prevent accidental approval."""

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
