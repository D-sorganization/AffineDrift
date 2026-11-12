"""Change fragment for Slack Take-Up witness tracking retarget (#5284)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGES = ROOT / "changes"


def test_fragment_5284_retargets_slack_takeup_from_5136() -> None:
    """Owner option (a) from #5282: fragments for the witness article attach to #5284."""
    paths = sorted(CHANGES.glob("5284-*.md"))
    if len(paths) == 1:
        text = paths[0].read_text(encoding="utf-8")
        assert re.search(r"^issue:\s*5284\s*$", text, re.MULTILINE)
        assert "tests/test_change_fragment_5284_slack_takeup.py" in text
        assert "docs/development/consolidation-manifest-5136.md" in text
        assert "#5136" in text
        assert "#5282" in text or "5282" in text
        return

    assert not paths, f"expected at most one 5284-* fragment, got {[p.name for p in paths]}"
    devlog = (ROOT / "docs/development/DEVELOPMENT_LOG.md").read_text(encoding="utf-8")
    assert "### DL-#5284" in devlog
    assert "### DL-#5282" in devlog
