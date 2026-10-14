"""Tests for the ZTCF and DCR falsification atlases and the validation roadmap (#4528, #4526)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parents[1]
ZTCF_ATLAS = ROOT / "data/trust/ztcf_falsification_atlas.json"
DCR_ATLAS = ROOT / "data/trust/dcr_falsification_atlas.json"
PROXIMAL_DISTAL_ATLAS = ROOT / "data/trust/proximal_distal_falsification_atlas.json"
ROADMAP_PAGE = ROOT / "pages/validation-roadmap.qmd"

REQUIRED_RECORD_KEYS = {
    "atlas_id",
    "title",
    "critique_id",
    "critique_question",
    "alternative_mechanism",
    "discriminating_measurement",
}

EXPECTED_ZTCF_IDS = {
    "ztcf-atlas-passive-element-torque-leakage",
    "ztcf-atlas-bilateral-grip-nullspace",
    "ztcf-atlas-horizon-sensitivity",
}

EXPECTED_DCR_IDS = {
    "dcr-atlas-coordinate-chart-invariance",
    "dcr-atlas-reflex-feedback-confounding",
    "dcr-atlas-impact-interval-truncation",
}

EVIDENCE_RUNGS = ("Theory", "Simulation", "Bench", "Human")


def _load_json(path: Path) -> dict[str, Any]:
    assert path.is_file(), f"File does not exist: {path}"
    content = path.read_text(encoding="utf-8")
    data = json.loads(content)
    assert isinstance(data, dict), f"Root must be a dictionary in {path}"
    return data


class TestZtcfFalsificationAtlas:
    """Validate structure and records of the Zero-Torque Counterfactual Atlas."""

    def test_file_exists_and_schema_version_is_valid(self) -> None:
        data = _load_json(ZTCF_ATLAS)
        assert data.get("schema_version") == "1.0.0"
        assert data.get("atlas_domain") == "zero-torque-counterfactual"
        assert "tracking_issue" in data

    def test_records_contain_all_required_keys(self) -> None:
        data = _load_json(ZTCF_ATLAS)
        records = data.get("records")
        assert isinstance(records, list)
        assert len(records) >= 3

        record_ids: set[str] = set()
        for record in records:
            assert isinstance(record, dict)
            for key in REQUIRED_RECORD_KEYS:
                assert key in record, f"Missing key {key} in record {record.get('atlas_id')}"
                assert (
                    isinstance(record[key], str) and len(record[key].strip()) > 0
                ), f"Empty or non-string value for {key}"
            record_ids.add(record["atlas_id"])

        assert len(record_ids) == len(records), "Atlas IDs must be unique"
        assert EXPECTED_ZTCF_IDS.issubset(record_ids)

    def test_ztcf_discriminating_measurements_are_substantive(self) -> None:
        data = _load_json(ZTCF_ATLAS)
        record_map = {r["atlas_id"]: r for r in data["records"]}

        passive_rec = record_map["ztcf-atlas-passive-element-torque-leakage"]
        assert "crit-ztcf-passive-torque-definition" == passive_rec["critique_id"]
        assert "UpstreamDrift" in passive_rec["discriminating_measurement"]

        grip_rec = record_map["ztcf-atlas-bilateral-grip-nullspace"]
        assert "crit-ztcf-identifiability" == grip_rec["critique_id"]
        assert "split-grip" in grip_rec["discriminating_measurement"].lower()

        horizon_rec = record_map["ztcf-atlas-horizon-sensitivity"]
        assert "crit-ztcf-horizon-divergence" == horizon_rec["critique_id"]
        assert "50 ms" in horizon_rec["discriminating_measurement"]


class TestDcrFalsificationAtlas:
    """Validate structure and records of the Drift-Control Ratio Atlas."""

    def test_file_exists_and_schema_version_is_valid(self) -> None:
        data = _load_json(DCR_ATLAS)
        assert data.get("schema_version") == "1.0.0"
        assert data.get("atlas_domain") == "drift-control-ratio"
        assert "tracking_issue" in data

    def test_records_contain_all_required_keys(self) -> None:
        data = _load_json(DCR_ATLAS)
        records = data.get("records")
        assert isinstance(records, list)
        assert len(records) >= 3

        record_ids: set[str] = set()
        for record in records:
            assert isinstance(record, dict)
            for key in REQUIRED_RECORD_KEYS:
                assert key in record, f"Missing key {key} in record {record.get('atlas_id')}"
                assert (
                    isinstance(record[key], str) and len(record[key].strip()) > 0
                ), f"Empty or non-string value for {key}"
            record_ids.add(record["atlas_id"])

        assert len(record_ids) == len(records), "Atlas IDs must be unique"
        assert EXPECTED_DCR_IDS.issubset(record_ids)

    def test_dcr_discriminating_measurements_are_substantive(self) -> None:
        data = _load_json(DCR_ATLAS)
        record_map = {r["atlas_id"]: r for r in data["records"]}

        chart_rec = record_map["dcr-atlas-coordinate-chart-invariance"]
        assert "crit-dcr-coordinate-invariance" == chart_rec["critique_id"]
        assert (
            "kinetic-energy" in chart_rec["discriminating_measurement"].lower()
            or "riemannian" in chart_rec["discriminating_measurement"].lower()
        )

        reflex_rec = record_map["dcr-atlas-reflex-feedback-confounding"]
        assert "crit-neuromuscular-control" == reflex_rec["critique_id"]
        assert "musculoskeletal" in reflex_rec["discriminating_measurement"].lower()

        impact_rec = record_map["dcr-atlas-impact-interval-truncation"]
        assert "crit-impact-evasion" == impact_rec["critique_id"]
        assert "audit_impact_interval" in impact_rec["discriminating_measurement"]


class TestValidationRoadmapPage:
    """Validate presence, frontmatter, and references in pages/validation-roadmap.qmd."""

    def test_page_exists(self) -> None:
        assert ROADMAP_PAGE.is_file(), f"Missing roadmap page at {ROADMAP_PAGE}"

    def test_frontmatter_and_title(self) -> None:
        content = ROADMAP_PAGE.read_text(encoding="utf-8")
        assert content.startswith("---")
        assert 'title: "Model-to-Human Validation Roadmap"' in content
        assert "description:" in content
        assert "summary-plain:" in content

    def test_references_all_four_evidence_rungs(self) -> None:
        content = ROADMAP_PAGE.read_text(encoding="utf-8")
        for rung in EVIDENCE_RUNGS:
            assert rung in content, f"Missing evidence rung '{rung}' in validation roadmap"

    def test_references_all_three_falsification_atlases(self) -> None:
        content = ROADMAP_PAGE.read_text(encoding="utf-8")
        assert (
            "Proximal-Distal" in content or "proximal_distal" in content
        ), "Roadmap must reference Proximal-Distal Falsification Atlas"
        assert (
            "Zero-Torque Counterfactual" in content or "ztcf" in content.lower()
        ), "Roadmap must reference Zero-Torque Counterfactual Atlas"
        assert (
            "Drift-Control Ratio" in content or "dcr" in content.lower()
        ), "Roadmap must reference Drift-Control Ratio Atlas"

    def test_references_instrumentation_and_falsification_thresholds(self) -> None:
        content = ROADMAP_PAGE.read_text(encoding="utf-8")
        assert "Falsification Threshold" in content
        assert "Split-Grip" in content or "split-grip" in content
        assert "EMG" in content
        assert "Optical Motion Capture" in content or "optical" in content.lower()
