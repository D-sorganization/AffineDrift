"""Contract of the WEB-04.3 evidence ladder (#4517).

The six rungs live in ``config/maturity.yml``. A page may declare
``evidence-rung``; any rung above "qualified simulation" must link a measured
participant data record (``evidence-record``, a ``data/datasets.yml`` entry
flagged ``measured_participant_data: true``). The schema enum, the caveat-block
labels and the public "How to Read" ladder must all agree with the config.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from src.tools.caveats_block import EVIDENCE_LEVEL_MAP
from src.tools.utils.content_utils import collect_qmd_files, read_qmd_with_frontmatter
from src.tools.utils.evidence_ladder import (
    CANONICAL_RUNGS,
    check_evidence_rung,
    load_evidence_ladder,
    measured_record_ids,
)
from src.tools.utils.frontmatter_schema import (
    SCHEMA_PATH,
    load_frontmatter_allowlist,
    validate_article_frontmatter,
)

ROOT = Path(__file__).resolve().parent.parent
MEASURED = frozenset({"pilot-cohort"})


def test_config_defines_the_six_rungs_in_order() -> None:
    ladder = load_evidence_ladder()
    assert (
        tuple(rung.key for rung in ladder.rungs)
        == CANONICAL_RUNGS
        == (
            "mathematical-identity",
            "manufactured-fixture",
            "qualified-simulation",
            "measured-participant-result",
            "replicated-result",
            "bounded-application",
        )
    )
    for rung in ladder.rungs:
        assert rung.label and len(rung.definition) > 20, rung.key
    needs = [rung.requires_measured_data for rung in ladder.rungs]
    assert needs == [False, False, False, True, True, True]


def test_aliases_resolve_and_unknown_rungs_do_not() -> None:
    ladder = load_evidence_ladder()
    assert ladder.resolve("Qualified_Simulation") == "qualified-simulation"
    assert ladder.resolve("manufactured_synthetic") == "manufactured-fixture"
    assert ladder.resolve("published_claim") is None


@pytest.mark.parametrize("rung", CANONICAL_RUNGS[:3])
def test_model_rungs_need_no_record(rung: str) -> None:
    assert check_evidence_rung({"evidence-rung": rung}, "a.qmd", measured_ids=MEASURED) == []


@pytest.mark.parametrize("rung", [*CANONICAL_RUNGS[3:], "governed_dataset", "published_claim"])
def test_rungs_above_qualified_simulation_need_a_measured_record(rung: str) -> None:
    fm: dict[str, object] = {"evidence-rung": rung}
    assert check_evidence_rung(fm, "a.qmd", measured_ids=MEASURED)
    fm["evidence-record"] = "ztcf-fixtures"
    errors = check_evidence_rung(fm, "a.qmd", measured_ids=MEASURED)
    assert errors and "ztcf-fixtures" in errors[0]
    fm["evidence-record"] = "pilot-cohort"
    assert check_evidence_rung(fm, "a.qmd", measured_ids=MEASURED) == []


def test_pages_without_a_rung_are_not_checked() -> None:
    assert check_evidence_rung({}, "a.qmd", measured_ids=frozenset()) == []


def test_validator_applies_the_rule_even_to_allowlisted_pages() -> None:
    cfg = {"core_pages": [], "allowlist": ["articles/x.qmd"]}
    fm = {"evidence-rung": "replicated-result"}
    errors = validate_article_frontmatter(fm, "articles/x.qmd", allowlist_config=cfg)
    assert any("evidence-record" in error for error in errors)


def test_measured_records_are_flagged_datasets(tmp_path: Path) -> None:
    catalogue = tmp_path / "datasets.yml"
    catalogue.write_text(
        "third_party:\n  - id: a\n    measured_participant_data: true\naffinedrift:\n  - id: b\n",
        encoding="utf-8",
    )
    assert measured_record_ids(catalogue) == frozenset({"a"})


def test_every_core_page_declares_a_model_rung() -> None:
    ladder = load_evidence_ladder()
    for rel_path in load_frontmatter_allowlist()["core_pages"]:
        _, fm = read_qmd_with_frontmatter(ROOT / rel_path)
        assert ladder.resolve(str(fm.get("evidence-rung", ""))) in CANONICAL_RUNGS, rel_path


def test_no_page_claims_an_unsupported_rung() -> None:
    errors: list[str] = []
    for path in collect_qmd_files():
        _, fm = read_qmd_with_frontmatter(path)
        if "evidence-rung" in fm:
            errors.extend(check_evidence_rung(fm, path.as_posix()))
    assert errors == []


def test_schema_caveat_labels_and_lua_filter_cover_every_rung() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert set(CANONICAL_RUNGS) <= set(schema["properties"]["evidence-rung"]["enum"])
    assert "evidence-record" in schema["properties"]
    lua = (ROOT / "scripts" / "filters" / "caveats-block.lua").read_text(encoding="utf-8")
    for rung in CANONICAL_RUNGS:
        assert rung in EVIDENCE_LEVEL_MAP, rung
        assert f'["{rung}"]' in lua, rung


def test_how_to_read_lists_the_rungs_in_order() -> None:
    text = (ROOT / "pages" / "how-to-read.qmd").read_text(encoding="utf-8")
    start = text.index("{#evidence-ladder}")
    section = text[start : text.index("\n## ", start)]
    labels = re.findall(r"^\d\. \*\*(.+?)\*\*", section, flags=re.MULTILINE)
    assert labels == [rung.label for rung in load_evidence_ladder().rungs]
