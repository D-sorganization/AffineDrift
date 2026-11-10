"""Fail-closed gate when Alpha War UpstreamDrift integration is required (#5465)."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CALCS = ROOT / "research/alpha-war/calcs"


class TestAlphaWarIntegrationGate(unittest.TestCase):
    """``ALPHA_WAR_INTEGRATION_REQUIRED=1`` must error without a pinned checkout."""

    def test_sensitivity_suite_fails_without_upstream_when_required(self) -> None:
        """Integration flag turns missing UpstreamDrift into a hard failure."""
        env = os.environ.copy()
        env["ALPHA_WAR_INTEGRATION_REQUIRED"] = "1"
        env.pop("ALPHA_WAR_UPSTREAM_DRIFT_ROOT", None)
        proc = subprocess.run(  # noqa: S603
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                str(CALCS),
                "-p",
                "test_alpha_war_sensitivity_suite.py",
                "-q",
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(proc.returncode, 0)
        combined = proc.stdout + proc.stderr
        self.assertIn("ALPHA_WAR_INTEGRATION_REQUIRED", combined)


if __name__ == "__main__":
    unittest.main()
