"""Regression guards for Drake autodiff permalinks (issue #5608)."""

from __future__ import annotations

from pathlib import Path

from src.tools.utils.fdm_link_validation import UPSTREAM_EVIDENCE_COMMIT, upstream_artifact_entries

REPO_ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = REPO_ROOT / "articles" / "forward_dynamics_matching"
LINK_VALIDATION = BOOK_DIR / "link_validation.json"
DRAKE_TEST_PATH = "tests/test_drake_fit_swing_autodiff.py"
DRAKE_DRIVER_PATH = "src/engines/physics_engines/drake/python/motion_matching/fit_swing_autodiff.py"
PIN_URL = f"https://github.com/D-sorganization/UpstreamDrift/blob/{UPSTREAM_EVIDENCE_COMMIT}/{DRAKE_TEST_PATH}"
DRIVER_URL = f"https://github.com/D-sorganization/UpstreamDrift/blob/{UPSTREAM_EVIDENCE_COMMIT}/{DRAKE_DRIVER_PATH}"


def _link_by_path(path: str) -> dict:
    import json

    data = json.loads(LINK_VALIDATION.read_text(encoding="utf-8"))
    for entry in upstream_artifact_entries(data):
        if entry.get("path") == path:
            return entry
    raise AssertionError(f"missing link_validation entry for {path}")


def test_link_validation_records_drake_autodiff_test_at_evidence_pin() -> None:
    entry = _link_by_path(DRAKE_TEST_PATH)
    assert entry["evidence_commit"] == UPSTREAM_EVIDENCE_COMMIT
    assert entry["url"].endswith(DRAKE_TEST_PATH)


def test_gradient_and_software_chapters_cite_drake_autodiff_at_evidence_pin() -> None:
    """Chapters must not cite a newer commit/path than the book's link_validation pin."""
    gradients = (BOOK_DIR / "10_gradients.qmd").read_text(encoding="utf-8")
    assert PIN_URL in gradients
    assert DRIVER_URL in gradients
    contracts = (BOOK_DIR / "23_software_contracts.qmd").read_text(encoding="utf-8")
    assert PIN_URL in contracts
    for text in (gradients, contracts):
        assert "625a16e6897b88ab29fb5a64c65ecee820dd58f5" not in text
        assert "tests/engines/drake/test_drake_fit_swing_autodiff.py" not in text
