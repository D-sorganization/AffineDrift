"""Tests for the accessible video embed shortcode (VIS-SITE-2, #5424).

Enforces:
1. {{< vis-video >}} renders a local WebM or MP4 with a poster, an English
   captions track, a text alternative and a provenance-record reference.
2. It lazy-loads (``preload="none"``) and never autoplays or loops, so a
   reduced-motion reader sees only the poster until they press play.
3. Remote or escaping sources, missing captions, posters or records fail the
   render instead of publishing (no third-party trackers can be embedded).
4. The published-figure gate treats an embedded video like a figure: it must
   be traced by a projection record or exempted.

The shortcode runs through Pandoc with a thin wrapper filter, like the
provenance caption test, so the check runs without Quarto.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from scripts import check_figure_projection_records as gate

ROOT = Path(__file__).resolve().parents[1]
EXTENSION = ROOT / "_extensions/vis-video"
VIDEO_LUA = EXTENSION / "vis-video.lua"
RECORD = "evidence/projections/ud_figure_maps/demo.json"

# Calls the shortcode for every paragraph that starts with VISVIDEO, passing
# key="value" pairs as kwargs (Quarto passes the same shape).
WRAPPER_LUA = """
local shortcode = dofile(os.getenv("VIS_VIDEO_LUA"))["vis-video"]
function Pandoc(doc)
  local blocks = {}
  for _, block in ipairs(doc.blocks) do
    local text = pandoc.utils.stringify(block)
    if block.t == "Para" and text:match("^VISVIDEO") then
      local kwargs = {}
      for key, value in text:gmatch('([%w_]+)="([^"]*)"') do
        kwargs[key] = value
      end
      table.insert(blocks, shortcode({}, kwargs, doc.meta))
    else
      table.insert(blocks, block)
    end
  end
  return pandoc.Pandoc(blocks, doc.meta)
end
"""


def _pandoc() -> list[str]:
    if shutil.which("pandoc"):
        return ["pandoc"]
    if shutil.which("quarto"):
        return ["quarto", "pandoc"]
    pytest.skip("Pandoc (or Quarto) is required for the vis-video shortcode check")


def _render(tmp_path: Path, body: str) -> subprocess.CompletedProcess[str]:
    wrapper = tmp_path / "wrapper.lua"
    wrapper.write_text(WRAPPER_LUA, encoding="utf-8")
    source = f"---\ntitle: Video test\ndraft: true\n---\n\n{body}\n"
    return subprocess.run(  # noqa: S603 -- reason: fixed argv, no shell
        [*_pandoc(), "--from", "markdown-smart", "--to", "html", "--lua-filter", str(wrapper)],
        input=source,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
        env={**os.environ, "VIS_VIDEO_LUA": str(VIDEO_LUA)},
    )


def _kwargs(**overrides: str) -> str:
    values = {
        "src": "media/swing.webm",
        "poster": "media/swing.poster.png",
        "captions": "media/swing.en.vtt",
        "alt": "A golfer swings a driver, seen face-on",
        "record": RECORD,
    }
    values.update(overrides)
    pairs = " ".join(f'{key}="{value}"' for key, value in values.items() if value)
    return f"VISVIDEO {pairs}"


def test_extension_registers_shortcode() -> None:
    manifest = (EXTENSION / "_extension.yml").read_text(encoding="utf-8")
    assert "shortcodes:" in manifest
    assert "vis-video.lua" in manifest


def test_embed_renders_an_accessible_lazy_video(tmp_path: Path) -> None:
    result = _render(tmp_path, _kwargs())
    assert result.returncode == 0, result.stderr
    html = result.stdout
    assert 'preload="none"' in html
    assert 'poster="media/swing.poster.png"' in html
    assert '<source src="media/swing.webm" type="video/webm">' in html
    assert '<track kind="captions" src="media/swing.en.vtt" srclang="en"' in html
    assert 'aria-label="A golfer swings a driver, seen face-on"' in html
    assert f'data-provenance-record="{RECORD}"' in html
    assert "autoplay" not in html and "loop" not in html


def test_mp4_source_gets_its_own_type(tmp_path: Path) -> None:
    result = _render(tmp_path, _kwargs(src="media/swing.mp4"))
    assert result.returncode == 0, result.stderr
    assert '<source src="media/swing.mp4" type="video/mp4">' in result.stdout


def test_leading_parent_segments_reach_site_media(tmp_path: Path) -> None:
    # Pages under articles/ reach the shared static/ media this way (#5426).
    result = _render(tmp_path, _kwargs(src="../../static/explainers/ztcf.webm"))
    assert result.returncode == 0, result.stderr
    assert '<source src="../../static/explainers/ztcf.webm"' in result.stdout


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"src": "https://tracker.example/clip.mp4"}, "src"),
        ({"src": "media/../../clip.webm"}, "src"),
        ({"src": "../media/../clip.webm"}, "src"),
        ({"src": "../"}, "src"),
        ({"src": "media/swing.mov"}, "src"),
        ({"captions": ""}, "captions"),
        ({"captions": "media/swing.srt"}, "captions"),
        ({"poster": ""}, "poster"),
        ({"alt": ""}, "alt"),
        ({"record": ""}, "record"),
        ({"record": "docs/record.json"}, "record"),
        ({"autoplay": "true"}, "autoplay"),
    ],
)
def test_unsafe_or_incomplete_embed_fails_the_render(
    tmp_path: Path, overrides: dict[str, str], message: str
) -> None:
    result = _render(tmp_path, _kwargs(**overrides))
    assert result.returncode != 0
    assert message in result.stderr


def test_figure_gate_requires_a_record_for_an_embedded_video(tmp_path: Path) -> None:
    (tmp_path / "_quarto.yml").write_text(
        'project:\n  render:\n    - "articles/**/*.qmd"\n', encoding="utf-8"
    )
    page = tmp_path / "articles/page.qmd"
    page.parent.mkdir(parents=True)
    page.write_text(f"---\ntitle: P\n---\n\n{{{{< vis-video {_kwargs()[9:]} >}}}}\n")
    assert gate.embedded_figures(tmp_path, page) == ["articles/media/swing.webm"]
