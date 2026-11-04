#!/usr/bin/env python3
"""Fail when a published page embeds a figure without a projection record (#5421).

A figure is *traced* when a markerless-mocap publication projection under
``evidence/projections/`` lists it as a ``visualization`` artifact and the
manifest passes ``verify_projection_manifest`` against the figure's bytes.
Figures that predate projection records are listed as explicit, reasoned glob
exemptions in ``evidence/projections/figure_exemptions.json``.

Pages come from the ``_quarto.yml`` render list. A page with ``draft: true``
only warns. Exit 0 when no published page embeds an untraced figure, else 1.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import logging
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.verify_markerless_mocap_projection import verify_projection_manifest  # noqa: E402
from src.tools.site_page_scan import (  # noqa: E402
    expand_includes,
    is_rendered,
    page_body,
    parse_front_matter,
    rendered_relative_paths,
    strip_code,
)
from src.tools.utils.link_utils import (  # noqa: E402
    is_external_url,
    normalize_internal_url,
    resolve_relative_path,
)

logger = logging.getLogger(__name__)

DEFAULT_PROJECTIONS = REPO_ROOT / "evidence" / "projections"
DEFAULT_EXEMPTIONS = DEFAULT_PROJECTIONS / "figure_exemptions.json"
PAGE_SUFFIXES = (".qmd", ".md")
TRACING_KIND = "visualization"
FIGURE_PATTERN = re.compile(r"!\[[^\]]*\]\(\s*<?([^)\s>]+)|<img\b[^>]*?\bsrc=[\"']([^\"']+)")


@dataclass(frozen=True)
class Exemption:
    """A glob of repo-relative figure paths exempt from tracing, with its reason."""

    pattern: str
    reason: str


@dataclass
class FigureReport:
    """Untraced figures as ``page: figure`` lines, split by page state."""

    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def published_pages(root: Path) -> list[Path]:
    """Return the ``.qmd``/``.md`` pages the ``_quarto.yml`` render list covers."""
    render_set = rendered_relative_paths(root)
    if render_set is None:
        raise ValueError(f"{root / '_quarto.yml'} declares no project.render list")
    pages = {
        path
        for suffix in PAGE_SUFFIXES
        for path in root.rglob(f"*{suffix}")
        # Quarto never renders ``_``-prefixed files; they are include fragments.
        if not path.name.startswith("_") and not {"_site", "node_modules"} & set(path.parts)
    }
    return sorted(p for p in pages if is_rendered(p.relative_to(root).as_posix(), render_set))


def embedded_figures(root: Path, page: Path) -> list[str]:
    """Return repo-relative paths of local figures the page (with includes) embeds."""
    content = strip_code(page_body(expand_includes(root, page)))
    figures: list[str] = []
    for match in FIGURE_PATTERN.finditer(content):
        url = normalize_internal_url(match.group(1) or match.group(2))
        if url is None or is_external_url(url) or url.startswith("data:"):
            continue
        target = resolve_relative_path(root=root, source_file=page, url=url).resolve()
        if target.is_relative_to(root.resolve()):
            figures.append(target.relative_to(root.resolve()).as_posix())
    return sorted(set(figures))


def is_draft(page: Path) -> bool:
    """Return True when the page front matter sets ``draft: true``."""
    return parse_front_matter(page.read_text(encoding="utf-8")).get("draft") is True


def traced_figures(root: Path, projections: Path) -> set[str]:
    """Return figure paths named by verified ``visualization`` projection artifacts.

    Raises:
        MocapProjectionError: if any projection manifest fails verification,
            including a figure whose bytes no longer match its digest.
    """
    traced: set[str] = set()
    for manifest_path in sorted(projections.glob("*.json")):
        if manifest_path.name == DEFAULT_EXEMPTIONS.name:
            continue
        manifest: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
        verify_projection_manifest(manifest, root)
        traced.update(
            item["path"] for item in manifest["artifacts"] if item["kind"] == TRACING_KIND
        )
    return traced


def load_exemptions(path: Path) -> list[Exemption]:
    """Load exemption globs; every entry needs a non-empty pattern and reason.

    Raises:
        ValueError: if an entry is missing its pattern or reason.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    exemptions: list[Exemption] = []
    for index, entry in enumerate(data["exemptions"]):
        pattern = str(entry.get("pattern", "")).strip()
        reason = str(entry.get("reason", "")).strip()
        if not pattern or not reason:
            raise ValueError(f"{path}: exemption {index} needs a pattern and a reason")
        exemptions.append(Exemption(pattern, reason))
    return exemptions


def _exempt(figure: str, pattern: str) -> bool:
    # fnmatch's ``*`` crosses ``/``; keep each glob inside its own directory so a
    # new subdirectory never inherits an exemption.
    return figure.count("/") == pattern.count("/") and fnmatch.fnmatch(figure, pattern)


def check_site(root: Path, projections: Path, exemptions_path: Path) -> FigureReport:
    """Report every untraced, unexempted figure embedded by a rendered page."""
    traced = traced_figures(root, projections)
    patterns = [item.pattern for item in load_exemptions(exemptions_path)]
    report = FigureReport()
    for page in published_pages(root):
        bucket = report.warnings if is_draft(page) else report.failures
        for figure in embedded_figures(root, page):
            if figure in traced or any(_exempt(figure, pattern) for pattern in patterns):
                continue
            bucket.append(f"{page.relative_to(root).as_posix()}: {figure}")
    return report


def main(argv: Sequence[str] | None = None) -> int:
    """Run the gate and log untraced figures; return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--projections", type=Path, default=DEFAULT_PROJECTIONS)
    parser.add_argument("--exemptions", type=Path, default=DEFAULT_EXEMPTIONS)
    args = parser.parse_args(argv)
    report = check_site(args.root, args.projections, args.exemptions)
    for line in report.warnings:
        logger.warning("draft page embeds untraced figure: %s", line)
    for line in report.failures:
        logger.error("published page embeds untraced figure: %s", line)
    if report.failures:
        logger.error("Add a projection record or an exemption (%s).", DEFAULT_EXEMPTIONS.name)
        return 1
    logger.info("Every published figure has a projection record or an exemption.")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    raise SystemExit(main())
