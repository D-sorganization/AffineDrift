"""RED contracts for executable fixtures and safe deterministic projections."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import cast

from scripts.generate_research_readiness_library import _partial
from src.affine_control.research_readiness import build_public_summary
from tests.research_readiness_test_support import ROOT, canonical_library

GENERATOR = "scripts/generate_research_readiness_library.py"
DRY_RUNS = ROOT / "data" / "research_protocols" / "manufactured_dry_runs.json"
READINESS_MODULES = ROOT / "src" / "affine_control" / "research_readiness"


def test_every_protocol_has_an_executable_program_specific_workflow() -> None:
    """The catalog generator itself is not an E1--E8 analysis workflow."""
    protocols = cast(list[dict[str, object]], canonical_library()["protocols"])
    failures: list[str] = []
    for record in protocols:
        specification = cast(dict[str, object], record["specification"])
        analysis = cast(dict[str, object], specification["analysis"])
        workflow_path = str(analysis["workflow_path"])
        links = cast(dict[str, object], record["links"])
        artifacts = cast(list[dict[str, object]], links["workflow_artifacts"])
        artifact_paths = {str(artifact["path"]) for artifact in artifacts}
        if (
            workflow_path == GENERATOR
            or workflow_path not in artifact_paths
            or not workflow_path.endswith(".py")
            or not (ROOT / workflow_path).is_file()
        ):
            failures.append(str(record["protocol_id"]))
    assert not failures, f"Protocols lack executable program-specific workflows: {failures}"


def test_dry_runs_are_exact_program_specific_result_manifests() -> None:
    """Dry runs must join executed workflows, estimands, inputs, results, and outcomes."""
    document = json.loads(DRY_RUNS.read_text(encoding="utf-8"))
    manifests = document.get("protocols")
    assert isinstance(manifests, list), "Dry-run output must contain protocol result manifests"
    indexed = {manifest["protocol_id"]: manifest for manifest in manifests}
    protocols = cast(list[dict[str, object]], canonical_library()["protocols"])
    assert set(indexed) == {record["protocol_id"] for record in protocols}
    for record in protocols:
        manifest = indexed[record["protocol_id"]]
        specification = cast(dict[str, object], record["specification"])
        estimands = cast(list[dict[str, object]], specification["estimands"])
        analysis = cast(dict[str, object], specification["analysis"])
        assert manifest["workflow_path"] == analysis["workflow_path"]
        assert manifest["estimand_ids"] == [item["estimand_id"] for item in estimands]
        assert set(manifest["outcome_statuses"]) == {"negative", "null", "unavailable"}
        for field in ("input_sha256", "workflow_sha256", "result_sha256"):
            assert len(manifest[field]) == 64
            int(manifest[field], 16)


def test_generated_catalog_does_not_hard_code_a_simulation_ready_cap() -> None:
    """Mixed lifecycle states cannot render beside a false global cap statement."""
    summary: dict[str, object] = {
        "protocols": [
            {
                "companion_issue": 4036,
                "evidence_origin": "manufactured-synthetic",
                "next_gate": "ethics-approved",
                "state": "pilot-ready",
                "title": "Active Impedance Identification",
            }
        ]
    }
    rendered = _partial(summary)
    assert "`pilot-ready`" in rendered
    assert "All eight entries are capped at **simulation-ready**" not in rendered


def test_public_projection_is_deterministic_across_input_order() -> None:
    """Two distinct input orders must produce identical canonical public bytes."""
    first = canonical_library()
    second = copy.deepcopy(first)
    protocols = cast(list[dict[str, object]], second["protocols"])
    protocols.reverse()
    assert first["protocols"] != second["protocols"]

    first_bytes = json.dumps(
        build_public_summary(first), ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    second_bytes = json.dumps(
        build_public_summary(second), ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    assert hashlib.sha256(first_bytes).digest() == hashlib.sha256(second_bytes).digest()
    assert first_bytes == second_bytes


def test_generated_markdown_escapes_titles_before_table_interpolation() -> None:
    """Protocol titles cannot inject cells, new rows, or raw HTML into the public table."""
    summary: dict[str, object] = {
        "protocols": [
            {
                "companion_issue": 4036,
                "evidence_origin": "modeled",
                "next_gate": "pilot-ready",
                "state": "simulation-ready",
                "title": "Unsafe | title\n<script>alert(1)</script>",
            }
        ]
    }
    rendered = _partial(summary)
    assert "Unsafe \\| title &lt;script&gt;alert(1)&lt;/script&gt;" in rendered
    assert "<script>" not in rendered


def test_research_readiness_modules_obey_the_hard_400_line_policy() -> None:
    """The scoped production modules must satisfy the AGENTS.md hard limit."""
    violations: list[str] = []
    for path in sorted(READINESS_MODULES.glob("*.py")):
        content = path.read_text(encoding="utf-8")
        line_count = content.count("\n") + (0 if content.endswith("\n") else 1)
        if line_count > 400:
            violations.append(f"{path.relative_to(ROOT).as_posix()}: {line_count} > 400")
    assert not violations, "Hard module-size violations:\n" + "\n".join(violations)
