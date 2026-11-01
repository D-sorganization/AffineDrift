"""Unit tests for the Alpha War sensitivity and mechanism calculation suite."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

CALCS_DIR = Path(__file__).resolve().parent
if str(CALCS_DIR) not in sys.path:
    sys.path.insert(0, str(CALCS_DIR))

from alpha_war_sensitivity_suite import (
    run_study_1_grip_point_transport,
    run_study_2_couple_vs_sum_of_moments,
    run_study_3_frame_conventions,
    run_study_4_filtering_and_drag_sensitivity,
    run_study_5_closed_loop_and_identifiability,
    run_study_6_shaft_flex_contribution,
)


class TestAlphaWarSensitivitySuite(unittest.TestCase):
    """Test suite verifying all six Alpha War mechanics and sensitivity studies."""

    def test_study_1_grip_point_transport_sign_flip(self) -> None:
        """Verify reference-point transport shifts and flips the reported alpha moment."""
        res = run_study_1_grip_point_transport()
        wscg_min = res["wscg_at_minimum_couple"]
        self.assertLess(wscg_min["total_couple_about_mid_hands_nm"], -20.0)
        stations = {
            s["station"]: s["reported_alpha_moment_nm"] for s in wscg_min["stations"]
        }
        self.assertLess(stations["butt_end"], 0.0)
        self.assertLess(stations["mid_hands"], 0.0)
        self.assertGreater(stations["clubhead_center"], 0.0)

        case_pos = res["analytical_driver_transport_cases"][0]
        self.assertTrue(np.isclose(case_pos["couple_about_mid_hands_nm"], -16.0))
        com_moment = next(
            s["moment_nm"] for s in case_pos["stations"] if s["station"] == "club_com_G"
        )
        self.assertTrue(np.isclose(com_moment, 38.0))

    def test_study_2_couple_vs_sum_of_moments_decomposition(self) -> None:
        """Verify exact additivity of hand couple and moment of net force about COM."""
        res = run_study_2_couple_vs_sum_of_moments()
        for snap in res["snapshots"]:
            expected_sum = (
                snap["total_hand_couple_mid_nm"] + snap["moment_of_force_about_com_nm"]
            )
            self.assertTrue(
                np.isclose(snap["sum_of_moments_about_com_nm"], expected_sum, atol=1e-9)
            )

    def test_study_3_frame_conventions_norm_invariance(self) -> None:
        """Verify Euclidean norm invariance under clubface roll rotation."""
        res = run_study_3_frame_conventions()
        fsp = res["input_physical_couple_fsp_nm"]
        norm_fsp = np.linalg.norm(
            [fsp["M_shaft_t"], fsp["M_out_of_plane_p"], fsp["M_in_plane_n"]]
        )
        for row in res["jacobs_club_frame_roll_sweep"]:
            norm_club = np.linalg.norm(
                [
                    row["club_frame_alpha_couple_nm"],
                    row["club_frame_beta_couple_nm"],
                    row["club_frame_gamma_couple_nm"],
                ]
            )
            self.assertTrue(np.isclose(norm_fsp, norm_club, atol=1e-12))

    def test_study_4_filtering_sign_reversal_and_drag_bias(self) -> None:
        """Verify low cutoff (8 Hz) flips negative impact couple positive while collision bleed inflates it."""
        res = run_study_4_filtering_and_drag_sensitivity()
        self.assertLess(res["true_couple_at_impact_nm"], -15.0)
        by_fc = {row["cutoff_hz"]: row for row in res["butterworth_cutoff_sweep"]}
        self.assertGreater(by_fc[8.0]["clean_filtered_at_impact_nm"], 0.0)
        self.assertLess(by_fc[30.0]["clean_filtered_at_impact_nm"], -14.0)
        self.assertLess(
            by_fc[30.0]["across_impact_filtered_at_impact_nm"],
            by_fc[30.0]["clean_filtered_at_impact_nm"] - 15.0,
        )

    def test_study_5_closed_loop_identifiability_and_zero_arm(self) -> None:
        """Verify rank-5 point-force map, rank-6 full-wrench map, and zero-arm null couple."""
        res = run_study_5_closed_loop_and_identifiability()
        self.assertEqual(res["bilateral_point_force_map"]["rank"], 5)
        self.assertEqual(res["bilateral_point_force_map"]["nullity"], 1)
        self.assertEqual(res["bilateral_full_wrench_map"]["rank"], 6)
        self.assertEqual(res["bilateral_full_wrench_map"]["nullity"], 6)
        attr = res["two_arm_closed_loop_state_attribution"]
        self.assertTrue(np.isclose(attr["additivity_residual_nm"], 0.0, atol=1e-12))
        self.assertTrue(
            np.isclose(attr["zero_grip_separation_moment_nm"], 0.0, atol=1e-12)
        )

    def test_study_6_shaft_flex_contribution(self) -> None:
        """Verify matched 3-link flexible shaft decomposition and beam rebound couple."""
        res = run_study_6_shaft_flex_contribution()
        contrib = res["upstream_drift_matched_3link_study"][
            "distal_angular_accel_contributions_rad_s2"
        ]
        sum_terms = (
            contrib["control"]
            + contrib["momentum"]
            + contrib["gravity"]
            + contrib["joint_damping"]
            + contrib["shaft_elastic"]
            + contrib["shaft_damping"]
        )
        self.assertTrue(np.isclose(sum_terms, contrib["total"], atol=1e-6))
        rebound = res["two_hand_beam_rebound_wrench_model"]
        self.assertLess(rebound["net_equivalent_grip_couple_nm"], -20.0)


if __name__ == "__main__":
    unittest.main()
