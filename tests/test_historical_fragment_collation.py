"""Historical PR fragments must not regress terminal development-log entries."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from shared_scripts.changes_fragment import FragmentError, collate, load_fragment

pytestmark = [pytest.mark.integration, pytest.mark.headless_safe]

REPO_ROOT = Path(__file__).resolve().parents[1]
FRAGMENT_SOURCE = REPO_ROOT / "changes" / "5102-lock-prettier-drift-contracts-for-shot-p.md"
FRAGMENT_NAME = FRAGMENT_SOURCE.name
DEVLOG_RELATIVE = Path("docs/development/DEVELOPMENT_LOG.md")
COLLATION_DATE = date(2026, 10, 21)
COLLATION_SHA = "abcdef0123456789abcdef0123456789abcdef01"
HISTORICAL_FRAGMENT = """---
issue: 5102
summary: "Lock prettier drift contracts for shot-pattern and companion snapshots"
next_step: "Merge after CI; technical-review.md stays owner-pinned drift."
branch: "chore/prettier-drift-5102"
---

Refs #5102 only. technical-review.md intentionally not reformatted or prettierignored.
"""
SHIPPED_ENTRY = """# Development Log

## Active

## Shipped

### DL-#5102 · Apply Prettier to Files Already Drifted on Main; Ignore the Attested Companion Snapshot

- **State:** shipped
- **Owner:** unassigned
- **Issue:** #5102
- **Branch:** merged via #5104
- **PR:** #5104
- **Paths:** see #5104
- **Started:** 2026-10-20
- **Last verified:** 2026-10-20 (`f09ccaa6`; collated from changes/5102-apply-prettier-to-files-already-drifted.md)
- **Summary:** Apply prettier to files already drifted on main; ignore the attested companion snapshot
- **Next step:** Shipped in PR #5104.
"""


def _scratch_repo(root: Path, source_path: Path | None) -> tuple[Path, Path]:
    """Build isolated collation inputs, falling back to durable historical fixtures."""
    devlog = root / DEVLOG_RELATIVE
    devlog.parent.mkdir(parents=True)
    spec_text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    spec_lines = [
        line
        for line in spec_text.splitlines()
        if not (line.startswith("|") and "#5110" in line)
    ]
    (root / "SPEC.md").write_text("\n".join(spec_lines) + "\n", encoding="utf-8")
    devlog.write_text(SHIPPED_ENTRY, encoding="utf-8", newline="\n")
    fragment = root / "changes" / FRAGMENT_NAME
    fragment.parent.mkdir()
    if source_path is not None and source_path.is_file():
        fragment_text = source_path.read_text(encoding="utf-8")
        if source_path == FRAGMENT_SOURCE:
            assert fragment_text == HISTORICAL_FRAGMENT
    else:
        fragment_text = HISTORICAL_FRAGMENT
    fragment.write_text(fragment_text, encoding="utf-8", newline="\n")
    return fragment, devlog


def _assert_shipped_entry_preserved(devlog: str) -> None:
    """Check historical identity, provenance, terminal state, and obligation."""
    entry = devlog.split("### DL-#5102 ·", maxsplit=1)[1]
    assert "- **State:** shipped" in entry
    assert "- **PR:** #5104, #5110" in entry
    assert "- **Started:** 2026-10-20" in entry
    assert "- **Paths:** see #5104" in entry
    assert "- **Next step:** Merge after CI; technical-review.md stays owner-pinned drift." in entry


@pytest.mark.parametrize("source_exists", [True, False])
def test_historical_pr_collates_when_source_fragment_is_present_or_removed(
    tmp_path: Path, source_exists: bool
) -> None:
    source_path = FRAGMENT_SOURCE if source_exists else tmp_path / "already-collated.md"
    fragment, devlog_path = _scratch_repo(tmp_path, source_path)
    parsed_fragment = load_fragment(fragment)
    assert parsed_fragment.dl_state is None
    assert parsed_fragment.next_step == (
        "Merge after CI; technical-review.md stays owner-pinned drift."
    )
    assert parsed_fragment.handoff == (
        "Refs #5102 only. technical-review.md intentionally not reformatted or prettierignored."
    )

    deleted = collate(
        tmp_path,
        [fragment],
        pr=5110,
        today=COLLATION_DATE,
        sha=COLLATION_SHA,
    )

    assert deleted == [fragment]
    assert not fragment.exists()
    spec = (tmp_path / "SPEC.md").read_text(encoding="utf-8")
    assert (
        "| 2026-10-21 | #5110 | Lock prettier drift contracts for shot-pattern and companion snapshots |"
        in spec
    )
    _assert_shipped_entry_preserved(devlog_path.read_text(encoding="utf-8"))


def test_terminal_state_regression_keeps_all_collation_inputs_unchanged(
    tmp_path: Path,
) -> None:
    fragment, devlog_path = _scratch_repo(tmp_path, source_path=None)
    fragment_text = fragment.read_text(encoding="utf-8")
    fragment_text = fragment_text.replace(
        'summary: "Lock prettier drift contracts for shot-pattern and companion snapshots"\n',
        'summary: "Lock prettier drift contracts for shot-pattern and companion snapshots"\n'
        'dl_state: "in_review"\n',
        1,
    )
    fragment.write_text(fragment_text, encoding="utf-8", newline="\n")
    targets = (fragment, tmp_path / "SPEC.md", devlog_path)
    before = {path: path.read_bytes() for path in targets}

    with pytest.raises(FragmentError, match="is shipped; it never moves to in_review"):
        collate(
            tmp_path,
            [fragment],
            pr=5110,
            today=COLLATION_DATE,
            sha=COLLATION_SHA,
        )

    assert {path: path.read_bytes() for path in targets} == before
