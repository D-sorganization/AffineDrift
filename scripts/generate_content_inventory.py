"""Generate the content inventory and ownership map (#4602).

For published Quarto (.qmd) content pages across the site, records word count, status (derived from
the ``status-banner`` component), a last-reviewed date (from front-matter
``date:``), a canonical pointer (front-matter ``canonical:``, defaulting to
the page's own route), inbound link count, and outbound broken links. Pages
under ``SHORT_PAGE_WORD_THRESHOLD`` words with no Planned status banner are
flagged as consolidation/retirement candidates.

Writes three deterministic artifacts:

- ``data/content/inventory.json``
- ``data/content/inventory.csv``
- ``pages/content-inventory.qmd`` (the dashboard page)

Usage:
    python3 -m scripts.generate_content_inventory [--check]
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.claim_audit_report import write_or_check
from scripts.cli_output import write_stderr, write_stdout
from scripts.public_site_manifest import _route_for
from src.tools.site_page_scan import (
    _resolve_target,
    _target_exists,
    expand_includes,
    extract_links,
    find_content_pages,
    page_body,
    parse_front_matter,
    strip_code,
)

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data/content"
JSON_OUTPUT = DATA_DIR / "inventory.json"
CSV_OUTPUT = DATA_DIR / "inventory.csv"
DASHBOARD_OUTPUT = ROOT / "pages/content-inventory.qmd"
SCHEMA_VERSION = "affinedrift/content-inventory/v1"
SHORT_PAGE_WORD_THRESHOLD = 300

STATUS_BANNER_PATTERN = re.compile(
    r'class="status-banner__title">\s*Status:\s*([^<]+?)\s*</p>', re.IGNORECASE
)
MD_LINK_URL_PATTERN = re.compile(r"\]\([^)]*\)")
TAG_PATTERN = re.compile(r"<[^>]+>")
ATTR_SPAN_PATTERN = re.compile(r"\{[^}]*\}")
WORD_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9'-]*")

CSV_FIELDS = [
    "route",
    "source",
    "title",
    "status",
    "word_count",
    "last_reviewed",
    "canonical",
    "inbound_links",
    "outbound_broken_links",
    "flagged_short",
]


def _page_status(raw_text: str) -> str:
    """Derive a page's status slug from its status-banner component, if any."""
    match = STATUS_BANNER_PATTERN.search(raw_text)
    if match is None:
        return "published"
    return match.group(1).strip().lower().replace(" ", "-")


def _word_count(body: str) -> int:
    """Approximate the visible word count of a page body."""
    text = strip_code(body)
    text = MD_LINK_URL_PATTERN.sub("]", text)
    text = TAG_PATTERN.sub(" ", text)
    text = ATTR_SPAN_PATTERN.sub(" ", text)
    return len(WORD_PATTERN.findall(text))


def _page_title(front_matter: dict[str, Any], body: str) -> str:
    """Return the page title from front matter, or its first heading."""
    title = front_matter.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    heading = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    return heading.group(1).strip() if heading else ""


def _normalize(path: Path) -> Path:
    """Resolve a path for use as a stable link-graph key."""
    try:
        return path.resolve()
    except OSError:
        return path


def _link_graph(root: Path, pages: list[Path]) -> tuple[dict[Path, int], dict[Path, list[str]]]:
    """Return per-page inbound link counts and outbound broken link URLs."""
    keys = {_normalize(page) for page in pages}
    inbound: dict[Path, int] = dict.fromkeys(keys, 0)
    broken: dict[Path, list[str]] = {_normalize(page): [] for page in pages}
    for page in pages:
        expanded = strip_code(expand_includes(root, page))
        page_key = _normalize(page)
        for link in extract_links(page_body(expanded)):
            target = _resolve_target(root, page, link.url)
            if target is None:
                continue
            if not _target_exists(root, target):
                broken[page_key].append(link.url)
                continue
            source = target.with_suffix(".qmd") if target.suffix == ".html" else target
            source_key = _normalize(source)
            if source_key in inbound and source_key != page_key:
                inbound[source_key] += 1
    return inbound, broken


