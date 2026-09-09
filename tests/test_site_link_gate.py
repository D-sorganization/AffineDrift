"""Tests for the site link gate (C3 / issue #3899).

The gate validates cross-page internal links, related-articles coverage,
orphan pages, path-style conventions, and controlled category vocabulary
for every rendered content page.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from src.tools.site_link_gate import (
    BASELINE_PATH,
    expand_includes,
    extract_links,
    find_content_pages,
    is_book_chapter,
    load_vocabulary,
    run_site_gate,
)
from src.tools.site_page_scan import CONTENT_DIRS


def write_page(path: Path, body: str, **front: object) -> Path:
    """Write a qmd page with YAML front matter and return its path."""
    fm = yaml.safe_dump(front, sort_keys=False).strip()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{fm}\n---\n\n{body}\n", encoding="utf-8")
    return path


def write_raw_page(path: Path, front_matter: str, body: str) -> Path:
    """Write a qmd page with verbatim front matter text."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{front_matter}\n---\n\n{body}\n", encoding="utf-8")
    return path


@pytest.fixture()
def site(tmp_path: Path) -> Path:
    """A minimal site with articles, a page, a resource, and a book index."""
    write_page(
        tmp_path / "articles" / "alpha.qmd",
        "See [beta](beta.html) and [gamma](../pages/gamma.html).\n",
        title="Alpha",
        categories=["theory-core"],
    )
    write_page(
        tmp_path / "pages" / "gamma.qmd",
        "[back](../articles/alpha.html)\n\n## Related Articles\n\n"
        "::: {.callout-note}\n- [a](../articles/alpha.html)\n"
        "- [b](../articles/beta.html)\n- [c](../pages/gamma.html)\n:::\n",
        title="Gamma",
        categories=["resources"],
    )
    write_page(
        tmp_path / "articles" / "beta.qmd",
        "[alpha](alpha.html)\n\n## Related Articles\n\n"
        "- [x](alpha.html)\n- [y](../pages/gamma.html)\n"
        "- [z](../resources/learning-paths.html)\n",
        title="Beta",
        categories=["theory-core"],
    )
    write_page(
        tmp_path / "resources" / "learning-paths.qmd",
        "[books](../books/index.html)\n",
        title="Learning paths",
        categories=["resources"],
    )
    write_page(tmp_path / "books" / "index.qmd", "[a](alpha.html)\n", title="Books")
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "categories.yml").write_text(
        "theory-core: Core theory\nresources: Learning resources\n"
        "models: Model pages\ntools: Tool pages\n",
        encoding="utf-8",
    )
    return tmp_path


class TestFindContentPages:
    def test_finds_front_matter_pages_in_content_dirs(self, site: Path) -> None:
        pages = {p.relative_to(site) for p in find_content_pages(site)}
        assert pages == {
            Path("articles/alpha.qmd"),
            Path("articles/beta.qmd"),
            Path("pages/gamma.qmd"),
            Path("resources/learning-paths.qmd"),
            Path("books/index.qmd"),
        }

    def test_ignores_pages_without_front_matter(self, site: Path) -> None:
        (site / "articles" / "notes.md").write_text("no front matter\n", encoding="utf-8")
        pages = {p.name for p in find_content_pages(site)}
        assert "notes.md" not in pages


class TestExpandIncludes:
    def test_include_content_resolves_relative_to_includer(self, site: Path) -> None:
        part = site / "articles" / "shared" / "part.qmd"
        part.parent.mkdir(parents=True, exist_ok=True)
        part.write_text("[deep](figures/deep.html)\n", encoding="utf-8")
        figures = site / "articles" / "figures"
        figures.mkdir(exist_ok=True)
        (figures / "deep.html").touch()
        host = site / "articles" / "host.qmd"
        host.write_text(
            "---\ntitle: Host\ncategories: [theory-core]\n---\n\n"
            "{{< include shared/part.qmd >}}\n",
            encoding="utf-8",
        )
        expanded = expand_includes(site, host)
        assert "figures/deep.html" in expanded

    def test_include_cycle_is_safe(self, site: Path) -> None:
        a = site / "articles" / "a.qmd"
        b = site / "articles" / "b.qmd"
        a.write_text("{{< include b.qmd >}}\n", encoding="utf-8")
        b.write_text("{{< include a.qmd >}}\n", encoding="utf-8")
        assert "include" not in expand_includes(site, a)


