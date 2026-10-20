"""Read access to the shared null-space exploration numbers (#5096).

The article "After One Solution: Exploring Dynamically Equivalent Force Allocations" quotes only
numbers that ``scripts/build_null_space_exploration_examples.py`` wrote to
``data/null_space_exploration/examples.json``.  This module is the one place that reads that file,
so the article's code listing and ``tests/test_after_one_solution_article.py`` share one loader
and a number cannot be typed into prose without the data agreeing.

The JSON layout is ``{"schema_version": 1, "sections": {"<name>": {...}}}``; the sections are
``"linear"`` (propositions P1-P5 and P7 and the toy examples) and ``"continuation"`` (P6).
"""

import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_PATH = ROOT / "data/null_space_exploration/examples.json"
SUPPORTED_SCHEMA_VERSION = 1


def load_examples(path: Path = EXAMPLES_PATH) -> dict[str, Any]:
    """Return the parsed examples document.

    Preconditions: ``path`` is a readable JSON file written by the builder script.

    Postconditions: the result has ``schema_version == 1`` and a ``sections`` mapping.
    Raises ``FileNotFoundError`` for a missing file and ``ValueError`` for malformed JSON, an
    unsupported ``schema_version`` or a missing ``sections`` mapping.
    """
    if not isinstance(path, Path):
        raise TypeError(f"path must be a pathlib.Path, got {type(path).__name__}")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"{path} is not valid JSON: {error}") from error
    if not isinstance(document, dict):
        raise ValueError(f"{path} must contain a JSON object")
    if document.get("schema_version") != SUPPORTED_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported schema_version {document.get('schema_version')!r}; "
            f"expected {SUPPORTED_SCHEMA_VERSION}"
        )
    if not isinstance(document.get("sections"), dict):
        raise ValueError(f"{path} lacks a 'sections' mapping")
    return document


def example_section(name: str, path: Path = EXAMPLES_PATH) -> dict[str, Any]:
    """Return an independent copy of one named section of the examples document.

    Preconditions: ``name`` is a string naming a registered section (``"linear"`` or
    ``"continuation"``); ``path`` satisfies :func:`load_examples`.

    Postconditions: mutating the result never changes the file or later calls.  Raises
    ``TypeError`` for a non-string name and ``KeyError`` listing the known sections for an
    unknown one.
    """
    if not isinstance(name, str):
        raise TypeError(f"name must be a string, got {type(name).__name__}")
    sections: dict[str, Any] = load_examples(path)["sections"]
    if name not in sections:
        raise KeyError(f"unknown section {name!r}; known sections: {sorted(sections)}")
    section: dict[str, Any] = copy.deepcopy(sections[name])
    return section
