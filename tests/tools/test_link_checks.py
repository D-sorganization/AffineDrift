"""Tests for source-level site link checks (issue #3899).

Each check is exercised against small fixture trees: include-aware internal
link resolution, path-style normalization, related-coverage, and orphan
detection, plus the budget-config behavior of run_source_checks().
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from src.tools.check_links import main as check_links_main
from src.tools.utils.link_checks import (
    LinkIssue,
    check_internal_links,
    check_orphans,
    check_path_style,
    check_related_coverage,
    collect_nav_pages,
    rendered_pages,
    run_source_checks,
)

CONFIG_NAME = "link_checker_budget.json"


def _write(path: Path, text: str = "") -> None:
    """Create parent directories and write text to *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _json(config: dict[str, Any]) -> str:
    """Serialize *config* deterministically."""
    return json.dumps(config, indent=2)


def _write_config(
    root: Path,
    *,
    content_globs: list[str] | None = None,
    hubs: list[str] | None = None,
    related_allowlist: list[str] | None = None,
    orphan_allowlist: list[str] | None = None,
    root_abs_allowlist: list[str] | None = None,
    qmd_allowlist: list[str] | None = None,
) -> None:
    """Write a link-checker budget config into *root*/config."""
    config: dict[str, Any] = {
        "content_page_globs": content_globs or ["*.qmd", "articles/*.qmd"],
        "hub_pages": hubs if hubs is not None else ["index.qmd"],
        "related_coverage": {"min_links": 3, "allowlist": related_allowlist or []},
        "orphans": {"allowlist": orphan_allowlist or []},
        "path_style": {
            "root_absolute_allowlist": root_abs_allowlist or [],
            "qmd_extension_allowlist": qmd_allowlist or [],
        },
    }
    _write(root / "config" / CONFIG_NAME, _json(config))


def _quarto_yml(extra_render: str = "") -> str:
    """Return a minimal project render config."""
    return f"""project:
  type: website
  render:
    - "*.qmd"
    - "articles/**/*.qmd"
{extra_render}"""


@pytest.fixture()
def site(tmp_path: Path) -> Path:
    """Minimal rendered site: render config plus one entry page."""
    root = tmp_path
    _write(root / "_quarto.yml", _quarto_yml())
    _write(root / "index.qmd", "# Home\n")
    _write_config(root)
    return root


def _load_cfg(root: Path) -> dict[str, Any]:
    """Load the fixture budget config from *root*."""
    return json.loads((root / "config" / CONFIG_NAME).read_text(encoding="utf-8"))


def _issues_for(check: Any, root: Path) -> list[LinkIssue]:
    """Run one check against the fixture config."""
    return list(check(root, _load_cfg(root)))


class TestIncludeAwareResolution:
    """Internal links in {{< include >}}d files resolve against the includer."""

    def test_include_resolves_against_including_page(self, site: Path) -> None:
        _write(site / "index.qmd", "{{< include chapters/ch03.qmd >}}\n")
        _write(site / "chapters/ch03.qmd", "![fig](figures/fig_a.pdf)\n")
        _write(site / "figures/fig_a.pdf")
        assert _issues_for(check_internal_links, site) == []

    def test_monograph_data_prefix_is_broken(self, site: Path) -> None:
        """#3906 class: data/... prefix never resolves from the including page."""
        _write(site / "articles/monograph/index.qmd", "{{< include chapters/_ch03d.qmd >}}\n")
        chapter = (
            "![fig](data/shoulder_velocity_transfer/figures/"
            "fig_shoulder_velocity_drift_power.pdf){#fig-power}\n"
        )
        _write(site / "articles/monograph/chapters/_ch03d.qmd", chapter)
        _write(site / "articles/monograph/figures/fig_shoulder_velocity_drift_power.pdf")
        issues = _issues_for(check_internal_links, site)
        assert len(issues) == 1
        assert "_ch03d.qmd" in issues[0].file
        assert issues[0].check == "unresolved-internal-link"

    def test_parent_relative_prefix_is_broken(self, site: Path) -> None:
        """#3906 class: ../figures from an included chapter escapes the page."""
        _write(site / "articles/monograph/index.qmd", "{{< include chapters/_ch03b.qmd >}}\n")
        _write(
            site / "articles/monograph/chapters/_ch03b.qmd",
            "![fig](../figures/fig_hand_path.pdf)\n",
        )
        _write(site / "articles/monograph/figures/fig_hand_path.pdf")
        issues = _issues_for(check_internal_links, site)
        assert len(issues) == 1

    def test_missing_include_target_is_broken(self, site: Path) -> None:
        _write(site / "index.qmd", "{{< include chapters/nope.qmd >}}\n")
        issues = _issues_for(check_internal_links, site)
        assert len(issues) == 1
        assert "no_include_target" in issues[0].check

    def test_include_cycle_terminates(self, site: Path) -> None:
        _write(site / "index.qmd", "{{< include a.qmd >}}\n")
        _write(site / "a.qmd", "{{< include b.qmd >}}\n")
        _write(site / "b.qmd", "{{< include a.qmd >}}\n")
        assert _issues_for(check_internal_links, site) == []


