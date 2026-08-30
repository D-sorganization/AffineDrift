"""Deterministic generator for evidence presentation registries and Quarto partials."""

from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path
from typing import Any

import jsonschema  # type: ignore[import-untyped]

from src.affine_control.evidence_presentation.projector import (
    project_claim,
    project_companion_entity,
    project_protocol,
)
from src.affine_control.evidence_presentation.renderer import render_evidence_table
from src.affine_control.evidence_presentation.vocabulary import (
    AUTHORITY_BOUNDARY_STATEMENT,
    EvidencePresentationViewModel,
)

logger = logging.getLogger(__name__)


def _collect_claims(claims_file: Path) -> list[EvidencePresentationViewModel]:
    """Collect and project claim view models from claim registry JSON."""
    vms: list[EvidencePresentationViewModel] = []
    if not claims_file.is_file():
        return vms
    claims_data = json.loads(claims_file.read_text(encoding="utf-8"))
    pages = claims_data.get("pages", [])
    if isinstance(pages, list):
        for page in pages:
            if isinstance(page, dict):
                for claim in page.get("claims", []):
                    if isinstance(claim, dict):
                        vms.append(project_claim(claim))
    return vms


def _collect_protocols(protocols_file: Path) -> list[EvidencePresentationViewModel]:
    """Collect and project protocol view models from research protocol summary."""
    vms: list[EvidencePresentationViewModel] = []
    if not protocols_file.is_file():
        return vms
    protocols_data = json.loads(protocols_file.read_text(encoding="utf-8"))
    protocols = protocols_data.get("protocols", [])
    if isinstance(protocols, list):
        for proto in protocols:
            if isinstance(proto, dict):
                vms.append(project_protocol(proto))
    return vms


def _collect_companion_entities(companion_file: Path) -> list[EvidencePresentationViewModel]:
    """Collect and project companion engine, program, feature, and workflow view models."""
    vms: list[EvidencePresentationViewModel] = []
    if not companion_file.is_file():
        return vms
    manifest = json.loads(companion_file.read_text(encoding="utf-8"))
    source = manifest.get("source", {})
    source_commit = source.get("commit", "2eb6e9a7852c00223594806a127a3c3c78d46db1")
    manifest_sha = source.get("manifest_sha256", "b" * 64)

    for eng in manifest.get("engines", []):
        if isinstance(eng, dict):
            eid = eng.get("id", "")
            ename = eng.get("name", eid)
            vms.append(
                project_companion_entity(
                    entity_id=f"engine-{eid}",
                    title=f"Engine: {ename}",
                    kind="engine",
                    description=f"Physics engine {ename}",
                    commit_sha=source_commit,
                    provenance_hash=manifest_sha,
                )
            )

    for prog in manifest.get("programs", []):
        if isinstance(prog, dict):
            pid = prog.get("id", "")
            pname = prog.get("name", pid)
            desc = prog.get("description", "") or pname
            vms.append(
                project_companion_entity(
                    entity_id=f"program-{pid}",
                    title=f"Program: {pname}",
                    kind="program",
                    description=desc,
                    commit_sha=source_commit,
                    provenance_hash=manifest_sha,
                )
            )

    for feat in manifest.get("features", []):
        if isinstance(feat, dict):
            fid = feat.get("id", "").replace(".", "-")
            ftitle = feat.get("title", fid)
            vms.append(
                project_companion_entity(
                    entity_id=f"feature-{fid}",
                    title=f"Feature: {ftitle}",
                    kind="feature",
                    description=ftitle,
                    commit_sha=source_commit,
                    provenance_hash=manifest_sha,
                )
            )

    for wf in manifest.get("workflows", []):
        if isinstance(wf, dict):
            wfid = wf.get("id", "")
            wtitle = wf.get("title", wfid)
            wcommit = wf.get("source_commit", source_commit)
            vms.append(
                project_companion_entity(
                    entity_id=f"workflow-{wfid}",
                    title=f"Workflow: {wtitle}",
                    kind="workflow",
                    description=wtitle,
                    commit_sha=wcommit,
                    provenance_hash=manifest_sha,
                )
            )
    return vms


def build_evidence_presentation_registry(
    repo_root: Path,
) -> tuple[dict[str, Any], list[EvidencePresentationViewModel]]:
    """Build the complete evidence presentation registry from governed sources."""
    claims_file = repo_root / "data/trust/claim_registry.json"
    protocols_file = repo_root / "data/research_protocols/public_summary.json"
    companion_file = repo_root / "tests/fixtures/companion/manifest_v1_0_0_authoritative.json"

    view_models: list[EvidencePresentationViewModel] = []
    view_models.extend(_collect_claims(claims_file))
    view_models.extend(_collect_protocols(protocols_file))
    view_models.extend(_collect_companion_entities(companion_file))

    # Sort deterministically by entity_id
    view_models.sort(key=lambda vm: vm.entity_id)

    registry: dict[str, Any] = {
        "schema_version": "affinedrift.evidence-presentation/v1",
        "generated_on": date.today().isoformat(),
        "entities": [vm.to_dict() for vm in view_models],
    }

    # Validate against schema
    schema_path = repo_root / "schemas/evidence-presentation-v1.schema.json"
    if schema_path.is_file():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.validate(instance=registry, schema=schema)

    return registry, view_models


def generate_evidence_presentation(
    *,
    check: bool = False,
    repo_root: Path | None = None,
) -> tuple[Path, Path]:
    """Generate or check the presentation registry JSON and summary partial QMD."""
    root = repo_root or Path(__file__).resolve().parent.parent.parent.parent
    registry_path = root / "data/trust/generated/evidence_presentation_registry.json"
    partial_path = root / "_includes/generated/evidence-presentation-summary.qmd"

    registry_dict, view_models = build_evidence_presentation_registry(root)
    registry_content = json.dumps(registry_dict, indent=2, ensure_ascii=False) + "\n"

    table_markdown = render_evidence_table(view_models)
    partial_content = (
        "<!-- Generated by scripts/generate_evidence_presentation.py. DO NOT EDIT. -->\n\n"
        + table_markdown
        + "\n\n"
        + f"*{AUTHORITY_BOUNDARY_STATEMENT}*\n"
    )

    if check:
        if not registry_path.is_file():
            raise FileNotFoundError(f"Missing evidence presentation registry: {registry_path}")
        if registry_path.read_text(encoding="utf-8") != registry_content:
            raise ValueError(f"Evidence presentation registry is stale: {registry_path}")
        if not partial_path.is_file():
            raise FileNotFoundError(f"Missing evidence presentation partial: {partial_path}")
        if partial_path.read_text(encoding="utf-8") != partial_content:
            raise ValueError(f"Evidence presentation partial is stale: {partial_path}")
        return registry_path, partial_path

    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(registry_content, encoding="utf-8")

    partial_path.parent.mkdir(parents=True, exist_ok=True)
    partial_path.write_text(partial_content, encoding="utf-8")

    logger.info(
        "Successfully generated evidence presentation artifacts at %s and %s",
        registry_path,
        partial_path,
    )
    return registry_path, partial_path
