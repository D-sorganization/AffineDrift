"""Tests for the Standard "What This Shows / What It Does Not Show" Caveat Block (WEB-03.4 #4509).

Enforces:
1. One structured block per page, generated from front matter (`caveats`).
2. Schema validation for `caveats` with required `establishes` and `does-not-establish`.
3. Quarto Lua filter (`scripts/filters/caveats-block.lua`) transforms metadata into accessible HTML/DOM.
4. All core pages provide complete, honest caveats covering positive scope, negative boundaries, and validation gates.
5. Print stylesheet (`css/print.css`) styles `.caveats-card` with `break-inside: avoid`.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import jsonschema
import pytest

from src.tools.caveats_block import (
    render_caveats_html,
    validate_caveats_dict,
)
from src.tools.utils.frontmatter import split_frontmatter
from src.tools.utils.frontmatter_schema import (
    ALLOWLIST_PATH,
    SCHEMA_PATH,
    load_article_frontmatter_schema,
    load_frontmatter_allowlist,
)

ROOT = Path(__file__).resolve().parents[1]
FILTER = ROOT / "scripts/filters/caveats-block.lua"
PRINT_CSS = ROOT / "css/print.css"


def _render_html(frontmatter_extra: str, body: str = "Body paragraph.") -> str:
    """Render a synthetic page through Quarto/Pandoc with the caveats-block Lua filter."""
    quarto = shutil.which("quarto")
    if quarto is None:
        pytest.skip("Quarto is required for the caveats-block integration check")
    with tempfile.TemporaryDirectory() as tmp_dir:
        qmd = Path(tmp_dir) / "test.qmd"
        content = (
            "---\n"
            "title: Test Article\n"
            "description: Test article description\n"
            f"{frontmatter_extra}\n"
            f"filters:\n  - {FILTER.resolve().as_posix()}\n"
            "format: html\n"
            "---\n\n"
            f"{body}\n"
        )
        qmd.write_text(content, encoding="utf-8")
        result = subprocess.run(
            [quarto, "render", str(qmd), "--to", "html"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert result.returncode == 0, f"quarto render failed:\n{result.stderr}\n{result.stdout}"
        html_file = qmd.with_suffix(".html")
        assert html_file.exists()
        return html_file.read_text(encoding="utf-8")


def test_schema_validates_caveats_structure() -> None:
    """Verify that schemas/article-front-matter-v1.schema.json validates caveats."""
    schema = load_article_frontmatter_schema(SCHEMA_PATH)
    validator = jsonschema.Draft202012Validator(schema)

    valid_caveats = {
        "title": "Valid Article",
        "status": "available",
        "audience-level": "advanced",
        "summary-plain": "Concise summary.",
        "abstract": "Detailed abstract text.",
        "key-takeaways": ["One", "Two", "Three"],
        "date": "2026-01-01",
        "date-modified": "2026-09-01",
        "last-reviewed": "2026-09-01",
        "canonical": "/articles/valid.html",
        "evidence-rung": "mathematical-identity",
        "caveats": {
            "evidence-level": "Theory (Mathematical Identity)",
            "establishes": [
                "Decomposition of system dynamics into autonomous drift and input.",
            ],
            "does-not-establish": [
                "Individual muscle forces or motor unit recruitment.",
            ],
            "open-critiques": [
                "CRIT-001: Verification on human participants pending.",
            ],
            "next-gate": "Simscape torque matching (GATE-SIM-01)",
        },
    }
    errors = list(validator.iter_errors(valid_caveats))
    assert not errors, f"Unexpected validation errors: {[e.message for e in errors]}"

    # Missing establishes must fail
    invalid_caveats = dict(valid_caveats)
    invalid_caveats["caveats"] = {
        "does-not-establish": ["Only negative bound."],
    }
    errs = list(validator.iter_errors(invalid_caveats))
    assert any("establishes" in e.message for e in errs)

    # Missing does-not-establish must fail
    invalid_caveats2 = dict(valid_caveats)
    invalid_caveats2["caveats"] = {
        "establishes": ["Only positive claim."],
    }
    errs2 = list(validator.iter_errors(invalid_caveats2))
    assert any("does-not-establish" in e.message for e in errs2)


def test_caveats_python_helper() -> None:
    """Unit test for Python rendering and validation helpers."""
    data = {
        "evidence-level": "Theory",
        "establishes": ["Point A", "Point B"],
        "does-not-establish": ["Limit X", "Limit Y"],
        "open-critiques": ["Critique 1"],
        "next-gate": "Gate Alpha",
    }
    errs = validate_caveats_dict(data)
    assert not errs

    html = render_caveats_html(data)
    assert "What This Shows / What It Does Not Show" in html
    assert "What This Page Establishes" in html
    assert "What This Page Does Not Establish" in html
    assert "Open Critiques and Active Inquiries" in html
    assert "Next Validation Gate" in html
    assert "Point A" in html
    assert "Limit X" in html
    assert "Critique 1" in html
    assert "Gate Alpha" in html


@pytest.mark.integration
def test_page_without_caveats_is_unchanged() -> None:
    """A page without caveats metadata renders normally without the caveat card."""
    html = _render_html("categories: [test]")
    assert "caveats-card" not in html
    assert "What This Shows / What It Does Not Show" not in html


@pytest.mark.integration
def test_page_with_caveats_renders_component() -> None:
    """A page with caveats front matter renders the accessible caveat block."""
    frontmatter = (
        "evidence-rung: mathematical-identity\n"
        "caveats:\n"
        '  evidence-level: "Theory (Mathematical Identity)"\n'
        "  establishes:\n"
        '    - "Exact mathematical decomposition into autonomous drift and input."\n'
        '    - "Linear torque transmission through state-dependent input matrix."\n'
        "  does-not-establish:\n"
        '    - "Individual muscle forces or activation timing in living golfers."\n'
        '    - "Empirical optimality of real-world swing trajectories."\n'
        "  open-critiques:\n"
        '    - "CRIT-002: Model assumes rigid links without soft-tissue dynamics."\n'
        '  next-gate: "Simscape torque matching (GATE-SIM-01)"\n'
    )
    html = _render_html(frontmatter)
    assert "caveats-card" in html
    assert "What This Shows / What It Does Not Show" in html
    assert "What This Page Establishes (Evidence Level: Theory (Mathematical Identity))" in html
    assert "Exact mathematical decomposition into autonomous drift and input." in html
    assert "Linear torque transmission through state-dependent input matrix." in html
    assert "What This Page Does Not Establish" in html
    assert "Individual muscle forces or activation timing in living golfers." in html
    assert "Empirical optimality of real-world swing trajectories." in html
    assert "Open Critiques and Active Inquiries" in html
    assert "CRIT-002: Model assumes rigid links without soft-tissue dynamics." in html
    assert "Next Validation Gate" in html
    assert "Simscape torque matching (GATE-SIM-01)" in html


def test_core_pages_all_have_valid_caveats() -> None:
    """All 10 declared core pages must include valid caveats in front matter."""
    cfg = load_frontmatter_allowlist(ALLOWLIST_PATH)
    core_pages = cfg["core_pages"]
    assert len(core_pages) >= 10, "Expected at least 10 core pages"

    for rel_path in core_pages:
        full_path = ROOT / rel_path
        assert full_path.is_file(), f"Core page does not exist: {full_path}"
        content = full_path.read_text(encoding="utf-8")
        fm, _ = split_frontmatter(content)
        assert "caveats" in fm, f"Core page {rel_path} is missing 'caveats' front matter"
        c = fm["caveats"]
        assert isinstance(c, dict), f"Core page {rel_path} 'caveats' must be a mapping"
        errs = validate_caveats_dict(c)
        assert not errs, f"Core page {rel_path} caveats validation failed: {errs}"


def test_print_stylesheet_includes_caveats_rules() -> None:
    """The print stylesheet must style the caveats card and prevent page breaks."""
    assert PRINT_CSS.exists()
    content = PRINT_CSS.read_text(encoding="utf-8")
    assert ".caveats-card" in content or ".what-this-shows" in content
    assert "break-inside: avoid" in content
