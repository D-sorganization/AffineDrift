"""Article front matter schema validation and allowlist enforcement (WEB-03.1 #4506).

Loads and enforces schemas/article-front-matter-v1.schema.json against article front matter.
Enforces:
1. Canonical publication status from WEB-04.1.
2. Audience level (intro, intermediate, advanced, research).
3. Plain-language summary (maximum 60 words).
4. Key takeaways (3 to 5 items).
5. Explicit prohibition of 'date: today'.
6. Governed evidence-rung (WEB-04.3).
7. Strict validation for core pages with an allowlist for pages in migration.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from src.core.contracts import require

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPO_ROOT / "schemas" / "article-front-matter-v1.schema.json"
ALLOWLIST_PATH = REPO_ROOT / "config" / "article-front-matter-allowlist.yml"

_CACHED_SCHEMA: dict[str, Any] | None = None
_CACHED_VALIDATOR: Any = None
_CACHED_ALLOWLIST: dict[str, Any] | None = None


def load_article_frontmatter_schema(schema_path: Path | None = None) -> dict[str, Any]:
    """Load the article front matter JSON schema."""
    global _CACHED_SCHEMA, _CACHED_VALIDATOR
    target_path = schema_path or SCHEMA_PATH
    if schema_path is None and _CACHED_SCHEMA is not None:
        return _CACHED_SCHEMA

    require(target_path.is_file(), f"Article front matter schema not found: {target_path}")
    raw_text = target_path.read_text(encoding="utf-8")
    loaded = json.loads(raw_text)
    require(isinstance(loaded, dict), "Schema must be a JSON object")
    require("$id" in loaded, "Schema must declare $id")
    data: dict[str, Any] = loaded

    if schema_path is None:
        _CACHED_SCHEMA = data
        _CACHED_VALIDATOR = jsonschema.Draft202012Validator(data)
    return data


def get_schema_validator(schema_path: Path | None = None) -> Any:
    """Return a compiled jsonschema validator for the article front matter schema."""
    global _CACHED_VALIDATOR
    if schema_path is None and _CACHED_VALIDATOR is not None:
        return _CACHED_VALIDATOR
    schema = load_article_frontmatter_schema(schema_path)
    validator = jsonschema.Draft202012Validator(schema)
    if schema_path is None:
        _CACHED_VALIDATOR = validator
    return validator


def load_frontmatter_allowlist(allowlist_path: Path | None = None) -> dict[str, Any]:
    """Load the front matter allowlist configuration."""
    global _CACHED_ALLOWLIST
    target_path = allowlist_path or ALLOWLIST_PATH
    if allowlist_path is None and _CACHED_ALLOWLIST is not None:
        return _CACHED_ALLOWLIST

    if not target_path.is_file():
        return {"core_pages": [], "allowlist": []}

    data = yaml.safe_load(target_path.read_text(encoding="utf-8")) or {}
    require(isinstance(data, dict), "Allowlist config must be a YAML mapping")
    require("core_pages" in data, "Allowlist config must contain 'core_pages'")
    require("allowlist" in data, "Allowlist config must contain 'allowlist'")

    if allowlist_path is None:
        _CACHED_ALLOWLIST = data
    return data


def normalize_rel_path(path: Path | str) -> str:
    """Convert path to forward-slash string relative to repo root if inside repo."""
    p = Path(path)
    try:
        rel = p.resolve().relative_to(REPO_ROOT.resolve())
        return rel.as_posix()
    except ValueError:
        return p.as_posix()


def _check_content_constraints(fm: dict[str, Any], norm_path: str) -> list[str]:
    """Validate summary word count, takeaways count, and caveats structure."""
    errors: list[str] = []
    summary_plain = fm.get("summary-plain")
    if summary_plain and isinstance(summary_plain, str):
        words = re.findall(r"\b\w+\b", summary_plain)
        if len(words) > 60:
            errors.append(
                f"{norm_path}: 'summary-plain' exceeds 60 words (found {len(words)} words)"
            )

    takeaways = fm.get("key-takeaways")
    if takeaways is not None:
        if not isinstance(takeaways, list) or not (3 <= len(takeaways) <= 5):
            errors.append(f"{norm_path}: 'key-takeaways' must contain between 3 and 5 items")

    caveats = fm.get("caveats")
    if caveats is not None:
        from src.tools.caveats_block import validate_caveats_dict

        for ce in validate_caveats_dict(caveats):
            errors.append(f"{norm_path}: {ce}")

    return errors


def validate_article_frontmatter(
    fm: dict[str, Any],
    rel_path: str,
    *,
    schema_path: Path | None = None,
    allowlist_config: dict[str, Any] | None = None,
) -> list[str]:
    """Validate article YAML frontmatter against schema and project rules.

    Returns a list of error messages (empty if valid).
    """
    errors: list[str] = []
    norm_path = rel_path.replace("\\", "/")

    # Rule 1: date: today is strictly forbidden everywhere
    date_val = str(fm.get("date", "")).strip().lower()
    if date_val == "today":
        errors.append(f"{norm_path}: 'date: today' is prohibited. Use a real publication date.")

    cfg = allowlist_config if allowlist_config is not None else load_frontmatter_allowlist()
    core_pages = set(cfg.get("core_pages", []))
    allowlisted_pages = set(cfg.get("allowlist", []))

    is_core = norm_path in core_pages
    is_allowlisted = norm_path in allowlisted_pages

    # If it is allowlisted and not core, full schema validation is deferred
    if is_allowlisted and not is_core:
        return errors

    # If the file is not a core page and not located under articles/, skip article schema check
    if not is_core and not norm_path.startswith("articles/"):
        return errors

    # Core pages and un-allowlisted pages must strictly conform to the schema
    validator = get_schema_validator(schema_path)
    for err in validator.iter_errors(fm):
        field = ".".join(str(p) for p in err.path) if err.path else "root"
        errors.append(f"{norm_path}: schema error at '{field}': {err.message}")

    errors.extend(_check_content_constraints(fm, norm_path))
    return errors
