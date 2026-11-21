"""The #5520 math-baseline fragment must preserve the shipped log entry during collation."""

import shutil
from datetime import date
from pathlib import Path

import pytest

from shared_scripts.changes_fragment import collate, find_fragments
from shared_scripts.development_log import parse_entries

pytestmark = [pytest.mark.integration, pytest.mark.headless_safe]
ROOT = Path(__file__).resolve().parents[1]
FRAGMENT = "5253-repeatable-math-baseline.md"
DEVLOG = Path("docs/development/DEVELOPMENT_LOG.md")


def test_math_baseline_fragment_collates_without_regressing_shipped_entry(
    tmp_path: Path,
) -> None:
    """Exercise the real merged fragment against the real log in isolated storage."""
    source = ROOT / "changes" / FRAGMENT
    if not source.exists():
        text = (ROOT / DEVLOG).read_text(encoding="utf-8")
        entries = {entry.entry_id: entry for entry in parse_entries(text)}
        assert entries["DL-#5253"].state == "shipped"
        assert "#5520" in entries["DL-#5253"].fields["PR"]
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
    assert before["DL-#5253"] == "shipped"

    collate(
        tmp_path,
        [target],
        pr=5520,
        today=date(2026, 11, 7),
        sha="9b9f988a005cfe422ba713fb33521ec60f8c32d5",
    )

    entries = {entry.entry_id: entry for entry in parse_entries(log.read_text(encoding="utf-8"))}
    assert {key: entry.state for key, entry in entries.items()} == before
    assert "#5520" in entries["DL-#5253"].fields["PR"]
    assert "Review the baseline slice" in entries["DL-#5253"].fields["Next step"]
    assert not target.exists()


def test_all_existing_fragments_preserve_shipped_entries(tmp_path: Path) -> None:
    """Every current fragment must collate without regressing shipped development-log entries."""
    fragments = find_fragments(ROOT)
    for index, fragment_path in enumerate(fragments):
        sub_tmp = tmp_path / f"run_{index}"
        (sub_tmp / "changes").mkdir(parents=True)
        target = sub_tmp / "changes" / fragment_path.name
        shutil.copy(fragment_path, target)
        log = sub_tmp / DEVLOG
        log.parent.mkdir(parents=True)
        shutil.copy(ROOT / DEVLOG, log)
        shutil.copy(ROOT / "SPEC.md", sub_tmp / "SPEC.md")
        before_shipped = {
            e.entry_id
            for e in parse_entries(log.read_text(encoding="utf-8"))
            if e.state == "shipped"
        }
        collate(sub_tmp, [target], pr=9999, today=date(2026, 11, 7), sha="a" * 40)
        after_shipped = {
            e.entry_id
            for e in parse_entries(log.read_text(encoding="utf-8"))
            if e.state == "shipped"
        }
        assert before_shipped.issubset(after_shipped)
        assert not target.exists()
