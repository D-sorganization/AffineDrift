from __future__ import annotations

import re

from .file_utils import (
    _ensure_import,
    _get_error_line,
    add_type_ignore,
    get_line_indent,
    has_type_ignore,
)
from .models import Fix, MypyError

# Common third-party modules that trigger import-untyped
KNOWN_UNTYPED_MODULES = {
    "mujoco",
    "dm_control",
    "pinocchio",
    "pin",
    "drake",
    "pydrake",
    "opensim",
    "myosuite",
    "gymnasium",
    "gym",
    "meshcat",
    "trimesh",
    "pybullet",
    "cv2",
    "mediapipe",
    "onnxruntime",
    "sklearn",
    "scipy",
    "PIL",
    "yaml",
    "toml",
    "rich",
    "click",
    "uvicorn",
    "starlette",
    "websockets",
    "serial",
    "usb",
    "hid",
    "pygame",
    "OpenGL",
    "moderngl",
}

# Common type imports that resolve name-defined errors
COMMON_TYPE_IMPORTS = {
    "Callable": "from collections.abc import Callable",
    "Iterator": "from collections.abc import Iterator",
    "Generator": "from collections.abc import Generator",
    "Sequence": "from collections.abc import Sequence",
    "Mapping": "from collections.abc import Mapping",
    "Iterable": "from collections.abc import Iterable",
    "Optional": "from typing import Optional",
    "Union": "from typing import Union",
    "Any": "from typing import Any",
    "ClassVar": "from typing import ClassVar",
    "TypeVar": "from typing import TypeVar",
    "Protocol": "from typing import Protocol",
    "TypeAlias": "from typing import TypeAlias",
    "Final": "from typing import Final",
    "Literal": "from typing import Literal",
    "overload": "from typing import overload",
    "cast": "from typing import cast",
    "TYPE_CHECKING": "from typing import TYPE_CHECKING",
    "Self": "from typing import Self",
    "TypedDict": "from typing import TypedDict",
    "NamedTuple": "from typing import NamedTuple",
    "Path": "from pathlib import Path",
    "datetime": "from datetime import datetime",
    "timedelta": "from datetime import timedelta",
    "Enum": "from enum import Enum",
    "dataclass": "from dataclasses import dataclass",
    "abstractmethod": "from abc import abstractmethod",
    "ABC": "from abc import ABC",
}


def fix_callable_as_type(lines: list[str], error: MypyError) -> Fix | None:
    """Fix 'callable is not valid as a type' by replacing with Callable.

    This is a REAL fix, not a suppression.
    """
    if error.code != "valid-type":
        return None
    if '"callable" is not valid as a type' not in error.message.lower():
        return None

    result = _get_error_line(lines, error)
    if result is None:
        return None
    idx, line = result

    # Replace 'callable' with 'Callable[..., Any]' in type annotations
    if ": callable" in line.lower():
        original = line
        line = re.sub(
            r":\s*callable\b",
            ": Callable[..., Any]",
            line,
            flags=re.IGNORECASE,
        )
        lines[idx] = line

        _ensure_import(lines, "from collections.abc import Callable")
        _ensure_import(lines, "from typing import Any")

        return Fix(
            file=error.file,
            line=error.line,
            description="Replace 'callable' with 'Callable[..., Any]'",
            strategy="real-fix",
            original_code=original.strip(),
        )
    return None


def fix_union_attr(lines: list[str], error: MypyError) -> Fix | None:
    """Fix union-attr by adding isinstance narrowing.

    This is a REAL fix - adds proper type narrowing.
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

    assert_line = f"{indent}assert isinstance({var_name}, {target_type})\n"
    lines.insert(idx, assert_line)

    return Fix(
        file=error.file,
        line=error.line,
        description=f"Add isinstance({var_name}, {target_type}) narrowing for union-attr",
        strategy="real-fix",
        original_code=line.strip(),
    )


def fix_name_not_defined(lines: list[str], error: MypyError) -> Fix | None:
    """Fix name-defined errors by adding missing imports.

    This is a REAL fix when the name is a known type.
    """
    if error.code != "name-defined":
        return None

    match = re.search(r'Name "(\w+)" is not defined', error.message)
    if not match:
        return None

    name = match.group(1)
    if name in COMMON_TYPE_IMPORTS:
        import_line = COMMON_TYPE_IMPORTS[name]
        if _ensure_import(lines, import_line):
            return Fix(
                file=error.file,
                line=error.line,
                description=f"Add missing import: {import_line}",
                strategy="real-fix",
            )
    return None


# Error codes eligible for targeted suppression (import-related)
_IMPORT_SUPPRESSIBLE = frozenset({"import-untyped", "import-not-found"})

# Error codes eligible for last-resort suppression
_GENERIC_SUPPRESSIBLE = frozenset(
    {
        "assignment",
        "arg-type",
        "return-value",
        "attr-defined",
        "override",
        "misc",
        "call-overload",
        "type-arg",
        "index",
        "operator",
        "no-untyped-call",
        "redundant-cast",
        "var-annotated",
    }
)


def _apply_suppression(
    lines: list[str],
    error: MypyError,
    description: str,
) -> Fix | None:
    """Add a targeted type: ignore suppression to the error line.

    Shared by import-error and generic-suppression strategies.
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
    """Suppress import-untyped and import-not-found for third-party packages."""
    if error.code not in _IMPORT_SUPPRESSIBLE:
        return None
    return _apply_suppression(
        lines,
        error,
        f"Suppress {error.code} for third-party import",
    )


def fix_generic_suppression(lines: list[str], error: MypyError) -> Fix | None:
    """Last resort: add targeted type: ignore[code] for known error codes."""
    if error.code not in _GENERIC_SUPPRESSIBLE:
        return None
    return _apply_suppression(
        lines,
        error,
        f"Suppress mypy [{error.code}]: {error.message[:80]}",
    )


# Fix strategies in priority order (real fixes first, suppressions last)
FIX_STRATEGIES = [
    fix_callable_as_type,
    fix_union_attr,
    fix_name_not_defined,
    fix_import_errors,
    fix_generic_suppression,  # Last resort
]
