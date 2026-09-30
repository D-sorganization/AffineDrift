"""Repository page UpstreamDrift links must be pinned or labelled (#4542).

``repositories/*.qmd`` links to UpstreamDrift either to cite a specific commit's
state (must carry a `tree|blob|commit` SHA) or to send the reader to browse the
live repository (must say so explicitly, since it is not pinned to any
reviewed revision).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
REPOSITORIES_DIR = ROOT / "repositories"

# A bare link to the UpstreamDrift repository root, not a pinned tree/blob/commit path.
BARE_LINK = re.compile(r'href="https://github\.com/D-sorganization/UpstreamDrift"')
NAVIGATION_LABEL = "navigation only"
LABEL_WINDOW = 200


@pytest.mark.unit
def test_every_bare_upstreamdrift_link_is_labelled_navigation_only() -> None:
    """Every unpinned repository-root link must say it is navigation only."""
    unlabelled: list[str] = []
    for qmd in sorted(REPOSITORIES_DIR.glob("*.qmd")):
        content = qmd.read_text(encoding="utf-8")
        for match in BARE_LINK.finditer(content):
            window = content[match.end() : match.end() + LABEL_WINDOW]
            if NAVIGATION_LABEL not in window:
                unlabelled.append(f"{qmd.name}:{content.count(chr(10), 0, match.start()) + 1}")

    assert unlabelled == [], f"unlabelled, unpinned UpstreamDrift links: {unlabelled}"


@pytest.mark.unit
def test_repositories_directory_has_at_least_the_known_bare_links() -> None:
    """Regression guard: confirms the scan above actually inspects the 16 known links."""
    total = 0
    for qmd in REPOSITORIES_DIR.glob("*.qmd"):
        total += len(BARE_LINK.findall(qmd.read_text(encoding="utf-8")))

    assert total == 16