class TestExtractLinks:
    def test_finds_markdown_and_html_links(self) -> None:
        content = '[text](page.html) ![img](pic.png) <a href="x.html">x</a> ' '<img src="y.png">'
        urls = [link.url for link in extract_links(content)]
        assert urls == ["page.html", "pic.png", "x.html", "y.png"]


class TestPathStyle:
    def test_root_absolute_link_is_rejected(self, site: Path) -> None:
        write_raw_page(
            site / "articles" / "bad.qmd",
            "title: Bad\ncategories:\n- theory-core\n",
            "[a](/pages/gamma.html)\n",
        )
        report = run_site_gate(site, use_baseline=False)
        assert any("root-absolute" in e for e in report["path-style"])

    def test_qmd_extension_link_is_rejected(self, site: Path) -> None:
        write_raw_page(
            site / "articles" / "bad.qmd",
            "title: Bad\ncategories:\n- theory-core\n",
            "[a](gamma.qmd)\n",
        )
        report = run_site_gate(site, use_baseline=False)
        assert any(".qmd" in e for e in report["path-style"])


class TestInternalResolution:
    def test_broken_relative_link_fails(self, site: Path) -> None:
        write_raw_page(
            site / "articles" / "broken.qmd",
            "title: B\ncategories:\n- theory-core\n",
            "[x](missing.html)\n",
        )
        report = run_site_gate(site, use_baseline=False)
        assert any("missing.html" in e for e in report["broken-links"])

    def test_broken_link_inside_include_is_caught(self, site: Path) -> None:
        (site / "articles" / "part.qmd").write_text("[x](nope/missing.html)\n", encoding="utf-8")
        write_raw_page(
            site / "articles" / "host2.qmd",
            "title: H\ncategories:\n- theory-core\n",
            "{{< include part.qmd >}}\n",
        )
        report = run_site_gate(site, use_baseline=False)
        assert any("nope/missing.html" in e for e in report["broken-links"])


class TestRelatedCoverage:
    def test_missing_related_section_fails(self, site: Path) -> None:
        report = run_site_gate(site, use_baseline=False)
        assert any(e.startswith("articles/alpha.qmd") for e in report["related-coverage"])

    def test_undersized_related_section_fails(self, site: Path) -> None:
        page = site / "resources" / "learning-paths.qmd"
        body = page.read_text(encoding="utf-8")
        page.write_text(
            body + "## Related Articles\n\n- [one](../articles/alpha.html)\n",
            encoding="utf-8",
        )
        report = run_site_gate(site, use_baseline=False)
        assert any(e.startswith("resources/learning-paths.qmd") for e in report["related-coverage"])

    def test_book_chapter_is_exempt(self, site: Path) -> None:
        chapter = site / "articles" / "The_Physics_of_Golf" / "chapters" / "ch01.qmd"
        write_page(chapter, "[x](../alpha.html)\n", title="Chapter 1")
        report = run_site_gate(site, use_baseline=False)
        assert not any("The_Physics_of_Golf" in e for e in report["related-coverage"])

    def test_index_pages_are_exempt(self, site: Path) -> None:
        report = run_site_gate(site, use_baseline=False)
        assert not any(e.startswith("books/index.qmd") for e in report["related-coverage"])


