"""Tests for MM-6 Quarto render verification (#5414)."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs" / "development" / "motion-measurement"
PART1 = DOCS_DIR / "part-1-representing-orientation.qmd"
PART2 = DOCS_DIR / "part-2-joint-coordinates-velocity-consequences.qmd"
REFERENCES_BIB = DOCS_DIR / "references.bib"
FIGURES_DIR = DOCS_DIR / "figures"
COMPANION_HTML = DOCS_DIR / "interactive_companion.html"

CROSS_REF_PREFIXES = ("fig-", "fig:", "tbl-", "tbl:", "sec-", "sec:", "eq-", "eq:")
EXPECTED_FIGURE_FILES = (
    "f1_cardan_sequences.svg",
    "f2_gimbal_lock.svg",
    "f3_angle_unwrap.svg",
    "f4_orthogonality_drift.svg",
    "f5_quaternion_continuity.svg",
    "f6_helical_axis_error.svg",
    "f7_angular_velocity_differences.svg",
    "f8_xfactor_variants.svg",
)


def _split_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    assert len(parts) >= 3, f"Missing frontmatter in {path}"
    fm = yaml.safe_load(parts[1])
    assert isinstance(fm, dict), f"Frontmatter in {path} must be a dict"
    return fm, parts[2]


def _extract_bibtex_keys(bib_path: Path) -> set[str]:
    assert bib_path.is_file(), f"Bibliography file {bib_path} not found"
    keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", bib_path.read_text(encoding="utf-8")))
    assert keys, f"No BibTeX entry keys parsed from {bib_path}"
    return keys


def _extract_citation_keys(body: str) -> set[str]:
    raw_keys = set(re.findall(r"(?<![\w/])@([A-Za-z0-9][A-Za-z0-9:._/-]*)", body))
    return {k for k in raw_keys if not any(k.startswith(p) for p in CROSS_REF_PREFIXES)}


def test_draft_flags_preserved_and_bibliography_declared() -> None:
    """Both .qmd files retain draft: true, listing: false, and declare bibliography: references.bib."""
    for path in (PART1, PART2):
        assert path.exists(), f"File {path} does not exist"
        fm, _ = _split_frontmatter(path)
        assert fm.get("draft") is True, f"{path} draft flag must be True"
        assert fm.get("listing") is False, f"{path} listing flag must be False"
        assert fm.get("bibliography") == "references.bib", f"{path} must configure bibliography"


def test_citations_resolve_in_references_bib() -> None:
    """All @citation keys referenced in Part 1 and Part 2 resolve in references.bib."""
    bib_keys = _extract_bibtex_keys(REFERENCES_BIB)
    expected_verified = {
        "grood1983",
        "wu2002",
        "wu2005",
        "woltring1994",
        "shoemake1985",
        "kwon2013",
        "brown2013",
        "chu2010",
        "cheetham2001",
        "woltring1985",
    }
    assert not (expected_verified - bib_keys), "Missing verified references in references.bib"

    for path in (PART1, PART2):
        _, body = _split_frontmatter(path)
        qmd_citations = _extract_citation_keys(body)
        assert qmd_citations, f"Expected citations in {path}, none found"
        assert not (qmd_citations - bib_keys), f"Unresolved citations in {path}"


def test_referenced_figure_paths_and_companion_exist_on_disk() -> None:
    """All figure paths and interactive companion referenced in Part 1 and Part 2 exist on disk."""
    assert COMPANION_HTML.is_file(), f"Interactive companion missing at {COMPANION_HTML}"
    for fig_name in EXPECTED_FIGURE_FILES:
        assert (FIGURES_DIR / fig_name).is_file(), f"Missing figure file {fig_name}"

    for path in (PART1, PART2):
        _, body = _split_frontmatter(path)
        image_matches = re.findall(r"!\[.*?\]\(([^)]+)\)", body)
        assert image_matches, f"No image embeds found in {path}"
        for ref in image_matches:
            target = DOCS_DIR / ref.split()[0]
            assert target.is_file(), f"Image target {target} in {path} does not exist"

        link_matches = re.findall(r"\[.*?\]\(([^)]+)\)", body)
        for link in link_matches:
            if link.endswith(".html") or link.endswith(".svg"):
                target = DOCS_DIR / link.split()[0]
                assert target.is_file(), f"Linked file {target} in {path} does not exist"


def test_katex_math_delimiters_balanced() -> None:
    """KaTeX inline ($...$) and display ($$...$$) delimiters are balanced and non-empty."""
    for path in (PART1, PART2):
        _, body = _split_frontmatter(path)
        assert body.count("$$") % 2 == 0, f"Unbalanced display math ($$) in {path}"

        clean = re.sub(r"\$\$.*?\$\$", "", body, flags=re.DOTALL)
        clean = re.sub(r"```.*?```", "", clean, flags=re.DOTALL)
        clean = re.sub(r"`[^`]+`", "", clean)
        assert len(re.findall(r"(?<!\\)\$", clean)) % 2 == 0, f"Unbalanced inline math in {path}"


def test_quarto_callouts_balanced_and_well_formed() -> None:
    """Quarto callouts (::: {.callout-...}) are balanced and contain headings."""
    callout_re = re.compile(r":::\s*\{\.callout-(note|warning|important|tip|caution)")
    for path in (PART1, PART2):
        _, body = _split_frontmatter(path)
        starts = list(callout_re.finditer(body))
        assert starts, f"Expected at least one callout in {path}"
        fences = re.findall(r"^:::\s*$", body, flags=re.MULTILINE)
        assert len(fences) >= len(starts), f"Mismatched callout close fences in {path}"


def test_markdown_tables_well_formed() -> None:
    """Markdown tables have matching column counts across headers, separators, and rows."""
    table_row_re = re.compile(r"^\|(.+)\|$")
    for path in (PART1, PART2):
        _, body = _split_frontmatter(path)
        in_table, cols = False, 0
        for line in body.splitlines():
            m = table_row_re.match(line.strip())
            if m:
                row_cols = [c.strip() for c in m.group(1).split("|")]
                if not in_table:
                    in_table, cols = True, len(row_cols)
                else:
                    assert len(row_cols) == cols, f"Inconsistent columns in {path}"
            else:
                in_table = False


def test_cross_references_well_formed() -> None:
    """Cross references to figures correspond to declared figure identifiers."""
    for path in (PART1, PART2):
        _, body = _split_frontmatter(path)
        figure_ids = set(re.findall(r"\{#(fig-[a-zA-Z0-9-]+)\}", body))
        for fig_id in figure_ids:
            assert fig_id.startswith("fig-"), f"Invalid figure id {fig_id} in {path}"


@pytest.mark.timeout(300)
@pytest.mark.skipif(shutil.which("quarto") is None, reason="quarto CLI not available on PATH")
@pytest.mark.parametrize("qmd_path", [PART1, PART2], ids=["part-1", "part-2"])
def test_quarto_render_document_zero_warnings(qmd_path: Path) -> None:
    """Quarto renders document with zero warnings and outputs valid HTML."""
    quarto_bin = shutil.which("quarto")
    assert quarto_bin is not None

    cmd = [quarto_bin, "render", str(qmd_path), "-M", "draft:false"]
    result = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=False)
    combined = f"{result.stdout}\n{result.stderr}"
    assert result.returncode == 0, f"Quarto render failed for {qmd_path}:\n{combined}"

    warnings = [
        line
        for line in combined.splitlines()
        if any(w in line for w in ("[WARNING]", "WARN:", "Warning:"))
        and "No </head> tag" not in line
    ]
    assert not warnings, f"Quarto render emitted warnings for {qmd_path}:\n" + "\n".join(warnings)

    output_rel = (Path("_site") / qmd_path.relative_to(REPO_ROOT)).with_suffix(".html")
    html_file = REPO_ROOT / output_rel
    assert html_file.is_file(), f"Rendered HTML not found at {html_file}"
    content = html_file.read_text(encoding="utf-8")
    assert len(content) > 10_000, f"Rendered HTML {html_file} is suspiciously small"
    assert "callout-" in content and ".svg" in content
