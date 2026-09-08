"""Series navigation contract (issue #3904).

Three reading series gain Quarto sidebar groups (prev/next + breadcrumbs):
the theory series (theory-part1..5 plus the applications appendix and the
foundations monograph), the seven-part tangent-space series, and the Geometry
of Motion volumes. The four isolated geometry articles are wired into the
tangent-space cluster with the canonical Related Articles component, and the
tangent series parts return the links.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
QUARTO_YML = REPO_ROOT / "_quarto.yml"
HUB_QMD = REPO_ROOT / "pages" / "tangent-hyperplanes.qmd"

GEOMETRY_ARTICLES = (
    "superposition",
    "null-space-constraint-jacobian",
    "force-mobility-matrices",
    "degrees-of-freedom-and-dimensionality",
)

TANGENT_PARTS = (
    "part-1-geometry",
    "part-2-dynamics",
    "part-3-control",
    "part-4-residuals-curvature",
    "part-5-contraction",
    "part-6-hybrid",
    "part-7-residual-aware",
)

THEORY_CHAIN = (
    "articles/theory-part1.html",
    "articles/theory-part2.html",
    "articles/theory-part3.html",
    "articles/theory-part4.html",
    "articles/theory-part5.html",
    "articles/appendix-applications.html",
    "articles/affine-nature-golf-swing.html",
)

TANGENT_CHAIN = ("pages/tangent-hyperplanes.html",) + tuple(
    f"articles/tangent-hyperplanes-series/{part}.html" for part in TANGENT_PARTS
)

GEOMETRY_MOTION_CHAIN = (
    "articles/The_Geometry_of_Motion/quarto/volume0.html",
    "articles/The_Geometry_of_Motion/quarto/volume1.html",
    "articles/The_Geometry_of_Motion/quarto/volume2.html",
)


def _sidebar_hrefs(node: object) -> list[str]:
    """Collect hrefs from a sidebar contents tree in declaration order."""
    hrefs: list[str] = []
    if isinstance(node, dict):
        href = node.get("href")
        if isinstance(href, str):
            hrefs.append(href)
        for value in node.values():
            hrefs.extend(_sidebar_hrefs(value))
    elif isinstance(node, list):
        for item in node:
            hrefs.extend(_sidebar_hrefs(item))
    return hrefs


@pytest.fixture(scope="module")
def website() -> dict:
    data = yaml.safe_load(QUARTO_YML.read_text(encoding="utf-8"))
    return data["website"]


@pytest.fixture(scope="module")
def sidebars(website: dict) -> list[dict]:
    return list(website.get("sidebar", []))


class TestSidebarGroups:
    def test_config_parses(self, website: dict) -> None:
        assert website["title"] == "AffineDrift"

    @pytest.mark.parametrize(
        "page",
        [
            *[f"articles/theory-part{n}.html" for n in range(1, 6)],
            "articles/appendix-applications.html",
            "articles/affine-nature-golf-swing.html",
            *[f"articles/tangent-hyperplanes-series/{part}.html" for part in TANGENT_PARTS],
            *[url for url in GEOMETRY_MOTION_CHAIN],
        ],
    )
    def test_series_page_in_exactly_one_sidebar_group(
        self, sidebars: list[dict], page: str
    ) -> None:
        """Each named series page must appear in exactly one ordered sidebar."""
        owners = [sidebar for sidebar in sidebars if page in _sidebar_hrefs(sidebar)]
        assert len(owners) == 1, f"{page} appears in {len(owners)} sidebars"

    @pytest.mark.parametrize(
        ("sidebar_id", "chain"),
        [
            ("theory-nav", THEORY_CHAIN),
            ("tangent-nav", TANGENT_CHAIN),
            ("geometry-motion-nav", GEOMETRY_MOTION_CHAIN),
        ],
    )
    def test_series_sidebar_keeps_reading_order(
        self, sidebars: list[dict], sidebar_id: str, chain: tuple
    ) -> None:
        sidebar = next(s for s in sidebars if s.get("id") == sidebar_id)
        hrefs = _sidebar_hrefs(sidebar)
        positions = [hrefs.index(page) for page in chain]
        assert positions == sorted(positions), f"{sidebar_id} order is not the reading order"

    @pytest.mark.parametrize(
        "page",
        [
            *[f"articles/theory-part{n}.qmd" for n in range(1, 6)],
            "articles/appendix-applications.qmd",
            "articles/affine-nature-golf-swing.qmd",
            *[f"articles/tangent-hyperplanes-series/{part}.qmd" for part in TANGENT_PARTS],
            *[url.replace(".html", ".qmd") for url in GEOMETRY_MOTION_CHAIN],
        ],
    )
    def test_series_page_source_exists(self, page: str) -> None:
        assert (REPO_ROOT / page).exists(), f"missing sidebar target source: {page}"


def _related_articles_section(text: str) -> str:
    """Return the body of the canonical Related Articles section, if present."""
    match = re.search(r"^## Related Articles\s*$", text, flags=re.MULTILINE)
    assert match is not None, "canonical '## Related Articles' section missing"
    rest = text[match.end() :]
    next_heading = re.search(r"^## (?!See Also$)", rest, flags=re.MULTILINE)
    return rest[: next_heading.start()] if next_heading else rest


def _relative_link_targets(section: str) -> list[str]:
    """Return relative .html link targets from a markdown/html fragment."""
    targets = re.findall(r"\]\((?!https?://)([^)#]+\.html)", section)
    targets += re.findall(r'href="(?!(?:https?:)?//)([^"#]+\.html)"', section)
    return targets


def _target_exists(source: Path, target: str) -> bool:
    """A link target resolves when its .qmd source or the target itself exists."""
    resolved = (source.parent / target).resolve()
    return resolved.with_suffix(".qmd").exists() or resolved.exists()


class TestHubWiring:
    @pytest.mark.parametrize("slug", GEOMETRY_ARTICLES)
    def test_hub_links_geometry_article(self, slug: str) -> None:
        text = HUB_QMD.read_text(encoding="utf-8")
        assert re.search(
            rf"\]\(\.\./articles/{re.escape(slug)}\.html", text
        ), f"cluster hub does not link {slug}"


class TestGeometryClusterWiring:
    @pytest.mark.parametrize("slug", GEOMETRY_ARTICLES)
    def test_geometry_article_has_related_articles(self, slug: str) -> None:
        source = REPO_ROOT / "articles" / f"{slug}.qmd"
        section = _related_articles_section(source.read_text(encoding="utf-8"))
        targets = _relative_link_targets(section)
        assert len(targets) >= 3, f"{slug} Related Articles has {len(targets)} outbound links"
        broken = [t for t in targets if not _target_exists(source, t)]
        assert not broken, f"{slug} has broken relative links: {broken}"

    @pytest.mark.parametrize("slug", GEOMETRY_ARTICLES)
    def test_geometry_article_has_non_hub_inbound(self, slug: str) -> None:
        """At least one rendered non-hub page must link to the article."""
        pattern = re.compile(rf"[(<](?:\.\./)*{re.escape(slug)}\.html")
        inbounds = []
        for qmd in REPO_ROOT.rglob("*.qmd"):
            if qmd.name == f"{slug}.qmd" or qmd == HUB_QMD or "_generated" in qmd.parts:
                continue
            if pattern.search(qmd.read_text(encoding="utf-8")):
                inbounds.append(qmd)
        non_hub = [p for p in inbounds if p != HUB_QMD]
        assert non_hub, f"{slug} is only linked from the cluster hub"


class TestTangentReturnLinks:
    @pytest.mark.parametrize("part", TANGENT_PARTS)
    def test_part_links_hub_and_geometry_article(self, part: str) -> None:
        source = REPO_ROOT / "articles" / "tangent-hyperplanes-series" / f"{part}.qmd"
        text = source.read_text(encoding="utf-8")
        assert "tangent-hyperplanes.html" in text, f"{part} does not link the cluster hub"
        geometry_links = [
            slug
            for slug in GEOMETRY_ARTICLES
            if re.search(rf"[(<](?:\.\./)+{re.escape(slug)}\.html", text)
        ]
        assert geometry_links, f"{part} does not link any geometry article"
        for slug in geometry_links:
            assert _target_exists(
                source, f"../{slug}.html"
            ), f"{part} -> {slug}.html target missing"


class TestTheoryChain:
    def test_part5_links_applications_appendix(self) -> None:
        text = (REPO_ROOT / "articles" / "theory-part5.qmd").read_text(encoding="utf-8")
        assert "appendix-applications.html" in text

    def test_applications_appendix_links_chain(self) -> None:
        source = REPO_ROOT / "articles" / "appendix-applications.qmd"
        text = source.read_text(encoding="utf-8")
        assert "theory-part5.html" in text, "appendix-applications must link back to Part 5"
        assert (
            "affine-nature-golf-swing.html" in text
        ), "appendix-applications must link forward to the monograph"

    def test_monograph_links_applications_appendix(self) -> None:
        text = (REPO_ROOT / "articles" / "affine-nature-golf-swing.qmd").read_text(encoding="utf-8")
        assert "appendix-applications.html" in text
