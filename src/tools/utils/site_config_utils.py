"""Site configuration and navigation parsing for link-quality checks.

Parses the render source set and navigation graph of a Quarto website
project so the link checks in ``link_checks`` can reason about which
pages are rendered and how they are reachable.

Design by Contract:
    - All functions are deterministic and side-effect free given the
      project root.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from src.tools.utils.link_utils import normalize_internal_url, page_target_key

logger = logging.getLogger(__name__)

#: Fallback render pattern when ``_quarto.yml`` declares none
DEFAULT_RENDER_GLOB = "*.qmd"

#: Directories never searched for nested navigation configs
SKIP_DIR_PARTS = frozenset({"node_modules", "_site", "archive", "legacy-pages"})


@dataclass(frozen=True)
class RenderPatterns:
    """Include/exclude glob patterns from the project render config.

    Attributes:
        includes: Glob patterns of rendered source paths.
        excludes: Glob patterns subtracted from the includes.
    """

    includes: tuple[str, ...]
    excludes: tuple[str, ...]


def load_yaml_config(path: Path) -> dict[str, Any]:
    """Load a YAML file, returning an empty dict when absent or empty.

    Args:
        path: The YAML file path.

    Returns:
        Parsed mapping, or an empty dict when the file is missing,
        unreadable, or not a mapping.
    """
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8", errors="ignore"))
    except yaml.YAMLError as exc:
        logger.warning("Could not parse %s: %s", path, exc)
        return {}
    return data if isinstance(data, dict) else {}


def load_render_patterns(root: Path) -> RenderPatterns:
    """Load render include/exclude globs from the root ``_quarto.yml``.

    Args:
        root: The project root directory.

    Returns:
        Include and exclude glob patterns; negated ``!pattern`` entries
        become excludes, with a ``*.qmd`` fallback when none declared.
    """
    data = load_yaml_config(root / "_quarto.yml")
    render = data.get("project", {}).get("render", []) or []
    includes = tuple(p for p in render if not p.startswith("!"))
    excludes = tuple(p[1:] for p in render if p.startswith("!"))
    return RenderPatterns(includes or (DEFAULT_RENDER_GLOB,), excludes)


def _iter_nav_targets(node: Any) -> Iterator[str]:
    """Yield ``href`` values and ``chapters`` entries from a nav tree."""
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, str) and key == "href":
                yield value
            elif key == "chapters" and isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        yield item
                    else:
                        yield from _iter_nav_targets(item)
            else:
                yield from _iter_nav_targets(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_nav_targets(item)


def collect_nav_pages(root: Path) -> set[str]:
    """Collect page keys reachable from project navigation configs.

    Every ``_quarto.yml`` contributes its ``href`` values and book
    ``chapters`` entries, resolved relative to that config file's
    directory (over-traversal clamped to the project root).

    Args:
        root: The project root directory.

    Returns:
        Canonical page keys (root-relative POSIX paths) reachable from nav.
    """
    pages: set[str] = set()
    for yml in sorted(root.glob("**/_quarto.yml")):
        if any(part in SKIP_DIR_PARTS for part in yml.relative_to(root).parts):
            continue
        data = load_yaml_config(yml)
        for target in _iter_nav_targets(data):
            normalized = normalize_internal_url(target)
            if normalized is None:
                continue
            key = page_target_key(root=root, source_file=yml, url=normalized)
            if key:
                pages.add(key)
    return pages
