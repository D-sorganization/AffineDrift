"""The 3D golfer viewer's motion clip is small, synthetic and honestly labelled (#5425)."""

from __future__ import annotations

import json
import re

import numpy as np
import pytest

from scripts.generate_motion_clip_data import OUTPUT, stale
from src.affine_control.motion_clip_frames import MARKERS, SEGMENTS, build_frames

MAX_BYTES = 20_000
CLUB = (MARKERS.index("hands"), MARKERS.index("clubhead"))
FORBIDDEN_KEYS = ("subject", "capture", "trial", "athlete", "c3d")


def _data() -> dict:
    match = re.search(r"var data = (\{.*\});\n", OUTPUT.read_text(encoding="utf-8"))
    assert match is not None
    return json.loads(match.group(1))


DATA = _data()


def test_data_module_is_current() -> None:
    assert not stale(), "run python -m scripts.generate_motion_clip_data"


def test_label_says_synthetic_and_not_licensed_or_traced() -> None:
    label = DATA["label"]
    assert "synthetic" in label
    assert "not licensed motion capture" in label
    assert "not a traced UpstreamDrift render" in label


def test_clip_is_small_and_carries_no_capture_metadata() -> None:
    text = OUTPUT.read_text(encoding="utf-8")
    assert len(text.encode("utf-8")) < MAX_BYTES
    names = [*DATA, *DATA["frames"][0], *DATA["markers"]]
    assert not any(key in name.lower() for name in names for key in FORBIDDEN_KEYS)


def test_skeleton_joins_every_marker_and_frames_are_ordered() -> None:
    assert DATA["markers"] == list(MARKERS)
    assert DATA["segments"] == [list(pair) for pair in SEGMENTS]
    assert {index for pair in SEGMENTS for index in pair} == set(range(len(MARKERS)))
    frames = DATA["frames"]
    assert len(frames) > 10
    assert all(len(frame["points"]) == len(MARKERS) for frame in frames)
    assert [frame["s"] for frame in frames] == sorted({frame["s"] for frame in frames})


def test_club_stays_rigid_and_the_hands_travel() -> None:
    points = np.array([frame["points"] for frame in DATA["frames"]])
    club = np.linalg.norm(points[:, CLUB[1]] - points[:, CLUB[0]], axis=1)
    np.testing.assert_allclose(club, club[0], atol=2e-3)
    assert np.ptp(points[:, CLUB[0], 1]) > 0.5


def test_frames_need_at_least_two() -> None:
    with pytest.raises(ValueError, match="two frames"):
        build_frames(1)
