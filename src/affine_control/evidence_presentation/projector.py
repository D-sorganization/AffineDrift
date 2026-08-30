"""Pure functional projectors mapping raw governed records into typed view models."""

from __future__ import annotations

import logging
from typing import Any

from src.affine_control.evidence_presentation.vocabulary import (
    AUTHORITY_BOUNDARY_STATEMENT,
    TIER_BADGE_CLASSES,
    TIER_DISPLAY_NAMES,
    EvidencePresentationViewModel,
    EvidenceTier,
)

logger = logging.getLogger(__name__)


def _clean_str(val: Any) -> str:
    """Normalize arbitrary metadata value to a stripped string."""
    if isinstance(val, dict):
        return str(val.get("content", "") or val.get("title", "") or "")
    return str(val or "").strip()


def _derive_claim_tier(evidence_class: str) -> EvidenceTier:
    """Map evidence class string to an EvidenceTier enum."""
    if evidence_class == "analytical_counterexample":
        return EvidenceTier.MATHEMATICAL_IDENTITY
    if evidence_class == "computational":
        return EvidenceTier.QUALIFIED_SIMULATION
    if evidence_class == "experimental":
        return EvidenceTier.VALIDATED_EVIDENCE
    return EvidenceTier.PILOT_BOUNDED


def _derive_claim_establishes(claim_record: dict[str, Any], claim_id: str) -> list[str]:
    """Derive list of established facts for a claim."""
    summary = _clean_str(claim_record.get("accessible_summary"))
    tech_claim = _clean_str(claim_record.get("technical_claim"))
    establishes: list[str] = []
    if summary:
        establishes.append(summary)
    if tech_claim and tech_claim != summary:
        establishes.append(tech_claim)
    if not establishes:
        establishes.append(f"Governed mathematical or analytical property for {claim_id}")
    return establishes


def _derive_claim_falsifiers(claim_record: dict[str, Any]) -> list[str]:
    """Derive list of non-established bounds and falsification criteria for a claim."""
    does_not: list[str] = [
        "Does not establish universal human execution invariance",
        "Does not establish clinical, coaching, or equipment design prescription",
    ]
    falsifiers = claim_record.get("falsifiers", [])
    if isinstance(falsifiers, list):
        for f in falsifiers[:2]:
            f_str = _clean_str(f)
            if f_str:
                does_not.append(f"Falsified if: {f_str}")
    return does_not


def _derive_claim_limitations(claim_record: dict[str, Any]) -> list[str]:
    """Derive list of governed limitations for a claim."""
    raw_limits = claim_record.get("limitations", [])
    limitations: list[str] = []
    if isinstance(raw_limits, list):
        for limit in raw_limits:
            l_str = _clean_str(limit)
            if l_str:
                limitations.append(l_str)
    if not limitations:
        limitations.append("Restricted to governed planar and multibody simulation assumptions")
    return limitations


def _derive_claim_source_revision(claim_record: dict[str, Any]) -> str:
    """Extract or fall back to the exact source commit revision."""
    source_rev = _clean_str(claim_record.get("review_commit"))
    if not source_rev:
        prov = claim_record.get("software_provenance")
        if isinstance(prov, list) and prov and isinstance(prov[0], dict):
            source_rev = _clean_str(prov[0].get("commit"))
    return source_rev or "2eb6e9a7852c00223594806a127a3c3c78d46db1"


def project_claim(claim_record: dict[str, Any]) -> EvidencePresentationViewModel:
    """Project a raw claim registry entry into an EvidencePresentationViewModel."""
    claim_id = _clean_str(claim_record.get("claim_id"))
    title = _clean_str(claim_record.get("title")) or f"Claim {claim_id}"
    evidence_class = _clean_str(claim_record.get("evidence_class")) or "unknown"
    critique_status = _clean_str(claim_record.get("critique_status")) or "not_reviewed"

    tier = _derive_claim_tier(evidence_class)
    establishes_list = _derive_claim_establishes(claim_record, claim_id)
    does_not_establish_list = _derive_claim_falsifiers(claim_record)
    limitations_list = _derive_claim_limitations(claim_record)
    source_rev = _derive_claim_source_revision(claim_record)

    next_gate = (
        _clean_str(claim_record.get("next_validation_gate")) or "Independent empirical review"
    )

    state_label = f"{TIER_DISPLAY_NAMES[tier]} ({critique_status.replace('_', ' ').title()})"
    badge_class = TIER_BADGE_CLASSES[tier]
    accessible_label = f"Evidence state for {title}: {state_label}. Tier: {tier.value}."

    return EvidencePresentationViewModel(
        entity_id=claim_id,
        title=title,
        kind="claim",
        tier=tier.value,
        state_label=state_label,
        state_badge_class=badge_class,
        establishes=tuple(establishes_list),
        does_not_establish=tuple(does_not_establish_list),
        limitations=tuple(limitations_list),
        next_gate=next_gate,
        source_revision=source_rev,
        evidence_origin=evidence_class,
        authority_boundary=AUTHORITY_BOUNDARY_STATEMENT,
        accessible_label=accessible_label,
        source_url=f"/data/trust/claim_registry.json#{claim_id}",
    )


