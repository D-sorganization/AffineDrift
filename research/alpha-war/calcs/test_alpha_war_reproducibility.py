"""Reproducibility guards for Alpha War sensitivity outputs (#5465)."""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

CALCS_DIR = Path(__file__).resolve().parent
if str(CALCS_DIR) not in sys.path:
    sys.path.insert(0, str(CALCS_DIR))

from alpha_war_upstream import LOCK_PATH  # noqa: E402

CALC_JSON = CALCS_DIR / "alpha_war_calculations.json"
MANIFEST_JSON = CALCS_DIR / "alpha_war_regeneration_manifest.json"


class TestAlphaWarReproducibility(unittest.TestCase):
    """Lock file, manifest, and golden numerical anchors for calcs outputs."""

    def test_upstream_lock_has_full_commit_sha(self) -> None:
        """Pinned UpstreamDrift commit must be a full 40-character hex SHA."""
        lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        commit = str(lock["commit"])
        self.assertRegex(commit, r"^[0-9a-f]{40}$")
        self.assertIn("wscg_input_sha256", lock)
        self.assertEqual(len(lock["wscg_input_sha256"]), 3)

    def test_manifest_matches_studies_payload_hash(self) -> None:
        """Manifest studies_sha256 must match the six study blocks in the JSON export."""
        self.assertTrue(CALC_JSON.is_file(), "alpha_war_calculations.json missing")
        self.assertTrue(MANIFEST_JSON.is_file(), "alpha_war_regeneration_manifest.json missing")
        manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        payload = json.loads(CALC_JSON.read_text(encoding="utf-8"))
        studies = {k: v for k, v in payload.items() if k.startswith("study_")}
        digest = hashlib.sha256(json.dumps(studies, indent=2).encode("utf-8")).hexdigest()
        self.assertEqual(manifest.get("studies_sha256"), digest)

    def test_calculations_json_carries_generation_provenance(self) -> None:
        """Exported JSON must record upstream commit and input hashes."""
        payload = json.loads(CALC_JSON.read_text(encoding="utf-8"))
        prov = payload.get("generation_provenance")
        self.assertIsInstance(prov, dict)
        self.assertRegex(str(prov.get("upstream_commit", "")), r"^[0-9a-f]{40}$")
        self.assertIn("wscg_input_sha256", prov)
        self.assertIn("study_1_grip_point_transport", payload)

    def test_golden_table7_anchors_unchanged(self) -> None:
        """Key draft Table 7 / ZTCF numbers must match the stored export."""
        payload = json.loads(CALC_JSON.read_text(encoding="utf-8"))
        study1 = payload["study_1_grip_point_transport"]
        wscg_min = study1["wscg_at_minimum_couple"]
        self.assertAlmostEqual(wscg_min["total_couple_about_mid_hands_nm"], -22.814765666163638)
        self.assertAlmostEqual(wscg_min["sign_flip_station_offset_m"], 0.7370108875058125, places=6)
        snapshots = payload["study_2_couple_vs_sum_of_moments"]["snapshots"]
        min_snap = next(s for s in snapshots if abs(s["time_s"] - 0.2151) < 1e-4)
        ztcf_share_pct = (
            100.0
            * abs(min_snap["ztcf_passive_couple_mid_nm"])
            / abs(min_snap["total_hand_couple_mid_nm"])
        )
        self.assertAlmostEqual(ztcf_share_pct, 86.04, places=2)


if __name__ == "__main__":
    unittest.main()