def build_inventory(root: Path) -> list[dict[str, Any]]:
    """Build a deterministic content inventory record for published Quarto (.qmd) content pages."""
    pages = find_content_pages(root)
    inbound, broken = _link_graph(root, pages)
    records: list[dict[str, Any]] = []
    for page in pages:
        raw_text = page.read_text(encoding="utf-8", errors="ignore")
        front_matter = parse_front_matter(raw_text)
        body = page_body(expand_includes(root, page))
        word_count = _word_count(body)
        status = _page_status(raw_text)
        relative_html = page.relative_to(root).with_suffix(".html")
        route = _route_for(relative_html)
        canonical = front_matter.get("canonical") or route
        last_reviewed = front_matter.get("date")
        outbound_broken = sorted(set(broken[_normalize(page)]))
        records.append(
            {
                "route": route,
                "source": page.relative_to(root).as_posix(),
                "title": _page_title(front_matter, body),
                "status": status,
                "word_count": word_count,
                "last_reviewed": str(last_reviewed) if last_reviewed else None,
                "canonical": str(canonical),
                "inbound_links": inbound.get(_normalize(page), 0),
                "outbound_broken_links": outbound_broken,
                "flagged_short": word_count < SHORT_PAGE_WORD_THRESHOLD and status != "planned",
            }
        )
    records.sort(key=lambda record: str(record["route"]).casefold())
    return records


def render_json(records: list[dict[str, Any]]) -> str:
    """Render the JSON inventory artifact."""
    flagged = sum(1 for record in records if record["flagged_short"])
    payload = {
        "schema_version": SCHEMA_VERSION,
        "page_count": len(records),
        "flagged_short_count": flagged,
        "short_page_word_threshold": SHORT_PAGE_WORD_THRESHOLD,
        "pages": records,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def render_csv(records: list[dict[str, Any]]) -> str:
    """Render the CSV inventory artifact."""
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    for record in records:
        row = dict(record)
        row["outbound_broken_links"] = "; ".join(record["outbound_broken_links"])
        writer.writerow(row)
    return buffer.getvalue()


def render_dashboard(records: list[dict[str, Any]]) -> str:
    """Render the Content Inventory and Ownership Map dashboard page."""
    flagged = [record for record in records if record["flagged_short"]]
    broken = [record for record in records if record["outbound_broken_links"]]
    header = (
        "| Route | Status | Words | Last Reviewed | Inbound | Broken Outbound |\n"
        "| --- | --- | ---: | --- | ---: | ---: |\n"
    )
    rows = "\n".join(
        f"| `{record['route']}` | {record['status']} | {record['word_count']} | "
        f"{record['last_reviewed'] or '—'} | {record['inbound_links']} | "
        f"{len(record['outbound_broken_links'])} |"
        for record in records
    )
    flagged_section = (
        "\n".join(f"- `{record['route']}` ({record['word_count']} words)" for record in flagged)
        if flagged
        else "None."
    )
    broken_section = (
        "\n".join(
            f"- `{record['route']}`: " + ", ".join(record["outbound_broken_links"])
            for record in broken
        )
        if broken
        else "None."
    )
    return (
        "---\n"
        'title: "Content Inventory and Ownership Map"\n'
        'description: "Generated inventory of published Quarto (.qmd) content pages across the '
        'site: word count, status, last-reviewed date, canonical pointer, and link health"\n'
        "categories:\n- site-information\n"
        "---\n\n"
        "Generated by `scripts/generate_content_inventory.py` from published Quarto (.qmd) content "
        f"pages across the site. Committed snapshot baseline as of 2026-09-30 (schema version "
        f"`{SCHEMA_VERSION}`). {len(records)} pages, {len(flagged)} flagged as short (fewer than "
        f"{SHORT_PAGE_WORD_THRESHOLD} words with no Planned status), {len(broken)} with "
        "outbound broken links. Machine-readable copies: `data/content/inventory.json` and "
        "`data/content/inventory.csv`.\n\n"
        "## Consolidation and Retirement Candidates\n\n"
        f"{flagged_section}\n\n"
        "## Outbound Broken Links\n\n"
        f"{broken_section}\n\n"
        "## Full Inventory\n\n"
        f"{header}{rows}\n\n"
        "## Related Articles\n\n"
        "- [Development Roadmap](development-roadmap.html) — Content-review process and "
        "planning authorities\n"
        "- [Tools](tools.html) — Interactive tools and converters index\n"
        "- [Resources Hub](../resources/resources.html) — Curated resources and reviews\n"
    )


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n", maxsplit=1)[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-output", type=Path, default=JSON_OUTPUT)
    parser.add_argument("--csv-output", type=Path, default=CSV_OUTPUT)
    parser.add_argument("--dashboard-output", type=Path, default=DASHBOARD_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    args = _parse_args(argv)
    records = build_inventory(args.root)
    outputs = {
        args.json_output: render_json(records),
        args.csv_output: render_csv(records),
        args.dashboard_output: render_dashboard(records),
    }
    try:
        for path, content in outputs.items():
            write_or_check(path, content, args.check)
    except ValueError as exc:
        write_stderr(str(exc))
        return 1
    action = "verified" if args.check else "generated"
    write_stdout(f"{action} content inventory for {len(records)} page(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
