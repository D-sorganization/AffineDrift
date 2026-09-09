"""Page scanning and link resolution helpers for the site link gate."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from src.tools.utils.link_utils import (
    ALL_LINK_PATTERNS,
    is_external_url,
    normalize_internal_url,
    path_exists_in_search_roots,
    resolve_relative_path,
)

logger = logging.getLogger(__name__)

NAV_FILE = "_quarto.yml"

#: Top-level directories that hold rendered content pages.
CONTENT_DIRS: tuple[str, ...] = (
    "articles",
    "pages",
    "resources",
    "models",
    "repositories",
    "books",
)

#: Book trees whose .qmd files (except their index pages) are book chapters.
#: These are covered by the per-chapter bridge program (#3905), not by the
#: Related Articles content-page rule.
BOOK_TREES: tuple[str, ...] = (
    "articles/The_Physics_of_Golf",
    "articles/The_Geometry_of_Motion",
    "articles/proximal_distal_companion",
    "articles/proximal_distal_energy_transfer",
    "articles/tangent-hyperplane-contraction/chapters",
)


def _pattern_to_regex(pattern: str) -> re.Pattern[str] | None:
    """Translate a Quarto render glob into a regex over POSIX paths."""
    pattern = pattern.strip()
    if pattern.startswith("!"):
        pattern = pattern[1:]
    regex = re.escape(pattern).replace(r"\*\*/", r"(?:[^/]+/)*").replace(r"\*", r"[^/]+")
    if regex.endswith(r"\.qmd") or regex.endswith(r"\.md"):
        return re.compile(rf"^{regex}$")
    return None


def rendered_relative_paths(root: Path) -> set[str] | None:
    """Return the site's rendered source paths per _quarto.yml, or None.

    Returns None when no render list is declared, meaning every
    front-matter page is considered rendered.
    """
    nav = root / NAV_FILE
    if not nav.is_file():
        return None
    try:
        data = yaml.safe_load(nav.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        logger.warning("Could not parse %s: %s", NAV_FILE, exc)
        return None
    project = data.get("project")
    render_list = project.get("render") if isinstance(project, dict) else None
    if not isinstance(render_list, list):
        return None
    positives: list[re.Pattern[str]] = []
    negatives: list[re.Pattern[str]] = []
    for pattern in render_list:
        if not isinstance(pattern, str):
            continue
        regex = _pattern_to_regex(pattern)
        if regex is None:
            continue
        if pattern.lstrip().startswith("!"):
            negatives.append(regex)
        else:
            positives.append(regex)
    return {"positives": positives, "negatives": negatives}


def is_rendered(rel: str, render_set: dict | None) -> bool:
    """Return True if a POSIX source path is covered by the render list."""
    if render_set is None:
        return True
    if any(pattern.match(rel) for pattern in render_set["negatives"]):
        return False
    return any(pattern.match(rel) for pattern in render_set["positives"])


def find_content_pages(root: Path) -> list[Path]:
    """Find rendered content pages: front-matter .qmd files in CONTENT_DIRS."""
    pages: list[Path] = []
    render_set = rendered_relative_paths(root)
    for content_dir in CONTENT_DIRS:
        base = root / content_dir
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.qmd")):
            if not _has_front_matter(path):
                continue
            rel = path.relative_to(root).as_posix()
            if not is_rendered(rel, render_set):
                continue
            pages.append(path)
    return pages


RELATED_MIN_LINKS = 3

MAX_INCLUDE_DEPTH = 8

INCLUDE_PATTERN = re.compile(r"\{\{<\s*include\s+(\S+?)\s*>\}\}")
HEADING_SPLIT_PATTERN = re.compile(r"^##\s", re.MULTILINE)
INLINE_CATEGORIES_PATTERN = re.compile(r"^categories:\s*\[", re.MULTILINE)
FENCE_PATTERN = re.compile(r"```(?!\{)[^\n]*\n.*?```", re.DOTALL)


@dataclass(frozen=True)
class Link:
    """A link URL extracted from page content."""

    url: str


def is_book_chapter(rel: Path | str) -> bool:
    """Return True if the content-relative path is a book chapter page."""
    rel = Path(rel)
    if rel.name == "index.qmd":
        return False
    posix = rel.as_posix()
    return posix.startswith(tuple(f"{tree}/" for tree in BOOK_TREES))


def _has_front_matter(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        logger.warning("Could not read %s: %s", path, exc)
        return False
    return text.startswith("---\n")


def parse_front_matter(text: str) -> dict:
    """Parse the YAML front matter block of a page; empty dict when absent."""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        data = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def page_body(text: str) -> str:
    """Return page content with the front matter block removed."""
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    return text[end + 4 :]


def strip_code(content: str) -> str:
    """Remove fenced code blocks so example links are not validated.

    Quarto raw ``{=html}`` blocks are content, not code: they are kept
    (and their links validated).
    """
    out: list[str] = []
    in_fence = False
    raw_block = False
    for line in content.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            info = stripped[3:].strip()
            if not in_fence:
                in_fence = True
                raw_block = info.startswith("{")
                if raw_block:
                    out.append(line)
                continue
            in_fence = False
            if raw_block:
                out.append(line)
                raw_block = False
            continue
        if in_fence and not raw_block:
            continue
        out.append(line)
    return "".join(out)


def extract_links(content: str) -> list[Link]:
    """Extract link URLs (markdown links, HTML href/src) from content."""
    urls: list[Link] = []
    seen: set[str] = set()
    for pattern in ALL_LINK_PATTERNS:
        for match in pattern.finditer(content):
            url = match.group(1).strip()
            if url and url not in seen:
                seen.add(url)
                urls.append(Link(url))
    return urls


def expand_includes(root: Path, page: Path, _depth: int = 0) -> str:
    """Return page content with ``{{< include >}}`` blocks spliced in.

    Included paths resolve relative to the including page. Cycles are cut
    and the include depth is bounded.
    """
    if _depth > MAX_INCLUDE_DEPTH:
        logger.warning("Include depth exceeded at %s", page)
        return ""
    text = page.read_text(encoding="utf-8", errors="ignore")

    def _sub(match: re.Match[str]) -> str:
        target = page.parent / match.group(1)
        if not target.is_file():
            return match.group(0)
        return expand_includes(root, target, _depth + 1)

    return INCLUDE_PATTERN.sub(_sub, text)


def _resolve_target(root: Path, source_file: Path, url: str) -> Path | None:
    """Resolve a URL to its source-tree path, or None when unresolvable."""
    if is_external_url(url) or url.startswith("#") or url.startswith("mailto:"):
        return None
    normalized = normalize_internal_url(url)
    if normalized is None:
        return None
    return resolve_relative_path(root=root, source_file=source_file, url=normalized)


def _target_exists(root: Path, target: Path) -> bool:
    if target.exists():
        return True
    # A rendered .html target may map back to a .qmd or .md source page.
    if target.suffix == ".html" and (
        target.with_suffix(".qmd").exists() or target.with_suffix(".md").exists()
    ):
        return True
    # Links into a directory (trailing slash or bare) resolve to its index.
    if target.is_dir():
        return True
    if target.suffix == "" and (target / "index.qmd").exists():
        return True
    if (target / "index.html").exists():
        return True
    return path_exists_in_search_roots(root=root, target=target)
