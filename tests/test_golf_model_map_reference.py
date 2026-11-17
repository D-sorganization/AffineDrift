"""Tests for UpstreamDrift MuJoCo golf model-map extraction and generated reference."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/upstreamdrift_golf_models/manifest.json"
GENERATED_JSON = ROOT / "data/upstreamdrift_golf_models/generated/mujoco_maps.json"
GENERATED_QMD = ROOT / "models/_generated/golf-model-maps-mujoco.qmd"


def test_manifest_pins_upstream_commit_and_snapshots() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["upstream_commit"] == "625a16e6897b88ab29fb5a64c65ecee820dd58f5"
    for entry in manifest["mujoco_models"]:
        snapshot = ROOT / entry["snapshot_path"]
        assert snapshot.is_file(), entry["snapshot_path"]


def test_generated_json_matches_canonical_dof_counts() -> None:
    data = json.loads(GENERATED_JSON.read_text(encoding="utf-8"))
    canonical = next(m for m in data["models"] if m["model_id"] == "canonical")
    assert canonical["nq"] == 26
    assert canonical["nv"] == 25
    assert canonical["nu"] == 19
    assert canonical["neq"] == 1
    weld = canonical["equalities"][0]
    assert weld["kind"] == "weld"
    assert weld["attributes"]["site1"] == "right_grip_site"


def test_generated_qmd_is_checked_in() -> None:
    text = GENERATED_QMD.read_text(encoding="utf-8")
    assert "canonical" in text
    assert "pelvis_floating" in text
    assert "do not edit" in text.lower()


@pytest.mark.requires_mujoco
def test_generator_matches_committed_artifacts() -> None:
    pytest.importorskip("mujoco")
    import scripts.generate_golf_model_maps as generator

    assert generator.generate(check=True)


@pytest.mark.requires_mujoco
def test_advanced_model_reports_hip_connect_constraints() -> None:
    pytest.importorskip("mujoco")
    data = json.loads(GENERATED_JSON.read_text(encoding="utf-8"))
    advanced = next(m for m in data["models"] if m["model_id"] == "advanced")
    kinds = {row["kind"] for row in advanced["equalities"]}
    assert "connect" in kinds
    assert "weld" in kinds
    assert advanced["neq"] == 3


def test_parse_equalities_uses_defusedxml() -> None:
    from defusedxml.common import DefusedXmlException

    import src.tools.golf_model_map as golf_model_map

    assert golf_model_map.ET.__name__.startswith("defusedxml")
    payload = (
        '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe "bar">]><mujoco><equality/></mujoco>'
    )
    with pytest.raises(DefusedXmlException):
        golf_model_map._parse_equalities(payload)


def test_simscape_spec_dof_counts_and_sign_map() -> None:
    from src.tools.simscape_golf_map import DEFAULT_SIMSCAPE_SPEC, load_simscape_spec

    spec = load_simscape_spec(DEFAULT_SIMSCAPE_SPEC)
    assert spec["model_id"] == "golfer-scapula/2.0"
    assert spec["upstream_commit"] == "625a16e6897b88ab29fb5a64c65ecee820dd58f5"
    by_dof = {row["dof"]: row for row in spec["dofs"]}
    assert by_dof["pelvis.rx"]["sign"] == -1.0
    assert by_dof["left_scapula.rz"]["sign"] == -1.0
    assert by_dof["left_scapula.rx"]["axes"] == "xz"
    assert by_dof["right_scapula.ry"]["axes"] == "yz"
    assert by_dof["left_shoulder.rx"]["axes"] == "xyz"
    assert by_dof["right_shoulder.ry"]["axes"] == "yzx"
    assert by_dof["left_wrist.rx"]["validated"] is False
    assert by_dof["left_hip.rx"]["simscape_var"] == "—"


def test_simscape_generated_qmd_is_current() -> None:
    import scripts.generate_golf_model_maps as generator
    from src.tools.simscape_golf_map import DEFAULT_SIMSCAPE_QMD_OUT

    assert DEFAULT_SIMSCAPE_QMD_OUT.is_file()
    assert generator.generate_simscape(check=True)


def test_golf_model_maps_covers_slice2_sections() -> None:
    model_maps_page = (ROOT / "models/golf-model-maps.qmd").read_text(encoding="utf-8")
    simulink_page = (ROOT / "models/models-simulink.qmd").read_text(encoding="utf-8")
    mocap_page = (ROOT / "articles/technology-motion-capture.qmd").read_text(encoding="utf-8")

    for needle in (
        "golf-model-maps-simscape.qmd",
        "golfer-scapula/2.0",
        "isb_thorax",
        "SIDE_SIGN",
        "arccos",
        "G^#",
    ):
        assert needle in model_maps_page, f"missing {needle!r} in models/golf-model-maps.qmd"

    assert "golf-model-maps.html#sec-simscape-golfer-scapula" in simulink_page
    assert "arccos" in mocap_page
    assert "golf-model-maps.html#sec-pose-estimator-included-angle" in mocap_page
