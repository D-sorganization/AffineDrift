"""Tests for the figure provenance caption shortcode (VIS-EVIDENCE-2, #5420).

Enforces:
1. {{< provenance >}} renders model, run_id, UpstreamDrift commit and claim class.
2. The commit (and optional model source path) link only to the public
   UpstreamDrift repository; no other URL can be injected.
3. Values come from kwargs or from a ``provenance:`` front-matter map shaped
   like the #5419 run-identity record.
4. Malformed or host-like values fail the render instead of publishing.

The shortcode is exercised through Pandoc with a thin wrapper filter so the
check runs without Quarto; a Quarto integration check runs when Quarto exists.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXTENSION = ROOT / "_extensions/provenance"
PROVENANCE_LUA = EXTENSION / "provenance.lua"
RUN_IDENTITY = ROOT / "tests/fixtures/markerless_mocap/run_identity.json"
UD_REPO = "https://github.com/D-sorganization/UpstreamDrift"

COMMIT = "0123456789abcdef0123456789abcdef01234567"
RUN_ID = "4" * 64

# Calls the shortcode for every paragraph that starts with PROVENANCE, passing
# the key=value pairs that follow it as kwargs (Quarto passes the same shape).
WRAPPER_LUA = """
local shortcode = dofile(os.getenv("PROVENANCE_LUA")).provenance
function Pandoc(doc)
  local blocks = {}
  for _, block in ipairs(doc.blocks) do
    local text = pandoc.utils.stringify(block)
    if block.t == "Para" and text:match("^PROVENANCE") then
      local kwargs = {}
      for key, value in text:gmatch("([%w_]+)=(%S+)") do
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
    pytest.skip("Pandoc (or Quarto) is required for the provenance shortcode check")


def _render(tmp_path: Path, body: str, frontmatter: str = "") -> subprocess.CompletedProcess[str]:
    wrapper = tmp_path / "wrapper.lua"
    wrapper.write_text(WRAPPER_LUA, encoding="utf-8")
    source = f"---\ntitle: Provenance test\n{frontmatter}---\n\n{body}\n"
    return subprocess.run(  # noqa: S603 -- reason: fixed argv, no shell
        [*_pandoc(), "--from", "markdown", "--to", "html", "--lua-filter", str(wrapper)],
        input=source,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
        env={**os.environ, "PROVENANCE_LUA": str(PROVENANCE_LUA)},
    )


def _kwargs(**overrides: str) -> str:
    values = {
        "model_id": "synthetic-driver-skeleton",
        "run_id": RUN_ID,
        "ud_commit": COMMIT,
        "claim_class": "derived",
    }
    values.update(overrides)
    return "PROVENANCE " + " ".join(f"{key}={value}" for key, value in values.items())


def test_extension_registers_shortcode() -> None:
    manifest = (EXTENSION / "_extension.yml").read_text(encoding="utf-8")
    assert "shortcodes:" in manifest
    assert "provenance.lua" in manifest


def test_caption_shows_model_run_commit_and_claim_class(tmp_path: Path) -> None:
    result = _render(tmp_path, _kwargs())
    assert result.returncode == 0, result.stderr
    html = result.stdout
    assert 'class="provenance-note figure-provenance"' in html
    assert 'data-claim-class="derived"' in html
    assert "synthetic-driver-skeleton" in html
    assert RUN_ID in html
    assert f'href="{UD_REPO}/commit/{COMMIT}"' in html
    assert COMMIT[:7] in html
    assert "Derived" in html


def test_model_path_links_to_source_at_commit(tmp_path: Path) -> None:
    body = _kwargs(model_path="src/models/driver_skeleton.osim", claim_class="model_scenario")
    result = _render(tmp_path, body)
    assert result.returncode == 0, result.stderr
    assert f'href="{UD_REPO}/blob/{COMMIT}/src/models/driver_skeleton.osim"' in result.stdout
    assert "Model scenario" in result.stdout


def test_front_matter_run_identity_record(tmp_path: Path) -> None:
    """A #5419 run-identity record in front matter is enough on its own."""
    record = json.loads(RUN_IDENTITY.read_text(encoding="utf-8"))
    frontmatter = "provenance:\n" + "".join(
        f'  {key}: "{value}"\n' for key, value in record.items()
    )
    result = _render(tmp_path, "PROVENANCE", frontmatter)
    assert result.returncode == 0, result.stderr
    html = result.stdout
    assert record["model_id"] in html
    assert record["run_id"] in html
    assert f'{UD_REPO}/commit/{record["ud_commit"]}' in html
    assert f'data-claim-class="{record["claim_class"]}"' in html


def test_kwargs_override_front_matter(tmp_path: Path) -> None:
    frontmatter = 'provenance:\n  claim_class: "observed"\n'
    result = _render(tmp_path, _kwargs(claim_class="derived"), frontmatter)
    assert result.returncode == 0, result.stderr
    assert 'data-claim-class="derived"' in result.stdout


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("claim_class", "speculative"),
        ("ud_commit", "main"),
        ("run_id", "run;drop"),
        ("model_id", "http://10.0.0.5/model"),
        ("model_id", "user@buildhost"),
        ("model_path", "../../etc/passwd"),
        ("model_path", "/home/someone/model.osim"),
    ],
)
def test_malformed_values_fail_the_render(tmp_path: Path, field: str, value: str) -> None:
    result = _render(tmp_path, _kwargs(**{field: value}))
    assert result.returncode != 0
    assert "provenance" in result.stderr
    assert field in result.stderr


def test_missing_required_field_fails(tmp_path: Path) -> None:
    body = f"PROVENANCE model_id=m run_id={RUN_ID} claim_class=derived"
    result = _render(tmp_path, body)
    assert result.returncode != 0
    assert "ud_commit" in result.stderr


def test_caption_has_no_host_details(tmp_path: Path) -> None:
    result = _render(tmp_path, _kwargs(model_path="src/models/a.osim"))
    assert result.returncode == 0, result.stderr
    caption = re.search(r'<div class="provenance-note.*?</div>', result.stdout, re.S)
    assert caption is not None
    hrefs = re.findall(r'href="([^"]+)"', caption.group(0))
    assert hrefs and all(href.startswith(f"{UD_REPO}/") for href in hrefs)
    assert not re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b|localhost|/home/", caption.group(0))


def test_quarto_render(tmp_path: Path) -> None:
    quarto = shutil.which("quarto")
    if quarto is None:
        pytest.skip("Quarto is required for the provenance shortcode integration check")
    shutil.copytree(ROOT / "_extensions", tmp_path / "_extensions")
    (tmp_path / "page.qmd").write_text(
        "---\ntitle: Provenance\n---\n\n"
        f"{{{{< provenance model_id=synthetic run_id={RUN_ID} ud_commit={COMMIT} "
        "claim_class=observed >}}\n",
        encoding="utf-8",
    )
    subprocess.run(  # noqa: S603 -- reason: fixed argv, no shell
        [quarto, "render", "page.qmd", "--to", "html"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        timeout=300,
    )
    html = (tmp_path / "page.html").read_text(encoding="utf-8")
    assert 'data-claim-class="observed"' in html
    assert f"{UD_REPO}/commit/{COMMIT}" in html
