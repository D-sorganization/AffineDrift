"""Figure generator unit tests for Alpha War draft figures."""

from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path

CALCS_DIR = Path(__file__).resolve().parent
JSON_PATH = CALCS_DIR / "alpha_war_calculations.json"
DRAFT_DIR = CALCS_DIR.parent / "draft"
FIG_DIR = DRAFT_DIR / "figures"

if str(CALCS_DIR) not in sys.path:
    sys.path.insert(0, str(CALCS_DIR))

from alpha_war_figures import main  # noqa: E402


def _current_draft_text() -> str:
    """Return text of alpha-war-v1.md if assembled, else alpha-war-v0.md."""
    v1 = DRAFT_DIR / "alpha-war-v1.md"
    v0 = DRAFT_DIR / "alpha-war-v0.md"
    target = v1 if v1.is_file() else v0
    return target.read_text(encoding="utf-8")


class TestAlphaWarFigures(unittest.TestCase):
    """Verify SVG figure generation and JSON-derived annotations."""

    def test_generate_figures(self) -> None:
        """Running main must write all expected SVG files under draft/figures/."""
        main()
        for name in (
            "fig-transport-stations.svg",
            "fig-filter-cutoff-sweep.svg",
            "fig-couple-vs-com.svg",
            "fig-club-roll-projection.svg",
            "fig-swing-plane-schematic.svg",
            "fig-nesbit-fig11-schematic.svg",
        ):
            self.assertTrue((FIG_DIR / name).is_file(), name)

    def test_fig1_transport_stations_matches_json(self) -> None:
        """Fig 1 must plot M(s)=C-s*R_y with simulated and illustrative s* from JSON."""
        main()
        payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        study1 = payload["study_1_grip_point_transport"]
        s_star_sim = study1["wscg_at_minimum_couple"]["sign_flip_station_offset_m"]
        c_sim = study1["wscg_at_minimum_couple"]["total_couple_about_mid_hands_nm"]
        ry_sim = study1["wscg_at_minimum_couple"]["resultant_axial_normal_n"][1]
        self.assertAlmostEqual(s_star_sim, c_sim / ry_sim, places=6)

        case1 = study1["analytical_driver_transport_cases"][0]
        s_star_ill = case1["sign_flip_offset_from_mid_hands_m"]
        c_ill = case1["couple_about_mid_hands_nm"]
        ry_ill = case1["resultant_force_n"][1]
        self.assertAlmostEqual(s_star_ill, c_ill / ry_ill, places=6)

        svg = (FIG_DIR / "fig-transport-stations.svg").read_text(encoding="utf-8")
        self.assertIn(f"+{s_star_sim:.3f} m", svg)
        self.assertIn(f"+{s_star_ill:.3f} m", svg)
        self.assertIn("simulated", svg.lower())
        self.assertIn("illustrative", svg.lower())
        self.assertIn("<polygon", svg)
        self.assertIn("sensitivity", svg.lower())
        self.assertIn("F_FSP", svg)
        self.assertIn("+CCW uncocking", svg)
        self.assertIn("N·m", svg)
        self.assertIn("Plain-language takeaway:", svg)

        draft = _current_draft_text()
        self.assertIn("figures/fig-transport-stations.svg", draft)
        self.assertIn("Plain-language takeaway (Figure 1):", draft)

    def test_fig3_club_roll_projection_matches_json(self) -> None:
        """Fig 3 must plot M_alpha,club(phi) with illustrative phi*=61.93 deg from JSON."""
        main()
        payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        fsp = payload["study_3_frame_conventions"]["input_physical_couple_fsp_nm"]
        phi_star_deg = math.degrees(math.atan2(-fsp["M_in_plane_n"], fsp["M_out_of_plane_p"]))
        self.assertAlmostEqual(phi_star_deg, 61.92751306414704, places=6)

        svg = (FIG_DIR / "fig-club-roll-projection.svg").read_text(encoding="utf-8")
        self.assertIn(f"{phi_star_deg:.2f} deg", svg)
        self.assertIn("illustrative", svg.lower())
        self.assertIn("<polygon", svg)
        self.assertIn("F_club", svg)
        self.assertIn("F_FSP", svg)
        self.assertIn("+CCW uncocking", svg)
        self.assertIn("N·m", svg)
        self.assertIn("deg", svg)
        self.assertIn("Plain-language takeaway:", svg)

        draft = _current_draft_text()
        self.assertIn("figures/fig-club-roll-projection.svg", draft)
        self.assertIn("Plain-language takeaway (Figure 3):", draft)


if __name__ == "__main__":
    unittest.main()
