#!/usr/bin/env python3
"""Verify scaffolding styling and stub hub card policy (issue #4500).

Enforces two acceptance criteria from WEB-02.6:
1. Scaffolding/stub pages must never use success styling (status-banner--success,
   callout-success, alert-success, status-pill--success, status-badge--success).
2. No hub card links to a page under 300 words unless it carries a Planned badge.

Usage:
    python3 scripts/check_scaffolding_styling.py
    python3 scripts/check_scaffolding_styling.py --root .
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

SUCCESS_STYLING_PATTERNS = (
    re.compile(r"\bstatus-banner--success\b"),
    re.compile(r"\bcallout-success\b"),
    re.compile(r"\balert-success\b"),
    re.compile(r"\bstatus-pill--success\b"),
    re.compile(r"\bstatus-badge--success\b"),
)

SCAFFOLDING_INDICATORS = (
    re.compile(r"status:\s*in\s*progress\s*\(\s*scaffolding", re.IGNORECASE),
    re.compile(r"scaffolding\s*phase", re.IGNORECASE),
    re.compile(r"review\s*scaffold", re.IGNORECASE),
    re.compile(r"source-collection\s*stub", re.IGNORECASE),
    re.compile(r"status:\s*planned", re.IGNORECASE),
)

SCAFFOLDING_EXPLICIT_PAGES = {
    "resources/research-reviews.qmd",
    "resources/research-review-interaction-forces.qmd",
    "resources/research-review-induced-acceleration-analysis.qmd",
    "resources/research-review-baseball-pitching.qmd",
    "resources/research-review-shaft-flexibility.qmd",
    "pages/book-reviews.qmd",
    "pages/daydreams-doodles.qmd",
}

PLANNED_BADGE_PATTERN = re.compile(
    r"\bplanned\b|status-badge--planned|status-pill--planned",
    re.IGNORECASE,
)

CARD_BLOCK_PATTERN = re.compile(
    r"(<(?:div|article)[^>]*class=\"[^\"]*(?:card|category-card)[^\"]*\"[^>]*>.*?</(?:div|article)>)",
    re.DOTALL | re.IGNORECASE,
)

HREF_PATTERN = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)

WORD_PATTERN = re.compile(r"\b[A-Za-z0-9_-]+\b")


class Violation(NamedTuple):
    file_path: Path
    line_number: int
    rule: str
    message: str


UTILITY_PAGES = {
    "pages/contact.qmd",
    "resources/bibliography.qmd",
}

INCLUDE_PATTERN = re.compile(r"\{\{<\s*include\s+([^\s>]+)\s*>\}\}")


def count_prose_words(file_path: Path, visited: set[Path] | None = None) -> int:
    """Extract and count visible prose words from a QMD document, expanding includes."""
    if visited is None:
        visited = set()
    resolved_path = file_path.resolve()
    if resolved_path in visited or not resolved_path.is_file():
        return 0
    visited.add(resolved_path)

    try:
        text = resolved_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return 0

    # Retain abstract and description from YAML frontmatter if present
    extra_text = []
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm = parts[1]
            text = parts[2]
            for m in re.finditer(r"^(?:description|abstract):\s*(.+)$", fm, re.MULTILINE):
                extra_text.append(m.group(1))

    # Expand {{< include ... >}} directives before stripping markup
    included_words = 0
    for inc_match in INCLUDE_PATTERN.finditer(text):
        inc_rel = inc_match.group(1).strip()
        inc_path = (resolved_path.parent / inc_rel).resolve()
        if inc_path.is_file():
            included_words += count_prose_words(inc_path, visited)

    # Keep content inside ```{=html} blocks, strip other executable code blocks
    text = re.sub(r"```\{=html\}", " ", text)
    text = re.sub(r"```[^\n]*\n.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"```", " ", text)
    # Strip HTML tags and markdown link syntax
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    words = WORD_PATTERN.findall(text + " " + " ".join(extra_text))
    return len(words) + included_words


def is_scaffolding_page(relative_posix: str, content: str) -> bool:
    """Return True if the page is designated or marked as scaffolding/stub."""
    if relative_posix in SCAFFOLDING_EXPLICIT_PAGES:
        return True
    return any(p.search(content) for p in SCAFFOLDING_INDICATORS)


def check_scaffolding_styling(root: Path) -> list[Violation]:
    """Ensure scaffolding pages never use success styling."""
    violations: list[Violation] = []
    for qmd in sorted(root.glob("**/*.qmd")):
        if "_includes" in str(qmd) or ".quarto" in str(qmd):
            continue
        rel = qmd.relative_to(root).as_posix()
        try:
            content = qmd.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if not is_scaffolding_page(rel, content):
            continue
        for line_num, line in enumerate(content.splitlines(), start=1):
            for pat in SUCCESS_STYLING_PATTERNS:
                if pat.search(line):
                    violations.append(
                        Violation(
                            file_path=qmd,
                            line_number=line_num,
                            rule="scaffolding-no-success-styling",
                            message=(
                                f"Scaffolding page '{rel}' must not use success styling "
                                f"('{pat.pattern}'). Use warning or info status styling instead."
                            ),
                        )
                    )
    return violations


def check_hub_cards(root: Path) -> list[Violation]:
    """Ensure no hub card links to a page under 300 words without a Planned badge."""
    violations: list[Violation] = []
    # Check hub pages across pages/ and resources/
    hub_dirs = ("pages", "resources")
    for dirname in hub_dirs:
        dirpath = root / dirname
        if not dirpath.is_dir():
            continue
        for qmd in sorted(dirpath.glob("*.qmd")):
            rel_source = qmd.relative_to(root).as_posix()
            try:
                content = qmd.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for card_match in CARD_BLOCK_PATTERN.finditer(content):
                card_text = card_match.group(1)
                has_planned = bool(PLANNED_BADGE_PATTERN.search(card_text))
                card_start_line = content[: card_match.start()].count("\n") + 1
                for href in HREF_PATTERN.findall(card_text):
                    if href.startswith(("http", "#", "mailto:")):
                        continue
                    clean_path = href.split("#")[0].split("?")[0]
                    if not clean_path:
                        continue
                    target_file = (qmd.parent / clean_path).resolve()
                    if target_file.suffix == ".html":
                        target_qmd = target_file.with_suffix(".qmd")
                    elif target_file.suffix == "":
                        target_qmd = target_file / "index.qmd"
                    else:
                        target_qmd = target_file
                    if not target_qmd.exists() and target_file.is_dir():
                        target_qmd = target_file / "index.qmd"
                    if not target_qmd.is_file() or target_qmd.suffix != ".qmd":
                        continue
                    rel_target = target_qmd.relative_to(root).as_posix()
                    if rel_target in UTILITY_PAGES:
                        continue
                    word_count = count_prose_words(target_qmd)
                    if word_count < 300 and not has_planned:
                        violations.append(
                            Violation(
                                file_path=qmd,
                                line_number=card_start_line,
                                rule="hub-card-stub-needs-planned-badge",
                                message=(
                                    f"Hub card in '{rel_source}' links to page '{rel_target}' "
                                    f"under 300 words ({word_count} words) without a Planned badge."
                                ),
                            )
                        )
    return violations


def run_checks(root: Path) -> list[Violation]:
    """Run all scaffolding styling and hub card checks."""
    violations: list[Violation] = []
    violations.extend(check_scaffolding_styling(root))
    violations.extend(check_hub_cards(root))
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify scaffolding styling and stub hub card policy (WEB-02.6 / #4500)."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root directory (default: current directory).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if any violations are found.",
    )
    args = parser.parse_args()
    root = args.root.resolve()

    violations = run_checks(root)
    if not violations:
        print("Scaffolding styling and hub card checks passed cleanly.")
        return 0

    print(f"Found {len(violations)} violation(s):", file=sys.stderr)
    for v in violations:
        rel = v.file_path.relative_to(root).as_posix()
        print(f"::error file={rel},line={v.line_number}::{v.message}", file=sys.stderr)
        print(f"  {rel}:{v.line_number} [{v.rule}] {v.message}", file=sys.stderr)

    return 1


if __name__ == "__main__":
    sys.exit(main())