def _derive_protocol_tier(state: str, origin: str) -> EvidenceTier:
    """Map protocol state and evidence origin to an EvidenceTier enum."""
    if state in ("concept", "evidence-reviewed", "pilot-ready", "ethics-approved"):
        return EvidenceTier.PILOT_BOUNDED
    if state == "simulation-ready":
        if origin == "manufactured-synthetic":
            return EvidenceTier.MANUFACTURED_SYNTHETIC
        return EvidenceTier.QUALIFIED_SIMULATION
    if state in ("data-ready", "preregistered"):
        return EvidenceTier.GOVERNED_DATASET
    if state in ("collecting", "analysis-locked"):
        return EvidenceTier.COLLECTING_LOCKED
    if state == "validated":
        return EvidenceTier.VALIDATED_EVIDENCE
    if state == "published":
        return EvidenceTier.PUBLISHED_CLAIM
    if state == "superseded":
        return EvidenceTier.SUPERSEDED_REVOKED
    return EvidenceTier.PILOT_BOUNDED


def project_protocol(protocol_record: dict[str, Any]) -> EvidencePresentationViewModel:
    """Project a raw research protocol readiness entry into an EvidencePresentationViewModel."""
    protocol_id = _clean_str(protocol_record.get("protocol_id"))
    title = _clean_str(protocol_record.get("title")) or f"Protocol {protocol_id}"
    state = _clean_str(protocol_record.get("state")) or "simulation-ready"
    origin = _clean_str(protocol_record.get("evidence_origin")) or "manufactured-synthetic"
    next_gate = _clean_str(protocol_record.get("next_gate")) or "pilot-ready"
    issue_num = protocol_record.get("companion_issue")

    tier = _derive_protocol_tier(state, origin)

    establishes_list: list[str] = [
        f"Governed research protocol readiness for {title} at state {state}",
        f"Synthetic dry-run and contract verification under origin {origin}",
    ]

    does_not_establish_list: list[str] = [
        "Does not establish participant-level clinical or human biomechanical truth",
        "Does not authorize unreviewed data collection or claim promotion",
    ]

    limitations_list: list[str] = [
        f"Gated by verification stage {state} with blocking gate {next_gate}",
        "Subject to preregistered statistical power and exclusion criteria",
    ]

    record_rev = (
        _clean_str(protocol_record.get("record_revision"))
        or "2eb6e9a7852c00223594806a127a3c3c78d46db1"
    )
    state_label = f"{state.replace('-', ' ').title()} [{origin}]"
    badge_class = TIER_BADGE_CLASSES[tier]
    accessible_label = (
        f"Research protocol readiness for {title}: {state_label} (Gate: {next_gate})."
    )
    source_url = (
        f"https://github.com/D-sorganization/AffineDrift/issues/{issue_num}"
        if issue_num
        else f"/data/research_protocols/library.json#{protocol_id}"
    )

    return EvidencePresentationViewModel(
        entity_id=protocol_id,
        title=title,
        kind="protocol",
        tier=tier.value,
        state_label=state_label,
        state_badge_class=badge_class,
        establishes=tuple(establishes_list),
        does_not_establish=tuple(does_not_establish_list),
        limitations=tuple(limitations_list),
        next_gate=next_gate,
        source_revision=record_rev,
        evidence_origin=origin,
        authority_boundary=AUTHORITY_BOUNDARY_STATEMENT,
        accessible_label=accessible_label,
        source_url=source_url,
    )


def project_companion_entity(
    entity_id: str,
    title: str,
    kind: str,
    description: str,
    commit_sha: str,
    provenance_hash: str,
) -> EvidencePresentationViewModel:
    """Project a Programming Companion catalog entity into an EvidencePresentationViewModel."""
    tier = EvidenceTier.QUALIFIED_SIMULATION
    state_label = "Pinned Companion Artifact (CI-Verified)"
    badge_class = TIER_BADGE_CLASSES[tier]

    establishes_list = (
        f"Verified executable computation in UpstreamDrift pinned release {commit_sha[:10]}",
        f"Deterministic provenance with SHA-256 {provenance_hash[:16]}...",
    )

    does_not_establish_list = (
        "Does not establish universal human golf biomechanics authority",
        "Does not infer empirical performance without governed field trials",
    )

    limitations_list = (
        f"Bounded by numerical integrator tolerances and pinned UpstreamDrift commit {commit_sha}",
        "Execution requires compliant Python 3.12 environment with pinned dependencies",
    )

    next_gate = "Upstream golden regression workflow verification"
    accessible_label = f"Companion {kind} {title}: Pinned at commit {commit_sha[:10]}."

    return EvidencePresentationViewModel(
        entity_id=entity_id,
        title=title,
        kind=kind,
        tier=tier.value,
        state_label=state_label,
        state_badge_class=badge_class,
        establishes=establishes_list,
        does_not_establish=does_not_establish_list,
        limitations=limitations_list,
        next_gate=next_gate,
        source_revision=commit_sha,
        evidence_origin="computational-ci",
        authority_boundary=AUTHORITY_BOUNDARY_STATEMENT,
        accessible_label=accessible_label,
        source_url=f"/models/programming/{kind}s.html#{entity_id}",
    )
