"""Regression coverage for Tangent-Space Series internal links."""

from pathlib import Path

from src.tools.check_links import _is_broken_link, find_links

REPO_ROOT = Path(__file__).resolve().parents[1]
TANGENT_LINK_SOURCES = (
    Path("resources/articles.qmd"),
    Path("pages/tangent-hyperplanes.qmd"),
    Path("articles/tangent-hyperplanes-series/part-4-residuals-curvature.qmd"),
    Path("articles/tangent-hyperplanes-series/part-5-contraction.qmd"),
    Path("articles/tangent-hyperplanes-series/part-6-hybrid.qmd"),
    Path("articles/tangent-hyperplanes-series/part-7-residual-aware.qmd"),
    Path("articles/tangent-hyperplane-articles/LAYMANS_TERMS_SUMMARY.qmd"),
    Path("articles/tangent-hyperplane-articles/Advanced/Contraction_Tangent_LAYMAN.qmd"),
    Path("articles/tangent-hyperplane-articles/Advanced/Hybrid_Tangent_LAYMAN.qmd"),
)

CANONICAL_SERIES_PARTS = (
    Path("articles/tangent-hyperplanes-series/part-1-geometry.qmd"),
    Path("articles/tangent-hyperplanes-series/part-2-dynamics.qmd"),
    Path("articles/tangent-hyperplanes-series/part-3-control.qmd"),
    Path("articles/tangent-hyperplanes-series/part-4-residuals-curvature.qmd"),
    Path("articles/tangent-hyperplanes-series/part-5-contraction.qmd"),
    Path("articles/tangent-hyperplanes-series/part-6-hybrid.qmd"),
    Path("articles/tangent-hyperplanes-series/part-7-residual-aware.qmd"),
)


def test_tangent_series_internal_links_resolve() -> None:
    """Tangent-space overview pages must link to source-backed local targets."""
    broken_links: list[str] = []

    for relative_path in TANGENT_LINK_SOURCES:
        source_file = REPO_ROOT / relative_path
        for link, line_number in find_links(source_file):
            if _is_broken_link(root_path=REPO_ROOT, file_path=source_file, link=link):
                broken_links.append(f"{relative_path}:{line_number} -> {link}")

    assert broken_links == []


def test_canonical_tangent_series_has_seven_part_reading_path() -> None:
    """The compact series should carry the heavy-merge advanced topics."""
    missing_parts = [
        str(path) for path in CANONICAL_SERIES_PARTS if not (REPO_ROOT / path).is_file()
    ]
    assert missing_parts == []

    hub_text = (REPO_ROOT / "pages/tangent-hyperplanes.qmd").read_text(encoding="utf-8")
    for part in CANONICAL_SERIES_PARTS:
        rendered_href = f"../{part.with_suffix('.html').as_posix()}"
        assert rendered_href in hub_text


def test_reference_manuscript_is_demoted_from_canonical_path() -> None:
    """The single-file manuscript remains rendered but is clearly secondary."""
    manuscript = (
        REPO_ROOT / "articles/tangent-hyperplane-articles/Tangent_Hyperplanes_Unified_Thesis.qmd"
    )
    text = manuscript.read_text(encoding="utf-8")

    assert 'title: "Full Reference Manuscript:' in text
    assert "canonical rendered reading path" in text
