"""Verify Chapter 7 tables, ZTCF share, s* separation, and CLM verdicts match calcs and panel audit."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

CALCS_DIR = Path(__file__).resolve().parent
ALPHA_WAR_DIR = CALCS_DIR.parent
JSON_PATH = CALCS_DIR / "alpha_war_calculations.json"

# Draft Table 7.1 (mid-hands and clubhead rows at two time states)
DRAFT_TABLE_7_1 = {
    ("mid_hands", "wscg_at_peak_clubhead_speed"): -14.08,
    ("clubhead_center", "wscg_at_peak_clubhead_speed"): -10.64,
    ("mid_hands", "wscg_at_minimum_couple"): -22.81,
    ("clubhead_center", "wscg_at_minimum_couple"): 8.76,
}


def _find_draft_path() -> Path:
    """Return alpha-war-v1.md if present, else alpha-war-v0.md."""
    v1 = ALPHA_WAR_DIR / "draft" / "alpha-war-v1.md"
    if v1.exists():
        return v1
    return ALPHA_WAR_DIR / "draft" / "alpha-war-v0.md"


class TestAlphaWarDraftTable7(unittest.TestCase):
    """Draft numbers and claim verdicts must match the sensitivity JSON export and panel audit."""

    def test_table_7_1_matches_calculations_json(self) -> None:
        """Draft Table 7.1 moments match ``study_1_grip_point_transport`` in the JSON export."""
        payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        study = payload["study_1_grip_point_transport"]
        for (station, state_key), expected in DRAFT_TABLE_7_1.items():
            block = study[state_key]
            row = next(s for s in block["stations"] if s["station"] == station)
            self.assertAlmostEqual(
                row["reported_alpha_moment_nm"],
                expected,
                places=2,
                msg=f"{station} @ {state_key}",
            )

    def test_ztcf_share_derived_from_json_matches_draft(self) -> None:
        """ZTCF share at t=0.2151 s derived from JSON (86.04%) must match draft prose."""
        payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        snapshots = payload["study_2_couple_vs_sum_of_moments"]["snapshots"]
        min_snap = next(s for s in snapshots if abs(s["time_s"] - 0.2151) < 1e-4)
        ztcf_share_pct = (
            100.0
            * abs(min_snap["ztcf_passive_couple_mid_nm"])
            / abs(min_snap["total_hand_couple_mid_nm"])
        )
        self.assertAlmostEqual(ztcf_share_pct, 86.04, places=2)
        formatted_share = f"{ztcf_share_pct:.2f}%"
        draft_text = _find_draft_path().read_text(encoding="utf-8")
        self.assertIn(formatted_share, draft_text)
        self.assertNotIn("86.15%", draft_text)

    def test_s_star_illustrative_vs_simulated_and_claim_verdicts(self) -> None:
        """Illustrative (+0.213 m) and simulated (+0.737 m) s* values and CLM relabels must be present."""
        payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        study1 = payload["study_1_grip_point_transport"]
        sim_s_star = study1["wscg_at_minimum_couple"]["sign_flip_station_offset_m"]
        illus_s_star = study1["analytical_driver_transport_cases"][0][
            "sign_flip_offset_from_mid_hands_m"
        ]
        self.assertAlmostEqual(sim_s_star, 0.737, places=3)
        self.assertAlmostEqual(illus_s_star, 0.213, places=3)

        draft_text = _find_draft_path().read_text(encoding="utf-8")
        self.assertIn("Unverified - convention mapping required", draft_text)
        self.assertNotIn("Refuted / Definitional Artifact", draft_text)
        self.assertIn(
            "Unverified - primary source check required (VRF-04b)", draft_text
        )
        self.assertIn("Adjudicated by:", draft_text)


if __name__ == "__main__":
    unittest.main()
