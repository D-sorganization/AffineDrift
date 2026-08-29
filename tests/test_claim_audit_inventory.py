"""Contracts for the rendered-route scientific claim-audit inventory."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest

from scripts.claim_audit_ids import (
    DEFERRED_AUDIT_SCOPE_COUNTS,
    deferred_issue_url,
    deferred_issue_urls,
)
from scripts.generate_claim_audit_inventory import (
    AuditContractError,
    AuditSources,
    GenerationOptions,
    ReportTargets,
    build_report,
    enforce_publication,
    generate,
    initialize_inventory,
    stable_audit_id,
    validate_inventory,
    validate_manifest_coverage,
)

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "data/trust/claim_audit_inventory.json"
SCHEMA = ROOT / "schemas/claim-audit-inventory-v1.schema.json"
CLAIMS = ROOT / "data/trust/claim_registry.json"
LEDGER = ROOT / "data/trust/claim_critique_ledger.json"
REPORT_JSON = ROOT / "data/trust/generated/claim_audit_report.json"
REPORT_MD = ROOT / "reports/scientific-claim-audit.md"
REVIEW_DIMENSIONS = ["evidence", "uncertainty", "falsifiers", "audience_framing"]


def _route(
    route: str,
    status: str,
    *,
    claim_ids: list[str] | None = None,
    critique_ids: list[str] | None = None,
) -> dict[str, object]:
    record: dict[str, object] = {
        "audit_id": stable_audit_id(route),
        "route": route,
        "status": status,
        "claim_ids": claim_ids or [],
        "critique_ids": critique_ids or [],
        "findings": [],
    }
    if status == "reviewed":
        record["review"] = {
            "reviewed_on": "2026-08-29",
            "review_commit": "a" * 40,
            "reviewer": "protected review",
            "source_path": "articles/superposition.qmd",
            "evidence_paths": [
                "articles/superposition.qmd",
                "tests/review_evidence.txt",
            ],
            "evidence_sha256": {},
            "dimensions": REVIEW_DIMENSIONS,
        }
    elif status == "deferred":
        record["deferment"] = {
            "issue_url": deferred_issue_url(route),
            "rationale": "The adversarial page review has not yet been completed.",
            "next_gate": "Complete the evidence and uncertainty review.",
        }
    else:
        record["exemption"] = {
            "issue_url": "https://github.com/D-sorganization/AffineDrift/issues/4021",
            "rationale": "This system page makes no scientific claim.",
            "scope": "Static error handling only.",
            "approved_by": "protected review",
            "approved_on": "2026-08-29",
        }
    return record


def _fixture(tmp_path: Path) -> tuple[dict[str, object], dict[str, object], Path, Path]:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/review_evidence.txt").write_text("reviewed\n", encoding="utf-8")
    (tmp_path / "articles").mkdir()
    (tmp_path / "articles/superposition.qmd").write_text(
        "# Superposition\n",
        encoding="utf-8",
    )
    claims_path = tmp_path / "claims.json"
    claims_path.write_text(
        json.dumps(
            {
                "pages": [
                    {
                        "source_path": "articles/superposition.qmd",
                        "claims": [{"claim_id": "ad-example-001", "title": "Example Claim"}],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_text(
        json.dumps(
            {
                "critiques": [
                    {
                        "critique_id": "crit-example",
                        "source_path": "critiques/example.md",
                        "affected_pages": ["articles/superposition.qmd"],
                        "severity": "high",
                        "disposition": "open",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    inventory = {
        "schema_version": "1.1.0",
        "manifest_contract": "affinedrift/public-site-manifest/v1",
        "claim_registry": "data/trust/claim_registry.json",
        "critique_ledger": "data/trust/claim_critique_ledger.json",
        "routes": [
            _route("/", "deferred"),
            _route("/404.html", "exempt"),
            _route(
                "/articles/superposition.html",
                "reviewed",
                claim_ids=["ad-example-001"],
                critique_ids=["crit-example"],
            ),
            _route("/critiques/example.html", "deferred", critique_ids=["crit-example"]),
        ],
    }
    reviewed = _find_route(inventory, "/articles/superposition.html")
    review = reviewed["review"]
    assert isinstance(review, dict)
    evidence_paths = review["evidence_paths"]
    assert isinstance(evidence_paths, list)
    review["evidence_sha256"] = {
        path: _sha256(tmp_path / path) for path in evidence_paths if isinstance(path, str)
    }
    manifest = {
        "schema_version": "affinedrift/public-site-manifest/v1",
        "page_count": 4,
        "pages": [
            {"route": "/"},
            {"route": "/404.html"},
            {"route": "/articles/superposition.html"},
            {"route": "/critiques/example.html"},
        ],
    }
    return inventory, manifest, claims_path, ledger_path


def _find_route(inventory: dict[str, object], route: str) -> dict[str, object]:
    routes = inventory["routes"]
    assert isinstance(routes, list)
    return next(
        record for record in routes if isinstance(record, dict) and record.get("route") == route
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_review_evidence_is_self_contained_and_covers_included_sources(tmp_path: Path) -> None:
    inventory, _, claims_path, ledger_path = _fixture(tmp_path)
    article = tmp_path / "articles/superposition.qmd"
    included = tmp_path / "articles/_generated/superposition-review.qmd"
    included.parent.mkdir(parents=True)
    article.write_text(
        "# Superposition\n\n{{< include _generated/superposition-review.qmd >}}\n",
        encoding="utf-8",
    )
    included.write_text("Reviewed boundary.\n", encoding="utf-8")
    reviewed = _find_route(inventory, "/articles/superposition.html")
    review = reviewed["review"]
    assert isinstance(review, dict)
    review["source_path"] = "articles/superposition.qmd"
    review["evidence_paths"] = [
        "articles/_generated/superposition-review.qmd",
        "articles/superposition.qmd",
        "tests/review_evidence.txt",
    ]
    review["evidence_sha256"] = {
        path: _sha256(tmp_path / path) for path in review["evidence_paths"]
    }
    sources = AuditSources(SCHEMA, claims_path, ledger_path, tmp_path)

    validate_inventory(inventory, sources)

    wrong_digest = copy.deepcopy(inventory)
    wrong_review = _find_route(wrong_digest, "/articles/superposition.html")["review"]
    assert isinstance(wrong_review, dict)
    wrong_hashes = wrong_review["evidence_sha256"]
    assert isinstance(wrong_hashes, dict)
    wrong_hashes["articles/superposition.qmd"] = "0" * 64
    with pytest.raises(AuditContractError, match="digest mismatch"):
        validate_inventory(wrong_digest, sources)

    missing_include = copy.deepcopy(inventory)
    missing_review = _find_route(missing_include, "/articles/superposition.html")["review"]
    assert isinstance(missing_review, dict)
    missing_paths = missing_review["evidence_paths"]
    missing_hashes = missing_review["evidence_sha256"]
    assert isinstance(missing_paths, list)
    assert isinstance(missing_hashes, dict)
    missing_paths.remove("articles/_generated/superposition-review.qmd")
    del missing_hashes["articles/_generated/superposition-review.qmd"]
    with pytest.raises(AuditContractError, match="included source"):
        validate_inventory(missing_include, sources)


def test_stable_audit_id_is_route_derived_and_order_independent() -> None:
    assert stable_audit_id("/articles/example.html") == "ad-route-3bd723407b99"
    assert stable_audit_id("/articles/example.html") == stable_audit_id("/articles/example.html")
    assert stable_audit_id("/articles/other.html") != stable_audit_id("/articles/example.html")


def test_schema_is_strict_and_status_records_are_auditable(tmp_path: Path) -> None:
    inventory, _, claims_path, ledger_path = _fixture(tmp_path)
    sources = AuditSources(SCHEMA, claims_path, ledger_path, tmp_path)
    validate_inventory(inventory, sources)

    invalid = copy.deepcopy(inventory)
    invalid["undeclared"] = True
    with pytest.raises(AuditContractError, match="Additional properties"):
        validate_inventory(invalid, sources)

    invalid = copy.deepcopy(inventory)
    reviewed = _find_route(invalid, "/articles/superposition.html")
    assert isinstance(reviewed, dict)
    review = reviewed["review"]
    assert isinstance(review, dict)
    review["dimensions"] = ["evidence", "uncertainty"]
    with pytest.raises(AuditContractError, match="too short|review dimensions"):
        validate_inventory(invalid, sources)

    invalid = copy.deepcopy(inventory)
    reviewed = _find_route(invalid, "/articles/superposition.html")
    reviewed["deferment"] = _route("/pages/unused.html", "deferred")["deferment"]
    with pytest.raises(AuditContractError, match="not valid under any|valid under each"):
        validate_inventory(invalid, sources)


def test_byte_evidence_does_not_depend_on_a_reachable_review_commit(tmp_path: Path) -> None:
    inventory, _, claims_path, ledger_path = _fixture(tmp_path)
    reviewed = _find_route(inventory, "/articles/superposition.html")
    review = reviewed["review"]
    assert isinstance(review, dict)
    review["review_commit"] = "f" * 40

    validate_inventory(inventory, AuditSources(SCHEMA, claims_path, ledger_path, tmp_path))


def test_every_rendered_route_requires_exactly_one_inventory_record(tmp_path: Path) -> None:
    inventory, manifest, _, _ = _fixture(tmp_path)
    validate_manifest_coverage(inventory, manifest)

    missing = copy.deepcopy(inventory)
    missing["routes"].pop()  # type: ignore[union-attr]
    with pytest.raises(AuditContractError, match="coverage mismatch"):
        validate_manifest_coverage(missing, manifest)

    extra = copy.deepcopy(inventory)
    extra["routes"].append(_route("/pages/not-rendered.html", "deferred"))  # type: ignore[union-attr]
    with pytest.raises(AuditContractError, match="coverage mismatch"):
        validate_manifest_coverage(extra, manifest)


def test_initial_inventory_is_deterministic_and_fail_closed(tmp_path: Path) -> None:
    _, manifest, claims_path, ledger_path = _fixture(tmp_path)
    manifest["pages"][1]["page_kind"] = "system"  # type: ignore[index]
    sources = AuditSources(SCHEMA, claims_path, ledger_path, tmp_path)

    first = initialize_inventory(manifest, sources, "2026-08-29")
    second = initialize_inventory(manifest, sources, "2026-08-29")

    assert first == second
    assert _find_route(first, "/404.html")["status"] == "exempt"
    assert _find_route(first, "/articles/superposition.html")["status"] == "deferred"
    assert _find_route(first, "/articles/superposition.html")["claim_ids"] == ["ad-example-001"]
    assert _find_route(first, "/articles/superposition.html")["critique_ids"] == ["crit-example"]
    validate_inventory(first, sources)


def test_inventory_rejects_unstable_ids_and_authority_link_drift(tmp_path: Path) -> None:
    inventory, _, claims_path, ledger_path = _fixture(tmp_path)
    sources = AuditSources(SCHEMA, claims_path, ledger_path, tmp_path)

    invalid = copy.deepcopy(inventory)
    invalid["routes"][0]["audit_id"] = "ad-route-000000000000"  # type: ignore[index]
    with pytest.raises(AuditContractError, match="stable audit ID"):
        validate_inventory(invalid, sources)

    invalid = copy.deepcopy(inventory)
    _find_route(invalid, "/articles/superposition.html")["claim_ids"] = []
    with pytest.raises(AuditContractError, match="claim authority links"):
        validate_inventory(invalid, sources)

    invalid = copy.deepcopy(inventory)
    _find_route(invalid, "/articles/superposition.html")["critique_ids"] = []
    with pytest.raises(AuditContractError, match="critique authority links"):
        validate_inventory(invalid, sources)


def test_deferred_route_rejects_parent_or_wrong_child_issue(tmp_path: Path) -> None:
    inventory, _, claims_path, ledger_path = _fixture(tmp_path)
    sources = AuditSources(SCHEMA, claims_path, ledger_path, tmp_path)
    deferred = _find_route(inventory, "/")
    deferment = deferred["deferment"]
    assert isinstance(deferment, dict)
    deferment["issue_url"] = "https://github.com/D-sorganization/AffineDrift/issues/4021"

    with pytest.raises(AuditContractError, match="exact child issue.*4063"):
        validate_inventory(inventory, sources)


def test_p0_p1_findings_fail_closed_or_block_publication(tmp_path: Path) -> None:
    inventory, _, claims_path, ledger_path = _fixture(tmp_path)
    sources = AuditSources(SCHEMA, claims_path, ledger_path, tmp_path)
    reviewed = _find_route(inventory, "/articles/superposition.html")
    assert isinstance(reviewed, dict)
    findings = reviewed["findings"]
    assert isinstance(findings, list)
    findings.append(
        {
            "finding_id": "ad-finding-example-p1",
            "priority": "p1",
            "disposition": "open",
            "issue_url": "https://github.com/D-sorganization/AffineDrift/issues/4021",
            "rationale": "An unqualified causal statement remains public.",
            "claim_ids": ["ad-example-001"],
            "critique_ids": ["crit-example"],
        }
    )

    with pytest.raises(AuditContractError, match="P0/P1 finding"):
        validate_inventory(inventory, sources)

    findings[0]["disposition"] = "publication_blocked"
    validate_inventory(inventory, sources)
    with pytest.raises(AuditContractError, match="publication blocker"):
        enforce_publication(inventory)


def test_corrected_findings_require_exact_byte_digests(tmp_path: Path) -> None:
    inventory, _, claims_path, ledger_path = _fixture(tmp_path)
    sources = AuditSources(SCHEMA, claims_path, ledger_path, tmp_path)
    reviewed = _find_route(inventory, "/articles/superposition.html")
    findings = reviewed["findings"]
    assert isinstance(findings, list)
    evidence_path = "tests/review_evidence.txt"
    findings.append(
        {
            "finding_id": "ad-finding-example-corrected",
            "priority": "p1",
            "disposition": "corrected",
            "issue_url": "https://github.com/D-sorganization/AffineDrift/issues/4021",
            "rationale": "The canonical source now states the bounded result.",
            "claim_ids": ["ad-example-001"],
            "critique_ids": ["crit-example"],
            "evidence_paths": [evidence_path],
            "evidence_sha256": {evidence_path: _sha256(tmp_path / evidence_path)},
            "verification_commit": "f" * 40,
        }
    )

    validate_inventory(inventory, sources)

    finding = findings[0]
    finding["evidence_sha256"] = {evidence_path: "0" * 64}
    with pytest.raises(AuditContractError, match="digest mismatch"):
        validate_inventory(inventory, sources)


def test_report_generation_is_deterministic_and_joins_authorities(tmp_path: Path) -> None:
    inventory, manifest, claims_path, ledger_path = _fixture(tmp_path)
    sources = AuditSources(SCHEMA, claims_path, ledger_path, tmp_path)
    validate_inventory(inventory, sources)
    validate_manifest_coverage(inventory, manifest)

    first = build_report(inventory, sources)
    second = build_report(inventory, sources)

    assert first == second
    assert first["counts"] == {"deferred": 2, "exempt": 1, "reviewed": 1}
    assert first["deferred_issue_counts"] == {
        "https://github.com/D-sorganization/AffineDrift/issues/4057": 1,
        "https://github.com/D-sorganization/AffineDrift/issues/4063": 1,
    }
    root_route = next(route for route in first["routes"] if route["route"] == "/")
    assert root_route["deferment_issue_url"].endswith("/4063")
    article = next(
        route for route in first["routes"] if route["route"] == "/articles/superposition.html"
    )
    assert article["claims"] == [{"claim_id": "ad-example-001", "title": "Example Claim"}]
    assert article["critiques"] == [
        {"critique_id": "crit-example", "disposition": "open", "severity": "high"}
    ]
    reviewed = _find_route(inventory, "/articles/superposition.html")
    review = reviewed["review"]
    assert isinstance(review, dict)
    assert article["review_evidence"] == {
        "evidence_file_count": 2,
        "evidence_sha256": review["evidence_sha256"],
        "source_path": "articles/superposition.qmd",
    }


def test_canonical_inventory_and_generated_reports_are_current() -> None:
    outputs = generate(
        INVENTORY,
        AuditSources(SCHEMA, CLAIMS, LEDGER, ROOT),
        ReportTargets(REPORT_JSON, REPORT_MD),
        GenerationOptions(check=True),
    )

    assert outputs == [REPORT_JSON, REPORT_MD]


def test_deferred_route_partition_is_exhaustive_and_exact() -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    deferred = [record for record in inventory["routes"] if record["status"] == "deferred"]
    reviewed_completed_batches = [
        record
        for record in inventory["routes"]
        if record["status"] == "reviewed"
        and (
            record["route"] == "/"
            or record["route"].startswith("/pages/")
            or record["route"].startswith("/books/")
        )
    ]
    observed: Counter[str] = Counter()

    for record in deferred:
        issue_urls = deferred_issue_urls(record["route"])
        assert len(issue_urls) == 1, f"{record['route']} maps to {issue_urls}"
        assert record["deferment"]["issue_url"] == issue_urls[0]
        observed[issue_urls[0]] += 1

    expected_deferred = Counter(DEFERRED_AUDIT_SCOPE_COUNTS)
    del expected_deferred["https://github.com/D-sorganization/AffineDrift/issues/4063"]
    del expected_deferred["https://github.com/D-sorganization/AffineDrift/issues/4062"]
    assert len(deferred) == 200
    assert len(reviewed_completed_batches) == 19
    assert observed == expected_deferred
    assert len(deferred) + len(reviewed_completed_batches) == sum(
        DEFERRED_AUDIT_SCOPE_COUNTS.values()
    )


def test_deploy_workflow_enforces_rendered_coverage_and_publication_blockers() -> None:
    workflow = (ROOT / ".github/workflows/deploy-website.yml").read_text(encoding="utf-8")

    assert "scripts.generate_claim_audit_inventory" in workflow
    assert "--manifest docs/public-site-manifest.json" in workflow
    assert "--enforce-publication" in workflow
