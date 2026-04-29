"""Centralized constants for AffineDrift tools.

This module provides shared constants to avoid DRY violations across the codebase.
All tools should import exclusion lists and other shared constants from here.

Example:
    from src.tools.utils.constants import EXCLUDE_DIRS, EXCLUDE_FILES
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Common directories to exclude when searching for source files
EXCLUDE_DIRS_PYTHON: frozenset[str] = frozenset(
    {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "env",
        "node_modules",
        ".tox",
        ".eggs",
        ".pytest_cache",
        "build",
        "dist",
        ".mypy_cache",
        ".ruff_cache",
        "content",
        "legacy",
        "Archive",
    }
)

# Directories to exclude for content files (QMD, HTML, etc.)
EXCLUDE_DIRS_CONTENT: frozenset[str] = frozenset(
    {
        "_site",
        ".quarto",
        "docs",
        "archive",
    }
)

# All excluded directories combined
EXCLUDE_DIRS: frozenset[str] = EXCLUDE_DIRS_PYTHON | EXCLUDE_DIRS_CONTENT

# Common files to skip during processing
EXCLUDE_FILES: frozenset[str] = frozenset(
    {
        "sitemap.xml",
        "search.json",
        "404.html",
        "offline.html",
    }
)

# Path replacement mappings for HTML templates
# Used by fix_relative_paths to avoid repetitive .replace() calls
PATH_REPLACEMENT_PATTERNS: tuple[tuple[str, str], ...] = (
    # ./ prefix replacements
    ('href="./', 'href="{prefix}'),
    ('src="./', 'src="{prefix}'),
    # site_libs replacements
    ('src="site_libs/', 'src="{prefix}site_libs/'),
    ('href="site_libs/', 'href="{prefix}site_libs/'),
    # Specific asset replacements
    ('src="script.js"', 'src="{prefix}script.js"'),
    ('href="styles.css"', 'href="{prefix}styles.css"'),
    ('src="logo/', 'src="{prefix}logo/'),
    # Root page link replacements
    ('href="index.html"', 'href="{prefix}index.html"'),
    ('href="about.html"', 'href="{prefix}about.html"'),
    ('href="feed.xml"', 'href="{prefix}feed.xml"'),
    ('href="favicon.ico"', 'href="{prefix}favicon.ico"'),
)

# HTML validation fix patterns: (pattern, replacement, description)
# Used by fix_html_validation.py to consolidate regex fixes
HTML_FIX_PATTERNS: tuple[tuple[str, str, str], ...] = (
    (r'crossorigin=""', "crossorigin", "boolean attribute normalization"),
    (r'\s+role="link"', "", "redundant role='link' on anchors"),
)

# ── LaTeX Environment Conversion Patterns ────────────────────────────────
# Shared regex patterns for LaTeX-to-{HTML,QMD} converters (DRY).

LATEX_ABSTRACT_PATTERN: str = r"\\begin\{abstract\}(.*?)\\end\{abstract\}"
"""Regex matching LaTeX abstract environments."""

LATEX_KEYPOINT_PATTERN: str = r"\\begin\{keypoint\}(?:\[[^\]]*\])?(.*?)\\end\{keypoint\}"
"""Regex matching LaTeX keypoint environments (with optional title)."""

LATEX_LIMITATION_PATTERN: str = r"\\begin\{limitation\}(?:\[[^\]]*\])?(.*?)\\end\{limitation\}"
"""Regex matching LaTeX limitation environments (with optional title)."""

LATEX_ALIGN_BEGIN_PATTERN: str = r"\\begin\{align\}"
"""Regex matching the start of a LaTeX align environment."""

LATEX_ALIGN_END_PATTERN: str = r"\\end\{align\}"
"""Regex matching the end of a LaTeX align environment."""

LATEX_EQUATION_BEGIN_PATTERN: str = r"\\begin\{equation\}"
"""Regex matching the start of a LaTeX equation environment."""

LATEX_EQUATION_END_PATTERN: str = r"\\end\{equation\}"
"""Regex matching the end of a LaTeX equation environment."""

LATEX_TIKZ_PATTERN: str = r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}"
"""Regex matching LaTeX tikzpicture environments."""

LATEX_CUSTOM_COMMAND_BVEC_PATTERN: str = r"\\bvec\{([^}]+)\}"
"""Regex matching custom \\bvec command."""

LATEX_CUSTOM_COMMAND_SYMBOLS_PATTERN: str = r"\\(Feq|Ceq|Rdrift|Rinput)"
"""Regex matching custom symbol commands (Feq, Ceq, etc.)."""
