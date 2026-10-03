"""Storage ancestry and optional evidence count consistency regressions."""

from pathlib import Path

import pytest

from tests.test_historical_research_handoff import acquisition, admitted, package


@pytest.mark.parametrize("unsafe_component", ["parent", "snapshot"])
def test_install_rejects_snapshot_junction_before_acquisition_or_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, unsafe_component: str
) -> None:

    consumer, pins, _ = acquisition(tmp_path)
    snapshot_parent = tmp_path / "store/historical-player-research-v1/snapshots"
    snapshot_id = f"{pins.request.source_commit}-{pins.request.manifest_sha256[:16]}"
    unsafe = snapshot_parent if unsafe_component == "parent" else snapshot_parent / snapshot_id
    original = Path.is_junction
    monkeypatch.setattr(Path, "is_junction", lambda path: path == unsafe or original(path))
    with pytest.raises(ValueError, match="junction"):
        consumer.install(pins)
    assert not (tmp_path / "store").exists()


def _image_counts() -> dict[str, int]:
    return {
        "source_frame_count": 2,
        "training_frame_count": 1,
        "training_observation_count": 1,
        "dense_observation_count": 3,
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_frame_count", 3),
        ("training_frame_count", 3),
        ("training_observation_count", 4),
    ],
)
def test_image_counts_cannot_contradict_original_clock_or_coverage(field: str, value: int) -> None:
    data = package()
    counts = _image_counts()
    counts[field] = value
    data["records"][0]["image_counts"] = counts
    with pytest.raises(ValueError, match="count"):
        admitted(data)


def test_optional_image_counts_allow_partial_training_coverage() -> None:
    data = package()
    data["records"][0]["image_counts"] = _image_counts()
    result = admitted(data)
    assert result.records[1].to_record()["image_counts"] == _image_counts()
    assert "image_counts" not in result.records[0].to_record()
