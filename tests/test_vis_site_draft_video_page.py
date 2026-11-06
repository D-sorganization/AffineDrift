"""Tests for the first draft video page (VIS-SITE-4, part of #5426).

Enforces:
1. The page is a draft (``draft: true``, ``listing: false``), so nothing is
   published until Dieter approves it.
2. It embeds the ZTCF explainer through {{< vis-video >}} with media that
   resolves to files in this repository.
3. The video is traced by an ``ad_generated`` exemption pinned to the
   explainer manifest digest, and both the exemption and the page caption say
   plainly that it is an AffineDrift synthetic explainer, not a traced
   UpstreamDrift render (no false attestation; see #5423 and UpstreamDrift
   #14442).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from scripts import check_figure_projection_records as gate
from src.tools.site_page_scan import parse_front_matter

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "articles/vis-site/ztcf-explainer-draft.qmd"
VIDEO = "static/explainers/ztcf.webm"
DISCLAIMER = "not a traced UpstreamDrift render"
KWARG = re.compile(r'(\w+)="([^"]*)"')


def _embed_kwargs() -> dict[str, str]:
    shortcodes = re.findall(r"\{\{<\s*vis-video\b(.*?)>\}\}", PAGE.read_text(encoding="utf-8"))
    assert len(shortcodes) == 1, shortcodes
    return dict(KWARG.findall(shortcodes[0]))


def _video_exemption() -> dict[str, Any]:
    data = json.loads(gate.DEFAULT_EXEMPTIONS.read_text(encoding="utf-8"))
    matches = [entry for entry in data["exemptions"] if entry["pattern"] == VIDEO]
    assert len(matches) == 1, matches
    return dict(matches[0])


def _manifest_digest() -> str:
    manifest = json.loads((ROOT / "data/explainers/manifest.json").read_text(encoding="utf-8"))
    (ztcf,) = [item for item in manifest["explainers"] if item["id"] == "ztcf"]
    return str(ztcf["assets"]["webm"]["sha256"])


def test_page_is_an_unlisted_draft() -> None:
    meta = parse_front_matter(PAGE.read_text(encoding="utf-8"))
    assert meta.get("draft") is True
    assert meta.get("listing") is False


def test_page_embeds_the_ztcf_explainer_with_resolving_media() -> None:
    kwargs = _embed_kwargs()
    for key in ("src", "poster", "captions"):
        assert (PAGE.parent / kwargs[key]).resolve().is_file(), kwargs[key]
    assert gate.embedded_figures(ROOT, PAGE) == [VIDEO]
    assert (ROOT / kwargs["record"]).resolve() == gate.DEFAULT_EXEMPTIONS


def test_video_is_traced_as_a_pinned_ad_generated_explainer() -> None:
    exemption = _video_exemption()
    assert exemption["provenance"] == "ad_generated"
    assert exemption["sha256"] == _manifest_digest()
    assert "scripts/generate_explainer_videos.py" in exemption["generators"]
    assert DISCLAIMER in exemption["reason"]
    assert gate.exemption_failures(ROOT, gate.load_exemptions(gate.DEFAULT_EXEMPTIONS)) == []


def test_caption_states_the_source_honestly() -> None:
    caption = _embed_kwargs()["caption"]
    assert DISCLAIMER in caption
    assert "#5423" in caption and "UpstreamDrift #14442" in caption
