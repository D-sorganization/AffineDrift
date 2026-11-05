"""Contract tests for the VIS-SITE-1 visual-placement audit (#5423).

Enforces:
1. The audit is a draft doc with one table whose columns are page, concept,
   proposed visual, source UD model/run and priority.
2. Every row names a page that exists in this repository, a P1-P3 priority,
   and either a pinned UD source or ``needs render``.
3. The table covers ZTCF, the kinematic sequence, the motion-measurement
   series, Alpha War and putting.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
AUDIT = REPO_ROOT / "docs" / "audits" / "vis-site-visual-placement-audit-5423.md"
COLUMNS = ["Page", "Concept", "Proposed visual", "Source UD model/run", "Priority"]
TOPICS = ("ZTCF", "kinematic sequence", "motion measurement", "Alpha War", "putting")
PRIORITIES = frozenset({"P1", "P2", "P3"})
# A pinned UD source cites a UD path or issue and a commit or run id.
PINNED = re.compile(r"UD .*(@ ?[0-9a-f]{8,40}|run [0-9a-f]{12})")


def _rows() -> list[list[str]]:
    lines = [
        line for line in AUDIT.read_text(encoding="utf-8").splitlines() if line.startswith("|")
    ]
    cells = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines]
    assert cells and cells[0] == COLUMNS, f"table header must be {COLUMNS}"
    return [row for row in cells[2:] if row]


def test_audit_is_a_draft_doc() -> None:
    text = AUDIT.read_text(encoding="utf-8")
    assert "Status: draft" in text


def test_table_has_rows_with_the_required_columns() -> None:
    rows = _rows()
    assert len(rows) >= len(TOPICS)
    assert all(len(row) == len(COLUMNS) for row in rows)


@pytest.mark.parametrize("topic", TOPICS)
def test_table_covers_each_required_topic(topic: str) -> None:
    concepts = " ".join(row[1] for row in _rows()).lower()
    assert topic.lower() in concepts, f"no row covers {topic}"


def test_every_row_names_an_existing_page_a_priority_and_a_source() -> None:
    for page, _concept, _visual, source, priority in _rows():
        path = page.strip("`").split(" ")[0]
        assert (REPO_ROOT / path).is_file() or path.startswith("branch:"), f"{path} not found"
        assert priority in PRIORITIES, f"{path}: priority {priority!r}"
        assert source.startswith("needs render") or PINNED.search(source), f"{path}: {source!r}"
