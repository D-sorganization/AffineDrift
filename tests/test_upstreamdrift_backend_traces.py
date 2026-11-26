"""Executable documentation contracts for the backend trace guide (Refs #5620)."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "pages/upstreamdrift-backend-traces.qmd"
PIN = "2867049f33a57637ee766b351538cc8f96e62cd6"
pytestmark = pytest.mark.integration


def example_blocks() -> list[str]:
    """Extract the sequential runnable Python examples from the public guide."""
    return re.findall(r"```python\n(.*?)```", PAGE.read_text(encoding="utf-8"), re.DOTALL)


def test_guide_pins_sources_and_explains_sample_alignment() -> None:
    """Keep the time/control alignment and persistence caveats visible to readers."""
    text = PAGE.read_text(encoding="utf-8")
    assert PIN in text
    links = re.findall(r"https://github.com/D-sorganization/UpstreamDrift/blob/([^/)]+)", text)
    assert links and set(links) == {PIN}
    for required in (
        "horizon + 1",
        "zero-padded",
        "relative to the rollout",
        "coordinate_units_json",
        "effort_units_json",
        "silently skipped",
        "BatchTrace",
        "upstreamdrift-engine-protocol.html",
    ):
        assert required in text
    blocks = example_blocks()
    assert len(blocks) == 2
    for block in blocks:
        compile(block, str(PAGE), "exec")


def test_examples_against_upstream(tmp_path: Path) -> None:
    """Run the literal guide, including HDF5 inspection, against a provider checkout."""
    upstream = os.environ.get("UPSTREAMDRIFT_ROOT")
    if not upstream:
        pytest.skip("Set UPSTREAMDRIFT_ROOT to the guide's pinned UpstreamDrift checkout")
    provider = Path(upstream).resolve()
    assert (provider / "src/shared/python/simulation_backends/protocol.py").is_file()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(provider)
    result = subprocess.run(
        [sys.executable, "-c", "\n".join(example_blocks())],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