class TestPathStyle:
    def test_root_absolute_page_link_rejected(self, site: Path) -> None:
        _write(site / "articles/foo.qmd", "[Overview](/pages/overview.html)\n")
        issues = _issues_for(check_path_style, site)
        assert len(issues) == 1
        assert issues[0].check == "root-absolute-link"

    def test_qmd_extension_rejected(self, site: Path) -> None:
        _write(site / "articles/foo.qmd", "[Other](other-page.qmd)\n")
        issues = _issues_for(check_path_style, site)
        assert len(issues) == 1
        assert issues[0].check == "qmd-extension-link"

    def test_bare_and_parent_relative_html_pass(self, site: Path) -> None:
        _write(site / "articles/foo.qmd", "[A](bar.html) [B](../pages/x.html)\n")
        _write(site / "articles/bar.qmd", "")
        _write(site / "pages/x.qmd", "")
        issues = _issues_for(check_path_style, site)
        assert issues == []

    def test_allowlisted_file_is_exempt(self, site: Path) -> None:
        _write(site / "articles/foo.qmd", "[A](/abs.html) [B](x.qmd)\n")
        cfg = _load_cfg(site)
        cfg["path_style"]["root_absolute_allowlist"] = ["articles/foo.qmd"]
        cfg["path_style"]["qmd_extension_allowlist"] = ["articles/foo.qmd"]
        assert check_path_style(site, cfg) == []


class TestRelatedCoverage:
    def test_missing_component_is_flagged(self, site: Path) -> None:
        _write(site / "articles/foo.qmd", "# Article\n")
        issues = _issues_for(check_related_coverage, site)
        assert [i.file for i in issues] == ["articles/foo.qmd"]
        assert issues[0].check == "related-missing"

    def test_undersized_component_is_flagged(self, site: Path) -> None:
        section = (
            "## Related Articles\n\n"
            "::: {.callout-note}\n## See Also\n\n"
            "- **[One](../pages/one.html)** — a\n"
            "- **[Two](../pages/two.html)** — b\n"
            ":::\n"
        )
        _write(site / "articles/foo.qmd", section)
        _write(site / "pages/one.qmd", "")
        _write(site / "pages/two.qmd", "")
        issues = _issues_for(check_related_coverage, site)
        assert [i.file for i in issues] == ["articles/foo.qmd"]
        assert issues[0].check == "related-undersized"

    def test_canonical_component_passes(self, site: Path) -> None:
        section = (
            "## Related Articles\n\n"
            "::: {.callout-note}\n## See Also\n\n"
            "- **[One](../pages/one.html)** — a\n"
            "- **[Two](../pages/two.html)** — b\n"
            "- **[Three](../pages/three.html)** — c\n"
            ":::\n"
        )
        _write(site / "articles/foo.qmd", section)
        for name in ("one", "two", "three"):
            _write(site / f"pages/{name}.qmd", "")
        assert _issues_for(check_related_coverage, site) == []

    def test_hub_page_is_exempt(self, site: Path) -> None:
        assert check_related_coverage(site, _load_cfg(site)) == []

    def test_allowlisted_page_is_exempt(self, site: Path) -> None:
        _write(site / "articles/foo.qmd", "# Article\n")
        cfg = _load_cfg(site)
        cfg["related_coverage"]["allowlist"] = ["articles/foo.qmd"]
        assert check_related_coverage(site, cfg) == []


