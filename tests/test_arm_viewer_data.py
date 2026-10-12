"""Parity of the spatial arm viewer's frames with golf_model_3d.JOHNSON_2015_ARM (#4973)."""

from __future__ import annotations

import json
import re

import numpy as np
import pytest

from scripts.generate_arm_viewer_data import OUTPUT, stale
from src.affine_control.arm_viewer_frames import (
    CAVEATS,
    JOINT_NAMES,
    build_frames,
    build_joint_table,
)
from src.affine_control.golf_model_3d import JOHNSON_2015_ARM as ARM


def _data() -> dict:
    match = re.search(r"var data = (\{.*\});\n", OUTPUT.read_text(encoding="utf-8"))
    assert match is not None
    return json.loads(match.group(1))


DATA = _data()
FRAMES = DATA["frames"]


def test_data_module_is_current() -> None:
    assert not stale(), "run python -m scripts.generate_arm_viewer_data"


def test_label_and_provenance_state_the_model_and_its_limits() -> None:
    assert "Spatial (3D)" in DATA["label"]
    assert "not a measured or simulated swing" in DATA["label"]
    assert DATA["provenance"] == ARM.provenance
    assert DATA["source"] == "src/affine_control/golf_model_3d.py"


def test_every_owner_ruled_caveat_is_in_the_payload() -> None:
    joined = " ".join(DATA["caveats"])
    for phrase in ("passive-moment breakpoints", "are assumed", "unverified", "viewer placement"):
        assert phrase in joined
    assert DATA["caveats"] == list(CAVEATS)


@pytest.mark.parametrize("index", range(0, len(FRAMES), 6))
def test_stored_points_are_the_models_forward_kinematics(index: int) -> None:
    frame = FRAMES[index]
    expected = ARM.joint_positions(np.array(frame["q"]))
    np.testing.assert_allclose(frame["points"], expected, atol=1e-5)


def test_every_frame_is_inside_the_declared_limits() -> None:
    for frame in FRAMES:
        for value, (lower, upper) in zip(frame["q"], ARM.joint_limits_rad, strict=True):
            assert lower <= value <= upper


def test_sweep_leaves_the_swing_plane() -> None:
    assert max(abs(frame["points"][-1][2]) for frame in FRAMES) > 0.01


def test_joint_table_matches_the_model() -> None:
    table = build_joint_table()
    assert [row["name"] for row in table] == list(JOINT_NAMES)
    assert [row["axis"] for row in table] == [list(a) for a in ARM.joint_axes]
    assert [row["limitsRad"] for row in table] == [list(lim) for lim in ARM.joint_limits_rad]


def test_frames_need_at_least_two() -> None:
    with pytest.raises(Exception, match="two frames"):
        build_frames(1)
