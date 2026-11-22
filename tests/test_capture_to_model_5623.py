"""Guard the capture guide's observable contracts and frame boundaries (#5623)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "pages/upstreamdrift-capture-to-model-pipeline.qmd"


def test_pipeline_commands_and_artifacts_are_distinct() -> None:
    """Keep the synthetic fitter separate from the real-session orchestrator."""
    text = GUIDE.read_text(encoding="utf-8")
    for command in (
        "src.motion_capture.reconstruct synth --out",
        "src.motion_capture.reconstruct fit --bundle",
        "src.motion_capture.rig reconstruct --session",
        "src.motion_capture.rig export --session",
        "src.motion_capture.reference.fit_job --config",
        "src.tools.model_converter --validate-only",
    ):
        assert command in text
    for artifact in (
        "observations/<view>.json",
        "intrinsics.json",
        "reconstruct/reconstruction.json",
        "joints_3d_m.npy",
        "model/joint_angles.json",
        "joint_angles_simscape.csv",
    ):
        assert artifact in text


def test_import_profile_declares_handedness_preserving_axis_map() -> None:
    """A complete example must preserve orientation and keep missing data explicit."""
    text = GUIDE.read_text(encoding="utf-8")
    profile = json.loads(re.search(r"```json\n(.*?)\n```", text, re.S).group(1))
    assert profile["units"] == "mm"
    assert profile["axes"] == ["+X", "-Z", "+Y"]
    assert set(profile["joints"]) == {
        "mid_hip",
        "neck",
        "nose",
        *(
            f"{side}_{joint}"
            for side in ("left", "right")
            for joint in ("shoulder", "elbow", "wrist", "hip", "knee", "ankle")
        ),
    }
    assert "NaN" in text and "not interpolated" in text
    assert "Y-up" in text and "Z-up" in text


def test_scaling_example_uses_declared_length_and_inertia_axis() -> None:
    """Check the worked inertia instead of blessing a height-only scaling claim."""
    text = GUIDE.read_text(encoding="utf-8")
    ratio = (0.186 / (0.2817 / 1.741)) ** 2
    assert ratio == pytest.approx(1.3214, rel=1e-4)
    assert "1.321" in text
    assert "de Leva radii with builder lengths" in text
    assert "longitudinal $z$" in text and "longitudinal $x$" in text
    assert "placeholder" in text and "reserve" in text


def test_defaults_and_implementation_links_do_not_conflate_gates() -> None:
    """The 8 px triangulation gate differs from the bundle's 6 px default."""
    text = GUIDE.read_text(encoding="utf-8")
    assert "| Triangulation gate | 8 px |" in text
    assert "| Bundle rejection gate | 6 px |" in text
    assert "20,000 px/s²" in text and "6 Hz" in text
    assert "calibration or timing uncertainty" in " ".join(text.split())
    links = re.findall(
        r"https://github.com/D-sorganization/UpstreamDrift/blob/([^/]+)/([^\s)]+)", text
    )
    assert len(links) >= 10
    assert all(re.fullmatch(r"[0-9a-f]{40}", pin) for pin, _ in links)
