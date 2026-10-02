"""Site-wide glossary models, validation, and loader (WEB-01.5 #4490).

Provides:
- `load_glossary`: load and parse data/glossary.yml.
- `validate_glossary_entry`: validate schema and fields for a glossary item.
- `MINIMUM_TERMS`: minimum term count requirement at launch.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

MINIMUM_TERMS: int = 60


def get_glossary_path(root: Path | None = None) -> Path:
    """Return canonical path to data/glossary.yml."""
    if root is None:
        root = Path(__file__).resolve().parents[2]
    return root / "data" / "glossary.yml"


def load_glossary(yaml_path: Path | None = None) -> dict[str, dict[str, Any]]:
    """Load and parse data/glossary.yml."""
    path = yaml_path or get_glossary_path()
    if not path.exists():
        raise FileNotFoundError(f"Missing glossary data file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("data/glossary.yml must be a mapping of term keys to definitions")
    return data


def validate_glossary_entry(key: str, entry: dict[str, Any]) -> None:
    """Validate schema conformance for a single glossary entry."""
    required = ("name", "plain", "technical", "canonical_page")
    for req in required:
        if req not in entry or not entry[req]:
            raise ValueError(f"Glossary term '{key}' is missing required field '{req}'")
    if not isinstance(entry["name"], str):
        raise ValueError(f"Glossary term '{key}' name must be a string")
