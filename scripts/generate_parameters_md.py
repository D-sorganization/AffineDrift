"""Regenerate PARAMETERS.md from data/canonical_parameters.json (issue #5595).

Usage:
    python3 -m scripts.generate_parameters_md [--check]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.canonical_parameters_registry import (
    PARAMETERS_MD,
    load_registry,
    render_parameters_markdown,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=None,
        help="path to canonical_parameters.json (default: data/canonical_parameters.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PARAMETERS_MD,
        help="output markdown path (default: PARAMETERS.md)",
    )
    parser.add_argument("--check", action="store_true", help="exit 1 if output would change")
    args = parser.parse_args()

    data_path = args.data or (
        Path(__file__).resolve().parent.parent / "data" / "canonical_parameters.json"
    )
    rendered = render_parameters_markdown(load_registry(data_path))
    if args.check:
        current = args.output.read_text(encoding="utf-8") if args.output.is_file() else ""
        if current != rendered:
            print(f"{args.output} is out of date; run python3 scripts/generate_parameters_md.py")
            return 1
        print(f"{args.output} matches data/canonical_parameters.json")
        return 0

    args.output.write_text(rendered, encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
