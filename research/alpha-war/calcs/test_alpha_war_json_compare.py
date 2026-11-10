"""Tests for Alpha War study JSON tolerance comparison (#5465)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

CALCS_DIR = Path(__file__).resolve().parent
if str(CALCS_DIR) not in sys.path:
    sys.path.insert(0, str(CALCS_DIR))

from alpha_war_json_compare import (  # noqa: E402
    COMPARE_ATOL,
    COMPARE_RTOL,
    JsonCompareError,
    compare_study_blocks,
    load_export,
)

CALC_JSON = CALCS_DIR / "alpha_war_calculations.json"


class TestAlphaWarJsonCompare(unittest.TestCase):
    """Golden export must match itself; tiny mutations must fail tolerance."""

    def test_committed_export_matches_itself(self) -> None:
        """Self-comparison yields zero mismatches under default tolerance."""
        payload = load_export(CALC_JSON)
        summary = compare_study_blocks(payload, payload)
        self.assertEqual(summary["mismatch_count"], 0)
        self.assertLess(float(summary["max_abs_deviation"]), COMPARE_ATOL)

    def test_numeric_mutation_exceeds_tolerance(self) -> None:
        """A one-ulp bump in a study float is reported as a mismatch."""
        payload = load_export(CALC_JSON)
        mutant = load_export(CALC_JSON)
        study3 = mutant["study_3_frame_conventions"]
        study3["input_physical_couple_fsp_nm"]["M_in_plane_n"] += 1e-6
        summary = compare_study_blocks(payload, mutant, rtol=COMPARE_RTOL, atol=COMPARE_ATOL)
        self.assertGreater(summary["mismatch_count"], 0)

    def test_missing_study_block_fails_closed(self) -> None:
        """Dropping a study block is not treated as a numeric match."""
        payload = load_export(CALC_JSON)
        trimmed = {k: v for k, v in payload.items() if k != "study_6_shaft_flex_contribution"}
        with self.assertRaises(JsonCompareError):
            compare_study_blocks(payload, trimmed)


if __name__ == "__main__":
    unittest.main()
