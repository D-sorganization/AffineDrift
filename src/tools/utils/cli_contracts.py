"""Shared CLI boundary contract helpers."""

from __future__ import annotations

from pathlib import Path

from src.core.contracts import require


def parse_csv_enum(
    raw: str,
    *,
    allowed: set[str],
    aliases: dict[str, set[str]] | None = None,
    value_name: str = "value",
) -> set[str]:
    """Parse comma-separated tokens and validate against allowed values.

    Args:
        raw: Comma-separated token string.
        allowed: Allowed terminal values.
        aliases: Optional alias-to-values expansion mapping.
        value_name: Label used in error messages.

    Returns:
        Normalized set of parsed values.

    Raises:
        ValueError: If unknown tokens are present.
    """
    require(len(allowed) > 0, "allowed set must not be empty")
    alias_map = aliases or {}
    tokens = {item.strip().lower() for item in raw.split(",") if item.strip()}
    resolved: set[str] = set()

    for token in tokens:
        if token in alias_map:
            resolved.update(alias_map[token])
        else:
            resolved.add(token)

    unknown = sorted(item for item in resolved if item not in allowed)
    if unknown:
        raise ValueError(
            f"Unsupported {value_name}: {', '.join(unknown)}. "
            f"Allowed: {', '.join(sorted(allowed | set(alias_map)))}"
        )

    return resolved


def ensure_existing_file(raw_path: str, *, value_name: str = "path") -> Path:
    """Validate that a CLI path argument points to an existing file."""
    path = Path(raw_path)
    if not path.exists() or not path.is_file():
        raise ValueError(f"{value_name} must be an existing file: {raw_path}")
    return path


def ensure_existing_dir(raw_path: str, *, value_name: str = "path") -> Path:
    """Validate that a CLI path argument points to an existing directory."""
    path = Path(raw_path)
    if not path.exists() or not path.is_dir():
        raise ValueError(f"{value_name} must be an existing directory: {raw_path}")
    return path