class TestOrphans:
    def test_unreferenced_page_fails(self, site: Path) -> None:
        write_page(
            site / "articles" / "lonely.qmd",
            "[alpha](alpha.html)\n\n## Related Articles\n\n- [a](alpha.html)\n"
            "- [b](beta.html)\n- [c](../pages/gamma.html)\n",
            title="Lonely",
            categories=["theory-core"],
        )
        report = run_site_gate(site, use_baseline=False)
        assert "articles/lonely.qmd" in report["orphans"]

    def test_nav_reference_prevents_orphan(self, site: Path) -> None:
        write_page(
            site / "pages" / "nav-only.qmd",
            "[alpha](../articles/alpha.html)\n",
            title="Nav",
            categories=["resources"],
        )
        (site / "_quarto.yml").write_text(
            "website:\n  navbar:\n    left:\n      - text: Nav\n"
            "        href: pages/nav-only.html\n",
            encoding="utf-8",
        )
        report = run_site_gate(site, use_baseline=False)
        assert "pages/nav-only.qmd" not in report["orphans"]

    def test_index_page_is_exempt(self, site: Path) -> None:
        report = run_site_gate(site, use_baseline=False)
        assert "books/index.qmd" not in report["orphans"]


class TestCategories:
    def test_unknown_category_fails(self, site: Path) -> None:
        write_raw_page(
            site / "articles" / "beta.qmd",
            "title: Beta\ncategories:\n- golf\n- theory-core\n",
            "[alpha](alpha.html)\n",
        )
        report = run_site_gate(site, use_baseline=False)
        assert any("golf" in e for e in report["categories"])

    def test_missing_categories_fail(self, site: Path) -> None:
        write_page(
            site / "models" / "m1.qmd",
            "[alpha](../articles/alpha.html)\n",
            title="M1",
        )
        report = run_site_gate(site, use_baseline=False)
        assert any(e.startswith("models/m1.qmd") for e in report["categories"])

    def test_inline_list_syntax_is_rejected(self, site: Path) -> None:
        write_raw_page(
            site / "models" / "m2.qmd",
            "title: M2\ncategories: [models, tools]\n",
            "[alpha](../articles/alpha.html)\n",
        )
        report = run_site_gate(site, use_baseline=False)
        assert any(e.startswith("models/m2.qmd") for e in report["categories"])


class TestBaseline:
    def test_baseline_suppresses_known_failures(self, site: Path) -> None:
        report = run_site_gate(site, use_baseline=True)
        # No baseline file exists in the fixture, so nothing is suppressed.
        assert report["related-coverage"]

    def test_baseline_entries_filter(self, site: Path, tmp_path: Path) -> None:
        baseline = {"related-coverage": ["articles/alpha.qmd: missing Related Articles section"]}
        path = tmp_path / "baseline.json"
        path.write_text(json.dumps(baseline), encoding="utf-8")
        report = run_site_gate(site, baseline_path=path)
        assert not any(e.startswith("articles/alpha.qmd") for e in report["related-coverage"])
        assert any(e.startswith("resources/learning-paths.qmd") for e in report["related-coverage"])

    def test_default_baseline_path_is_in_tests(self) -> None:
        assert BASELINE_PATH.as_posix() == "tests/link_gate_baseline.json"


class TestVocabulary:
    def test_vocabulary_ships_with_repo(self) -> None:
        vocabulary = load_vocabulary(Path("."))
        assert "theory-core" in vocabulary
        assert all(isinstance(v, str) for v in vocabulary.values())


class TestBookChapterClassification:
    @pytest.mark.parametrize(
        "rel",
        [
            "articles/The_Physics_of_Golf/chapters/ch01.qmd",
            "articles/The_Geometry_of_Motion/Volume_I/intro.qmd",
            "articles/proximal_distal_companion/chapters/ch01.qmd",
        ],
    )
    def test_chapters(self, rel: str) -> None:
        assert is_book_chapter(Path(rel)) is True

    @pytest.mark.parametrize(
        "rel",
        ["articles/alpha.qmd", "pages/tools.qmd", "books/index.qmd"],
    )
    def test_non_chapters(self, rel: str) -> None:
        assert is_book_chapter(Path(rel)) is False


def test_content_dirs_constant() -> None:
    assert CONTENT_DIRS == (
        "articles",
        "pages",
        "resources",
        "models",
        "repositories",
        "books",
    )
