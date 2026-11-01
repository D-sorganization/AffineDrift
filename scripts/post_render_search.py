#!/usr/bin/env python3
"""Bound Quarto search data and defer its runtime libraries (#5170)."""

from __future__ import annotations

import argparse
import gzip
import json
import logging
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)
SEARCHABLE_PREFIXES = ("articles/", "books/")
MAX_SEARCH_TEXT_CHARS = 1_200
MAX_GZIP_BYTES = 1_000_000
SKIP_LINK_TEXT_RE = re.compile(r"skip\s+to\s+main\s+content", re.IGNORECASE)
REQUIRED_FIELDS = ("objectID", "href", "title", "section", "text")
SEARCH_LIBRARIES = frozenset({"autocomplete.umd.js", "fuse.min.js", "quarto-search.js"})
SCRIPT_RE = re.compile(r"<script\b(?P<attrs>[^>]*)>\s*</script\s*>", re.I)
SRC_RE = re.compile(r"\bsrc\s*=\s*(['\"])(.*?)\1", re.I | re.S)


def _searchable_route(href: str) -> bool:
    path = urlsplit(href).path.lstrip("/")
    return path.startswith(SEARCHABLE_PREFIXES) and ".." not in path.split("/")


def bound_search_index(entries: list[object]) -> list[dict[str, str]]:
    if not isinstance(entries, list):
        raise ValueError("search index must be a JSON array")
    result = []
    for entry in entries:
        if not isinstance(entry, dict) or any(
            not isinstance(entry.get(k), str) for k in REQUIRED_FIELDS
        ):
            raise ValueError(
                "search entry must contain string objectID, href, title, section, and text"
            )
        if _searchable_route(entry["href"]):
            text = re.sub(r"\s+", " ", SKIP_LINK_TEXT_RE.sub(" ", entry["text"])).strip()
            if len(text) > MAX_SEARCH_TEXT_CHARS:
                head = MAX_SEARCH_TEXT_CHARS // 3
                text = (
                    text[:head].rstrip() + " " + text[-MAX_SEARCH_TEXT_CHARS + head + 1 :].lstrip()
                )
            result.append({**entry, "text": text})
    if not result:
        raise ValueError("search index contains no article or book entries")
    return result


def process_html(content: str) -> tuple[str, bool]:
    seen = []

    def remove(match: re.Match[str]) -> str:
        src = SRC_RE.search(match.group("attrs"))
        path = urlsplit(src.group(2)).path if src else ""
        if "/site_libs/quarto-search/" not in f"/{path.lstrip('/')}":
            return match.group(0)
        name = path.rsplit("/", 1)[-1]
        if name not in SEARCH_LIBRARIES:
            return match.group(0)
        seen.append(name)
        return ""

    updated = SCRIPT_RE.sub(remove, content)
    if not seen:
        return content, False
    if len(seen) != len(SEARCH_LIBRARIES) or set(seen) != SEARCH_LIBRARIES:
        raise ValueError("partial Quarto search library set in rendered HTML")
    return updated, True


def process_site(site_dir: Path) -> bool:
    index_path = site_dir / "search.json"
    raw = index_path.read_text(encoding="utf-8")
    index = (
        json.dumps(bound_search_index(json.loads(raw)), ensure_ascii=False, separators=(",", ":"))
        + "\n"
    )
    compressed_size = len(gzip.compress(index.encode("utf-8"), mtime=0))
    if compressed_size > MAX_GZIP_BYTES:
        raise ValueError(
            f"bounded search index is {compressed_size} gzip bytes; budget is {MAX_GZIP_BYTES}"
        )

    changed = index != raw
    if changed:
        temporary = index_path.with_suffix(".json.tmp")
        temporary.write_text(index, encoding="utf-8")
        temporary.replace(index_path)
    for html_path in sorted(site_dir.rglob("*.html")):
        original = html_path.read_text(encoding="utf-8")
        updated, was_changed = process_html(original)
        if was_changed:
            html_path.write_text(updated, encoding="utf-8")
            changed = True
    logger.info("Search index: %d gzip bytes; HTML updated: %s", compressed_size, changed)
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", type=Path, default=Path("_site"))
    process_site(parser.parse_args(argv).site_dir)
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        sys.exit(main())
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        logger.error("Unable to post-process Quarto search: %s", exc)
        sys.exit(1)
