"""Parity of the planar swing viewer's frames with golf_model.py (#4540).

The viewer draws precomputed frames. These tests check those frames against
``src/affine_control/golf_model.py`` independently of the generator's own
integration: finite differences of the stored velocities must equal the
model's drift acceleration plus ``M(q)^-1 u``, and the drawn points must be
the model's forward kinematics.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np
import pytest

from scripts.generate_swing_viewer_data import OUTPUT, stale
from src.affine_control.golf_model import GolfModel

ROOT = Path(__file__).resolve().parent.parent
MODEL = GolfModel()


def _data() -> dict:
    text = OUTPUT.read_text(encoding="utf-8")
    match = re.search(r"var data = (\{.*\});\n", text)
    assert match is not None
    return json.loads(match.group(1))


DATA = _data()
FRAMES = DATA["frames"]


def test_data_module_is_current() -> None:
    assert not stale(), "run python -m scripts.generate_swing_viewer_data"


def test_label_states_the_model_dimension_and_rigid_shaft() -> None:
    assert "Planar (2D)" in DATA["label"] and "shaft is rigid" in DATA["label"]
    assert "not measured" in DATA["label"]
    assert DATA["source"] == "src/affine_control/golf_model.py"


@pytest.mark.parametrize("index", range(1, len(FRAMES) - 2, 7))
def test_stored_motion_obeys_the_model_dynamics(index: int) -> None:
    before, frame, after = FRAMES[index - 1], FRAMES[index], FRAMES[index + 1]
    span = after["t"] - before["t"]
    measured = (np.array(after["qd"]) - np.array(before["qd"])) / span
    q, qd = np.array(frame["q"]), np.array(frame["qd"])
    torque = np.array(DATA["torqueNm"])
    expected = MODEL.drift_acceleration(q, qd) + np.linalg.solve(MODEL.rigid_mass_matrix(q), torque)
    np.testing.assert_allclose(measured, expected, rtol=0.02, atol=0.5)


@pytest.mark.parametrize("index", [0, len(FRAMES) // 2, len(FRAMES) - 1])
def test_points_are_the_model_forward_kinematics(index: int) -> None:
    frame = FRAMES[index]
    angles = MODEL.link_angles(np.array(frame["q"]))
    tip = sum(
        length * np.array([math.cos(a), math.sin(a)])
        for a, length in zip(angles, MODEL.lengths, strict=True)
    )
    np.testing.assert_allclose(frame["points"][-1], tip, atol=1e-5)
    assert frame["clubheadSpeed"] == pytest.approx(
        MODEL.clubhead_speed(np.array(frame["q"]), np.array(frame["qd"])), abs=1e-3
    )


def test_run_starts_at_rest_and_ends_with_the_club_pointing_down() -> None:
    assert FRAMES[0]["t"] == 0 and FRAMES[0]["qd"] == [0.0, 0.0, 0.0]
    last = MODEL.link_angles(np.array(FRAMES[-1]["q"]))[2]
    assert 1.5 * math.pi <= last < 1.5 * math.pi + 0.1
    assert all(a["t"] < b["t"] for a, b in zip(FRAMES, FRAMES[1:], strict=False))


def test_input_shares_are_fractions_and_the_wrist_is_passive() -> None:
    assert DATA["torqueNm"][2] == 0.0
    for frame in FRAMES:
        assert all(0.0 <= share <= 1.0 for share in frame["inputShare"])


def test_viewer_is_embedded_with_no_cdn_and_listed_for_deploy() -> None:
    page = (ROOT / "models" / "model-ladder.qmd").read_text(encoding="utf-8")
    assert 'id="swing-viewer"' in page
    assert '<script src="../js/swing-viewer-data.js"></script>' in page
    assert '<script src="../js/swing-viewer.js"></script>' in page
    sources = (ROOT / "js" / "swing-viewer.js").read_text(encoding="utf-8")
    for host in ("cdn.jsdelivr.net", "unpkg.com", "cdn.plot.ly", "esm.sh", "skypack"):
        assert host not in sources
    sync = (ROOT / "scripts" / "sync_frontend_assets.py").read_text(encoding="utf-8")
    assert '"swing-viewer.js"' in sync and '"swing-viewer-data.js"' in sync


def test_noscript_summary_matches_the_data() -> None:
    page = (ROOT / "models" / "model-ladder.qmd").read_text(encoding="utf-8")
    last = FRAMES[-1]
    assert f"about {round(last['clubheadSpeed'])} m/s after {last['t']:.2f} s" in page
