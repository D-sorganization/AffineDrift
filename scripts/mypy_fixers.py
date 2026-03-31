"""Fix strategies for the Mypy Autofix Agent.

Each public function receives the file's lines (mutated in-place) and the
MypyError to fix.  A function returns a Fix on success or None when it
cannot handle the error.

Priority order (real fixes first, suppressions last) is defined by the
exported FIX_STRATEGIES list.
"""

from __future__ import annotations

import logging
import re

from scripts.mypy_models import (
    COMMON_TYPE_IMPORTS,
    GENERIC_SUPPRESSIBLE,
    IMPORT_SUPPRESSIBLE,
    Fix,
    MypyError,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Low-level line helpers
# ---------------------------------------------------------------------------


def get_line_indent(line: str) -> str:
    """Return the leading whitespace of *line*."""
    return line[: len(line) - len(line.lstrip())]


def has_type_ignore(line: str, code: str | None = None) -> bool:
    """Return True when *line* already carries a suitable ``# type: ignore``.

    Args:
        line: Source line text.
        code: Specific error code to look for inside brackets.  When None any
            ``# type: ignore`` annotation counts.
    """
    if "# type: ignore" not in line:
        return False
    if code and f"[{code}]" in line:
        return True
    if code is None:
        return True
    if "# type: ignore\n" in line or line.rstrip().endswith("# type: ignore"):
        return True
    return False


def add_type_ignore(line: str, code: str) -> str:
    """Append ``# type: ignore[code]`` to *line*, merging if one already exists.

    Args:
        line: Original source line.
        code: Mypy error code to suppress.

    Returns:
        Modified line ending with ``\\n``.
    """
    stripped = line.rstrip("\n\r")
    if "# type: ignore" in stripped:
        if re.search(r"# type: ignore\[([^\]]+)\]", stripped):
            return (
                re.sub(
                    r"# type: ignore\[([^\]]+)\]",
                    rf"# type: ignore[\1, {code}]",
                    stripped,
                )
                + "\n"
            )
        return stripped + "\n"  # blanket ignore already present
    return stripped + f"  # type: ignore[{code}]\n"


def _get_error_line(lines: list[str], error: MypyError) -> tuple[int, str] | None:
    """Return ``(index, line)`` for *error*, or None when out of bounds."""
    idx = error.line - 1
    if idx >= len(lines):
        return None
    return (idx, lines[idx])


def ensure_import(lines: list[str], import_statement: str) -> bool:
    """Insert *import_statement* into *lines* if it is not already present.

    The statement is inserted after the last existing import block.

    Args:
        lines: Source lines (mutated in-place).
        import_statement: Full import line, e.g. ``"from typing import Any"``.

    Returns:
        True when the import was added, False when it was already present.
    """
    for line in lines:
        if import_statement in line:
            return False

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
            break

    if last_import_idx >= 0:
        lines.insert(last_import_idx + 1, import_statement + "\n")
    else:
        insert_at = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
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


# ---------------------------------------------------------------------------
# Real-fix strategies
# ---------------------------------------------------------------------------


def fix_callable_as_type(lines: list[str], error: MypyError) -> Fix | None:
    """Replace bare ``callable`` type annotation with ``Callable[..., Any]``.

    This is a REAL fix - it rewrites the annotation and adds necessary imports.

    Args:
        lines: Source lines of the file (mutated in-place on success).
        error: The mypy error to fix.

    Returns:
        A Fix descriptor, or None when this strategy does not apply.
    """
    if error.code != "valid-type":
        return None
    if '"callable" is not valid as a type' not in error.message.lower():
        return None

    result = _get_error_line(lines, error)
    if result is None:
        return None
    idx, line = result

    if ": callable" in line.lower():
        original = line
        line = re.sub(r":\s*callable\b", ": Callable[..., Any]", line, flags=re.IGNORECASE)
        lines[idx] = line
        ensure_import(lines, "from collections.abc import Callable")
        ensure_import(lines, "from typing import Any")
        return Fix(
            file=error.file,
            line=error.line,
            description="Replace 'callable' with 'Callable[..., Any]'",
            strategy="real-fix",
            original_code=original.strip(),
        )
    return None


def fix_union_attr(lines: list[str], error: MypyError) -> Fix | None:
    """Narrow a union type with an ``assert isinstance(...)`` guard.

    This is a REAL fix - it inserts a narrowing assertion before the offending
    line so mypy can prove attribute access is safe.

    Args:
        lines: Source lines of the file (mutated in-place on success).
        error: The mypy ``union-attr`` error to fix.

    Returns:
        A Fix descriptor, or None when this strategy does not apply.
    """
    if error.code != "union-attr":
        return None

    match = re.search(
        r'Item "(\w+)" of "([^"]+)" has no attribute "(\w+)"',
        error.message,
    )
    if not match:
        return None

    bad_type, union_type, attr = match.groups()
    types_in_union = [t.strip() for t in union_type.split("|")]
    good_types = [t for t in types_in_union if t != bad_type and t != "None"]
    if not good_types:
        return None

    result = _get_error_line(lines, error)
    if result is None:
        return None
    idx, line = result
    indent = get_line_indent(line)

    var_match = re.search(rf"(\w+)\.{re.escape(attr)}", line)
    if not var_match:
        return None

    var_name = var_match.group(1)
    target_type = good_types[0]

    for check_idx in range(max(0, idx - 3), idx):
        if f"isinstance({var_name}" in lines[check_idx]:
            return None

    lines.insert(idx, f"{indent}assert isinstance({var_name}, {target_type})\n")
    return Fix(
        file=error.file,
        line=error.line,
        description=f"Add isinstance({var_name}, {target_type}) narrowing for union-attr",
        strategy="real-fix",
        original_code=line.strip(),
    )


def fix_name_not_defined(lines: list[str], error: MypyError) -> Fix | None:
    """Add a missing import for a name-defined error when the name is a known type.

    This is a REAL fix - it adds the correct import statement.

    Args:
        lines: Source lines of the file (mutated in-place on success).
        error: The mypy ``name-defined`` error to fix.

    Returns:
        A Fix descriptor, or None when this strategy does not apply.
    """
    if error.code != "name-defined":
        return None

    match = re.search(r'Name "(\w+)" is not defined', error.message)
    if not match:
        return None

    name = match.group(1)
    if name in COMMON_TYPE_IMPORTS:
        import_line = COMMON_TYPE_IMPORTS[name]
        if ensure_import(lines, import_line):
            return Fix(
                file=error.file,
                line=error.line,
                description=f"Add missing import: {import_line}",
                strategy="real-fix",
            )
    return None


# ---------------------------------------------------------------------------
# Suppression strategies (last resort)
# ---------------------------------------------------------------------------


def _apply_suppression(lines: list[str], error: MypyError, description: str) -> Fix | None:
    """Add a targeted ``# type: ignore[code]`` to the error line.

    Shared implementation used by both import and generic suppression strategies.

    Args:
        lines: Source lines of the file (mutated in-place on success).
        error: The mypy error to suppress.
        description: Human-readable description for the Fix record.

    Returns:
        A Fix descriptor, or None when already suppressed or line not found.
    """
    result = _get_error_line(lines, error)
    if result is None:
        return None
    idx, line = result
    if has_type_ignore(line, error.code):
        return None
    lines[idx] = add_type_ignore(line, error.code)
    return Fix(
        file=error.file,
        line=error.line,
        description=description,
        strategy="suppression",
        original_code=line.strip(),
    )


def fix_import_errors(lines: list[str], error: MypyError) -> Fix | None:
    """Suppress ``import-untyped`` / ``import-not-found`` for third-party packages.

    Args:
        lines: Source lines of the file (mutated in-place on success).
        error: The mypy import error to suppress.

    Returns:
        A Fix descriptor, or None when this strategy does not apply.
    """
    if error.code not in IMPORT_SUPPRESSIBLE:
        return None
    return _apply_suppression(lines, error, f"Suppress {error.code} for third-party import")


def fix_generic_suppression(lines: list[str], error: MypyError) -> Fix | None:
    """Last resort: add ``# type: ignore[code]`` for known suppressible codes.

    Args:
        lines: Source lines of the file (mutated in-place on success).
        error: The mypy error to suppress.

    Returns:
        A Fix descriptor, or None when the error code is not suppressible.
    """
    if error.code not in GENERIC_SUPPRESSIBLE:
        return None
    return _apply_suppression(
        lines,
        error,
        f"Suppress mypy [{error.code}]: {error.message[:80]}",
    )


# ---------------------------------------------------------------------------
# Strategy registry (priority order: real fixes first, suppressions last)
# ---------------------------------------------------------------------------

FIX_STRATEGIES = [
    fix_callable_as_type,
    fix_union_attr,
    fix_name_not_defined,
    fix_import_errors,
    fix_generic_suppression,
]
