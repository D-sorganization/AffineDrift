#!/usr/bin/env python3
"""Post-render HTML performance fixes for UX slice 2 (#5165).

- Drop Quarto's duplicate ``quarto-color-scheme-extra`` stylesheets.
- Make alternate (dark) theme stylesheets non-render-blocking.
- Remove Quarto dev-only ``axe-check.js`` from production output.
- Prune ``citation_reference`` meta tags to bibliography entries rendered on-page.
- Defer non-critical head scripts that Quarto emits synchronously.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from html import unescape
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

LINK_TAG_RE = re.compile(r"<link\b[^>]*>", re.IGNORECASE)
SCRIPT_TAG_RE = re.compile(r"<script\b[^>]*\bsrc=[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
SCRIPT_OPEN_RE = re.compile(r"<script\b([^>]*)>", re.IGNORECASE)
META_CITATION_REFERENCE_RE = re.compile(
    r'\s*<meta\s+name="citation_reference"\s+content="([^"]*)"\s*/?>\s*',
    re.IGNORECASE,
)
REFS_SECTION_RE = re.compile(
    r'<section[^>]*\bid="refs"[^>]*>(.*?)</section>',
    re.IGNORECASE | re.DOTALL,
)
CITATION_TITLE_IN_META_RE = re.compile(r"citation_title=([^;,]+)", re.IGNORECASE)
AXE_CHECK_SCRIPT_RE = re.compile(
    r'\s*<script\b[^>]*\bsrc="[^"]*axe-check\.js"[^>]*>\s*</script>\s*',
    re.IGNORECASE,
)

DEFER_HEAD_SCRIPTS = (
    "autocomplete.umd.js",
    "fuse.min.js",
    "quarto-search.js",
    "clipboard.min.js",
    "headroom.min.js",
    "popper.min.js",
    "tippy.umd.min.js",
    "anchor.min.js",
)

NON_BLOCKING_ALTERNATE_ATTRS = ' media="print" onload="this.media=\'all\'"'


def _strip_html_tags(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", fragment)
    return unescape(re.sub(r"\s+", " ", text)).strip().lower()


def _refs_plain_text(content: str) -> str:
    match = REFS_SECTION_RE.search(content)
    if not match:
        return ""
    return _strip_html_tags(match.group(1))


def _citation_reference_matches_refs(meta_content: str, refs_text: str) -> bool:
    if not refs_text:
        return False
    title_match = CITATION_TITLE_IN_META_RE.search(meta_content)
    if not title_match:
        return False
    title = unescape(title_match.group(1)).strip().lower()
    if not title:
        return False
    # Match on a stable prefix; refs text is short for on-page bibliographies.
    needle = title[:48]
    return needle in refs_text


def prune_citation_reference_meta(content: str) -> str:
    """Keep scholar reference meta only for works listed in the page ``#refs`` section."""

    refs_text = _refs_plain_text(content)

    def replace_meta(match: re.Match[str]) -> str:
        meta_content = match.group(1)
        if _citation_reference_matches_refs(meta_content, refs_text):
            return match.group(0)
        return ""

    return META_CITATION_REFERENCE_RE.sub(replace_meta, content)


def remove_quarto_color_scheme_extra_links(content: str) -> str:
    """Remove duplicate light-theme links Quarto emits as ``quarto-color-scheme-extra``."""

    def replace_link(match: re.Match[str]) -> str:
        tag = match.group(0)
        if "quarto-color-scheme-extra" in tag:
            return ""
        return tag

    return LINK_TAG_RE.sub(replace_link, content)


def make_alternate_stylesheets_non_blocking(content: str) -> str:
    """Defer dark/alternate Quarto stylesheets so only the active light theme blocks."""

    def replace_link(match: re.Match[str]) -> str:
        tag = match.group(0)
        if 'rel="stylesheet"' not in tag.lower():
            return tag
        if "quarto-color-alternate" not in tag:
            return tag
        if "media=" in tag.lower():
            return tag
        return tag[:-1] + NON_BLOCKING_ALTERNATE_ATTRS + ">"

    return LINK_TAG_RE.sub(replace_link, content)


def strip_axe_check_script(content: str) -> str:
    return AXE_CHECK_SCRIPT_RE.sub("\n", content)


def defer_noncritical_head_scripts(content: str) -> str:
    """Add ``defer`` to known non-critical Quarto head scripts."""

    head, tail = content.split("</head>", maxsplit=1)

    def replace_script_open(match: re.Match[str]) -> str:
        attrs = match.group(1)
        lowered = attrs.lower()
        if "defer" in lowered or 'type="module"' in lowered:
            return match.group(0)
        if not any(name in lowered for name in DEFER_HEAD_SCRIPTS):
            return match.group(0)
        if lowered.strip().endswith("/"):
            return f"<script{attrs} defer>"
        return f"<script{attrs} defer>"

    head = SCRIPT_OPEN_RE.sub(replace_script_open, head)
    return head + "</head>" + tail


def process_html_head_performance(content: str) -> str:
    updated = content
    updated = remove_quarto_color_scheme_extra_links(updated)
    updated = make_alternate_stylesheets_non_blocking(updated)
    updated = strip_axe_check_script(updated)
    updated = prune_citation_reference_meta(updated)
    updated = defer_noncritical_head_scripts(updated)
    return updated


def process_html_file(html_path: Path) -> bool:
    original = html_path.read_text(encoding="utf-8")
    updated = process_html_head_performance(original)
    if updated != original:
        html_path.write_text(updated, encoding="utf-8")
        return True
    return False


def process_site(docs_dir: Path) -> int:
    changed = 0
    if not docs_dir.is_dir():
        logger.warning("Output directory %s does not exist; skipping.", docs_dir)
        return changed
    for html_file in sorted(docs_dir.rglob("*.html")):
        if process_html_file(html_file):
            changed += 1
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply post-render page performance fixes.")
    parser.add_argument(
        "--docs-dir",
        default="_site",
        help="Quarto output directory (default: _site)",
    )
    args = parser.parse_args()
    docs_dir = Path(args.docs_dir)
    changed = process_site(docs_dir)
    logger.info("Updated %d HTML file(s) in %s", changed, docs_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
