"""Tests for MM-5 review panel critiques and draft enhancements (#5413)."""

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs" / "development" / "motion-measurement"
PART1 = DOCS_DIR / "part-1-representing-orientation.qmd"
PART2 = DOCS_DIR / "part-2-joint-coordinates-velocity-consequences.qmd"

CRITIQUE_DOCS = DOCS_DIR / "critiques" / "mm5-panel-review.md"
CRITIQUE_RESEARCH = (
    REPO_ROOT / "research" / "motion-measurement" / "critiques" / "mm5-panel-review.md"
)

REQUIRED_SEATS = [
    "Rigid-body math",
    "Golf measurement practice",
    "Numerical rigor",
    "Lay reader",
]


def _split_frontmatter(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    assert len(parts) >= 3, f"Missing YAML frontmatter in {path}"
    fm = yaml.safe_load(parts[1])
    assert isinstance(fm, dict), f"Frontmatter in {path} must be a dict"
    return fm, parts[2]


def test_critique_documents_exist_and_match() -> None:
    assert CRITIQUE_DOCS.exists(), f"Missing {CRITIQUE_DOCS}"
    assert CRITIQUE_RESEARCH.exists(), f"Missing {CRITIQUE_RESEARCH}"
    text_docs = CRITIQUE_DOCS.read_text(encoding="utf-8")
    text_res = CRITIQUE_RESEARCH.read_text(encoding="utf-8")
    assert text_docs == text_res, "Docs and research critique files must match identically"


def test_critique_covers_all_four_seats() -> None:
    text = CRITIQUE_DOCS.read_text(encoding="utf-8")
    for seat in REQUIRED_SEATS:
        assert seat in text, f"Seat '{seat}' missing from critique review"


def test_critique_disposition_table_structure() -> None:
    text = CRITIQUE_DOCS.read_text(encoding="utf-8")
    assert "Disposition Table" in text or "disposition table" in text.lower()

    # Find table rows with finding status
    # Expect rows formatted like: | F-... | ADDRESSED/DEFERRED | ... |
    finding_rows = re.findall(
        r"\|\s*(F-[A-Z0-9_-]+)\s*\|\s*(ADDRESSED|DEFERRED)\s*\|\s*([^|]+)\|", text
    )
    assert (
        len(finding_rows) >= 6
    ), f"Expected at least 6 findings in disposition table, found {len(finding_rows)}"

    statuses = {row[1] for row in finding_rows}
    assert "ADDRESSED" in statuses, "Must have ADDRESSED findings"
    assert "DEFERRED" in statuses, "Must have DEFERRED findings"

    for finding_id, _status, rationale in finding_rows:
        assert (
            len(rationale.strip()) > 10
        ), f"Finding {finding_id} has insufficient rationale: '{rationale}'"


def test_critique_seat_status_and_degradation_ledger() -> None:
    text = CRITIQUE_DOCS.read_text(encoding="utf-8")
    assert "Seat Status" in text or "Degradation Ledger" in text or "Status and Degradation" in text
    assert "subscription" in text.lower()
    assert "zero pay-per-use" in text.lower() or "0 pay-per-use" in text.lower()
    for seat in REQUIRED_SEATS:
        assert seat in text


def test_draft_frontmatter_and_verify_tags_preserved() -> None:
    for path in (PART1, PART2):
        fm, body = _split_frontmatter(path)
        assert fm.get("draft") is True, f"{path} draft flag must remain True"
        assert fm.get("listing") is False, f"{path} listing flag must remain False"
        assert "[VERIFY]" not in body, f"{path} must not contain [VERIFY] tags"
