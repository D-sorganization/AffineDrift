#!/usr/bin/env python3
"""Validate Quarto cross-references and detect orphan pages.

Two checks run in sequence:

1. **Cross-reference validation** — scans all .qmd files for ``@sec-``,
   ``@fig-``, ``@eq-``, ``@tbl-`` references and verifies that every target
   label is defined somewhere in the same directory tree.  Only within-book
   references are checked to avoid false-positives from multi-volume projects
   where volumes are rendered separately.

2. **Orphan-page detection** — compares the ``project.render`` glob list in
   ``_quarto.yml`` against the navbar ``href`` values.  A page is flagged as
   orphaned when it appears in the rendered output but is not reachable from
   the top-level navigation (navbar or sidebar).

Exit codes
----------
0  All checks passed.
1  One or more errors found.

Usage
-----
    python3 scripts/check_quarto_xrefs.py
    python3 scripts/check_quarto_xrefs.py --xrefs-only
    python3 scripts/check_quarto_xrefs.py --orphans-only
    python3 scripts/check_quarto_xrefs.py --root /path/to/repo
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Regex patterns for Quarto cross-reference syntax
# ---------------------------------------------------------------------------

# Matches labels as they appear in .qmd source:
#   {#sec-my-section}  {#fig-plot1}  {#eq-eom}  {#tbl-results}
_LABEL_PATTERN = re.compile(r"\{#((?:sec|fig|eq|tbl)-[\w-]+)\}")

# Matches cross-reference calls: @sec-foo, @fig-bar, etc.
# Also handles ([-@sec-foo]) cite-style and [@fig-foo] biblio-style syntax.
_REF_PATTERN = re.compile(r"@((?:sec|fig|eq|tbl)-[\w-]+)")

# Fenced code block (``` ... ```) — we skip label/ref scanning inside these
_CODE_FENCE = re.compile(r"^```")

# Inline code span
_INLINE_CODE = re.compile(r"`[^`]+`")

# YAML frontmatter delimiter
_FRONTMATTER_FENCE = "---"

# Directories never scanned
_SKIP_DIRS = {
    "docs",
    "_site",
    ".quarto",
    "node_modules",
    ".git",
    "archive",
    "__pycache__",
}


# ---------------------------------------------------------------------------
# Helpers: QMD scanning
# ---------------------------------------------------------------------------


def _strip_frontmatter(lines: list[str]) -> list[str]:
    """Remove YAML frontmatter block (between opening and closing ---)."""
    if not lines or lines[0].strip() != _FRONTMATTER_FENCE:
        return lines
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == _FRONTMATTER_FENCE:
            return lines[i + 1 :]
    return lines


def _strip_inline_code(line: str) -> str:
    """Remove inline code spans so embedded labels/refs are not matched."""
    return _INLINE_CODE.sub("", line)


def collect_labels_and_refs(
    file_path: Path,
) -> tuple[set[str], list[tuple[str, int]]]:
    """Return (labels_defined, [(ref_key, line_number), ...]) for a .qmd file.

    Labels are identifiers defined in this file (e.g. ``sec-intro``).
    Refs are cross-reference targets used in this file.

    Lines inside fenced code blocks are skipped so that example code
    embedded in the document does not generate false positives.
    """
    try:
        raw = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        logger.warning("Could not read %s — skipping", file_path)
        return set(), []

    all_lines = raw.splitlines()
    content_lines = _strip_frontmatter(all_lines)

    labels: set[str] = set()
    refs: list[tuple[str, int]] = []

    in_code_block = False
    # Line numbers relative to original file for diagnostic messages
    offset = len(all_lines) - len(content_lines)

    for idx, line in enumerate(content_lines):
        line_num = idx + offset + 1

        if _CODE_FENCE.match(line):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        clean = _strip_inline_code(line)
        for m in _LABEL_PATTERN.finditer(clean):
            labels.add(m.group(1))

        for m in _REF_PATTERN.finditer(clean):
            refs.append((m.group(1), line_num))

    return labels, refs


def _is_scanned_dir(path: Path) -> bool:
    """Return False when the path contains a skip-dir component."""
    return not any(part in _SKIP_DIRS for part in path.parts)


def find_qmd_files(root: Path) -> list[Path]:
    """Recursively collect .qmd files under *root*, skipping ignored dirs."""
    results: list[Path] = []
    for f in root.rglob("*.qmd"):
        if _is_scanned_dir(f.relative_to(root)):
            results.append(f)
    return sorted(results)


# ---------------------------------------------------------------------------
# Check 1: cross-reference validation
# ---------------------------------------------------------------------------


def validate_xrefs(root: Path) -> list[tuple[str, int, str]]:
    """Validate all @sec-/@fig-/@eq-/@tbl- cross-references.

    Returns a list of (relative_file_path, line_number, missing_label)
    tuples for every reference whose target label is not defined anywhere
    in the scanned .qmd files under *root*.
    """
    qmd_files = find_qmd_files(root)
    if not qmd_files:
        logger.info("No .qmd files found under %s", root)
        return []

    # First pass: collect all labels defined across the project
    all_labels: set[str] = set()
    per_file_refs: dict[Path, list[tuple[str, int]]] = {}

    for qmd in qmd_files:
        labels, refs = collect_labels_and_refs(qmd)
        all_labels.update(labels)
        per_file_refs[qmd] = refs

    # Second pass: find references to undefined labels
    errors: list[tuple[str, int, str]] = []
    for qmd, refs in per_file_refs.items():
        rel = qmd.relative_to(root).as_posix()
        for label, line_num in refs:
            if label not in all_labels:
                errors.append((rel, line_num, label))

    return errors


# ---------------------------------------------------------------------------
# Check 2: orphan-page detection
# ---------------------------------------------------------------------------


def _collect_nav_hrefs(nav_node: object) -> set[str]:
    """Recursively collect all href values from a navbar/sidebar node."""
    hrefs: set[str] = set()
    if isinstance(nav_node, dict):
        href = nav_node.get("href")
        if isinstance(href, str):
            hrefs.add(href)
        for value in nav_node.values():
            hrefs.update(_collect_nav_hrefs(value))
    elif isinstance(nav_node, list):
        for item in nav_node:
            hrefs.update(_collect_nav_hrefs(item))
    return hrefs


def _html_to_source_stem(href: str) -> str:
    """Convert a nav href like ``pages/about.html`` to a source stem.

    Returns the path stem without extension, using forward slashes, so we
    can compare against .qmd source files regardless of rendered extension
    and OS path separator.
    """
    # Work with PurePosixPath-style strings to stay OS-independent
    if href.endswith(".html") or href.endswith(".htm"):
        stem = href.rsplit(".", 1)[0]
        return stem
    return href


def _resolve_render_globs(quarto_data: dict, root: Path) -> list[Path]:
    """Expand ``project.render`` glob patterns into actual .qmd paths."""
    render_rules: list[str] = quarto_data.get("project", {}).get("render", [])
    matched: list[Path] = []
    for rule in render_rules:
        rule = rule.strip()
        # Skip negation rules (!) — those suppress rendering
        if rule.startswith("!"):
            continue
        # Only care about .qmd globs for this check
        if not rule.endswith(".qmd"):
            continue
        matched.extend(root.glob(rule))
    return matched


def detect_orphans(root: Path, quarto_yml: Path) -> list[str]:
    """Find pages that are rendered but not reachable from the navbar.

    Returns a list of relative path strings for orphaned pages.
    Only reports pages that come from ``project.render`` globs — pages
    listed under negation rules are explicitly excluded.

    The check is intentionally lenient: a page is only flagged when its
    stem (no extension) does not appear anywhere in the nav href set.
    Index pages (``index.qmd`` / ``index.html``) are excluded because
    they are the implicit root of a section and always reachable.
    """
    try:
        data = yaml.safe_load(quarto_yml.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        logger.error("Could not parse %s: %s", quarto_yml, exc)
        return []

    # Collect all nav hrefs from website.navbar and website.sidebar
    website = data.get("website", {})
    nav_hrefs: set[str] = set()
    nav_hrefs.update(_collect_nav_hrefs(website.get("navbar", {})))
    nav_hrefs.update(_collect_nav_hrefs(website.get("sidebar", {})))

    # Build a set of stem paths from nav hrefs
    nav_stems: set[str] = {_html_to_source_stem(h) for h in nav_hrefs}

    # Expand render globs
    rendered_pages = _resolve_render_globs(data, root)

    orphans: list[str] = []
    for page in rendered_pages:
        rel = page.relative_to(root)
        # Index pages are never orphans — they are section roots
        if rel.stem == "index":
            continue
        # Use forward-slash paths for cross-platform comparison against nav hrefs
        stem = rel.with_suffix("").as_posix()
        # Check against nav stems (both with and without leading slash)
        if stem not in nav_stems and ("/" + stem) not in nav_stems:
            orphans.append(rel.as_posix())

    return sorted(orphans)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Validate Quarto cross-references and detect orphan pages."
    )
    p.add_argument(
        "--root",
        default=".",
        help="Repository root (default: current directory)",
    )
    p.add_argument(
        "--xrefs-only",
        action="store_true",
        help="Run only cross-reference validation",
    )
    p.add_argument(
        "--orphans-only",
        action="store_true",
        help="Run only orphan-page detection",
    )
    p.add_argument(
        "--warn-orphans",
        action="store_true",
        help="Treat orphan pages as warnings rather than errors (non-blocking)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    """Run both checks and return an exit code."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = _build_parser().parse_args(argv)

    root = Path(args.root).resolve()
    quarto_yml = root / "_quarto.yml"
    run_xrefs = not args.orphans_only
    run_orphans = not args.xrefs_only

    all_passed = True

    # ------------------------------------------------------------------
    # Check 1 — cross-reference validation
    # ------------------------------------------------------------------
    if run_xrefs:
        logger.info("--- Cross-reference validation ---")
        xref_errors = validate_xrefs(root)
        if xref_errors:
            all_passed = False
            logger.error("Unresolved cross-references found:")
            for rel_file, line_num, label in sorted(xref_errors):
                logger.error("  %s:%d  @%s", rel_file, line_num, label)
        else:
            logger.info("All cross-references resolve correctly.")

    # ------------------------------------------------------------------
    # Check 2 — orphan-page detection
    # ------------------------------------------------------------------
    if run_orphans and quarto_yml.exists():
        logger.info("--- Orphan-page detection ---")
        orphans = detect_orphans(root, quarto_yml)
        if orphans:
            if args.warn_orphans:
                logger.warning("Pages rendered but not linked from nav (%d):", len(orphans))
                for page in orphans:
                    logger.warning("  %s", page)
            else:
                all_passed = False
                logger.error("Orphan pages found (rendered but not in nav) (%d):", len(orphans))
                for page in orphans:
                    logger.error("  %s", page)
        else:
            logger.info("No orphan pages detected.")
    elif run_orphans:
        logger.warning("_quarto.yml not found at %s — skipping orphan check", quarto_yml)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
