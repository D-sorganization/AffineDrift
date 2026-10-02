"""Tests for website page titles and meta descriptions (WEB-10.7, #4575).

Enforces that:
1. The home page title is descriptive (not generic "Home").
2. Every published page in sitemap.xml has a non-empty and globally unique title.
3. Every published page in sitemap.xml has a meta description between 70 and 160 characters.
4. Standalone status pages (e.g. 404.qmd) also carry valid titles and descriptions.
5. Navigation labels match page titles or an explicit allowlist (WEB-02.8, #4502).
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from scripts.check_quarto_render_coverage import sitemap_loc_to_source_path
from scripts.generate_sitemap import build_pages
from src.tools.utils.frontmatter import split_frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent


def get_effective_page_title(fm: dict[str, object], body: str) -> str:
    """Extract page title from YAML title, pagetitle, or first level-1 heading."""
    if fm.get("title"):
        return str(fm["title"]).strip()
    if fm.get("pagetitle"):
        return str(fm["pagetitle"]).strip()
    # Match markdown H1 outside code blocks
    m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if m:
        return re.sub(r"\{#[^}]+\}", "", m.group(1)).strip()
    # Match HTML H1
    m_html = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.DOTALL | re.IGNORECASE)
    if m_html:
        return re.sub(r"<[^>]+>", "", m_html.group(1)).strip()
    return ""


def get_published_sources() -> list[Path]:
    """Return all published source paths from the current sitemap page set."""
    locs = [page["loc"] for page in build_pages()]
    return [sitemap_loc_to_source_path(loc, REPO_ROOT) for loc in locs]


def test_home_page_title_is_descriptive() -> None:
    """Home page must use a descriptive title rather than generic 'Home'."""
    index_path = REPO_ROOT / "index.qmd"
    assert index_path.exists(), "index.qmd must exist"
    fm, _ = split_frontmatter(index_path.read_text(encoding="utf-8"))
    title = str(fm.get("title", "")).strip()

    assert title, "index.qmd must declare a title"
    assert title.lower() != "home", "Home page title must not be generic 'Home' (#4575)"
    assert "AffineDrift" in title, f"Home page title '{title}' should identify the site"


def test_every_published_page_has_non_empty_unique_title() -> None:
    """Every published page must have a non-empty and unique title across the site."""
    sources = get_published_sources()
    assert len(sources) >= 200, f"Expected full sitemap coverage; got {len(sources)} sources"

    titles_by_source: dict[Path, str] = {}
    for source in sources:
        text = source.read_text(encoding="utf-8")
        fm, body = split_frontmatter(text)
        title = get_effective_page_title(fm, body)
        assert title, f"{source} has an empty or unresolvable title"
        titles_by_source[source] = title

    # Check uniqueness
    titles_list = list(titles_by_source.values())
    duplicates: dict[str, list[str]] = {}
    for title in set(titles_list):
        if titles_list.count(title) > 1:
            duplicates[title] = [
                str(s.relative_to(REPO_ROOT)) for s, t in titles_by_source.items() if t == title
            ]

    assert not duplicates, f"Found duplicate page titles (#4575): {duplicates}"


def test_every_published_page_has_valid_meta_description() -> None:
    """Every published page must have a description between 70 and 160 characters."""
    sources = get_published_sources()
    failures: list[str] = []

    for source in sources:
        text = source.read_text(encoding="utf-8")
        fm, _ = split_frontmatter(text)
        desc = str(fm.get("description", "")).strip()

        if not desc:
            failures.append(f"{source.relative_to(REPO_ROOT)}: missing description")
        elif len(desc) < 70:
            failures.append(
                f"{source.relative_to(REPO_ROOT)}: description too short ({len(desc)} < 70): '{desc}'"
            )
        elif len(desc) > 160:
            failures.append(
                f"{source.relative_to(REPO_ROOT)}: description too long ({len(desc)} > 160): '{desc}'"
            )

    assert not failures, (
        f"Found {len(failures)} pages with invalid descriptions (must be 70-160 chars, #4575):\n"
        + "\n".join(failures[:20])
    )


def test_not_found_page_has_valid_title_and_description() -> None:
    """404.qmd must carry a valid title and 70-160 character description."""
    path = REPO_ROOT / "404.qmd"
    text = path.read_text(encoding="utf-8")
    fm, _ = split_frontmatter(text)

    title = str(fm.get("title", "")).strip()
    desc = str(fm.get("description", "")).strip()

    assert title, "404.qmd must have a title"
    assert 70 <= len(desc) <= 160, f"404.qmd description length ({len(desc)}) must be 70-160 chars"


ALLOWLISTED_NAV_SHORT_FORMS: frozenset[tuple[str, str]] = frozenset(
    {
        ("index.qmd", "Home"),
        ("books/index.qmd", "Books & Textbooks"),
        ("articles/theory-part1.qmd", "Part 1: Control-Affine Foundations"),
        ("articles/theory-part2.qmd", "Part 2: Counterfactual Diagnostics"),
        ("articles/theory-part3.qmd", "Part 3: Drift Invariance and Force Taxonomy"),
        ("articles/theory-part4.qmd", "Part 4: Worked Pendulum Dynamics"),
        ("articles/theory-part5.qmd", "Part 5: Numerical Consistency"),
        ("articles/appendix-applications.qmd", "Applications Appendix"),
        ("articles/affine-nature-golf-swing.qmd", "Consolidated Edition"),
        ("pages/tangent-hyperplanes.qmd", "Series Overview"),
        ("articles/tangent-hyperplanes-series/part-1-geometry.qmd", "Part 1: Geometry"),
        ("articles/tangent-hyperplanes-series/part-2-dynamics.qmd", "Part 2: Dynamics"),
        ("articles/tangent-hyperplanes-series/part-3-control.qmd", "Part 3: Control"),
        (
            "articles/tangent-hyperplanes-series/part-4-residuals-curvature.qmd",
            "Part 4: Residuals and Curvature",
        ),
        ("articles/tangent-hyperplanes-series/part-5-contraction.qmd", "Part 5: Contraction"),
        ("articles/tangent-hyperplanes-series/part-6-hybrid.qmd", "Part 6: Hybrid Systems"),
        (
            "articles/tangent-hyperplanes-series/part-7-residual-aware.qmd",
            "Part 7: Residual-Aware Control",
        ),
        ("pages/accessibility.qmd", "Accessibility"),
        ("books/tangent-space-methods.qmd", "Volume I: Tangent-Space Methods"),
        ("books/biomechanics-biology-to-systems.qmd", "Volume III: Biomechanics"),
        ("books/roadmap.qmd", "Roadmap & Curriculum"),
        (
            "articles/proximal_distal_energy_transfer/index.qmd",
            "Proximal-to-Distal Energy Transfer",
        ),
        (
            "articles/proximal_distal_energy_transfer/index.qmd",
            "Proximal-to-Distal Technical Monograph",
        ),
        (
            "articles/proximal-distal-falsification-atlas.qmd",
            "Proximal–Distal Falsification Atlas",
        ),
        ("pages/drifter-manifesto.qmd", "Theory Series"),
        ("resources/bibliography.qmd", "Bibliography"),
        ("pages/technology.qmd", "Technology Overview"),
        ("articles/technology-force-measurement.qmd", "Force Measurement"),
        ("articles/technology-motion-capture.qmd", "Motion Capture"),
        ("articles/technology-launch-monitors.qmd", "Launch Monitors"),
        ("articles/technology-club-fitting.qmd", "Club Fitting Simulation"),
        (
            "articles/technology-heavy-hit-impact-coupling.qmd",
            "Multibody Impact Coupling",
        ),
        ("articles/reference-point-problem.qmd", "The Reference-Point Problem"),
        (
            "articles/The_Geometry_of_Motion/quarto/volume1.qmd",
            "Volume I: Tangent-Space Methods for Nonlinear Control",
        ),
        (
            "articles/The_Geometry_of_Motion/quarto/volume2.qmd",
            "Volume II: Control Is Motion",
        ),
    }
)


def extract_quarto_navigation_links(quarto_yml_path: Path) -> list[tuple[str, str]]:
    """Extract all (text, href) navigation pairs from navbar, sidebar, and page-footer."""
    config = yaml.safe_load(quarto_yml_path.read_text(encoding="utf-8")) or {}
    website = config.get("website", {})

    def _walk(node: object) -> list[tuple[str, str]]:
        collected: list[tuple[str, str]] = []
        if isinstance(node, dict):
            if "text" in node and "href" in node:
                collected.append((str(node["text"]).strip(), str(node["href"]).strip()))
            for value in node.values():
                collected.extend(_walk(value))
        elif isinstance(node, list):
            for item in node:
                collected.extend(_walk(item))
        return collected

    links: list[tuple[str, str]] = []
    for section_name in ("navbar", "sidebar", "page-footer"):
        links.extend(_walk(website.get(section_name)))
    return links


def test_navigation_labels_match_page_titles_or_allowlist() -> None:
    """Navigation labels in _quarto.yml must match page title or explicit short-form allowlist (#4502)."""
    quarto_yml = REPO_ROOT / "_quarto.yml"
    assert quarto_yml.exists(), "_quarto.yml must exist"

    raw_links = extract_quarto_navigation_links(quarto_yml)
    assert raw_links, "Expected to extract navigation links from _quarto.yml"

    internal_links: list[tuple[str, str]] = [
        (text, href)
        for text, href in raw_links
        if not href.startswith(("http://", "https://", "mailto:", "//"))
        and href.split("#")[0].split("?")[0].endswith((".html", ".qmd"))
    ]
    assert (
        len(internal_links) >= 50
    ), f"Expected at least 50 internal navigation links, got {len(internal_links)}"

    mismatches: list[str] = []
    for text, href in internal_links:
        clean_href = href.split("#")[0].split("?")[0].lstrip("/")
        rel_qmd_str = clean_href.removesuffix(".html").removesuffix(".qmd") + ".qmd"
        source_path = REPO_ROOT / rel_qmd_str
        assert (
            source_path.exists()
        ), f"Navigation link href '{href}' points to non-existent source {source_path}"

        rel_path = source_path.relative_to(REPO_ROOT).as_posix()
        fm, body = split_frontmatter(source_path.read_text(encoding="utf-8"))
        page_title = get_effective_page_title(fm, body)

        if text != page_title and (rel_path, text) not in ALLOWLISTED_NAV_SHORT_FORMS:
            mismatches.append(f"- ({rel_path!r}, nav={text!r}, page_title={page_title!r})")

    assert not mismatches, (
        f"Found {len(mismatches)} navigation label(s) diverging from page title (#4502):\n"
        + "\n".join(mismatches)
    )
