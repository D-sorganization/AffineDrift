"""Contract tests for VIS-SITE-4: first draft page with embedded UD render (#5426).

Enforces:
1. The draft page exists at ``pages/ud-render-draft.qmd`` with ``draft: true``
   and ``listing: false`` so it is never published or indexed without approval.
2. The page includes an explicit warning callout stating that publication
   needs Dieter's approval and the Assessment Board gate.
3. The page embeds the accessible video/render component ({{< vis-video >}})
   with media resolving to repository files, pointing to the proximal-distal
   UD figure map record.
4. The embed caption contains the exact UpstreamDrift provenance (commit,
   run id, and model) from the #5423 placement audit top pick.
5. The traced UD figure (fig_ztcf_drift_control.svg) is referenced and verified
   by the projection record.
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts import check_figure_projection_records as gate
from src.tools.site_page_scan import parse_front_matter

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "pages" / "ud-render-draft.qmd"
UD_COMMIT_SHORT = "b753c279"
UD_RUN_SHORT = "44c11639c1f3"
UD_MODEL = "release-preset/make_figures"
FIGURE_MAP_RECORD = "evidence/projections/ud_figure_maps/proximal_distal_energy_transfer.json"
KWARG = re.compile(r'(\w+)="([^"]*)"')


def _embed_kwargs() -> dict[str, str]:
    assert PAGE.is_file(), f"{PAGE} does not exist"
    shortcodes = re.findall(r"\{\{<\s*vis-video\b(.*?)>\}\}", PAGE.read_text(encoding="utf-8"))
    assert len(shortcodes) == 1, f"expected exactly 1 vis-video embed, got {len(shortcodes)}"
    return dict(KWARG.findall(shortcodes[0]))


def test_page_is_an_unlisted_draft() -> None:
    assert PAGE.is_file(), f"draft page {PAGE} not found"
    meta = parse_front_matter(PAGE.read_text(encoding="utf-8"))
    assert meta.get("draft") is True, "frontmatter must declare draft: true"
    assert meta.get("listing") is False, "frontmatter must declare listing: false"


def test_page_has_approval_and_assessment_board_banner() -> None:
    text = PAGE.read_text(encoding="utf-8")
    assert "Dieter's approval" in text, "draft page must state Dieter's approval is required"
    assert (
        "Assessment Board gate" in text
    ), "draft page must state Assessment Board gate is required"


def test_page_embeds_vis_video_with_resolving_media() -> None:
    kwargs = _embed_kwargs()
    for key in ("src", "poster", "captions"):
        assert key in kwargs, f"vis-video missing required attribute: {key}"
        media_path = (PAGE.parent / kwargs[key]).resolve()
        assert media_path.is_file(), f"vis-video {key} '{kwargs[key]}' does not resolve to a file"


def test_provenance_caption_and_projection_record() -> None:
    kwargs = _embed_kwargs()
    assert (
        kwargs.get("record") == FIGURE_MAP_RECORD
    ), f"record must be {FIGURE_MAP_RECORD}, got {kwargs.get('record')}"
    assert (ROOT / kwargs["record"]).is_file(), f"record file {kwargs['record']} must exist"

    caption = kwargs.get("caption", "")
    assert UD_COMMIT_SHORT in caption, f"caption must cite UD commit {UD_COMMIT_SHORT}"
    assert UD_RUN_SHORT in caption, f"caption must cite UD run {UD_RUN_SHORT}"
    assert UD_MODEL in caption, f"caption must cite UD model {UD_MODEL}"
    assert "#5423" in caption, "caption must reference the #5423 audit"


def test_embedded_figures_pass_projection_gate() -> None:
    text = PAGE.read_text(encoding="utf-8")
    assert "fig_ztcf_drift_control.svg" in text, "page should reference the traced top pick figure"
    figs = gate.embedded_figures(ROOT, PAGE)
    assert any(
        "fig_ztcf_drift_control.svg" in f for f in figs
    ), f"fig_ztcf_drift_control.svg must be embedded; got {figs}"
