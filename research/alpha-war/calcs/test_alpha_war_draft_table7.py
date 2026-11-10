"""Verify Chapter 7 tables, ZTCF share, s* separation, and CLM verdicts match calcs and panel."""

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

    def test_wscg_ztcf_provenance_language_present_5462(self) -> None:
        """Draft must label WSCG bundle as modeled and ZTCF ratio as diagnostic (#5462)."""
        draft_text = _find_draft_path().read_text(encoding="utf-8")
        self.assertNotIn("unavoidable mathematical consequence", draft_text.lower())
        self.assertIn("project-originated planar WSCG bundle", draft_text)
        self.assertIn(
            "### Table 7.1: Reference-Point Transport on Simulated WSCG Trajectory", draft_text
        )
        self.assertIn("measured share of physiological muscle torque", draft_text)
        claims = (ALPHA_WAR_DIR / "work" / "03_claims.md").read_text(encoding="utf-8")
        self.assertIn("86.04", claims)
        self.assertIn("measured muscle share", claims)
        self.assertIn("modeled", claims.lower())

    def test_s_star_illustrative_vs_simulated_and_claim_verdicts(self) -> None:
        """Illustrative (+0.213 m) and simulated (+0.737 m) s* and CLM relabels must exist."""
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
        self.assertIn("Unverified - primary source check required (VRF-04b)", draft_text)
        self.assertIn("Adjudicated by:", draft_text)

    def test_vrf_cut_and_reframe_5397(self) -> None:
        """VRF-09 and rain clip must be cut; VRF-01/03/04/07/08 reframed; App D adjudicated."""
        draft_text = _find_draft_path().read_text(encoding="utf-8")
        for forbidden in (
            "rain-soaked professional tournament",
            "rain-release",
            "private coaching forum whose name",
            "[VERIFY: PGA Tour",
            "[VERIFY: Tutelman",
            "[VERIFY webinars]",
        ):
            self.assertNotIn(forbidden, draft_text)

        self.assertIn("[@manzella2020webinar]", draft_text)
        self.assertIn("[@sinclair2020workshop]", draft_text)

        app_d = draft_text.split("## Appendix D:")[1]
        for vrf_id in (
            "VRF-01",
            "VRF-02",
            "VRF-03",
            "VRF-04",
            "VRF-04b",
            "VRF-05",
            "VRF-06",
            "VRF-07",
            "VRF-08",
            "VRF-09",
            "VRF-10",
        ):
            line = next(ln for ln in app_d.splitlines() if f"**{vrf_id}**" in ln)
            self.assertIn("Adjudicated by:", line, msg=f"Missing adjudication on {vrf_id}")

    def test_vrf_verify_first_5398(self) -> None:
        """VRF-04b, VRF-10, VRF-02, and VRF-06 outcomes must be verified and recorded in App D."""
        draft_text = _find_draft_path().read_text(encoding="utf-8")
        bib_text = (ALPHA_WAR_DIR / "references.bib").read_text(encoding="utf-8")

        # VRF-04b: Kwon FSP/axle-chain papers cited; CLM-LIT-05 unverified without [VERIFY]
        self.assertIn("[@kwon2012fsp; @madrid2020axle]", draft_text)
        self.assertNotIn("`[VERIFY]`", draft_text.split("## 8.2")[1].split("## 8.3")[0])

        # VRF-10: Explicitly called a new proposal alongside ISB standards
        self.assertIn("[@wu2002isb; @wu2005isb]", draft_text)
        self.assertIn("@article{wu2002isb", bib_text)
        self.assertIn("@article{wu2005isb", bib_text)
        self.assertIn("new methodological proposal", draft_text)

        # VRF-02 & VRF-06: Jacobs & Nesbit (2019) 339 pp. and Jacobs (2020) documented
        self.assertIn("339 pp.", bib_text)
        self.assertIn("[@jacobs2019science; @jacobs2020lookinside]", draft_text)

    def test_v1_assembly_boxed_caveats_and_no_verify_5401(self) -> None:
        """Draft v1 must exist with App B primer, boxed caveats, provisional sign, no [VERIFY]."""
        v1 = ALPHA_WAR_DIR / "draft" / "alpha-war-v1.md"
        v0 = ALPHA_WAR_DIR / "draft" / "alpha-war-v0.md"
        self.assertTrue(v1.is_file(), "alpha-war-v1.md must exist")
        self.assertFalse(v0.is_file(), "alpha-war-v0.md must be renamed via git mv")

        draft_text = v1.read_text(encoding="utf-8")
        self.assertNotIn("[VERIFY", draft_text)
        self.assertNotIn("VERIFY]", draft_text)

        # App B convention-mapping primer
        app_b = draft_text.split("## Appendix B:")[1].split("## Appendix C:")[0]
        self.assertIn("### B.0 Convention-Mapping Primer:", app_b)
        for required_term in (
            "Positive Alpha Rotation",
            "Moment Components",
            "Transport Direction",
            "Plain-language lead:",
        ):
            self.assertIn(required_term, app_b)

        # Boxed callouts for filtering and 12-DOF split-grip under-identifiability
        self.assertIn('::: {.callout-warning title="Box 6.2:', draft_text)
        self.assertIn('::: {.callout-important title="Box 6.3:', draft_text)
        self.assertIn('::: {.callout-important title="Box 8.1:', draft_text)
        self.assertNotIn(
            "LAYER 2: THE COMPONENT DISCREPANCY (Muscular Driving Refuted)", draft_text
        )
        self.assertIn("not declared settled", draft_text)

    def test_table_7_10_study_6_matches_json_5463(self) -> None:
        """Draft Table 7.10 and §7.6 prose track `study_6` JSON (#5463)."""
        payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        study = payload["study_6_shaft_flex_contribution"]["upstream_drift_matched_3link_study"]
        flex = study["distal_angular_accel_contributions_flexible_rad_s2"]
        rigid = study["distal_angular_accel_contributions_rigid_rad_s2"]
        iface = study["shaft_interface_force_xy_n"]

        for block in (flex, rigid):
            tot = sum(block[k] for k in block if k != "total")
            self.assertAlmostEqual(block["total"], tot, places=3)

        checks = (
            ("flex control", flex["control"], -401.55, 2),
            ("flex momentum", flex["momentum"], 57.05, 2),
            ("flex gravity", flex["gravity"], 1.86, 2),
            ("flex joint_damping", flex["joint_damping"], 47.55, 2),
            ("flex shaft_elastic", flex["shaft_elastic"], 325.28, 2),
            ("flex shaft_damping", flex["shaft_damping"], -5.42, 2),
            ("flex total", flex["total"], 24.77, 2),
            ("rigid control", rigid["control"], 58.84, 2),
            ("rigid momentum", rigid["momentum"], -22.83, 2),
            ("rigid gravity", rigid["gravity"], -3.21, 2),
            ("rigid joint_damping", rigid["joint_damping"], -7.79, 2),
            ("rigid total", rigid["total"], 25.01, 2),
            ("iface Fx", iface[0], 8.73, 2),
            ("iface Fy", iface[1], 55.69, 2),
        )
        for _label, value, expected, places in checks:
            self.assertAlmostEqual(value, expected, places=places)

        draft_text = _find_draft_path().read_text(encoding="utf-8")
        section_76 = draft_text.split("## 7.6")[1].split("# 8.")[0]
        for phrase in (
            "### Table 7.10:",
            "Distal $\\ddot{q}$: Control",
            "Hypothetical Two-Hand Beam",
        ):
            self.assertIn(phrase, section_76)
        self.assertNotIn("overpowering voluntary wrist muscles", section_76.lower())

    def test_executive_summary_shaft_kick_interface_not_overpower_proof_5463(self) -> None:
        """§1 executive summary must state interface balance, not universal shaft dominance."""
        draft_text = _find_draft_path().read_text(encoding="utf-8")
        block = draft_text.split("### 3. Two Hands on One Handle")[1].split("## The Two-Layer")[0]
        self.assertIn("Newton", block)
        self.assertIn("1\\text{ to }10\\text{ N}\\cdot\\text{m}", block)
        self.assertNotIn("naturally resist this violent kick", block.lower())
        self.assertIn("not a standalone proof", block.lower())

    def test_work_claims_clm_mch_03_hypothesis_separation_5463(self) -> None:
        """Work claim matrix must separate hypothetical beam scalars from rollout (#5463)."""
        claims_path = ALPHA_WAR_DIR / "work" / "03_claims.md"
        claims_text = claims_path.read_text(encoding="utf-8")
        row = next(ln for ln in claims_text.splitlines() if "CLM-MCH-03" in ln)
        self.assertIn("scenario-dependent", row.lower())
        self.assertIn("#5463", row)
        narrative = claims_text.split("### Claim CLM-MCH-03:")[1].split("---", 1)[0]
        self.assertIn("hypothetical", narrative.lower())
        self.assertIn("not** interchangeable", narrative)


if __name__ == "__main__":
    unittest.main()
