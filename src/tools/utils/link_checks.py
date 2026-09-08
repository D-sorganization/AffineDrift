"""Source-level site link checks for rendered Quarto pages (issue #3899).

Four checks run over the rendered source set declared by the root
``_quarto.yml``:

1. ``check_internal_links`` — every relative ``.html``/``.qmd``/asset link
   must resolve. Links inside ``{{< include >}}``d files resolve against
   the *including* page (the #3906 monograph defect class).
2. ``check_path_style`` — cross-page links must use the bare/parent-relative
   ``.html`` convention; root-absolute and ``.qmd`` targets are rejected.
3. ``check_related_coverage`` — every content page (excluding book-chapter
   interiors and hub pages) carries the canonical Related Articles component
   with at least ``min_links`` resolving page links.
4. ``check_orphans`` — every rendered page has in-degree >= 1 from content
   pages, navigation (``_quarto.yml``), or index/hub pages.

Known baseline violations are budgeted through
``config/link_checker_budget.json`` (the repository's standard budget
mechanism); violations outside the budget fail the check.

Design by Contract:
    - Public checks take a project root and a parsed config mapping and are
      deterministic and side-effect free.
    - Exit-code semantics: ``0`` = pass, ``1`` = violations beyond budget
      (documented in ``docs/LINK-CHECKER.md``).
"""

from __future__ import annotations

import logging
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.tools.utils.budget_check_utils import load_config, report_results
from src.tools.utils.link_utils import (
    INCLUDE_SHORTCODE_PATTERN,
    RELATED_HEADING_PATTERN,
    extract_related_section_links,
    find_include_paths,
    find_links,
    internal_link_resolvable,
    normalize_internal_url,
    page_key_for_target,
    page_target_key,
)
from src.tools.utils.site_config_utils import (
    collect_nav_pages,
    load_render_patterns,
)

logger = logging.getLogger(__name__)

#: Default budget config under ``config/``
DEFAULT_CONFIG_NAME = "link_checker_budget.json"

#: Fallback content-page universe when the config declares none
DEFAULT_CONTENT_GLOBS: tuple[str, ...] = ("*.qmd", "articles/*.qmd")

#: Fallback hub pages exempt from related coverage and the orphan gate
DEFAULT_HUB_PAGES: tuple[str, ...] = ("index.qmd",)

#: Suffixes whose link targets must obey the page-link path convention
PAGE_LINK_SUFFIXES: tuple[str, ...] = (".html", ".qmd")

#: Suffixes counted as resolving page links in Related Articles sections
RELATED_PAGE_SUFFIXES: tuple[str, ...] = (".html", ".qmd", ".md")


@dataclass(frozen=True)
class LinkIssue:
    """A single link-quality violation.

    Attributes:
        file: Root-relative POSIX path of the offending file.
        line: 1-based line number (``0`` when not tied to a line).
        url: The raw link text as written in the source.
        check: Machine-readable check name that produced the issue.
        detail: Human-readable explanation appended to reports.
    """

    file: str
    line: int
    url: str
    check: str
    detail: str = ""


