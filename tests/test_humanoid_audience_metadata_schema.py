"""Guard the phase-zero metadata example against the existing article contract."""

import json
import re
from pathlib import Path

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/humanoid"
pytestmark = pytest.mark.integration


def test_example_reuses_article_prerequisite_contract() -> None:
    """The planning example must preserve the established prerequisite type."""
    text = (DOCS / "content-metadata-schema.md").read_text()
    example = yaml.safe_load(re.search(r"```yaml\n(.*?)```", text, re.S).group(1))
    schema = json.loads((ROOT / "schemas/article-front-matter-v1.schema.json").read_text())
    jsonschema.validate(example["prerequisites"], schema["properties"]["prerequisites"])
    assert set(example) == {"pillar", "series", "prerequisites", "engines_used", "datasets_used"}
    assert example["engines_used"]  # A parity outline cannot silently omit its engines.
    assert example["datasets_used"] == []  # No dataset clearance is implied by the example.


def test_handoff_keeps_design_and_publication_gates() -> None:
    """The deliverable routes UX work and leaves held data out of the example."""
    brief = (DOCS / "audience-brief.md").read_text()
    contract = (DOCS / "content-metadata-schema.md").read_text()
    assert "#5171" in brief
    assert all(audience in brief for audience in ("Learners", "Practitioners", "Researchers"))
    for reference in (
        "article-front-matter-v1.schema.json",
        "trust-metadata-v1.schema.json",
        "rights-licence-ledger.md",
        "AMASS",
        "ON-HOLD",
    ):
        assert reference in contract
