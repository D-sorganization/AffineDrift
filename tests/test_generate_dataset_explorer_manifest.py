"""Manifest generation for the Fixture and Dataset Explorer (#4541)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.generate_dataset_explorer_manifest import (
    MANIFEST_TARGET,
    build_manifest,
    render,
)

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_lists_every_fixture_file_per_family() -> None:
    manifest = build_manifest()
    families = {family["family_id"]: family for family in manifest["families"]}

    assert set(families) == {
        "ztcf",
        "population_generalization",
        "proximal_distal_energy_transfer",
    }

    ztcf_paths = {fixture["path"] for fixture in families["ztcf"]["fixtures"]}
    on_disk = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "data" / "ztcf").glob("*.json")
        if not path.name.endswith(".schema.json")
    }
    assert ztcf_paths == on_disk
    assert ztcf_paths, "expected at least one ztcf fixture on disk"


def test_manifest_reports_a_schema_only_when_one_is_published() -> None:
    manifest = build_manifest()
    families = {family["family_id"]: family for family in manifest["families"]}

    assert families["ztcf"]["schema_path"] == "data/ztcf/ztcf_intervention_v1.schema.json"
    # Neither family has a published *.schema.json today; the explorer must not
    # fabricate a schema reference for them.
    assert families["population_generalization"]["schema_path"] is None
    assert families["proximal_distal_energy_transfer"]["schema_path"] is None


def test_manifest_records_the_declared_schema_version_per_fixture() -> None:
    manifest = build_manifest()
    families = {family["family_id"]: family for family in manifest["families"]}
    ztcf_fixtures = {
        fixture["path"]: fixture["schema_version"] for fixture in families["ztcf"]["fixtures"]
    }
    assert (
        ztcf_fixtures["data/ztcf/planar_golf_forward_fixture_v1.json"]
        == "affinedrift.ztcf-intervention/v1"
    )


def test_committed_manifest_matches_the_generator(tmp_path: Path) -> None:
    """Guards against the checked-in manifest drifting from the fixtures on disk."""
    assert MANIFEST_TARGET.exists(), "run scripts/generate_dataset_explorer_manifest.py"
    committed = json.loads(MANIFEST_TARGET.read_text(encoding="utf-8"))
    assert committed == build_manifest()


def test_check_mode_fails_when_manifest_is_stale(tmp_path: Path, monkeypatch) -> None:
    import scripts.generate_dataset_explorer_manifest as module

    stale_target = tmp_path / "dataset_explorer_manifest.json"
    stale_target.write_text(json.dumps({"schema_version": "stale"}) + "\n", encoding="utf-8")
    monkeypatch.setattr(module, "MANIFEST_TARGET", stale_target)

    assert render(check_only=True) == 1


def test_check_mode_passes_when_manifest_is_current(monkeypatch) -> None:
    assert render(check_only=True) == 0


@pytest.mark.parametrize(
    "family_id,expected_min_count",
    [
        ("ztcf", 2),
        ("population_generalization", 1),
        ("proximal_distal_energy_transfer", 3),
    ],
)
def test_family_fixture_counts_are_at_least(family_id: str, expected_min_count: int) -> None:
    manifest = build_manifest()
    families = {family["family_id"]: family for family in manifest["families"]}
    assert len(families[family_id]["fixtures"]) >= expected_min_count
