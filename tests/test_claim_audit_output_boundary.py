"""Reviewed-route evidence must survive deployment output pruning (#4342)."""

import json
import shutil
from itertools import chain
from pathlib import Path

import pytest
import yaml

from scripts.claim_audit_evidence import split_evidence_path, validate_review_evidence
from scripts.prune_internal_docs_from_deploy import prune_internal_deploy_artifacts

ROOT = Path(__file__).resolve().parents[1]


def test_finding_evidence_is_outside_generated_output() -> None:
    """Finding evidence must survive a clean render, just like route reviews."""
    inventory = json.loads((ROOT / "data/trust/claim_audit_inventory.json").read_text())
    config = yaml.safe_load((ROOT / "_quarto.yml").read_text(encoding="utf-8"))
    output = (ROOT / config["project"]["output-dir"]).resolve()
    findings = chain.from_iterable(record["findings"] for record in inventory["routes"])
    evidence_paths = chain.from_iterable(finding.get("evidence_paths", []) for finding in findings)
    for evidence in sorted(set(evidence_paths)):
        relative, _ = split_evidence_path(evidence)
        source = (ROOT / relative).resolve()
        assert source.is_file(), evidence
        assert not source.is_relative_to(output), evidence


@pytest.mark.integration
def test_review_evidence_survives_deployment_pruning(tmp_path: Path) -> None:
    """Exercise actual pruning against isolated copies of every reviewed route."""
    inventory = json.loads((ROOT / "data/trust/claim_audit_inventory.json").read_text())
    config = yaml.safe_load((ROOT / "_quarto.yml").read_text(encoding="utf-8"))
    output = (tmp_path / config["project"]["output-dir"]).resolve()
    assert output.is_relative_to(tmp_path.resolve()) and output != tmp_path.resolve()
    records = [row for row in inventory["routes"] if row["status"] == "reviewed"]
    assert records
    for record in records:
        for evidence in record["review"]["evidence_paths"]:
            relative, _ = split_evidence_path(evidence)
            destination = tmp_path / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
        validate_review_evidence(record, tmp_path)

    output.mkdir(parents=True, exist_ok=True)
    # Markdown can no longer reach the output (issue #4597), so pruning removes nothing here.
    assert prune_internal_deploy_artifacts(output) == []
    for record in records:
        validate_review_evidence(record, tmp_path)
        for evidence in record["review"]["evidence_paths"]:
            relative, _ = split_evidence_path(evidence)
            assert not (tmp_path / relative).resolve().is_relative_to(output), evidence
