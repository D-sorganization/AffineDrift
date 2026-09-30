"""Standard "Where Next" Footer component generator and validator (WEB-03.5 #4510).

Acceptance Criteria:
1. No page links to itself (strictly validated).
2. Each core page has at least one "simpler" and one "deeper" link.
3. Coordinated with #3900 (reference cluster) and #3901 (motor-control / neuro cluster).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from src.tools.utils import escape_html

# The authoritative list of Core Pages defined under WEB-03.8 / issue #4510
CORE_PAGES: tuple[str, ...] = (
    "articles/theory-part1.qmd",
    "articles/theory-part2.qmd",
    "articles/theory-part3.qmd",
    "articles/theory-part4.qmd",
    "articles/theory-part5.qmd",
    "articles/affine-nature-golf-swing.qmd",
    "articles/zero-torque-counterfactual.qmd",
    "articles/controllability-drift-ratio.qmd",
    "articles/superposition.qmd",
    "articles/tangent-hyperplanes-series/part-1-geometry.qmd",
    "articles/tangent-hyperplanes-series/part-2-dynamics.qmd",
    "articles/tangent-hyperplanes-series/part-3-control.qmd",
    "articles/tangent-hyperplanes-series/part-4-residuals-curvature.qmd",
    "articles/tangent-hyperplanes-series/part-5-contraction.qmd",
    "articles/tangent-hyperplanes-series/part-6-hybrid.qmd",
    "articles/tangent-hyperplanes-series/part-7-residual-aware.qmd",
    "articles/drift-components-wrench-double-pendulum.qmd",
    "articles/inverse-dynamics.qmd",
    "articles/inverse-dynamics-inference.qmd",
    "articles/proximal-distal-energy-transfer.qmd",
    "articles/proximal-distal-a-journey-through-the-swing.qmd",
    "articles/technology-force-measurement.qmd",
    "articles/technology-launch-monitors.qmd",
    "articles/technology-motion-capture.qmd",
    "articles/technology-club-fitting.qmd",
    "articles/technology-heavy-hit-impact-coupling.qmd",
    "books/index.qmd",
    "articles/The_Physics_of_Golf/quarto/index.qmd",
    "articles/The_Geometry_of_Motion/quarto/index.qmd",
    "articles/proximal_distal_energy_transfer/index.qmd",
)


def load_where_next_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load config/where_next.yml from repo or specified path."""
    if config_path is None:
        repo_root = Path(__file__).resolve().parents[2]
        config_path = repo_root / "config" / "where_next.yml"
    if not config_path.exists():
        raise FileNotFoundError(f"Where Next config not found: {config_path}")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    return data


def normalize_page_key(path_str: str) -> str:
    """Normalize a path to a forward-slash key matching config."""
    p = path_str.replace("\\", "/").strip().lstrip("/")
    if p.endswith(".html"):
        p = p[:-5] + ".qmd"
    return p


def compute_relative_href(from_page: str, target_href: str) -> str:
    """Compute relative href from the directory of from_page to target_href."""
    if target_href.startswith(("http://", "https://", "#", "mailto:")):
        return target_href

    clean_target = target_href.split("#")[0].replace("\\", "/").lstrip("/")
    target_fragment = ("#" + target_href.split("#", 1)[1]) if "#" in target_href else ""

    from_dir = os.path.dirname(from_page.replace("\\", "/").lstrip("/"))
    if not from_dir:
        rel = clean_target
    else:
        rel = os.path.relpath(clean_target, from_dir).replace("\\", "/")

    return rel + target_fragment


def _check_missing_core_pages(config: dict[str, Any]) -> list[str]:
    """Check that all required core pages are present in configuration."""
    errors: list[str] = []
    for core_page in CORE_PAGES:
        norm_core = normalize_page_key(core_page)
        if norm_core not in config:
            errors.append(f"Missing required core page in where_next config: {core_page}")
    return errors


