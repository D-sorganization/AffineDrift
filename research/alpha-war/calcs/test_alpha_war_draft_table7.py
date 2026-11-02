"""Verify Chapter 7 Table 7.1 values match alpha_war_calculations.json."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

CALCS_DIR = Path(__file__).resolve().parent
JSON_PATH = CALCS_DIR / "alpha_war_calculations.json"

# Draft Table 7.1 (mid-hands and clubhead rows at two time states)
DRAFT_TABLE_7_1 = {
    ("mid_hands", "wscg_at_peak_clubhead_speed"): -14.08,
    ("clubhead_center", "wscg_at_peak_clubhead_speed"): -10.64,
    ("mid_hands", "wscg_at_minimum_couple"): -22.81,
    ("clubhead_center", "wscg_at_minimum_couple"): 8.76,
}


class TestAlphaWarDraftTable7(unittest.TestCase):
    """Table 7.1 in alpha-war-v0.md must match the sensitivity JSON export."""

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


if __name__ == "__main__":
    unittest.main()
