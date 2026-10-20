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

REPO_ROOT = Path(__file__).resolve().parent.parent
BOOK_DIR = REPO_ROOT / "articles" / "forward_dynamics_matching"
LINK_VALIDATION = BOOK_DIR / "link_validation.json"
UPSTREAM_COMMIT = "d7c7d07add0d7407a5a3376d5fe4a97aee9112a0"
QUALIFICATION_JSON = (
    "docs/development/simscape_tour_matching/native_evidence/"
    "two_window_fit_9967_102/simscape_replay_qualification.json"
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PROVENANCE_CAVEAT = "Cross-repo provenance caveat"


def _entries() -> list[dict]:
    data = json.loads(LINK_VALIDATION.read_text(encoding="utf-8"))
    return [e for e in data["links"] if "path" in e]


def _chapter(name: str) -> str:
    return (BOOK_DIR / name).read_text(encoding="utf-8")


# --- 1. content digests for cited upstream artifacts -----------------------


def test_every_cited_upstream_artifact_records_a_digest_status() -> None:
    entries = _entries()
    assert entries, "no UpstreamDrift artifacts found in link_validation.json"
    for entry in entries:
        assert entry["evidence_commit"] == UPSTREAM_COMMIT, entry["path"]
        kind = entry.get("kind")
        assert kind in {"blob", "tree"}, f"{entry['path']}: missing kind"
        if kind == "blob":
            assert SHA256_RE.match(entry.get("content_sha256", "")), entry["path"]
            assert entry.get("snapshot_status") in {"vendored", "digest_only"}, entry["path"]
        else:
            assert entry.get("content_sha256") is None, entry["path"]
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
    data = json.loads(LINK_VALIDATION.read_text(encoding="utf-8"))
    assert "network_only_gaps" in data
    assert "digest_only" in data["network_only_gaps"]
    assert "pending_network_stop" in data["network_only_gaps"]


def test_numeric_sources_are_vendored() -> None:
    by_path = {e["path"]: e for e in _entries()}
    assert by_path[QUALIFICATION_JSON]["snapshot_status"] == "vendored"


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

QUALIFIERS = (
    "diagnostic",
    "unmeasured",
    "synthetic-only",
    "decline to repeat",
    "declines to repeat",
    "not consistent",
    "discrepancy",
    "inconsisten",
    "per the cited",
    "the cited",
)
TRIGGER_RE = re.compile(r"promot|speed-?up", re.IGNORECASE)
FIGURE_RE = re.compile(r"\d")


def lint_promoted_speedups(text: str) -> list[str]:
    """Return sentences citing a promoted/speedup figure without a qualifier."""
    flagged: list[str] = []
    for para in re.split(r"\n\s*\n", text):
        for sentence in re.split(r"(?<=[.!?])\s+", para):
            if not (TRIGGER_RE.search(sentence) and FIGURE_RE.search(sentence)):
                continue
            if sentence.lstrip().startswith(("description:", "**Evidence")):
                continue
            lowered = sentence.lower()
            if not any(q in lowered for q in QUALIFIERS):
                flagged.append(sentence.strip())
    return flagged


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
