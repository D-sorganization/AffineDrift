"""Repository review #4719: historical screw-theory research outline boundaries.

Numerical radar rank, TDM budget, and appendix wording remain in
test_radar_screw_appendix_review.py and test_launch_monitor_estimation_rigor.py.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
OUTLINE = (
    ROOT / "articles/Launch_Monitor_Technology_Review/research/screw-theory-research-outline.md"
)


@pytest.mark.parametrize(
    "unsupported",
    [
        "honest covariances",
        "swing plane as free projections",
        "face normal ∥ line of sight at",
        "continuous ω truth",
        "a skidding ball's passes through the CG",
        "~\\$20–50",
        "≥71% of marker velocity is ISA-rotational",
        "novel, near-term",
    ],
)
def test_outline_does_not_repeat_disproved_inference(unsupported: str) -> None:
    assert unsupported not in OUTLINE.read_text(encoding="utf-8")


def test_outline_banner_records_completed_adjudication_pass() -> None:
    banner = OUTLINE.read_text(encoding="utf-8").split("---", 1)[0]
    assert "Qualification Pending" not in banner
    assert "4719" in banner
    assert "proposal" in banner.lower() or "conditional" in banner.lower()


def test_outline_sections_distinguish_proposals_from_measurements() -> None:
    body = OUTLINE.read_text(encoding="utf-8")
    assert "experiment status" in body.lower() or "proposal only" in body.lower()
    assert "E7 is the" in body
    assert "proof-of-concept" in body
    assert "not executed" in body.lower() or "unexecuted" in body.lower()


def test_experiment_table_marks_unexecuted_hardware_rows() -> None:
    body = OUTLINE.read_text(encoding="utf-8")
    assert "| Status |" in body or "proposal" in body[body.find("## 8.") :].lower()
