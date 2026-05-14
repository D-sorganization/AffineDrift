"""Regression coverage for Tangent-Space Series internal links."""

from pathlib import Path

from src.tools.check_links import _is_broken_link, find_links

REPO_ROOT = Path(__file__).resolve().parents[1]
TANGENT_LINK_SOURCES = (
    Path("resources/articles.qmd"),
    Path("pages/tangent-hyperplanes.qmd"),
    Path("articles/tangent-hyperplanes-series/part-4-residuals-curvature.qmd"),
    Path("articles/tangent-hyperplane-articles/LAYMANS_TERMS_SUMMARY.qmd"),
    Path("articles/tangent-hyperplane-articles/Advanced/Contraction_Tangent_LAYMAN.qmd"),
    Path("articles/tangent-hyperplane-articles/Advanced/Hybrid_Tangent_LAYMAN.qmd"),
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
