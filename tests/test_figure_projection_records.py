"""Tests for the published-figure projection-record gate (VIS-EVIDENCE-3, #5421).

Enforces:
1. A non-draft rendered page fails when it embeds a figure that has no
   projection record and no explicit exemption.
2. A draft page (``draft: true``) only warns.
3. A figure is traced only by a ``visualization`` artifact of a projection
   manifest that passes ``verify_projection_manifest`` with matching bytes.
4. Exemptions are explicit globs, each with a reason.
5. The current site passes with the checked-in exemptions.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from scripts import check_figure_projection_records as gate
from scripts.mocap_projection_primitives import MocapProjectionError
from tests.test_markerless_mocap_projection_contract import _valid_manifest

ROOT = Path(__file__).resolve().parents[1]
FIGURE = "articles/figures/swing.svg"
SVG = b'<svg xmlns="http://www.w3.org/2000/svg"/>\n'
QUARTO = 'project:\n  render:\n    - "articles/**/*.qmd"\n    - "!articles/hidden/**/*.qmd"\n'


def _site(tmp_path: Path, body: str, frontmatter: str = "") -> Path:
    (tmp_path / "_quarto.yml").write_text(QUARTO, encoding="utf-8")
    (tmp_path / "articles/figures").mkdir(parents=True)
    (tmp_path / FIGURE).write_bytes(SVG)
    page = f"---\ntitle: Page\n{frontmatter}---\n\n{body}\n"
    (tmp_path / "articles/page.qmd").write_text(page, encoding="utf-8")
    return tmp_path


def _exemptions(tmp_path: Path, entries: list[dict[str, str]]) -> Path:
    path = tmp_path / "exemptions.json"
    path.write_text(json.dumps({"exemptions": entries}), encoding="utf-8")
    return path


def _projection(tmp_path: Path, kind: str = "visualization", data: bytes = SVG) -> Path:
    manifest: dict[str, Any] = _valid_manifest(tmp_path)[0]
    artifact = manifest["artifacts"][0]
    revision = manifest["source"]["revision"]
    artifact.update(
        path=FIGURE,
        kind=kind,
        media_type="image/svg+xml",
        sha256=hashlib.sha256(data).hexdigest(),
        bytes=len(data),
        source_url=f"https://github.com/D-sorganization/UpstreamDrift/blob/{revision}/{FIGURE}",
    )
    directory = tmp_path / "projections"
    directory.mkdir()
    (directory / "swing.json").write_text(json.dumps(manifest), encoding="utf-8")
    return directory


def _check(
    root: Path, projections: Path | None = None, exemptions: Path | None = None
) -> gate.FigureReport:
    return gate.check_site(
        root,
        projections or root / "no-projections",
        exemptions or _exemptions(root, []),
    )


def test_untraced_figure_on_published_page_fails(tmp_path: Path) -> None:
    root = _site(tmp_path, "![A swing](figures/swing.svg)")
    report = _check(root)
    assert report.failures == [f"articles/page.qmd: {FIGURE}"]
    assert report.warnings == []


def test_draft_page_only_warns(tmp_path: Path) -> None:
    root = _site(tmp_path, "![A swing](figures/swing.svg)", "draft: true\n")
    report = _check(root)
    assert report.failures == []
    assert report.warnings == [f"articles/page.qmd: {FIGURE}"]


def test_html_img_and_root_relative_paths_are_found(tmp_path: Path) -> None:
    root = _site(tmp_path, f'<img src="/{FIGURE}" alt="A swing">')
    assert _check(root).failures == [f"articles/page.qmd: {FIGURE}"]


def test_external_code_fenced_and_unrendered_figures_are_ignored(tmp_path: Path) -> None:
    body = "![Remote](https://example.org/a.png)\n\n```markdown\n![Example](figures/swing.svg)\n```"
    root = _site(tmp_path, body)
    hidden = root / "articles/hidden"
    hidden.mkdir()
    (hidden / "page.qmd").write_text("---\ntitle: H\n---\n\n![x](../figures/swing.svg)\n")
    assert _check(root).failures == []


def test_included_fragment_figures_count(tmp_path: Path) -> None:
    root = _site(tmp_path, "{{< include _fragment.qmd >}}")
    (root / "articles/_fragment.qmd").write_text("![A swing](figures/swing.svg)\n")
    assert _check(root).failures == [f"articles/page.qmd: {FIGURE}"]


def test_visualization_projection_record_traces_figure(tmp_path: Path) -> None:
    root = _site(tmp_path, "![A swing](figures/swing.svg)")
    assert _check(root, _projection(tmp_path)).failures == []


def test_non_visualization_artifact_does_not_trace(tmp_path: Path) -> None:
    root = _site(tmp_path, "![A swing](figures/swing.svg)")
    report = _check(root, _projection(tmp_path, kind="calibration_summary"))
    assert report.failures == [f"articles/page.qmd: {FIGURE}"]


def test_projection_with_changed_figure_bytes_fails_closed(tmp_path: Path) -> None:
    root = _site(tmp_path, "![A swing](figures/swing.svg)")
    projections = _projection(tmp_path, data=b"<svg/>\n")
    with pytest.raises(MocapProjectionError, match="artifact mismatch"):
        _check(root, projections)


def test_exemption_glob_with_reason_passes(tmp_path: Path) -> None:
    root = _site(tmp_path, "![A swing](figures/swing.svg)")
    exemptions = _exemptions(tmp_path, [{"pattern": "articles/figures/*", "reason": "theory"}])
    assert _check(root, exemptions=exemptions).failures == []


def test_exemption_glob_stays_in_its_directory(tmp_path: Path) -> None:
    root = _site(tmp_path, "![A swing](figures/swing.svg)")
    exemptions = _exemptions(tmp_path, [{"pattern": "articles/*", "reason": "theory"}])
    assert _check(root, exemptions=exemptions).failures == [f"articles/page.qmd: {FIGURE}"]


@pytest.mark.parametrize("entry", [{"pattern": "articles/*"}, {"pattern": "a/*", "reason": " "}])
def test_exemption_without_reason_is_rejected(tmp_path: Path, entry: dict[str, str]) -> None:
    with pytest.raises(ValueError, match="reason"):
        gate.load_exemptions(_exemptions(tmp_path, [entry]))


def test_main_exit_codes(tmp_path: Path) -> None:
    root = _site(tmp_path, "![A swing](figures/swing.svg)")
    args = ["--root", str(root), "--projections", str(root / "none")]
    exemptions = _exemptions(tmp_path, [])
    assert gate.main([*args, "--exemptions", str(exemptions)]) == 1
    exempt = _exemptions(tmp_path, [{"pattern": "articles/figures/*", "reason": "theory"}])
    assert gate.main([*args, "--exemptions", str(exempt)]) == 0


def test_current_site_passes_with_explicit_exemptions() -> None:
    report = gate.check_site(ROOT, gate.DEFAULT_PROJECTIONS, gate.DEFAULT_EXEMPTIONS)
    assert report.failures == []
    assert all(item.reason.strip() for item in gate.load_exemptions(gate.DEFAULT_EXEMPTIONS))
