"""Site link gate: cross-page link validation for the linking program.

Implements the C3 gate (issue #3899) on top of the shared link utilities:

- include-aware internal link resolution (``{{< include >}}`` content is
  checked with links resolving relative to the *including* page),
- Related Articles coverage (canonical component from #3897),
- orphan detection (in-degree from content pages, nav, or index pages),
- path-style normalization (bare/parent-relative ``.html`` only),
- controlled category vocabulary validation (C2 / issue #3898).

Known, pre-existing violations live in a committed baseline
(``tests/link_gate_baseline.json``) so the gate fails on every *new*
defect while the historical backlog is worked down.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from src.tools.site_page_scan import (
    CONTENT_DIRS,
    _resolve_target,
    _target_exists,
    Link,
    expand_includes,
    extract_links,
    find_content_pages,
    is_book_chapter,
    is_external_url,
    is_rendered,
    page_body,
    parse_front_matter,
    rendered_relative_paths,
    strip_code,
)
from src.tools.utils.link_utils import normalize_internal_url

logger = logging.getLogger(__name__)

VOCABULARY_PATH = Path("config/categories.yml")
BASELINE_PATH = Path("tests/link_gate_baseline.json")
NAV_FILE = "_quarto.yml"
RELATED_MIN_LINKS = 3
HEADING_SPLIT_PATTERN = re.compile(r"^##\s", re.MULTILINE)
INLINE_CATEGORIES_PATTERN = re.compile(r"^categories:\s*\[", re.MULTILINE)


def check_path_style(root: Path, pages: list[Path]) -> list[str]:
    """Reject root-absolute and .qmd-extension internal links."""
    errors: list[str] = []
    for page in pages:
        expanded = strip_code(expand_includes(root, page))
        for link in extract_links(page_body(expanded)):
            url = link.url
            if is_external_url(url) or url.startswith("#"):
                continue
            if url.startswith("/"):
                errors.append(f"{_rel(root, page)}: root-absolute link '{url}'")
            elif url.endswith(".qmd"):
                errors.append(f"{_rel(root, page)}: .qmd link extension '{url}'")
    return errors


def check_internal_links(root: Path, pages: list[Path]) -> list[str]:
    """Validate that every internal relative link resolves."""
    errors: list[str] = []
    for page in pages:
        expanded = strip_code(expand_includes(root, page))
        for link in extract_links(page_body(expanded)):
            target = _resolve_target(root, page, link.url)
            if target is None:
                continue
            if not _target_exists(root, target):
                errors.append(f"{_rel(root, page)}: broken link '{link.url}'")
    return errors


def _related_section(content: str) -> str | None:
    body = page_body(content)
    marker = body.find("## Related Articles")
    if marker == -1:
        return None
    section = body[marker:]
    next_heading = HEADING_SPLIT_PATTERN.search(section[1:])
    if next_heading:
        section = section[: next_heading.start() + 1]
    return section


def _related_errors_for_page(root: Path, page: Path, expanded: str) -> str | None:
    section = _related_section(expanded)
    if section is None:
        return f"{_rel(root, page)}: missing Related Articles section"
    resolving = 0
    for link in extract_links(section):
        target = _resolve_target(root, page, link.url)
        if target is not None and _target_exists(root, target):
            resolving += 1
    if resolving < RELATED_MIN_LINKS:
        return (
            f"{_rel(root, page)}: related section has {resolving} resolving "
            f"links (<{RELATED_MIN_LINKS})"
        )
    return None


def check_related_coverage(root: Path, pages: list[Path]) -> list[str]:
    """Require the canonical Related Articles component on content pages.

    Book chapters and index/hub pages are exempt.
    """
    errors: list[str] = []
    for page in pages:
        rel = _rel(root, page)
        if is_book_chapter(rel) or page.name == "index.qmd":
            continue
        expanded = expand_includes(root, page)
        error = _related_errors_for_page(root, page, expanded)
        if error:
            errors.append(error)
    return errors


def _nav_targets(root: Path) -> set[Path]:
    """Collect content pages referenced from _quarto.yml navigation."""
    nav = root / NAV_FILE
    targets: set[Path] = set()
    if not nav.is_file():
        return targets
    try:
        data = yaml.safe_load(nav.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        logger.warning("Could not parse %s: %s", NAV_FILE, exc)
        return targets

    def _walk(node: object) -> None:
        if isinstance(node, dict):
            href = node.get("href")
            if isinstance(href, str) and href.endswith(".html"):
                candidate = root / href.replace(".html", ".qmd")
                if candidate.exists():
                    targets.add(candidate)
            for value in node.values():
                _walk(value)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(data)
    return targets


def check_orphans(root: Path, pages: list[Path]) -> list[str]:
    """Flag rendered pages with in-degree 0 from content pages or nav.

    Index/hub pages are exempt: they are the site's entry points.
    """

    def _norm(path: Path) -> Path:
        try:
            return path.resolve()
        except OSError:
            return path

    in_degree: dict[Path, int] = {_norm(page): 0 for page in pages}
    for page in pages:
        expanded = strip_code(expand_includes(root, page))
        for link in extract_links(page_body(expanded)):
            target = _resolve_target(root, page, link.url)
            if target is None:
                continue
            source = target.with_suffix(".qmd") if target.suffix == ".html" else target
            source = _norm(source)
            if source in in_degree and source != _norm(page):
                in_degree[source] += 1
    nav_targets = {_norm(target) for target in _nav_targets(root)}
    orphans = [
        _rel(root, page)
        for page in pages
        if in_degree[_norm(page)] == 0
        and _norm(page) not in nav_targets
        and page.name != "index.qmd"
    ]
    return sorted(orphans)


def load_vocabulary(root: Path) -> dict[str, str]:
    """Load the controlled category vocabulary (category -> description)."""
    path = root / VOCABULARY_PATH
    if not path.is_file():
        raise FileNotFoundError(f"Category vocabulary missing: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {str(key): str(value) for key, value in data.items()}


def check_categories(root: Path, pages: list[Path]) -> list[str]:
    """Validate front-matter categories against the controlled vocabulary.

    Book chapters are exempt (they join via #3905); every other rendered
    content page must carry a non-empty block-list ``categories:`` whose
    values are all known.
    """
    vocabulary = load_vocabulary(root)
    errors: list[str] = []
    for page in pages:
        rel = _rel(root, page)
        if is_book_chapter(rel):
            continue
        text = page.read_text(encoding="utf-8", errors="ignore")
        front = parse_front_matter(text)
        categories = front.get("categories")
        if categories is None or categories == []:
            errors.append(f"{rel}: missing categories front matter")
            continue
        if INLINE_CATEGORIES_PATTERN.search(text[: text.find("\n---", 3) + 4]):
            errors.append(f"{rel}: inline categories list; use YAML block list")
        if not isinstance(categories, list):
            errors.append(f"{rel}: categories must be a YAML block list")
            continue
        unknown = [value for value in categories if str(value) not in vocabulary]
        for value in unknown:
            errors.append(f"{rel}: unknown category '{value}'")
    return errors


def _rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def load_baseline(path: Path) -> dict[str, list[str]]:
    """Load the committed baseline of known gate violations."""
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {str(k): [str(v) for v in values] for k, values in data.items()}


def run_site_gate(
    root: Path,
    baseline_path: Path | None = None,
    use_baseline: bool = True,
) -> dict[str, list[str]]:
    """Run all site gate checks and return non-baseline errors per check."""
    pages = find_content_pages(root)
    report: dict[str, list[str]] = {
        "broken-links": check_internal_links(root, pages),
        "path-style": check_path_style(root, pages),
        "related-coverage": check_related_coverage(root, pages),
        "orphans": check_orphans(root, pages),
        "categories": check_categories(root, pages),
    }
    if not use_baseline:
        return report
    baseline_path = baseline_path or root / BASELINE_PATH
    baseline = load_baseline(baseline_path)
    for check, entries in baseline.items():
        known = set(entries)
        report[check] = [entry for entry in report.get(check, []) if entry not in known]
    return report