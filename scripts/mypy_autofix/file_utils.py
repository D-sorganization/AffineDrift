from __future__ import annotations

import re
from pathlib import Path

from .models import MypyError


def read_file_lines(filepath: str) -> list[str]:
    """Read file and return lines (preserving newlines)."""
    path = Path(filepath)
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


def write_file_lines(filepath: str, lines: list[str]) -> None:
    """Write lines back to file."""
    Path(filepath).write_text("".join(lines), encoding="utf-8")


def has_type_ignore(line: str, code: str | None = None) -> bool:
    """Check if a line already has a type: ignore comment."""
    if "# type: ignore" in line:
        if code and f"[{code}]" in line:
            return True
        if code is None:
            return True
        # Has a blanket ignore
        if "# type: ignore\n" in line or line.rstrip().endswith("# type: ignore"):
            return True
    return False


def add_type_ignore(line: str, code: str) -> str:
    """Add # type: ignore[code] to a line."""
    stripped = line.rstrip("\n\r")
    # Check if there's already an inline comment
    if "# type: ignore" in stripped:
        # Already has type ignore - add our code to existing bracket
        if re.search(r"# type: ignore\[([^\]]+)\]", stripped):
            return (
                re.sub(
                    r"# type: ignore\[([^\]]+)\]",
                    rf"# type: ignore[\1, {code}]",
                    stripped,
                )
                + "\n"
            )
        return stripped + "\n"  # Has blanket ignore, leave it
    if "#" in stripped:
        # Has another comment - add before existing comment's content
        return stripped + f"  # type: ignore[{code}]\n"
    return stripped + f"  # type: ignore[{code}]\n"


def get_line_indent(line: str) -> str:
    """Get the leading whitespace of a line."""
    return line[: len(line) - len(line.lstrip())]


def _get_error_line(
    lines: list[str],
    error: MypyError,
) -> tuple[int, str] | None:
    """Return (index, line) for the error, or None if out of bounds."""
    idx = error.line - 1
    if idx >= len(lines):
        return None
    return (idx, lines[idx])


def is_safe_path(filepath: str) -> bool:
    """Check if a file is safe to modify."""
    path = Path(filepath)
    # Only modify src/ and tests/ directories
    parts = path.parts
    if not any(p in ("src", "tests") for p in parts):
        return False
    # Never modify __pycache__, .git, vendor files
    if any(p.startswith(".") or p == "__pycache__" or p == "vendor" for p in parts):
        return False
    # Only modify .py files
    return path.suffix == ".py"


def _ensure_import(lines: list[str], import_statement: str) -> bool:
    """Add an import statement if not already present.

    Inserts after the last existing import from the same module.
    Returns True if import was added.
    """
    # Check if already imported
    for line in lines:
        if import_statement in line:
            return False

    # Find the right place to insert
    # Look for the last import line before any code
    last_import_idx = -1
    in_docstring = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            if in_docstring:
                in_docstring = False
                continue
            if stripped.count('"""') == 1 or stripped.count("'''") == 1:
                in_docstring = True
                continue
        if in_docstring:
            continue
        if stripped.startswith(("import ", "from ")):
            last_import_idx = i
        elif stripped and not stripped.startswith("#") and last_import_idx >= 0:
            break  # Hit non-import code after imports

    if last_import_idx >= 0:
        lines.insert(last_import_idx + 1, import_statement + "\n")
    else:
        # No imports found, add after module docstring or at top
        insert_at = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                # Skip past docstring
                if stripped.count('"""') >= 2 or stripped.count("'''") >= 2:
                    insert_at = i + 1
                    break
                for j in range(i + 1, len(lines)):
                    if '"""' in lines[j] or "'''" in lines[j]:
                        insert_at = j + 1
                        break
                break
            elif stripped and not stripped.startswith("#"):
                insert_at = i
                break
        lines.insert(insert_at, import_statement + "\n")
    return True
