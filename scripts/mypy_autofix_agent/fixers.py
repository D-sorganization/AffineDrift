"""Mypy auto-fix strategies - extracted from mypy_autofix_agent.py."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def apply_type_ignore(file_path: str, line_num: int, error_code: str) -> bool:
    """Add # type: ignore[error_code] to the specified line."""
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
        idx = line_num - 1
        if 0 <= idx < len(lines):
            line = lines[idx].rstrip("\n")
            if "# type: ignore" not in line:
                lines[idx] = f"{line}  # type: ignore[{error_code}]\n"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                return True
    except Exception as exc:
        logger.warning("Failed to apply type ignore: %s", exc)
    return False
