"""The #5521 planning fragment must preserve the original ledger's shipped state."""

from datetime import date
from pathlib import Path

import pytest

from shared_scripts.changes_fragment import collate
from shared_scripts.development_log import parse_entries

pytestmark = [pytest.mark.integration, pytest.mark.headless_safe]
ROOT = Path(__file__).resolve().parents[1]
FRAGMENT = "5176-outline-ledger-candidates.md"
DEVLOG = Path("docs/development/DEVELOPMENT_LOG.md")


def test_rights_candidate_fragment_collates_without_regressing_shipped_entry(
    tmp_path: Path,
) -> None:
    """Exercise the real merged fragment against the real log in isolated storage."""
    source = ROOT / "changes" / FRAGMENT
    if not source.exists():
        text = (ROOT / DEVLOG).read_text(encoding="utf-8")
        entries = {entry.entry_id: entry for entry in parse_entries(text)}
        assert entries["DL-#5176"].state == "shipped"
        assert "#5521" in entries["DL-#5176"].fields["PR"]
        return
    target = tmp_path / "changes" / FRAGMENT
    target.parent.mkdir()
    target.write_bytes(source.read_bytes())
    log = tmp_path / DEVLOG
    log.parent.mkdir(parents=True)
    log.write_bytes((ROOT / DEVLOG).read_bytes())
    (tmp_path / "SPEC.md").write_bytes((ROOT / "SPEC.md").read_bytes())
    before = {
        entry.entry_id: entry.state for entry in parse_entries(log.read_text(encoding="utf-8"))
    }
    assert before["DL-#5176"] == "shipped"

    collate(
        tmp_path,
        [target],
        pr=5521,
        today=date(2026, 11, 7),
        sha="ece74650b5e87e25f698c09f79bd94eb072656e8",
    )

    entries = {entry.entry_id: entry for entry in parse_entries(log.read_text(encoding="utf-8"))}
    assert {key: entry.state for key, entry in entries.items()} == before
    assert "#5521" in entries["DL-#5176"].fields["PR"]
    assert "rights decisions remain owner-gated" in entries["DL-#5176"].fields["Next step"]
    assert not target.exists()
