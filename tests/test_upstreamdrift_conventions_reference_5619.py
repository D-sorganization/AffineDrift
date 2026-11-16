"""Publication and agent-entry contracts for UpstreamDrift conventions (#5619)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.tools.agent_entry_point import MANIFEST_PATH, load_manifest, render_both

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "pages/upstreamdrift-conventions.qmd"
PINNED_COMMIT = "c8814a1b9d120ce382ee1de9a6583bb5ef569a15"


@pytest.fixture(scope="module")
def page_text() -> str:
    assert PAGE.is_file(), f"missing reference page: {PAGE}"
    return PAGE.read_text(encoding="utf-8")


def test_page_pins_upstreamdrift_commit(page_text: str) -> None:
    assert PINNED_COMMIT in page_text


def test_page_covers_issue_sections(page_text: str) -> None:
    section_ids = (
        "units-gravity",
        "canonical-state",
        "per-engine-table",
        "spatial-vectors",
        "world-frames",
        "impact-parameters",
        "ball-flight",
        "wrenches",
        "analytics-signs",
        "site-vs-code",
    )
    for anchor in section_ids:
        assert f"{{#{anchor}}}" in page_text, f"missing section anchor #{anchor}"


def test_agent_canonical_pages_lists_conventions_reference() -> None:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    notation = next(
        s for s in payload["sections"] if s["name"] == "Notation, Conventions, and Parameters"
    )
    sources = {p["source"] for p in notation["pages"]}
    assert "pages/upstreamdrift-conventions.qmd" in sources


def test_llms_txt_links_conventions_reference() -> None:
    manifest = load_manifest(MANIFEST_PATH.read_text(encoding="utf-8"))
    llms, _ = render_both(manifest)
    assert "/pages/upstreamdrift-conventions.html" in llms


def test_llms_full_cites_conventions_source() -> None:
    manifest = load_manifest(MANIFEST_PATH.read_text(encoding="utf-8"))
    _, full = render_both(manifest)
    assert "`pages/upstreamdrift-conventions.qmd`" in full
