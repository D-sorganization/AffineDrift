"""Governance of the WEB-08.4 animated explainers (#4555).

The videos are generated from ``src/`` trajectories by
``scripts/generate_explainer_videos.py``. These tests keep every output current
against its sources, inside the 3 MB budget, captioned, transcribed, never
autoplaying (so ``prefers-reduced-motion`` is respected), and embedded where
their media paths resolve.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts.explainer_scenes import EXPLAINERS, Cue, Explainer
from scripts.generate_explainer_videos import (
    INCLUDE_DIR,
    MAX_VIDEO_BYTES,
    asset_path,
    render_include,
    render_vtt,
    stale_outputs,
)

ROOT = Path(__file__).resolve().parents[1]
IDS = [explainer.id for explainer in EXPLAINERS]


def test_outputs_are_current_with_their_sources() -> None:
    assert stale_outputs() == [], "run: python -m scripts.generate_explainer_videos"


def test_there_are_two_or_three_explainers_of_30_to_90_seconds() -> None:
    assert 2 <= len(EXPLAINERS) <= 3
    assert all(30.0 <= explainer.duration <= 90.0 for explainer in EXPLAINERS)


@pytest.mark.parametrize("explainer", EXPLAINERS, ids=IDS)
def test_videos_are_mp4_and_webm_under_three_megabytes(explainer: Explainer) -> None:
    mp4 = (ROOT / asset_path(explainer, "mp4")).read_bytes()
    webm = (ROOT / asset_path(explainer, "webm")).read_bytes()
    assert mp4[4:8] == b"ftyp"
    assert webm[:4] == b"\x1a\x45\xdf\xa3"
    assert len(mp4) < MAX_VIDEO_BYTES and len(webm) < MAX_VIDEO_BYTES
    assert (ROOT / asset_path(explainer, "poster")).read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


@pytest.mark.parametrize("explainer", EXPLAINERS, ids=IDS)
def test_captions_cover_the_whole_video(explainer: Explainer) -> None:
    vtt = render_vtt(explainer)
    assert vtt.startswith("WEBVTT\n")
    assert vtt.count(" --> ") == len(explainer.cues)
    assert explainer.cues[0].start == 0.0
    assert explainer.cues[-1].end == explainer.duration


def test_captions_reject_overlapping_cues() -> None:
    bad = Explainer(
        id="bad",
        title="Bad",
        duration=10.0,
        cues=(Cue(0.0, 6.0, "a"), Cue(5.0, 10.0, "b")),
        sources=(),
        paint=lambda ax, t: None,
        poster_time=1.0,
    )
    with pytest.raises(ValueError, match="cue 2"):
        render_vtt(bad)


@pytest.mark.parametrize("explainer", EXPLAINERS, ids=IDS)
def test_embed_is_captioned_transcribed_and_never_autoplays(explainer: Explainer) -> None:
    include = render_include(explainer)
    video = re.search(r"<video [^>]*>", include)
    assert video is not None
    for attribute in ("autoplay", "loop", "muted"):
        assert attribute not in video.group(0)
    assert 'preload="none"' in video.group(0) and "poster=" in video.group(0)
    assert '<track kind="captions"' in include and " default>" in include
    assert 'type="video/webm"' in include and 'type="video/mp4"' in include
    transcript = include.split("<summary>Transcript</summary>", 1)[1]
    for cue in explainer.cues:
        assert cue.text.replace('"', "&quot;").replace("'", "&#x27;") in transcript


@pytest.mark.parametrize("explainer", EXPLAINERS, ids=IDS)
def test_each_explainer_is_embedded_once_where_its_media_resolves(explainer: Explainer) -> None:
    directive = f"{{{{< include ../{INCLUDE_DIR}/{explainer.id}.qmd >}}}}"
    hosts = [
        p
        for p in sorted((ROOT / "articles").glob("*.qmd"))
        if directive in p.read_text(encoding="utf-8")
    ]
    assert len(hosts) == 1, hosts
    for src in re.findall(r'(?:src|poster)="([^"]+)"', render_include(explainer)):
        assert (hosts[0].parent / src).resolve().is_file(), src


def test_media_is_published_with_the_site() -> None:
    assert "    - static/explainers/" in (ROOT / "_quarto.yml").read_text(encoding="utf-8")
