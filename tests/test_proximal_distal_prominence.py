"""Cross-surface contracts for the governed proximal-distal study library."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONOGRAPH_ROUTE = "articles/proximal_distal_energy_transfer/index.html"
MONOGRAPH_SOURCE_COMMIT = "85cce4d3307bb7ad3953d9fc6e583e370803515c"
TOOLS_SOURCE_COMMIT = "cefcc1878de11804c44cd7d1d19c0ffcf58fa89e"


def _read(relative_path: str) -> str:
    """Read one governed source surface as UTF-8 text."""
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _read_navigation_block(quarto: str) -> str:
    """Return the global Read navigation block without matching the Books sidebar."""
    match = re.search(
        r'      - text: "Read"(?P<body>.*?)      - text: "Technology"',
        quarto,
        re.DOTALL,
    )
    assert match is not None, "Read navigation block is missing"
    return match.group("body")


def test_global_read_navigation_promotes_the_technical_monograph() -> None:
    """The three long-form technical entries should be peers in the Read menu."""
    read_navigation = _read_navigation_block(_read("_quarto.yml"))

    assert 'text: "Proximal-to-Distal Technical Monograph"' in read_navigation
    assert f"href: {MONOGRAPH_ROUTE}" in read_navigation


def test_home_promotes_the_monograph_in_latest_writing_and_books() -> None:
    """The home page should expose the monograph in both discovery surfaces."""
    home = _read("index.qmd")

    assert home.count(f'href="{MONOGRAPH_ROUTE}"') >= 2
    assert "Technical monograph and computational publication" in home
    assert "Independent scientific review and human validation remain open" in home


def test_books_hub_treats_the_monograph_as_a_distinct_long_form_reference() -> None:
    """The Books hub should give the monograph equal prominence without calling it a textbook."""
    books = _read("books/index.qmd")

    assert "two rendered textbook collections and one governed technical monograph" in books
    assert "### Proximal-to-Distal Energy Transfer in the Golf Swing" in books
    assert f"../{MONOGRAPH_ROUTE}" in books
    assert "## Proximal-to-Distal Study Library" in books
    for route in (
        "../articles/proximal-distal-a-journey-through-the-swing.html",
        "../articles/proximal-distal-energy-transfer.html",
        "../articles/proximal-distal-model-workbench.html",
    ):
        assert route in books
    assert "computational publication" in books
    assert "not a completed or peer-reviewed textbook" in books


def test_article_catalog_uses_current_monograph_scope_and_long_form_orientation() -> None:
    """The catalog should use the governed chapter count and distinguish publication types."""
    catalog = _read("resources/articles.qmd")

    assert "full 37-chapter mathematical monograph" in catalog
    assert "34-chapter" not in catalog
    assert "two textbooks and the governed technical monograph" in catalog


def test_learning_paths_link_the_study_library_at_the_point_of_use() -> None:
    """Both relevant learning paths should connect reading, evidence, and exploration."""
    for path in (
        "resources/learning-path-golf-science.qmd",
        "resources/learning-path-biomechanics.qmd",
    ):
        learning_path = _read(path)
        assert f"../{MONOGRAPH_ROUTE}" in learning_path
        assert "../articles/proximal-distal-a-journey-through-the-swing.html" in learning_path
        assert "../articles/proximal-distal-model-workbench.html" in learning_path
        assert "model result" in learning_path.lower()
        assert "human validation" in learning_path.lower()


def test_software_surfaces_connect_reading_evidence_and_workbench() -> None:
    """UpstreamDrift surfaces should expose the study as a bounded worked program."""
    for path in ("models/models.qmd", "resources/resources-software.qmd"):
        software_surface = _read(path)
        assert f"../{MONOGRAPH_ROUTE}" in software_surface
        assert "../articles/proximal-distal-model-workbench.html" in software_surface
        assert MONOGRAPH_SOURCE_COMMIT in software_surface
        assert "models, claims, and evidence" in software_surface
        assert "human validation" in software_surface.lower()


def test_companion_and_workbench_use_governed_or_immutable_research_links() -> None:
    """Reader routes must not bypass the governed publication through mutable source links."""
    companion = _read("articles/proximal-distal-a-journey-through-the-swing.qmd")
    workbench = _read("articles/proximal-distal-model-workbench.qmd")

    for source in (companion, workbench):
        assert "D-sorganization/UpstreamDrift/blob/main/" not in source
        assert "D-sorganization/UpstreamDrift/tree/main/" not in source
        assert "raw.githubusercontent.com/D-sorganization/UpstreamDrift/main/" not in source
        assert "proximal_distal_energy_transfer/index.html" in source
        assert MONOGRAPH_SOURCE_COMMIT in source

    assert "D-sorganization/Tools/tree/main/" not in workbench
    assert "D-sorganization/Tools/blob/main/" not in workbench
    assert TOOLS_SOURCE_COMMIT in workbench


def test_search_e2e_requires_the_canonical_monograph_result() -> None:
    """The browser contract should search for and select the canonical monograph route."""
    search_spec = _read("tests/e2e/search.spec.js")

    assert "finds the governed proximal-distal technical monograph" in search_spec
    assert MONOGRAPH_ROUTE in search_spec
