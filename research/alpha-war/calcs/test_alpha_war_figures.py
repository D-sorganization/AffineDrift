"""Figure generator smoke test."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

CALCS_DIR = Path(__file__).resolve().parent
FIG_DIR = CALCS_DIR.parent / "draft" / "figures"

if str(CALCS_DIR) not in sys.path:
    sys.path.insert(0, str(CALCS_DIR))

from alpha_war_figures import main  # noqa: E402


class TestAlphaWarFigures(unittest.TestCase):
    """Smoke-test SVG figure generation from the calculations JSON payload."""

    def test_generate_figures(self) -> None:
        """Running main must write all expected SVG files under draft/figures/."""
        main()
        for name in (
            "fig-transport-stations.svg",
            "fig-filter-cutoff-sweep.svg",
            "fig-couple-vs-com.svg",
            "fig-swing-plane-schematic.svg",
            "fig-nesbit-fig11-schematic.svg",
        ):
            self.assertTrue((FIG_DIR / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