class TestOrphans:
    def test_unreachable_page_is_flagged(self, site: Path) -> None:
        _write(site / "articles/lonely.qmd", "# Lonely\n")
        issues = _issues_for(check_orphans, site)
        assert [i.file for i in issues] == ["articles/lonely.qmd"]
        assert issues[0].check == "orphan-page"

    def test_inbound_content_link_clears_orphan(self, site: Path) -> None:
        _write(site / "articles/lonely.qmd", "# Lonely\n")
        _write(site / "index.qmd", "[Lonely](articles/lonely.html)\n")
        assert _issues_for(check_orphans, site) == []

    def test_nav_href_clears_orphan(self, site: Path) -> None:
        _write(site / "articles/lonely.qmd", "# Lonely\n")
        nav = {
            "project": {"type": "website"},
            "website": {"navbar": {"left": [{"href": "articles/lonely.html"}]}},
        }
        _write(site / "_quarto.yml", _json(nav))
        assert collect_nav_pages(site) == {"articles/lonely.qmd"}
        assert _issues_for(check_orphans, site) == []

    def test_include_edge_clears_orphan(self, site: Path) -> None:
        _write(site / "index.qmd", "{{< include articles/ch01.qmd >}}\n")
        _write(site / "articles/ch01.qmd", "# Ch\n")
        assert _issues_for(check_orphans, site) == []

    def test_allowlisted_orphan_is_exempt(self, site: Path) -> None:
        _write(site / "articles/lonely.qmd", "# Lonely\n")
        cfg = _load_cfg(site)
        cfg["orphans"]["allowlist"] = ["articles/lonely.qmd"]
        assert check_orphans(site, cfg) == []


class TestRunSourceChecks:
    def test_clean_tree_returns_zero(self, site: Path) -> None:
        assert run_source_checks(str(site), CONFIG_NAME) == 0

    def test_violation_returns_one(self, site: Path) -> None:
        _write(site / "articles/foo.qmd", "[Broken](nope.html)\n")
        assert run_source_checks(str(site), CONFIG_NAME) == 1

    def test_budgeted_violations_report_only(self, site: Path) -> None:
        _write(site / "articles/foo.qmd", "[A](/pages/abs.html)\n")
        _write(site / "pages/abs.qmd", "")
        _write(site / "index.qmd", "[Foo](articles/foo.html)\n")
        cfg = _load_cfg(site)
        cfg["path_style"]["root_absolute_allowlist"] = ["articles/foo.qmd"]
        cfg["related_coverage"]["allowlist"] = ["articles/foo.qmd"]
        cfg["orphans"]["allowlist"] = ["articles/foo.qmd"]
        _write(site / "config" / CONFIG_NAME, _json(cfg))
        assert run_source_checks(str(site), CONFIG_NAME) == 0


class TestRenderedPages:
    def test_render_globs_and_excludes(self, site: Path) -> None:
        _write(site / "articles/a.qmd", "")
        _write(site / "articles/b.qmd", "")
        _write(site / "_quarto.yml", _quarto_yml('    - "!articles/b.qmd"\n'))
        names = {p.name for p in rendered_pages(site)}
        assert "a.qmd" in names
        assert "b.qmd" not in names


class TestCheckLinksMain:
    def test_source_checks_exit_zero(self, site: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(site)
        assert check_links_main(["--source-checks"]) == 0

    def test_source_checks_exit_one_on_violation(
        self, site: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _write(site / "articles/foo.qmd", "[Broken](nope.html)\n")
        monkeypatch.chdir(site)
        assert check_links_main(["--source-checks"]) == 1
