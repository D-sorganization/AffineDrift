"""Contracts for generated scientific-trust panels and summary strength."""

from __future__ import annotations

import copy
import html
import json
import re
from pathlib import Path

import pytest

from scripts.generate_trust_panels import (
    TrustContractError,
    generate,
    load_registry,
    render_page_panel,
    validate_accessible_text,
    validate_non_amplification,
    validate_registry,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/trust/claim_registry.json"
SCHEMA = ROOT / "schemas/trust-metadata-v1.schema.json"
OUTPUT = ROOT / "articles/_generated/trust"
TRUST_STYLES = ROOT / "css/components/scientific-trust-panel.css"


def _canonical() -> dict[str, object]:
    return load_registry(REGISTRY, SCHEMA)


def _first_claim(registry: dict[str, object]) -> dict[str, object]:
    pages = registry["pages"]
    assert isinstance(pages, list)
    page = pages[0]
    assert isinstance(page, dict)
    claims = page["claims"]
    assert isinstance(claims, list)
    claim = claims[0]
    assert isinstance(claim, dict)
    return claim


def test_registry_uses_a_strict_versioned_schema() -> None:
    registry = _canonical()
    assert registry["schema_version"] == "1.0.0"

    invalid = copy.deepcopy(registry)
    invalid["undeclared_field"] = "must fail closed"
    with pytest.raises(TrustContractError, match="Additional properties"):
        validate_registry(invalid, SCHEMA)


@pytest.mark.parametrize(
    ("summary_text", "strength", "message"),
    (
        ("This ratio always proves that correction is locked-in.", "bounded", "term"),
        ("This ratio can prove that the golfer is locked-in.", "bounded", "term"),
        ("The modeled contribution is 85%.", "bounded", "percentage"),
        ("A universal golfer result.", "established", "strength"),
    ),
)
def test_accessible_summary_cannot_amplify_the_technical_claim(
    summary_text: str,
    strength: str,
    message: str,
) -> None:
    claim = copy.deepcopy(_first_claim(_canonical()))
    summary = claim["accessible_summary"]
    assert isinstance(summary, dict)
    summary["text"] = summary_text
    summary["modal_strength"] = strength

    with pytest.raises(TrustContractError, match=message):
        validate_non_amplification(claim)


@pytest.mark.parametrize(
    "summary_text",
    (
        "DCR does not prove that a golfer is locked-in.",
        "DCR doesn't prove that a golfer is locked-in.",
    ),
)
def test_negated_boundary_terms_remain_allowed_in_accessible_text(summary_text: str) -> None:
    claim = copy.deepcopy(_first_claim(_canonical()))
    summary = claim["accessible_summary"]
    assert isinstance(summary, dict)
    summary["text"] = summary_text

    validate_non_amplification(claim)


def test_unknown_evidence_is_visible_and_unqualified() -> None:
    registry = copy.deepcopy(_canonical())
    pages = registry["pages"]
    assert isinstance(pages, list)
    page = pages[0]
    assert isinstance(page, dict)
    claim = _first_claim(registry)
    claim["evidence_class"] = "unknown"
    claim["critique_status"] = "unknown"
    uncertainty = claim["uncertainty"]
    assert isinstance(uncertainty, dict)
    uncertainty["status"] = "unknown"

    panel = render_page_panel(page, registry_sha256="0" * 64)

    assert "Unqualified" in panel
    assert panel.count("Unknown") >= 3


def test_generated_panels_are_current_and_deterministic() -> None:
    first = generate(REGISTRY, SCHEMA, OUTPUT, check=True)
    second = generate(REGISTRY, SCHEMA, OUTPUT, check=True)

    assert first == second
    assert first


def test_every_governed_page_includes_its_generated_panel_and_claim_links() -> None:
    registry = _canonical()
    pages = registry["pages"]
    assert isinstance(pages, list)

    for page in pages:
        assert isinstance(page, dict)
        page_id = page["page_id"]
        source_path = ROOT / str(page["source_path"])
        source = source_path.read_text(encoding="utf-8")
        include = f"{{{{< include _generated/trust/{page_id}.qmd >}}}}"
        assert include in source

        claims = page["claims"]
        assert isinstance(claims, list)
        for claim in claims:
            assert isinstance(claim, dict)
            claim_id = str(claim["claim_id"])
            anchor = str(claim["technical_anchor"])
            assert f'data-trust-claim="{claim_id}"' in source
            assert f'href="#{anchor}"' in source


def test_generated_panel_exposes_all_required_trust_fields() -> None:
    panel = (OUTPUT / "ad-dcr-reachability.qmd").read_text(encoding="utf-8")
    required_labels = (
        "Evidence class",
        "Uncertainty",
        "Limitations",
        "Falsifier",
        "Critique status",
        "Software provenance",
        "Data provenance",
        "Next validation gate",
    )
    for label in required_labels:
        assert label in panel

    assert re.search(r"Reviewed:.*[0-9a-f]{40}", panel)
    assert "DO NOT EDIT" in panel
    assert "Plain-language summary" in panel


def test_authored_lay_summary_cannot_amplify_the_governed_claim() -> None:
    registry = _canonical()
    claim = _first_claim(registry)
    technical = claim["technical_claim"]
    assert isinstance(technical, dict)
    page = ROOT / "articles/controllability-drift-ratio.qmd"
    source = page.read_text(encoding="utf-8")
    section = re.search(
        r'<section class="laymans-terms">(?P<body>.*?)</section>',
        source,
        flags=re.DOTALL,
    )
    assert section is not None
    lay_text = html.unescape(re.sub(r"<[^>]+>", " ", section.group("body")))

    validate_accessible_text(
        technical_text=str(technical["text"]),
        accessible_text=lay_text,
        technical_strength=str(technical["modal_strength"]),
        accessible_strength="bounded",
    )


def test_registry_json_is_canonical_utf8() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    canonical = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    assert REGISTRY.read_text(encoding="utf-8") == canonical


def test_trust_panel_styles_preserve_responsive_and_print_contracts() -> None:
    styles = TRUST_STYLES.read_text(encoding="utf-8")

    assert ".scientific-trust-panel" in styles
    assert "overflow-wrap: anywhere" in styles
    assert "@media print" in styles
    assert "break-inside: avoid" in styles
    assert "background: transparent" in styles
    assert "!important" not in styles
