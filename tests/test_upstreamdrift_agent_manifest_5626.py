"""Agent entry points must advertise UpstreamDrift install and headless guides (#5626)."""

from __future__ import annotations

from pathlib import Path

from src.tools.agent_entry_point import LLMS_PATH, load_manifest

ROOT = Path(__file__).resolve().parents[1]


def test_canonical_manifest_includes_upstreamdrift_guides() -> None:
    manifest = load_manifest((ROOT / "data/agent/canonical_pages.json").read_text(encoding="utf-8"))
    paths = {page.path for section in manifest.sections for page in section.pages}
    assert "/pages/upstreamdrift-getting-started.html" in paths
    assert "/pages/upstreamdrift-headless-and-agents.html" in paths


def test_llms_txt_links_upstreamdrift_guides() -> None:
    text = LLMS_PATH.read_text(encoding="utf-8")
    assert "/pages/upstreamdrift-getting-started.html" in text
    assert "/pages/upstreamdrift-headless-and-agents.html" in text
    assert "ud-sim" in text or "Headless" in text
