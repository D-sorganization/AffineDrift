"""Figure generator smoke test."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

CALCS_DIR = Path(__file__).resolve().parent
FIG_DIR = CALCS_DIR.parent / "draft" / "figures"


class TestAlphaWarFigures(unittest.TestCase):
    def test_generate_figures(self) -> None:
        subprocess.run(
            ["python3", str(CALCS_DIR / "alpha_war_figures.py")],
            check=True,
            cwd=CALCS_DIR,
        )
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
