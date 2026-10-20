"""Regenerate ``data/null_space_exploration/examples.json`` (#5094).

The document layout is ``{"schema_version": 1, "sections": {"<name>": {...}}}``.  Each section is
produced by one zero-argument callable registered in :data:`SECTION_BUILDERS`; adding a section
(for example the nonlinear-continuation companion) is a one-line registry entry, and the
rendering and writing below are shared.  Output is deterministic: sections are built from seeded
generators, floats are rounded to :data:`SIGNIFICANT_DIGITS` significant digits, negative zero is
normalised, keys are sorted, the layout matches prettier (the repository's JSON hook) and the
file is written with LF line endings.
"""

import argparse
import json
import math
from collections.abc import Callable, Mapping
from pathlib import Path

from src.tools.null_space_continuation_examples import build_continuation_section
from src.tools.null_space_exploration_examples import linear_section

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data/null_space_exploration/examples.json"
SCHEMA_VERSION = 1
SIGNIFICANT_DIGITS = 10
LINE_WIDTH = 80  # Prettier's default print width; longer arrays must wrap.
NEWLINE = chr(10)  # Explicit LF: never rely on the platform line ending.
INDENT = "  "

type Section = dict[str, object]
type SectionBuilder = Callable[[], Section]

SECTION_BUILDERS: dict[str, SectionBuilder] = {
    "linear": linear_section,
    "continuation": build_continuation_section,
}


def _stable(value: object) -> object:
    """Recursively round floats and normalise ``-0.0`` so rendering is reproducible."""
    if isinstance(value, bool) or value is None or isinstance(value, int | str):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("examples.json may not contain non-finite numbers")
        rounded = float(f"{value:.{SIGNIFICANT_DIGITS - 1}e}")
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {str(key): _stable(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [_stable(item) for item in value]
    raise TypeError(f"unsupported JSON value of type {type(value).__name__}")


def build_document(builders: Mapping[str, SectionBuilder] | None = None) -> dict[str, object]:
    """Run every registered section builder and wrap the results in the schema envelope."""
    registry = SECTION_BUILDERS if builders is None else builders
    sections = {name: build() for name, build in registry.items()}
    return {"schema_version": SCHEMA_VERSION, "sections": sections}


def _wide_container(item: object) -> bool:
    """True for a list or dict with two or more entries."""
    return isinstance(item, list | dict) and len(item) > 1


def _breaks_like_prettier(items: list[object]) -> bool:
    """Prettier forces a break for 2+ same-kind containers that each hold 2+ entries."""
    same_kind = len({type(item) for item in items}) == 1
    return len(items) > 1 and same_kind and all(_wide_container(item) for item in items)


def _layout_object(value: dict[str, object], depth: int) -> str:
    """Expanded object with sorted keys."""
    if not value:
        return "{}"
    inner = INDENT * (depth + 1)
    rows = []
    for key in sorted(value):
        lead = f"{inner}{json.dumps(key)}: "
        rows.append(lead + _layout(value[key], depth + 1, len(lead)))
    return "{" + NEWLINE + ("," + NEWLINE).join(rows) + NEWLINE + INDENT * depth + "}"


def _is_number(item: object) -> bool:
    return isinstance(item, int | float) and not isinstance(item, bool)


def _fill(items: list[str], depth: int) -> str:
    """Prettier's ``fill`` for all-number arrays: pack items per line up to ``LINE_WIDTH``."""
    inner = INDENT * (depth + 1)
    lines, current = [], inner + items[0]
    for index, item in enumerate(items[1:], start=2):
        comma = len(",") if index < len(items) else 0
        if len(current) + len(", ") + len(item) + comma > LINE_WIDTH:
            lines.append(current + ",")
            current = inner + item
        else:
            current += ", " + item
    lines.append(current)
    return "[" + NEWLINE + NEWLINE.join(lines) + NEWLINE + INDENT * depth + "]"


def _layout_array(value: list[object], depth: int, lead: int) -> str:
    """Inline array unless prettier would break it (see :func:`_layout`).

    ``lead`` is the width already used on the line (indent and key), which prettier counts.
    """
    pad = INDENT * depth
    items = [_layout(item, depth + 1, len(INDENT) * (depth + 1)) for item in value]
    flat = "[" + ", ".join(items) + "]"
    forced = _breaks_like_prettier(value) or any(isinstance(item, dict) for item in value)
    if not (forced or NEWLINE in flat or lead + len(flat) + 1 > LINE_WIDTH):
        return flat
    if value and all(_is_number(item) for item in value):
        return _fill(items, depth)
    rows = [f"{INDENT * (depth + 1)}{item}" for item in items]
    return "[" + NEWLINE + ("," + NEWLINE).join(rows) + NEWLINE + pad + "]"


def _number(value: object) -> str:
    """JSON number in prettier's normal form: no ``+`` or leading zeros in the exponent."""
    text = json.dumps(value)
    if "e" not in text:
        return text
    mantissa, exponent = text.split("e")
    sign = "-" if exponent.startswith("-") else ""
    return f"{mantissa}e{sign}{exponent.lstrip('+-').lstrip('0') or '0'}"


def _layout(value: object, depth: int, lead: int = 0) -> str:
    """Lay ``value`` out the way prettier prints JSON so the pre-commit hook is a no-op.

    Objects are always expanded with sorted keys; arrays stay on one line unless they must
    break (prettier's multi-container rule, a nested object, or exceeding ``LINE_WIDTH``).
    """
    if isinstance(value, dict):
        return _layout_object(value, depth)
    if isinstance(value, list):
        return _layout_array(value, depth, lead)
    if _is_number(value):
        return _number(value)
    return json.dumps(value)


def render_document(document: Mapping[str, object]) -> str:
    """Render ``document`` as prettier-stable JSON with stable floats and a final LF."""
    return _layout(_stable(document), 0) + NEWLINE


def write_document(path: Path = OUTPUT) -> Path:
    """Write the rendered document to ``path`` with LF endings and return the path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(render_document(build_document()).encode("utf-8"))
    return path


def main() -> int:
    """Command-line entry point: regenerate the examples file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    write_document(parser.parse_args().output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
