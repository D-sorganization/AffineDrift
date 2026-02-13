"""Shared CLI boundary contract helpers."""

from __future__ import annotations


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