def _check_core_page_completeness(
    page_key: str, page_norm: str, entry: dict[str, Any]
) -> list[str]:
    """Verify that a core page has at least one simpler and one deeper link."""
    errors: list[str] = []
    core_norm_keys = [normalize_page_key(cp) for cp in CORE_PAGES]
    if page_norm in core_norm_keys:
        simpler = entry.get("simpler")
        if not simpler or not isinstance(simpler, list) or len(simpler) == 0:
            errors.append(f"Core page {page_key} must have at least one 'simpler' link")
        deeper = entry.get("deeper")
        if not deeper or not isinstance(deeper, list) or len(deeper) == 0:
            errors.append(f"Core page {page_key} must have at least one 'deeper' link")
    return errors


def _parse_section_items(
    page_key: str, section: str, val: Any, errors: list[str]
) -> list[tuple[str, dict[str, Any]]]:
    """Parse section value into a list of (section, link_dict) tuples."""
    if val is None:
        return []
    if isinstance(val, dict):
        return [(section, val)]
    if isinstance(val, list):
        items: list[tuple[str, dict[str, Any]]] = []
        for item in val:
            if isinstance(item, dict):
                items.append((section, item))
            else:
                errors.append(f"{page_key}: items in '{section}' must be dictionaries")
        return items
    errors.append(f"{page_key}: '{section}' must be a dictionary or list")
    return []


def _collect_entry_links(
    page_key: str, entry: dict[str, Any], errors: list[str]
) -> list[tuple[str, dict[str, Any]]]:
    """Collect all defined section links for a page entry."""
    links: list[tuple[str, dict[str, Any]]] = []
    all_sections = ("series-prev", "series-next", "simpler", "deeper", "evidence", "try-it")
    for section in all_sections:
        links.extend(_parse_section_items(page_key, section, entry.get(section), errors))
    return links


def _validate_link_target(
    page_key: str,
    page_norm: str,
    section: str,
    link_obj: dict[str, Any],
    repo_root: Path,
) -> list[str]:
    """Validate that a link target exists, is well-formed, and is not a self-link."""
    errors: list[str] = []
    href = link_obj.get("href")
    if not href or not isinstance(href, str):
        return [f"{page_key}: link in '{section}' missing 'href'"]
    title = link_obj.get("title")
    if not title or not isinstance(title, str):
        errors.append(f"{page_key}: link '{href}' in '{section}' missing 'title'")

    clean_href = href.split("#")[0].strip()
    if not clean_href or clean_href.startswith(("http://", "https://", "mailto:")):
        return errors

    target_norm = normalize_page_key(clean_href)
    if target_norm == page_norm:
        errors.append(
            f"Self-link violation (Criterion 1): {page_key} links to itself in '{section}' ({href})"
        )

    clean_rel = clean_href.replace("\\", "/").lstrip("/")
    if clean_rel.endswith(".html"):
        stem_rel = clean_rel[:-5]
        candidates = [
            repo_root / f"{stem_rel}.qmd",
            repo_root / f"{stem_rel}.md",
            repo_root / f"{stem_rel}.html",
            repo_root / "docs" / clean_rel,
        ]
    else:
        candidates = [repo_root / clean_rel, repo_root / "docs" / clean_rel]

    if not any(c.exists() for c in candidates):
        errors.append(f"{page_key}: link target does not exist on disk: {href} ({target_norm})")

    return errors


def validate_where_next_config(
    config: dict[str, Any],
    repo_root: Path,
) -> list[str]:
    """Validate where_next configuration against requirements."""
    errors: list[str] = _check_missing_core_pages(config)

    for page_key, entry in config.items():
        page_norm = normalize_page_key(page_key)
        page_disk_path = repo_root / page_norm
        if not page_disk_path.exists():
            errors.append(f"Configured page key does not exist on disk: {page_key} ({page_norm})")

        if not isinstance(entry, dict):
            errors.append(f"Entry for {page_key} must be a dictionary")
            continue

        errors.extend(_check_core_page_completeness(page_key, page_norm, entry))
        links_to_check = _collect_entry_links(page_key, entry, errors)

        for section, link_obj in links_to_check:
            errors.extend(_validate_link_target(page_key, page_norm, section, link_obj, repo_root))

    return errors


