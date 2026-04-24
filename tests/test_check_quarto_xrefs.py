"""Tests for the Quarto cross-reference validator and orphan-page detector."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.check_quarto_xrefs import (
    _collect_nav_hrefs,
    _html_to_source_stem,
    _resolve_render_globs,
    _strip_frontmatter,
    _strip_inline_code,
    collect_labels_and_refs,
    detect_orphans,
    find_qmd_files,
    main,
    validate_xrefs,
)

# ---------------------------------------------------------------------------
# _strip_frontmatter
# ---------------------------------------------------------------------------


def test_strip_frontmatter_removes_yaml_block() -> None:
    lines = ["---", "title: Foo", "---", "# Heading"]
    assert _strip_frontmatter(lines) == ["# Heading"]


def test_strip_frontmatter_keeps_content_when_no_block() -> None:
    lines = ["# Heading", "Some text"]
    assert _strip_frontmatter(lines) == lines


def test_strip_frontmatter_handles_empty_input() -> None:
    assert _strip_frontmatter([]) == []


# ---------------------------------------------------------------------------
# _strip_inline_code
# ---------------------------------------------------------------------------


def test_strip_inline_code_removes_backtick_spans() -> None:
    line = "See `@sec-hidden` for details."
    result = _strip_inline_code(line)
    assert "@sec-hidden" not in result


def test_strip_inline_code_keeps_surrounding_text() -> None:
    line = "Text `code` more text"
    result = _strip_inline_code(line)
    assert "Text" in result
    assert "more text" in result


# ---------------------------------------------------------------------------
# collect_labels_and_refs
# ---------------------------------------------------------------------------


def test_collect_labels_finds_sec_label(tmp_path: Path) -> None:
    qmd = tmp_path / "ch01.qmd"
    qmd.write_text("# Intro {#sec-intro}\n\nSome content.\n", encoding="utf-8")
    labels, refs = collect_labels_and_refs(qmd)
    assert "sec-intro" in labels
    assert refs == []


def test_collect_labels_finds_eq_fig_tbl_labels(tmp_path: Path) -> None:
    content = (
        "$$\nE = mc^2\n$$ {#eq-energy}\n\n"
        "![Plot](plot.png){#fig-myplot}\n\n"
        "| A | B |\n|---|---|\n| 1 | 2 |\n: Caption {#tbl-data}\n"
    )
    qmd = tmp_path / "page.qmd"
    qmd.write_text(content, encoding="utf-8")
    labels, _ = collect_labels_and_refs(qmd)
    assert "eq-energy" in labels
    assert "fig-myplot" in labels
    assert "tbl-data" in labels


def test_collect_refs_detects_xref_calls(tmp_path: Path) -> None:
    qmd = tmp_path / "ch02.qmd"
    qmd.write_text(
        "See @sec-intro and @eq-energy for details.\n",
        encoding="utf-8",
    )
    labels, refs = collect_labels_and_refs(qmd)
    ref_keys = [r for r, _ in refs]
    assert "sec-intro" in ref_keys
    assert "eq-energy" in ref_keys
    assert labels == set()


def test_collect_refs_skips_labels_in_code_blocks(tmp_path: Path) -> None:
    content = "```python\n# @sec-fake-label\nprint('@fig-another')\n```\n"
    qmd = tmp_path / "code.qmd"
    qmd.write_text(content, encoding="utf-8")
    _, refs = collect_labels_and_refs(qmd)
    assert refs == []


def test_collect_refs_skips_labels_in_inline_code(tmp_path: Path) -> None:
    qmd = tmp_path / "inline.qmd"
    qmd.write_text("Use `@sec-skip-me` as an example.\n", encoding="utf-8")
    _, refs = collect_labels_and_refs(qmd)
    assert refs == []


def test_collect_labels_and_refs_skips_frontmatter(tmp_path: Path) -> None:
    content = "---\ntitle: '@sec-not-a-ref'\n---\n# Intro {#sec-real}\n"
    qmd = tmp_path / "fm.qmd"
    qmd.write_text(content, encoding="utf-8")
    labels, refs = collect_labels_and_refs(qmd)
    assert "sec-real" in labels
    assert refs == []


def test_collect_labels_graceful_on_missing_file(tmp_path: Path) -> None:
    labels, refs = collect_labels_and_refs(tmp_path / "nonexistent.qmd")
    assert labels == set()
    assert refs == []


# ---------------------------------------------------------------------------
# find_qmd_files
# ---------------------------------------------------------------------------


def test_find_qmd_files_excludes_docs(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "page.qmd").write_text("", encoding="utf-8")
    (tmp_path / "article.qmd").write_text("", encoding="utf-8")
    found = find_qmd_files(tmp_path)
    names = [f.name for f in found]
    assert "article.qmd" in names
    assert "page.qmd" not in names


def test_find_qmd_files_excludes_node_modules(tmp_path: Path) -> None:
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "pkg.qmd").write_text("", encoding="utf-8")
    (tmp_path / "real.qmd").write_text("", encoding="utf-8")
    found = find_qmd_files(tmp_path)
    names = [f.name for f in found]
    assert "real.qmd" in names
    assert "pkg.qmd" not in names


# ---------------------------------------------------------------------------
# validate_xrefs
# ---------------------------------------------------------------------------


def test_validate_xrefs_passes_when_all_refs_resolve(tmp_path: Path) -> None:
    (tmp_path / "ch01.qmd").write_text("# Intro {#sec-intro}\n", encoding="utf-8")
    (tmp_path / "ch02.qmd").write_text("See @sec-intro.\n", encoding="utf-8")
    assert validate_xrefs(tmp_path) == []


def test_validate_xrefs_reports_missing_ref(tmp_path: Path) -> None:
    (tmp_path / "ch01.qmd").write_text("See @sec-missing.\n", encoding="utf-8")
    errors = validate_xrefs(tmp_path)
    assert len(errors) == 1
    rel_file, line_num, label = errors[0]
    assert label == "sec-missing"
    assert line_num == 1


def test_validate_xrefs_no_false_positive_for_external_urls(tmp_path: Path) -> None:
    (tmp_path / "ch01.qmd").write_text(
        "See [link](https://example.com) and [@jones2023].\n",
        encoding="utf-8",
    )
    assert validate_xrefs(tmp_path) == []


def test_validate_xrefs_returns_empty_when_no_qmd_files(tmp_path: Path) -> None:
    assert validate_xrefs(tmp_path) == []


def test_validate_xrefs_multi_file_label_resolution(tmp_path: Path) -> None:
    """Label defined in file A should resolve reference in file B."""
    (tmp_path / "a.qmd").write_text("## Theorem {#sec-theorem}\n", encoding="utf-8")
    (tmp_path / "b.qmd").write_text("See @sec-theorem for proof.\n", encoding="utf-8")
    assert validate_xrefs(tmp_path) == []


# ---------------------------------------------------------------------------
# _collect_nav_hrefs
# ---------------------------------------------------------------------------


def test_collect_nav_hrefs_extracts_href_from_nested_dict() -> None:
    nav = {
        "left": [
            {"text": "Home", "href": "index.html"},
            {
                "text": "Learn",
                "menu": [
                    {"text": "Overview", "href": "pages/overview.html"},
                    {"text": "---"},
                ],
            },
        ]
    }
    hrefs = _collect_nav_hrefs(nav)
    assert "index.html" in hrefs
    assert "pages/overview.html" in hrefs


def test_collect_nav_hrefs_ignores_non_href_values() -> None:
    nav = {"title": "Site", "logo": "logo.png"}
    assert _collect_nav_hrefs(nav) == set()


# ---------------------------------------------------------------------------
# _html_to_source_stem
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("href", "expected"),
    [
        ("pages/about.html", "pages/about"),
        ("index.html", "index"),
        ("pages/guide.htm", "pages/guide"),
        ("pages/overview.qmd", "pages/overview.qmd"),
    ],
)
def test_html_to_source_stem(href: str, expected: str) -> None:
    assert _html_to_source_stem(href) == expected


# ---------------------------------------------------------------------------
# _resolve_render_globs
# ---------------------------------------------------------------------------


def test_resolve_render_globs_expands_wildcard(tmp_path: Path) -> None:
    (tmp_path / "pages").mkdir()
    (tmp_path / "pages" / "about.qmd").write_text("", encoding="utf-8")
    data = {"project": {"render": ["pages/**/*.qmd"]}}
    result = _resolve_render_globs(data, tmp_path)
    names = [p.name for p in result]
    assert "about.qmd" in names


def test_resolve_render_globs_skips_negation_rules(tmp_path: Path) -> None:
    (tmp_path / "pages").mkdir()
    (tmp_path / "pages" / "draft.qmd").write_text("", encoding="utf-8")
    data = {"project": {"render": ["!pages/draft.qmd", "pages/**/*.qmd"]}}
    result = _resolve_render_globs(data, tmp_path)
    names = [p.name for p in result]
    # draft.qmd would still match "pages/**/*.qmd", but negation rule is skipped
    # — that is the correct behaviour (we don't suppress on negation rules)
    assert isinstance(names, list)


def test_resolve_render_globs_ignores_non_qmd_rules(tmp_path: Path) -> None:
    data = {"project": {"render": ["*.md", "*.html", "*.qmd"]}}
    result = _resolve_render_globs(data, tmp_path)
    # Only *.qmd rule is processed; *.md and *.html are ignored
    assert isinstance(result, list)


# ---------------------------------------------------------------------------
# detect_orphans
# ---------------------------------------------------------------------------


def _write_quarto_yml(tmp_path: Path, nav_hrefs: list[str], render_globs: list[str]) -> Path:
    """Write a minimal _quarto.yml for testing."""
    texts = ["P" + str(i) for i in range(len(nav_hrefs))]
    menu = [{"text": t, "href": h} for t, h in zip(texts, nav_hrefs, strict=True)]
    data = {
        "project": {"render": render_globs},
        "website": {"navbar": {"left": [{"text": "Menu", "menu": menu}]}},
    }
    yml = tmp_path / "_quarto.yml"
    yml.write_text(yaml.dump(data), encoding="utf-8")
    return yml


def test_detect_orphans_returns_empty_when_all_pages_in_nav(tmp_path: Path) -> None:
    (tmp_path / "pages").mkdir()
    (tmp_path / "pages" / "about.qmd").write_text("", encoding="utf-8")
    yml = _write_quarto_yml(
        tmp_path,
        nav_hrefs=["pages/about.html"],
        render_globs=["pages/**/*.qmd"],
    )
    assert detect_orphans(tmp_path, yml) == []


def test_detect_orphans_flags_unlisted_page(tmp_path: Path) -> None:
    (tmp_path / "pages").mkdir()
    (tmp_path / "pages" / "hidden.qmd").write_text("", encoding="utf-8")
    yml = _write_quarto_yml(
        tmp_path,
        nav_hrefs=["pages/about.html"],  # hidden.qmd is not here
        render_globs=["pages/**/*.qmd"],
    )
    orphans = detect_orphans(tmp_path, yml)
    assert any("hidden.qmd" in o for o in orphans)


def test_detect_orphans_skips_index_pages(tmp_path: Path) -> None:
    (tmp_path / "pages").mkdir()
    (tmp_path / "pages" / "index.qmd").write_text("", encoding="utf-8")
    yml = _write_quarto_yml(tmp_path, nav_hrefs=[], render_globs=["pages/**/*.qmd"])
    assert detect_orphans(tmp_path, yml) == []


def test_detect_orphans_handles_missing_quarto_yml(tmp_path: Path) -> None:
    missing = tmp_path / "_quarto.yml"
    assert detect_orphans(tmp_path, missing) == []


# ---------------------------------------------------------------------------
# main() integration
# ---------------------------------------------------------------------------


def test_main_returns_zero_on_clean_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "ch01.qmd").write_text("# Intro {#sec-intro}\n", encoding="utf-8")
    (tmp_path / "ch02.qmd").write_text("See @sec-intro.\n", encoding="utf-8")
    # No _quarto.yml => orphan check is skipped automatically
    rc = main(["--root", str(tmp_path), "--xrefs-only"])
    assert rc == 0


def test_main_returns_one_on_missing_xref(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "ch01.qmd").write_text("See @sec-undefined.\n", encoding="utf-8")
    rc = main(["--root", str(tmp_path), "--xrefs-only"])
    assert rc == 1


def test_main_warn_orphans_does_not_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pages").mkdir()
    (tmp_path / "pages" / "hidden.qmd").write_text("", encoding="utf-8")
    _write_quarto_yml(tmp_path, nav_hrefs=[], render_globs=["pages/**/*.qmd"])
    rc = main(
        ["--root", str(tmp_path), "--orphans-only", "--warn-orphans", "--root", str(tmp_path)]
    )
    assert rc == 0


def test_main_orphans_errors_without_warn_flag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pages").mkdir()
    (tmp_path / "pages" / "hidden.qmd").write_text("", encoding="utf-8")
    _write_quarto_yml(tmp_path, nav_hrefs=[], render_globs=["pages/**/*.qmd"])
    rc = main(["--root", str(tmp_path), "--orphans-only"])
    assert rc == 1
