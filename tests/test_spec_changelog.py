"""Tests for AffineDrift's PR-keyed SPEC.md change-log gate (RM #1520).

Before #1520 the gate's contract was "the row carries the next free serial spec
version and the `Spec Version` field matches it". Every assertion below that
used to be about that serial is now about a pull-request key, which is unique
by construction, plus the two properties the migration had to preserve: no
content was lost, and the shipped `SPEC.md` validates.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_spec_changelog import check, load_spec_changelog

REPO_ROOT = Path(__file__).resolve().parents[1]
SHARED_MODULE = REPO_ROOT / "shared_scripts" / "spec_changelog.py"

HEADER = """# SPEC.md

## 1. Identity

| Field                | Value      |
| -------------------- | ---------- |
| **Spec Version**     | 1.0.290    |
| **Last Spec Update** | 2026-09-03 |

## 12. Change Log

| Date       | PR    | Changes    |
| ---------- | ----- | ---------- |
"""


@pytest.fixture(scope="module")
def sc():
    """The fleet-shared change-log module, loaded the way the gate loads it."""
    module = load_spec_changelog(SHARED_MODULE)
    assert module is not None, "shared_scripts/spec_changelog.py must be vendored"
    return module


def _spec(*rows: str) -> str:
    return HEADER + "".join(f"{row}\n" for row in rows)


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "SPEC.md"
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


# ---------------------------------------------------------------------------
# The new format
# ---------------------------------------------------------------------------


def test_pr_keyed_row_is_accepted(tmp_path: Path) -> None:
    """The canonical `| date | #pr | summary |` row passes the gate."""
    spec = _write(tmp_path, _spec("| 2026-09-03 | #1520 | key rows by PR |"))
    assert check(spec, module_path=SHARED_MODULE) == []


def test_two_distinct_pr_keys_are_accepted(tmp_path: Path) -> None:
    """Two concurrent pull requests each add a row; both survive."""
    spec = _write(
        tmp_path,
        _spec(
            "| 2026-09-03 | #4201 | one change |",
            "| 2026-09-03 | #4202 | another change |",
        ),
    )
    assert check(spec, module_path=SHARED_MODULE) == []


def test_legacy_no_key_marker_is_accepted(tmp_path: Path) -> None:
    """A migrated historical row with no recoverable reference is tolerated."""
    spec = _write(tmp_path, _spec("| 2026-01-04 | n/a | historical entry (spec 1.0.42) |"))
    assert check(spec, module_path=SHARED_MODULE) == []


# ---------------------------------------------------------------------------
# What replaced the serial-version assertions
# ---------------------------------------------------------------------------


def test_serial_version_in_the_key_column_is_rejected(tmp_path: Path) -> None:
    """A serial spec version where the key belongs is an error naming the fix."""
    spec = _write(tmp_path, _spec("| 2026-09-03 | 1.0.291 | bumped the serial |"))
    failures = check(spec, module_path=SHARED_MODULE)
    assert failures, "a serial-keyed row must not pass"
    joined = " ".join(failures)
    assert "serial spec version" in joined
    assert "#<pr or issue number>" in joined


def test_duplicate_post_cutover_key_is_rejected(tmp_path: Path) -> None:
    """Reusing a PR key means a row was copied instead of edited."""
    spec = _write(
        tmp_path,
        _spec(
            "| 2026-09-04 | #4300 | first row |",
            "| 2026-09-05 | #4300 | copied row |",
        ),
    )
    failures = check(spec, module_path=SHARED_MODULE)
    assert any("duplicate change-log key #4300" in failure for failure in failures)


def test_duplicate_pre_cutover_key_is_tolerated(tmp_path: Path, sc) -> None:
    """History nobody can change is exempt: one issue, several pull requests.

    Several AffineDrift entries predating the cutover genuinely share a
    governing issue, so enforcing uniqueness over them would fail the gate on
    the past.
    """
    assert sc.PR_KEYED_SINCE == "2026-09-03"
    spec = _write(
        tmp_path,
        _spec(
            "| 2026-08-30 | #4104 | bounded retry policy (spec 1.0.276) |",
            "| 2026-09-01 | #4104 | live-only retry closure (spec 1.0.278) |",
        ),
    )
    assert check(spec, module_path=SHARED_MODULE) == []


def test_header_field_need_not_match_the_newest_row(tmp_path: Path) -> None:
    """The `Spec Version` equality requirement is gone, not relaxed.

    That equality was the second half of the treadmill: the field is a global
    counter every pull request had to bump. It is release-derived now.
    """
    spec = _write(tmp_path, _spec("| 2026-09-03 | #1520 | key rows by PR |"))
    text = spec.read_text(encoding="utf-8")
    assert "1.0.290" in text, "the fixture still carries an unrelated header value"
    assert check(spec, module_path=SHARED_MODULE) == []


def test_malformed_key_is_rejected(tmp_path: Path) -> None:
    """A key that is neither `#<number>` nor the legacy marker fails."""
    spec = _write(tmp_path, _spec("| 2026-09-03 | PR-1520 | wrong key shape |"))
    failures = check(spec, module_path=SHARED_MODULE)
    assert any("must be '#<number>'" in failure for failure in failures)


def test_empty_summary_is_rejected(tmp_path: Path) -> None:
    """A row still has to say what changed."""
    spec = _write(tmp_path, _spec("| 2026-09-03 | #1520 |  |"))
    failures = check(spec, module_path=SHARED_MODULE)
    assert any("empty summary" in failure for failure in failures)


def test_unparsable_change_log_names_the_row_format(tmp_path: Path) -> None:
    """The pre-migration heading-entry form fails with an actionable message."""
    spec = _write(
        tmp_path,
        "# SPEC.md\n\n## 12. Change Log\n\n### 1.0.288 Some Entry (#4128)\n\nProse.\n",
    )
    failures = check(spec, module_path=SHARED_MODULE)
    assert failures
    assert "| YYYY-MM-DD | #<pr> | summary |" in " ".join(failures)


# ---------------------------------------------------------------------------
# Migration and the shipped file
# ---------------------------------------------------------------------------


def test_migration_preserves_every_row_summary(sc) -> None:
    """Campaign invariant 2: row count is unchanged and no summary is lost."""
    before = _spec(
        "| 2026-08-30 | 1.0.276 | bounded retry policy for #4104 |",
        "| 2026-09-02 | 1.0.288 | root hygiene cleanup for #4128 |",
    )
    before_rows = sc.parse_changelog(before).rows
    after, rewritten = sc.migrate_text(before)
    after_rows = sc.parse_changelog(after).rows

    assert rewritten == 2
    assert len(after_rows) == len(before_rows)
    for old, new in zip(before_rows, after_rows, strict=True):
        assert old.summary.rstrip() in new.summary
        assert f"(spec {old.key})" in new.summary
    assert [row.key for row in after_rows] == ["#4104", "#4128"]


def test_migration_is_idempotent(sc) -> None:
    """Re-running the migration changes nothing."""
    once, _ = sc.migrate_text(_spec("| 2026-09-02 | 1.0.288 | root hygiene cleanup for #4128 |"))
    twice, changed = sc.migrate_text(once)
    assert changed == 0
    assert twice == once


def test_shipped_spec_validates() -> None:
    """The SPEC.md this repository actually ships passes the gate."""
    assert check(REPO_ROOT / "SPEC.md", module_path=SHARED_MODULE) == []


def test_shipped_spec_carries_no_serial_keyed_rows(sc) -> None:
    """No row in the shipped file still keys on a serial version."""
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    changelog = sc.parse_changelog(text)
    assert changelog.rows, "the shipped change log must not be empty"
    assert changelog.is_pr_keyed
    for row in changelog.rows:
        assert not sc._SEMVER_RE.match(row.key), f"serial-keyed row: {row.render()}"


def test_shipped_spec_has_a_row_for_this_change(sc) -> None:
    """A substantive PR adds a row — this one included."""
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    keys = {row.key for row in sc.parse_changelog(text).rows}
    assert "#1520" in keys


# ---------------------------------------------------------------------------
# Fail-open on a partial rollout (campaign invariant 7)
# ---------------------------------------------------------------------------


def test_missing_shared_module_warns_rather_than_failing(tmp_path: Path) -> None:
    """A repository that gets the gate before the module is not blocked."""
    spec = _write(tmp_path, _spec("| 2026-09-03 | 1.0.291 | serial-keyed |"))
    assert check(spec, module_path=tmp_path / "absent.py") == []


def test_absent_spec_is_not_an_error(tmp_path: Path) -> None:
    """No SPEC.md means nothing to check."""
    assert check(tmp_path / "nope.md", module_path=SHARED_MODULE) == []


# ---------------------------------------------------------------------------
# Vendored file integrity & drift prevention (RM #1525, AD #4146)
# ---------------------------------------------------------------------------


def test_vendored_helpers_match_pinned_hashes() -> None:
    """Vendored spec-changelog helpers must match pinned SHA256 hashes from Repository_Management."""
    import hashlib

    expected_digests = {
        "shared_scripts/spec_changelog.py": "9a9dd5eaf38dd4bdd8ebb9ef9424155296ff7b4e59e5907570a56bea22439418",
        "scripts/spec_rows_merge_driver.py": "c908a4a15bfc831143fd1b2514d3ffb32beb74fb3143ffd7a52ea9ebc8476a5b",
        "scripts/install_spec_merge_driver.py": "ab682df2063f9df01bf8dc3abb81b2678906ad8476a573147868265971818b57",
    }
    for rel_path, expected_hash in expected_digests.items():
        full_path = REPO_ROOT / rel_path
        assert full_path.exists(), f"Vendored file missing: {rel_path}"
        actual_hash = hashlib.sha256(full_path.read_bytes()).hexdigest()
        assert actual_hash == expected_hash, (
            f"Vendored file {rel_path} has drifted from upstream Repository_Management. "
            f"Expected {expected_hash}, got {actual_hash}."
        )


def test_driver_command_is_worktree_relative() -> None:
    """The merge driver command must use a relative script path, not an absolute worktree path."""
    from scripts.install_spec_merge_driver import DRIVER_SCRIPT, driver_command

    cmd = driver_command(REPO_ROOT)
    assert DRIVER_SCRIPT in cmd
    assert not Path(DRIVER_SCRIPT).is_absolute()
    # Confirm it does not embed repo root / worktree path
    assert str(REPO_ROOT) not in cmd
    assert REPO_ROOT.as_posix() not in cmd