def _render_series_banner(entry: dict[str, Any], current_page: str) -> str | None:
    """Render the series progression banner containing previous and next links."""
    series_prev = entry.get("series-prev")
    series_next = entry.get("series-next")
    if not series_prev and not series_next:
        return None

    series_items: list[str] = []
    if series_prev and isinstance(series_prev, dict):
        prev_href = escape_html(compute_relative_href(current_page, series_prev["href"]))
        prev_title = escape_html(series_prev.get("title", "Previous"))
        series_items.append(
            f'<a href="{prev_href}" class="where-next-link where-next-link--prev">'
            f'<span class="where-next-direction">&larr; Previous in Series</span>'
            f'<span class="where-next-link-title">{prev_title}</span></a>'
        )
    if series_next and isinstance(series_next, dict):
        next_href = escape_html(compute_relative_href(current_page, series_next["href"]))
        next_title = escape_html(series_next.get("title", "Next"))
        series_items.append(
            f'<a href="{next_href}" class="where-next-link where-next-link--next">'
            f'<span class="where-next-direction">Next in Series &rarr;</span>'
            f'<span class="where-next-link-title">{next_title}</span></a>'
        )

    return (
        '<div class="where-next-series" role="group" aria-label="Series progression">\n'
        + "\n".join(series_items)
        + "\n</div>"
    )


def _render_column_section(
    column_class: str,
    title: str,
    icon_entity: str,
    items_data: Any,
    current_page: str,
) -> str | None:
    """Render a where-next column section (e.g., simpler, deeper, evidence, try-it)."""
    if not items_data:
        return None
    items = items_data if isinstance(items_data, list) else [items_data]

    items_html: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        href = escape_html(compute_relative_href(current_page, item["href"]))
        link_title = escape_html(item.get("title", ""))
        blurb = item.get("blurb")
        blurb_html = f'<p class="where-next-blurb">{escape_html(blurb)}</p>' if blurb else ""
        items_html.append(
            f'<li class="where-next-item">'
            f'<a href="{href}" class="where-next-item-link">{link_title}</a>'
            f"{blurb_html}</li>"
        )

    if not items_html:
        return None

    return (
        f'<div class="where-next-column where-next-column--{column_class}">\n'
        f'<h3 class="where-next-subtitle"><span class="where-next-icon" aria-hidden="true">'
        f"{icon_entity}</span> {escape_html(title)}</h3>\n"
        f'<ul class="where-next-list">\n' + "\n".join(items_html) + "\n</ul>\n</div>"
    )


def render_where_next_html(entry: dict[str, Any], current_page: str) -> str:
    """Render the accessible semantic HTML for the Where Next card."""
    sections_html: list[str] = []

    series_banner = _render_series_banner(entry, current_page)
    if series_banner:
        sections_html.append(series_banner)

    columns: list[str] = []
    col_configs = [
        ("simpler", "Go Simpler", "&#9662;", entry.get("simpler")),
        ("deeper", "Go Deeper", "&#9652;", entry.get("deeper")),
        ("evidence", "See the Evidence", "&#9745;", entry.get("evidence")),
        ("try-it", "Try It", "&#9881;", entry.get("try-it")),
    ]
    for col_class, title, icon, data in col_configs:
        rendered = _render_column_section(col_class, title, icon, data, current_page)
        if rendered:
            columns.append(rendered)

    if columns:
        sections_html.append('<div class="where-next-grid">\n' + "\n".join(columns) + "\n</div>")

    return (
        '<nav class="where-next-card" aria-label="Where to go next">\n'
        '  <h2 class="where-next-title unlisted unnumbered">Where Next</h2>\n'
        + "\n".join(f"  {s}" for s in sections_html)
        + "\n</nav>"
    )
