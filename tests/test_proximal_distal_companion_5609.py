"""Regression guards for lay proximal-distal companion content (#5609)."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "articles/proximal_distal_companion/chapters"
PIN = ROOT / "data/companion/proximal_distal_companion_upstream_pin.json"
SOURCE_MANIFEST = ROOT / "articles/proximal_distal_energy_transfer/source_manifest.json"
FALSIFICATION_ATLAS = ROOT / "articles/proximal-distal-falsification-atlas.qmd"
JOURNEY = ROOT / "articles/proximal-distal-a-journey-through-the-swing.qmd"
CANONICAL_FORCE_DIFF = r"\mathbf F_d=(\mathbf F_L-\mathbf F_T)/2"
CANONICAL_SEPARATION = r"\mathbf d=\mathbf r_T-\mathbf r_L"
TWO_HAND_CHAPTERS = (
    "ch04_geometry_machine.qmd",
    "ch06_constraints_push_back.qmd",
    "ch12_two_hands_one_wrench.qmd",
    "ch13_negative_torque.qmd",
    "ch29_whole_swing_ledger.qmd",
    "ch30_curiosity_and_review.qmd",
)


def _chapter_text(name: str) -> str:
    return (CHAPTERS / name).read_text(encoding="utf-8")


def _all_companion_chapter_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in sorted(CHAPTERS.glob("ch*.qmd")))


def test_companion_uses_lead_trail_hand_labels_not_left_right_forces() -> None:
    """Grip mechanics use lead (L) and trail (T); right-hand R subscripts drifted signs (#5609 F2)."""
    forbidden = (
        r"\mathbf F_R",
        r"\mathbf r_R",
        r"F_{Ry}",
        r"F_Ry",
        r"C_{R",
        r"\mathbf r_R",
        r"left and right force",
        r"for $i=L,R$",
    )
    for path in sorted(CHAPTERS.glob("ch*.qmd")):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, f"{path.name} still contains {token!r}"


def test_companion_two_hand_chapters_share_lead_minus_trail_differential_mode() -> None:
    """Common/differential decomposition matches ch04 and ch12 (#5609 F2)."""
    for name in TWO_HAND_CHAPTERS:
        text = _chapter_text(name)
        assert CANONICAL_FORCE_DIFF in text, name
        assert CANONICAL_SEPARATION in text, name


def test_companion_falsification_matrix_links_use_model_completion_filename() -> None:
    """The dead provider path FALSIFICATION_MATRIX.md 404s at the companion pin (#5609 F5)."""
    text = _all_companion_chapter_text()
    assert not re.search(r"(?<!MODEL_COMPLETION_)FALSIFICATION_MATRIX\.md", text)
    assert "MODEL_COMPLETION_FALSIFICATION_MATRIX.md" in text
    pin = __import__("json").loads(PIN.read_text(encoding="utf-8"))["commit"]
    matrix_links = re.findall(
        r"UpstreamDrift/blob/([0-9a-f]{40})/docs/research/proximal_distal_energy_transfer/MODEL_COMPLETION_FALSIFICATION_MATRIX\.md",
        text,
    )
    assert matrix_links, "expected at least one falsification-matrix deep link"
    assert all(ref == pin for ref in matrix_links)


def test_companion_avoids_unqualified_preregistration_claims() -> None:
    """Archive comparisons cite a declared primary criterion unless registration is evidenced (#5609 F3)."""
    for name in ("ch19_model_ladder.qmd", "ch28_practical_synthesis.qmd"):
        text = _chapter_text(name).casefold()
        assert "preregistered" not in text, name
        assert "declared primary" in text


def test_journey_documents_companion_and_monograph_upstream_pins() -> None:
    """Readers see which UpstreamDrift revision applies to lay companion vs monograph atlas (#5609 F1/F4)."""
    companion_commit = json.loads(PIN.read_text(encoding="utf-8"))["commit"]
    manifest_commit = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))["source"]["commit"]
    journey = JOURNEY.read_text(encoding="utf-8")
    assert companion_commit[:8] in journey
    assert manifest_commit[:8] in journey
    assert "Evidence pins" in journey or "evidence pins" in journey.casefold()
    assert companion_commit in journey or companion_commit[:8] in journey
    assert manifest_commit in journey or manifest_commit[:8] in journey


def test_falsification_atlas_prose_matches_imported_monograph_revision() -> None:
    """Atlas timing example links the same UpstreamDrift revision as the generated cards (#5609 F4)."""
    manifest_commit = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))["source"]["commit"]
    atlas_text = FALSIFICATION_ATLAS.read_text(encoding="utf-8")
    assert manifest_commit in atlas_text
    assert (
        f"UpstreamDrift/blob/{manifest_commit}/docs/research/proximal_distal_energy_transfer/"
        "data/rotating_base_torso_velocity_study.json"
    ) in atlas_text


def test_ch11_indexes_bridge_to_lead_trail_convention() -> None:
    """Counterfactual geometry uses contact indices; ch11 must map them to companion lead/trail labels (#5609 F2)."""
    text = _chapter_text("ch11_counterfactual_scissors.qmd")
    assert "sec-lay-ch04" in text or "lead/trail" in text.lower()


def test_ch06_opposing_force_increment_matches_trail_minus_lead_separation() -> None:
    """The lead-positive force pair has moment minus d cross f (#5609 F2)."""
    text = _chapter_text("ch06_constraints_push_back.qmd")
    assert r"\Delta\mathbf M=-\mathbf d\times\mathbf f" in text
    assert r"\Delta\mathbf M=+\mathbf d\times\mathbf f" not in text


def test_ch11_contact_mapping_preserves_defined_separation() -> None:
    """With p1=c+d/2, contact 1 is trail when d points lead to trail."""
    text = _chapter_text("ch11_counterfactual_scissors.qmd")
    assert "$1$ as trail ($T$) and $2$ as lead ($L$)" in text
