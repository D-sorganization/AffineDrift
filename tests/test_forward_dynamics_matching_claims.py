"""Claim-level guards for the Forward Dynamics Matching book (issue #5088).

``test_forward_dynamics_matching_book.py`` holds the structural-integrity tests
(directory, chapter count, manifest hashes of the chapters themselves). This
module checks what the book *claims* about UpstreamDrift:

* every cited UpstreamDrift artifact has a recorded content SHA-256, verified
  against a vendored snapshot where one exists (network-only gaps are explicit);
* the gate numbers quoted in the historical-lessons chapter match the vendored
  qualification receipt and are pinned verbatim;
* the "decline to repeat promoted speedups" policy is enforced by a lint.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from src.tools.utils.fdm_link_validation import (
    UPSTREAM_EVIDENCE_COMMIT,
    LinkValidationError,
    load_link_validation,
    upstream_artifact_entries,
    validate_link_validation_document,
)
from src.tools.utils.fdm_promoted_speedup import lint_promoted_speedups

REPO_ROOT = Path(__file__).resolve().parent.parent
BOOK_DIR = REPO_ROOT / "articles" / "forward_dynamics_matching"
LINK_VALIDATION = BOOK_DIR / "link_validation.json"
QUALIFICATION_JSON = (
    "docs/development/simscape_tour_matching/native_evidence/"
    "two_window_fit_9967_102/simscape_replay_qualification.json"
)
PROVENANCE_CAVEAT = "Cross-repo provenance caveat"


def _link_data() -> dict:
    return load_link_validation(LINK_VALIDATION)


def _entries() -> list[dict]:
    return upstream_artifact_entries(_link_data())


def _chapter(name: str) -> str:
    return (BOOK_DIR / name).read_text(encoding="utf-8")


# --- 1. content digests for cited upstream artifacts -----------------------


def test_link_validation_loader_rejects_malformed_json(tmp_path: Path) -> None:
    bad = tmp_path / "link_validation.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(LinkValidationError, match="invalid JSON"):
        load_link_validation(bad)


def test_link_validation_loader_rejects_incomplete_upstream_row(tmp_path: Path) -> None:
    payload = {
        "links": [
            {
                "url": "https://example.com/x",
                "path": "missing_fields.md",
                "evidence_commit": UPSTREAM_EVIDENCE_COMMIT,
            }
        ],
        "network_only_gaps": "digest_only pending_network_stop",
    }
    path = tmp_path / "link_validation.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(LinkValidationError):
        load_link_validation(path)


def test_every_cited_upstream_artifact_records_a_digest_status() -> None:
    entries = _entries()
    assert entries, "no UpstreamDrift artifacts found in link_validation.json"
    for entry in entries:
        assert entry["evidence_commit"] == UPSTREAM_EVIDENCE_COMMIT, entry["path"]
        kind = entry.get("kind")
        assert kind in {"blob", "tree"}, f"{entry['path']}: missing kind"
        if kind == "blob":
            assert entry.get("snapshot_status") in {"vendored", "digest_only"}, entry["path"]
        else:
            assert entry.get("snapshot_status") == "directory_not_digestible", entry["path"]


def test_vendored_snapshots_match_recorded_digests() -> None:
    vendored = [e for e in _entries() if e.get("snapshot_status") == "vendored"]
    assert vendored, "expected at least the numeric receipts to be vendored"
    for entry in vendored:
        snap = REPO_ROOT / entry["snapshot_path"]
        assert snap.is_file(), f"missing snapshot {entry['snapshot_path']}"
        digest = hashlib.sha256(snap.read_bytes()).hexdigest()
        assert digest == entry["content_sha256"], f"digest drift for {entry['path']}"


def test_network_only_gaps_are_stated_explicitly() -> None:
    data = _link_data()
    gaps = data["network_only_gaps"]
    assert "digest_only" in gaps
    assert "pending_network_stop" in gaps


def test_numeric_sources_are_vendored() -> None:
    by_path = {e["path"]: e for e in _entries()}
    assert by_path[QUALIFICATION_JSON]["snapshot_status"] == "vendored"


def test_real_link_validation_document_passes_contract() -> None:
    validate_link_validation_document(_link_data())


# --- 2. verbatim regression assertions for gate numbers ---------------------


def test_gate_numbers_match_vendored_receipt_and_chapter() -> None:
    entry = next(e for e in _entries() if e["path"] == QUALIFICATION_JSON)
    receipt = json.loads((REPO_ROOT / entry["snapshot_path"]).read_text(encoding="utf-8"))
    assert receipt["is_qualified"] is False
    terminal_m = receipt["gates"][-1]["measured"] if "gates" in receipt else None
    flat = json.dumps(receipt)
    assert "terminal RMSE 40.30 mm > 35.00 mm" in flat
    assert terminal_m is None or terminal_m == pytest.approx(0.0403, abs=1e-4)

    text = _chapter("03_historical_lessons.qmd")
    assert "40.303 mm" in text
    assert "35 mm" in text
    assert "35 mm gate" in text
    assert "is_qualified: false" in text


# --- 3. caveats and attribution --------------------------------------------


@pytest.mark.parametrize("chapter", ["02_upstream_inventory.qmd", "03_historical_lessons.qmd"])
def test_chapters_open_with_provenance_caveat(chapter: str) -> None:
    lines = _chapter(chapter).split("\n# ", 1)[1].splitlines()
    head = "\n".join(lines[:6])
    assert PROVENANCE_CAVEAT in head, f"{chapter}: caveat not at top"
    assert "link_validation.json" in head


def test_gate_numbers_are_attributed_not_bare() -> None:
    text = _chapter("03_historical_lessons.qmd")
    sentence = next(s for s in re.split(r"(?<=\.)\s+", text) if "40.303 mm" in s)
    assert re.search(r"\b(cited|records|reports|says)\b", sentence), sentence


# --- 4. promoted-speedup policy lint ---------------------------------------


def test_lint_flags_unqualified_promoted_speedup() -> None:
    assert lint_promoted_speedups("The promoted surrogate gives a 12x speedup.")
    assert lint_promoted_speedups("UpstreamDrift reports a 3.5 times speed-up.")


def test_lint_accepts_qualified_statements() -> None:
    ok = "The model card lists a 12x speedup, but receipts are diagnostic only."
    assert not lint_promoted_speedups(ok)
    assert not lint_promoted_speedups("We decline to repeat the promoted 12x figure.")


def test_book_has_no_unqualified_promoted_speedup_figures() -> None:
    problems = {
        qmd.name: lint_promoted_speedups(qmd.read_text(encoding="utf-8"))
        for qmd in sorted(BOOK_DIR.glob("*.qmd"))
    }
    problems = {k: v for k, v in problems.items() if v}
    assert not problems, f"unqualified promoted/speedup figures: {problems}"
