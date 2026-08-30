#!/usr/bin/env python3
"""Build the deterministic manifest consumed by public-site verification.

The Quarto render is the authority for which routes are public.  This module
turns that render into one sorted contract shared by local E2E, CI artifacts,
and post-deployment verification (AffineDrift#3998).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag

MANIFEST_SCHEMA_VERSION = "affinedrift/public-site-manifest/v1"
IGNORED_HTML_DIRECTORIES = frozenset({"coverage", "lcov-report", "site_libs"})
EVERY_PAGE_VIEWPORTS = (
    {"id": "mobile", "width": 390, "height": 844},
    {"id": "desktop", "width": 1440, "height": 900},
)
REPRESENTATIVE_VIEWPORTS = (
    {"id": "tablet", "width": 768, "height": 1024},
    {"id": "intermediate", "width": 1024, "height": 768},
    {"id": "desktop-small", "width": 1366, "height": 768},
    {"id": "desktop-wide", "width": 1920, "height": 1080},
)
REPRESENTATIVE_VIEWPORT_IDS = (
    "mobile",
    *(viewport["id"] for viewport in REPRESENTATIVE_VIEWPORTS),
)
THEMES = ("light", "dark")
REPRESENTATIVE_ROUTES = (
    {"family": "home", "route": "/", "scenario": "fold"},
    {"family": "books", "route": "/books/index.html", "scenario": "fold"},
    {
        "family": "monograph",
        "route": "/articles/proximal_distal_energy_transfer/index.html",
        "scenario": "fold",
    },
    {
        "family": "article",
        "route": "/articles/affine-nature-golf-swing.html",
        "scenario": "fold",
    },
    {
        "family": "model-workbench",
        "route": "/articles/proximal-distal-model-workbench.html",
        "scenario": "fold",
    },
    {"family": "programming", "route": "/models/models.html", "scenario": "fold"},
    {
        "family": "search",
        "route": "/resources/articles.html",
        "scenario": "site-search",
    },
    {"family": "critique", "route": "/critiques/index.html", "scenario": "fold"},
    {
        "family": "research-report",
        "route": "/reports/scientific-claim-audit.html",
        "scenario": "fold",
    },
    {"family": "resource", "route": "/resources/resources.html", "scenario": "fold"},
)


def _html_paths(docs_dir: Path) -> list[Path]:
    """Return public HTML paths relative to ``docs_dir`` in stable order."""
    if not docs_dir.is_dir():
        raise ValueError(f"rendered public HTML directory does not exist: {docs_dir}")

    paths = [
        path.relative_to(docs_dir)
        for path in docs_dir.rglob("*.html")
        if not any(part in IGNORED_HTML_DIRECTORIES for part in path.relative_to(docs_dir).parts)
    ]
    if not paths:
        raise ValueError(f"rendered public HTML directory contains no pages: {docs_dir}")
    return sorted(paths, key=lambda item: item.as_posix().casefold())


def _route_for(relative_path: Path) -> str:
    """Map a rendered HTML path to its canonical browser route."""
    posix = relative_path.as_posix()
    return "/" if posix == "index.html" else f"/{posix}"


def _page_kind(relative_path: Path) -> str:
    """Classify a route using the documented publication ownership rules."""
    posix = relative_path.as_posix()
    if posix == "index.html":
        return "home"
    if posix in {"404.html", "offline.html"}:
        return "system"
    if posix.startswith(
        (
            "articles/The_Physics_of_Golf/",
            "articles/The_Geometry_of_Motion/",
            "articles/proximal_distal_energy_transfer/",
        )
    ):
        return "textbook"
    if posix.startswith("books/"):
        return "book"
    if posix.startswith(("articles/", "critiques/")) and not posix.endswith("/index.html"):
        return "article"
    return "hub"


def _source_for(relative_path: Path, source_root: Path) -> str | None:
    """Return the canonical source path when a direct source mapping exists."""
    stem_path = relative_path.with_suffix("")
    candidates = (
        source_root / stem_path.with_suffix(".qmd"),
        source_root / stem_path.with_suffix(".md"),
        source_root / relative_path,
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.relative_to(source_root).as_posix()
    return None


def _nonempty_text(tag: Tag | None) -> str:
    """Return normalized text for a parsed tag."""
    return "" if tag is None else " ".join(tag.get_text(" ", strip=True).split())


def _page_record(path: Path, docs_dir: Path, source_root: Path) -> dict[str, Any]:
    """Create a validated manifest record for one rendered page."""
    soup = BeautifulSoup((docs_dir / path).read_text(encoding="utf-8"), "html.parser")
    title = _nonempty_text(soup.title)
    headings = [heading for heading in soup.find_all("h1") if _nonempty_text(heading)]
    quarto_content = soup.select_one("#quarto-content.page-layout-full")
    generated_title = soup.select_one("#title-block-header h1")
    authored_headings = [
        heading for heading in headings if generated_title is None or heading != generated_title
    ]

    if not headings:
        raise ValueError(f"{path.as_posix()} contains no static H1 candidate")

    if quarto_content is not None and generated_title is not None and authored_headings:
        title_owner = "authored"
        primary_heading = authored_headings[0]
    elif generated_title is not None:
        title_owner = "generated"
        primary_heading = generated_title
    else:
        title_owner = "authored"
        primary_heading = headings[0]

    if not title:
        raise ValueError(f"{path.as_posix()} has an empty document title")

    return {
        "route": _route_for(path),
        "output": path.as_posix(),
        "source": _source_for(path, source_root),
        "page_kind": _page_kind(path),
        "title_owner": title_owner,
        "static_h1_count": len(headings),
        "document_title": title,
        "primary_heading": _nonempty_text(primary_heading),
    }


def _discover_source_revision(source_root: Path) -> str:
    """Return the CI revision or current Git commit for deployment attestation."""
    ci_revision = os.environ.get("GITHUB_SHA", "").strip()
    if ci_revision:
        return ci_revision
    result = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        capture_output=True,
        check=False,
        text=True,
    )
    revision = result.stdout.strip()
    return revision or "unversioned"


def build_manifest(
    docs_dir: Path,
    *,
    source_root: Path,
    source_revision: str | None = None,
    require_representative: bool = True,
) -> dict[str, Any]:
    """Build and validate a complete public-page manifest.

    Preconditions: ``docs_dir`` contains a non-empty Quarto HTML render and
    ``source_root`` is a directory.  Postconditions: routes are unique, sorted,
    and every page carries a validated page-kind/title contract.
    """
    if not source_root.is_dir():
        raise ValueError(f"source root does not exist: {source_root}")

    pages = [_page_record(path, docs_dir, source_root) for path in _html_paths(docs_dir)]
    pages.sort(key=lambda page: (page["route"] != "/", page["route"].casefold()))
    routes = [page["route"] for page in pages]
    if len(routes) != len(set(routes)):
        raise ValueError("rendered public HTML contains duplicate routes")
    if require_representative:
        missing_routes = [
            record["route"] for record in REPRESENTATIVE_ROUTES if record["route"] not in routes
        ]
        if missing_routes:
            raise ValueError(
                "rendered public HTML is missing representative route(s): "
                + ", ".join(missing_routes)
            )

    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "source_revision": source_revision or _discover_source_revision(source_root),
        "page_count": len(pages),
        "pages": pages,
        "verification": {
            "themes": list(THEMES),
            "viewports": [*EVERY_PAGE_VIEWPORTS, *REPRESENTATIVE_VIEWPORTS],
            "every_page": {
                "viewports": [item["id"] for item in EVERY_PAGE_VIEWPORTS],
                "themes": list(THEMES),
            },
            "representative": {
                "routes": [dict(record) for record in REPRESENTATIVE_ROUTES],
                "viewports": list(REPRESENTATIVE_VIEWPORT_IDS),
                "themes": list(THEMES),
            },
        },
    }


def write_manifest(manifest: dict[str, Any], output_path: Path) -> str:
    """Write a manifest atomically enough for build tooling and return its text."""
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise ValueError("manifest schema version is missing or unsupported")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    output_path.write_text(text, encoding="utf-8")
    return text


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs-dir", type=Path, default=Path("docs"))
    parser.add_argument("--source-root", type=Path, default=Path("."))
    parser.add_argument("--source-revision")
    parser.add_argument("--output", type=Path, default=Path("docs/public-site-manifest.json"))
    return parser.parse_args()


def main() -> int:
    """Build the configured manifest for CI or local verification."""
    args = _parse_args()
    manifest = build_manifest(
        args.docs_dir,
        source_root=args.source_root,
        source_revision=args.source_revision,
    )
    write_manifest(manifest, args.output)
    print(f"Public site manifest: {manifest['page_count']} pages -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