def _read_text(path: Path) -> str:
    """Read text defensively, returning an empty string on failure."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:  # pragma: no cover - defensive
        logger.warning("Could not read %s: %s", path, exc)
        return ""


def _rel(root: Path, path: Path) -> str:
    """Return *path* relative to *root* as a POSIX string."""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return Path(os.path.relpath(path.resolve(), root.resolve())).as_posix()


def rendered_pages(root: Path) -> list[Path]:
    """Return the rendered source pages declared by ``_quarto.yml``.

    Args:
        root: The project root directory.

    Returns:
        Sorted list of existing source page paths.
    """
    patterns = load_render_patterns(root)
    pages: set[Path] = set()
    for pattern in patterns.includes:
        pages.update(p for p in root.glob(pattern) if p.is_file())
    for pattern in patterns.excludes:
        pages.difference_update(p for p in root.glob(pattern) if p.is_file())
    return sorted(pages)


def include_units(page: Path) -> list[tuple[Path, Path]]:
    """Return scan units for *page*: the page plus its included files.

    Args:
        page: A rendered source page.

    Returns:
        ``(file, including_page)`` pairs; links in ``file`` resolve against
        ``including_page``'s directory (include-aware semantics).
    """
    units: list[tuple[Path, Path]] = [(page, page)]
    for include in find_include_paths(_read_text(page)):
        target = (page.parent / include).resolve()
        if target.exists():
            units.append((target, page))
    return units


def _include_line(text: str, target: str) -> int:
    """Return the 1-based line of the include shortcode for *target*."""
    for number, line in enumerate(text.splitlines(), start=1):
        if target in line and INCLUDE_SHORTCODE_PATTERN.search(line):
            return number
    return 0


def _unique(issues: list[LinkIssue]) -> list[LinkIssue]:
    """Collapse duplicate issues, preferring entries with context detail."""
    best: dict[tuple[str, int, str, str], LinkIssue] = {}
    for issue in issues:
        key = (issue.file, issue.line, issue.url, issue.check)
        if key not in best or (not best[key].detail and issue.detail):
            best[key] = issue
    return list(best.values())


def check_internal_links(root: Path, config: dict[str, Any]) -> list[LinkIssue]:
    """Validate every internal link in rendered sources (include-aware).

    Args:
        root: The project root directory.
        config: Parsed budget config (reserved; broken links are unbudgeted).

    Returns:
        Issues for unresolved links and missing include targets.
    """
    del config
    issues: list[LinkIssue] = []
    for page in rendered_pages(root):
        text = _read_text(page)
        for include in find_include_paths(text):
            if not (page.parent / include).resolve().exists():
                issues.append(
                    LinkIssue(
                        _rel(root, page),
                        _include_line(text, include),
                        include,
                        "no_include_target",
                        "include target does not exist",
                    )
                )
        for unit_file, base in include_units(page):
            for url, line in find_links(unit_file):
                normalized = normalize_internal_url(url)
                if normalized is None:
                    continue
                if not internal_link_resolvable(root=root, source_file=base, url=normalized):
                    context = "" if base == unit_file else f"included by {_rel(root, base)}"
                    issues.append(
                        LinkIssue(
                            _rel(root, unit_file),
                            line,
                            url,
                            "unresolved-internal-link",
                            context,
                        )
                    )
    return _unique(issues)


def check_path_style(root: Path, config: dict[str, Any]) -> list[LinkIssue]:
    """Enforce the bare/parent-relative ``.html`` link convention.

    Args:
        root: The project root directory.
        config: Parsed budget config; ``path_style`` allowlists are keyed
            by root-relative file path.

    Returns:
        Issues for root-absolute and ``.qmd`` page links outside the
        configured allowlists.
    """
    settings = config.get("path_style", {})
    root_allow = set(settings.get("root_absolute_allowlist", []))
    qmd_allow = set(settings.get("qmd_extension_allowlist", []))
    issues: list[LinkIssue] = []
    for page in rendered_pages(root):
        for unit_file, _base in include_units(page):
            file_key = _rel(root, unit_file)
            for url, line in find_links(unit_file):
                normalized = normalize_internal_url(url)
                if normalized is None or not normalized.endswith(PAGE_LINK_SUFFIXES):
                    continue
                if normalized.startswith("/") and file_key not in root_allow:
                    issues.append(LinkIssue(file_key, line, url, "root-absolute-link"))
                if normalized.endswith(".qmd") and file_key not in qmd_allow:
                    issues.append(LinkIssue(file_key, line, url, "qmd-extension-link"))
    return _unique(issues)


def _resolving_related_links(root: Path, page: Path, urls: list[str]) -> int:
    """Count page links in *urls* that resolve from *page*."""
    count = 0
    for raw in urls:
        normalized = normalize_internal_url(raw)
        if normalized is None or not normalized.endswith(RELATED_PAGE_SUFFIXES):
            continue
        if page_target_key(root=root, source_file=page, url=normalized):
            count += 1
    return count


def check_related_coverage(root: Path, config: dict[str, Any]) -> list[LinkIssue]:
    """Require the canonical Related Articles component on content pages.

    Book-chapter interiors are excluded by construction (the content
    universe is declared by ``content_page_globs``); hub pages and
    allowlisted pages are budgeted via config.

    Args:
        root: The project root directory.
        config: Parsed budget config with ``related_coverage`` settings.

    Returns:
        Issues for missing components and undersized sections.
    """
    settings = config.get("related_coverage", {})
    min_links = int(settings.get("min_links", 3))
    allowlist = set(settings.get("allowlist", []))
    globs = config.get("content_page_globs", DEFAULT_CONTENT_GLOBS)
    hubs = set(config.get("hub_pages", DEFAULT_HUB_PAGES))
    issues: list[LinkIssue] = []
    for pattern in globs:
        for page in sorted(root.glob(pattern)):
            if not page.is_file():
                continue
            key = _rel(root, page)
            if key in hubs or key in allowlist:
                continue
            text = _read_text(page)
            resolving = _resolving_related_links(root, page, extract_related_section_links(text))
            if not RELATED_HEADING_PATTERN.search(text):
                issues.append(
                    LinkIssue(key, 0, "", "related-missing", "no Related Articles section")
                )
            elif resolving < min_links:
                issues.append(
                    LinkIssue(
                        key,
                        0,
                        "",
                        "related-undersized",
                        f"{resolving} resolving links (min {min_links})",
                    )
                )
    return issues


def _include_keys(root: Path, page: Path, keys: set[str]) -> set[str]:
    """Return rendered-page keys reached via ``{{< include >}}`` edges."""
    reached: set[str] = set()
    for include in find_include_paths(_read_text(page)):
        target = (page.parent / include).resolve()
        if not target.exists():
            continue
        key = page_key_for_target(root=root, target=target)
        if key is None:
            key = _rel(root, target)
        if key in keys:
            reached.add(key)
    return reached


def check_orphans(root: Path, config: dict[str, Any]) -> list[LinkIssue]:
    """Detect rendered pages with in-degree 0 from content, nav, or hubs.

    Args:
        root: The project root directory.
        config: Parsed budget config with ``orphans.allowlist`` and
            ``hub_pages`` (hubs are graph roots, always in-degree >= 1).

    Returns:
        One issue per un-budgeted orphan page.
    """
    settings = config.get("orphans", {})
    allowlist = set(settings.get("allowlist", []))
    hubs = set(config.get("hub_pages", DEFAULT_HUB_PAGES))
    pages = rendered_pages(root)
    keys = {_rel(root, page) for page in pages}
    in_degree: Counter[str] = Counter()
    for page in pages:
        in_degree.update(_include_keys(root, page, keys))
        for unit_file, base in include_units(page):
            for url, _line in find_links(unit_file):
                normalized = normalize_internal_url(url)
                if normalized is None:
                    continue
                key = page_target_key(root=root, source_file=base, url=normalized)
                if key:
                    in_degree[key] += 1
    orphans = sorted(keys - set(in_degree) - collect_nav_pages(root) - allowlist - hubs)
    return [
        LinkIssue(key, 0, "", "orphan-page", "no inbound content or nav link") for key in orphans
    ]


def run_source_checks(root_dir: str, config_name: str = DEFAULT_CONFIG_NAME) -> int:
    """Run all source-level link checks and return the CI exit code.

    Args:
        root_dir: The project root directory.
        config_name: Budget config name resolved under ``<root>/config/``.

    Returns:
        ``0`` when no unbudgeted violations exist, ``1`` otherwise.
    """
    root = Path(root_dir).resolve()
    config = load_config(root, config_name)
    pages = rendered_pages(root)
    results: dict[str, list[LinkIssue]] = {
        "internal-links": check_internal_links(root, config),
        "path-style": check_path_style(root, config),
        "related-coverage": check_related_coverage(root, config),
        "orphans": check_orphans(root, config),
    }
    details = [f"{name}: {len(issues)} violation(s)" for name, issues in results.items()]
    errors = [
        f"{issue.file}:{issue.line} [{issue.check}] {issue.url} {issue.detail}".rstrip()
        for issues in results.values()
        for issue in issues
    ]
    return report_results("Site link quality checks (issue #3899)", len(pages), details, errors)
