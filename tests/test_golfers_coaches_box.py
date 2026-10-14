"""Tests for the "What This Means for Golfers and Coaches" Box with Guardrails (WEB-03.7 #4512).

Enforces:
1. One accessible aside component driven by front matter (`golfers-coaches`) or `::: {.golfers-coaches}` Div.
2. Uses `<aside class="golfers-coaches-box" role="note" aria-label="What This Means for Golfers and Coaches">`.
3. Displays Title Case heading `## What This Means for Golfers and Coaches {.unlisted .unnumbered}`.
4. Automatically includes the page's `evidence-rung` badge linking to `/pages/how-to-read.html#evidence-ladder`.
5. Strictly enforces the mandatory Simulation-to-Human Epistemic Guardrail.
6. Core articles declare governed `golfers-coaches` metadata.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from src.tools.utils.frontmatter import split_frontmatter

ROOT = Path(__file__).resolve().parents[1]
FILTER = ROOT / "scripts/filters/golfers-coaches.lua"

MANDATORY_GUARDRAIL = (
    "Simulation-to-Human Guardrail: This section translates a mathematical or "
    "multibody simulation insight into coaching concepts. It does not measure live human "
    "muscle activation (EMG) or prescribe individual swing changes."
)

CORE_ARTICLES = (
    "articles/intentional-constraint-collapse.qmd",
    "articles/wrist-universal-joint.qmd",
    "articles/secondary-axis-stability.qmd",
)


def _render_html(frontmatter_extra: str, body: str = "Body paragraph.") -> str:
    """Render a synthetic page through Quarto/Pandoc with the golfers-coaches Lua filter."""
    quarto = shutil.which("quarto")
    if quarto is None:
        pytest.skip("Quarto is required for the golfers-coaches integration check")
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


@pytest.mark.integration
def test_page_without_frontmatter_or_div_is_unchanged() -> None:
    html = _render_html("categories: [test]")
    assert "golfers-coaches-box" not in html
    assert "What This Means for Golfers and Coaches" not in html
    assert "Simulation-to-Human Guardrail" not in html


@pytest.mark.integration
def test_page_with_frontmatter_renders_accessible_box() -> None:
    frontmatter = (
        'evidence-rung: "qualified-simulation"\n'
        "golfers-coaches:\n"
        '  takeaway: "The drift-control ratio compares modeled autonomous momentum to maximum active muscle correction capacity."\n'
        "  questions:\n"
        '    - "How much time is available in late downswing to adjust face angle?"\n'
        '    - "Are swing adjustments practiced early in transition?"\n'
    )
    html = _render_html(frontmatter)
    assert "golfers-coaches-box" in html
    assert 'role="note"' in html
    assert 'aria-label="What This Means for Golfers and Coaches"' in html
    assert "What This Means for Golfers and Coaches" in html
    assert "Conceptual Takeaway" in html
    assert (
        "The drift-control ratio compares modeled autonomous momentum to maximum active muscle correction capacity."
        in html
    )
    assert MANDATORY_GUARDRAIL in html
    assert "Questions to Explore With a Coach" in html
    assert "How much time is available in late downswing to adjust face angle?" in html
    assert "Are swing adjustments practiced early in transition?" in html
    assert "evidence-badge" in html
    assert "badge-qualified-simulation" in html
    assert "/pages/how-to-read.html#evidence-ladder" in html


@pytest.mark.integration
def test_page_with_div_renders_box() -> None:
    div_body = (
        "::: {.golfers-coaches}\n"
        "Varying mechanical impedance near impact stabilizes club delivery.\n\n"
        "- Does grip tension change dynamically before impact?\n"
        "- What drills encourage appropriate wrist compliance?\n"
        ":::\n\n"
        "Main article text continues here."
    )
    html = _render_html('evidence-rung: "mathematical-identity"', body=div_body)
    assert "golfers-coaches-box" in html
    assert 'role="note"' in html
    assert "What This Means for Golfers and Coaches" in html
    assert "Varying mechanical impedance near impact stabilizes club delivery." in html
    assert MANDATORY_GUARDRAIL in html
    assert "Does grip tension change dynamically before impact?" in html
    assert "badge-math-identity" in html
    assert "Main article text continues here." in html


@pytest.mark.integration
def test_custom_guardrail_preserves_mandatory_guardrail() -> None:
    frontmatter = (
        'evidence-rung: "mathematical-identity"\n'
        "golfers-coaches:\n"
        '  takeaway: "Constraint torques pass load through joints."\n'
        '  guardrail: "Custom mechanical identity note on joint limits."\n'
        "  questions:\n"
        '    - "Question one?"\n'
    )
    html = _render_html(frontmatter)
    assert MANDATORY_GUARDRAIL in html
    assert "Custom mechanical identity note on joint limits." in html


@pytest.mark.integration
@pytest.mark.parametrize(
    ("rung", "expected_badge"),
    [
        ("mathematical-identity", "badge-math-identity"),
        ("manufactured-fixture", "badge-manufactured-synthetic"),
        ("qualified-simulation", "badge-qualified-simulation"),
        ("measured-participant-result", "badge-pilot-bounded"),
    ],
)
def test_evidence_rung_mapping(rung: str, expected_badge: str) -> None:
    html = _render_html(
        f'evidence-rung: "{rung}"\n'
        "golfers-coaches:\n"
        '  takeaway: "Test takeaway."\n'
        "  questions:\n"
        '    - "Test question?"\n'
    )
    assert expected_badge in html, f"Expected {expected_badge} for rung {rung}"


def test_core_articles_declare_golfers_coaches_frontmatter() -> None:
    for rel_path in CORE_ARTICLES:
        file_path = ROOT / rel_path
        assert file_path.exists(), f"Core article missing: {rel_path}"
        content = file_path.read_text(encoding="utf-8")
        fm, _body = split_frontmatter(content)
        assert fm, f"Article {rel_path} has no YAML front matter"

        assert (
            "evidence-rung" in fm
        ), f"Article {rel_path} must declare evidence-rung in front matter"
        assert (
            "golfers-coaches" in fm
        ), f"Article {rel_path} must declare golfers-coaches in front matter"

        gc = fm["golfers-coaches"]
        assert isinstance(gc, dict), f"Article {rel_path} golfers-coaches must be a dict"
        takeaway = gc.get("takeaway") or gc.get("summary")
        assert (
            takeaway and len(str(takeaway).strip()) > 20
        ), f"Article {rel_path} must have a non-trivial takeaway"

        questions = gc.get("questions")
        assert (
            isinstance(questions, list) and len(questions) >= 2
        ), f"Article {rel_path} must have at least 2 questions for coaches"
