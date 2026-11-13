"""Display-title contract for tangent review finding 2B (#5180 / #5182)."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SERIES_DIR = REPO_ROOT / "articles" / "tangent-hyperplanes-series"
HUB = REPO_ROOT / "pages" / "tangent-hyperplanes.qmd"

PART_FILES = tuple(
    SERIES_DIR / f"part-{index}-{slug}.qmd"
    for index, slug in (
        (1, "geometry"),
        (2, "dynamics"),
        (3, "control"),
        (4, "residuals-curvature"),
        (5, "contraction"),
        (6, "hybrid"),
        (7, "residual-aware"),
    )
)

EXPECTED_TITLES = {
    "part-1-geometry.qmd": "Tangent-Space Series, Part 1: Geometry",
    "part-2-dynamics.qmd": "Tangent-Space Series, Part 2: Dynamics",
    "part-3-control.qmd": "Tangent-Space Series, Part 3: Control",
    "part-4-residuals-curvature.qmd": "Tangent-Space Series, Part 4: Residuals and Curvature",
    "part-5-contraction.qmd": "Tangent-Space Series, Part 5: Contraction",
    "part-6-hybrid.qmd": "Tangent-Space Series, Part 6: Hybrid Systems",
    "part-7-residual-aware.qmd": "Tangent-Space Series, Part 7: Residual-Aware Control",
}


def _front_matter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise AssertionError(f"{path} missing YAML front matter")
    end = text.index("---", 3)
    return yaml.safe_load(text[3:end]) or {}


def test_compact_series_front_matter_titles_retire_hyperplane_branding() -> None:
    """Roman-numeral 'Tangent Hyperplanes' titles must not remain in series front matter."""
    for path in PART_FILES:
        meta = _front_matter(path)
        title = str(meta.get("title", ""))
        assert "Tangent Hyperplanes" not in title, f"{path.name} title still uses legacy branding"
        assert title == EXPECTED_TITLES[path.name], f"{path.name} title mismatch: {title!r}"


def test_compact_series_descriptions_avoid_hyperplane_wording() -> None:
    """Meta descriptions must not describe the series using 'hyperplane'."""
    for path in PART_FILES:
        meta = _front_matter(path)
        description = str(meta.get("description", "")).lower()
        assert "hyperplane" not in description, f"{path.name} description still says hyperplane"


def test_compact_series_prev_next_links_use_part_labels() -> None:
    """In-body prev/next links must use Part N labels, not legacy hyperplane titles."""
    legacy = re.compile(r"Tangent Hyperplanes [IVXLC]+:")
    for path in PART_FILES:
        body = path.read_text(encoding="utf-8").split("---", 2)[-1]
        assert not legacy.search(body), f"{path.name} still links with legacy hyperplane titles"


def test_hub_intro_notes_legacy_slug_not_display_title() -> None:
    """Hub must explain legacy URL slug without resurrecting hyperplane as the series name."""
    text = HUB.read_text(encoding="utf-8")
    assert "legacy" in text.lower() and "tangent-hyperplanes" in text
    assert "Tangent Hyperplanes I:" not in text
