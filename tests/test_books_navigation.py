"""Regression tests for the Books section website information architecture."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
QUARTO_CONFIG = REPO_ROOT / "_quarto.yml"
BOOKS_DIR = REPO_ROOT / "books"

EXPECTED_BOOK_PAGES = (
    "index.qmd",
    "tangent-space-methods.qmd",
    "control-is-motion.qmd",
    "biomechanics-biology-to-systems.qmd",
    "human-motor-control.qmd",
    "roadmap.qmd",
)


def test_quarto_render_includes_books_folder() -> None:
    """Quarto project render list should include the Books folder."""
    quarto = QUARTO_CONFIG.read_text(encoding="utf-8")
    assert "books/**/*.qmd" in quarto


def test_navbar_includes_books_and_textbooks() -> None:
    """Learn menu should expose the website books hub and both full textbooks."""
    quarto = QUARTO_CONFIG.read_text(encoding="utf-8")
    assert "books/index.html" in quarto
    assert "articles/The_Physics_of_Golf/quarto/index.html" in quarto
    assert "articles/The_Geometry_of_Motion/quarto/index.html" in quarto


def test_books_pages_exist_and_use_shared_sidebar() -> None:
    """Books hub and the 4 book pages should exist and bind to shared sidebar."""
    for relative_name in EXPECTED_BOOK_PAGES:
        page_path = BOOKS_DIR / relative_name
        assert page_path.exists(), f"Missing Books page: {relative_name}"
        page_text = page_path.read_text(encoding="utf-8")
        assert "sidebar: books-nav" in page_text


def test_books_series_page_links_to_each_book() -> None:
    """Books series landing page should link to all four main books."""
    series_page = (BOOKS_DIR / "index.qmd").read_text(encoding="utf-8")
    assert "tangent-space-methods.html" in series_page
    assert "control-is-motion.html" in series_page
    assert "biomechanics-biology-to-systems.html" in series_page
    assert "human-motor-control.html" in series_page


VOLUME_I_CHAPTER_HTML = (
    "ch01_foundations.html",
    "ch02_variational.html",
    "ch03_superposition.html",
    "ch03b_induced_acceleration_biomechanics.html",
    "ch04_contraction.html",
    "ch05_optimal_control.html",
    "ch06_duality.html",
    "ch07_counterfactuals.html",
    "ch08_applications.html",
    "ch09_parallel_mechanisms_constrained_dynamics.html",
)


def test_geometry_of_motion_volume_i_book_page_links_rendered_chapters() -> None:
    """Volume I Books landing must link to published GoM chapter HTML, not deny they exist."""
    landing = (BOOKS_DIR / "tangent-space-methods.qmd").read_text(encoding="utf-8")
    assert "No Volume I chapter has its own web page yet" not in landing
    for chapter_html in VOLUME_I_CHAPTER_HTML:
        assert chapter_html in landing, f"Missing Volume I chapter link: {chapter_html}"


def test_geometry_of_motion_volume_ii_book_page_links_html_monograph() -> None:
    """Volume II Books landing must expose the rendered volume2.html monograph and manuscript titles."""
    landing = (BOOKS_DIR / "control-is-motion.qmd").read_text(encoding="utf-8")
    assert "volume2.html" in landing
    assert "Throwing Away the Target" not in landing
    assert "Motion, Targets, and Timing" in landing
    assert "Orbital Stability and Transverse Linearization" in landing
    assert "volume2.html#trajectory-optimization" in landing
    assert "volume2.html#ch-underactuation" in landing


def test_geometry_of_motion_volume0_chapter_blurbs_match_topics() -> None:
    """Volume 0 landing chapter lines must not misplace geodesic metrics in the rotations chapter."""
    volume0 = (
        REPO_ROOT / "articles" / "The_Geometry_of_Motion" / "quarto" / "volume0.qmd"
    ).read_text(encoding="utf-8")
    assert "geodesic metrics" not in volume0
    assert "geodesics/shortest rotation paths" in volume0
    assert "SLERP" in volume0


def test_stale_gom_audit_runbooks_removed_from_manuscript_tree() -> None:
    """Sandbox-era audit markdown must not remain beside LaTeX sources."""
    gom_root = REPO_ROOT / "articles" / "The_Geometry_of_Motion"
    for stale_name in (
        "AUDIT_INDEX.md",
        "QUICK_REFERENCE.md",
        "BIBLIOGRAPHY_AUDIT_REPORT.md",
        "PR_INSTRUCTIONS.md",
    ):
        assert not (gom_root / stale_name).exists(), stale_name


def test_textbook_landing_pages_contain_chapter_links() -> None:
    """Textbook landing pages must contain tables of contents linking to their chapters."""
    physics_index = (
        REPO_ROOT / "articles" / "The_Physics_of_Golf" / "quarto" / "index.qmd"
    ).read_text(encoding="utf-8")
    assert "ch01_why_physics.html" in physics_index
    assert "ch09b_passive_stabilization.html" in physics_index
    assert "ch32_putting.html" in physics_index
    assert "glossary.html" in physics_index

    geom_index = (
        REPO_ROOT / "articles" / "The_Geometry_of_Motion" / "quarto" / "index.qmd"
    ).read_text(encoding="utf-8")
    assert "volume0.html" in geom_index
    assert "volume1.html" in geom_index
    assert "volume2.html" in geom_index
    assert "vol0_ch01_linear_algebra.html" in geom_index
    assert "ch01_foundations.html" in geom_index


def test_article_index_includes_physics_of_golf_chapters() -> None:
    """Article catalog in resources/articles.qmd must include all chapters including ch09b and ch32."""
    catalog = (REPO_ROOT / "resources" / "articles.qmd").read_text(encoding="utf-8")
    assert "ch09b_passive_stabilization.html" in catalog
    assert "ch32_putting.html" in catalog


def test_models_hub_links_all_companion_guides() -> None:
    """models/models.qmd should link to all 7 companion engine guides."""
    models_hub = (REPO_ROOT / "models" / "models.qmd").read_text(encoding="utf-8")
    for engine_page in (
        "models-mujoco.html",
        "models-drake.html",
        "models-pinocchio.html",
        "models-opensim.html",
        "models-myosim.html",
        "models-simulink.html",
        "models-pendulum.html",
    ):
        assert engine_page in models_hub, f"Missing {engine_page} link in models/models.qmd"


def test_repositories_hub_links_model_repositories() -> None:
    """repositories/repositories.qmd should link to repositories-models.html."""
    repo_hub = (REPO_ROOT / "repositories" / "repositories.qmd").read_text(encoding="utf-8")
    assert "repositories-models.html" in repo_hub
